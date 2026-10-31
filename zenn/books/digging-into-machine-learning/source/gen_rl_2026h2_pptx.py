"""gen_rl_2026h2_pptx.py: figures for the 2026H2 open-model chapter (3 slides).

Slides 1-3: rl-objectives-after-grpo (grpo-anatomy, clip-shapes, token-vs-sequence-ratio)
Slides 4-6: rl-mismatch-and-on-policy-distillation (mismatch-sources, sft-rl-opd, multi-teacher-opd)
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "rl-post-training-figures.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_MID = RGBColor(26, 110, 52)
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
        dash=None, sw=1.25, bold=True):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, bold, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2, dashed=False):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


import math

# ------------------------------------------------------------------ 1. pipeline
s = d.slide().s
title(s, "Build domain experts with RL, then merge them with OPD",
      "Green: student model.  Blue: domain experts.  Yellow: what reports vary on, per stage")
box(s, 43, 250, 190, 100, GRN_DK, stroke=GRN_HI, body="SFT\nbase", size=18, sw=2)
for i, name in enumerate(["math / reasoning", "coding agent", "general agent", "... more domains"]):
    y = 130 + i * 92
    box(s, 300, y, 250, 70, LINK_DK, stroke=LINK, body=f"{name}\nRL expert" if i < 3 else name, size=15)
    arrow(s, 233, 300, 300, y + 35, color=MUTED, width=1.25)
    arrow(s, 550, y + 35, 640, 300, color=LINK, width=1.25, dashed=True)
box(s, 640, 240, 220, 120, GRN_DK, stroke=GRN_HI, body="OPD\none student\nmodel", size=18, sw=2)
box(s, 300, 520, 250, 140, YEL_DK, stroke=YEL,
    body="RL stage\nasync rollouts, staleness\ntrain-inference mismatch\nsandbox environments", size=14, bold=False)
box(s, 640, 520, 220, 140, YEL_DK, stroke=YEL,
    body="OPD stage\nnumber of teachers\nsampled token or\nfull vocabulary", size=14, bold=False)
arrow(s, 425, 520, 425, 476, color=YEL, width=1.5)
arrow(s, 750, 520, 750, 360, color=YEL, width=1.5)
label(s, 900, 130, 337, 30, "examples in the reports", size=16, color=MUTED, align="left")
ex = [("DeepSeek-V4.1-Flash", "40+ teachers, full vocabulary"),
      ("Kimi K3", "9 experts: 3 domains × 3 efforts"),
      ("Nemotron 3.5 Super", "teachers branched at RL step 120"),
      ("KAT-Coder-V2.5", "SWE, tool use, terminal, web"),
      ("variant: MiMo-V2.6", "one mixed RL run, then MOPD2")]
for i, (m, d_) in enumerate(ex):
    box(s, 900, 170 + i * 90, 337, 76, CHIP, stroke=EDGE, body=f"{m}\n{d_}", size=14, bold=False)

# ------------------------------------------------------------------ 2. mask shapes
s = d.slide().s
title(s, "Which tokens each mismatch criterion keeps",
      "Green: kept.  Dark: masked.  Log axes.  Thresholds: ratio band [0.5, 5], |difference| ≤ 0.3, binary KL ≤ 0.05 (φ illustrative)")
def kl_b(p, q):
    eps = 1e-12
    p = min(max(p, eps), 1 - eps); q = min(max(q, eps), 1 - eps)
    return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))
crit = [("ratio band (IcePop)", lambda mu, pi: 0.5 <= pi / mu <= 5.0),
        ("probability difference (IPO)", lambda mu, pi: abs(pi - mu) <= 0.3),
        ("binary KL, both ways (KPop)", lambda mu, pi: kl_b(pi, mu) <= 0.05 and kl_b(mu, pi) <= 0.05)]
N = 28
side = 336
cell = side / N
lo, hi = -4.0, 0.0
def val(k):
    return 10 ** (lo + (hi - lo) * (k + 0.5) / N)
def pos(v):
    return (math.log10(v) - lo) / (hi - lo) * side
pts = [(0.01, 0.06, "A"), (0.90, 0.20, "B")]
for k, (name, f) in enumerate(crit):
    x0 = 70 + k * 400
    y0 = 170
    label(s, x0 - 20, 120, side + 40, 34, name, size=18, bold=True)
    for i in range(N):
        for j in range(N):
            keep = f(val(i), val(j))
            sh.rect(s, t, x0 + i * cell, y0 + side - (j + 1) * cell, cell - 0.6, cell - 0.6,
                    fill=GRN if keep else CHIP, stroke=None)
    for (mu, pi, tag) in pts:
        kept = f(mu, pi)
        cx, cy = x0 + pos(mu), y0 + side - pos(pi)
        sh.rect(s, t, cx - 9, cy - 9, 18, 18, fill=WHITE if kept else YEL, stroke=CHIP,
                shape=MSO_SHAPE.OVAL)
        label(s, cx - 9, cy - 9, 18, 18, tag, size=11, color=CHIP, bold=True)
    for v, txt in [(1e-4, "1e-4"), (1e-2, "0.01"), (1.0, "1")]:
        label(s, x0 + pos(v) - 25, y0 + side + 6, 50, 20, txt, size=12, color=MUTED)
    label(s, x0, y0 + side + 28, side, 22, "inference probability μ  →", size=13, color=MUTED)
    label(s, x0 - 66, y0 + side / 2 - 12, 62, 24, "π ↑", size=13, color=MUTED, align="right")
label(s, 43, 590, 1194, 26, "A: 0.01 → 0.06 (6× ratio, difference 0.05).  B: 0.90 → 0.20 (0.22× ratio, difference 0.70).  White: kept.  Yellow: masked",
      size=14, color=WHITE, align="left")
label(s, 43, 622, 1194, 26, "same axes for π: 1e-4 at the bottom, 1 at the top.  Ratio band: fixed-width diagonal.  Binary KL: wider ratios at small probabilities",
      size=13, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. allocation rules
s = d.slide().s
title(s, "Rollouts per prompt by pass rate p",
      "Bars: rollouts for one prompt, computed.  Top three rows share the same mean of 16")
ps = [0.05 + 0.1 * i for i in range(10)]
def scale(ws):
    m = sum(ws) / len(ws)
    return [16 * w / m for w in ws]
rows = [("uniform (GRPO)", [16] * 10, LINK_DK, LINK),
        ("Neyman, G ∝ σ", scale([math.sqrt(p * (1 - p)) for p in ps]), GRN_DK, GRN_HI),
        ("Reinforce-Ada, ∝ 1/√p", scale([1 / math.sqrt(p) for p in ps]), YEL_DK, YEL)]
bx0, bw, gapb = 330, 78, 14
hmax = 40.0
for r, (name, gs, fill, stroke) in enumerate(rows):
    base = 215 + r * 122
    label(s, 43, base - 70, 280, 34, name, size=17, bold=True, align="left")
    for i, g in enumerate(gs):
        h = 90 * min(g, hmax) / hmax
        sh.rect(s, t, bx0 + i * (bw + gapb), base - h, bw, h, fill=fill, stroke=stroke)
        label(s, bx0 + i * (bw + gapb), base - h - 22, bw, 20, f"{g:.0f}", size=12, color=WHITE)
label(s, 43, 500, 280, 34, "DAPO dynamic sampling", size=17, bold=True, align="left")
for i, p in enumerate(ps):
    same = p ** 16 + (1 - p) ** 16
    keep = 16 * (1 - same)
    h = 90 * keep / hmax
    base = 590
    sh.rect(s, t, bx0 + i * (bw + gapb), base - h, bw, h, fill=CHIP, stroke=MUTED, dash=DASH)
    label(s, bx0 + i * (bw + gapb), base - h - 22, bw, 20, f"{keep:.0f}", size=12, color=MUTED)
label(s, 43, 536, 280, 50, "16 per prompt; expected rollouts\nleft after all-same groups drop", size=12, color=MUTED, align="left")
for i, p in enumerate(ps):
    label(s, bx0 + i * (bw + gapb), 600, bw, 24, f"p={p:.2f}", size=13, color=MUTED)
label(s, 330, 640, 900, 26, "computed for binary reward; Reinforce-Ada bounds omitted; reports here state a fixed count",
      size=14, color=MUTED, align="left")

d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
