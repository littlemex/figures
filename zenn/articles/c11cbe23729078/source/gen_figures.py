"""gen_figures.py — 「SkyPilot v0.14.0 の解説」の図を、ネイティブ shape の pptx 5 枚で組む。

    /usr/bin/python3 gen_figures.py <out.pptx>

1. SkyPilot の全体像: タスクの YAML、API サーバー、その下の Kubernetes / Slurm / クラウドの VM
2. 動的なジョブグループ: グループの中のタスクが評価ジョブを足し、グループと一緒に止まる
3. 複数ユーザーの Slurm: 共通の SSH ユーザーで出していたものを、ユーザーごとの Unix アカウントで出す
4. Kubernetes での Neuron: Trainium2:16 の要求から、ポッドに足される 3 つ (+ EFA) とノードの広告
5. Trainium の 2 つの道: VM (以前から) と Kubernetes (v0.14.0)
図の文字は英語。根拠は skypilot v0.14.0 (commit 7b62fd8) のソースとドキュメント、Karpenter の instance-types の表。
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "skypilot-figures.pptx"

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
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width)


# ------------------------------------------------------------------ 1. overview
s = d.slide()
title(s.s, "One task file, any infrastructure you own",
      "Green: you write it.  Blue: SkyPilot.  Grey: your clusters and cloud accounts")
box(s.s, 43, 130, 330, 210, GRN_DK, stroke=GRN, radius=0.06)
label(s.s, 63, 140, 290, 34, "task.yaml", size=20, bold=True, color=GRN_HI)
label(s.s, 63, 180, 290, 150,
      "resources:\n  accelerators: H100:8\nsetup: pip install ...\nrun: python train.py",
      size=15, align="left")
arrow(s.s, 373, 235, 433, 235)
label(s.s, 373, 196, 60, 30, "sky", size=13, color=MUTED)
box(s.s, 433, 130, 380, 210, LINK_DK, stroke=LINK, radius=0.06)
label(s.s, 453, 140, 340, 34, "SkyPilot API server", size=20, bold=True, color=LINK)
for i, row in enumerate(["choose infra and region", "provision, setup, run",
                         "failover if provisioning fails", "jobs, logs, users"]):
    box(s.s, 463, 184 + i * 37, 320, 30, CHIP, stroke=LINK, body=row, size=14, radius=0.3)
for i, (name, sub) in enumerate([("Kubernetes", "pods"), ("Slurm", "sbatch / srun"),
                                 ("Cloud VMs", "in your AWS, GCP, ...")]):
    y = 130 + i * 74
    box(s.s, 873, y, 364, 62, GREY, stroke=EDGE, radius=0.12)
    label(s.s, 893, y + 4, 170, 54, name, size=18, bold=True, align="left")
    label(s.s, 1043, y + 4, 180, 54, sub, size=14, color=MUTED, align="right")
    arrow(s.s, 813, 235, 873, y + 31)
box(s.s, 43, 380, 1194, 66, CHIP, stroke=EDGE, radius=0.2)
label(s.s, 63, 380, 1154, 66,
      "sky launch   (interactive cluster)      sky jobs launch   (managed job)      sky serve   (endpoint)",
      size=16, color=WHITE)

# ------------------------------------------------------------------ 2. dynamic job group
s = d.slide()
title(s.s, "A task in a job group can add more jobs to it",
      "Green: tasks you define ([P] = primary).  Yellow: dynamic tasks added at run time")
box(s.s, 43, 120, 1194, 420, CHIP, stroke=EDGE, radius=0.03)
label(s.s, 63, 128, 600, 34, "job group  train-and-eval  (ID 122)", size=18, bold=True, align="left")
box(s.s, 83, 180, 330, 70, GRN_DK, stroke=GRN, body="0  trainer [P]\nH100:8", size=16)
box(s.s, 83, 300, 330, 60, GREY, stroke=EDGE, body="/checkpoints", size=16)
box(s.s, 83, 410, 330, 70, GRN_DK, stroke=GRN, body="1  eval-watcher [P]\nwaits for its evals", size=16)
arrow(s.s, 248, 250, 248, 300, color=MUTED)
label(s.s, 258, 256, 150, 32, "writes", size=13, color=MUTED, align="left")
arrow(s.s, 248, 410, 248, 360, color=MUTED)
label(s.s, 258, 366, 150, 32, "watches", size=13, color=MUTED, align="left")
for i, (name, st) in enumerate([("2  eval-step-1", "SUCCEEDED"), ("3  eval-step-2", "RUNNING"),
                                ("4  eval-step-3", "RUNNING")]):
    y = 180 + i * 110
    box(s.s, 650, y, 330, 70, YEL_DK, stroke=YEL, body=f"{name}\n{st}", size=16)
    arrow(s.s, 413, 445, 650, y + 35, color=YEL, width=2)
label(s.s, 450, 470, 200, 32, "sky jobs launch", size=13, color=YEL, align="left")
box(s.s, 995, 180, 8, 290, MUTED, radius=0.5)
label(s.s, 1015, 180, 215, 290,
      "listed under the group\n\ncancelled with the group\n\nown resources,\nown status",
      size=15, color=WHITE, align="left")
box(s.s, 43, 556, 1194, 44, None, stroke=EDGE, radius=0.3,
    body="Needs: remote API server (consolidation mode) + API access from the task", size=14,
    color=MUTED)

# ------------------------------------------------------------------ 3. multi-user slurm
s = d.slide()
title(s.s, "With submit_as_user, each Slurm job runs as its user",
      "Blue: SkyPilot.  Grey: Slurm cluster.  Green: per user")
for x, head in ((43, "submit_as_user: false (default)"), (665, "submit_as_user: true")):
    label(s.s, x, 112, 572, 34, head, size=22, bold=True)
    box(s.s, x, 152, 572, 360, CHIP, stroke=EDGE, radius=0.04)
for x in (43, 665):
    box(s.s, x + 30, 172, 240, 50, GRN_DK, stroke=GRN, body="alice@example.com", size=14)
    box(s.s, x + 302, 172, 240, 50, GRN_DK, stroke=GRN, body="bob@example.com", size=14)
    box(s.s, x + 30, 252, 512, 50, LINK_DK, stroke=LINK, body="SkyPilot API server", size=16)
    arrow(s.s, x + 150, 222, x + 150, 252)
    arrow(s.s, x + 422, 222, x + 422, 252)
    box(s.s, x + 30, 332, 512, 50, GREY, stroke=EDGE, body="SSH user in ~/.slurm/config", size=15)
    arrow(s.s, x + 286, 302, x + 286, 332)
box(s.s, 73, 412, 512, 56, GREY, stroke=EDGE, body="jobs run as the SSH user", size=16)
arrow(s.s, 329, 382, 329, 412)
label(s.s, 73, 472, 512, 36, "one Unix user for accounting and file owner", size=14, color=MUTED)
box(s.s, 695, 412, 240, 56, GRN_DK, stroke=GRN_HI, body="sudo -u alice\n/bin/bash", size=15)
box(s.s, 967, 412, 240, 56, GRN_DK, stroke=GRN_HI, body="sudo -u bob\n/bin/bash", size=15)
arrow(s.s, 815, 382, 815, 412, color=GRN_HI)
arrow(s.s, 1087, 382, 1087, 412, color=GRN_HI)
label(s.s, 695, 472, 512, 36, "accounting, fairshare, file owner per user", size=14, color=MUTED)
box(s.s, 43, 528, 1194, 52, CHIP, stroke=EDGE, radius=0.3,
    body="slurm.quota  ->  sbatch --qos / --account (Slurm account), per workspace", size=15,
    color=MUTED)

# ------------------------------------------------------------------ 4. neuron on k8s
s = d.slide()
title(s.s, "What SkyPilot adds to the pod for Trainium2:16",
      "Green: your request.  Blue: added by SkyPilot.  Yellow: conditional.  Grey: on the node")
box(s.s, 43, 130, 300, 120, GRN_DK, stroke=GRN, body="--gpus Trainium2:16\n--infra k8s\nimage_id: Neuron image",
    size=17)
label(s.s, 43, 256, 300, 30, "16 devices", size=14, color=MUTED)
arrow(s.s, 343, 190, 400, 190)
box(s.s, 400, 120, 470, 440, CHIP, stroke=LINK, radius=0.04)
label(s.s, 420, 128, 430, 34, "pod spec", size=18, bold=True, color=LINK, align="left")
rows = [("1  resource", "aws.amazon.com/neuron: 16", False),
        ("2  nodeAffinity (Karpenter label)", "karpenter.k8s.aws/\ninstance-accelerator-name: trainium2", False),
        ("3  toleration", "aws.amazon.com/neuron\nExists, NoSchedule", False),
        ("+  only with network_tier: best", "vpc.amazonaws.com/efa: 16\n(if the node has EFA)", True)]
for i, (k, v, cond) in enumerate(rows):
    y = 172 + i * 96
    box(s.s, 420, y, 430, 84, YEL_DK if cond else LINK_DK, stroke=YEL if cond else LINK,
        radius=0.12)
    label(s.s, 436, y + 4, 400, 26, k, size=14, color=YEL if cond else LINK, bold=True,
          align="left")
    label(s.s, 436, y + 30, 400, 50, v, size=14, align="left")
arrow(s.s, 870, 340, 930, 340)
label(s.s, 868, 348, 64, 30, "placed", size=12, color=MUTED)
box(s.s, 930, 120, 307, 440, GREY, stroke=EDGE, radius=0.04)
label(s.s, 950, 128, 270, 34, "trn2.48xlarge node", size=18, bold=True, align="left")
node_rows = ["label (by Karpenter)\nkarpenter.k8s.aws/\ninstance-accelerator-name\n= trainium2",
             "taint (if set)\naws.amazon.com/neuron\nNoSchedule",
             "allocatable\nneuron: 16\nneuroncore: 128\nefa: 16"]
for i, v in enumerate(node_rows):
    box(s.s, 950, 172 + i * 128, 267, 112, CHIP, stroke=EDGE, body=v, size=13, radius=0.08)
label(s.s, 43, 575, 1194, 30, "Without Karpenter: label the node skypilot.co/accelerator=trainium2",
      size=14, color=MUTED, align="left")

# ------------------------------------------------------------------ 5. VM vs k8s
s = d.slide()
title(s.s, "Two paths to Trainium in SkyPilot",
      "Blue: SkyPilot does it.  Green: you choose it.  Grey: you set up beforehand")
for x, head, sub in ((43, "Cloud VM on AWS", "available before v0.14.0"),
                     (665, "Kubernetes (EKS)", "new in v0.14.0")):
    label(s.s, x, 112, 572, 34, head, size=22, bold=True)
    label(s.s, x, 144, 572, 24, sub, size=14, color=MUTED)
    box(s.s, x, 178, 572, 360, CHIP, stroke=EDGE, radius=0.04)
box(s.s, 73, 200, 512, 56, GREY, stroke=EDGE, body="AWS account and quota", size=16)
box(s.s, 73, 276, 512, 56, LINK_DK, stroke=LINK, body="pick a trn instance and region", size=16)
box(s.s, 73, 352, 512, 56, LINK_DK, stroke=LINK, body="boot the Neuron image", size=16)
box(s.s, 73, 428, 512, 56, LINK_DK, stroke=LINK, body="run setup and run", size=16)
box(s.s, 695, 200, 512, 56, GREY, stroke=EDGE,
    body="EKS + Neuron device plugin + accelerator label", size=15)
box(s.s, 695, 276, 512, 56, LINK_DK, stroke=LINK, body="request neuron, select node, tolerate",
    size=15)
box(s.s, 695, 352, 512, 56, GRN_DK, stroke=GRN, body="image_id: a Neuron container image",
    size=15)
box(s.s, 695, 428, 512, 56, LINK_DK, stroke=LINK, body="run setup and run", size=16)

d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(os.path.abspath(OUT))
