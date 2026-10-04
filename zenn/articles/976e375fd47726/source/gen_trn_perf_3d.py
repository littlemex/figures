"""gen_trn_perf_3d.py — Trainium 3 世代の伸びを、指標ごとのビル群として立体で並べる図 (図の文字は英語)。

    OUT_DIR=<出力先> /usr/bin/python3 gen_trn_perf_3d.py

高さは初代 Trainium を 1 倍とした倍率。手前から奥へ Trainium, Trainium2, Trainium3。
出典 Neuron 公式ドキュメント about-neuron/arch/neuron-hardware/ (2026-10-04 取得)
- trainium.html: 190 FP16/BF16/cFP8/TF32 TFLOPS, 32 GiB
- trainium2.html: 1,299 FP8 / 667 BF16 TFLOPS, 96 GiB, 2.9 TB/sec, 1,280 GB/sec/chip
  比較表の初代の値は HBM 帯域 0.8 TB/sec, 相互接続 384 GB/sec
- trainium3.html: 2,517 MXFP8/MXFP4 / 671 BF16 TFLOPS, 144 GiB, 4.9 TB/sec, 2,560 GB/sec/chip
  比較表で MXFP4 は Trainium2 が Not applicable
- neuron-core-v3.html: cFP8 は指数の偏り (exponent bias) を調整できる
- neuron-core-v4.html: MXFP8/MXFP4 は OCP 準拠。MXFP4 は Tensor Engine の計算前に MXFP8 へ変換される
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, R, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "trainium-perf-3d.png")

YEL = (251, 211, 50)
ORG = (255, 140, 40)
BLU = (40, 150, 240)
GRN = (36, 160, 70)
PUR = (150, 100, 220)
RED = (220, 38, 88)
GRID = (52, 52, 58)

GENS = ["Trainium", "Trainium2", "Trainium3"]
# (name, unit, values per generation, colour). None = the generation has no such format.
# MXFP4 is drawn against the same baseline as FP8 (first-gen Trainium FP8 = 1x).
FP8_BASE = 190
SERIES = [
    ("FP8", "cFP8 / MXFP8", (190, 1299, 2517), YEL),
    ("MXFP4", "TFLOPS", (None, None, 2517), ORG),
    ("Chip-to-chip", "GB/s", (384, 1280, 2560), BLU),
    ("HBM bandwidth", "TB/s", (0.8, 2.9, 4.9), GRN),
    ("HBM capacity", "GiB", (32, 96, 144), PUR),
    ("BF16", "TFLOPS", (190, 667, 671), RED),
]
GEN_ALPHA = (0.42, 0.68, 1.0)

img = Image.new("RGB", (int(960 * R), int(540 * R)), BG)
g = ImageDraw.Draw(img)
XF = (1.0, 0.0, 0.0)


def P(x, y):
    return (x * R, y * R)


def ratio(vals, row):
    v = vals[row]
    if v is None:
        return None
    base = vals[0] if vals[0] is not None else FP8_BASE
    return v / base


g.text(P(50, 40), "Relative to first-generation Trainium", font=s.font(16),
       fill=MUTED, anchor="lm")
g.text(P(50, 78), "Per-chip performance", font=s.font(28),
       fill=TX, anchor="lm")

X0, BASE = 120, 452
PITCH, W, D = 120, 44, 26
STEP_X, STEP_Y = 34, 22
UNIT = 18.0
OX, OY = D * 0.9, D * 0.6


def origin(col, row):
    return X0 + col * PITCH + row * STEP_X, BASE - row * STEP_Y


ncol = len(SERIES)
fx0, fx1 = X0 - 24, X0 + (ncol - 1) * PITCH + W + 26
k = 2 + OY / STEP_Y + 0.4
bx, by = k * STEP_X, k * STEP_Y
g.polygon([P(*p) for p in [(fx0, BASE), (fx1, BASE), (fx1 + bx, BASE - by),
                           (fx0 + bx, BASE - by)]], fill=(20, 20, 24))
VTOP = 14
g.polygon([P(*p) for p in [(fx0, BASE), (fx0 + bx, BASE - by), (fx0 + bx, BASE - by - VTOP * UNIT),
                           (fx0, BASE - VTOP * UNIT)]], fill=(13, 13, 16))
g.polygon([P(*p) for p in [(fx0 + bx, BASE - by), (fx1 + bx, BASE - by),
                           (fx1 + bx, BASE - by - VTOP * UNIT), (fx0 + bx, BASE - by - VTOP * UNIT)]],
          fill=(10, 10, 12))
for v in (1, 5, 10):
    h = v * UNIT
    g.line([P(fx0, BASE - h), P(fx0 + bx, BASE - by - h), P(fx1 + bx, BASE - by - h)],
           fill=GRID, width=int(1.2 * R))
    g.text(P(fx0 - 8, BASE - h), f"{v}x", font=s.font(14), fill=MUTED, anchor="rm")
g.line([P(fx0, BASE), P(fx0, BASE - VTOP * UNIT)], fill=GRID, width=int(1.2 * R))
for row in range(3):
    x, y = origin(0, row)
    g.text(P(fx1 + row * STEP_X + 8, y), GENS[row], font=s.font(13),
           fill=mix(BG, TX, GEN_ALPHA[row]), anchor="lm")

# Back row first so the front row hides it. A missing format leaves a dashed footprint.
for row in (2, 1, 0):
    for col, (name, unit, vals, c) in enumerate(SERIES):
        x, y = origin(col, row)
        r = ratio(vals, row)
        if r is None:
            fp = [(x, y), (x + W, y), (x + W + OX, y - OY), (x + OX, y - OY), (x, y)]
            for a_, b_ in zip(fp, fp[1:]):
                n = 6
                for i in range(0, n, 2):
                    p0 = (a_[0] + (b_[0] - a_[0]) * i / n, a_[1] + (b_[1] - a_[1]) * i / n)
                    p1 = (a_[0] + (b_[0] - a_[0]) * (i + 1) / n,
                          a_[1] + (b_[1] - a_[1]) * (i + 1) / n)
                    g.line([P(*p0), P(*p1)], fill=mix(BG, c, 0.55 * GEN_ALPHA[row]),
                           width=int(1.4 * R))
            continue
        h = r * UNIT
        s.box(g, XF, x, y - h, W, h, D, c, a=GEN_ALPHA[row])

# Trainium2 multiple on the front face of its bar
for col, (name, unit, vals, c) in enumerate(SERIES):
    r = ratio(vals, 1)
    if r is None:
        continue
    x, y = origin(col, 1)
    g.text(P(x + W / 2, y - r * UNIT + 12), f"{r:.1f}x", font=s.font(13), fill=TX,
           anchor="mm")

# Trainium3 multiple on top of the back bar. MXFP4 is new, so it gets a NEW tag instead.
for col, (name, unit, vals, c) in enumerate(SERIES):
    r = ratio(vals, 2)
    x, y = origin(col, 2)
    top = y - r * UNIT - OY
    label = "NEW" if vals[0] is None else f"{r:.1f}x"
    g.text(P(x + W / 2 + OX / 2, top - 16), label, font=s.font(20), fill=c, anchor="mm")

for col, (name, unit, vals, c) in enumerate(SERIES):
    x, _ = origin(col, 0)
    cx = x + W / 2 + 16
    g.text(P(cx, BASE + 26), name, font=s.font(15), fill=c, anchor="mm")
    g.text(P(cx, BASE + 46), unit, font=s.font(12), fill=MUTED, anchor="mm")

img.save(OUT)
print(OUT)
