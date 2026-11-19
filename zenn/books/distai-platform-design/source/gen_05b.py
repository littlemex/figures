"""Figures for 05b-delivery-layer.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05b-delivery-layer.pptx")
d = new_deck()
NAMES = []
t = d.theme

# -------------------------------------------------------------------------- 05b-bootstrap-flow
s = d.slide().s
title(s, t, "Terraform makes the association; bootstrap.sh writes 3 objects")
legend(s, t, 43, 108, [(GRN_DK, GRN, "AWS API side (Terraform)"),
                       (LINK_DK, LINK, "inside the cluster (bootstrap.sh)")])
box2(s, t, 43, 150, 320, 78, GRN_DK, GRN, "terraform apply",
     "infra/foundation/argocd.tf", size=15, sub_size=12, color=GRN_HI, align="center",
     pad=10)
arrow(s, t, 203, 228, 203, 238, color=GRN_HI)
box2(s, t, 43, 238, 320, 90, GRN_DK, GRN, "aws_eks_access_policy_association",
     "AmazonEKSClusterAdminPolicy", size=12, sub_size=11, color=GRN_HI, align="center",
     pad=10)

box(s, t, 403, 150, 2, 400, LINK, stroke=None, pattern=False)

box2(s, t, 463, 150, 350, 110, LINK_DK, LINK, "bootstrap.sh",
     "2 checks before any write\n(kubeconfig, existing Secret's cluster_arn)",
     size=15, sub_size=11, color=LINK_HI, align="center", pad=10)
arrow(s, t, 363, 283, 463, 205, color=GRN_HI)
arrow(s, t, 638, 260, 638, 280, color=LINK_HI)
box2(s, t, 463, 280, 350, 84, LINK_DK, LINK, "1. cell-registration Secret",
     "argocd.argoproj.io/secret-type: cluster", size=13, sub_size=11, color=LINK_HI,
     align="center", pad=10)
arrow(s, t, 638, 364, 638, 380, color=LINK_HI)
box2(s, t, 463, 380, 350, 62, LINK_DK, LINK, "2. platform AppProject", None, size=14,
     color=LINK_HI, align="center", pad=10)
arrow(s, t, 638, 442, 638, 456, color=LINK_HI)
box2(s, t, 463, 456, 350, 76, LINK_DK, LINK, "3. root Application",
     "spec.project: platform", size=13, sub_size=11, color=LINK_HI, align="center",
     pad=10)
arrow(s, t, 813, 475, 893, 370, color=YEL)
arrow(s, t, 813, 500, 893, 510, color=YEL)
box2(s, t, 893, 330, 260, 80, YEL_DK, YEL, "platform\nApplicationSet", None, size=14,
     color=YEL, align="center")
box2(s, t, 893, 470, 260, 80, YEL_DK, YEL, "cells\nApplicationSet", None, size=14,
     color=YEL, align="center")
NAMES.append("05b-bootstrap-flow")

# ------------------------------------------------------------------------ 05b-generator-matrix
s = d.slide().s
title(s, t, "Two generators, matrixed into one Application per add-on per cell")
box2(s, t, 43, 170, 440, 90, LINK_DK, LINK, "cell-registration Secret",
     "annotations: region, revision, ...", size=16, sub_size=12, color=LINK_HI,
     align="center")
arrow(s, t, 263, 260, 263, 320, color=LINK_HI)
box2(s, t, 43, 320, 440, 80, LINK_DK, LINK, "Cluster generator", None, size=16,
     color=LINK_HI, align="center")

box2(s, t, 663, 170, 440, 90, YEL_DK, YEL, "addons/<name>/addon.yaml",
     "chart, version, wave, values", size=15, sub_size=12, color=YEL, align="center")
arrow(s, t, 883, 260, 883, 320, color=YEL)
box2(s, t, 663, 320, 440, 80, YEL_DK, YEL, "Git file generator", None, size=16,
     color=YEL, align="center")

arrow(s, t, 283, 400, 503, 460, color=LINK_HI)
arrow(s, t, 903, 400, 683, 460, color=YEL)
box2(s, t, 403, 460, 380, 80, GRN_DK, GRN, "Matrix generator",
     "selector: secret-type=cluster", size=16, sub_size=12, color=GRN_HI, align="center")
arrow(s, t, 593, 540, 593, 580, color=GRN_HI)
box2(s, t, 403, 580, 380, 70, GRN_DK, GRN, "Application", "metadata.name: {{name}}-{{addon}}",
     size=16, sub_size=12, color=GRN_HI, align="center")
NAMES.append("05b-generator-matrix")

# -------------------------------------------------------------------------- 05b-ordering-steps
s = d.slide().s
title(s, t, "RollingSync orders steps within an ApplicationSet, not across them")
label(s, t, 43, 140, 540, 24, "platform.ApplicationSet  (RollingSync)", size=16,
      color=LINK_HI, bold=True)
psteps = ["crds", "controllers", "accelerators", "extras"]
x = 43
w = 265
gap = 20
for i, step in enumerate(psteps):
    box(s, t, x, 174, w, 80, LINK_DK, stroke=LINK, body=step, size=16, color=LINK_HI)
    if i < len(psteps) - 1:
        arrow(s, t, x + w, 214, x + w + gap, 214, color=LINK_HI)
    x += w + gap

label(s, t, 328, 355, 540, 24, "cells.ApplicationSet  (RollingSync)", size=16,
      color=YEL, bold=True, align="left")
box(s, t, 43, 410, 265, 80, YEL_DK, stroke=YEL, body="capacity", size=16, color=YEL)
arrow(s, t, 308, 450, 328, 450, color=YEL)
box(s, t, 328, 410, 265, 80, YEL_DK, stroke=YEL, body="teams", size=16, color=YEL)

arrow(s, t, 304, 254, 175, 410, color=RED, dashed=True)
label(s, t, 350, 295, 300, 44, "retry-based convergence\n(not a guaranteed order)",
      size=12, color=RED, align="left")
box(s, t, 43, 500, 1156, 70, CHIP, stroke=EDGE,
    body="RollingSync only orders Application objects generated by its own ApplicationSet -- a dependency across platform and cells is retried until it converges, never ordered",
    size=14, color=MUTED, pattern=False)
NAMES.append("05b-ordering-steps")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
