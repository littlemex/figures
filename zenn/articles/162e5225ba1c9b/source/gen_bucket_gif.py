"""gen_bucket_gif.py -- Mamba2 の状態 h を「少しずつ漏れるバケツ」として見せ、chunked SSD の青いマスが
バケツの水位 1 つで済む理由を、記号を使わずに具体的な数で追う GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_bucket_gif.py

例: 毎ステップ水が半分に減り (a = 0.5)、入力 x をそのまま注ぐ (b = 1)、水位をそのまま読む (c = 1)。
入力は x1..x3 = 8, 4, 2、x4..x6 = 0 (2 つ目の塊の新しい入力は省き、古い水だけを追う)。
1. バケツ: 半分に減る -> 注ぐ -> 読む
2. 読んだ値の中身: どの入力がどれだけ残っているか -> 階段の 1 行
3. 階段: 時刻 i は入力 1..i だけを含む
4. 青: 1 つ目の塊の水が 2 つ目の塊の出力に残っている分
5. 塊の終わりのバケツ (6) を渡せば、色ごとに追わなくても同じ値
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
OUT = os.path.join(OUT_DIR, "bucket.gif")
SC = 4 / 3
FPS = 2                       # slow on purpose: one change per frame
COL = [(240, 110, 150), (60, 200, 170), (240, 190, 60)]   # x1, x2, x3
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL = (251, 211, 50)
DIM = (46, 50, 56)
X = [8, 4, 2]


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def layers_at(t):
    """amount of x1..x3 left in the bucket after step t (t = 1..6)."""
    out = []
    for j in range(3):
        if t < j + 1:
            out.append(0.0)
        else:
            out.append(X[j] * 0.7 ** (t - (j + 1)))
    return out


def bucket(g, x, y, lay, label=None, scale=14.0):
    W, H = 150, 230
    g.rectangle([P(x, y), P(x + W, y + H)], outline=MUTED, width=int(3 * SC))
    top = y + H
    for j, v in enumerate(lay):
        if v <= 0:
            continue
        h = v * scale
        g.rectangle([P(x + 3, top - h), P(x + W - 3, top)], fill=COL[j])
        top -= h
    if label:
        g.text(P(x + W / 2, y - 18), label, font=F(15), fill=MUTED, anchor="mm")


def hatch(g, x0, y0, w, h, col=(200, 205, 210), step=9):
    """thin diagonal lines so the cell is told apart without color."""
    for k in range(-int(h), int(w), step):
        xa, ya = max(x0, x0 + k), y0 + max(0, -k)
        xb, yb = min(x0 + w, x0 + k + h), y0 + min(h, w - k)
        if xb > xa:
            g.line([P(xa, ya), P(xb, yb)], fill=col, width=int(1 * SC))


def grid(g, upto_row, show_blue=False, hl_row=None, ox=470, oy=150, C=58):
    for i in range(1, 7):
        g.text(P(ox - 26, oy + (i - 1) * C + 27), f"y{i}", font=F(14), fill=MUTED, anchor="mm")
        g.text(P(ox + (i - 1) * C + 27, oy - 16), f"x{i}", font=F(14), fill=MUTED, anchor="mm")
        for j in range(1, 7):
            x0, y0 = ox + (j - 1) * C, oy + (i - 1) * C
            on = i <= upto_row and j <= i
            blue = show_blue and i >= 4 and j <= 3
            fill = BG
            out = DIM
            txt = None
            if on and j <= 3:
                fill = mix(BG, COL[j - 1], 0.85 * 0.7 ** (i - j) + 0.1)
                out = COL[j - 1]
            elif on:
                fill, out = GRN_DK, DIM
            if blue:
                out = YEL if hl_row == i else BLU
            g.rectangle([P(x0, y0), P(x0 + C - 4, y0 + C - 4)], fill=fill, outline=out,
                        width=int((3 if blue else 1) * SC))
            if blue:
                hatch(g, x0 + 2, y0 + 2, C - 8, C - 8)
            if txt:
                g.text(P(x0 + (C - 4) / 2, y0 + (C - 4) / 2), txt, font=F(14), fill=TX, anchor="mm")
    g.line([P(ox - 6, oy + 3 * C - 2), P(ox + 6 * C, oy + 3 * C - 2)], fill=MUTED, width=int(1 * SC))
    g.line([P(ox + 3 * C - 2, oy - 6), P(ox + 3 * C - 2, oy + 6 * C)], fill=MUTED, width=int(1 * SC))


def canvas(cap):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 50), cap, font=F(26), fill=YEL, anchor="lm")
    return img, g


frames = []


def hold(img, n):
    frames.extend([img] * n)


# 1. the bucket rule: leak, pour, read
for k in range(1, 4):
    prev = layers_at(k - 1) if k > 1 else [0, 0, 0]
    img, g = canvas("leak a little")
    bucket(g, 100, 140, [v * 0.7 for v in prev])
    hold(img, 3)
    img, g = canvas(f"pour in x{k}")
    bucket(g, 100, 140, layers_at(k))
    hold(img, 3)
    img, g = canvas(f"read the level: y{k}")
    bucket(g, 100, 140, layers_at(k))
    hold(img, 3)

# 2. staircase
for r in range(1, 7):
    img, g = canvas("each row: what is left")
    bucket(g, 100, 140, layers_at(r))
    grid(g, r)
    hold(img, 3)
img, g = canvas("a staircase")
bucket(g, 100, 140, layers_at(6))
grid(g, 6)
hold(img, 6)

# 3. blue
img, g = canvas("hatched: chunk 1 left in chunk 2")
bucket(g, 100, 140, layers_at(3))
grid(g, 6, show_blue=True)
hold(img, 8)

# 4. the bucket at the end of chunk 1 is h3
img, g = canvas("this bucket is h3")
bucket(g, 100, 140, layers_at(3))
g.text(P(175, 405), "h3", font=F(30), fill=YEL, anchor="mm")
grid(g, 6, show_blue=True)
hold(img, 8)

# 5. each blue row = h3 after more leaking; the colors fade together
for k in range(4, 7):
    n = k - 3
    img, g = canvas(f"row y{k} = h3 leaked {n}x")
    bucket(g, 100, 140, layers_at(k))
    g.text(P(175, 405), "h3 \u00d7 leak" + ("" if n == 1 else "\u00b2" if n == 2 else "\u00b3"), font=F(20), fill=YEL, anchor="mm")
    grid(g, 6, show_blue=True, hl_row=k)
    oy, C = 150, 58
    g.line([P(255, 300), P(428, oy + (k - 1) * C + 27)], fill=YEL, width=int(3 * SC))
    hold(img, 6)

img, g = canvas("so pass h3, not 9 cells")
bucket(g, 100, 140, layers_at(3))
g.text(P(175, 405), "h3", font=F(30), fill=YEL, anchor="mm")
grid(g, 6, show_blue=True)
hold(img, 10)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    seen = []
    for k, fr in enumerate(frames):
        if not seen or fr is not seen[-1]:
            seen.append(fr)
    for k, fr in enumerate(seen):
        fr.save(os.path.join(OUT_DIR, f"b{k:02d}.png"))
    print("scenes", len(seen))
