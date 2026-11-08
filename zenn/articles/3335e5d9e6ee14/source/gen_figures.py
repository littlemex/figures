"""Figures for part 1 (GDS and KvikIO): native pptx shapes in the zenn-doc template look.

    /usr/bin/python3 gen_part1.py <out.pptx>

Green = what the application writes. Blue = libraries and the kernel (KvikIO, cuFile, nvidia-fs).
Yellow = the host bounce path and cautions. Grey = hardware. Each role also carries a pattern (ZN-29).
Sources: NVIDIA blog (2026-10-22), GDS Overview Guide, KvikIO docs at 6ddda9a, kvikio#941, FSx for Lustre guide.
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
TPL_DIR = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, TPL_DIR)
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "part1.pptx"

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
ROLE_PATTERN = {GRN_DK: "diagonal", LINK_DK: "cross", YEL_DK: "grid"}

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align, anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=16, color=WHITE, radius=0.1, dash=None, sw=1.5):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def arrow(s, x1, y1, x2, y2, color=WHITE, width=2.0, dash=False):
    a = sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width)
    if dash:
        a.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return a


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


LEGEND = "Green: you.  Blue: library / kernel.  Yellow: relay or caution.  Grey: hardware.  Thick white arrow: direct DMA"

# 1 ------------------------------------------------------------------ two paths
s = d.slide().s
title(s, "Two ways from NVMe to GPU memory", LEGEND)
for x, head in ((43, "Without GDS: relay through CPU memory"), (665, "With GDS: NVMe writes into the GPU")):
    label(s, x, 112, 572, 34, head, size=20, bold=True)
    box(s, x, 152, 572, 440, CHIP, stroke=EDGE, radius=0.04)
# left
box(s, 83, 190, 200, 70, GREY, stroke=EDGE, body="NVMe", size=20)
box(s, 343, 300, 260, 80, YEL_DK, stroke=YEL, body="CPU memory\n(relay)", size=18)
box(s, 83, 470, 200, 80, GREY, stroke=EDGE, body="GPU memory", size=20)
arrow(s, 283, 225, 400, 300, width=3)
label(s, 330, 220, 260, 30, "1  DMA to host", size=16, color=YEL, align="left")
arrow(s, 400, 380, 283, 500, width=3)
label(s, 360, 430, 240, 30, "2  copy to GPU", size=16, color=YEL, align="left")
label(s, 83, 556, 520, 30, "two transfers, the CPU memory is in the middle", size=15, color=MUTED)
# right
box(s, 705, 190, 200, 70, GREY, stroke=EDGE, body="NVMe", size=20)
box(s, 705, 470, 200, 80, GREY, stroke=EDGE, body="GPU memory", size=20)
arrow(s, 805, 260, 805, 470, color=WHITE, width=7)
label(s, 830, 340, 380, 40, "1  direct DMA into the GPU", size=18, color=WHITE, align="left")
box(s, 965, 190, 230, 80, CHIP, stroke=EDGE, body="CPU memory\nnot used", size=16, color=MUTED, dash=MSO_LINE_DASH_STYLE.DASH)
label(s, 705, 556, 520, 30, "one transfer, the CPU only issues the request", size=15, color=MUTED)

# 2 ------------------------------------------------------------------ parts
s = d.slide().s
title(s, "Five parts hand the read down", LEGEND)
rows = [
    (GRN_DK, GRN, "Your application", "you", "what to read, where"),
    (LINK_DK, LINK, "KvikIO", "library", "split into tasks"),
    (LINK_DK, LINK, "cuFile (libcufile)", "library", "register GPU memory"),
    (LINK_DK, LINK, "nvidia-fs.ko  or  PCI P2PDMA", "kernel", "target = GPU memory"),
    (LINK_DK, LINK, "ext4  +  NVMe driver", "kernel", "O_DIRECT read"),
]
y = 120
for fill, stroke, name, owner, what in rows:
    box(s, 43, y, 440, 70, fill, stroke=stroke, body=name, size=18)
    label(s, 493, y, 110, 70, owner, size=15, color=MUTED, align="left")
    label(s, 610, y, 360, 70, what, size=17, align="left")
    if y > 120:
        arrow(s, 263, y - 14, 263, y, width=2)
    y += 84
box(s, 1060, 140, 177, 120, GREY, stroke=EDGE, body="GPU\nmemory", size=20)
label(s, 1060, 262, 177, 26, "hardware", size=15, color=MUTED)
box(s, 1060, 446, 177, 90, GREY, stroke=EDGE, body="NVMe SSD", size=20)
label(s, 1060, 538, 177, 26, "hardware", size=15, color=MUTED)
arrow(s, 975, 491, 1060, 491, width=2)
arrow(s, 1148, 446, 1148, 290, color=WHITE, width=7)
label(s, 1000, 330, 140, 60, "direct\nDMA", size=17, color=WHITE, bold=True)

# 3a ----------------------------------------------------------------- nvidia-fs flow
s = d.slide().s
title(s, "nvidia-fs path: the NVMe driver swaps the DMA target", LEGEND)
steps = [(LINK_DK, LINK, "1  cuFile -> nvidia-fs", "pin GPU pages (nvidia_p2p_get_pages_persistent)"),
         (LINK_DK, LINK, "2  nvidia-fs -> filesystem", "O_DIRECT read aimed at a shadow buffer (no data lands there)"),
         (LINK_DK, LINK, "3  GDS-capable NVMe driver", "calls nvidia-fs: shadow address -> GPU address"),
         (GREY, EDGE, "4  NVMe SSD", "DMA into GPU memory")]
y = 120
for f, st, name, what in steps:
    box(s, 43, y, 400, 80, f, stroke=st, body=name, size=18)
    label(s, 470, y, 560, 80, what, size=17, align="left")
    if y > 120:
        arrow(s, 243, y - 18, 243, y, width=2)
    y += 98
box(s, 1060, 120, 177, 120, GREY, stroke=EDGE, body="GPU\nmemory", size=20)
arrow(s, 1148, 414, 1148, 240, color=WHITE, width=7)
box(s, 43, 520, 1194, 64, YEL_DK, stroke=YEL, body="needs an NVMe driver with nvidia-fs callbacks (not in the stock Linux driver)", size=17)

# 3b ----------------------------------------------------------------- P2PDMA flow
s = d.slide().s
title(s, "P2PDMA path: the kernel checks the PCIe topology", LEGEND)
steps = [(LINK_DK, LINK, "1  NVIDIA driver", "map all GPU memory into BAR1, register with P2PDMA"),
         (LINK_DK, LINK, "2  O_DIRECT read", "GPU pages used as an ordinary target"),
         (YEL_DK, YEL, "3  kernel P2PDMA check", "upstream bridge w/o ACS redirect, allowed host bridge, or AMD Zen or later? (v6.8)"),
         (GREY, EDGE, "4  NVMe SSD", "DMA into GPU memory")]
y = 120
for f, st, name, what in steps:
    box(s, 43, y, 400, 80, f, stroke=st, body=name, size=18)
    label(s, 470, y, 560, 80, what, size=17, align="left")
    if y > 120:
        arrow(s, 243, y - 18, 243, y, width=2)
    y += 98
box(s, 1060, 120, 177, 120, GREY, stroke=EDGE, body="GPU\nmemory", size=20)
arrow(s, 1148, 414, 1148, 240, color=WHITE, width=7)
box(s, 43, 520, 580, 64, CHIP, stroke=EDGE, body="no nvidia-fs, stock NVMe driver", size=17)
box(s, 657, 520, 580, 64, YEL_DK, stroke=YEL, body="needs BAR1 fixed (RMForceStaticBar1=1)", size=17)

# 4 ------------------------------------------------------------------ two stage
s = d.slide().s
title(s, "Two decisions pick the path", LEGEND)
box(s, 43, 150, 260, 70, GRN_DK, stroke=GRN, body="read / pread", size=20)
box(s, 360, 140, 360, 90, LINK_DK, stroke=LINK, body="1  KvikIO: call cuFile?", size=19)
box(s, 820, 140, 417, 90, YEL_DK, stroke=YEL, body="KvikIO reads itself through CPU memory\n(compat ON, or AUTO fallback)", size=15)
box(s, 820, 250, 417, 46, CHIP, stroke=EDGE, body="compat OFF: error", size=15)
arrow(s, 303, 185, 360, 185, width=2)
arrow(s, 720, 185, 820, 185, color=YEL, width=2, dash=True)
label(s, 728, 150, 90, 30, "no", size=15, color=YEL)
arrow(s, 720, 215, 820, 268, width=2, dash=True)
box(s, 360, 340, 360, 90, LINK_DK, stroke=LINK, body="2  cuFile: direct DMA?", size=19)
arrow(s, 540, 230, 540, 340, width=2)
label(s, 552, 268, 80, 34, "yes", size=15, color=WHITE, align="left")
box(s, 820, 340, 417, 90, YEL_DK, stroke=YEL, body="cuFile compat mode\nthrough CPU memory (if allowed)", size=15)
box(s, 820, 450, 417, 46, CHIP, stroke=EDGE, body="not allowed: error", size=15)
arrow(s, 720, 385, 820, 385, color=YEL, width=2, dash=True)
label(s, 728, 350, 90, 30, "no", size=15, color=YEL)
arrow(s, 720, 415, 820, 468, width=2, dash=True)
box(s, 360, 540, 360, 70, GREY, stroke=EDGE, body="NVMe DMA into GPU memory", size=17)
box(s, 43, 540, 280, 70, CHIP, stroke=EDGE, body="refused by device\nor kernel: error", size=15)
arrow(s, 360, 575, 323, 575, width=2, dash=True)
arrow(s, 540, 430, 540, 540, color=WHITE, width=7)
label(s, 560, 470, 80, 34, "yes", size=15, color=WHITE, align="left")
label(s, 820, 530, 417, 80, "if the read succeeds,\nthe same bytes either way", size=15, color=MUTED)

# 5 ------------------------------------------------------------------ verify
s = d.slide().s
title(s, "Count, do not time", "A relayed read still succeeds, so throughput alone cannot tell the paths apart")
cols = [("1  before: gdscheck -p", "NVMe : Supported\nNVMe P2PDMA : Supported", "is the environment capable"),
        ("2  read, compat off, stats 3", "KVIKIO_COMPAT_MODE=off\nCUFILE_STATS_LEVEL=3", "KvikIO cannot relay silently"),
        ("3  counters while alive", "gds_stats: nvfs / posix\nnvidia-fs stats: Reads", "example: 1 GiB in 4 MiB tasks")]
for i, (head, body, foot) in enumerate(cols):
    x = 43 + i * 405
    box(s, x, 130, 384, 76, LINK_DK, stroke=LINK, body=head, size=19)
    box(s, x, 226, 384, 150, CHIP, stroke=EDGE, radius=0.04)
    label(s, x + 14, 236, 356, 130, body, size=16, align="left")
    label(s, x, 386, 384, 30, foot, size=15, color=MUTED)
box(s, 43, 450, 1194, 70, YEL_DK, stroke=YEL, body="if refused, cuFile log and dmesg name the layer that said no", size=18)

# 6 ------------------------------------------------------------------ where
s = d.slide().s
title(s, "GDS on AWS: documented and reported", "FSx for Lustre guide (documented) and kvikio#941 (reported)")
box(s, 43, 130, 572, 450, CHIP, stroke=EDGE, radius=0.04)
label(s, 43, 140, 572, 36, "EC2 instance-store NVMe", size=20, bold=True)
box(s, 103, 200, 200, 70, GREY, stroke=EDGE, body="NVMe", size=19)
box(s, 103, 430, 200, 80, GREY, stroke=EDGE, body="GPU", size=19)
box(s, 343, 300, 240, 80, YEL_DK, stroke=YEL, body="CPU memory\n(relay)", size=17)
arrow(s, 303, 235, 400, 300, color=YEL, width=2, dash=True)
arrow(s, 400, 380, 303, 470, color=YEL, width=2, dash=True)
label(s, 63, 520, 532, 40, "reported unsupported (kvikio#941)", size=17, color=YEL)
box(s, 665, 130, 572, 450, CHIP, stroke=EDGE, radius=0.04)
label(s, 665, 140, 572, 36, "FSx for Lustre (EFA, Persistent 2)", size=20, bold=True)
box(s, 725, 200, 260, 70, GREY, stroke=EDGE, body="Lustre servers", size=19)
box(s, 725, 430, 260, 80, GREY, stroke=EDGE, body="GPU on P5 / P5e / P5en\nP6-B200 / P6-B300", size=15)
arrow(s, 855, 270, 855, 430, color=WHITE, width=7)
label(s, 870, 330, 340, 40, "direct path Lustre to GPU", size=17, color=WHITE, align="left")
label(s, 685, 520, 532, 40, "documented (p4d is not in the list)", size=17, color=WHITE)

# 8 ------------------------------------------------------------------ p4d stops
s = d.slide().s
title(s, "p4d.24xlarge instance store: where each path stops", "Both reached Supported in gdscheck after the prerequisites; both were refused later")
for x, head in ((43, "nvidia-fs path"), (665, "P2PDMA path")):
    label(s, x, 112, 572, 34, head, size=20, bold=True)
    box(s, x, 152, 572, 440, CHIP, stroke=EDGE, radius=0.04)
rows_l = [("custom kernel, NVMe as modules", "ok"), ("mlnx-nvme + nvidia-fs loaded", "ok"), ("GPU pages pinned, DMA target = GPU", "ok"), ("NVMe completion: sc 0x2 (invalid field); layer unknown", "stop")]
rows_r = [("BAR1 fixed (RMForceStaticBar1=1)", "ok"), ("gdscheck: NVMe P2PDMA Supported", "ok"), ("kernel: no shared bridge, host bridge not whitelisted", "stop")]
for x, rows in ((63, rows_l), (685, rows_r)):
    y = 180
    for text, st in rows:
        stop = st == "stop"
        box(s, x, y, 532, 80, YEL_DK if stop else LINK_DK, stroke=YEL if stop else LINK, body=text, size=16)
        if y > 180:
            arrow(s, x + 266, y - 20, x + 266, y, width=2)
        y += 100

d.save(OUT)
print("saved", OUT)
