"""Figures for 01-principles.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, diamond, label, arrow, legend,
                     save_and_strip, render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI,
                     YEL, YEL_DK, RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-principles.pptx")
d = new_deck()
NAMES = []
t = d.theme


def chip_row(s, items, x, y, w, h, fill, stroke, cols, size=14):
    gap = 12
    cw = (w - gap * (cols - 1)) // cols
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        box(s, t, x + c * (cw + gap), y + r * (h + gap), cw, h, fill, stroke=stroke,
            body=it, size=size, color=WHITE)


# -------------------------------------------------------------------- 01-tenancy-roles
s = d.slide().s
title(s, t, "Admin owns cluster-scoped objects; teams self-serve inside a namespace")
y0 = 150
box(s, t, 43, y0, 1156, 36, None, stroke=None, body="Admin  (cluster-scoped)", size=17,
    color=GRN_HI, align="left", pattern=False)
chip_row(s, ["Terraform shell", "NodePool", "EC2NodeClass", "Device advertiser",
             "Shared storage", "Capacity Block cohort"], 43, y0 + 44, 1156, 70,
         GRN_DK, GRN, 3, size=15)
y1 = y0 + 44 + 2 * 70 + 12 + 50
box(s, t, 43, y1, 1156, 36, None, stroke=None, body="Team namespace  (self-service)",
    size=17, color=LINK, align="left", pattern=False)
chip_row(s, ["AcceleratorPool", "PersistentVolumeClaim"], 43, y1 + 44, 1156, 60,
         LINK_DK, LINK, 2, size=15)
arrow(s, t, 621, y1 + 44, 621, y0 + 44 + 2 * 70 + 12, color=RED, width=2.25, dashed=True)
label(s, t, 300, y1 - 2, 650, 24,
      "no cluster-scoped write to karpenter.sh / kueue objects", size=13, color=RED,
      align="center")
NAMES.append("01-tenancy-roles")

# --------------------------------------------------------------- 01-shared-vs-separate
s = d.slide().s
title(s, t, "One mechanism, parameterised by accelerator type vs. separate implementations")
y0 = 150
box2(s, t, 43, y0, 560, 36, None, None, "One mechanism (accelerator type is a value)",
     size=16, color=GRN_HI, pad=0)
chip_row(s, ["NodePool", "Capacity Block", "Kueue", "Storage", "Identity", "Provenance",
             "Probe framework"], 43, y0 + 46, 560, 54, GRN_DK, GRN, 2, size=14)
box2(s, t, 659, y0, 540, 36, None, None,
     "Separate implementations, aligned entry point", size=16, color=LINK, pad=0)
pairs = [("Device plugin", "GPU / Neuron"), ("Driver / runtime", "GPU / Neuron"),
         ("Metrics", "DCGM / neuron-monitor"), ("Collective comm", "NCCL / Neuron"),
         ("Profiler", "Nsight / Neuron Profiler")]
yy = y0 + 46
for head, sub in pairs:
    box2(s, t, 659, yy, 540, 72, LINK_DK, LINK, head, sub, size=14, sub_size=12,
         color=LINK_HI, sub_color=MUTED, align="left", pad=10)
    yy += 80
NAMES.append("01-shared-vs-separate")

# ----------------------------------------------------------------- 01-abstraction-test
s = d.slide().s
title(s, t, "The test for a new general mechanism")
y0 = 220
box(s, t, 43, y0, 260, 90, GREY, stroke=EDGE, body="New mechanism\nneeded", size=15,
    color=WHITE)
arrow(s, t, 303, y0 + 45, 383, y0 + 45, color=WHITE)
diamond(s, t, 383, y0 - 35, 260, 160, YEL_DK, YEL, "Portable\nstandalone?", size=15,
        color=YEL)
arrow(s, t, 643, y0 - 15, 723, y0 - 15, color=GRN_HI)
label(s, t, 650, y0 - 42, 90, 22, "yes", size=12, color=GRN_HI, align="center")
box(s, t, 723, y0 - 60, 300, 90, GRN_DK, stroke=GRN,
    body="Extract as\nindependent OSS", size=15, color=GRN_HI)
arrow(s, t, 873, y0 + 30, 873, y0 + 140, color=GRN_HI)
box(s, t, 723, y0 + 140, 300, 90, GRN_DK, stroke=GRN,
    body="Consume as\ndependency", size=15, color=GRN_HI)
arrow(s, t, 513, y0 + 125, 513, y0 + 220, color=RED, dashed=False)
label(s, t, 513, y0 + 128, 90, 22, "no", size=12, color=RED, align="center")
box(s, t, 383, y0 + 220, 260, 90, LINK_DK, stroke=LINK,
    body="Keep in this\nrepository", size=15, color=LINK)
NAMES.append("01-abstraction-test")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
