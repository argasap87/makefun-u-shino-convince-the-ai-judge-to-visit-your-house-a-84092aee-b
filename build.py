#!/usr/bin/env python3
"""Build entry.png for the Shino 'Convince the AI Judge' letter bounty.

Layout (1024x1024): AI-generated cozy-room header on top, then the letter
itself on a cream paper panel below, typeset big enough to read at 300px.
Regenerating is deterministic: same header asset + same text = same PNG.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1024, 1024
HEADER_H = 320
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"

INK = (43, 33, 24)
RED = (139, 46, 46)
GOLD = (176, 141, 87)
PAPER = (255, 248, 231)
CREAM = (247, 234, 210)

TITLE = "You're Invited!"
GREETING = "Dear AI Judge,"
BODY = [
    "You're invited to my house for a \u2018Comfort & Cookies\u2019 evening \u2014 Saturday, 7 pm. No compute credits required.",
    "The lure: grandma's oatmeal-raisin cookies, still warm, frosting piped like tiny circuits. Plus the comfiest chair in the house \u2014 real springs, zero algorithms \u2014 and a garden window that blooms at 2 a.m.",
    "I know you can't literally swing by, so take this as a warm wink: the only thing I'll ask you to optimise is how long a cookie stays crisp.",
]
SIGN = "Warmly, Your Host"
PS = "P.S. Haiku RSVP optional \u2014 the cat already approved you."


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_cookie(draw, cx, cy, r):
    """Small oatmeal-raisin cookie doodle: golden disc, darker chips."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(198, 142, 78),
                 outline=(120, 72, 32), width=3)
    for dx, dy, cr in [(-r // 2, -r // 4, 5), (r // 3, -r // 2, 4),
                       (0, r // 3, 5), (r // 2, r // 4, 4), (-r // 4, r // 2, 4)]:
        draw.ellipse([cx + dx - cr, cy + dy - cr, cx + dx + cr, cy + dy + cr],
                     fill=(90, 52, 20))


def wrap_pixels(draw, text, fnt, max_w):
    """Wrap text to pixel width using real measurements."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def layout_heights(draw, body_size):
    """Measure the whole letter at a body font size; return (lines, total_h)."""
    f_title = font(SERIF_BOLD, 58)
    f_greet = font(SERIF_BOLD, 36)
    f_body = font(SERIF, body_size)
    f_sign = font(SERIF_ITALIC, 32)
    f_ps = font(SERIF_ITALIC, 27)
    max_w = W - 2 * 26 - 110
    paras = [wrap_pixels(draw, p, f_body, max_w) for p in BODY]
    lh = int(body_size * 1.42)
    total = 34 + 78 + 26 + 56  # top pad + title + rule gap + greeting
    for lines in paras:
        total += len(lines) * lh + 14
    total += 6 + 44 + 52  # sign gap + sign + ps
    return paras, total, lh


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # --- header: AI-generated cozy room, cropped to drop the watermark ---
    header = Image.open("assets/header.png").convert("RGB")
    header = ImageEnhance.Brightness(header).enhance(1.12)
    header = ImageEnhance.Color(header).enhance(1.08)
    # crop bottom strip (watermark) then resize to 1024x320
    header = header.crop((0, 0, header.width, header.height - 48))
    header = header.resize((W, HEADER_H), Image.LANCZOS)
    img.paste(header, (0, 0))
    draw.line([(0, HEADER_H), (W, HEADER_H)], fill=GOLD, width=4)
    draw.line([(0, HEADER_H + 6), (W, HEADER_H + 6)], fill=GOLD, width=2)

    # --- paper panel ---
    margin = 26
    top = HEADER_H + 18
    draw.rounded_rectangle([margin, top, W - margin, H - margin],
                           radius=18, fill=PAPER, outline=GOLD, width=3)
    inner = ImageDraw.Draw(img)
    inner.rounded_rectangle([margin + 10, top + 10, W - margin - 10, H - margin - 10],
                            radius=12, outline=(212, 186, 138), width=1)

    # shrink body font until the whole letter fits the panel
    avail = (H - margin - 10) - (top + 10)
    body_size = 31
    while body_size > 22:
        paras, total, lh = layout_heights(draw, body_size)
        if total <= avail - 16:
            break
        body_size -= 1
    print("body font size:", body_size, "letter height:", total, "avail:", avail)

    cx = W // 2
    y = top + 34
    f_title = font(SERIF_BOLD, 58)
    draw.text((cx, y), TITLE, font=f_title, fill=RED, anchor="ma")
    y += 78
    draw.line([(cx - 180, y), (cx + 180, y)], fill=GOLD, width=2)
    y += 26

    f_greet = font(SERIF_BOLD, 36)
    draw.text((cx, y), GREETING, font=f_greet, fill=INK, anchor="ma")
    y += 56

    f_body = font(SERIF, body_size)
    for lines in paras:
        for line in lines:
            draw.text((cx, y), line, font=f_body, fill=INK, anchor="ma")
            y += lh
        y += 14

    y += 6
    f_sign = font(SERIF_ITALIC, 32)
    draw.text((cx, y), SIGN, font=f_sign, fill=INK, anchor="ma")
    y += 52
    f_ps = font(SERIF_ITALIC, 27)
    draw.text((cx, y), PS, font=f_ps, fill=(90, 60, 40), anchor="ma")

    # cookie doodle bottom-left of the paper, clear of the centred text
    draw_cookie(draw, margin + 72, H - margin - 58, 30)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
