"""Figures for 06-dra-experiments-nvidia.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "06-dra-experiments-nvidia.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ------------------------------------------------------------------ 06-e1-double-allocation
s = d.slide().s
title(s, t, "E1: the same GPU UUID reaches two Pods, no warning")
box(s, t, 43, 150, 300, 70, RED_DK, stroke=RED, body="device plugin\n(should not run here)",
    size=14, color=RED)
box(s, t, 403, 150, 300, 70, LINK_DK, stroke=LINK, body="DRA driver", size=15,
    color=LINK_HI)
box(s, t, 193, 270, 300, 60, GREY, stroke=EDGE, body="kubelet", size=16, color=WHITE)
arrow(s, t, 193, 220, 280, 270, color=RED)
arrow(s, t, 553, 220, 400, 270, color=LINK_HI)
box2(s, t, 43, 380, 450, 90, RED_DK, RED, "Pod A  (limits)",
     "nvidia.com/gpu: 1  via device plugin", size=16, sub_size=13, color=RED,
     align="center")
box2(s, t, 663, 380, 450, 90, LINK_DK, LINK, "Pod B  (ResourceClaim)",
     "same GPU, via DRA", size=16, sub_size=13, color=LINK_HI, align="center")
arrow(s, t, 320, 330, 268, 380, color=RED)
arrow(s, t, 353, 330, 888, 380, color=LINK)
box(s, t, 43, 500, 1156, 70, RED_DK, stroke=RED,
    body="same GPU UUID handed to both Pods -- no warning, no event, anywhere", size=16,
    color=RED)
NAMES.append("06-e1-double-allocation")

# ---------------------------------------------------------------------- 06-e2-node-states
s = d.slide().s
title(s, t, "E2: a Layer 1 pod leaves the node stuck uninitialized")
box2(s, t, 403, 150, 400, 60, GREY, EDGE, "dynamically provisioned DRA pool", None,
     size=15, color=WHITE, align="center")
box2(s, t, 123, 260, 380, 90, GRN_DK, GRN, "Layer 1 pod", "resources.limits", size=16,
     sub_size=13, color=GRN_HI, align="center")
box2(s, t, 703, 260, 380, 90, YEL_DK, YEL, "Layer 2 pod", "ResourceClaim", size=16,
     sub_size=13, color=YEL, align="center")
arrow(s, t, 313, 210, 313, 260, color=GRN_HI)
arrow(s, t, 893, 210, 893, 260, color=YEL)
box2(s, t, 123, 400, 380, 110, RED_DK, RED, "Initialized=Unknown  (47s)",
     "not consolidated after 5 min+\nreason: ResourceNotRegistered", size=15,
     sub_size=12, color=RED, align="center")
box2(s, t, 703, 400, 380, 110, GRN_DK, GRN, "Initialized=True  (48s)",
     "consolidated after 145s\nonce the pod is deleted", size=15, sub_size=12,
     color=GRN_HI, align="center")
arrow(s, t, 313, 350, 313, 400, color=RED)
arrow(s, t, 893, 350, 893, 400, color=GRN_HI)
NAMES.append("06-e2-node-states")

# --------------------------------------------------------------------- 06-e3-kueue-flavor
s = d.slide().s
title(s, t, "E3: a Layer 2 job gets stuck in the free device-plugin flavor")
box2(s, t, 43, 220, 320, 90, YEL_DK, YEL, "Layer 2 job", "ResourceClaimTemplate",
     size=17, sub_size=13, color=YEL, align="center")
arrow(s, t, 363, 265, 463, 220, color=RED)
box2(s, t, 463, 150, 340, 90, RED_DK, RED, "device-plugin flavor", "free, so admitted here",
     size=15, sub_size=13, color=RED, align="center")
box2(s, t, 843, 150, 340, 90, CHIP, EDGE, "cannot allocate all claims", "stuck", size=15,
     sub_size=13, color=RED, align="center")
arrow(s, t, 803, 195, 843, 195, color=RED)
arrow(s, t, 363, 290, 463, 335, color=GRN_HI)
box2(s, t, 463, 335, 340, 90, GRN_DK, GRN, "DRA flavor", "pinned by karpenter.sh/nodepool",
     size=15, sub_size=13, color=GRN_HI, align="center")
box2(s, t, 843, 335, 340, 90, GRN_DK, GRN, "runs correctly", "claims allocate", size=15,
     sub_size=13, color=GRN_HI, align="center")
arrow(s, t, 803, 380, 843, 380, color=GRN_HI)
NAMES.append("06-e3-kueue-flavor")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
