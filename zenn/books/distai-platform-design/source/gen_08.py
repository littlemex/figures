"""Figures for 08-foundation.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "08-foundation.pptx")
d = new_deck()
NAMES = []
t = d.theme


def chip_col(s, items, x, y, w, h, fill, stroke, size=14, gap=10):
    yy = y
    for it in items:
        box(s, t, x, yy, w, h, fill, stroke=stroke, body=it, size=size, color=WHITE)
        yy += h + gap
    return yy - gap


# --------------------------------------------------------------------------- 08-scope
s = d.slide().s
title(s, t, "Terraform's range and Argo CD's range meet only at outputs")
label(s, t, 43, 140, 540, 26, "infra/foundation  (Terraform)", size=17, color=GRN_HI,
      bold=True)
chip_col(s, ["VPC", "EKS cluster", "system node group", "Karpenter prerequisites",
             "teardown guard"], 43, 176, 540, 56, GRN_DK, GRN, size=15)
label(s, t, 659, 140, 540, 26, "Argo CD  (not this layer)", size=17, color=LINK_HI,
      bold=True)
chip_col(s, ["NodePool", "Kueue", "device plugin", "DRA driver"], 659, 176, 540, 56,
         LINK_DK, LINK, size=15)
arrow(s, t, 599, 300, 643, 300, color=YEL, both=True)
label(s, t, 540, 326, 220, 22, "outputs only", size=13, color=YEL, align="center")
NAMES.append("08-scope")

# ------------------------------------------------------------------------ 08-interface
s = d.slide().s
title(s, t, "10 variables in, 11 outputs out")
box2(s, t, 43, 230, 280, 110, GREY, EDGE, "variables", "10", size=18, sub_size=28,
     color=WHITE, align="center")
arrow(s, t, 323, 285, 423, 285, color=WHITE)
box2(s, t, 423, 230, 360, 110, GRN_DK, GRN, "infra/foundation", "1 cell, 1 state",
     size=17, sub_size=14, color=GRN_HI, align="center")
arrow(s, t, 783, 285, 883, 285, color=WHITE)
box2(s, t, 883, 230, 280, 110, LINK_DK, LINK, "outputs", "11", size=18, sub_size=28,
     color=LINK_HI, align="center")
chip_col(s, ["cluster_name", "karpenter_node_role_name",
             "karpenter_interruption_queue_name", "argocd_capability_arn"], 43, 390,
         1120, 44, CHIP, EDGE, size=13, gap=8)
label(s, t, 43, 390 - 28, 1120, 22, "example outputs the later layers read", size=12,
      color=MUTED, align="left")
NAMES.append("08-interface")

# -------------------------------------------------------------------------- 08-network
s = d.slide().s
title(s, t, "VPC CIDR split across Availability Zones")
box2(s, t, 43, 140, 1156, 30, None, None, "VPC  10.0.0.0/16", None, size=15,
     color=WHITE, pad=0)
azs = ["AZ 1", "AZ 2", "AZ 3"]
x0, y0, cw = 43, 190, 360
for i, az in enumerate(azs):
    x = x0 + i * (cw + 20)
    box2(s, t, x, y0, cw, 200, GRN_DK, GRN, az, None, size=16, color=GRN_HI,
         align="center", pad=10)
    box2(s, t, x + 16, y0 + 54, cw - 32, 130, GRN_DK, GRN, "private subnet",
         "/19, ~8190 addresses\nKarpenter nodes here\ntag: karpenter.sh/discovery",
         size=14, sub_size=12, color=GRN_HI, align="center", pad=8)
box2(s, t, 43, 410, 1156, 90, YEL_DK, YEL, "public subnets  (/24 each, one per AZ)",
     "NAT gateway + load balancers only -- no instance gets a public IP", size=15,
     sub_size=13, color=YEL, align="left")
box(s, t, 43, 520, 1156, 60, CHIP, stroke=EDGE,
    body="control plane and system node group avoid AZs EKS can't use there (use1-az3, usw1-az2, cac1-az3)",
    size=13, color=MUTED, pattern=False)
NAMES.append("08-network")

# ------------------------------------------------------------------------- 08-teardown
s = d.slide().s
title(s, t, "teardown guard forces: policies, then instances, then network")
legend(s, t, 43, 110, [(RED_DK, RED, "wrong order (fails)"),
                       (GRN_DK, GRN, "teardown-guard.sh order")])
label(s, t, 43, 160, 540, 24, "destroying the network first", size=15, color=RED,
      bold=True)
box2(s, t, 43, 194, 540, 70, RED_DK, RED, "NAT gateway destroyed", None, size=15,
     color=RED, align="center")
arrow(s, t, 313, 264, 313, 310, color=RED)
box2(s, t, 43, 310, 540, 70, RED_DK, RED, "Karpenter instance loses its route to AWS",
     None, size=14, color=RED, align="center")
arrow(s, t, 313, 380, 313, 426, color=RED)
box2(s, t, 43, 426, 540, 70, RED_DK, RED, "stray ENI blocks destroy", None, size=15,
     color=RED, align="center")

label(s, t, 659, 160, 540, 24, "teardown-guard.sh  (destroy-time provisioner)",
      size=15, color=GRN_HI, bold=True)
box2(s, t, 659, 194, 540, 62, GRN_DK, GRN, "0. Karpenter controller policies detached",
     "terraform_data depends_on -- blocks new launches first", size=13, sub_size=11,
     color=GRN_HI, align="center")
arrow(s, t, 929, 256, 929, 284, color=GRN_HI)
box2(s, t, 659, 284, 540, 62, GRN_DK, GRN, "1. terminate instances", "tag: eks-cluster-name",
     size=13, sub_size=11, color=GRN_HI, align="center")
arrow(s, t, 929, 346, 929, 374, color=GRN_HI)
box2(s, t, 659, 374, 540, 62, GRN_DK, GRN, "2. delete stray ENIs", "aws-K8S-* only",
     size=13, sub_size=11, color=GRN_HI, align="center")
arrow(s, t, 929, 436, 929, 464, color=GRN_HI)
box2(s, t, 659, 464, 540, 62, GRN_DK, GRN, "3. network destroy proceeds",
     "cluster, node role, VPC", size=13, sub_size=11, color=GRN_HI, align="center")
NAMES.append("08-teardown")

# ------------------------------------------------------------------------------ 08-e2e
s = d.slide().s
title(s, t, "7 end-to-end runs: a PASS that still left a launch template behind")
legend(s, t, 43, 108, [(RED_DK, RED, "FAIL (test defect)"), (GRN_DK, GRN, "PASS (clean)"),
                       (YEL_DK, YEL, "script said PASS, leftover found")])
runs = [
    ("run 1", "FAIL", "null output\ntreated as missing",
     RED_DK, RED, RED),
    ("run 2", "PASS", "apply 636s\ndestroy 883s", GRN_DK, GRN, GRN_HI),
    ("run 3", "PASS", "commit 00afa70\nafter review", GRN_DK, GRN, GRN_HI),
    ("run 4", "FAIL", "netpol pods:\nmissing toleration",
     RED_DK, RED, RED),
    ("run 5", "PASS", "commit 66c8cf8\ntenancy prep", GRN_DK, GRN, GRN_HI),
    ("run 6", "PASS*", "fc1afc0: guard's tag\nkey, Karpenter v1\nnever sets it",
     YEL_DK, YEL, YEL),
    ("run 7", "PASS", "7884eaf: tag key +\nleftover check fixed", GRN_DK, GRN, GRN_HI),
]
x = 43
w = 148
gap = 13
for head, status, note, fill, stroke, col in runs:
    box2(s, t, x, 150, w, 200, fill, stroke, f"{head}\n{status}", note, size=14,
         sub_size=10, color=col, align="center", pad=12)
    if head != "run 7":
        arrow(s, t, x + w, 250, x + w + gap, 250, color=WHITE)
    x += w + gap
box(s, t, 43, 390, 1156, 70, CHIP, stroke=EDGE,
    body="a script PASS is only proof of cleanup for resource types its leftover check actually covers -- run 6's launch template was found by the verifier re-checking tags by hand",
    size=14, color=MUTED, pattern=False)
NAMES.append("08-e2e")

# -------------------------------------------------------------------------- 08-addon-order
s = d.slide().s
title(s, t, "vpc-cni waits for the Pod Identity agent to go ACTIVE first")
legend(s, t, 43, 110, [(GRN_DK, GRN, "before nodes"), (YEL_DK, YEL, "gated: depends_on ACTIVE"),
                       (LINK_DK, LINK, "node joins / after nodes")])
box2(s, t, 43, 160, 220, 90, GRN_DK, GRN, "kube-proxy", "before nodes", size=14,
     sub_size=11, color=GRN_HI, align="center", pad=12)
box2(s, t, 303, 160, 280, 90, GRN_DK, GRN, "eks-pod-identity-agent", "before nodes",
     size=13, sub_size=11, color=GRN_HI, align="center", pad=12)
arrow(s, t, 443, 250, 443, 300, color=YEL)
label(s, t, 463, 260, 80, 20, "ACTIVE", size=11, color=YEL, align="left")
box2(s, t, 303, 300, 280, 100, YEL_DK, YEL, "Pod Identity association",
     "kube-system/aws-node", size=12, sub_size=11, color=YEL, align="center", pad=12)
arrow(s, t, 583, 345, 643, 345, color=YEL)
box2(s, t, 643, 300, 220, 100, YEL_DK, YEL, "vpc-cni", "depends_on the agent",
     size=14, sub_size=11, color=YEL, align="center", pad=12)
box2(s, t, 43, 460, 800, 100, LINK_DK, LINK, "system node group joins",
     "aws-node and the identity agent DaemonSet are already present -- no startup race",
     size=14, sub_size=12, color=LINK_HI, align="center", pad=12)
arrow(s, t, 153, 250, 153, 460, color=GRN_HI)
arrow(s, t, 753, 400, 753, 460, color=YEL)
box2(s, t, 883, 460, 230, 100, GRN_DK, GRN, "coredns", "after nodes (Deployment)",
     size=14, sub_size=12, color=GRN_HI, align="center", pad=12)
arrow(s, t, 843, 510, 883, 510, color=LINK_HI)
NAMES.append("08-addon-order")

# ------------------------------------------------------------------------------ 08-tenancy
s = d.slide().s
title(s, t, "What this layer guarantees vs. what Issue #22 still has to add")
box2(s, t, 43, 150, 560, 36, None, None, "this layer  (#20 / #21)", None, size=16,
     color=GRN_HI, pad=0)
box2(s, t, 43, 196, 560, 90, GRN_DK, GRN, "IMDSv2 required, hop limit 1",
     "no Pod reaches node-role credentials via IMDS", size=14, sub_size=12,
     color=GRN_HI, align="left")
box2(s, t, 43, 296, 560, 90, GRN_DK, GRN, "aws-node: Pod Identity only",
     "node role carries no AmazonEKS_CNI_Policy", size=14, sub_size=12, color=GRN_HI,
     align="left")
box2(s, t, 43, 396, 560, 90, GRN_DK, GRN, "enableNetworkPolicy = true",
     "enforcement is on; no NetworkPolicy objects exist yet", size=14, sub_size=12,
     color=GRN_HI, align="left")

box2(s, t, 659, 150, 540, 36, None, None, "tenancy layer  (Issue #22)", None, size=16,
     color=LINK_HI, pad=0)
box2(s, t, 659, 196, 540, 90, LINK_DK, LINK, "CriticalAddonsOnly admission policy",
     "makes the taint an actual boundary (any Pod can tolerate it today)", size=14,
     sub_size=12, color=LINK_HI, align="left")
box2(s, t, 659, 296, 540, 90, LINK_DK, LINK, "the NetworkPolicy objects themselves",
     None, size=14, color=LINK_HI, align="left")
box2(s, t, 659, 396, 540, 90, LINK_DK, LINK, "AppProject per team", None, size=14,
     color=LINK_HI, align="left")
arrow(s, t, 603, 340, 659, 340, color=YEL, both=True)
box(s, t, 43, 500, 1156, 60, CHIP, stroke=EDGE,
    body="this layer only prepares the ground (IMDSv2, CNI separation, enforcement switch) -- #22 does the actual enforcing",
    size=14, color=MUTED, pattern=False)
NAMES.append("08-tenancy")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
