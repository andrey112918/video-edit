#!/usr/bin/env python3
"""Offline VO + caption timing via piper (ro_RO-mihai-medium), replacing
gen_vo.py + gen_captions.py when no cloud GPU / whisper is available.

Synthesizes each scene sentence-by-sentence, records exact sentence offsets,
and distributes word timings inside each sentence proportionally to word
length. Outputs match the standard pipeline:

    audio/scenes/{id}_{slug}.mp3   vo_durations.json   captions/words_{id}.json

Voice model (downloaded from sherpa-onnx GitHub releases):
    https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ro_RO-mihai-medium.tar.bz2
Set PIPER_RO_MODEL to the extracted .onnx path (default: /tmp/...).
"""
import json
import os
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from piper import PiperVoice

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
CAPS = CONFIG.get("captions", {})
MAX_WORDS = CAPS.get("maxWords", 3)
MAX_CHARS = CAPS.get("maxChars", 22)

MODEL = os.environ.get(
    "PIPER_RO_MODEL",
    "/tmp/vits-piper-ro_RO-mihai-medium/ro_RO-mihai-medium.onnx")

SENTENCE_GAP = 0.18   # extra silence between sentences
TAIL_TRIM_DB = -45.0  # trim trailing near-silence before timing words


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p for p in parts if p]


def trimmed_len(samples: np.ndarray, rate: int) -> int:
    """Sample count up to the end of actual speech (skip trailing silence)."""
    thresh = 32767 * (10 ** (TAIL_TRIM_DB / 20))
    idx = np.nonzero(np.abs(samples.astype(np.int32)) > thresh)[0]
    return int(idx[-1]) + 1 if len(idx) else len(samples)


def word_chunks(words: list[tuple[str, float, float]]):
    """Group (word, start, end) into caption pills per config limits."""
    chunks, cur = [], []
    for w, s, e in words:
        candidate = " ".join([c[0] for c in cur] + [w])
        if cur and (len(cur) >= MAX_WORDS or len(candidate) > MAX_CHARS):
            chunks.append(cur)
            cur = []
        cur.append((w, s, e))
        if w[-1:] in ".!?…:":  # break pills at punctuation
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return [{"text": " ".join(c[0] for c in ch),
             "start": round(ch[0][1], 3),
             "end": round(ch[-1][2], 3)} for ch in chunks]


def main() -> None:
    voice = PiperVoice.load(MODEL)
    rate = voice.config.sample_rate
    scenes = json.loads((HERE / "scenes.json").read_text())["scenes"]
    (HERE / "audio" / "scenes").mkdir(parents=True, exist_ok=True)
    (HERE / "captions").mkdir(exist_ok=True)
    durations = {}

    for s in scenes:
        sentences = split_sentences(s["text"])
        pieces, words, cursor = [], [], 0.0
        for sent in sentences:
            tmp = HERE / ".text_cache" / "sent.wav"
            tmp.parent.mkdir(exist_ok=True)
            with wave.open(str(tmp), "wb") as w:
                voice.synthesize_wav(sent, w)
            with wave.open(str(tmp)) as w:
                samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
            speech_n = trimmed_len(samples, rate)
            keep_n = min(len(samples), speech_n + int(0.08 * rate))
            samples = samples[:keep_n]
            dur = len(samples) / rate
            speech_dur = speech_n / rate

            toks = sent.split()
            weights = [len(re.sub(r"[^\w]", "", t)) + 1.5 for t in toks]
            total_w = sum(weights)
            t = cursor
            for tok, wt in zip(toks, weights):
                wdur = speech_dur * wt / total_w
                words.append((tok, t, t + wdur))
                t += wdur

            pieces.append(samples)
            pieces.append(np.zeros(int(SENTENCE_GAP * rate), dtype=np.int16))
            cursor += dur + SENTENCE_GAP

        audio = np.concatenate(pieces)
        total = len(audio) / rate
        wav_path = HERE / ".text_cache" / f"{s['id']}.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(audio.tobytes())

        mp3 = HERE / "audio" / "scenes" / f"{s['id']}_{s['slug']}.mp3"
        import imageio_ffmpeg
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                        "-i", str(wav_path), "-codec:a", "libmp3lame", "-q:a", "3",
                        str(mp3)], check=True)

        durations[s["id"]] = round(total, 3)
        (HERE / "captions" / f"words_{s['id']}.json").write_text(
            json.dumps(word_chunks(words), ensure_ascii=False, indent=1))
        (HERE / "captions" / f"wordsraw_{s['id']}.json").write_text(
            json.dumps([{"text": w, "start": round(a, 3), "end": round(b, 3)}
                        for w, a, b in words], ensure_ascii=False, indent=1))
        wpm = len(s["text"].split()) / total * 60
        print(f"  {s['id']} {s['slug']:16s} {total:6.2f}s  {wpm:5.0f} wpm")

    (HERE / "vo_durations.json").write_text(json.dumps(durations, indent=1))
    print(f"total VO: {sum(durations.values()):.1f}s")


if __name__ == "__main__":
    main()
