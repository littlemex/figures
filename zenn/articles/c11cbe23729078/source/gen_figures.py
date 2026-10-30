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
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
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
title(s.s, "Adding an eval job per checkpoint while training runs",
      "Green: tasks in the group YAML.  Yellow: eval jobs.  Numbers: order of events")
for x, head in ((43, "v0.13.0: separate jobs"), (665, "v0.14.0: dynamic tasks")):
    label(s.s, x, 112, 572, 34, head, size=22, bold=True)
# --- as-is
box(s.s, 43, 156, 572, 196, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 59, 160, 400, 28, "job group", size=14, color=MUTED, align="left")
box(s.s, 63, 192, 250, 56, GRN_DK, stroke=GRN, body="trainer", size=15)
box(s.s, 343, 192, 250, 56, GRN_DK, stroke=GRN, body="eval-watcher", size=15)
box(s.s, 63, 272, 530, 56, GREY, stroke=EDGE, body="/checkpoints", size=15)
arrow(s.s, 188, 248, 188, 272, color=MUTED)
arrow(s.s, 468, 272, 468, 248, color=MUTED)
box(s.s, 63, 380, 250, 56, YEL_DK, stroke=YEL, body="eval job A", size=15)
box(s.s, 343, 380, 250, 56, YEL_DK, stroke=YEL, body="eval job B", size=15)
label(s.s, 43, 446, 572, 30, "separate top-level jobs", size=14, color=MUTED)
box(s.s, 43, 560, 572, 44, CHIP, stroke=EDGE, radius=0.3,
    body="cancel the group -> eval jobs keep running", size=15)
# --- to-be
box(s.s, 665, 156, 572, 306, CHIP, stroke=LINK, radius=0.03)
label(s.s, 681, 160, 400, 28, "job group", size=14, color=LINK, align="left")
box(s.s, 685, 196, 250, 52, GRN_DK, stroke=GRN, body="trainer", size=15)
box(s.s, 685, 296, 250, 52, GREY, stroke=EDGE, body="/checkpoints", size=15)
box(s.s, 685, 396, 250, 52, GRN_DK, stroke=GRN, body="eval-watcher", size=15)
box(s.s, 965, 196, 252, 52, YEL_DK, stroke=YEL, body="eval-step-1", size=15)
box(s.s, 965, 296, 252, 52, YEL_DK, stroke=YEL, body="eval-step-2", size=15)
box(s.s, 965, 396, 252, 52, YEL_DK, stroke=YEL, dash=MSO_LINE_DASH_STYLE.DASH, body="...", size=15)
arrow(s.s, 810, 248, 810, 296, color=WHITE)
label(s.s, 820, 258, 110, 28, "1 write", size=13, color=WHITE, align="left")
arrow(s.s, 810, 348, 810, 396, color=WHITE)
label(s.s, 820, 358, 110, 28, "2 find", size=13, color=WHITE, align="left")
box(s.s, 665, 504, 572, 46, LINK_DK, stroke=LINK, body="SkyPilot API server", size=15)
arrow(s.s, 810, 448, 810, 504, color=YEL, width=2.5)
label(s.s, 820, 470, 170, 28, "3 sky jobs launch", size=13, color=YEL, align="left")
arrow(s.s, 1091, 504, 1091, 448, color=YEL, width=2.5)
label(s.s, 1101, 470, 130, 28, "4 join group", size=13, color=YEL, align="left")
label(s.s, 965, 160, 252, 30, "5 own resources, own status", size=13, color=YEL)
box(s.s, 665, 560, 572, 44, CHIP, stroke=EDGE, radius=0.3,
    body="6  cancel the group -> eval jobs stop too", size=15)

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
title(s.s, "What SkyPilot writes into the pod for Trainium2:16",
      "Green: your request.  Blue: written by SkyPilot.  Grey: prepared on the cluster")
box(s.s, 43, 150, 300, 120, GRN_DK, stroke=GRN, body="Trainium2:16\nimage_id: Neuron image", size=17)
arrow(s.s, 343, 210, 400, 210)
box(s.s, 400, 120, 470, 400, CHIP, stroke=LINK, radius=0.04)
label(s.s, 420, 128, 430, 34, "pod spec", size=18, bold=True, color=LINK, align="left")
rows = [("1  how many chips", "use 16 Trainium chips"),
        ("2  where to run", "only on Trainium nodes"),
        ("3  permission", "allowed onto Neuron-only nodes")]
