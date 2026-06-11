#!/usr/bin/env python3
"""Kinetic-typography build — TikTok talking-head energy, no person.

Each 1-3 word caption chunk becomes a full-screen text moment: words pop in
at their spoken time, keywords get accent colors, the generic-ad quote gets a
red strikethrough, and the background is a slow-zoom gradient that changes
hue per scene. Audio-anchored exactly like build.py.

    python3 gen_vo_local.py   # produces audio + wordsraw_*.json first
    python3 build_kinetic.py  # → out/short-kinetic.mp4
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import (AudioFileClip, ColorClip, CompositeAudioClip,
                     CompositeVideoClip, ImageClip, vfx)
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".text_cache"
CONFIG = json.loads((HERE / "config.json").read_text())
P = CONFIG["palette"]
FMT = CONFIG["format"]
W, H, FPS = FMT["width"], FMT["height"], FMT["fps"]

START_PAD, LEAD, TAIL, XFADE = 0.3, 0.35, 0.7, 0.3
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# scene id → background accent hue
SCENE_ACCENT = {"01": P["accent1"], "02": P["warn"], "03": P["accent1"],
                "04": P["accent2"], "05": P["accent1"]}

# lowercase word (letters only) → color
KEYWORDS = {
    "reclama": P["warn"], "reclamă": P["warn"], "bani": P["warn"],
    "generic": P["warn"], "problema": P["warn"], "greșeli": P["warn"],
    "oferta": P["accent2"], "pagina": P["accent2"], "mesaj": P["accent2"],
    "mesajul": P["accent2"], "concret": P["accent2"], "rezultat": P["accent2"],
    "30": P["accent2"], "zile": P["accent2"], "conversații": P["accent2"],
    "funcționează": P["warn"], "schimbe": P["warn"], "schimbi": P["warn"],
}

# the quoted generic ad in scene 03 → slate + red strikethrough
STRIKE_WORDS = {"03": {"învață", "engleză", "rapid"}}
QUOTE_AFTER = {"03": {"doar:"}}  # words after this marker get quote styling


def rgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def clean(w):
    return re.sub(r"[^\w]", "", w.lower())


def bg_image(accent_hex: str, key: str) -> str:
    """Dark gradient + soft glow + faint grid, oversized for slow zoom."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"kbg_{key}.png"
    if path.exists():
        return str(path)
    ink, acc = rgb(P["ink"]), rgb(accent_hex)
    img = Image.new("RGB", (W, H), ink)
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 700, -500, W // 2 + 700, 900), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(260))
    img = Image.composite(Image.new("RGB", (W, H), acc), img, glow)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=tuple(min(255, c + 5) for c in ink))
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=tuple(min(255, c + 5) for c in ink))
    img.save(path)
    return str(path)


