"""gen_prismyra_figs.py -- 3 figures for the Prismyra serving-design Zenn article.

    /usr/bin/python3 gen_prismyra_figs.py <out.pptx>

1. fig1-fork: the context's KV is written once and read by every branch; each branch's own
   recurrence state and tokens are private.
2. fig2-shelf: a document's KV stays resident on the shelf between separate HTTP requests;
   Batcher lanes run several shelves on independent CUDA streams.
3. fig3-determinism: the kernel pipeline (FP8/NVFP4 matmul, MoE routing, fused rope+gate,
   recorded one-pass graph) each carries its own fix for same-bits-every-process.

Colors follow this project's house style: green = Prismyra's own code, blue = the framework's
own code/kernel, yellow = a glue/caution point. Basis: docs/FORK.md, docs/PERFORMANCE.md,
docs/KERNELS.md in littlemex/Prismyra @ e617f059f86c94560f025d19ba931e4c8b70d575.
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "prismyra-figs.pptx"

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

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 24, 1190, 44, head, size=28, bold=True, align="left")
    label(s, 43, 68, 1190, 26, sub, size=15, color=MUTED, align="left")


def legend(s, y, items):
    x = 43
    for color, text in items:
        box(s, x, y, 22, 22, color, radius=0.3)
        label(s, x + 28, y - 2, 230, 26, text, size=13, color=MUTED, align="left")
        x += 250


# ------------------------------------------------------------------ 1. fork
s = d.slide()
title(s.s, "Read the context once, fork per question",
      "Green: written once, shared.  Blue/Yellow: written per branch, private, must be copied.")
legend(s.s, 108, [(GRN, "shared, read-only"), (LINK, "the branch itself"), (YEL, "its private state")])

box(s.s, 43, 170, 230, 320, GRN_DK, stroke=GRN, radius=0.1)
label(s.s, 55, 182, 206, 50, "Context KV\n(key / value)", size=17, bold=True)
label(s.s, 55, 250, 206, 60, "written once by\nthe context read", size=14, color=MUTED)
box(s.s, 65, 330, 186, 130, CHIP, stroke=EDGE, body="attention reads\nthis for every\nbranch alike",
    size=14, color=MUTED, radius=0.15)

branches = [
    ("Branch A", "Question: thirty-day limit?", 210),
    ("Branch B", "Question: who pays shipping?", 330),
    ("Branch C", "Question: item opened?", 450),
]
for name, q, y in branches:
    sh.arrow(s.s, t, 273, 330, 420, y + 40, color=GRN_HI, width=2)
    box(s.s, 420, y, 330, 95, LINK_DK, stroke=LINK, radius=0.12)
    label(s.s, 434, y + 8, 302, 26, name, size=16, bold=True, align="left")
    label(s.s, 434, y + 36, 302, 50, q, size=13, color=MUTED, align="left")
    box(s.s, 790, y + 12, 170, 70, YEL_DK, stroke=YEL, radius=0.15,
        body="own recurrence\nstate + tokens", size=12)
    sh.arrow(s.s, t, 750, y + 47, 790, y + 47, color=WHITE, width=1.75)
    sh.arrow(s.s, t, 960, y + 47, 1120, y + 47, color=WHITE, width=1.75)
    box(s.s, 1120, y + 12, 95, 70, CHIP, stroke=EDGE, body="answer", size=14)

box(s.s, 43, 560, 1194, 66, CHIP, stroke=EDGE, radius=0.2,
    body="ForkLayer: one row written -> landed in every row; a read returns only the rows the caller brought",
    size=14, color=MUTED)

# ------------------------------------------------------------------ 2. shelf
s = d.slide()
title(s.s, "Keep a document's KV on the shelf between requests",
      "Green: resident document.  Blue: an incoming request.  Yellow: the scheduler that routes it.")
legend(s.s, 108, [(GRN, "resident on the shelf"), (LINK, "incoming request"), (YEL, "scheduler / lane routing")])

box(s.s, 43, 168, 230, 70, LINK_DK, stroke=LINK, radius=0.15,
    body="Request 1\nabout doc X", size=14)
box(s.s, 43, 268, 230, 70, LINK_DK, stroke=LINK, radius=0.15,
    body="Request 2, new call\nabout doc X", size=14)
sh.arrow(s.s, t, 273, 203, 360, 238, color=WHITE, width=1.75)
sh.arrow(s.s, t, 273, 303, 360, 268, color=WHITE, width=1.75)
box(s.s, 360, 198, 230, 110, YEL_DK, stroke=YEL, radius=0.12,
    body="Batcher\nhash(doc) -> lane", size=15)

for i, (yy, hot) in enumerate([(160, False), (280, True), (400, False)]):
    fill = GRN_DK if hot else CHIP
    stroke = GRN if hot else EDGE
    box(s.s, 660, yy, 540, 100, fill, stroke=stroke, radius=0.1)
    label(s.s, 675, yy + 8, 300, 26, f"Lane {i}: shelf", size=15, bold=True, align="left")
    body = "doc X resident, KV on device" if hot else "idle, no document resident"
    label(s.s, 675, yy + 38, 500, 50, body, size=13, color=MUTED if not hot else WHITE, align="left")

sh.arrow(s.s, t, 590, 253, 660, 160, color=YEL, width=1.5, dashed=True)
sh.arrow(s.s, t, 590, 253, 660, 330, color=YEL, width=2)
sh.arrow(s.s, t, 590, 253, 660, 400, color=YEL, width=1.5, dashed=True)
box(s.s, 43, 540, 1194, 90, CHIP, stroke=EDGE, radius=0.15,
    body="doc X always hashes to lane 1, so request 2 hits the resident shelf: no context read, answer measured "
         "bit-exact against a fresh ask().  /v1/decide now reaches the same shelf, not only /ask.",
    size=14, color=MUTED)

# ------------------------------------------------------------------ 3. determinism
s = d.slide()
title(s.s, "Same input, same bits, in every process",
      "Green: a kernel this project sped up.  Yellow: a process-wide guardrail, not tied to one kernel.")
legend(s.s, 108, [(GRN, "sped up, speed only"), (YEL, "guardrail, process-wide")])

stages = ["FP8 dense\nmatmul", "MoE routed\nexperts", "rope + gate\nfusion", "one-pass\nreplay"]
x = 43
w = 280
gap = 18
for i, name in enumerate(stages):
    box(s.s, x, 168, w, 80, GRN_DK, stroke=GRN, body=name, size=16)
    if i < len(stages) - 1:
        sh.arrow(s.s, t, x + w, 208, x + w + gap, 208, color=WHITE, width=2)
    x += w + gap

label(s.s, 43, 268, 1194, 30, "these four run inside one guardrail, applied to the whole process:",
      size=14, color=MUTED, align="left")

guards = [
    "Triton autotune: pinned to one config per GPU generation, not re-timed per cold start",
    "aten::mm / addmm / matmul / linear: a fixed-tile kernel registered process-wide (batch invariance)",
    "FP8 matmul: run 8 times on a fixed input at startup, must return identical bits each time",
]
x = 43
gw = (1194 - 2 * 18) / 3
for g in guards:
    box(s.s, x, 306, gw, 110, YEL_DK, stroke=YEL, body=g, size=13)
    x += gw + 18

box(s.s, 43, 440, 1194, 70, CHIP, stroke=EDGE, radius=0.15,
    body="Companion-count x question-count audit, 4,392 checks: 1,692 non-exact on the first run (RTX PRO 4500) "
         "-> 0 non-exact, on both supported cards, once the guardrails above were in place.",
    size=14, color=MUTED)

# ------------------------------------------------------------------ 4. readout (no head)
s = d.slide()
title(s.s, "Scoring an option: unembedding[ids] against the final hidden state",
      "Green: this project's own code path.  Pale: the full matrix, never read whole.")
legend(s.s, 108, [(GRN_HI, "gathered / used"), (CHIP, "full matrix, not read")])

# -- declared options, left column
opt_y = [190, 380]
opt_names = ["no", "yes"]
for name, y in zip(opt_names, opt_y):
    box(s.s, 43, y, 110, 70, LINK_DK, stroke=LINK, body=name, size=18)
    box(s.s, 183, y, 90, 70, CHIP, stroke=EDGE, body="id", size=15, color=MUTED)
    sh.arrow(s.s, t, 153, y + 35, 183, y + 35, color=WHITE, width=1.5)
label(s.s, 43, 150, 280, 24, "declared options", size=13, color=MUTED, align="left")
label(s.s, 43, 470, 280, 24, "token_ids  [k]", size=13, color=MUTED, align="left")

# -- the big, pale vocabulary matrix
mat_x, mat_y, mat_w, mat_h = 400, 150, 150, 420
box(s.s, mat_x, mat_y, mat_w, mat_h, CHIP, stroke=EDGE, radius=0.04)
label(s.s, mat_x, mat_y - 28, mat_w, 24, "lm_head.weight", size=14, bold=True, align="center")
label(s.s, mat_x, mat_y + mat_h + 4, mat_w, 24, "[V, d]", size=15, color=GRN_HI, align="center")
label(s.s, mat_x, mat_y + mat_h + 30, mat_w, 22, "V=248,320  d=2,048", size=11, color=MUTED, align="center")

# two highlighted rows inside the pale matrix, at the two option rows' height
row_ys = [mat_y + 90, mat_y + 320]
for y, oy in zip(row_ys, opt_y):
    box(s.s, mat_x + 6, y, mat_w - 12, 20, GRN_HI, body="", radius=0.0)
    sh.arrow(s.s, t, 273, oy + 35, mat_x + 6, y + 10, color=GRN_HI, width=1.5, dashed=True)

# -- gathered rows, pulled out to their own small stack
gx, gy0 = 620, 260
for i, y in enumerate(row_ys):
    gy = gy0 + i * 70
    box(s.s, gx, gy, 170, 50, GRN_DK, stroke=GRN, body="row", size=14)
    sh.arrow(s.s, t, mat_x + mat_w, y + 10, gx, gy + 25, color=GRN_HI, width=1.5)
label(s.s, gx, 198, 220, 24, "gathered  [k, d]", size=14, color=GRN_HI, align="left")

# -- final hidden state vector
hx, hy = 620, 460
box(s.s, hx, hy, 170, 60, LINK_DK, stroke=LINK, body="hidden state", size=14)
label(s.s, hx, hy + 64, 220, 22, "[d]", size=13, color=MUTED, align="left")

# -- dot product -> logits
dot_x, dot_y = 850, 330
box(s.s, dot_x, dot_y, 70, 70, CHIP, stroke=WHITE, body="·", size=28)
sh.arrow(s.s, t, gx + 170, gy0 + 25, dot_x, dot_y + 25, color=GRN_HI, width=1.5)
sh.arrow(s.s, t, hx + 170, hy + 30, dot_x, dot_y + 45, color=LINK, width=1.5)

logit_x = 970
box(s.s, logit_x, 300, 130, 70, GRN_DK, stroke=GRN, body="logits", size=16)
label(s.s, logit_x, 374, 170, 22, "[k]", size=13, color=MUTED, align="left")
sh.arrow(s.s, t, dot_x + 70, dot_y + 35, logit_x, 335, color=WHITE, width=2)

# -- softmax over k -> probabilities
sm_x = 1140
box(s.s, sm_x, 300, 97, 70, CHIP, stroke=WHITE, body="softmax\n(over k)", size=12)
sh.arrow(s.s, t, logit_x + 130, 335, sm_x, 335, color=WHITE, width=2)

prob_x, prob_y = 970, 440
box(s.s, prob_x, prob_y, 267, 70, GRN_HI, body="probabilities", size=16, color=CHIP)
label(s.s, prob_x, prob_y + 74, 267, 22, "[k]", size=13, color=MUTED, align="center")
sh.arrow(s.s, t, sm_x + 48, 370, prob_x + 133, prob_y, color=WHITE, width=2)

d.save(OUT)
print("saved", OUT)
