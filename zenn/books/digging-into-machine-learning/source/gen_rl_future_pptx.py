"""gen_rl_future_pptx.py: figures for the future-directions chapter (3 slides).

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


# ------------------------------------------------------------------ 1. three layers
s = d.slide().s
title(s, "Three layers of open problems in RL post-training",
      "Green: the layer.  Blue: current mitigation.  Yellow: what remains open.  Schematic")
layers = [("numerical precision",
           "FP8 / FP4 rollouts can move ρ\naway from 1; low-bit models\ncan lose long reasoning",
           "rollout activation fixes,\nsame quantization on both sides,\nOPD to recover low-bit models",
           "few measurements linking\nquantization error to stability"),
          ("training system",
           "slow rollouts, heavy weight\nsync, fragile environments",
           "async rollouts, delta weight sync,\nrouter freezing, deterministic kernels",
           "cost of long agent tasks,\nenvironment loopholes"),
          ("science of RL",
           "what RL learns, reward\ntrust, how it scales",
           "statistical tests, hacking\ndetectors, scaling-law fits",
           "many results rest on\none lab or one paper")]
heads = [("layer", 43, 220), ("problem", 283, 300), ("mitigation now", 603, 320), ("still open", 943, 294)]
for name, x, w in heads:
    label(s, x, 116, w, 28, name, size=16, color=MUTED, bold=True)
for i, (lay, prob, mit, opn) in enumerate(layers):
    y = 156 + i * 160
    box(s, 43, y, 220, 130, GRN_DK, stroke=GRN_HI, body=lay, size=18, sw=2)
    box(s, 283, y, 300, 130, CHIP, stroke=EDGE, body=prob, size=15, bold=False)
    box(s, 603, y, 320, 130, LINK_DK, stroke=LINK, body=mit, size=15, bold=False)
    box(s, 943, y, 294, 130, YEL_DK, stroke=YEL, body=opn, size=15, bold=False)
    arrow(s, 263, y + 65, 283, y + 65, color=MUTED, width=1.25)
    arrow(s, 583, y + 65, 603, y + 65, color=MUTED, width=1.25)
    arrow(s, 923, y + 65, 943, y + 65, color=MUTED, width=1.25)

# ------------------------------------------------------------------ 2. FP4 consistency (HiFloat4 Table 1)
s = d.slide().s
title(s, "Raising only the training side hurts; rollout precision matters",
      "Qwen2.5-3B, GRPO, GSM8K accuracy (%), reported in HiFloat4 Table 1.  Upper bar: HiF4.  Lower bar: MXFP4")
rows = [("BF16", "BF16", 86.96, 86.96),
        ("FP4", "BF16", 86.88, 86.20),
        ("FP4", "W4A16", 85.22, 81.57),
        ("FP4", "W4A8", 85.06, 79.91),
        ("FP4", "W16A4", 84.30, 77.71),
        ("FP4", "FP4", 82.03, 73.31),
        ("BF16", "FP4", 78.01, 50.57)]
label(s, 43, 120, 200, 26, "training", size=15, color=MUTED, bold=True, align="left")
label(s, 163, 120, 200, 26, "rollout", size=15, color=MUTED, bold=True, align="left")
x0, xmax = 330, 1180
lo, hi = 40.0, 90.0
def bx(v):
    return x0 + (xmax - x0) * (v - lo) / (hi - lo)
for k, (tr, ro, h4, mx) in enumerate(rows):
    y = 158 + k * 62
    hl = (tr == "BF16" and ro == "FP4")
    label(s, 43, y, 110, 48, tr, size=16, bold=hl, color=YEL if hl else WHITE, align="left")
    label(s, 163, y, 150, 48, ro, size=16, bold=hl, color=YEL if hl else WHITE, align="left")
    sh.rect(s, t, x0, y + 4, bx(h4) - x0, 20, fill=GRN_DK, stroke=GRN_HI)
    label(s, bx(h4) + 6, y, 140, 26, f"{h4:.2f} HiF4", size=13, color=WHITE, align="left")
    sh.rect(s, t, x0, y + 26, bx(mx) - x0, 20, fill=LINK_DK, stroke=LINK)
    label(s, bx(mx) + 6, y + 23, 140, 26, f"{mx:.2f} MXFP4", size=13, color=WHITE, align="left")
for v in (40, 60, 80, 90):
    sh.rect(s, t, bx(v) - 1, 590, 2, 10, fill=MUTED)
    label(s, bx(v) - 30, 602, 60, 22, f"{v}", size=13, color=MUTED)
label(s, 330, 628, 900, 26, "axis starts at 40.  Yellow row: training back to BF16, rollout still FP4: lower than FP4 on both sides",
      size=14, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. time budget
s = d.slide().s
title(s, "Where RL time and cost go, and how weight sync shrank",
      "Left: MiMo-V2.6-Pro RL cost shares (reported).  Right: reported weight-sync times, before → after")
box(s, 43, 120, 560, 520, CHIP, stroke=EDGE, radius=0.04)
label(s, 63, 132, 520, 30, "RL cost share (MiMo-V2.6-Pro)", size=17, bold=True)
shares = [("rollout", 43.8, LINK_DK, LINK), ("training", 43.5, GRN_DK, GRN_HI), ("grader", 12.7, YEL_DK, YEL)]
yb = 200
for name, v, fill, stroke in shares:
    w = 360 * v / 50.0
    label(s, 63, yb, 110, 40, name, size=16, align="left")
    sh.rect(s, t, 180, yb + 6, w, 30, fill=fill, stroke=stroke)
    label(s, 180 + w + 8, yb + 4, 80, 32, f"{v}%", size=15, align="left")
    yb += 70
label(s, 63, 430, 520, 60, "verl docs: rollout ≈ 70% of time\nin DAPO 32B training", size=16, color=WHITE)
label(s, 63, 520, 520, 60, "1,568 prompts × 16 rollouts per step\n$2.6M (Pro) and $0.9M (Flash) for RL", size=14, color=MUTED)
box(s, 637, 120, 600, 520, CHIP, stroke=EDGE, radius=0.04)
label(s, 657, 132, 560, 30, "weight sync, trainer → inference", size=17, bold=True)
syncs = [("Kimi-K2 1T, SGLang + Mooncake RDMA", 53.0, 7.2),
         ("Qwen3-235B-A22B, verl delta sync", 256.0, 13.2)]
yb = 200
for name, a, b in syncs:
    label(s, 657, yb, 560, 26, name, size=15, align="left")
    wa = 440 * a / 260.0
    wb = 440 * b / 260.0
    sh.rect(s, t, 677, yb + 34, wa, 24, fill=GREY, stroke=EDGE)
    label(s, 677 + wa + 8, yb + 32, 150, 26, f"{a:g} s" if a != 256 else "246–266 s", size=14, color=MUTED, align="left")
    sh.rect(s, t, 677, yb + 66, max(wb, 4), 24, fill=GRN_DK, stroke=GRN_HI)
    label(s, 677 + max(wb, 4) + 8, yb + 64, 150, 26, f"{b:g} s" if b != 13.2 else "11.4–14.9 s", size=14, align="left")
    yb += 130
label(s, 657, 470, 560, 60, "checkpoint-engine: about 20 s for Kimi-K2 1T\n(different transport and date)", size=15, color=WHITE)
label(s, 657, 560, 560, 50, "upper bar: before.  lower bar: after.  bars to scale", size=14, color=MUTED)

d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
