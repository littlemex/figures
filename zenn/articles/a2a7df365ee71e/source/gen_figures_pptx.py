"""Figures for the Zenn article a2a7df365ee71e (tierbook: certified switch to a cheap student), as native pptx shapes.

    /usr/bin/python3 gen_figures_pptx.py <out.pptx>

Built like review-html's zenn-doc template (nxd_interfaces_pptx.py): pptxkit's aws-dark-2024 template, black
background, short English labels, every role box carrying a faint pattern as well as its colour (ZN-25, ZN-29).
Roles: green = you declare it, blue = tierbook does it, yellow = serving (router and models).
Numbers come from tierbook docs/verify/v0.5.0-distillation-loop.md (commit 36ea513).
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
TPLDIR = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, TPLDIR)
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
LINK = RGBColor(40, 150, 240)
LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)
RED = RGBColor(235, 96, 90)

ROLE_PATTERN = {GRN_DK: "diagonal", LINK_DK: "cross", YEL_DK: "grid"}
LEGEND = "Green (diagonal): you declare.   Blue (cross-hatch): tierbook.   Yellow (grid): serving"

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align, anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=16, color=WHITE, radius=0.1, sw=1.25, dash=None):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def you(s, x, y, w, h, body, size=16):
    return box(s, x, y, w, h, GRN_DK, stroke=GRN, body=body, size=size)


def tb(s, x, y, w, h, body, size=16):
    return box(s, x, y, w, h, LINK_DK, stroke=LINK, body=body, size=size)


def serve(s, x, y, w, h, body, size=16):
    return box(s, x, y, w, h, YEL_DK, stroke=YEL, body=body, size=size)


def plain(s, x, y, w, h, body, size=16, color=WHITE):
    return box(s, x, y, w, h, CHIP, stroke=EDGE, body=body, size=size, color=color)


def arrow(s, x1, y1, x2, y2, dashed=False, width=2.5):
    return sh.arrow(s, t, x1, y1, x2, y2, color=WHITE, width=width, dashed=dashed)


def title(s, head, sub=LEGEND):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


# 1. loop -------------------------------------------------------------------------------------------
s = d.slide().s
title(s, "The tierbook loop")
steps = [(43, 170, "1  Teacher answers", serve), (343, 170, "2  Student trains", serve),
         (643, 170, "3  Declare arms", you), (943, 170, "4  Certify", tb),
         (943, 360, "5  Export to router", tb), (643, 360, "6  Drift check", tb)]
for x, y, body, f in steps:
    f(s, x, y, 260, 90, body, size=20)
arrow(s, 303, 215, 343, 215)
arrow(s, 603, 215, 643, 215)
arrow(s, 903, 215, 943, 215)
arrow(s, 1073, 260, 1073, 360)
arrow(s, 943, 405, 903, 405)
arrow(s, 1073, 170, 1073, 145, dashed=True, width=1.5)
arrow(s, 1073, 145, 173, 145, dashed=True, width=1.5)
arrow(s, 173, 145, 173, 170, dashed=True, width=1.5)
label(s, 400, 113, 500, 24, "repeat as records grow", size=15, color=MUTED)
you(s, 43, 330, 500, 170, "", size=16)
label(s, 63, 340, 460, 30, "Declared by you", size=18, bold=True, color=GRN_HI, align="left")
label(s, 63, 375, 460, 115, "floor, alpha, held-out share\nrungs to test, threshold\nrequests to amortise over", size=17,
      align="left")

# 2. split and certify ------------------------------------------------------------------------------
s = d.slide().s
title(s, "Choose on one half, certify on the other")
plain(s, 43, 230, 230, 110, "Scored records\n1,200 items", size=18)
tb(s, 323, 230, 200, 110, "Split by\nhash(item)", size=18)
tb(s, 573, 140, 330, 120, "Selection half (~600)\ncheapest arm with\nlower bound >= floor", size=17)
tb(s, 573, 310, 330, 120, "Held-out half (~600)\nlower bound\n>= floor ?", size=17)
arrow(s, 273, 285, 323, 285)
arrow(s, 523, 260, 573, 200)
arrow(s, 523, 310, 573, 370)
arrow(s, 738, 260, 738, 310)
label(s, 748, 268, 160, 34, "chosen arm", size=15, color=MUTED, align="left")
tb(s, 953, 290, 250, 70, "certified", size=20)
plain(s, 953, 380, 250, 60, "unconfirmed", size=18, color=MUTED)
arrow(s, 903, 345, 953, 325)
arrow(s, 903, 395, 953, 410, dashed=True, width=1.5)
label(s, 905, 290, 50, 24, "yes", size=14, color=MUTED)
label(s, 905, 405, 50, 24, "no", size=14, color=MUTED)
label(s, 43, 500, 600, 30, "Wilson lower bound, alpha 0.05", size=17, color=MUTED, align="left")

# 3. held-out ladder --------------------------------------------------------------------------------
s = d.slide().s
title(s, "Held-out ladder at floor 0.85 (887 held-out items, alpha 0.025)", "The two cheapest arms that cleared selection, tested dearest first.  Blue (cross-hatch): adopted arm")
label(s, 43, 112, 420, 28, "Arm (cheapest at the bottom)", size=15, color=MUTED, align="left")
label(s, 500, 112, 180, 28, "Selection LB", size=15, color=MUTED)
label(s, 700, 112, 180, 28, "Held-out LB", size=15, color=MUTED)
label(s, 900, 112, 150, 28, "$ / 1M accepted", size=15, color=MUTED)
label(s, 1060, 112, 150, 28, "Result", size=15, color=MUTED)
rows = [("Teacher (Prismyra)", "0.886", "0.866", "46.7", "above the ladder", plain),
        ("Cascade: student -> teacher, 0.99", "0.888", "0.8515", "19.1", "1  pass: adopted", tb),
        ("Student alone (generation)", "0.871", "0.825", "13.9", "2  miss: stop", plain)]
y = 148
for name, sel, ho, cost, res, f in rows:
    f(s, 43, y, 440, 74, name, size=17)
    label(s, 500, y, 180, 74, sel, size=20)
    label(s, 700, y, 180, 74, ho, size=20, bold=res[0] in "12")
    label(s, 900, y, 150, 74, cost, size=20)
    label(s, 1060, y, 160, 74, res, size=17, bold=res.startswith("1"))
    y += 92
arrow(s, 1220, 260, 1220, 340, width=3)
label(s, 43, 520, 1170, 30, "Order fixed on the selection half", size=17, color=MUTED, align="left")

# 4. generation version: input, target, loss -----------------------------------------------------------
s = d.slide().s
title(s, "Training the 0.8B student (generation version)", "One teacher-labelled headline")
plain(s, 43, 130, 560, 170, "Input (chat template)\n<|im_start|>user\nWhy Home Depot Stumbled on Earnings<|im_end|>\n<|im_start|>assistant", size=16)
serve(s, 683, 130, 550, 80, "Qwen3.5-0.8B", size=20)
plain(s, 683, 230, 550, 70, "Target: bearish<|im_end|>   (teacher's label)", size=17)
arrow(s, 603, 215, 683, 170)
tb(s, 43, 340, 1190, 120, "Loss: next-token cross-entropy over the full vocabulary, answer tokens only\n-[ log P(bear) + log P(ish | bear) + log P(<|im_end|> | bearish) ] / 3", size=18)
plain(s, 43, 490, 1190, 70, "Serving: generate until <|im_end|> and read the label.  Accuracy 0.873 on 1,200 items", size=17)

# 5. vLLM Semantic Router ---------------------------------------------------------------------------
s = d.slide().s
title(s, "Routed run through vLLM Semantic Router (300 items)")
plain(s, 43, 250, 190, 90, "Request", size=20)
serve(s, 283, 220, 290, 150, "vLLM Semantic Router\nconfidence looper", size=18)
serve(s, 663, 140, 290, 100, "0.8B student\nvLLM on a GPU", size=18)
serve(s, 663, 360, 290, 100, "Teacher\nPrismyra", size=18)
arrow(s, 233, 295, 283, 295)
arrow(s, 573, 250, 663, 190, width=3)
label(s, 560, 150, 110, 40, "1  all 300", size=15, color=MUTED)
arrow(s, 573, 340, 663, 410, dashed=True, width=1.5)
label(s, 420, 420, 150, 50, "2  conf < 0.98\n31 items", size=15, color=MUTED)
tb(s, 1003, 120, 230, 380, "", size=16)
label(s, 1013, 128, 210, 30, "Result", size=19, bold=True, color=LINK)
label(s, 1013, 165, 210, 320, "student 269\nteacher 31\naccepted 267\nroute match 300/300\nfloor 0.85\ndrift: consistent\nsame conf formula\nas certification",
      size=17)

# 6. CPU throughput -----------------------------------------------------------------------------------
s = d.slide().s
title(s, "Generating 0.8B on a c8g.xlarge (4 vCPU): items per hour", "Blue (cross-hatch): the run priced by tierbook")
bars = [("batch 8", 7105, plain), ("batch 1", 12918, plain), ("batch 8, padded head", 19488, plain),
        ("batch 16, padded head", 19612, tb)]
x0, base, top = 380, 120, 1160
for i, (name, v, f) in enumerate(bars):
    y = 140 + i * 105
    label(s, 43, y, 320, 70, name, size=19, align="left")
    w = (top - x0) * v / 19612
    f(s, x0, y, w, 70, "")
    label(s, x0 + w - 170, y, 160, 70, f"{v:,}", size=20, bold=True, align="right")
label(s, 43, 580, 1190, 28, "output layer: 8 rows 871 ms, 16 rows 52 ms", size=17, color=MUTED, align="left")

# 7. cost ---------------------------------------------------------------------------------------------
s = d.slide().s
title(s, "Cost per 1M accepted tasks (second look, 887 held-out items)",
      "Blue (cross-hatch): arm adopted at each floor.  Priced from GPU answers, batch 16, full utilisation, teacher GPU shared")
bars = [("Teacher alone (L40S, $3.80/h)", 46.7, "$46.7  (1.00×)", plain),
        ("Cascade, CPU student -> teacher, floor 0.85", 19.1, "$19.1  (0.41×)", tb),
        ("CPU student alone, floor 0.80", 13.9, "$13.9  (0.30×)", tb)]
for i, (name, v, txt, f) in enumerate(bars):
    y = 150 + i * 120
    label(s, 43, y, 440, 80, name, size=18, align="left")
    w = 480 * v / 46.7
    f(s, 500, y, w, 80, "")
    label(s, 500 + w + 15, y, 240, 80, txt, size=20, bold=True, align="left")
label(s, 43, 520, 1190, 28, "student per 1M requests: inference $10.2 + teaching $1.6", size=17, color=MUTED, align="left")

# 8. drift ranges -------------------------------------------------------------------------------------
s = d.slide().s
title(s, "Drift check: 300 items, floor 0.85, alpha 0.05", "Accepted items out of 300")
x0, x1, lo, hi = 63, 1213, 225, 285
X = lambda k: x0 + (x1 - x0) * (k - lo) / (hi - lo)
plain(s, X(225), 220, X(242.5) - X(225), 110, "contradicted\n<= 242", size=17)
box(s, X(242.5), 220, X(267.5) - X(242.5), 110, YEL_DK, stroke=YEL, body="consistent\n243 - 267", size=18)
tb(s, X(267.5), 220, X(285) - X(267.5), 110, "confirmed\n>= 268", size=18)
for k in (230, 240, 250, 260, 270, 280):
    label(s, X(k) - 30, 340, 60, 26, str(k), size=15, color=MUTED)
arrow(s, X(267), 440, X(267), 335, width=3)
label(s, X(267) - 260, 445, 520, 30, "267: vLLM Semantic Router run", size=17)
label(s, 43, 540, 1190, 28, "lower bound >= floor: confirmed.  upper bound < floor: contradicted", size=17, color=MUTED,
      align="left")

# 9. architecture -------------------------------------------------------------------------------------
s = d.slide().s
title(s, "tierbook sits beside the request path", "Thick solid: request path.   Dashed: records and config")
plain(s, 43, 150, 170, 80, "Client", size=20)
serve(s, 283, 140, 300, 100, "Router\n(vLLM SR / Prismyra)", size=18)
serve(s, 663, 120, 240, 70, "Student (CPU)", size=18)
serve(s, 663, 210, 240, 70, "Teacher (GPU)", size=18)
arrow(s, 213, 190, 283, 190, width=4)
arrow(s, 583, 170, 663, 155, width=4)
arrow(s, 583, 210, 663, 245, width=4)
plain(s, 983, 150, 250, 90, "Answer records\n(observations)", size=17)
arrow(s, 903, 160, 983, 180, dashed=True, width=1.5)
arrow(s, 903, 245, 983, 215, dashed=True, width=1.5)
you(s, 983, 300, 250, 80, "Grader\n(accepted?)", size=18)
arrow(s, 1108, 240, 1108, 300, dashed=True, width=1.5)
tb(s, 283, 300, 300, 80, "policy.json\n-> router config", size=17)
arrow(s, 433, 300, 433, 240, dashed=True, width=1.5)
tb(s, 543, 440, 380, 130, "tierbook\nderive / certify / drift", size=20)
arrow(s, 643, 440, 583, 380, dashed=True, width=1.5)
arrow(s, 1108, 380, 923, 470, dashed=True, width=1.5)
you(s, 43, 430, 400, 70, "candidates.json: arms, prices", size=17)
you(s, 43, 520, 400, 70, "declarations.json: floor, alpha", size=17)
arrow(s, 443, 465, 543, 490, dashed=True, width=1.5)
arrow(s, 443, 555, 543, 530, dashed=True, width=1.5)
label(s, 43, 610, 1190, 26, "Green (diagonal): you.   Blue (cross-hatch): tierbook.   Yellow (grid): serving", size=16,
      color=MUTED, align="left")

# 10. headline result -----------------------------------------------------------------------------------
s = d.slide().s
title(s, "0.30x the teacher's cost at 2.3 points lower accuracy",
      "Blue (cross-hatch): certified on the held-out half.  Grey: teacher")
label(s, 43, 120, 330, 28, "Arm", size=15, color=MUTED, align="left")
label(s, 390, 120, 400, 28, "Cost per 1M accepted (vs teacher)", size=15, color=MUTED, align="left")
label(s, 830, 120, 400, 28, "Accuracy", size=15, color=MUTED, align="left")
rows = [("Teacher (GPU)", 46.7, "$46.7  1.00x", 0.896, False, ""),
        ("Cascade: student -> teacher", 19.1, "$19.1  0.41x", 0.878, True, "floor 0.85, 2nd look"),
        ("CPU student alone", 13.9, "$13.9  0.30x", 0.873, True, "floor 0.80")]
for k, (name, cost, ctxt, acc, cert, note) in enumerate(rows):
    y = 160 + k * 135
    label(s, 43, y, 330, 50, name, size=19, bold=True, align="left")
    if note:
        label(s, 43, y + 46, 330, 30, note, size=15, color=MUTED, align="left")
    f = tb if cert else plain
    w = 260 * cost / 46.7
    f(s, 390, y + 10, w, 60, "")
    label(s, 390 + w + 10, y + 10, 160, 60, ctxt, size=17, bold=True, align="left")
    wa = 300 * acc
    f(s, 830, y + 10, wa, 60, "")
    label(s, 830 + wa + 10, y + 10, 90, 60, f"{acc:.3f}", size=17, bold=True, align="left")
label(s, 830, 570, 400, 26, "teacher, student: 1,200 items.  cascade: 887 held-out", size=15, color=MUTED, align="left")
label(s, 43, 570, 760, 26, "Priced from GPU answers at batch 16, full utilisation", size=15, color=MUTED, align="left")

# 11. two-sided interval and the false-pass tail --------------------------------------------------------
import math  # noqa: E402
from pptx.util import Pt  # noqa: E402
s = d.slide().s
title(s, "When can a below-floor arm pass?", "Worst case: true rate p = floor f = 0.85, n = 600, alpha = 0.05.  Yellow (grid): alpha/2 tails")
F, N, Z = 0.85, 600, 1.96
SE = math.sqrt(F * (1 - F) / N)
XL, XR, YB, YT = 120, 1160, 500, 170
lo, hi = F - 4.2 * SE, F + 4.2 * SE
px = lambda v: XL + (XR - XL) * (v - lo) / (hi - lo)
pdf = lambda v: math.exp(-0.5 * ((v - F) / SE) ** 2)
py = lambda v: YB - (YB - YT) * pdf(v)


def area(a, b, fill, stroke):
    xs = [a + (b - a) * k / 60 for k in range(61)]
    ff = s.shapes.build_freeform(sh.U(px(a)), sh.U(YB))
    ff.add_line_segments([(sh.U(px(v)), sh.U(py(v))) for v in xs] + [(sh.U(px(b)), sh.U(YB))], close=True)
    sp = ff.convert_to_shape()
    sp.line.color.rgb = stroke
    sp.line.width = Pt(1)
    if ROLE_PATTERN.get(fill):
        pattern_fill(sp, ROLE_PATTERN[fill], fill, stroke)
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    return sp


area(lo, hi, GREY, EDGE)
cut_hi, cut_lo = F + Z * SE, F - Z * SE
area(cut_hi, hi, YEL_DK, YEL)
area(lo, cut_lo, YEL_DK, YEL)
sh.rect(s, t, XL, YB, XR - XL, 2, fill=EDGE)
arrow(s, px(F), YB, px(F), YT - 30, dashed=True, width=1.5)
label(s, px(F) - 160, YT - 62, 320, 30, "floor f = true rate p", size=17)
arrow(s, px(cut_hi), YB + 40, px(cut_hi), YB, width=2)
label(s, px(cut_hi) - 210, YB + 42, 420, 28, "f + z * SE: lower bound reaches f", size=16)
label(s, px(cut_hi) + 30, 330, 300, 90, "alpha/2 = 0.025\nlower bound above p:\nfalse pass", size=17, bold=True, align="left")
label(s, px(cut_lo) - 320, 380, 300, 90, "alpha/2 = 0.025\nupper bound below p", size=17, bold=True, align="right")
for v in (0.82, 0.84, 0.86, 0.88):
    label(s, px(v) - 40, YB + 82, 80, 24, f"{v:.2f}", size=15, color=MUTED)
label(s, XL, YB + 108, XR - XL, 26, "measured acceptance rate p-hat (SE = 0.0146)", size=15, color=MUTED)

# 12. selection, true and false positives -----------------------------------------------------------------
s = d.slide().s
title(s, "Why choose on one half and certify on the other", "Simulated: 600 items per half, floor 0.85, alpha 0.05, arms independent")
label(s, 43, 115, 560, 28, "Truth vs decision", size=17, bold=True, align="left")
label(s, 233, 148, 180, 28, "certified", size=15, color=MUTED)
label(s, 423, 148, 180, 28, "not certified", size=15, color=MUTED)
label(s, 43, 185, 180, 70, "true rate\n>= floor", size=15, color=MUTED, align="left")
label(s, 43, 270, 180, 70, "true rate\n< floor", size=15, color=MUTED, align="left")
tb(s, 233, 185, 180, 70, "true positive", size=16)
plain(s, 423, 185, 180, 70, "false negative\n(missed)", size=15)
box(s, 233, 270, 180, 70, YEL_DK, stroke=YEL, body="false positive\n<= alpha/2", size=15)
tb(s, 423, 270, 180, 70, "true negative", size=16)
label(s, 663, 115, 560, 28, "Chance a below-floor arm (true 0.84) passes", size=17, bold=True, align="left")
data = [(1, 0.003, 0.004), (9, 0.031, 0.004), (37, 0.119, 0.003)]
for k, (K, sel_only, held) in enumerate(data):
    y = 160 + k * 120
    label(s, 663, y, 140, 50, f"{K} arm" + ("" if K == 1 else "s"), size=17, align="left")
    w1 = 380 * sel_only / 0.12
    box(s, 803, y, max(w1, 4), 40, YEL_DK, stroke=YEL)
    label(s, 803 + max(w1, 4) + 8, y, 160, 40, f"{sel_only:.3f}", size=16, align="left")
    w2 = 380 * held / 0.12
    tb(s, 803, y + 46, max(w2, 4), 40, "")
    label(s, 803 + max(w2, 4) + 8, y + 46, 160, 40, f"{held:.3f}", size=16, align="left")
label(s, 663, 520, 570, 26, "Yellow (grid): judged on the selection half alone", size=15, color=MUTED, align="left")
label(s, 663, 548, 570, 26, "Blue (cross-hatch): chosen on selection, certified on held-out", size=15, color=MUTED, align="left")
label(s, 43, 380, 560, 120, "Best measured rate on the selection half\nis inflated: +2.1 pt with 9 arms, +3.1 pt with 37", size=16, align="left")

d.save(OUT)
import strip_branding  # noqa: E402

strip_branding.main(OUT, OUT)
print(OUT)
