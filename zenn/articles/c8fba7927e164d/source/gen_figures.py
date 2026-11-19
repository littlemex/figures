"""gen_figures.py: figures for the Zenn article on EC2 Capacity Manager "Check supportability".

    /usr/bin/python3 gen_figures.py <out.pptx>

Native shapes with pptxkit on the AWS dark template. Text is English (house rule ZN-18), with identifiers as
written in the article (High, Medium, Low, API and file names).

Universal design rules used in every figure:
- Green, amber and red (each with its own pattern) mean only the scores High, Medium and Low.
- Other boxes are blue with a back-diagonal pattern (inputs and processing) or grey (outputs and notes).
- Scores also carry their name and a three-bar meter whose filled bars count 3, 2 or 1.
- Relations are told apart by line style and a word label, not by colour.
- All text is 24 pt or larger.

Sources: the AWS documentation pages cited in the article, the example response in "How to check
capacity", the Spot placement score pages and the Spot Placement Score Tracker README.
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from patterns import pattern_fill  # noqa: E402
from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures.pptx"

WHITE = RGBColor(245, 245, 248)
MUTED = RGBColor(178, 180, 188)
EDGE = RGBColor(120, 124, 132)
PANEL = RGBColor(30, 34, 40)
OFF = RGBColor(70, 74, 82)
ROLES = {
    "high": (RGBColor(18, 64, 34), RGBColor(59, 209, 111), "diagonal"),
    "med": (RGBColor(84, 58, 10), RGBColor(245, 170, 40), "cross"),
    "low": (RGBColor(88, 28, 28), RGBColor(240, 110, 110), "grid"),
    "info": (RGBColor(16, 44, 72), RGBColor(70, 165, 245), "backdiagonal"),
}
LEVEL = {"High": ("high", 3), "Medium": ("med", 2), "Low": ("low", 1)}

d = Deck(TPL, check_layout=False)
t = d.theme
t.font_ea = "Hiragino Sans"  # a Gothic face; the template's Meiryo is not on this machine and falls back to Mincho

_CJK = r"[\u3000-\u30ff\u4e00-\u9fff\uff00-\uffef]"


def tight(text):
    """Drop the half-width space between Japanese and Latin text: in a figure the font change already spaces it."""
    import re
    text = re.sub(rf"(?<={_CJK}) (?=[A-Za-z0-9.\-])", "", text)
    return re.sub(rf"(?<=[A-Za-z0-9.:\-)]) (?={_CJK})", "", text)


def label(s, x, y, w, h, body, size=24, color=WHITE, bold=False, align="center", anchor="middle"):
    return sh.textbox(s, t, x, y, w, h, tight(body), size=size, color=color, bold=bold, align=align, anchor=anchor)


def _text(sp, body, size, bold):
    sh._write(sp.text_frame, t, tight(body), size, WHITE, bold, "center", "middle")
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = sh.U(10)
    tf.margin_top = tf.margin_bottom = sh.U(6)


def plain(s, x, y, w, h, body="", size=24, bold=True, sw=1.75, dash=None, radius=0.06):
    sp = sh.rect(s, t, x, y, w, h, fill=PANEL, stroke=EDGE, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        _text(sp, body, size, bold)
    return sp


def rbox(s, x, y, w, h, role, body="", size=24, bold=True, sw=2.5, dash=None, radius=0.06):
    fill, stroke, pat = ROLES[role]
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    pattern_fill(sp, pat, fill, stroke)
    if body:
        _text(sp, body, size, bold)
    return sp


def num(s, x, y, n, d_=44):
    return sh.badge(s, t, x, y, d_, str(n), color=WHITE, size=26, fill=RGBColor(60, 64, 72))


def score(s, x, y, w, name):
    """A score pill: role colour and pattern, a meter with 3/2/1 filled bars, and the name."""
    role, lvl = LEVEL[name]
    fill, stroke, _ = ROLES[role]
    rbox(s, x, y, w, 56, role, "", radius=0.3)
    for i in range(3):
        h = 16 + 14 * i
        sh.rect(s, t, x + 14 + i * 22, y + 6 + (44 - h), 16, h,
                fill=stroke if i < lvl else OFF, stroke=None)
    label(s, x + 84, y, w - 92, 56, name, size=26, bold=True, align="left")


def arrow(s, x1, y1, x2, y2, width=4, style="solid", head=True, cap=True):
    c = sh.arrow(s, t, x1, y1, x2, y2, color=WHITE, width=width, head=False)
    if style == "dashed":
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    elif style == "dotted":
        c.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
    if not cap:
        ln = c.line._get_or_add_ln()
        for el in ln.findall("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd"):
            ln.remove(el)
    return c


def tag(s, x, y, w, text):
    """A word on a line, on a black patch so the line visibly breaks around it."""
    sh.rect(s, t, x, y - 4, w, 48, fill=RGBColor(0, 0, 0), stroke=None)
    label(s, x, y, w, 40, text, size=24, bold=True)


def title(s, head, sub=None):
    label(s, 43, 10, 1194, 60, head, size=36, bold=True, align="left")
    if sub:
        label(s, 43, 70, 1194, 40, sub, size=24, color=MUTED, align="left")


# ------------------------------------------------------------- 1. the flow
s = d.slide().s
title(s, "Ask before you launch", "Current capacity compared with the amount you request")
xs, W, Y0, H0 = [43, 470, 897], 340, 120, 196
rbox(s, xs[0], Y0, W, H0, "info", "Your request\ntypes × AZs\namount, unit\nmarket", size=24)
plain(s, xs[1] - 30, Y0, W + 60, H0, "Check supportability\nno launch,\nno reservation", size=24, sw=3)
plain(s, xs[2], Y0, W, H0, "Scores\nper combination\n+ aggregate", size=26, sw=3)
for a, b in ((xs[0] + W, xs[1] - 30), (xs[1] + W + 30, xs[2])):
    arrow(s, a + 6, Y0 + H0 / 2, b - 6, Y0 + H0 / 2, width=5)
label(s, 43, 330, 1194, 36, "AWS documentation example: On-Demand, 50 instances", size=24, color=MUTED, align="left")
rows = [("c6g.xlarge", "use1-az1", "High"), ("c7g.xlarge", "use1-az1", "High"), ("m6g.xlarge", "use1-az1", "Medium")]
ry = 376
for i, (typ, az, name) in enumerate(rows):
    y = ry + i * 70
    plain(s, 43, y, 330, 58, typ, size=26, bold=False)
    plain(s, 386, y, 230, 58, az, size=26, bold=False)
    score(s, 640, y, 250, name)
sh.rect(s, t, 43, ry + 3 * 70 + 2, 1150, 3, fill=WHITE)
y = ry + 3 * 70 + 14
plain(s, 43, y, 573, 58, "Aggregate score", size=26, sw=3)
score(s, 640, y, 250, "High")

# ------------------------------------------------------------- 2. conditions
s = d.slide().s
title(s, "Four conditions before you start", "As stated in the AWS documentation")
CW, CH = 590, 208
cards = [
    (1, "Support plan", "AWS Support\nUnified Operations"),
    (2, "Capacity Manager", "enabled in one Region\nper account"),
    (3, "Limits", "100 queries per account per hour\nup to 100 combinations per request"),
    (4, "Results", "no sharing with third parties"),
]
for i, (n, head, body) in enumerate(cards):
    x = 43 + (i % 2) * (CW + 14)
    y = 118 + (i // 2) * (CH + 18)
    rbox(s, x, y, CW, CH, "info", "", radius=0.05)
    num(s, x + 16, y + 16, n)
    label(s, x + 76, y + 12, CW - 96, 52, head, size=30, bold=True, align="left")
    label(s, x + 24, y + 80, CW - 48, 116, body, size=24, bold=False, align="left", anchor="top")

# ------------------------------------------------------------- 3. what a score means
s = d.slide().s
title(s, "Held capacity relative to the request", "Schematic, not to scale")
TX, TW = 330, 700
MX = TX + 200
rows = [("High", 620, "several times the request"), ("Medium", 235, "little to spare"),
        ("Low", 130, "below the request")]
for i, (name, held, note) in enumerate(rows):
    y = 132 + i * 146
    score(s, 43, y + 20, 250, name)
    rbox(s, TX, y + 34, held, 28, LEVEL[name][0], "", sw=2.0, radius=0.0)
    sh.rect(s, t, MX - 2, y + 14, 4, 68, fill=WHITE)
    label(s, TX, y + 88, TW, 40, note, size=24, align="left")
label(s, MX - 100, 100, 200, 36, "request", size=24, bold=True)
label(s, TX + 360, 100, 340, 36, "bar: held capacity", size=24, color=MUTED, align="left")

# ------------------------------------------------------------- 4. pair vs aggregate
s = d.slide().s
title(s, "Low per combination, High in aggregate", "Schematic: the number of combinations is illustrative")
for i, y in enumerate([150, 270, 390]):
    plain(s, 43, y, 300, 70, f"Combination {i + 1}", size=26, bold=False)
    score(s, 362, y + 7, 200, "Low")
    arrow(s, 582, y + 35, 700, 330, width=4)
plain(s, 700, 250, 420, 160, "", sw=3)
label(s, 716, 262, 388, 50, "Aggregate score", size=30, bold=True)
score(s, 810, 332, 200, "High")

# ------------------------------------------------------------- 5. which score to read
s = d.slide().s
title(s, "Which score to read", "By fleet situation")
COLS, BW, IND = [43, 450, 857], 380, 26
HEADS = ["Several types", "One type only", "Capacity error"]
COLS_BOXES = [
    ("Read the aggregate", [("High", "High: proceed"), ("Medium", "Medium or Low:\nadd options or wait")]),
    ("Read each combination", [(None, "Pick the highest-\nscoring combination")]),
    ("Re-check the request", [("High", "High: launch,\nretry the rest"), ("Medium", "Medium or Low:\nuse another High\none, or add types")]),
]
for ci, x in enumerate(COLS):
    plain(s, x, 118, BW, 60, "", sw=3)
    num(s, x + 10, 126, ci + 1, d_=44)
    label(s, x + 62, 118, BW - 70, 60, HEADS[ci], size=26, bold=True, align="left")
    read_text, outs = COLS_BOXES[ci]
    ry, rh = 196, 72
    rbox(s, x, ry, BW, rh, "info", read_text, size=24)
    arrow(s, x + BW / 2, 180, x + BW / 2, ry - 2, width=4)
    oy, oh, gap = ry + rh + 16, 148, 10
    bottom = oy + (len(outs) - 1) * (oh + gap) + oh / 2
    sh.rect(s, t, x + 8, ry + rh, 4, bottom - (ry + rh) + 2, fill=WHITE)
    for k, (lvl, text) in enumerate(outs):
        yy = oy + k * (oh + gap)
        if lvl:
            rbox(s, x + IND, yy, BW - IND, oh, LEVEL[lvl][0], text, size=24)
        else:
            plain(s, x + IND, yy, BW - IND, oh, text, size=24)
        arrow(s, x + 10, yy + oh / 2, x + IND - 2, yy + oh / 2, width=4)

# ------------------------------------------------------------- 7. connections
s = d.slide().s
title(s, "How the pieces connect", "Spot in Check supportability is built on SPS")
plain(s, 43, 140, 340, 100, "Check supportability\n(Spot)", size=24, sw=3)
rbox(s, 560, 140, 320, 100, "info", "Spot placement\nscore (SPS)", size=24)
rbox(s, 43, 400, 300, 100, "info", "Tracker\n(Lambda)", size=24)
plain(s, 520, 400, 260, 100, "CloudWatch\nmetrics", size=24, sw=3)
plain(s, 1010, 400, 227, 100, "CloudWatch\ndashboard", size=24, sw=3)
arrow(s, 383, 190, 560, 190, width=4, style="dotted")
arrow(s, 193, 400, 700, 240, width=4)
arrow(s, 343, 450, 520, 450, width=4)
arrow(s, 780, 450, 1010, 450, width=4)
label(s, 383, 146, 177, 36, "built on", size=24, bold=True)
label(s, 470, 300, 120, 36, "calls", size=24, bold=True, align="left")
label(s, 343, 406, 177, 36, "writes", size=24, bold=True)
label(s, 780, 406, 230, 36, "displayed in", size=24, bold=True)

d.save(OUT)
print("saved", OUT)
