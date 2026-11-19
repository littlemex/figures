"""Figures for 11-upstream.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "11-upstream.pptx")
d = new_deck()
NAMES = []
t = d.theme

# -------------------------------------------------------------------- 11-plugin-detect
s = d.slide().s
title(s, t, "Detect by release name vs. detect by what a device plugin always does")
label(s, t, 43, 140, 540, 24, "today: helm list for 2 fixed release names", size=15,
      color=RED, bold=True)
box2(s, t, 43, 174, 540, 96, RED_DK, RED, "helm list", "nvdp/nvidia-device-plugin\naws-efa-k8s-device-plugin",
     size=14, sub_size=12, color=RED, align="center")
box2(s, t, 43, 300, 540, 70, CHIP, EDGE, "GPU Operator", "installed another way: invisible",
     size=14, sub_size=12, color=MUTED, align="center")
box2(s, t, 43, 400, 540, 70, CHIP, EDGE, "eksctl", "installed another way: invisible",
     size=14, sub_size=12, color=MUTED, align="center")

label(s, t, 659, 140, 540, 24, "proposed: look for the kubelet mount", size=15,
      color=GRN_HI, bold=True)
box2(s, t, 659, 174, 540, 96, GRN_DK, GRN, "/var/lib/kubelet/device-plugins",
     "any DaemonSet that mounts this path", size=14, sub_size=12, color=GRN_HI,
     align="center")
box2(s, t, 659, 300, 540, 70, GRN_DK, GRN, "found regardless of installer", "Helm, GPU Operator, eksctl",
     size=14, sub_size=12, color=GRN_HI, align="center")
box(s, t, 43, 500, 1156, 60, CHIP, stroke=EDGE,
    body="stops and reports instead of silently installing a second one beside the first",
    size=14, color=MUTED, pattern=False)
NAMES.append("11-plugin-detect")

# -------------------------------------------------------------- 11-capacity-block-flow
s = d.slide().s
title(s, t, "Upstream has only the last of four steps")
steps = [
    ("1. search", "describe-capacity-block-offerings", RED_DK, RED, RED),
    ("2. view offering", "start, AZ, prepay amount", RED_DK, RED, RED),
    ("3. purchase", "purchase-capacity-block", RED_DK, RED, RED),
    ("4. CapacityReservationId", "the only param upstream has", GRN_DK, GRN, GRN_HI),
]
x = 43
w = 265
gap = 24
for i, (head, sub, fill, stroke, col) in enumerate(steps):
    box2(s, t, x, 200, w, 120, fill, stroke, head, sub, size=15, sub_size=12, color=col,
         align="center", pad=14)
    if i < len(steps) - 1:
        arrow(s, t, x + w, 260, x + w + gap, 260, color=WHITE)
    x += w + gap
box(s, t, 43, 360, 1156, 60, CHIP, stroke=EDGE,
    body="no tooling exists upstream for steps 1-3 -- users must learn the AWS CLI calls themselves",
    size=14, color=MUTED, pattern=False)
NAMES.append("11-capacity-block-flow")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
