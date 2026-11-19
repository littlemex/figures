"""Figures for 00-introduction.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, YEL, YEL_DK, GREY, CHIP,
                     EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "00-introduction.pptx")
d = new_deck()
NAMES = []

# ---------------------------------------------------------------- 00-repo-relation
s = d.slide().s
t = d.theme
title(s, t, "Three repositories and what moves between them")
legend(s, t, 43, 100, [(GREY, EDGE, "kept as-is"), (GRN_DK, GRN, "this book's subject"),
                       (LINK_DK, LINK, "upstream")])
y0 = 160
box2(s, t, 43, y0, 300, 140, GREY, EDGE, "distributed-ai",
     "infra/  (superseded)\ninvestigations/  (kept)", color=WHITE)
box2(s, t, 494, y0, 300, 140, GRN_DK, GRN, "distai-platform",
     "new long-lived baseline\n(this book's subject)", color=GRN_HI)
box2(s, t, 945, y0, 300, 140, LINK_DK, LINK, "awsome-distributed-ai",
     "AWS reference repo\n(upstream)", color=LINK)
arrow(s, t, 353, y0 + 55, 484, y0 + 55, color=MUTED, dashed=True)
label(s, t, 343, y0 + 64, 151, 24, "reference", size=12, color=MUTED, align="center")
arrow(s, t, 935, y0 + 40, 804, y0 + 40, color=LINK)
label(s, t, 794, y0 + 12, 151, 24, "reference", size=12, color=LINK, align="center")
arrow(s, t, 804, y0 + 100, 935, y0 + 100, color=GRN_HI)
label(s, t, 794, y0 + 108, 151, 24, "contribute", size=12, color=GRN_HI, align="center")
box(s, t, 43, y0 + 190, 1156, 90, CHIP, stroke=EDGE,
    body="distai-platform treats distributed-ai@e092c3f as reference material;\nit both follows and contributes back to awsome-distributed-ai's conventions",
    size=14, color=MUTED, pattern=False)
NAMES.append("00-repo-relation")

# ---------------------------------------------------------- 00-import-then-redesign
s = d.slide().s
title(s, t, "Import, verify, then redesign from scratch")
y0 = 170
steps = [
    ("PR #14", "draft", GREY, EDGE, WHITE),
    ("diff -r", "IDENTICAL", GRN_DK, GRN, GRN_HI),
    ("git ls-files -s", "SAME-MODES", GRN_DK, GRN, GRN_HI),
    ("Issue #2 + PR #14", "closed, not merged", YEL_DK, YEL, YEL),
    ("Issue #17", "redesign", LINK_DK, LINK, LINK),
]
x = 43
w = 210
gap = 36
for i, (head, sub, fill, stroke, col) in enumerate(steps):
    box2(s, t, x, y0, w, 110, fill, stroke, head, sub, size=16, sub_size=13, color=col,
         align="center")
    if i < len(steps) - 1:
        arrow(s, t, x + w, y0 + 55, x + w + gap, y0 + 55, color=WHITE)
    x += w + gap
box(s, t, 43, y0 + 170, 1156, 70, CHIP, stroke=EDGE,
    body="e092c3f54e2ebcee665389cbdfc17348f612c2d3 stays the reference commit for the redesign",
    size=14, color=MUTED, pattern=False)
last_cx = 43 + 4 * (w + gap) + w // 2
arrow(s, t, last_cx, y0 + 170, last_cx, y0 + 110, color=LINK, dashed=True)
NAMES.append("00-import-then-redesign")

# ------------------------------------------------------------------- 00-reading-map
s = d.slide().s
title(s, t, "Chapter dependency map")
legend(s, t, 43, 100, [(GRN_DK, GRN, "grounds every chapter"),
                       (LINK_DK, LINK, "design chapters"),
                       (YEL_DK, YEL, "tested by experiments"),
                       (GREY, EDGE, "process / upstream")])
y_found = 560
box(s, t, 43, y_found, 1156, 60, GRN_DK, stroke=GRN, body="01  Principles", size=17,
    color=GRN_HI)
mid = [("02  Four\ndecisions", 43), ("03  Capacity\npools", 207),
       ("3b  Multi-\ntenancy", 371), ("04  Capacity\nmap", 535)]
y_mid = 420
for txt, x in mid:
    box(s, t, x, y_mid, 150, 100, LINK_DK, stroke=LINK, body=txt, size=13, color=LINK)
    arrow(s, t, x + 75, y_mid + 100, x + 75, y_found, color=GRN_HI)
box(s, t, 859, y_mid, 340, 100, YEL_DK, stroke=YEL, body="08  Foundation", size=15,
    color=YEL)
arrow(s, t, 859 + 170, y_mid + 100, 859 + 170, y_found, color=GRN_HI)
box(s, t, 43, 280, 420, 100, LINK_DK, stroke=LINK,
    body="05  Device plugin / DRA design", size=14, color=LINK)
arrow(s, t, 207 + 75, y_mid, 207 + 75, 380, color=WHITE)
box(s, t, 523, 280, 300, 100, YEL_DK, stroke=YEL, body="06-07  Experiments\n(GPU, Trainium)",
    size=14, color=YEL)
arrow(s, t, 463, 325, 523, 325, color=WHITE)
arrow(s, t, 523, 355, 463, 355, color=YEL, dashed=True)
label(s, t, 388, 357, 135, 20, "feed back", size=11, color=YEL, align="center")
box(s, t, 43, 140, 1156, 100, GREY, stroke=EDGE,
    body="09 Verification        10 Development process        11 Upstream        12 Summary",
    size=15, color=WHITE)
arrow(s, t, 621, 280, 621, 240, color=WHITE)
arrow(s, t, 1029, 380, 1029, 240, color=WHITE)
NAMES.append("00-reading-map")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
