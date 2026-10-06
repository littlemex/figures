"""gen_h3_block_gif.py -- 青い 9 マスが「h3 の中の各入力の分 × 2 つ目の塊の減衰」だけでできていることを、具体的な数と色で見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_h3_block_gif.py

例: 入力 x1..x3 = 16, 6, 1、毎ステップの減衰 a = 0.5、b = c = 1。
h3 = 8 の中身は x1 の分 4、x2 の分 3、x3 の分 1。
y4 の行 = 各分 x a4、y5 の行 = 各分 x a4 x a5、y6 の行 = 各分 x a4 x a5 x a6。
図の文字は英語。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "h3-block.gif")
SC = 4 / 3
FPS = 2
COL = [(240, 110, 150), (60, 200, 170), (240, 190, 60)]       # x1, x2, x3
DEC = {4: (255, 235, 90), 5: (255, 160, 60), 6: (230, 90, 230)}  # a4, a5, a6
BLU = (40, 150, 240)
DIM = (46, 50, 56)
PART = [4, 3, 1]          # what is left of x1, x2, x3 in h3 (16*0.25, 6*0.5, 1)


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def runs(g, x, y, parts, size=18, anchor="lm"):
    """draw [(text, color), ...] left to right."""
    f = F(size)
    if anchor == "mm":
        w = sum(g.textlength(t, font=f) for t, _ in parts) / SC
        x -= w / 2
    for t, c in parts:
        g.text(P(x, y), t, font=f, fill=c, anchor="lm")
        x += g.textlength(t, font=f) / SC


def h3_bucket(g, glow=None):
    x, y, W, H = 40, 140, 150, 272
    g.rectangle([P(x, y), P(x + W, y + H)], outline=MUTED, width=int(3 * SC))
    top = y + H
    for j in range(3):
        h = PART[j] * 33
        on = glow is None or glow == j
        g.rectangle([P(x + 3, top - h), P(x + W - 3, top)], fill=COL[j] if on else mix(BG, COL[j], 0.35))
        g.text(P(x + W / 2, top - h / 2), f"x{j+1}: {PART[j]:g}", font=F(18), fill=(15, 15, 15), anchor="mm")
        top -= h
    runs(g, x + W / 2, y + H + 30, [(f"h3 = {sum(PART):g}", TX)], size=22, anchor="mm")


def hatch(g, x0, y0, w, h, col=(70, 76, 84), step=12):
    for k in range(-int(h), int(w), step):
        xa, ya = max(x0, x0 + k), y0 + max(0, -k)
        xb, yb = min(x0 + w, x0 + k + h), y0 + min(h, w - k)
        if xb > xa:
            g.line([P(xa, ya), P(xb, yb)], fill=col, width=int(1 * SC))


def block(g, upto, hl_row=None, hl_col=None):
    ox, oy, C = 280, 150, 215
    for jj in range(3):
        g.text(P(ox + jj * C + C / 2 - 4, oy - 18), f"x{jj+1}", font=F(16), fill=COL[jj], anchor="mm")
    for r, i in enumerate((4, 5, 6)):
        g.text(P(ox - 24, oy + r * 80 + 38), f"y{i}", font=F(16), fill=MUTED, anchor="mm")
        for jj in range(3):
            x0, y0 = ox + jj * C, oy + r * 80
            on = i <= upto
            hl = hl_row == i or hl_col == jj
            g.rectangle([P(x0, y0), P(x0 + C - 8, y0 + 72)], fill=BG,
                        outline=(255, 255, 255) if hl else BLU, width=int((3 if hl else 2) * SC))
            pass  # all nine cells are the same kind here, so no hatch (it would only add noise)
            if not on:
                continue
            dim = hl_col is not None and hl_col != jj
            parts = [(f"{PART[jj]:g}", mix(BG, COL[jj], 0.3) if dim else COL[jj])]
            for k in range(4, i + 1):
                parts += [(" \u00d7 ", DIM if dim else TX), (f"a{k}", mix(BG, DEC[k], 0.3) if dim else DEC[k])]
            runs(g, x0 + (C - 8) / 2, y0 + 24, parts, size=16 if i < 6 else 13, anchor="mm")
            g.text(P(x0 + (C - 8) / 2, y0 + 52), f"= {PART[jj] * 0.5 ** (i - 3):g}", font=F(15), fill=MUTED, anchor="mm")


def canvas(cap):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 50), cap, font=F(26), fill=(251, 211, 50), anchor="lm")
    g.text(P(40, 92), "x = 16, 6, 1   a = 0.5", font=F(15), fill=MUTED, anchor="lm")
    return img, g


frames = []


def hold(img, n):
    frames.extend([img] * n)


img, g = canvas("inside h3")
h3_bucket(g)
block(g, 3)
hold(img, 8)

for i in (4, 5, 6):
    img, g = canvas(f"row y{i}")
    h3_bucket(g)
    block(g, i, hl_row=i)
    parts = [("sum = ", TX), ("h3", TX)]
    for k in range(4, i + 1):
        parts += [(" \u00d7 ", TX), (f"a{k}", DEC[k])]
    parts += [(f" = {sum(PART) * 0.5 ** (i - 3):g}", MUTED)]
    runs(g, 280, 420 + 0, parts, size=18)
    hold(img, 8)

img, g = canvas("x1 column")
h3_bucket(g, glow=0)
block(g, 6, hl_col=0)
runs(g, 280, 420, [("4", COL[0]), (" \u00d7 ", TX), ("a4", DEC[4]), (" \u00d7 ", TX), ("a5", DEC[5]), (" \u00d7 ", TX), ("a6", DEC[6])], size=18)
hold(img, 10)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    seen = []
    for fr in frames:
        if not seen or fr is not seen[-1]:
            seen.append(fr)
    for k, fr in enumerate(seen):
        fr.save(os.path.join(OUT_DIR, f"h{k}.png"))
