#!/usr/bin/env python3
"""Generate the five 1080x1920 scene cards with PIL (offline stand-in for
Ideogram 4 — same palette as config.json). Run from the project directory:

    python3 gen_cards.py
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
P = CONFIG["palette"]
W, H = 1080, 1920

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_BOOK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Ken Burns zooms up to 7%; captions sit at y=1640. Keep content inside.
SAFE_TOP, SAFE_BOTTOM = 300, 1450


def rgb(hex_color):
    return tuple(int(hex_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def font(size, book=False):
    return ImageFont.truetype(FONT_BOOK if book else FONT, size)


def base_card(accent_hex, glow_pos=(0.5, 0.18)):
    """Dark ink background with a soft accent glow and faint grid."""
    ink, acc = rgb(P["ink"]), rgb(accent_hex)
    img = Image.new("RGB", (W, H), ink)
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gx, gy, r = int(W * glow_pos[0]), int(H * glow_pos[1]), 620
    gd.ellipse((gx - r, gy - r, gx + r, gy + r), fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    tint = Image.new("RGB", (W, H), acc)
    img = Image.composite(tint, img, glow)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=tuple(min(255, c + 6) for c in ink))
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=tuple(min(255, c + 6) for c in ink))
    return img


def kicker(d, text, y, accent_hex):
    """Small all-caps label pill centered at y. Returns bottom y."""
    f = font(40)
    t = text.upper()
    bbox = d.textbbox((0, 0), t, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 36, 22
    x0 = (W - tw) / 2 - pad_x
    d.rounded_rectangle((x0, y, x0 + tw + 2 * pad_x, y + th + 2 * pad_y),
                        radius=(th + 2 * pad_y) // 2, outline=rgb(accent_hex), width=4)
    d.text(((W - tw) / 2 - bbox[0], y + pad_y - bbox[1]), t, font=f, fill=rgb(accent_hex))
    return y + th + 2 * pad_y


def centered_lines(d, lines, y, sizes, fills, gap=26, tracking=0):
    """Draw centered lines; lines[i] uses sizes[i]/fills[i]. Returns bottom y."""
    for line, size, fill in zip(lines, sizes, fills):
        f = font(size)
        bbox = d.textbbox((0, 0), line, font=f)
        d.text(((W - bbox[2] + bbox[0]) / 2 - bbox[0], y - bbox[1]), line,
               font=f, fill=rgb(fill) if isinstance(fill, str) else fill)
        y += (bbox[3] - bbox[1]) + gap
    return y


def progress_dots(d, idx, total=5):
    y = H - 120
    r, gap = 10, 44
    x0 = (W - (total - 1) * gap) / 2
    for i in range(total):
        x = x0 + i * gap
        c = rgb(P["accent2"]) if i == idx else rgb(P["slate"])
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)


def card_01():
    img = base_card(P["accent1"])
    d = ImageDraw.Draw(img)
    y = kicker(d, "Copywriting · Ads", SAFE_TOP + 40, P["accent2"]) + 90
    f_huge = font(330)
    t = "3"
    bbox = d.textbbox((0, 0), t, font=f_huge)
    d.text(((W - bbox[2] + bbox[0]) / 2 - bbox[0], y - bbox[1]), t,
           font=f_huge, fill=rgb(P["warn"]))
    y += (bbox[3] - bbox[1]) + 60
    y = centered_lines(d, ["GREȘELI"], y, [150], [P["white"]], gap=40)
    y += 30
    y = centered_lines(d, ["care fac o reclamă", "să piardă bani"], y,
                       [78, 78], [P["slate"], P["slate"]], gap=22)
    progress_dots(d, 0)
    return img


def card_02():
    img = base_card(P["accent2"], glow_pos=(0.5, 0.12))
    d = ImageDraw.Draw(img)
    y = kicker(d, "Problema reală", SAFE_TOP + 20, P["warn"]) + 80
    items = [("1", "OFERTA"), ("2", "PAGINA DE\nDESTINAȚIE"), ("3", "MESAJ\nGENERIC")]
    box_h, gap = 300, 50
    for n, label in items:
        x0, x1 = 90, W - 90
        d.rounded_rectangle((x0, y, x1, y + box_h), radius=40,
                            fill=tuple(min(255, c + 14) for c in rgb(P["ink"])),
                            outline=rgb(P["accent2"]), width=3)
        f_num = font(150)
        d.text((x0 + 70, y + (box_h - 150) / 2 - 20), n, font=f_num, fill=rgb(P["warn"]))
        f_lab = font(72)
        lines = label.split("\n")
        total_h = sum(d.textbbox((0, 0), l, font=f_lab)[3] for l in lines) + 14 * (len(lines) - 1)
        ly = y + (box_h - total_h) / 2
        for l in lines:
            bbox = d.textbbox((0, 0), l, font=f_lab)
            d.text((x0 + 260, ly - bbox[1]), l, font=f_lab, fill=rgb(P["white"]))
            ly += (bbox[3] - bbox[1]) + 14
        y += box_h + gap
    progress_dots(d, 1)
    return img


def card_03():
    img = base_card(P["warn"], glow_pos=(0.5, 0.15))
    d = ImageDraw.Draw(img)
    y = kicker(d, "Exemplu · Cursuri de engleză", SAFE_TOP + 20, P["accent2"]) + 90
    # mock generic ad
    x0, x1 = 90, W - 90
    box_h = 460
    d.rounded_rectangle((x0, y, x1, y + box_h), radius=40,
                        fill=tuple(min(255, c + 14) for c in rgb(P["ink"])),
                        outline=rgb(P["slate"]), width=3)
    d.rounded_rectangle((x0 + 50, y + 60, x0 + 330, y + 110), radius=20, fill=rgb(P["slate"]))
    d.rounded_rectangle((x0 + 50, y + 140, x1 - 200, y + 175), radius=16,
                        fill=tuple(min(255, c + 40) for c in rgb(P["ink"])))
    yy = centered_lines(d, ["„Învață engleză", "rapid.”"], y + 230, [88, 88],
                        [P["white"], P["white"]], gap=18)
    # red X stamp over the ad
    cx, cy, r = x1 - 140, y + 120, 85
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb(P["warn"]))
    lw = 18
    d.line((cx - 38, cy - 38, cx + 38, cy + 38), fill=rgb(P["white"]), width=lw)
    d.line((cx - 38, cy + 38, cx + 38, cy - 38), fill=rgb(P["white"]), width=lw)
    y += box_h + 110
    centered_lines(d, ["La fel ca alte", "1.000 de școli."], y, [96, 96],
                   [P["warn"], P["warn"]], gap=20)
    progress_dots(d, 2)
    return img


def card_04():
    img = base_card(P["accent2"], glow_pos=(0.5, 0.15))
    d = ImageDraw.Draw(img)
    y = kicker(d, "Mesaj concret", SAFE_TOP + 20, P["accent2"]) + 90
    x0, x1 = 90, W - 90
    box_h = 640
    d.rounded_rectangle((x0, y, x1, y + box_h), radius=40,
                        fill=tuple(min(255, c + 14) for c in rgb(P["ink"])),
                        outline=rgb(P["accent2"]), width=4)
    yy = centered_lines(
        d,
        ["„Conversații", "simple în engleză", "după primele", "30 de zile.”"],
        y + 90, [82, 82, 82, 110],
        [P["white"], P["white"], P["white"], P["accent2"]], gap=24)
    # check badge
    cx, cy, r = x1 - 140, y - 10, 85
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb(P["accent2"]))
    d.line((cx - 42, cy + 2, cx - 10, cy + 36), fill=rgb(P["ink"]), width=20)
    d.line((cx - 10, cy + 36, cx + 44, cy - 30), fill=rgb(P["ink"]), width=20)
    y += box_h + 100
    centered_lines(d, ["UN REZULTAT", "CONCRET"], y, [104, 104],
                   [P["white"], P["accent2"]], gap=20)
    progress_dots(d, 3)
    return img


def card_05():
    img = base_card(P["accent1"], glow_pos=(0.5, 0.2))
    d = ImageDraw.Draw(img)
    y = kicker(d, "Pe scurt", SAFE_TOP + 60, P["accent2"]) + 110
    y = centered_lines(d, ["Înainte să schimbi", "reclama,"], y, [88, 88],
                       [P["slate"], P["slate"]], gap=20)
    y += 50
    y = centered_lines(d, ["UITĂ-TE", "LA MESAJ."], y, [150, 150],
                       [P["white"], P["accent2"]], gap=28)
    # arrow down to the caption zone
    y += 70
    cx = W / 2
    d.line((cx, y, cx, y + 110), fill=rgb(P["warn"]), width=16)
    d.polygon([(cx - 34, y + 100), (cx + 34, y + 100), (cx, y + 160)], fill=rgb(P["warn"]))
    progress_dots(d, 4)
    return img


if __name__ == "__main__":
    out = HERE / "images"
    out.mkdir(exist_ok=True)
    for name, fn in [("01_hook", card_01), ("02_greseli", card_02),
                     ("03_exemplu", card_03), ("04_mesaj_concret", card_04),
                     ("05_cta", card_05)]:
        fn().save(out / f"{name}.png")
        print("wrote", out / f"{name}.png")
