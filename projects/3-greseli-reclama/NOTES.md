# 3-greseli-reclama — note de proiect

Video vertical 9:16 (44s) pentru TikTok / Instagram Reels / Facebook Reels,
pe baza scriptului „3 greșeli care fac o reclamă să piardă bani".

## Cum a fost produs (mediu fără cloud GPU)

Acest proiect a fost construit într-un sandbox fără Modal/RunPod configurat,
deci pipeline-ul standard (Ideogram/LTX + Qwen3-TTS + whisper) a fost înlocuit
cu echivalente offline:

- **Carduri vizuale** — `gen_cards.py` (PIL, paleta din `config.json`),
  în loc de Ideogram 4. Regenerare: `python3 gen_cards.py`.
- **Voiceover RO** — `gen_vo_local.py` cu piper `ro_RO-mihai-medium`
  (voce masculină românească, rulează local pe CPU), în loc de Qwen3-TTS.
  Model: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ro_RO-mihai-medium.tar.bz2
  Dezarhivează și setează `PIPER_RO_MODEL=<cale>/ro_RO-mihai-medium.onnx`.
  Necesită `pip install piper-tts`.
- **Subtitrări karaoke** — tot `gen_vo_local.py`: sintetizează propoziție cu
  propoziție și distribuie cuvintele proporțional, în loc de whisper.

## Upgrade-uri recomandate (după `/setup`)

1. **Voce mai naturală**: `python3 gen_vo.py` cu Qwen3-TTS (clonare voce
   proprie posibilă cu `/voice-clone`) — apoi `gen_captions.py` + `build.py`.
2. **B-roll cu mișcare**: înlocuiește 1–2 carduri cu clipuri LTX-2
   (`tools/ltx2.py`, 576x1024) pentru pattern interrupt.
3. **Muzică de fundal**: `tools/music_gen.py` → `audio/music.mp3`
   (build.py o preia și o atenuează automat).

## Rerandare

```bash
python3 gen_cards.py      # doar dacă schimbi cardurile
python3 gen_vo_local.py   # doar dacă schimbi textul din scenes.json
python3 build.py          # → out/short.mp4
```
