"""Figures for 02-four-decisions.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02-four-decisions.pptx")
d = new_deck()
NAMES = []
t = d.theme

# -------------------------------------------------------------------- 02-four-decisions
s = d.slide().s
title(s, t, "Four decisions, four different timescales")
y0 = 210
steps = [
    ("D1  Buy", "days", "human + script", GREY, EDGE, WHITE),
    ("D2  Choose a cell", "at submission", "SkyPilot", LINK_DK, LINK, LINK_HI),
    ("D3  Admit", "at submission", "Kueue", LINK_DK, LINK, LINK_HI),
    ("D4  Launch", "seconds to minutes", "Karpenter", GRN_DK, GRN, GRN_HI),
]
x = 43
w = 270
gap = 26
for i, (head, when, who, fill, stroke, col) in enumerate(steps):
    box2(s, t, x, y0, w, 150, fill, stroke, head, f"{when}\nowner: {who}", size=17,
         sub_size=14, color=col, align="center", pad=16)
    if i < len(steps) - 1:
        arrow(s, t, x + w, y0 + 75, x + w + gap, y0 + 75, color=WHITE)
    x += w + gap
box(s, t, 43, y0 + 190, 1156, 64, CHIP, stroke=EDGE,
    body="putting all four into one Terraform variable mixed ~380 lines and 19 validations into a single knob",
    size=14, color=MUTED, pattern=False)
NAMES.append("02-four-decisions")

# ----------------------------------------------------------------------- 02-options-axes
s = d.slide().s
title(s, t, "Six options on two axes: deciding layer vs. how it's wrapped")
cols = ["Karpenter", "Kueue", "SkyPilot"]
rows = ["(a)/(e)/(f) wrap:\nTF variable", "plain manifest", "kro", "custom CRD"]
x0, y0 = 260, 170
cw, rh = 300, 80
label(s, t, x0, y0 - 40, cw * 3, 24, "deciding layer  -->", size=13, color=MUTED,
      align="center")
for j, c in enumerate(cols):
    label(s, t, x0 + j * cw, y0 - 14, cw, 24, c, size=15, color=WHITE, bold=True)
for i, r in enumerate(rows):
    label(s, t, 43, y0 + i * rh + 10, 200, rh - 10, r, size=13, color=MUTED, align="left")
for j in range(3):
    for i in range(4):
        box(s, t, x0 + j * cw + 8, y0 + i * rh + 8, cw - 16, rh - 16, None, stroke=EDGE,
            pattern=False)
cells = {
    (0, 0): ("(a)\nextend TF var", GREY, EDGE, WHITE),
    (1, 0): ("(b)\nKarpenter + ArgoCD", GRN_DK, GRN, GRN_HI),
    (1, 1): ("(c)\nKueue-centric", GRN_DK, GRN, GRN_HI),
    (1, 2): ("(d)\nSkyPilot outside", GRN_DK, GRN, GRN_HI),
    (2, 0): ("(e)\nkro", YEL_DK, YEL, YEL),
    (3, 0): ("(f)\ncustom CRD", RED_DK, RED, RED),
}
for (row, col), (txt, fill, stroke, color) in cells.items():
    box(s, t, x0 + col * cw + 18, y0 + row * rh + 12, cw - 36, rh - 24, fill,
        stroke=stroke, body=txt, size=13, color=color)
label(s, t, 43, y0 + 4 * rh + 20, 1150, 26,
      "(a) (e) (f) differ in wrapping only -- (b) (c) (d) differ in deciding layer only",
      size=13, color=MUTED, align="left")
NAMES.append("02-options-axes")

# ------------------------------------------------------------------ 02-recommended-layers
s = d.slide().s
title(s, t, "Recommended layering, entry to Terraform shell")
rows2 = [
    ("Entry", "SkyPilot hub / direct", LINK_DK, LINK),
    ("D2  Choose a cell", "SkyPilot", LINK_DK, LINK),
    ("D3  Admit", "Kueue", LINK_DK, LINK),
    ("D4  Launch", "Karpenter", GRN_DK, GRN),
    ("Deliver", "Argo CD", GRN_DK, GRN),
    ("Shell", "Terraform", YEL_DK, YEL),
    ("Buy", "human procedure", GREY, EDGE),
]
y = 118
h = 70
gap = 10
for i, (head, sub, fill, stroke) in enumerate(rows2):
    box2(s, t, 260, y, 680, h, fill, stroke, head, sub, size=14, sub_size=12,
         color=WHITE if fill == GREY else stroke, align="left", pad=10)
    if i < len(rows2) - 1:
        arrow(s, t, 600, y + h, 600, y + h + gap, color=MUTED)
    y += h + gap
NAMES.append("02-recommended-layers")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
