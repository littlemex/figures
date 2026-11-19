"""Figure for 04-capacity-map.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.enum.shapes import MSO_SHAPE
from pptxkit import shapes as sh
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE, pattern_fill,
                     ROLE_PATTERN)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04-capacity-map.pptx")
d = new_deck()
NAMES = []
t = d.theme


def dot(s, x, y, d_, fill, stroke):
    sp = sh.rect(s, t, x - d_ / 2, y - d_ / 2, d_, d_, fill=fill, stroke=stroke, sw=2,
                 shape=MSO_SHAPE.OVAL)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    return sp


# -------------------------------------------------------------------- 04-score-vs-offering
s = d.slide().s
title(s, t, "Offer count and spot placement score are two different axes")
ox, oy, ow, oh = 160, 520, 980, 320  # plot origin (bottom-left) and size
arrow(s, t, ox, oy, ox + ow, oy, color=MUTED)
label(s, t, ox, oy + 10, ow, 22, "offer count  (regions x AZs)  -->", size=13,
      color=MUTED, align="left")
arrow(s, t, ox, oy, ox, oy - oh, color=MUTED)
label(s, t, 10, oy - oh - 6, 140, 50, "spot placement\nscore (1-10)", size=13,
      color=MUTED, align="left")

points = [
    (0.12, 0.90, "trn2.3xlarge", "3 regions only,\nbut score 9 in ap-southeast-4",
     GRN_DK, GRN, GRN_HI, "right"),
    (0.88, 0.22, "g6e.xlarge", "offered almost everywhere,\nbut score 1 everywhere",
     RED_DK, RED, RED, "left"),
    (0.80, 0.82, "g7.2xlarge", "offered widely AND\nscores 8-9 almost everywhere",
     LINK_DK, LINK, LINK_HI, "left"),
]
for fx, fy, name, note, fill, stroke, col, side in points:
    px = ox + fx * ow
    py = oy - fy * oh
    dot(s, px, py, 26, fill, stroke)
    if side == "left":
        lx, align = px - 260, "right"
    else:
        lx, align = px + 30, "left"
    label(s, t, lx, py - 30, 230, 22, name, size=15, bold=True, color=col, align=align)
    label(s, t, lx, py - 6, 230, 44, note, size=11, color=MUTED, align=align)

box(s, t, 43, 568, 1156, 60, CHIP, stroke=EDGE,
    body="a type can be offered everywhere and still be hard to get on spot, or offered almost nowhere and still be easy where it is offered",
    size=14, color=MUTED, pattern=False)
NAMES.append("04-score-vs-offering")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
