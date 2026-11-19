"""Figures for 05-device-plugin-and-dra.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "05-device-plugin-and-dra.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ----------------------------------------------------------------------- 05-opt-in-labels
s = d.slide().s
title(s, t, "DaemonSet opt-out today vs. a method label opt-in")
label(s, t, 43, 100, 560, 24, "As-is: opt-out, every node pool", size=15, color=RED,
      bold=True)
box(s, t, 43, 134, 560, 60, RED_DK, stroke=RED, body="DaemonSet  (no selector)",
    size=15, color=RED)
pools1 = ["node pool 1", "node pool 2", "node pool 3"]
for i, p in enumerate(pools1):
    x = 43 + i * 190
    box(s, t, x, 260, 170, 56, GREY, stroke=EDGE, body=p, size=13, color=WHITE)
    arrow(s, t, 323, 194, x + 85, 260, color=RED, dashed=True)
label(s, t, 43, 326, 560, 22, "spreads to all node pools regardless of fit", size=12,
      color=RED, align="left")

label(s, t, 659, 100, 540, 24, "To-be: opt-in, one label key per device class",
      size=15, color=GRN_HI, bold=True)
box(s, t, 659, 134, 260, 56, GRN_DK, stroke=GRN, body="DaemonSet\nmethod=device-plugin",
    size=13, color=GRN_HI)
box(s, t, 939, 134, 260, 56, LINK_DK, stroke=LINK, body="DaemonSet\nmethod=dra",
    size=13, color=LINK_HI)
pools2 = [("node pool 1", "method=\ndevice-plugin", GRN_DK, GRN, GRN_HI),
          ("node pool 2", "method=\ndevice-plugin", GRN_DK, GRN, GRN_HI),
          ("node pool 3", "method=\ndra", LINK_DK, LINK, LINK_HI)]
for i, (name, lbl, fill, stroke, col) in enumerate(pools2):
    x = 659 + i * 190
    box2(s, t, x, 260, 170, 88, fill, stroke, name, lbl, size=13, sub_size=11, color=col,
         align="center", pad=8)
arrow(s, t, 789, 190, 744, 260, color=GRN_HI)
arrow(s, t, 789, 190, 934, 260, color=GRN_HI)
arrow(s, t, 1069, 190, 1114, 260, color=LINK_HI)
label(s, t, 659, 374, 540, 22, "each advertiser selects its own node pools", size=12,
      color=GRN_HI, align="left")
NAMES.append("05-opt-in-labels")

# ------------------------------------------------------------------- 05-pod-request-layers
s = d.slide().s
title(s, t, "Layer 1 reaches both node kinds; Layer 2 reaches DRA only")
box2(s, t, 43, 170, 500, 90, GRN_DK, GRN, "Layer 1  (default)", "resources.limits",
     size=17, sub_size=14, color=GRN_HI, align="center")
box2(s, t, 43, 320, 500, 90, YEL_DK, YEL, "Layer 2  (opt-in)", "ResourceClaimTemplate",
     size=17, sub_size=14, color=YEL, align="center")
box2(s, t, 723, 170, 476, 90, CHIP, EDGE, "device plugin node", None, size=16,
     color=WHITE, align="center")
box2(s, t, 723, 320, 476, 90, LINK_DK, LINK, "DRA node",
     "needs a DeviceClass with extendedResourceName", size=16, sub_size=12,
     color=LINK_HI, align="center")
arrow(s, t, 543, 215, 723, 215, color=GRN_HI)
arrow(s, t, 543, 232, 723, 365, color=GRN_HI)
arrow(s, t, 543, 365, 723, 365, color=YEL)
box(s, t, 43, 420, 680, 40, None, stroke=None, pattern=False,
    body="reaches a DRA node only via KEP-5004 (DeviceClass.extendedResourceName)",
    size=13, color=GRN_HI, align="left")
box(s, t, 43, 470, 1156, 60, CHIP, stroke=EDGE,
    body="Layer 1 is the seam: the same Pod spec works whether a node pool advertises via device plugin or via DRA",
    size=14, color=MUTED, pattern=False)
NAMES.append("05-pod-request-layers")

# ---------------------------------------------------------------------- 05-migration-steps
s = d.slide().s
title(s, t, "Blue/green migration, device plugin pool to DRA pool")
steps = [
    ("1", "narrow", "device plugin opt-in\nexcludes method=dra"),
    ("2", "install DRA driver", "0 nodes yet"),
    ("3", "new node pool", "method=dra, low weight"),
    ("4", "canary", "one Layer 2 pod"),
    ("5", "swap weights", "old pool limit -> 0"),
    ("6", "clean up", "once old pool is empty"),
]
x = 43
w = 180
gap = 16
y0 = 190
for n, head, sub in steps:
    box2(s, t, x, y0, w, 130, GRN_DK, GRN, f"{n}. {head}", sub, size=14, sub_size=11,
         color=GRN_HI, align="center", pad=10)
    if n != "6":
        arrow(s, t, x + w, y0 + 65, x + w + gap, y0 + 65, color=WHITE)
    x += w + gap
box2(s, t, 43, 360, 1156, 70, RED_DK, RED, "rollback",
     "restore weights and limits only -- nodes themselves are untouched", size=15,
     sub_size=13, color=RED, align="left")
arrow(s, t, 403, 360, 403, 320, color=RED, dashed=True)
label(s, t, 423, 332, 200, 20, "if the canary fails", size=11, color=RED, align="left")
NAMES.append("05-migration-steps")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
