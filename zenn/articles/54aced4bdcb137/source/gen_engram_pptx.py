"""gen_engram_pptx.py: Engram 記事の静止画 6 枚（アドレスの出どころ、分けて持った表から行を集める 3 つの方法、2 種類の疎、Engram が空ける層、N-gram、表の中身）。"""
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
box(s, 83, 418, 504, 50, PNK_DK, stroke=PNK, body="experts #17, #203, ... (6 of 384, illustrative)", size=15)
arrow(s, 335, 468, 335, 492)
box(s, 83, 492, 504, 50, GRN_DK, stroke=GRN, body="experts (FFN)", size=15)
label(s, 83, 552, 504, 30, "address known only when layer l runs", size=14, color=MUTED)
# right
box(s, 693, 196, 504, 50, GREY, stroke=EDGE, body="tokens \"Alexander the Great\"", size=15)
arrow(s, 945, 246, 945, 270)
box(s, 693, 270, 504, 50, PNK_DK, stroke=PNK, body="hash \"the Great\", \"Alexander the Great\"", size=15)
arrow(s, 945, 320, 945, 344)
box(s, 693, 344, 504, 50, PNK_DK, stroke=PNK, body="rows 4,112,907, 7,340,551, ... (illustrative)", size=15)
arrow(s, 945, 394, 945, 418)
box(s, 693, 418, 504, 50, YEL_DK, stroke=YEL, body="embedding table rows", size=15)
arrow(s, 945, 468, 945, 492)
box(s, 693, 492, 504, 50, GRN_DK, stroke=GRN, body="gate with h, add to residual", size=15)
label(s, 693, 552, 504, 30, "address known from the input tokens, before the layers run", size=14, color=MUTED)

# ------------------------------------------------------------------ 2. three ways to gather rows
s = d.slide().s
title(s, "Gathering rows from a table split across ranks",
      "Green: reader GPU.  Blue: owner GPU works.  Grey: owner GPU runs no kernel.  Pink: row ids.  Yellow: rows")
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
rank_pair(863, GRN_DK, GRN, "rank 0: get(row offset)\nthen waits for completion", GREY, EDGE, "rank 1: no row-serving kernel\nNIC reads its storage (RDMA)")
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
label(s, 673, 484, 544, 30, "the lookup itself: 24 × 256 bytes of FP8 values", size=14, color=MUTED)
# ------------------------------------------------------------------ 4. what Engram frees up
s = d.slide().s
title(s, "What Engram may free up (the paper's view)",
      "Grey: input.  Pink: composing the phrase.  Green: context and reasoning.  Yellow: N-gram lookup")
for x, head_, sub in [(43, "Without Engram", "early layers build the phrase"),
                      (653, "With Engram", "the lookup helps build it early")]:
    label(s, x, 112, 584, 30, head_, size=18, bold=True)
    label(s, x, 142, 584, 24, sub, size=14, color=MUTED)
    box(s, x, 176, 584, 420, CHIP, stroke=EDGE, radius=0.04)
