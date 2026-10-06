"""gen_nki_pptx.py -- NemotronH 記事の「NKI カーネルで速くする」の図を、1 枚に 1 つの考え方だけで描き直す。

    /usr/bin/python3 gen_nki_pptx.py <out.pptx>

1. decode の速さの変化 (棒だけ)
2. 4 本に共通の 2 つの考え方: 2 コアで分けて話さない / 小さな転送をまとめる
3. Mamba2 decode: 1 件ずつ -> 全リクエストを 1 枚に
4. SSD prefill: 128 トークンの塊ごとの三角形 + 状態を渡す
5. MoE decode: 128 個のうち選ばれた 6 個だけ運ぶ
6. matvec: x を計算器に固定し、重みを流し込む
図の文字は英語、最小限。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "nki-figures.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
BLU = RGBColor(40, 150, 240)
BLU_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
RED = RGBColor(220, 38, 88)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=18, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align, anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=18, color=WHITE, sw=1.5, radius=0.12):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
    return sp


def sq(s, x, y, w, h, fill, stroke=None, sw=1.0):
    return sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw)


def arrow(s, x1, y1, x2, y2, color=WHITE, w=2.5):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=w)


def title(s, head):
    label(s, 43, 30, 1190, 50, head, size=32, bold=True, align="left")


def panel_titles(s, left, right, y=110):
    label(s, 43, y, 560, 36, left, size=22, color=MUTED)
    label(s, 677, y, 560, 36, right, size=22, color=GRN_HI)


# 1. decode time
s = d.slide().s
title(s, "Decode: 72.5 ms -> 9.0 ms per token")
bars = [("start", 72.5, GREY), ("6 experts only", 14.0, GRN), ("attention", 12.8, GRN),
        ("MoE kernel", 12.6, GREY), ("Mamba2 kernel", 10.0, GRN), ("matvec kernel", 9.0, GRN)]
for k, (name, v, col) in enumerate(bars):
    y = 130 + k * 78
    label(s, 43, y, 300, 56, name, size=20, align="left", color=WHITE if col == GRN or k == 0 else MUTED)
    sq(s, 360, y + 8, 780 * v / 72.5, 40, col)
    label(s, 360 + 780 * v / 72.5 + 12, y, 140, 56, f"{v:g} ms", size=20, align="left",
          color=GRN_HI if col == GRN else MUTED)

# 2. two shared ideas
s = d.slide().s
title(s, "Two ideas behind all four kernels")
label(s, 43, 110, 560, 36, "1. split over 2 cores, no talking", size=22, color=GRN_HI)
for k in range(2):
    x = 63 + k * 280
    box(s, x, 170, 240, 220, GRN_DK, GRN_HI)
    label(s, x, 180, 240, 40, f"core {k}", size=22, bold=True)
    for r in range(3):
        sq(s, x + 40, 250 + r * 40, 160, 28, BLU_DK, BLU)
label(s, 43, 410, 560, 36, "no arrow between them", size=18, color=MUTED)
label(s, 677, 110, 560, 36, "2. few big transfers", size=22, color=GRN_HI)
label(s, 677, 160, 260, 30, "before", size=18, color=MUTED)
for r in range(8):
    arrow(s, 697, 200 + r * 22, 897, 200 + r * 22, color=RED, w=1.5)
label(s, 957, 160, 260, 30, "after", size=18, color=GRN_HI)
arrow(s, 977, 280, 1197, 280, color=GRN_HI, w=14)

# 3. Mamba2 decode
s = d.slide().s
title(s, "Mamba2 decode: all requests in one tile")
panel_titles(s, "before: one request at a time", "after: one tile")
for r in range(8):
    y = 170 + r * 50
    box(s, 63, y, 120, 38, BLU_DK, BLU, f"r{r}", size=16)
    arrow(s, 183, y + 19, 263, y + 19, color=RED, w=1.5)
    sq(s, 263, y, 300, 38, GREY, EDGE)
box(s, 697, 170, 150, 390, BLU_DK, BLU, "r0 ... r7", size=18)
arrow(s, 847, 365, 917, 365, color=GRN_HI, w=10)
for r in range(8):
    for c in range(6):
        sq(s, 927 + c * 48, 170 + r * 49, 44, 45, GRN_DK, GRN_HI)
label(s, 677, 580, 560, 36, "9.0 ms -> 3.0 ms (Mamba2 part, 8 requests)", size=18, color=YEL)

# 4. SSD prefill
s = d.slide().s
title(s, "SSD prefill: one triangle per 128 tokens")
for k in range(4):
    x = 63 + k * 290
    tri = sh.rect(s, t, x, 200, 220, 220, fill=GRN_DK, stroke=GRN_HI, sw=1.5, shape=MSO_SHAPE.RIGHT_TRIANGLE)
    label(s, x, 430, 220, 30, f"tokens {k*128}-{k*128+127}", size=15, color=MUTED)
    if k < 3:
        arrow(s, x + 225, 300, x + 285, 300, color=YEL, w=6)
        label(s, x + 225, 255, 60, 36, "h", size=24, bold=True, color=YEL)
label(s, 43, 520, 1190, 40, "about 800 -> 2,600 tokens/s", size=22, color=YEL)

# 5. MoE decode
s = d.slide().s
title(s, "MoE decode: move only the 6 chosen experts")
picked = {5, 19, 40, 77, 101, 120}
for e in range(128):
    r, c = divmod(e, 16)
    on = e in picked
    sq(s, 63 + c * 44, 140 + r * 44, 38, 38, YEL_DK if on else CHIP, YEL if on else EDGE, sw=2 if on else 1)
box(s, 907, 250, 290, 160, GRN_DK, GRN_HI, "on-chip memory", size=20)
for k, e in enumerate(sorted(picked)):
    r, c = divmod(e, 16)
    arrow(s, 63 + c * 44 + 38, 140 + r * 44 + 19, 907, 280 + k * 20, color=YEL, w=1.5)
label(s, 63, 510, 700, 36, "128 experts, 6 used per token", size=18, color=MUTED)

# 6. matvec
s = d.slide().s
title(s, "matvec: keep x in the engine, stream the weights")
panel_titles(s, "usual: reload weights, tiny work", "here: x stays, weights flow")
box(s, 133, 230, 300, 200, CHIP, EDGE, "", size=18)
label(s, 133, 230, 300, 40, "engine", size=18, color=MUTED)
for k in range(4):
    sq(s, 163 + k * 64, 290, 50, 110, GREY, EDGE)
label(s, 133, 450, 300, 30, "load, compute 1 token, reload", size=16, color=MUTED)
box(s, 767, 230, 300, 200, CHIP, GRN_HI, "", size=18)
label(s, 767, 230, 300, 40, "engine", size=18, color=MUTED)
box(s, 787, 300, 90, 100, YEL_DK, YEL, "x", size=26)
for k in range(3):
    sq(s, 907 + k * 50, 300, 36, 100, BLU_DK, BLU)
arrow(s, 1077, 350, 1217, 350, color=BLU, w=8)
label(s, 767, 450, 450, 30, "10.0 ms -> 9.0 ms", size=18, color=YEL)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
