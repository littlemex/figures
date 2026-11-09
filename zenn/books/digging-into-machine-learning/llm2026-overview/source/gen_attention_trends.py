"""gen_attention_trends.py -- figures for the two "Attention trends" chapters of digging-into-machine-learning.

    /usr/bin/python3 gen_attention_trends.py <out.pptx>

1. roofline-wall      decode sits far left of every generation's ridge point
2. kv-four-axes       KV bytes = product of four independent axes, and who cuts which
3. softmax-lineage    two softmax-side flows (hold lighter / select what to read) merging at CSA2
4. update-ladder      fixed-state update rules: add -> forget -> correct -> enrich
5. flops-vs-time      where time goes at short length: attention vs state models
6. hybrid-stacks      layer patterns of shipped hybrid models
Look follows templates/nxd_interfaces_pptx.py (ZN-25). Numbers come from the chapter text and its cited papers.
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL_DIR = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, TPL_DIR)
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "attention-trends.pptx"

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

ROLE_PATTERN = {GRN_DK: "diagonal", LINK_DK: "cross", YEL_DK: "grid"}


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25, pattern=True):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if pattern:
        pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width)


def line(s, x1, y1, x2, y2, color=GREY, width=1.25, dashed=False):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
    c.shadow.inherit = False
    c.line.color.rgb = color
    c.line.width = sh.Pt(width) if hasattr(sh, "Pt") else c.line.width
    if dashed:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def title(s, head, sub):
    label(s, 43, 22, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 68, 1190, 26, sub, size=16, color=MUTED, align="left")


# ------------------------------------------------------------------ 1. roofline wall
s = d.slide().s
title(s, "Decode sits far left of every ridge point",
      "Green: where decode lives.  Blue: where each GPU becomes compute-bound (ridge point)")
X0, X1, Y0, Y1 = 120, 1200, 140, 610
box(s, X0, Y0, X1 - X0, Y1 - Y0, CHIP, stroke=EDGE, radius=0.02, pattern=False)
import math  # noqa: E402


def xpos(ai):
    lo, hi = math.log10(0.5), math.log10(4000)
    return X0 + (math.log10(ai) - lo) / (hi - lo) * (X1 - X0)


box(s, xpos(0.8), Y0 + 10, xpos(5) - xpos(0.8), Y1 - Y0 - 20, GRN_DK, stroke=GRN, radius=0.05)
label(s, xpos(0.8), Y0 + 20, xpos(5) - xpos(0.8), 80, "decode\nbatch 1\n1 to 4", size=18, bold=True)
label(s, xpos(0.8), Y1 - 70, xpos(5) - xpos(0.8), 50, "BF16 1\nFP8 2  FP4 4", size=14, color=GRN_HI)
for ai, name, y in ((153, "A100 BF16\n153", 330), (591, "H100 FP8\n591", 250), (1180, "B200 FP4\n~1100-1250", 170)):
    x = xpos(ai)
    line(s, x, Y0 + 10, x, Y1 - 10, color=LINK, width=2, dashed=True)
    box(s, x - 75, y, 150, 58, LINK_DK, stroke=LINK, body=name, size=15)
arrow(s, xpos(160), 540, xpos(1200), 540, color=YEL, width=3)
label(s, xpos(20), 525, xpos(150) - xpos(20), 30, "ridge point moves right each generation", size=16, color=YEL, align="right")
label(s, xpos(6), 380, xpos(140) - xpos(6), 60, "bandwidth-bound\n2+ orders of magnitude gap", size=17, color=WHITE)
for ai in (1, 10, 100, 1000):
    label(s, xpos(ai) - 40, Y1 + 6, 80, 26, str(ai), size=14, color=MUTED)
label(s, X0, Y1 + 34, X1 - X0, 28, "arithmetic intensity (FLOP per byte, log scale)", size=16, color=MUTED)

# ------------------------------------------------------------------ 2. KV four axes
s = d.slide().s
title(s, "KV bytes split into four axes",
      "Blue: the factor in the formula.  Green: methods that cut it.  Cuts roughly multiply")
cols = [
    ("layers", "n_layer", "CLA, YOCO\nCSA2 reuse"),
    ("entry size", "n_kv x d_h", "MQA, GQA\nMLA"),
    ("precision", "b_KV", "KIVI\nMXFP4 KV"),
    ("sequence", "L", "SWA, CSA merge, H2O\nNSA, DSA: read only"),
]
label(s, 43, 112, 1194, 48, "Bytes_KV  =  2  x  n_layer  x  n_kv  x  d_h  x  b_KV  x  L", size=26, bold=True)
x = 43
W = 280
for i, (axis, factor, who) in enumerate(cols):
    box(s, x, 190, W, 56, CHIP, stroke=EDGE, body=axis, size=20)
    box(s, x, 266, W, 70, LINK_DK, stroke=LINK, body=factor, size=22)
    arrow(s, x + W / 2, 336, x + W / 2, 370)
    box(s, x, 370, W, 110, GRN_DK, stroke=GRN, body=who, size=19)
    x += W + 25
box(s, 43, 512, 1194, 70, YEL_DK, stroke=YEL, radius=0.3,
    body="Stored bytes set how many requests fit; read bytes set decode time. DSA cuts only the read side", size=18)

# ------------------------------------------------------------------ 3. softmax lineage
s = d.slide().s
title(s, "Two flows on the softmax side, merging in 2026",
      "Green: hold each KV lighter.  Blue: choose what to read.  Yellow: where they merge")
W, G, X = 150, 22, 43
label(s, 43, 112, 600, 30, "hold each KV lighter", size=18, bold=True, color=GRN_HI, align="left")
hold = ["MHA\n2017", "MQA\n2019", "GQA\n2023", "MLA\n2024", "CLA / YOCO\n2024", "KV quant\n2024-26"]
for i, n in enumerate(hold):
    x = X + i * (W + G)
    box(s, x, 150, W, 70, GRN_DK, stroke=GRN, body=n, size=16)
    if i:
        arrow(s, x - G, 185, x, 185)
label(s, 43, 238, 1000, 26, "share heads  ->  low-rank latent  ->  share layers  ->  fewer bits", size=15, color=MUTED, align="left")
label(s, 43, 330, 600, 30, "choose what to read", size=18, bold=True, color=LINK, align="left")
sel = ["SWA\n2020", "Streaming\nLLM 2023", "NSA / MoBA\n2025-02", "DSA\n2025-09", "CSA / HCA\n2026-06"]
for i, n in enumerate(sel):
    x = X + i * (W + G)
    box(s, x, 368, W, 70, LINK_DK, stroke=LINK, body=n, size=16)
    if i:
        arrow(s, x - G, 403, x, 403)
label(s, 43, 456, 1000, 26, "by position  ->  keep the sink  ->  compress + select, trained in  ->  indexer top-k  ->  compress, then select", size=15, color=MUTED, align="left")
box(s, 1080, 250, 157, 110, YEL_DK, stroke=YEL, body="CSA2\n2026-09\n890 B / token", size=17)
arrow(s, X + 5 * (W + G) + W, 185, 1158, 250, color=YEL, width=2.5)
arrow(s, X + 4 * (W + G) + W, 403, 1080, 330, color=YEL, width=2.5)
box(s, 43, 530, 1194, 64, CHIP, stroke=EDGE, radius=0.3,
    body="What stays: KV still grows with L, and DSA keeps every KV in HBM  ->  next chapter drops the KV itself", size=17)

# ------------------------------------------------------------------ 4. update ladder
s = d.slide().s
title(s, "One update rule, four steps of making A_t smarter",
      "S_t = A_t S_(t-1) + beta_t k_t v_t^T.  Green: the A_t each step adds.  Blue: shipped examples")
steps = [
    ("1. add", "A_t = I", "Linear Attention\n2020", "fills up: past mixes\nonce L > d_k"),
    ("2. forget", "A_t = gate (scalar or diag)", "RetNet (fixed)\nGLA, Mamba, Mamba-2", "decay old memory,\nfixed or per token"),
    ("3. correct", "A_t = g (I - beta k k^T)\ng: scalar or diag", "DeltaNet, Gated DeltaNet\nKDA (diag gate)", "write only the error\nof the current guess"),
    ("4. enrich", "negative eigenvalues,\nproducts, complex A_t", "Grazzi 2024, DeltaProduct\nMamba-3 (+ MIMO)", "flip, rotate,\ntrack state (parity)"),
]
for i, (step, rule, who, why) in enumerate(steps):
    y = 490 - i * 110
    x = 43 + i * 70
    box(s, x, y, 170, 90, CHIP, stroke=EDGE, body=step, size=21)
    box(s, x + 182, y, 300, 90, GRN_DK, stroke=GRN, body=rule, size=17)
    box(s, x + 494, y, 270, 90, LINK_DK, stroke=LINK, body=who, size=15)
    label(s, x + 776, y, 220, 90, why, size=15, color=MUTED, align="left")
    if i:
        arrow(s, x + 30, y + 110, x + 30, y + 90, color=YEL, width=2.5)

# ------------------------------------------------------------------ 5. flops vs time
s = d.slide().s
title(s, "Fewer FLOPs, yet slower at short length",
      "Short sequences, plus decode state traffic.  Green: matmul on Tensor Cores.  Yellow: element-wise.  Blue: fixes")
label(s, 43, 112, 560, 30, "attention, short sequence", size=19, bold=True, align="left")
box(s, 43, 150, 470, 60, GRN_DK, stroke=GRN, body="QKV / FFN matmul (big, Tensor Core)", size=15)
box(s, 513, 150, 90, 60, GRN_DK, stroke=GRN_HI, body="L^2", size=15)
label(s, 43, 214, 560, 26, "the L^2 part is small when L is short", size=15, color=MUTED, align="left")
label(s, 650, 112, 590, 30, "state model, same length", size=19, bold=True, align="left")
box(s, 650, 150, 330, 60, GRN_DK, stroke=GRN, body="projection matmul", size=15)
box(s, 980, 150, 110, 60, YEL_DK, stroke=YEL, body="scan", size=15)
box(s, 1090, 150, 60, 60, YEL_DK, stroke=YEL, body="conv", size=13)
box(s, 1150, 150, 87, 60, YEL_DK, stroke=YEL, body="norm\ngates", size=13)
label(s, 650, 214, 590, 26, "scan: no Tensor Core, bandwidth-bound; many small kernels", size=15, color=MUTED, align="left")
fix = [
    ("chunk the sequence,\nmatmul inside chunks", "Mamba-2 SSD, GLA,\nDeltaNet parallel"),
    ("drop and fuse\nsmall ops", "Mamba-3 (Triton, CuTe)\nReWY (backward)"),
    ("reshape for the\nmatrix unit", "TPU: Systolic LA\nNPU: matmul inverse"),
    ("cut state traffic\nin decode", "ReplaySSM, SPARE\nPACE (4-bit state)"),
]
for i, (what, who) in enumerate(fix):
    x = 43 + i * 304
    box(s, x, 300, 286, 90, LINK_DK, stroke=LINK, body=what, size=17)
    arrow(s, x + 143, 390, x + 143, 420)
    box(s, x, 420, 286, 90, CHIP, stroke=EDGE, body=who, size=15)
box(s, 43, 545, 1194, 56, CHIP, stroke=EDGE, radius=0.3,
    body="Measured: Transformer up to 1.9x faster below 8K tokens, SSM up to 4x faster near 57K (Mitra et al. 2025)", size=16)

# ------------------------------------------------------------------ 6. hybrid stacks
s = d.slide().s
title(s, "Shipped models keep a few attention layers",
      "Green: linear / state layer.  Blue: attention layer.  One cell = one layer in a repeating block")
rows = [
    ("Jamba  2024-03", "Mamba 7 : 1 full attention", "LLLLLLLA"),
    ("MiniMax-01  2025-01", "Lightning 7 : 1 softmax", "LLLLLLLA"),
    ("Qwen3-Next  2025-09", "Gated DeltaNet 3 : 1 Gated Attn", "LLLA"),
    ("MiniMax M2  2025-10", "back to full attention", "AAAA"),
    ("Kimi Linear  2025-10", "KDA 3 : 1 MLA, NoPE", "LLLA"),
    ("Qwen3.5  2026-02", "Gated DeltaNet 3 : 1 Gated Attn", "LLLA"),
    ("Kimi K3  2026-07", "KDA 3 : 1 Gated MLA, NoPE", "LLLA+"),
]
for i, (name, what, pat) in enumerate(rows):
    y = 112 + i * 68
    label(s, 43, y, 310, 30, name, size=17, bold=True, align="left")
    label(s, 43, y + 28, 310, 26, what, size=13, color=MUTED, align="left")
    tail = pat.endswith("+")
    pat = pat.rstrip("+")
    reps = 3 if len(pat) <= 4 else (2 if len(pat) <= 8 else 1)
    cells = pat * reps + ("A" if tail else "")
    cw = min(70, 860 / len(cells))
    for j, c in enumerate(cells):
        lin = c == "L"
        box(s, 360 + j * cw, y + 4, cw - 6, 50, GRN_DK if lin else LINK_DK, stroke=GRN if lin else LINK,
            radius=0.15, body="" if cw < 40 else ("lin" if lin else "attn"), size=12)
label(s, 360, 600, 877, 30, "One repeating block shown 2-3 times. Kimi K3 adds one more attention layer at the end",
      size=14, color=MUTED, align="left")

d.save(OUT)
sys.path.insert(0, TPL_DIR)
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
