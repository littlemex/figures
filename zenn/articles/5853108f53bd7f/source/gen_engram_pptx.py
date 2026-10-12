"""gen_engram_pptx.py: Engram 記事の静止画 2 枚（アドレスの出どころ、分けて持った表から行を集める 3 つの方法）。"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "engram-figures.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
LINK = RGBColor(40, 150, 240)
LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)
DASH = MSO_LINE_DASH_STYLE.DASH

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2, dashed=False):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)




PNK = RGBColor(255, 120, 160)
PNK_DK = RGBColor(80, 30, 46)
# ------------------------------------------------------------------ 1. where the address comes from
s = d.slide().s
title(s, "Where the lookup address comes from",
      "Grey: input.  Green: GPU compute.  Pink: the address.  Yellow: memory read")
for x, head_, sub in [(43, "MoE (conditional computation)", "expert ids from the hidden state"),
                      (653, "Engram (conditional memory)", "row ids from the token ids")]:
    label(s, x, 112, 584, 30, head_, size=18, bold=True)
    label(s, x, 142, 584, 24, sub, size=14, color=MUTED)
    box(s, x, 176, 584, 420, CHIP, stroke=EDGE, radius=0.04)
# left
box(s, 83, 196, 504, 50, GREY, stroke=EDGE, body="token \"Great\"", size=15)
arrow(s, 335, 246, 335, 270)
box(s, 83, 270, 504, 50, GRN_DK, stroke=GRN, body="layers before layer l", size=15)
arrow(s, 335, 320, 335, 344)
box(s, 83, 344, 504, 50, GRN_DK, stroke=GRN, body="hidden state of \"Great\" -> router", size=15)
arrow(s, 335, 394, 335, 418)
box(s, 83, 418, 504, 50, PNK_DK, stroke=PNK, body="experts #17, #203, ... (6 of 384)", size=15)
arrow(s, 335, 468, 335, 492)
box(s, 83, 492, 504, 50, GRN_DK, stroke=GRN, body="experts (FFN)", size=15)
label(s, 83, 552, 504, 30, "address known only when layer l runs", size=14, color=MUTED)
# right
box(s, 693, 196, 504, 50, GREY, stroke=EDGE, body="tokens \"Alexander the Great\"", size=15)
arrow(s, 945, 246, 945, 270)
box(s, 693, 270, 504, 50, PNK_DK, stroke=PNK, body="hash \"the Great\", \"Alexander the Great\"", size=15)
arrow(s, 945, 320, 945, 344)
box(s, 693, 344, 504, 50, PNK_DK, stroke=PNK, body="rows 4,112,907, 7,340,551, ...", size=15)
arrow(s, 945, 394, 945, 418)
box(s, 693, 418, 504, 50, YEL_DK, stroke=YEL, body="embedding table rows", size=15)
arrow(s, 945, 468, 945, 492)
box(s, 693, 492, 504, 50, GRN_DK, stroke=GRN, body="gate with h, add to residual", size=15)
label(s, 693, 552, 504, 30, "address known before the forward pass", size=14, color=MUTED)

# ------------------------------------------------------------------ 2. three ways to gather rows
s = d.slide().s
title(s, "Gathering rows from a table split across GPUs",
      "Green: reader GPU.  Blue: owner GPU works.  Grey: owner GPU idle.  Pink: row ids.  Yellow: rows")
cols = [(43, "all_reduce", "V4.1 reference inference code"),
        (453, "All-to-All", "paper, training"),
        (863, "GIN get", "DeepEP Engram (experimental)")]
for x, head_, sub in cols:
    label(s, x, 112, 374, 30, head_, size=18, bold=True)
    label(s, x, 142, 374, 24, sub, size=14, color=MUTED)
    box(s, x, 176, 374, 400, CHIP, stroke=EDGE, radius=0.04)
def rank_pair(x, top_fill, top_st, top_body, bot_fill, bot_st, bot_body):
    box(s, x + 30, 200, 314, 96, top_fill, stroke=top_st, body=top_body, size=14)
    box(s, x + 30, 440, 314, 96, bot_fill, stroke=bot_st, body=bot_body, size=14)
# (a) all_reduce: both ranks look up, sum
rank_pair(43, GRN_DK, GRN, "rank 0: looks up all ids\nrows it does not own = 0",
          LINK_DK, LINK, "rank 1: looks up all ids\nrows it does not own = 0")
arrow(s, 120, 440, 120, 296, color=YEL, width=3)
arrow(s, 190, 296, 190, 440, color=YEL, width=3)
label(s, 210, 343, 200, 50, "partial results\nsummed", size=14, color=YEL, align="left")
# (b) all-to-all: ids out, rows back
rank_pair(453, GRN_DK, GRN, "rank 0: sends row ids", LINK_DK, LINK, "rank 1: reads its rows\nsends them back")
arrow(s, 560, 296, 560, 440, color=PNK, width=3)
label(s, 463, 343, 85, 50, "row ids", size=14, color=PNK, align="right")
arrow(s, 720, 440, 720, 296, color=YEL, width=3)
label(s, 735, 340, 140, 50, "rows", size=14, color=YEL)
# (c) get: reader pulls
rank_pair(863, GRN_DK, GRN, "rank 0: get(row offset)\nflush_async, wait", GREY, EDGE, "rank 1: GPU not involved\nNIC reads its storage")
arrow(s, 1130, 440, 1130, 296, color=YEL, width=3)
label(s, 1145, 340, 100, 50, "rows", size=14, color=YEL)
# ------------------------------------------------------------------ 3. sparse compute vs sparse memory
s = d.slide().s
title(s, "Two kinds of sparsity per token (DeepSeek-V4.1-Flash)",
      "Green: used for this token (positions illustrative).  Grey: not used.  Yellow: Engram table")
label(s, 43, 112, 584, 30, "MoE layer: sparse compute", size=18, bold=True)
label(s, 653, 112, 584, 30, "Engram layer 1: sparse memory", size=18, bold=True)
box(s, 43, 150, 584, 380, CHIP, stroke=EDGE, radius=0.04)
box(s, 653, 150, 584, 380, CHIP, stroke=EDGE, radius=0.04)
lit = {5, 41, 77, 130, 201, 333}
for k in range(384):
    r, c = divmod(k, 32)
    x = 63 + c * 17
    y = 170 + r * 22
    on = k in lit
    box(s, x, y, 13, 16, GRN if on else GREY, stroke=GRN if on else EDGE, radius=0.2, sw=0.5)
label(s, 63, 450, 544, 30, "6 of 384 routed experts run their FFN", size=16)
label(s, 63, 484, 544, 30, "cost: FLOPs of 6 experts", size=14, color=MUTED)
box(s, 683, 180, 524, 240, YEL_DK, stroke=YEL, radius=0.02)
for k in range(24):
    x = 690 + (k * 97 % 510)
    box(s, x, 184 + (k % 8) * 29, 6, 26, GRN, stroke=GRN, radius=0.0, sw=0.5)
label(s, 673, 450, 544, 30, "24 of 384,006,168 rows are read", size=16)
label(s, 673, 484, 544, 30, "the lookup itself: 24 × 256 bytes read", size=14, color=MUTED)
d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
