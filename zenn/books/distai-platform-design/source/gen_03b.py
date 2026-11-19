"""Figures for 03b-multi-tenancy.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03b-multi-tenancy.pptx")
d = new_deck()
NAMES = []
t = d.theme

# ----------------------------------------------------------------------- 03b-tenancy-overview
s = d.slide().s
title(s, t, "Admin owns the cell and the frame; teams own only their namespace")
label(s, t, 43, 140, 560, 24, "admin  (cell)", size=17, color=GRN_HI, bold=True)
box2(s, t, 43, 174, 560, 90, GRN_DK, GRN, "Terraform shell", "per-team: access entry + Pod Identity association",
     size=15, sub_size=13, color=GRN_HI, align="center")
box2(s, t, 43, 284, 560, 110, GRN_DK, GRN, "GitOps shell  (the \"frame\")",
     "Namespace, ResourceQuota, LimitRange,\ndefault NetworkPolicy, LocalQueue, AppProject itself",
     size=15, sub_size=13, color=GRN_HI, align="center")
label(s, t, 659, 140, 540, 24, "team  (namespace)", size=17, color=LINK_HI, bold=True)
box2(s, t, 659, 174, 540, 220, LINK_DK, LINK, "namespace", "Application scoped to the team's own AppProject\n(workload manifests only -- TrainJob, JobSet, Pod, Service)",
     size=15, sub_size=13, color=LINK_HI, align="center")
arrow(s, t, 619, 340, 659, 284, color=RED, dashed=True)
label(s, t, 400, 400, 260, 40, "team cannot write\ninto the frame", size=12, color=RED,
      align="center")
box(s, t, 43, 450, 1156, 60, CHIP, stroke=EDGE,
    body="cell and GitOps shell are what the earlier chapters already decided -- this chapter fills in how teams are kept apart inside them",
    size=14, color=MUTED, pattern=False)
NAMES.append("03b-tenancy-overview")

# ------------------------------------------------------------------- 03b-identity-per-team
s = d.slide().s
title(s, t, "Three paths, one IdC group per team")
box2(s, t, 43, 150, 350, 110, LINK_DK, LINK, "IdC group", "1 team = 1 group", size=16,
     sub_size=13, color=LINK_HI, align="center")
arrow(s, t, 393, 180, 473, 180, color=LINK_HI)
box2(s, t, 473, 150, 350, 110, GRN_DK, GRN, "access entry",
     "AccessScope: namespace", size=16, sub_size=13, color=GRN_HI, align="center")

box2(s, t, 43, 300, 230, 110, CHIP, EDGE, "Pod", None, size=16, color=WHITE,
     align="center")
arrow(s, t, 273, 330, 353, 330, color=YEL)
box2(s, t, 353, 300, 230, 110, YEL_DK, YEL, "Pod Identity", "association", size=15,
     sub_size=13, color=YEL, align="center")
arrow(s, t, 583, 330, 663, 330, color=YEL)
box2(s, t, 663, 300, 260, 110, YEL_DK, YEL, "shared role", "1 role for all teams", size=15,
     sub_size=13, color=YEL, align="center")
arrow(s, t, 923, 330, 1003, 330, color=YEL)
box2(s, t, 1003, 300, 196, 110, YEL_DK, YEL, "ABAC tag", "namespace\nsession tag", size=14,
     sub_size=12, color=YEL, align="center")

arrow(s, t, 218, 180, 218, 300, color=LINK_HI, dashed=True)
box2(s, t, 43, 450, 350, 100, GRN_DK, GRN, "AppProject", "roles[].groups -> this team's\nIdC group only", size=15,
     sub_size=13, color=GRN_HI, align="center")
box(s, t, 423, 450, 776, 100, CHIP, stroke=EDGE,
    body="container is not a security boundary -- Pod Identity decides which credentials a Pod gets, not which Pods share a node",
    size=14, color=MUTED, pattern=False)
NAMES.append("03b-identity-per-team")

# ---------------------------------------------------------------------- 03b-cohort-quota
s = d.slide().s
title(s, t, "The Cohort holds the real quota; each team's ClusterQueue holds only weight")
box2(s, t, 403, 150, 400, 100, GRN_DK, GRN, "Cohort", "nominalQuota  (the real capacity)",
     size=18, sub_size=14, color=GRN_HI, align="center")
teams = [("team A\nClusterQueue", "0 nominalQuota\nborrowingLimit, lendingLimit"),
         ("team B\nClusterQueue", "0 nominalQuota\nborrowingLimit, lendingLimit"),
         ("team C\nClusterQueue", "0 nominalQuota\nborrowingLimit, lendingLimit")]
x = 43
w = 360
gap = 20
for head, sub in teams:
    box2(s, t, x, 310, w, 126, YEL_DK, YEL, head, sub, size=14, sub_size=12, color=YEL,
         align="center")
    arrow(s, t, x + w // 2, 310, x + w // 2 + (583 - x - w // 2), 250, color=GRN_HI)
    box2(s, t, x, 480, w, 60, LINK_DK, LINK, "LocalQueue  (in the team's namespace)",
         None, size=13, color=LINK_HI, align="center")
    arrow(s, t, x + w // 2, 480, x + w // 2, 436, color=LINK_HI)
    x += w + gap
NAMES.append("03b-cohort-quota")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
