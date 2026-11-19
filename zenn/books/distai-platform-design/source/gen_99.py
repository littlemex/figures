"""Figures for 99-summary.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99-summary.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ------------------------------------------------------------------------- 99-timeline
s = d.slide().s
title(s, t, "From a stopped import to three open decision threads")
chain = [
    ("Issue #2", "PR #14"), ("Issue #17", None), ("Issue #19", None),
    ("Issue #20", "PR #21"), ("Issue #16", None), ("Issue #1", "PR #15"),
]
x = 43
w = 180
gap = 18
for head, sub in chain:
    box2(s, t, x, 180, w, 110, LINK_DK, LINK, head, sub, size=15, sub_size=13,
         color=LINK_HI, align="center")
    arrow(s, t, x - gap, 235, x, 235, color=WHITE) if x > 43 else None
    x += w + gap
box(s, t, 43, 330, 1156, 60, RED_DK, stroke=RED,
    body="Issue #2 / PR #14: import attempt -- closed without merging, kept only as a reference commit",
    size=14, color=RED)
box(s, t, 43, 410, 1156, 60, CHIP, stroke=EDGE,
    body="#17 (capacity), #19 (device plugin/DRA) and #16 (verification) are the three open design threads this book follows",
    size=14, color=MUTED, pattern=False)
NAMES.append("99-timeline")

# ----------------------------------------------------------------------------- 99-open
s = d.slide().s
title(s, t, "What still waits on a decision")
box2(s, t, 43, 150, 350, 170, YEL_DK, YEL, "Issue #17  (capacity)",
     "E1 risky-assumption experiments\n(not yet run)", size=16, sub_size=13, color=YEL,
     align="left", pad=16)
box2(s, t, 423, 150, 350, 170, YEL_DK, YEL, "Issue #19  (device plugin / DRA)",
     "E5 migration\nE6 trn2.48xlarge\nE7 p5 / p5en re-run", size=16, sub_size=13,
     color=YEL, align="left", pad=16)
box2(s, t, 803, 150, 396, 170, LINK_DK, LINK, "Issue #18  (sharedfs)",
     "FilesystemShare\nwaits on #17's GitOps path\nand Kueue config", size=16,
     sub_size=13, color=LINK_HI, align="left", pad=16)
arrow(s, t, 598, 320, 598, 370, color=YEL, both=True)
box(s, t, 43, 370, 1156, 70, CHIP, stroke=EDGE,
    body="the riskiest assumption (Kueue admit = capacity exists) is the one experiment set every other open thread waits behind",
    size=14, color=MUTED, pattern=False)
NAMES.append("99-open")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
