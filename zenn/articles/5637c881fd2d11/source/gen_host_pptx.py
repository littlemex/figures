"""gen_host_pptx.py: the structure figure of the Engram host-table article, as native pptx shapes.

    /usr/bin/python3 gen_host_pptx.py <out.pptx>

Slides: two-ways (the two ways to read rows of a table kept in host memory).
Roles (ZN-25, ZN-29), each with a colour and a faint pattern so that it reads without colour:
  green + "/"       way A: the GPU reads each row from host memory itself (zero-copy)
  blue + "x" grid   way B: the CPU gathers the rows, then one copy to the GPU (dashed arrows)
  yellow + dotted   the row ids
  grey, no pattern  memory and hardware
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
ROLE = {"b": (BLU_DK, BLU, "cross"), "a": (GRN_DK, GRN, "diagonal"),
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


def title(s, head, roles, override=None):
    label(s, 43, 22, 1190, 46, head, size=30, bold=True, align="left")
    names = {"b": "way B", "a": "way A", "ids": "row ids", "data": "memory, hardware"}
    names = {**names, **(override or {})}
    x = 43
    for r in roles:
        box(s, x, 76, 34, 22, r)
        label(s, x + 42, 74, 220, 26, names[r], size=15, color=MUTED, align="left")
        x += 74 + 10 * len(names[r])


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2, dashed=False):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


def seg(s, pts, color=WHITE, width=2, dashed=False):
    """A polyline with one arrowhead, at the last point."""
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.util import Pt
    for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
        c.line.color.rgb = color
        c.line.width = Pt(width)
        if dashed:
            c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    arrow(s, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


def num(s, x, y, n):
    c = sh.rect(s, t, x, y, 30, 30, fill=WHITE, stroke=WHITE, sw=1, shape=MSO_SHAPE.OVAL)
    sh._write(c.text_frame, t, str(n), 15, RGBColor(10, 10, 12), True, "center", "middle")
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0



# ---------------------------------------------------------------- two ways to read rows from host memory
s = d.slide().s
title(s, "Two ways to read Engram rows kept in host memory", ["a", "b", "ids", "data"])
label(s, 43, 112, 560, 30, "Host (CPU side)", size=19, bold=True)
label(s, 713, 112, 524, 30, "GPU", size=19, bold=True)
frame(s, 43, 148, 560, 520)
frame(s, 713, 148, 524, 520)
sh.rect(s, t, 618, 148, 80, 520, fill=CHIP, stroke=EDGE, sw=1, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
label(s, 618, 152, 80, 30, "PCIe", size=16, bold=True)
box(s, 83, 190, 240, 440, "data", body="host memory\n\nEngram table\n\n256 B per row", size=16)
# way A
box(s, 753, 220, 240, 60, "a", body="gather kernel (on SMs)", size=15)
box(s, 1023, 220, 184, 60, "data", body="rows on GPU", size=15)
arrow(s, 323, 250, 753, 250, color=GRN, width=4)
label(s, 335, 206, 270, 28, "A: each row read over PCIe", size=14, color=GRN, align="left")
arrow(s, 993, 250, 1023, 250, color=GRN, width=3)
# row ids
box(s, 753, 360, 240, 50, "ids", body="row ids", size=15)
arrow(s, 873, 360, 873, 280, color=YEL, width=2)
seg(s, [(753, 385), (473, 385), (473, 460)], color=YEL, width=2)
label(s, 343, 340, 260, 28, "B: ids back to the CPU", size=14, color=YEL, align="left")
# way B
box(s, 383, 460, 180, 60, "b", body="CPU cores gather", size=15)
box(s, 383, 570, 180, 60, "b", body="staging buffer", size=15)
arrow(s, 323, 490, 383, 490, color=BLU, width=3, dashed=True)
arrow(s, 473, 520, 473, 570, color=BLU, width=3, dashed=True)
box(s, 1023, 570, 184, 60, "data", body="rows on GPU", size=15)
arrow(s, 563, 600, 1023, 600, color=BLU, width=4, dashed=True)
label(s, 700, 562, 320, 28, "B: one copy over PCIe", size=14, color=BLU, align="left")

# ---------------------------------------------------------------- how DeepEP reads Engram rows (GIN get)
s = d.slide().s
title(s, "How DeepEP's Engram reads rows: one GIN get per row", ["a", "b", "ids", "data"],
      {"a": "DeepEP kernel", "b": "GIN backend"})
label(s, 43, 112, 520, 30, "Reader GPU", size=19, bold=True)
label(s, 717, 112, 520, 30, "Owner (any rank, the reader too)", size=19, bold=True)
frame(s, 43, 148, 520, 492)
frame(s, 717, 148, 520, 492)
box(s, 73, 175, 220, 52, "ids", body="row ids", size=15)
box(s, 73, 270, 460, 60, "a", body="engram_fetch kernel: one get per row", size=15)
arrow(s, 183, 227, 183, 270, color=YEL, width=2)
box(s, 73, 380, 220, 64, "b", body="GDAKI: GPU rings the NIC", size=14)
box(s, 313, 380, 220, 64, "b", body="Proxy: a CPU thread posts it", size=14, dash=MSO_LINE_DASH_STYLE.DASH)
arrow(s, 183, 330, 183, 380, color=GRN, width=3)
arrow(s, 423, 330, 423, 380, color=GRN, width=3)
seg(s, [(183, 444), (183, 470), (640, 470)], color=BLU, width=2)
seg(s, [(423, 444), (423, 470)], color=BLU, width=2)
seg(s, [(640, 470), (640, 330), (757, 330)], color=BLU, width=2)
box(s, 757, 280, 440, 100, "data", body="host memory window\n(the owner's part of the table)", size=16)
box(s, 757, 430, 440, 64, "data", body="NIC reads it (RDMA) or a CPU sends it (TCP)", size=14)
arrow(s, 977, 380, 977, 430, color=BLU, width=2)
box(s, 73, 540, 460, 64, "data", body="rows land in the reader's GPU memory", size=15)
seg(s, [(757, 462), (680, 462), (680, 572), (533, 572)], color=BLU, width=4, dashed=True)
label(s, 757, 190, 440, 50, "the owner's GPU does no work", size=15, color=MUTED)
label(s, 43, 650, 1194, 30, "completion: flush_async per peer, then a wait kernel", size=14, color=MUTED)

# ---------------------------------------------------------------- where the table lives and the slack a lookup must fit in
s = d.slide().s
title(s, "Rows must arrive within the slack before each Engram layer", ["a", "b", "ids", "data"],
      {"a": "Engram layer", "b": "model blocks", "ids": "row ids", "data": "memory"})
box(s, 43, 120, 330, 110, "data", body="host memory\nEngram tables\n(V4.1-Flash: about 196 GB)", size=15)
box(s, 43, 260, 330, 70, "data", body="GPU memory: 32 GiB here\n(the other weights)", size=15)
label(s, 390, 132, 140, 30, "PCIe", size=16, bold=True)
box(s, 600, 120, 230, 50, "ids", body="token ids -> row ids", size=14)
label(s, 845, 122, 400, 46, "known before the blocks run", size=14, color=MUTED, align="left")
xs = [(600, "embed", "b"), (700, "block 0", "b"), (820, "Engram 1", "a"), (950, "blocks 1-13", "b"), (1110, "Engram 14", "a")]
ws = {"embed": 90, "block 0": 110, "Engram 1": 120, "blocks 1-13": 150, "Engram 14": 125}
for x, name, role in xs:
    box(s, x, 260, ws[name], 70, role, body=name, size=14)
for a_, b_ in ((690, 700), (810, 820), (940, 950), (1100, 1110)):
    arrow(s, a_, 295, b_, 295, color=WHITE, width=2)
seg(s, [(600, 145), (480, 145), (480, 120), (373, 120)], color=YEL, width=2)
label(s, 600, 172, 300, 28, "pick the rows", size=13, color=YEL, align="left")
seg(s, [(373, 175), (540, 175), (540, 400), (880, 400), (880, 330)], color=GRN, width=4)
seg(s, [(540, 400), (1172, 400), (1172, 330)], color=GRN, width=4, dashed=True)
box(s, 600, 450, 210, 56, "b", body="slack for Engram 1", size=14, dash=MSO_LINE_DASH_STYLE.DASH)
box(s, 600, 530, 500, 56, "b", body="slack for Engram 14", size=14, dash=MSO_LINE_DASH_STYLE.DASH)
label(s, 43, 380, 480, 40, "rows for one step travel over PCIe", size=15, color=GRN, align="left")
label(s, 43, 620, 1194, 30, "the read hides only if it fits in the slack without taking the SMs the blocks need", size=15, color=MUTED)

d.save(OUT)
import strip_branding  # noqa: E402

strip_branding.main(OUT, OUT)
print(OUT)
