"""Figures for 03-capacity-pools.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03-capacity-pools.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ------------------------------------------------------------------------ 03-pools-pairing
s = d.slide().s
title(s, t, "NodePool and ResourceFlavor, joined by karpenter.sh/nodepool")
cols = [
    ("-rsv", "reserved", "nominalQuota = real count", GRN_DK, GRN, GRN_HI),
    ("-od", "on-demand", "nominalQuota = budget cap", YEL_DK, YEL, YEL),
    ("-flex", "spot, on-demand", "nominalQuota = budget cap", YEL_DK, YEL, YEL),
]
x0, y0, cw, gap = 43, 150, 350, 56
for i, (name, ctype, quota, fill, stroke, col) in enumerate(cols):
    x = x0 + i * (cw + gap)
    box2(s, t, x, y0, cw, 70, fill, stroke, f"NodePool  {name}", f"capacity-type: {ctype}",
         size=15, sub_size=12, color=col, align="left", pad=12)
    arrow(s, t, x + cw // 2, y0 + 70, x + cw // 2, y0 + 150, color=col, both=True)
    label(s, t, x, y0 + 94, cw, 20, "karpenter.sh/nodepool", size=11, color=MUTED,
          align="center")
    box2(s, t, x, y0 + 150, cw, 70, fill, stroke, f"ResourceFlavor  {name}", quota,
         size=15, sub_size=12, color=col, align="left", pad=12)
box(s, t, 43, y0 + 260, 1156, 54, CHIP, stroke=EDGE,
    body="the name is the only link -- no new label is minted; Helm values set nodeLabels to match",
    size=13, color=MUTED, pattern=False)
NAMES.append("03-pools-pairing")

# --------------------------------------------------------------------- 03-workload-routes
s = d.slide().s
title(s, t, "Workload type decides the flavor order and interruption handling")
rows = [
    ("short, single-node training", "-rsv (borrow)  ->  -flex", "fine to retry after interruption"),
    ("multi-node EFA training", "-rsv only", "gang admission + waitForPodsReady, checkpoint before Capacity Block ends"),
    ("long-running inference", "-rsv (ODCR)  ->  -od", "Capacity Block is load-test only, not for always-on"),
    ("interruptible batch", "-rsv (borrow only)  ->  -flex", "SkyPilot managed jobs re-find and restart; reclaimWithinCohort takes borrowed capacity back"),
]
y = 150
rh = 102
for head, route, note in rows:
    box2(s, t, 43, y, 300, rh, LINK_DK, LINK, head, None, size=15, color=LINK_HI,
         align="left", pad=12)
    box(s, t, 363, y, 280, rh, YEL_DK, stroke=YEL, body=route, size=14, color=YEL)
    box2(s, t, 663, y, 536, rh, CHIP, EDGE, note, None, size=13, color=WHITE,
         align="left", pad=12, head_bold=False)
    y += rh + 14
NAMES.append("03-workload-routes")

# ------------------------------------------------------------------- 03-risky-assumption
s = d.slide().s
title(s, t, "The riskiest assumption: admitted means the capacity exists")
y0 = 220
box2(s, t, 43, y0, 320, 110, LINK_DK, LINK, "Kueue admit", "job is let in", size=17,
     sub_size=13, color=LINK_HI, align="center")
arrow(s, t, 363, y0 + 55, 483, y0 + 55, color=WHITE)
box2(s, t, 483, y0, 320, 110, GRN_DK, GRN, "Karpenter launch",
     "must still start a node", size=17, sub_size=13, color=GRN_HI, align="center")
box2(s, t, 923, y0 - 90, 276, 80, GRN_DK, GRN, "-rsv", "capacity guaranteed", size=16,
     sub_size=13, color=GRN_HI, align="center")
arrow(s, t, 803, y0 + 10, 923, y0 - 50, color=GRN_HI)
box2(s, t, 923, y0 + 100, 276, 80, RED_DK, RED, "-od / -flex", "not guaranteed",
     size=16, sub_size=13, color=RED, align="center")
arrow(s, t, 803, y0 + 95, 923, y0 + 140, color=RED)
box(s, t, 43, y0 + 220, 1156, 60, CHIP, stroke=EDGE,
    body="ProvisioningRequest checks capacity before admission, but is built for cluster-autoscaler, not Karpenter",
    size=13, color=MUTED, pattern=False)
NAMES.append("03-risky-assumption")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