ys = [258, 304, 350, 396, 442, 488]
for x0, n_build in [(83, 3), (693, 2)]:
    lw = 504 if x0 == 83 else 330
    lx = x0 if x0 == 83 else x0 + 174
    box(s, x0, 196, 504, 44, GREY, stroke=EDGE, body="tokens \"Alexander the Great\"", size=15)
    arrow(s, lx + lw // 2, 240, lx + lw // 2, ys[0])
    for i, y in enumerate(ys):
        build = i < n_build
        box(s, lx, y, lw, 38, PNK_DK if build else GRN_DK, stroke=PNK if build else GRN,
            body="compose the phrase" if build else "context / reasoning", size=14)
box(s, 693, 304, 150, 38, YEL_DK, stroke=YEL, body="N-gram lookup", size=14)
arrow(s, 768, 240, 768, 304, color=YEL, width=2)
arrow(s, 843, 323, 867, 323, color=YEL, width=3)
label(s, 83, 548, 504, 30, "6 layers", size=14, color=MUTED)
label(s, 867, 548, 330, 30, "same 6 layers", size=14, color=MUTED)
label(s, 43, 604, 1194, 30, "illustrative: layer counts and roles are not measured", size=14, color=MUTED)
# ------------------------------------------------------------------ 5. N-grams ending at position t
s = d.slide().s
title(s, "Longer N-grams narrow the meaning",
      "Grey: tokens.  Yellow: position t.  Blue: token embedding.  Green: Engram lookup")
words = ["Only", "Alexander", "the", "Great", "could", "tame", "the", "horse"]
TX, TW, TG = 160, 120, 13
def tx(i):
    return TX + i * (TW + TG)
label(s, tx(3), 150, TW, 30, "t", size=18, color=YEL, bold=True)
for i, w in enumerate(words):
    hot = i == 3
    box(s, tx(i), 184, TW, 56, YEL_DK if hot else GREY, stroke=YEL if hot else EDGE, body=w, size=16)
label(s, tx(4) + 20, 250, 400, 30, "what it can point to", size=14, color=MUTED, align="left")
for r, (n, fill, st, text, meaning) in enumerate([(1, LINK_DK, LINK, "Great", "many uses"),
                                                  (2, GRN_DK, GRN, "the Great", "fewer things"),
                                                  (3, GRN_DK, GRN, "Alexander the Great", "usually one person")]):
    y = 290 + r * 80
    label(s, 43, y, 110, 56, f"{n}-gram", size=18, bold=True, align="left")
    x1 = tx(4 - n)
    box(s, x1, y, tx(3) + TW - x1, 56, fill, stroke=st, body=text, size=16)
    arrow(s, tx(3) + TW + 6, y + 28, tx(4) + 14, y + 28, color=MUTED, width=2)
    label(s, tx(4) + 20, y, 400, 56, meaning, size=18, bold=True, align="left")
label(s, 43, 560, 1194, 30, "1 word = 1 token (illustrative)", size=14, color=MUTED)
# ------------------------------------------------------------------ 6. what the table holds
s = d.slide().s
title(s, "What the table holds (V4.1-Flash, one layer)",
      "Pink: row ids.  Yellow: table rows (learned weights).  Grey: hidden state.  Green: GPU compute")
box(s, 60, 130, 300, 56, PNK_DK, stroke=PNK, body="24 row ids\n(2/3/4-grams × 8 hashes)", size=14)
arrow(s, 210, 186, 210, 214)
box(s, 60, 214, 300, 360, YEL_DK, stroke=YEL, radius=0.02)
label(s, 60, 222, 300, 50, "table\n384,006,168 rows × 256", size=15, bold=True)
for yy in (300, 352, 430, 505):
    box(s, 70, yy, 280, 7, YEL, stroke=YEL, radius=0.0, sw=0.5)
label(s, 60, 530, 300, 30, "24 rows read per token", size=14, color=YEL)
box(s, 430, 366, 240, 56, GRN_DK, stroke=GRN, body="e_t: 24 rows joined", size=15)
arrow(s, 360, 394, 430, 394, color=YEL, width=3)
box(s, 740, 150, 230, 56, GREY, stroke=EDGE, body="h_t (context so far)", size=15)
box(s, 740, 266, 230, 56, GRN_DK, stroke=GRN, body="k_t = W_K e_t", size=15)
box(s, 740, 466, 230, 56, GRN_DK, stroke=GRN, body="v_t = W_V e_t", size=15)
arrow(s, 670, 380, 740, 294)
arrow(s, 670, 408, 740, 494)
box(s, 1020, 208, 220, 56, GRN_DK, stroke=GRN, body="gate α_t ∈ (0, 1)\nσ(norm h · norm k / √d)", size=14)
arrow(s, 970, 178, 1020, 228)
arrow(s, 970, 294, 1020, 246)
box(s, 1020, 466, 220, 56, GREY, stroke=EDGE, body="h_t + α_t · v_t", size=15)
# h_t is also the left-hand side of the final add: route it around the gate
from pptx.enum.shapes import MSO_CONNECTOR  # noqa: E402
from pptx.util import Pt  # noqa: E402
for x1, y1, x2, y2 in [(970, 168, 1262, 168), (1262, 168, 1262, 494)]:
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
    c.line.color.rgb = MUTED
    c.line.width = Pt(2)
arrow(s, 1262, 494, 1242, 494, color=MUTED)
arrow(s, 1130, 264, 1130, 466)
arrow(s, 970, 494, 1020, 494)
label(s, 43, 604, 1194, 30, "rows start random and are trained with the rest of the model", size=14, color=MUTED)

# ------------------------------------------------------------------ 7. how an LLM predicts the next token
s = d.slide().s
title(s, "An LLM predicts the next token",
      "Grey: data.  Green: GPU compute.  Yellow: learned weights.  Pink: training only")
xs = [43 + i * 202 for i in range(6)]
items = [("text", "\"Alexander the\""), ("token ids", "1, 2, 3 ..."), ("embedding table", "one row per id"),
         ("layers 0, 1, 2 ...", "Attention + FFN\nadd to residual"), ("probabilities", "of the next token"),
         ("\"Great\"", "most likely")]
fills = [(GREY, EDGE), (GREY, EDGE), (YEL_DK, YEL), (GRN_DK, GRN), (GRN_DK, GRN), (GREY, EDGE)]
for i, (x, (head_, sub), (f, st)) in enumerate(zip(xs, items, fills)):
    box(s, x, 170, 170, 110, f, stroke=st, body=f"{head_}\n{sub}", size=15)
    if i < 5:
        arrow(s, x + 170, 225, xs[i + 1], 225)
label(s, xs[2] - 60, 300, 800, 26, "hidden state: a list of numbers per position, rewritten by each layer", size=14,
      color=MUTED)
box(s, 43, 450, 1194, 120, PNK_DK, stroke=PNK, radius=0.04)
label(s, 63, 462, 1154, 30, "training", size=17, bold=True, align="left")
label(s, 63, 500, 1154, 56, "compare the probabilities with the true next token  ->  loss  ->  update weights using gradients to reduce it",
      size=16, align="left")

# ------------------------------------------------------------------ 8. hashing and collisions
s = d.slide().s
title(s, "Eight hashes per n-gram soften collisions",
      "Pink: hash heads.  Yellow: table rows.  Grey: another n-gram.  Rows shown are illustrative")
box(s, 60, 150, 300, 56, GRN_DK, stroke=GRN, body="\"Alexander the Great\"", size=15)
box(s, 60, 470, 300, 56, GREY, stroke=EDGE, body="\"Peter the Great\" (example)", size=15)
box(s, 700, 130, 520, 420, YEL_DK, stroke=YEL, radius=0.02)
label(s, 700, 138, 520, 26, "table rows", size=15, bold=True)
rows_a = [0, 1, 2, 3, 4, 5, 6, 7]
for k in range(8):
    y = 178 + k * 44
    box(s, 760, y, 400, 32, CHIP, stroke=YEL, radius=0.1, body=f"row {k * 7 + 3}", size=12)
for k in range(8):
    y = 178 + k * 44 + 16
    arrow(s, 360, 178, 760, y, color=PNK, width=1.25)
arrow(s, 360, 498, 760, 178 + 3 * 44 + 16, color=MUTED, width=2.5)
label(s, 60, 536, 600, 30, "one head collides: the same row as another n-gram", size=14, color=MUTED, align="left")
label(s, 43, 590, 1194, 30, "the 8 rows are joined, so a shared row is only one part of what is read", size=15, color=MUTED)

# ------------------------------------------------------------------ 9. where to place Engram
s = d.slide().s
title(s, "Which layer gets the Engram table",
      "Green: a layer.  Yellow: where Engram is added.  Layers counted from 1, as in the paper")
cols9 = [("one table: layer 2 is best", [2]), ("split in two: layers 2 and 6", [2, 6]),
         ("Engram-27B, V4.1-Flash: 2 and 15", [2, 15])]
for c, (head_, at) in enumerate(cols9):
    x = 43 + c * 402
    label(s, x, 112, 380, 30, head_, size=16, bold=True)
    ids = list(range(1, 13)) if c < 2 else [1, 2, 3, None, 14, 15, 16, None]
    n = len(ids) if c < 2 else 12
    for i, lid in enumerate(ids):
        y = 160 + i * (420 / n)
        if lid is None:
            label(s, x + 90, y, 200, 420 / n - 4, "...", size=14, color=MUTED)
            continue
        hot = lid in at
        box(s, x + 90, y, 200, 420 / n - 4, YEL_DK if hot else GRN_DK, stroke=YEL if hot else GRN,
            body=(f"layer {lid}" + ("  + Engram" if hot else "")), size=11)
label(s, 43, 600, 1194, 30, "12-layer 3B MoE with a 1.6B Engram (paper 6.2): validation loss 1.770 for layer 2, 1.768 when split",
      size=14, color=MUTED)
d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
