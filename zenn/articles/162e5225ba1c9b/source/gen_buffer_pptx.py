"""gen_buffer_pptx.py -- NemotronH の Mamba2 の状態をモジュールのバッファとして持つ仕組みの図 (1 枚)。

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


s = d.slide().s
title(s, "Mamba2 state: buffers inside the model")
# module
box(s, 43, 110, 560, 470, CHIP, EDGE, radius=0.04)
label(s, 63, 118, 520, 36, "Mamba2 layer  (nn.Module)", size=20, bold=True, align="left")
box(s, 73, 170, 500, 90, GREY, EDGE, "parameters: weights\n(load_weights)", size=17)
box(s, 73, 290, 500, 270, GRN_DK, GRN_HI, radius=0.05)
label(s, 93, 296, 460, 36, "buffers  (register_buffer)", size=18, bold=True, color=GRN_HI, align="left")
for k in range(5):
    y = 345 + k * 40
    on = k in (1, 3)
    sq(s, 103, y, 440, 32, YEL_DK if on else BLU_DK, YEL if on else BLU, sw=2 if on else 1)
    label(s, 103, y, 440, 32, f"row {k}" + ("   request A" if k == 1 else "   request B" if k == 3 else ""), size=14,
          color=WHITE if on else MUTED)
# step
steps = [("1  find my row", CHIP, EDGE), ("2  read the row", BLU_DK, BLU), ("3  compute", CHIP, EDGE),
         ("4  write the row back", YEL_DK, YEL)]
for k, (txt, f, st) in enumerate(steps):
    box(s, 727, 140 + k * 100, 460, 70, f, st, txt, size=18)
    if k:
        arrow(s, 957, 140 + (k - 1) * 100 + 70, 957, 140 + k * 100)
label(s, 727, 545, 460, 36, "stays on the device for the next step", size=17, color=GRN_HI)
arrow(s, 603, 425, 727, 275, color=BLU, w=2)
arrow(s, 727, 475, 603, 465, color=YEL, w=2)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
