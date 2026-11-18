"""gen_intro_pptx.py: the intro figure (what Engram buys) and the structure figures of the Engram hands-on article, as native pptx shapes.

    /usr/bin/python3 gen_figs_pptx.py <out.pptx>

Slides, in order: engram-why, overview, compress, hash, gate, placement, training-step, comparison.
Roles (ZN-25, ZN-29), each with a colour and a faint pattern so that it reads without colour:
  blue + "x" grid   the GPT backbone (embedding, blocks, output head)
  green + "/"       Engram (the table, key and value, the gate)
  yellow + dotted   computed from the token ids alone (compressed ids, n-grams, row ids)
  grey, no pattern  data and values (text, hidden state)
The numbers of the trained model come from zenmai-lab 7d12d41 (engram.py, model.py) and the published
trace traces/nanogpt-hastings.json (seed 1337).
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
TEMPLATES = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, TEMPLATES)
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures.pptx"

GRN, GRN_DK = RGBColor(36, 160, 70), RGBColor(18, 64, 34)
BLU, BLU_DK = RGBColor(40, 150, 240), RGBColor(16, 44, 72)
YEL, YEL_DK = RGBColor(251, 211, 50), RGBColor(80, 66, 14)
GREY, EDGE, CHIP = RGBColor(52, 56, 64), RGBColor(110, 116, 124), RGBColor(22, 26, 30)
MUTED, WHITE = RGBColor(160, 160, 168), RGBColor(245, 245, 248)
ROLE = {"backbone": (BLU_DK, BLU, "cross"), "engram": (GRN_DK, GRN, "diagonal"),
        "ids": (YEL_DK, YEL, "grid"), "data": (GREY, EDGE, None)}

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align, anchor="middle")


def box(s, x, y, w, h, role, body="", size=15, radius=0.1, dash=None, sw=1.5, color=WHITE):
    fill, stroke, pat = ROLE[role]
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    pattern_fill(sp, pat, fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def frame(s, x, y, w, h):
    return sh.rect(s, t, x, y, w, h, fill=CHIP, stroke=EDGE, sw=1, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)


def title(s, head, roles):
    label(s, 43, 22, 1190, 46, head, size=30, bold=True, align="left")
    names = {"backbone": "GPT backbone", "engram": "Engram", "ids": "from token ids only", "data": "data"}
    x = 43
    for r in roles:
        box(s, x, 76, 34, 22, r)
        label(s, x + 42, 74, 220, 26, names[r], size=15, color=MUTED, align="left")
        x += 74 + 10 * len(names[r])


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width)


def seg(s, pts, color=WHITE, width=2):
    """A polyline with one arrowhead, at the last point."""
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.util import Pt
    for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
        c.line.color.rgb = color
        c.line.width = Pt(width)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    arrow(s, x1, y1, x2, y2, color=color, width=width)


def num(s, x, y, n):
    c = sh.rect(s, t, x, y, 30, 30, fill=WHITE, stroke=WHITE, sw=1, shape=MSO_SHAPE.OVAL)
    sh._write(c.text_frame, t, str(n), 15, RGBColor(10, 10, 12), True, "center", "middle")
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0




# ---------------------------------------------------------------- what Engram buys (as-is / to-be)
s = d.slide().s
title(s, "What Engram buys (the paper's view)", ["data", "ids", "backbone", "engram"])
BH, STEP = 44, 54
# left: without Engram, all inside GPU memory
frame(s, 43, 120, 560, 540)
label(s, 43, 126, 560, 30, "Without Engram", size=19, bold=True)
label(s, 63, 160, 520, 24, "GPU memory", size=14, color=MUTED, align="left")
box(s, 83, 190, 480, 40, "data", body="tokens   … Little Red Riding", size=15)
arrow(s, 323, 230, 323, 262)
for i in range(6):
    y = 262 + i * STEP
    build = i < 3
    box(s, 83, y, 480, BH, "backbone", body=f"block {i}   " + ("build the name" if build else "think"),
        size=14, dash=MSO_LINE_DASH_STYLE.DASH if build else None)
label(s, 83, 600, 480, 30, "3 of 6 blocks think", size=17, bold=True)
# right: with Engram; the table sits outside GPU memory
frame(s, 633, 120, 604, 540)
label(s, 633, 126, 604, 30, "With Engram", size=19, bold=True)
sh.rect(s, t, 648, 160, 316, 488, fill=CHIP, stroke=BLU, sw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
label(s, 660, 164, 290, 24, "GPU memory", size=14, color=BLU, align="left")
sh.rect(s, t, 984, 160, 238, 488, fill=CHIP, stroke=GRN, sw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
label(s, 996, 164, 220, 24, "CPU memory", size=14, color=GRN, align="left")
box(s, 663, 190, 286, 40, "data", body="tokens   … Little Red Riding", size=15)
arrow(s, 806, 230, 806, 246)
box(s, 663, 246, 286, 34, "ids", body="16 row numbers", size=14)
box(s, 1002, 200, 202, 300, "engram", body="Engram table\n\nfar larger than\nthe model", size=16)
arrow(s, 949, 263, 1002, 263, color=YEL, width=2.5)
arrow(s, 806, 280, 806, 296)
for i in range(6):
    y = 296 + i * STEP
    build = i < 1
    box(s, 663, y, 286, BH, "backbone", body=f"block {i}   " + ("build the name" if build else "think"),
        size=14, dash=MSO_LINE_DASH_STYLE.DASH if build else None)
seg(s, [(1002, 345), (975, 345), (975, 345), (949, 345)], color=GRN, width=3)
label(s, 663, 612, 286, 30, "5 of 6 blocks think", size=17, bold=True)
label(s, 990, 512, 226, 66, "the 16 rows are\nfetched while\nblock 0 runs", size=14, color=GRN, bold=True)
label(s, 43, 668, 1194, 30, "illustrative · dashed outline: build the name · the row numbers come from the token ids alone, before block 0", size=14, color=MUTED)

# ---------------------------------------------------------------- n-grams ending at the current position
# counts: WikiText-103 train split, GPT-2 tokens, exact match (zenmai-lab 7d12d41 data/train.bin)
s = d.slide().s
title(s, "n-grams: the tokens that end at the current position", ["data", "ids"])
toks = ["The", "girl", "was", "called", "Little", "Red", "Riding"]
x = 60
pos = {}
for w in toks:
    wd = 30 + 15 * len(w)
    box(s, x, 130, wd, 46, "data", body=w, size=18)
    pos[w] = (x, wd)
    x += wd + 10
box(s, x, 130, 110, 46, "data", body="Hood ?", size=18, dash=MSO_LINE_DASH_STYLE.DASH)
label(s, x - 20, 180, 150, 26, "next token", size=14, color=MUTED)
rx, rw = pos["Riding"]
label(s, rx - 40, 180, rw + 80, 26, "current position", size=14, color=YEL, bold=True)
rows = [("1-gram", ["Riding"], 404, 41, "most often next: of (95 times)"),
        ("2-gram", ["Red", "Riding"], 45, 40, ""),
        ("3-gram", ["Little", "Red", "Riding"], 24, 24, "")]
label(s, 60, 236, 330, 26, "n tokens ending here", size=15, color=MUTED, align="left")
label(s, 470, 236, 220, 26, "seen in training", size=15, color=MUTED, align="left")
label(s, 700, 236, 520, 26, "share followed by Hood", size=15, color=MUTED, align="left")
for k, (name, ws, n, hood, note) in enumerate(rows):
    y = 270 + k * 118
    label(s, 60, y + 10, 90, 30, name, size=17, bold=True, align="left")
    xx = 150
    for w in ws:
        wd = 26 + 13 * len(w)
        box(s, xx, y, wd, 46, "ids", body=w, size=16)
        xx += wd + 6
    label(s, 470, y + 8, 200, 30, f"{n} times", size=17, bold=True, align="left")
    W = 440
    sh.rect(s, t, 700, y + 8, W, 30, fill=CHIP, stroke=EDGE, sw=1, shape=MSO_SHAPE.RECTANGLE)
    box(s, 700, y + 8, max(4, round(W * hood / n)), 30, "ids", radius=0.0)
    label(s, 1150, y + 8, 110, 30, f"{hood / n:.0%}", size=18, bold=True, align="left")
    label(s, 700, y + 44, 520, 26, f"Hood {hood} of {n}" + (f" · {note}" if note else ""), size=13, color=MUTED, align="left")
sh.rect(s, t, 48, 382, 1200, 228, fill=None, stroke=GRN, sw=2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
label(s, 60, 612, 700, 26, "Engram looks up the 2-gram and the 3-gram", size=16, color=GRN, bold=True, align="left")
label(s, 43, 660, 1194, 30, "counts: WikiText-103 training text, exact GPT-2 tokens · Engram does not count; it reads numbers learned for each n-gram", size=13, color=MUTED)

d.save(OUT)
import strip_branding  # noqa: E402

strip_branding.main(OUT, OUT)
print(OUT)