for i, (k, v) in enumerate(rows):
    y = 176 + i * 110
    box(s.s, 420, y, 430, 92, LINK_DK, stroke=LINK, radius=0.12)
    label(s.s, 436, y + 8, 400, 30, k, size=15, color=LINK, bold=True, align="left")
    label(s.s, 436, y + 44, 400, 36, v, size=16, align="left")
arrow(s.s, 870, 320, 930, 320)
label(s.s, 868, 328, 64, 30, "placed", size=12, color=MUTED)
box(s.s, 930, 120, 307, 400, GREY, stroke=EDGE, radius=0.04)
label(s.s, 950, 128, 270, 34, "Trainium node", size=18, bold=True, align="left")
node_rows = ["Neuron AMI", "Neuron device plugin\n(chips as a resource)", "Neuron-only mark"]
for i, v in enumerate(node_rows):
    box(s.s, 950, 176 + i * 110, 267, 92, CHIP, stroke=EDGE, body=v, size=15, radius=0.08)

# ------------------------------------------------------------------ 5. EFA before / after
s = d.slide()
title(s.s, "How v0.14.0 keeps multi-node jobs on EFA",
      "Blue: SkyPilot.  Grey: nodes.  Yellow: falls back to TCP")
for x, head in ((43, "v0.13.0"), (665, "v0.14.0")):
    label(s.s, x, 112, 572, 34, head, size=22, bold=True)
for y, row in ((156, "no accelerator node yet"), (376, "multi-node job")):
    label(s.s, 43, y, 300, 26, row, size=14, color=MUTED, align="left")
    label(s.s, 665, y, 300, 26, row, size=14, color=MUTED, align="left")
# row 1 as-is
box(s.s, 43, 186, 270, 60, LINK_DK, stroke=LINK, body="SkyPilot reads\nrunning nodes", size=14)
arrow(s.s, 313, 216, 345, 216)
box(s.s, 345, 186, 270, 60, YEL_DK, stroke=YEL, body="pod without EFA\n-> TCP", size=14)
label(s.s, 43, 252, 572, 30, "no node to read the EFA count from", size=13, color=MUTED)
# row 1 to-be
box(s.s, 665, 186, 270, 60, LINK_DK, stroke=LINK, body="SkyPilot reads\nthe instance catalog", size=14)
arrow(s.s, 935, 216, 967, 216)
box(s.s, 967, 186, 270, 60, LINK_DK, stroke=LINK, body="pod requests EFA", size=14)
label(s.s, 665, 252, 572, 30, "the autoscaler adds a node with EFA", size=13, color=MUTED)
# row 2 as-is
for i, az in enumerate(("AZ a", "AZ b")):
    x = 43 + i * 290
    box(s.s, x, 406, 282, 150, CHIP, stroke=EDGE, radius=0.05)
    label(s.s, x + 12, 410, 200, 26, az, size=13, color=MUTED, align="left")
    box(s.s, x + 40, 444, 200, 50, GREY, stroke=EDGE, body=f"pod {i}", size=14)
box(s.s, 43, 566, 572, 40, YEL_DK, stroke=YEL, radius=0.3, body="EFA cannot connect -> TCP or fails", size=14)
# row 2 to-be
box(s.s, 665, 406, 572, 150, CHIP, stroke=EDGE, radius=0.05)
label(s.s, 677, 410, 200, 26, "AZ a", size=13, color=MUTED, align="left")
box(s.s, 705, 444, 200, 50, GREY, stroke=EDGE, body="pod 0", size=14)
box(s.s, 997, 444, 200, 50, GREY, stroke=EDGE, body="pod 1", size=14)
arrow(s.s, 997, 469, 905, 469, color=LINK, width=2)
label(s.s, 905, 500, 92, 40, "same AZ", size=12, color=LINK)
box(s.s, 665, 566, 572, 40, LINK_DK, stroke=LINK, radius=0.3, body="pods follow pod 0 into one AZ", size=14)

d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(os.path.abspath(OUT))
