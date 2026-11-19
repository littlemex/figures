"""Figures for 07-dra-experiments-trainium.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "07-dra-experiments-trainium.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ------------------------------------------------------------- 07-e4b-deviceclass-before-after
s = d.slide().s
title(s, t, "E4b: a platform DeviceClass turns Pending into Scheduled in ~3s")
label(s, t, 43, 140, 540, 24, "as-is", size=16, color=RED, bold=True)
box2(s, t, 43, 174, 540, 80, CHIP, EDGE, "chart DeviceClass", "no extendedResourceName",
     size=15, sub_size=13, color=WHITE, align="center")
arrow(s, t, 313, 254, 313, 310, color=RED)
box2(s, t, 43, 310, 540, 100, RED_DK, RED, "Layer 1 pod", "Pending", size=16,
     sub_size=14, color=RED, align="center")

label(s, t, 659, 140, 540, 24, "to-be", size=16, color=GRN_HI, bold=True)
box2(s, t, 659, 174, 540, 80, GRN_DK, GRN, "+ platform DeviceClass",
     "extendedResourceName: aws.amazon.com/neuron", size=15, sub_size=13, color=GRN_HI,
     align="center")
arrow(s, t, 929, 254, 929, 310, color=GRN_HI)
box2(s, t, 659, 310, 540, 100, GRN_DK, GRN, "same Layer 1 pod, unmodified",
     "Scheduled in ~3s", size=16, sub_size=14, color=GRN_HI, align="center")
box(s, t, 43, 450, 1156, 60, CHIP, stroke=EDGE,
    body="the Neuron chart does not ship this DeviceClass itself -- the platform's small catalogue adds it",
    size=14, color=MUTED, pattern=False)
NAMES.append("07-e4b-deviceclass-before-after")

# -------------------------------------------------------------- 07-e4c-dynamic-vs-static
s = d.slide().s
title(s, t, "E4c: a Neuron DRA pool only works once it's static")
label(s, t, 43, 140, 540, 24, "dynamic pool  (StaticCapacity off)", size=15, color=RED,
      bold=True)
box2(s, t, 43, 174, 540, 90, RED_DK, RED, "Layer 1 pod", "node launches, Initialized=Unknown",
     size=15, sub_size=13, color=RED, align="center")
box2(s, t, 43, 280, 540, 90, RED_DK, RED, "Layer 2 pod", "no node launches at all",
     size=15, sub_size=13, color=RED, align="center")

label(s, t, 659, 140, 540, 24, "static pool  (StaticCapacity gate, replicas: 1)",
      size=15, color=GRN_HI, bold=True)
box2(s, t, 659, 174, 540, 90, GRN_DK, GRN, "Layer 1 pod", "runs on the static node",
     size=15, sub_size=13, color=GRN_HI, align="center")
box2(s, t, 659, 280, 540, 90, GRN_DK, GRN, "Layer 2 pod", "runs on the same static node",
     size=15, sub_size=13, color=GRN_HI, align="center")
box2(s, t, 659, 400, 540, 70, GRN_DK, GRN, "Ready in 38s", "node becomes initialized",
     size=16, sub_size=13, color=GRN_HI, align="center")
arrow(s, t, 929, 370, 929, 400, color=GRN_HI)
box(s, t, 43, 400, 540, 70, CHIP, stroke=EDGE,
    body="Karpenter has no Neuron DRA gate: dynamic provisioning cannot see the claim is already satisfied",
    size=13, color=MUTED, pattern=False)
NAMES.append("07-e4c-dynamic-vs-static")

# --------------------------------------------------------- 07-e4plus-double-advertisement
s = d.slide().s
title(s, t, "E4+: the same /dev/neuron0 reaches two Pods, no warning")
box(s, t, 43, 150, 300, 70, RED_DK, stroke=RED, body="device plugin\n(should not run here)",
    size=14, color=RED)
box(s, t, 403, 150, 300, 70, LINK_DK, stroke=LINK, body="DRA driver (existing)", size=14,
    color=LINK_HI)
box(s, t, 193, 270, 300, 60, GREY, stroke=EDGE, body="/dev/neuron0\nPCI 0000:33:00.0",
    size=14, color=WHITE)
arrow(s, t, 193, 220, 280, 270, color=RED)
arrow(s, t, 553, 220, 400, 270, color=LINK_HI)
box2(s, t, 43, 380, 450, 90, RED_DK, RED, "device-plugin pod", "same device", size=16,
     sub_size=13, color=RED, align="center")
box2(s, t, 663, 380, 450, 90, LINK_DK, LINK, "Layer 2 pod", "same device, via DRA",
     size=16, sub_size=13, color=LINK_HI, align="center")
arrow(s, t, 320, 330, 268, 380, color=RED)
arrow(s, t, 353, 330, 888, 380, color=LINK)
box(s, t, 43, 500, 1156, 70, RED_DK, stroke=RED,
    body="no warning -- the same root cause as E1 on NVIDIA: opt-out DaemonSet affinity meets an existing DRA driver",
    size=15, color=RED)
NAMES.append("07-e4plus-double-advertisement")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
