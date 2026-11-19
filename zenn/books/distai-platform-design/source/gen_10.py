"""Figure for 10-development-process.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "10-development-process.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ----------------------------------------------------------------------------- 10-roles
s = d.slide().s
title(s, t, "Issue to ready: roles hand off, no session plays two parts")
steps = [
    ("Issue", GREY, EDGE, WHITE),
    ("Orchestrator", LINK_DK, LINK, LINK_HI),
    ("Implementer +\nTest author", GRN_DK, GRN, GRN_HI),
    ("draft PR", GREY, EDGE, WHITE),
    ("Reviewer", YEL_DK, YEL, YEL),
    ("Maintainer\nstatus: verifying", RED_DK, RED, RED),
    ("Verifier", LINK_DK, LINK, LINK_HI),
    ("Test Results\nready", GRN_DK, GRN, GRN_HI),
]
x = 43
w = 134
gap = 10
for i, (txt, fill, stroke, col) in enumerate(steps):
    box(s, t, x, 220, w, 110, fill, stroke=stroke, body=txt, size=12, color=col)
    if i < len(steps) - 1:
        arrow(s, t, x + w, 275, x + w + gap, 275, color=WHITE)
    x += w + gap
box(s, t, 43, 380, 1156, 60, CHIP, stroke=EDGE,
    body="separate branches per role; the orchestrator merges the test branch into the implementation branch before the PR",
    size=14, color=MUTED, pattern=False)
NAMES.append("10-roles")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
