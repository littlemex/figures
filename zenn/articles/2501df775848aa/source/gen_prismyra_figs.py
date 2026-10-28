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

d.save(OUT)
print("saved", OUT)
