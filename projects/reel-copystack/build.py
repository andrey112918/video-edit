#!/usr/bin/env python3
"""CopyStack reel — kinetic typography + motion graphics, audio-free dub base.

9:16 1080x1920 @30fps, ~100s, timed exactly to the Romanian reel script so the
voice can be recorded over it. Sections: hook → autoritate → website hero →
proces timeline scroll → servicii cards → diferențiere → CTA.

    python3 build.py          # full render → out/reel-copystack.mp4
    python3 build.py --draft  # half-res fast draft → out/draft.mp4
    python3 build.py --stills # PNG of one frame per section → out/stills/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import CompositeVideoClip, ImageClip, vfx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONTS = ROOT / ".claude/skills/ui-styling/canvas-fonts"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

DRAFT = "--draft" in sys.argv
STILLS = "--stills" in sys.argv
SCALE = 0.5 if DRAFT else 1.0
W, H, FPS = int(1080 * SCALE), int(1920 * SCALE), 30
DUR = 100.0

# ---- palette (CopyStack tokens) ----
INK = (13, 12, 10)        # #0d0c0a
INK2 = (20, 18, 14)       # elevated
FG = (244, 239, 230)      # #f4efe6
MUT = (165, 158, 144)     # muted
FAINT = (110, 104, 92)
AMBER = (245, 166, 35)    # #f5a623
AMBER2 = (255, 193, 77)
RED = (248, 113, 113)
GREEN = (74, 222, 128)
BORDER = (46, 43, 36)

SERIF = str(FONTS / "Gloock-Regular.ttf")
SANS = str(FONTS / "InstrumentSans-Regular.ttf")
SANSB = str(FONTS / "InstrumentSans-Bold.ttf")
MONO = str(FONTS / "JetBrainsMono-Regular.ttf")

def S(v):            # scale helper
    return int(v * SCALE)

def font(path, size):
    return ImageFont.truetype(path, S(size))

# ---------------------------------------------------------------- backgrounds
def bg_image(key: str, glow_y: float, strength: int = 80) -> Image.Image:
    """Dark base + amber glow orb + faint grid, oversized 1.12x for slow zoom."""
    w, h = int(W * 1.12), int(H * 1.12)
    img = Image.new("RGB", (w, h), INK)
    glow = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    cy = int(h * glow_y)
    gd.ellipse((w // 2 - S(620), cy - S(520), w // 2 + S(620), cy + S(520)), fill=strength)
    glow = glow.filter(ImageFilter.GaussianBlur(S(230)))
    img = Image.composite(Image.new("RGB", (w, h), AMBER), img, glow)
    d = ImageDraw.Draw(img)
    grid = tuple(min(255, c + 6) for c in INK)
    for x in range(0, w, S(90)):
        d.line([(x, 0), (x, h)], fill=grid)
    for y in range(0, h, S(90)):
        d.line([(0, y), (w, y)], fill=grid)
    return img

def bg_clip(key, t0, t1, glow_y=0.32):
    img = bg_image(key, glow_y)
    base = ImageClip(np.array(img)).with_start(t0).with_duration(t1 - t0)
    z0, z1 = 1.0, 1.06
    dur = t1 - t0
    base = base.resized(lambda t: z0 + (z1 - z0) * (t / dur))
    return base.with_position(("center", "center"))

# ---------------------------------------------------------------- text pieces
def text_img(text, fnt, fill, max_w=None, line_gap=0.18, align="center"):
    """Render (possibly wrapped) text to a tight RGBA image."""
    probe = Image.new("RGBA", (10, 10))
    pd = ImageDraw.Draw(probe)
    if max_w:
        words, lines, cur = text.split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if pd.textlength(trial, font=fnt) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur); cur = wd
        lines.append(cur)
    else:
        lines = text.split("\n")
    asc, desc = fnt.getmetrics()
    lh = asc + desc
    gap = int(lh * line_gap)
    tw = max(int(pd.textlength(l, font=fnt)) for l in lines)
    th = lh * len(lines) + gap * (len(lines) - 1)
    pad = S(30)
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = pad
    for l in lines:
        x = pad if align == "left" else pad + (tw - int(d.textlength(l, font=fnt))) // 2
        d.text((x, y), l, font=fnt, fill=fill)
        y += lh + gap
    return img

def pop(img: Image.Image, t0, t1, pos, slide=26, fade=0.3):
    """ImageClip that fades in while sliding up slightly."""
    c = ImageClip(np.array(img)).with_start(t0).with_duration(max(t1 - t0, 0.1))
    px, py = pos
    sl = S(slide)
    def posf(t):
        k = min(t / fade, 1.0)
        ease = 1 - (1 - k) ** 3
        return (px, py + sl * (1 - ease))
    c = c.with_position(posf).with_effects([vfx.CrossFadeIn(fade), vfx.CrossFadeOut(0.25)])
    return c

def center_x(img):
    return (W - img.width) // 2

def kinetic(lines, t0, t1, accent_idx=(), base_size=92, y_center=0.42):
    """Sequential big statements: each line takes an equal slice of [t0,t1]."""
    clips = []
    n = len(lines)
    slot = (t1 - t0) / n
    for i, line in enumerate(lines):
        color = AMBER if i in accent_idx else FG
        img = text_img(line, font(SERIF, base_size), color, max_w=S(880))
        a, b = t0 + i * slot, t0 + (i + 1) * slot + (0.25 if i < n - 1 else 0)
        clips.append(pop(img, a, b, (center_x(img), int(H * y_center) - img.height // 2)))
    return clips

def caption(text, t0, t1):
    """Bottom subtitle pill with the voice-over line (for dubbing/readers)."""
    fnt = font(SANS, 40)
    txt = text_img(text, fnt, FG, max_w=S(800))
    pad_x, pad_y = S(38), S(20)
    pw, ph = txt.width + pad_x, txt.height + pad_y
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=S(30),
                        fill=(INK2[0], INK2[1], INK2[2], 225),
                        outline=(*BORDER, 255), width=max(S(2), 1))
    pill.alpha_composite(txt, (pad_x // 2, pad_y // 2))
    return pop(pill, t0, t1, ((W - pw) // 2, int(H * 0.80)), slide=18, fade=0.25)

def label(text, t0, t1, y=0.10):
    img = text_img(text.upper(), font(MONO, 30), AMBER)
    return pop(img, t0, t1, (center_x(img), int(H * y)), slide=12)

def watermark(t0, t1):
    img = Image.new("RGBA", (S(360), S(70)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((0, 0), "Copy", font=font(SERIF, 44), fill=FG)
    off = d.textlength("Copy", font=font(SERIF, 44))
    d.text((off, 0), "Stack", font=font(SERIF, 44), fill=AMBER)
    c = ImageClip(np.array(img)).with_start(t0).with_duration(t1 - t0)
    return c.with_position((S(48), S(54))).with_opacity(0.85)

# ---------------------------------------------------------------- site mocks
def frame_card(inner: Image.Image, title="copystack-9.polsia.app") -> Image.Image:
    """Wrap a mock screenshot in a browser chrome card."""
    bar_h = S(64)
    w = inner.width + S(8)
    h = inner.height + bar_h + S(8)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=S(26), fill=(*INK2, 255),
                        outline=(*BORDER, 255), width=max(S(2), 1))
    for i, col in enumerate((AMBER, FAINT, FAINT)):
        cx = S(34) + i * S(34)
        d.ellipse((cx, bar_h // 2 - S(7), cx + S(14), bar_h // 2 + S(7)), fill=col)
    fnt = font(MONO, 24)
    tw = d.textlength(title, font=fnt)
    d.rounded_rectangle((w // 2 - tw // 2 - S(18), S(13), w // 2 + tw // 2 + S(18), bar_h - S(13)),
                        radius=S(12), fill=(*INK, 255))
    d.text((w // 2 - tw // 2, bar_h // 2 - S(13)), title, font=fnt, fill=MUT)
    card.paste(inner, (S(4), bar_h + S(4)))
    return card

def mock_hero() -> Image.Image:
    w, h = S(960), S(1150)
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)
    # nav
    d.text((S(48), S(40)), "CopyStack", font=font(SERIF, 34), fill=FG)
    d.rounded_rectangle((w - S(330), S(30), w - S(40), S(86)), radius=S(28), fill=AMBER)
    d.text((w - S(305), S(42)), "Încearcă Generatorul", font=font(SANSB, 24), fill=INK)
    d.line((0, S(116), w, S(116)), fill=BORDER, width=max(S(2), 1))
    # eyebrow
    d.text((S(48), S(190)), "AI + MĂIESTRIE UMANĂ", font=font(MONO, 26), fill=AMBER)
    # headline
    d.text((S(44), S(250)), "Cuvinte care", font=font(SERIF, 96), fill=FG)
    d.text((S(44), S(370)), "chiar", font=font(SERIF, 96), fill=FG)
    d.text((S(44), S(490)), "funcționează.", font=font(SERIF, 96), fill=AMBER)
    # sub
    sub = text_img("Campanii, reclame și site-uri care convertesc. Viteza AI, măiestrie umană.",
                   font(SANS, 34), MUT, max_w=S(700), align="left")
    img.paste(sub, (S(28), S(640)), sub)
    # buttons
    d.rounded_rectangle((S(48), S(810), S(470), S(896)), radius=S(43), fill=AMBER)
    d.text((S(86), S(832)), "Încearcă Generatorul", font=font(SANSB, 30), fill=INK)
    d.rounded_rectangle((S(496), S(810), S(830), S(896)), radius=S(43), outline=FAINT, width=max(S(2), 1))
    d.text((S(540), S(832)), "Vezi serviciile", font=font(SANS, 30), fill=FG)
    # proof
    d.text((S(48), S(950)), "★★★★★", font=font(SANSB, 30), fill=AMBER)
    d.text((S(48), S(1000)), "Copy livrat pentru e-commerce, SaaS și servicii", font=font(SANS, 26), fill=FAINT)
    return img

PROC_STEPS = [
    ("01", "Apel de descoperire", "Gratuit · 20 min"),
    ("02", "Brief & Research", "Zilele 1–3"),
    ("03", "Ofertă & Plan", "Zilele 3–5"),
    ("04", "AI scrie, omul rafinează", "Săptămânile 1–2"),
    ("05", "Feedback & Revizii", "2 runde incluse"),
    ("06", "Lansare & Optimizare", "Continuu"),
]

def mock_proces() -> Image.Image:
    w = S(960)
    step_h, top = S(210), S(300)
    h = top + step_h * len(PROC_STEPS) + S(80)
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)
    d.text((S(48), S(60)), "CUM FUNCȚIONEAZĂ", font=font(MONO, 26), fill=AMBER)
    d.text((S(44), S(120)), "Drumul tău, pas cu pas.", font=font(SERIF, 64), fill=FG)
    rail_x = S(78)
    d.line((rail_x, top, rail_x, h - S(80)), fill=AMBER, width=max(S(4), 2))
    for i, (num, title, meta) in enumerate(PROC_STEPS):
        y = top + i * step_h
        d.ellipse((rail_x - S(16), y + S(40) - S(16), rail_x + S(16), y + S(40) + S(16)),
                  fill=INK, outline=AMBER, width=max(S(4), 2))
        d.rounded_rectangle((S(130), y, w - S(48), y + step_h - S(30)), radius=S(22),
                            fill=INK2, outline=BORDER, width=max(S(2), 1))
        d.text((S(165), y + S(34)), num, font=font(SERIF, 56), fill=AMBER)
        d.text((S(280), y + S(36)), title, font=font(SERIF, 42), fill=FG)
        d.text((S(280), y + S(104)), meta.upper(), font=font(MONO, 24), fill=FAINT)
    return img

SERVICES = [
    ("Reclame Meta & Google", "hooks care opresc scroll-ul, cost pe client mai mic"),
    ("Landing page-uri", "transformă vizitatorii în clienți, nu doar în trafic"),
    ("Email marketing", "audiența ta, vânzări pe pilot automat"),
    ("Copy pentru website", "fiecare secțiune împinge spre acțiune"),
    ("Scripturi reclame video", "30 de secunde care vând, cadru cu cadru"),
    ("Strategie completă", "poziționare, canale, plan pe 90 de zile"),
]

def service_card(title, sub, idx) -> Image.Image:
    w, h = S(880), S(168)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=S(24), fill=(*INK2, 255),
                        outline=(*AMBER, 255), width=max(S(3), 1))
    d.text((S(36), S(28)), f"0{idx+1}", font=font(SERIF, 46), fill=AMBER)
    d.text((S(135), S(26)), title, font=font(SERIF, 40), fill=FG)
    s = text_img(sub, font(SANS, 27), MUT, max_w=S(680), align="left")
    img.alpha_composite(s, (S(112), S(78)))
    return img

def mock_contact() -> Image.Image:
    w, h = S(960), S(900)
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)
    d.text((S(48), S(70)), "02 — CONTACT", font=font(MONO, 26), fill=AMBER)
    d.text((S(44), S(130)), "Hai să vorbim.", font=font(SERIF, 110), fill=FG)
    sub = text_img("6 întrebări scurte · venim pregătiți la primul apel",
                   font(SANS, 32), MUT, max_w=S(760), align="left")
    img.paste(sub, (S(28), S(300)), sub)
    # chat card
    d.rounded_rectangle((S(48), S(400), w - S(48), S(820)), radius=S(30),
                        fill=INK2, outline=BORDER, width=max(S(2), 1))
    d.ellipse((S(86), S(440), S(150), S(504)), fill=AMBER)
    d.text((S(100), S(452)), "CS", font=font(SERIF, 32), fill=INK)
    d.text((S(176), S(444)), "CopyStack", font=font(SANSB, 32), fill=FG)
    d.ellipse((S(178), S(502), S(192), S(516)), fill=GREEN)
    d.text((S(204), S(494)), "online — răspundem azi", font=font(SANS, 26), fill=GREEN)
    d.rounded_rectangle((S(86), S(560), w - S(200), S(680)), radius=S(22), fill=(28, 26, 22))
    msg = text_img("Salut! Spune-ne despre afacerea ta — durează sub un minut.",
                   font(SANS, 28), FG, max_w=S(560), align="left")
    img.paste(msg, (S(96), S(572)), msg)
    d.rounded_rectangle((S(86), S(706), S(520), S(786)), radius=S(40), fill=AMBER)
    d.text((S(126), S(726)), "Începe conversația →", font=font(SANSB, 30), fill=INK)
    return img

def scroll_clip(mock: Image.Image, t0, t1, x=None, y_from=0.18, y_to=None, chrome=True):
    """Browser-framed mock that scrolls upward over its duration."""
    card = frame_card(mock) if chrome else mock.convert("RGBA")
    c = ImageClip(np.array(card)).with_start(t0).with_duration(t1 - t0)
    px = x if x is not None else (W - card.width) // 2
    dur = t1 - t0
    yf = int(H * y_from)
    yt = y_to if y_to is not None else yf - max(card.height - int(H * 0.74), 0)
    def posf(t):
        k = min(max(t / dur, 0), 1)
        ease = k * k * (3 - 2 * k)
        return (px, yf + (yt - yf) * ease)
    return c.with_position(posf).with_effects([vfx.CrossFadeIn(0.4), vfx.CrossFadeOut(0.35)])

# ---------------------------------------------------------------- assemble
clips = [bg_clip("all", 0, DUR, glow_y=0.30), ]

# S1 — HOOK 0.0–6.5
clips += kinetic(["Nu primești mesaje sau vânzări?",
                  "Problema nu e produsul tău…",
                  "ci modul în care îl prezinți."],
                 0.2, 6.0, accent_idx=(2,), base_size=88)
banner = text_img("MARKETINGUL NU ÎNSEAMNĂ DOAR RECLAME.", font(SANSB, 40), AMBER2, max_w=S(820))
clips.append(pop(banner, 4.6, 6.5, (center_x(banner), int(H * 0.66))))

# S2 — AUTORITATE 6.5–18.5
clips.append(label("Adevărul despre AI", 6.7, 18.4))
clips += kinetic(["Toată lumea scrie texte cu AI,", "în câteva secunde."],
                 6.8, 11.2, base_size=82, y_center=0.36)
xf = font(SANSB, 46)
for i, line in enumerate(["AI nu îți cunoaște clienții",
                          "AI nu îți înțelege afacerea",
                          "AI nu știe de ce cumpără oamenii"]):
    img = Image.new("RGBA", (S(900), S(110)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((0, S(18)), "✕", font=font(SANSB, 56), fill=RED)
    d.text((S(80), S(26)), line, font=xf, fill=FG)
    clips.append(pop(img, 11.6 + i * 1.6, 18.3, (S(110), int(H * 0.40) + i * S(140))))

# S3 — WEBSITE HERO 18.5–35.5
clips.append(label("Procesul meu", 18.8, 35.4))
clips.append(scroll_clip(mock_hero(), 18.8, 35.4, y_from=0.16))
clips.append(caption("Eu folosesc AI doar ca un instrument — ca să lucrez mai rapid.", 19.0, 24.4))
clips.append(caption("Înainte să scriu un cuvânt: analizez afacerea, competiția și clientul ideal.", 24.6, 30.2))
clips.append(caption("Abia apoi construiesc mesajele care conving oamenii să cumpere.", 30.4, 35.3))

# S4 — PROCES 35.5–55.5
clips.append(label("Proces — fiecare client", 35.8, 55.4))
clips.append(scroll_clip(mock_proces(), 35.8, 55.4, y_from=0.14))
clips.append(caption("Acesta este procesul prin care trece fiecare client.", 36.0, 40.8))
clips.append(caption("Pornim de la cercetare și strategie…", 41.0, 45.3))
clips.append(caption("Continuăm cu poziționarea afacerii…", 45.5, 49.3))
clips.append(caption("Și construim texte și reclame create pentru conversii.", 49.5, 55.3))

# S5 — SERVICII 55.5–75.5
clips.append(label("Cu ce te pot ajuta", 55.8, 75.4))
slot = (75.0 - 56.0) / len(SERVICES)
for i, (title, sub) in enumerate(SERVICES):
    card = service_card(title, sub, i)
    t0 = 56.0 + i * slot
    y = int(H * 0.145) + i * S(196)
    clips.append(pop(card, t0, 75.4, ((W - card.width) // 2, y), slide=40, fade=0.35))

# S6 — DIFERENȚIERE 75.5–90.5
clips.append(label("Diferența", 75.8, 90.4))
a1 = text_img("AI generează texte.", font(SERIF, 84), FAINT, max_w=S(880))
a2 = text_img("Eu construiesc strategia\ndin spatele lor.", font(SERIF, 84), AMBER, max_w=S(880))
clips.append(pop(a1, 76.0, 82.0, (center_x(a1), int(H * 0.30))))
clips.append(pop(a2, 78.2, 84.4, (center_x(a2), int(H * 0.43))))
clips += kinetic(["AI = viteză.", "Psihologia, cercetarea, mesajul: eu."],
                 84.6, 90.4, accent_idx=(1,), base_size=78, y_center=0.40)

# S7 — CTA 90.5–100
clips.append(scroll_clip(mock_contact(), 90.7, 100.0, y_from=0.10, y_to=int(H * 0.10)))
cta = text_img("Programează un apel gratuit", font(SANSB, 46), INK, max_w=S(800))
pw, ph = cta.width + S(60), cta.height + S(8)
pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
ImageDraw.Draw(pill).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, fill=(*AMBER, 255))
pill.alpha_composite(cta, (S(30), S(4)))
clips.append(pop(pill, 91.6, 100.0, ((W - pw) // 2, int(H * 0.72)), slide=30))
url = text_img("copystack-9.polsia.app", font(MONO, 36), AMBER2)
clips.append(pop(url, 92.4, 100.0, (center_x(url), int(H * 0.80))))

clips.append(watermark(0, DUR))

video = CompositeVideoClip(clips, size=(W, H)).with_duration(DUR)

if STILLS:
    sd = OUT / "stills"; sd.mkdir(exist_ok=True)
    for name, t in [("1-hook", 3.0), ("2-autoritate", 15.0), ("3-hero", 27.0),
                    ("4-proces", 47.0), ("5-servicii", 70.0), ("6-diferenta", 80.0),
                    ("7-cta", 96.0)]:
        Image.fromarray(video.get_frame(t)).save(sd / f"{name}.png")
    print("stills →", sd)
else:
    target = OUT / ("draft.mp4" if DRAFT else "reel-copystack.mp4")
    video.write_videofile(str(target), fps=FPS, codec="libx264", audio=False,
                          preset="medium", bitrate="6000k" if not DRAFT else "2000k",
                          logger="bar")
    print("done →", target)
