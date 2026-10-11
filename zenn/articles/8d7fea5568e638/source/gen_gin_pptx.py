"""gen_gin_pptx.py: NCCL roadmap article GIN static figures."""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "looped-figures.pptx"

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
DASH = MSO_LINE_DASH_STYLE.DASH

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


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2, dashed=False):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)




PNK = RGBColor(255, 120, 160)
# ------------------------------------------------------------------ 1. three layers
s = d.slide().s
title(s, "GIN: kernel, backend, network", "Green: GPU code.  Blue: CPU on the path.  Yellow: network")
box(s, 43, 120, 1194, 110, GRN_DK, stroke=GRN, radius=0.04)
label(s, 63, 128, 400, 30, "CUDA kernel", size=19, bold=True, align="left")
label(s, 63, 158, 1150, 34, "Device GIN API (ncclGin): put / get / signal / flush / wait", size=16, color=WHITE, align="left")
box(s, 43, 290, 1194, 200, CHIP, stroke=EDGE, radius=0.04)
label(s, 63, 296, 400, 30, "GIN backend", size=19, bold=True, align="left")
box(s, 73, 330, 360, 130, GRN_DK, stroke=GRN, body="GDAKI\nWQE + doorbell\nIB / RoCE, ConnectX-6 Dx+", size=15)
box(s, 459, 330, 360, 130, LINK_DK, stroke=LINK, body="Proxy\n64-byte descriptor, CPU proxy\nany RDMA NIC", size=15)
box(s, 845, 330, 362, 130, GRN_DK, stroke=GRN, body="EFA GDA\nWQE + doorbell\nEFA, NCCL 2.31.2+", size=15)
for cx, col in ((253, WHITE), (639, LINK), (1026, WHITE)):
    arrow(s, cx, 230, cx, 330, color=col)
for cx, col in ((253, WHITE), (639, LINK), (1026, WHITE)):
    arrow(s, cx, 460, cx, 584, color=col)
box(s, 43, 584, 1194, 70, YEL_DK, stroke=YEL, body="Network: InfiniBand / RoCE / EFA", size=18, radius=0.08)

# ------------------------------------------------------------------ 2. small-message latency
s = d.slide().s
title(s, "Round-trip latency for 4-128 byte messages", "arXiv:2511.15076: put with signal ping-pong, two H100 GPUs, NCCL 2.28.  Lower is faster")
vals = [("NCCL GIN GDAKI", 16.7, GRN_DK, GRN), ("NCCL GIN Proxy", 18.0, LINK_DK, LINK),
        ("NVSHMEM IBRC", 16.0, GREY, EDGE), ("NVSHMEM IBGDA", 24.3, GREY, EDGE)]
for i, (name, v, fill, st) in enumerate(vals):
    y = 150 + i * 105
    label(s, 43, y + 18, 300, 40, name, size=18, bold=True, align="left")
    w = 820 * v / 25.0
    box(s, 343, y, w, 70, fill, stroke=st, radius=0.06)
    label(s, 343 + w + 12, y + 18, 160, 40, f"{v} us", size=18, bold=True, align="left")
label(s, 43, 590, 1190, 30, "Green: GIN GDAKI (GPU path).  Blue: GIN Proxy (CPU on the path).  Grey: NVSHMEM", size=14, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. GIN on EFA
s = d.slide().s
title(s, "GIN on AWS EFA: two modes",
      "Green: GPU.  Blue: CPU on the path.  Yellow: EFA.  Grey: requirements")
for x, head_, sub in [(43, "Host-proxy mode", "CPU proxy thread issues ops"),
                      (653, "Kernel backend (EFA GDA)", "GPU builds the WQE, rings the doorbell")]:
    label(s, x, 112, 584, 30, head_, size=18, bold=True)
    label(s, x, 142, 584, 24, sub, size=14, color=MUTED)
    box(s, x, 176, 584, 300, CHIP, stroke=EDGE, radius=0.04)
box(s, 83, 196, 504, 56, GRN_DK, stroke=GRN, body="GPU kernel (ncclGin)", size=15)
arrow(s, 335, 252, 335, 282)
box(s, 83, 282, 504, 56, LINK_DK, stroke=LINK, body="CPU proxy -> libfabric (efa)", size=15)
arrow(s, 335, 338, 335, 368)
box(s, 83, 368, 504, 56, YEL_DK, stroke=YEL, body="EFA (SRD)", size=15)
box(s, 693, 196, 504, 56, GRN_DK, stroke=GRN, body="GPU kernel (ncclGin)", size=15)
arrow(s, 945, 252, 945, 368)
label(s, 955, 296, 260, 30, "auto-selected", size=13, color=MUTED, align="left")
box(s, 693, 368, 504, 56, YEL_DK, stroke=YEL, body="EFA (SRD)", size=15)
label(s, 43, 490, 584, 30, "NCCL 2.31.2+ · GDRCopy 2.5+", size=14, color=MUTED)
label(s, 653, 490, 584, 30, "NCCL 2.31.2+ · GDRCopy 2.5+", size=14, color=MUTED)
label(s, 653, 520, 584, 30, "+ Libfabric 2.6.0+ · supported EFA instance", size=14, color=MUTED)
label(s, 43, 560, 1190, 30, "source: aws-ofi-nccl v1.21.0, NCCL 2.31.2 release notes", size=13, color=MUTED, align="left")
d.save(OUT)
# ZN-24: テンプレートのロゴ、著作権表示、ヘッダー、フッターを必ず消してから使う
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
