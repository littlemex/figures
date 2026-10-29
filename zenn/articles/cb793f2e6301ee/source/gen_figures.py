"""gen_figures.py -- figures for the Zenn article on deploying to BYOI (bring your own infrastructure) nodes
with EKS Hybrid Nodes and the EKS Capabilities managed Argo CD.

    /usr/bin/python3 gen_figures.py <out.pptx>

1. targets   what the managed Argo CD can deploy to, and how each target is registered
2. hybrid    why a BYOI machine joined as a hybrid node is reachable: Argo CD talks
             only to the EKS API server; the kubelet connects out over the private link
3. two-stage reaching a non-EKS cluster through a relay Argo CD that Managed Argo CD installs
Text is English. Facts come from the article and from
littlemex/distributed-ai investigations/2026-10-29-eks-capabilities-hybrid-nodes.
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
LINK = RGBColor(40, 150, 240)
LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
RED = RGBColor(235, 87, 87)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25, bold=True):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, bold, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def frame(s, x, y, w, h, name, color=EDGE):
    box(s, x, y, w, h, None, stroke=color, radius=0.03, dash=MSO_LINE_DASH_STYLE.DASH, sw=1.5)
    label(s, x + 14, y + 6, w - 28, 26, name, size=14, color=MUTED, align="left")


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


# One colour scheme in all three figures: blue = run by AWS, grey = in the cluster
# VPC, green = run by you / BYOI, yellow = the non-EKS cluster.
# ------------------------------------------------------------------ 0. placement
s = d.slide()
title(s.s, "Where each piece of Managed Argo CD lives",
      "Blue: run by AWS.  Grey: your EKS cluster.  Green: BYOI.  Yellow: non-EKS cluster")
frame(s.s, 43, 112, 300, 180, "Run by AWS", color=LINK)
box(s.s, 63, 160, 260, 100, LINK_DK, stroke=LINK, body="Managed Argo CD\ncontroller", size=17)
box(s.s, 63, 340, 260, 70, CHIP, stroke=EDGE, body="Helm chart / Git repo\n(outside AWS)", size=13, color=MUTED)
sh.arrow(s.s, t, 193, 340, 193, 260, color=WHITE, width=1.75)
label(s.s, 200, 300, 120, 26, "fetches", size=12, color=MUTED, align="left")

frame(s.s, 463, 112, 520, 400, "Your EKS cluster")
box(s.s, 483, 160, 230, 100, LINK_DK, stroke=LINK, body="EKS control plane\nAPI server", size=15)
frame(s.s, 733, 140, 230, 130, "namespace argocd")
box(s.s, 748, 180, 200, 36, GREY, stroke=EDGE, body="Application", size=13)
box(s.s, 748, 224, 200, 36, GREY, stroke=EDGE, body="cluster secret", size=13)
sh.arrow(s.s, t, 713, 210, 733, 210, color=WHITE, width=1.5)
box(s.s, 483, 340, 230, 80, GREY, stroke=EDGE, body="cloud nodes", size=15)
box(s.s, 733, 340, 230, 80, GRN_DK, stroke=GRN, body="hybrid nodes (BYOI)", size=15)
sh.arrow(s.s, t, 598, 260, 598, 340, color=WHITE, width=1.75)
sh.arrow(s.s, t, 690, 260, 800, 340, color=WHITE, width=1.75)
label(s.s, 483, 440, 480, 50, "Application and cluster secret are\nKubernetes objects stored in this cluster", size=12, color=MUTED, align="left")

sh.arrow(s.s, t, 323, 200, 483, 200, color=LINK, width=2.5, head=True)
label(s.s, 343, 140, 120, 50, "reads, then\napplies", size=12, color=LINK)
box(s.s, 63, 450, 260, 56, CHIP, stroke=EDGE, body="you: kubectl apply", size=14)
sh.arrow(s.s, t, 323, 470, 483, 250, color=WHITE, width=1.75, dashed=True)

box(s.s, 1013, 160, 224, 100, YEL_DK, stroke=YEL, body="non-EKS cluster", size=15)
label(s.s, 1013, 270, 224, 50, "not a target of\nManaged Argo CD", size=12, color=MUTED)

# ------------------------------------------------------------------ 1. register
s = d.slide()
title(s.s, "How Managed Argo CD reaches a cluster",
      "Blue: run by AWS.  Grey: in your cluster.  Green: applied.  Yellow: where it stops")
label(s.s, 43, 118, 600, 30, "Target registered by EKS cluster ARN", size=17, bold=True, color=GRN_HI, align="left")
box(s.s, 43, 160, 260, 120, GREY, stroke=EDGE, body="cluster secret\nserver: EKS cluster ARN", size=15)
box(s.s, 343, 160, 300, 120, LINK_DK, stroke=LINK, body="Managed Argo CD\nfinds the cluster by ARN,\nsigns in with its IAM role", size=15)
box(s.s, 683, 160, 280, 120, GREY, stroke=EDGE, body="EKS access entry\nIAM role to Kubernetes\npermissions", size=15)
box(s.s, 1003, 160, 234, 120, GRN_DK, stroke=GRN, body="manifests\napplied", size=16)
for x1, x2 in ((303, 343), (643, 683), (963, 1003)):
    sh.arrow(s.s, t, x1, 220, x2, 220, color=WHITE, width=2.25)

label(s.s, 43, 330, 600, 30, "Target registered by API URL + token", size=17, bold=True, color=YEL, align="left")
box(s.s, 43, 372, 260, 120, GREY, stroke=EDGE, body="cluster secret\nserver: API URL\nconfig: bearer token", size=15)
box(s.s, 343, 372, 300, 120, LINK_DK, stroke=LINK, body="Managed Argo CD\nexpects an ARN", size=15)
box(s.s, 683, 372, 280, 120, YEL_DK, stroke=YEL, body="Application stops\nserver should be specified\nas a cluster ARN", size=14)
box(s.s, 1003, 372, 234, 120, None, stroke=EDGE, dash=MSO_LINE_DASH_STYLE.DASH, body="non-EKS cluster\nnothing arrives", size=15, color=MUTED)
sh.arrow(s.s, t, 303, 432, 343, 432, color=WHITE, width=2.25)
sh.arrow(s.s, t, 643, 432, 683, 432, color=YEL, width=2.25)
label(s.s, 43, 498, 260, 26, "created without error", size=13, color=MUTED)

# ------------------------------------------------------------------ 2. hybrid deploy
s = d.slide()
title(s.s, "How a deployment reaches BYOI",
      "Blue: run by AWS.  Grey: AWS cloud nodes.  Green: BYOI")
box(s.s, 43, 220, 260, 110, LINK_DK, stroke=LINK, body="Managed Argo CD", size=18)
frame(s.s, 353, 140, 300, 270, "EKS control plane", color=LINK)
box(s.s, 373, 180, 260, 80, LINK_DK, stroke=LINK, body="API server", size=16)
box(s.s, 373, 300, 260, 80, LINK_DK, stroke=LINK, body="scheduler\npicks a node per Pod", size=15)
sh.arrow(s.s, t, 303, 260, 373, 225, color=WHITE, width=2.25)
label(s.s, 300, 196, 70, 30, "apply", size=13, color=MUTED)
sh.arrow(s.s, t, 503, 260, 503, 300, color=WHITE, width=1.75)
box(s.s, 793, 160, 444, 100, GREY, stroke=EDGE, body="cloud nodes (EC2 in the cluster VPC)", size=16)
box(s.s, 793, 330, 444, 100, GRN_DK, stroke=GRN, body="hybrid nodes (BYOI)\neks.amazonaws.com/compute-type: hybrid", size=13)
sh.arrow(s.s, t, 633, 330, 793, 210, color=WHITE, width=2)
sh.arrow(s.s, t, 633, 350, 793, 380, color=GRN_HI, width=2.5)
label(s.s, 650, 186, 140, 40, "affinity\nNotIn hybrid", size=12, color=MUTED)
label(s.s, 640, 400, 150, 50, "nodeSelector\ncompute-type: hybrid", size=12, color=GRN_HI)

# ------------------------------------------------------------------ 2b. hybrid network
s = d.slide()
title(s.s, "Connectivity between the cluster VPC and BYOI",
      "Grey: your AWS settings.  Green: BYOI.  Solid: from the node.  Dashed: from the API server")
frame(s.s, 43, 112, 440, 440, "Cluster VPC and EKS settings")
box(s.s, 63, 150, 400, 80, GREY, stroke=EDGE, body="control plane ENIs\nendpoint: private only", size=15)
box(s.s, 63, 260, 400, 60, CHIP, stroke=EDGE, body="VPC route table: BYOI node and pod CIDRs\nto the private link", size=13)
box(s.s, 63, 335, 400, 60, CHIP, stroke=EDGE, body="cluster security group:\nallow BYOI node and pod CIDRs", size=13)
box(s.s, 63, 410, 400, 70, CHIP, stroke=EDGE, body="EKS: RemoteNodeNetwork = BYOI node CIDR\nRemotePodNetwork = BYOI pod CIDR", size=13)

box(s.s, 513, 150, 200, 400, None, stroke=EDGE, dash=MSO_LINE_DASH_STYLE.DASH, radius=0.05)
label(s.s, 513, 470, 200, 70, "private link\nVPN / Direct Connect\ntested: Transit Gateway", size=12, color=MUTED)

frame(s.s, 743, 112, 494, 440, "BYOI network", color=GRN)
box(s.s, 763, 150, 300, 80, GRN_DK, stroke=GRN, body="hybrid node\nkubelet, Cilium", size=15)
box(s.s, 763, 310, 300, 80, GRN_DK, stroke=GRN_HI, body="Pods\nBYOI pod CIDR", size=15)
box(s.s, 763, 430, 454, 70, CHIP, stroke=EDGE, body="your network: BGP or static route\nfor the BYOI pod CIDR", size=13)
sh.arrow(s.s, t, 913, 230, 913, 310, color=WHITE, width=1.5)

sh.arrow(s.s, t, 763, 172, 463, 172, color=GRN_HI, width=2.75)
label(s.s, 523, 140, 180, 30, "kubelet to API: 443", size=12, color=GRN_HI)
sh.arrow(s.s, t, 463, 210, 763, 210, color=WHITE, width=1.75, dashed=True)
label(s.s, 523, 214, 180, 30, "API to kubelet: 10250", size=12, color=MUTED)

# ------------------------------------------------------------------ 3a. relay concept
s = d.slide()
title(s.s, "Managed Argo CD hands off to a self-hosted Argo CD",
      "Blue: run by AWS.  Green: self-hosted, run by you.  Yellow: non-EKS cluster")
box(s.s, 43, 230, 300, 130, LINK_DK, stroke=LINK, body="Managed Argo CD", size=19)
frame(s.s, 453, 170, 340, 250, "EKS cluster")
box(s.s, 473, 230, 300, 130, GRN_DK, stroke=GRN_HI, body="relay Argo CD\n(self-hosted)", size=18)
box(s.s, 903, 230, 334, 130, YEL_DK, stroke=YEL, body="non-EKS cluster", size=18)
sh.arrow(s.s, t, 343, 295, 473, 295, color=LINK, width=2.75)
label(s.s, 343, 180, 130, 100, "installs it\nlike any app,\nwith its\nApplications", size=12, color=LINK)
sh.arrow(s.s, t, 773, 295, 903, 295, color=GRN_HI, width=2.75)
label(s.s, 783, 200, 120, 80, "deploys by\nAPI URL\n+ token", size=12, color=GRN_HI)
label(s.s, 43, 450, 1194, 30, "you change what is deployed in one place, the Applications on Managed Argo CD, except the cluster token", size=14, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. relay auth
s = d.slide()
title(s.s, "Who signs in where in the relay setup",
      "Blue: run by AWS.  Green: relay Argo CD, run by you.  Yellow: non-EKS cluster.  Each arrow: the credential it uses")
box(s.s, 43, 170, 260, 100, LINK_DK, stroke=LINK, body="Managed Argo CD", size=18)
label(s.s, 43, 276, 260, 30, "people sign in: Identity Center", size=12, color=MUTED)

frame(s.s, 353, 112, 520, 440, "EKS cluster")
box(s.s, 373, 160, 230, 110, LINK_DK, stroke=LINK, body="API server\naccess entry:\nIAM role to Kubernetes\npermissions", size=12)
box(s.s, 373, 370, 480, 110, GRN_DK, stroke=GRN_HI, body="relay Argo CD\nown ServiceAccount + ClusterRole", size=15)
label(s.s, 373, 486, 480, 50, "default in-cluster target removed, AppProject limits destinations\npeople sign in: local admin", size=12, color=MUTED, align="left")
box(s.s, 633, 160, 220, 110, GRN_DK, stroke=GRN, body="cluster secret\nnon-EKS token\n(not in Git)", size=13)
sh.arrow(s.s, t, 303, 215, 373, 215, color=LINK, width=2.5)
label(s.s, 303, 222, 70, 40, "IAM role", size=12, color=LINK)
sh.arrow(s.s, t, 488, 370, 488, 270, color=GRN_HI, width=2)
label(s.s, 493, 300, 140, 40, "ServiceAccount", size=12, color=GRN_HI, align="left")
sh.arrow(s.s, t, 743, 370, 743, 270, color=GRN_HI, width=1.5, dashed=True)
label(s.s, 748, 300, 120, 40, "reads token", size=12, color=MUTED, align="left")

frame(s.s, 923, 112, 314, 440, "Non-EKS cluster", color=YEL)
box(s.s, 943, 300, 274, 120, YEL_DK, stroke=YEL, body="API server\nRBAC for the token's\nServiceAccount", size=14)
sh.arrow(s.s, t, 853, 425, 943, 360, color=GRN_HI, width=2.75)
label(s.s, 943, 430, 274, 40, "token over the private network", size=12, color=GRN_HI)

d.save(OUT)
print(OUT)