def word_png(text: str, size: int, color: str, strike: bool) -> str:
    key = hashlib.sha1(f"kw|{text}|{size}|{color}|{strike}".encode()).hexdigest()[:16]
    path = CACHE / f"{key}.png"
    if path.exists():
        return str(path)
    f = ImageFont.truetype(FONT, size)
    sw = max(6, size // 12)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = probe.textbbox((0, 0), text, font=f, stroke_width=sw)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = sw + 8
    img = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=(*rgb(color), 255),
           stroke_width=sw, stroke_fill=(*rgb(P["ink"]), 255))
    if strike:
        y = img.height // 2 + size // 12
        d.line((pad // 2, y, img.width - pad // 2, y), fill=(*rgb(P["warn"]), 255),
               width=max(10, size // 9))
    img.save(path)
    return str(path)


def strike_flags(words: list[dict], scene_id: str) -> list[bool]:
    """Per-word strikethrough flags: words between the QUOTE_AFTER marker and
    the next sentence end (inclusive) that belong to the strike set."""
    strikes = STRIKE_WORDS.get(scene_id, set())
    markers = QUOTE_AFTER.get(scene_id, set())
    flags, on = [], False
    for w in words:
        flag = on and clean(w["text"]) in strikes
        flags.append(flag)
        if w["text"].lower() in markers:
            on = True
        elif on and flag and w["text"][-1:] in ".!?…":
            on = False
    return flags


def layout_chunk(chunk_words: list[dict], scene_id: str, flags: list[bool]):
    """Plan lines/sizes/colors for one full-screen text moment.

    Returns entries = [{img, x, y, start}]."""
    texts = [w["text"].upper().strip(",.;") if not w["text"][-1:] in ".!?…"
             else w["text"].upper().strip(",;") for w in chunk_words]
    texts = [t if t else w["text"].upper() for t, w in zip(texts, chunk_words)]
    n = len(texts)
    joined = " ".join(texts)
    base = 175 if len(joined) <= 10 else 150 if len(joined) <= 16 else 125

    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    def width_at(size):
        f = ImageFont.truetype(FONT, size)
        sw = max(6, size // 12)
        return [probe.textbbox((0, 0), t, font=f, stroke_width=sw)[2] for t in texts]

    max_w = int(W * 0.86)
    # try one word per line if any word is long, else pack 1-2 per line
    lines: list[list[int]] = []
    cur, cur_w = [], 0
    size = base
    widths = width_at(size)
    gap_w = int(size * 0.30)
    for i, wd in enumerate(widths):
        if cur and cur_w + gap_w + wd > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
        cur.append(i)
        cur_w += (gap_w if len(cur) > 1 else 0) + wd
    lines.append(cur)
    # shrink if a single word still overflows
    while any(sum(width_at(size)[i] for i in ln) +
              (len(ln) - 1) * int(size * 0.3) > max_w for ln in lines) and size > 70:
        size -= 10
    widths = width_at(size)
    gap_w = int(size * 0.30)
    line_h = int(size * 1.32)
    total_h = line_h * len(lines)
    y0 = (H - total_h) / 2 - H * 0.04

    entries = []
    for li, ln in enumerate(lines):
        lw = sum(widths[i] for i in ln) + (len(ln) - 1) * gap_w
        x = (W - lw) / 2
        for i in ln:
            w = chunk_words[i]
            is_strike = flags[i]
            color = (P["slate"] if is_strike
                     else KEYWORDS.get(clean(w["text"]), P["white"]))
            img = word_png(texts[i], size, color, is_strike)
            entries.append({"img": img, "x": x, "y": y0 + li * line_h,
                            "start": w["start"]})
            x += widths[i] + gap_w
    return entries


def pop(clip: ImageClip, x: float, y: float) -> ImageClip:
    """Overshoot pop-in anchored roughly at the word position."""
    def scale(t):
        if t >= 0.14:
            return 1.0
        k = t / 0.14
        return 1.45 - 0.45 * (1 - (1 - k) ** 2)
    iw, ih = clip.size
    return (clip.resized(lambda t: scale(t))
            .with_position(lambda t: (x - iw * (scale(t) - 1) / 2,
                                      y - ih * (scale(t) - 1) / 2)))


def build():
    scenes = json.loads((HERE / "scenes.json").read_text())["scenes"]
    durations = json.loads((HERE / "vo_durations.json").read_text())

    clips = [ColorClip((W, H), color=rgb(P["ink"]))]
    audio = []
    cursor = START_PAD

    print("── kinetic timeline ──")
    for s in scenes:
        sid = s["id"]
        vo = durations[sid]
        scene_start, audio_start = cursor, cursor + LEAD
        scene_dur = LEAD + vo + TAIL
        print(f"  {sid} {s['slug']:14s} {scene_start:6.2f} → {scene_start + scene_dur:6.2f}")

        bg = bg_image(SCENE_ACCENT[sid], sid)
        with Image.open(bg) as im:
            base_scale = max(W / im.width, H / im.height)
        zoom = (ImageClip(bg).with_duration(scene_dur)
                .resized(lambda t, d=scene_dur, b=base_scale: b * (1.0 + 0.06 * t / d))
                .with_position(("center", "center")))
        clips.append(zoom.with_start(scene_start)
                     .with_effects([vfx.FadeIn(XFADE), vfx.FadeOut(XFADE)]))

        words = json.loads((HERE / "captions" / f"wordsraw_{sid}.json").read_text())
        pills = json.loads((HERE / "captions" / f"words_{sid}.json").read_text())

        # map raw words onto pill chunks in order
        wi = 0
        chunk_list = []
        for pill in pills:
            n = len(pill["text"].split())
            chunk_list.append(words[wi:wi + n])
            wi += n

        flags = strike_flags(words, sid)
        wi = 0
        for ci, chunk in enumerate(chunk_list):
            chunk_end = (chunk_list[ci + 1][0]["start"] if ci + 1 < len(chunk_list)
                         else vo + TAIL * 0.6)
            entries = layout_chunk(chunk, sid, flags[wi:wi + len(chunk)])
            wi += len(chunk)
            for e in entries:
                t0 = audio_start + e["start"]
                dur = max(0.25, audio_start + chunk_end - t0)
                c = ImageClip(e["img"]).with_duration(dur)
                clips.append(pop(c, e["x"], e["y"]).with_start(t0))

        mp3 = HERE / "audio" / "scenes" / f"{sid}_{s['slug']}.mp3"
        audio.append(AudioFileClip(str(mp3)).with_effects([MultiplyVolume(1.1)])
                     .with_start(audio_start))
        cursor = scene_start + scene_dur

    total = cursor + 0.4
    clips[0] = clips[0].with_duration(total)
    print(f"  total: {total:.2f}s")

    final = (CompositeVideoClip(clips, size=(W, H)).with_duration(total)
             .with_audio(CompositeAudioClip(audio)))
    out = HERE / "out" / "short-kinetic.mp4"
    out.parent.mkdir(exist_ok=True)
    final.write_videofile(str(out), fps=FPS, codec="libx264",
                          audio_codec="aac", preset="medium", threads=8)
    print("wrote", out)


if __name__ == "__main__":
    build()
