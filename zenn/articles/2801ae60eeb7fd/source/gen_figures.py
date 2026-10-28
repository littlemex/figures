"""gen_figures.py -- NCCL Roadmap Nov 2026 - Jan 2027 の解説記事の図を pptx 4 枚で組む。

    /usr/bin/python3 gen_figures.py <out.pptx>

1. genk-flow: GENK の層。集団通信 -> コストモデル -> GENK -> Flow -> LSA / GIN の接続
2. efa-signals: EFA の 2 つの GIN の経路と、strong signal を要る使い手の対応
3. barrier-slots: GIN の barrier 1 つが使う signal の数。既定の per-peer と EFA GDA の 2 本
4. enqueue-layers: 新しい enqueue の 3 層
9. cft-endpoint: LSA の番地への書き込みと CFT の宛先の番号への put、CFT team の入れ子
見た目は review-html の zenn-doc テンプレート nxd_interfaces_pptx.py と同じ。
根拠は記事本文と NVIDIA/nccl staging af13236、aws-ofi-nccl d8f9640。
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.dml import MSO_PATTERN, MSO_LINE_DASH_STYLE  # noqa: E402

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
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

PATTERNS = {
    str(GRN_DK): (MSO_PATTERN.WIDE_UPWARD_DIAGONAL, RGBColor(28, 88, 46)),
    str(YEL_DK): (MSO_PATTERN.LIGHT_VERTICAL, RGBColor(102, 85, 20)),
    str(GREY): (MSO_PATTERN.LIGHT_HORIZONTAL, RGBColor(72, 77, 86)),
}
SWATCH = {"Green": (GRN_DK, GRN), "Yellow": (YEL_DK, YEL), "Grey": (GREY, EDGE), "Blue": (LINK_DK, LINK)}

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    # Colour-blind readers: each role colour also carries a faint texture (blue stays plain).
    if fill is not None and str(fill) in PATTERNS:
        kind, fore = PATTERNS[str(fill)]
        sp.fill.patterned()
        sp.fill.pattern = kind
        sp.fill.fore_color.rgb = fore
        sp.fill.back_color.rgb = fill
        if fill == YEL_DK and stroke is not None:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    # Legend as swatches: each swatch carries the same texture as the boxes, so the key works without colour.
    x = 43
    for part in [p.strip().rstrip(".") for p in sub.split(".  ") if p.strip()]:
        word, _, text = part.partition(":")
        key = word.split(" ")[0]
        fill, stroke = SWATCH.get(key, (None, None))
        if fill is not None:
            box(s, x, 75, 40, 22, fill, stroke=stroke, radius=0.2)
            x += 48
            text = (word[len(key):].strip() + " " + text.strip()).strip()
        else:
            text = part
        w = int(len(text) * 9.5) + 24
        label(s, x, 72, w, 28, text, size=14, color=MUTED, align="left")
        x += w + 18


def down(s, x, y1, y2, color=WHITE):
    sh.arrow(s, t, x, y1, x, y2, color=color, width=2)


# ------------------------------------------------------------------ 1. GENK on Flow
s = d.slide()
title(s.s, "GENK: NCCL collectives built on the Device API",
      "Blue: inside NCCL.  Green (API tag): Device API you can call.  Grey: link.  Yellow: condition")
box(s.s, 43, 118, 1194, 52, LINK_DK, stroke=LINK,
    body="AllReduce / AllGather / ReduceScatter / Broadcast / Reduce", size=18)
down(s.s, 640, 170, 194)
box(s.s, 43, 194, 1194, 46, LINK_DK, stroke=LINK, body="cost model picks one kernel family", size=16)
for x, w, body in ((43, 380, "legacy kernels"), (450, 380, "specialized symmetric kernels"),
                   (857, 380, "GENK\nRing (5 ops) · Tree (AllReduce)")):
    down(s.s, x + w // 2, 240, 264)
    box(s.s, x, 264, w, 60, LINK_DK, stroke=LINK, body=body, size=16)
down(s.s, 1047, 324, 346)
box(s.s, 857, 346, 380, 64, GRN_DK, stroke=GRN_HI, sw=2.5, body="[API] Flow processor\nreceive / reduce / copy / send", size=15)
label(s.s, 450, 346, 390, 64, "also usable from\nyour own kernels", size=15, color=GRN_HI, align="right")
for x, body in ((857, "[API] LSA connection"), (1052, "[API] GIN connection")):
    box(s.s, x, 444, 185, 56, GRN_DK, stroke=GRN_HI, sw=2.5, body=body, size=14)
sh.arrow(s.s, t, 1000, 410, 950, 444, color=WHITE, width=2)
sh.arrow(s.s, t, 1094, 410, 1144, 444, color=WHITE, width=2)
label(s.s, 450, 444, 390, 56, "chosen per peer at run time", size=15, color=MUTED, align="right")
box(s.s, 857, 548, 185, 60, GREY, stroke=EDGE, body="NVLink /\nCUDA P2P", size=15)
box(s.s, 1052, 548, 185, 60, GREY, stroke=EDGE, body="network\n(GENK: GIN Proxy)", size=15)
down(s.s, 950, 500, 548)
down(s.s, 1144, 500, 548)
box(s.s, 1150, 510, 87, 30, YEL_DK, stroke=YEL, body="strong", size=12, radius=0.3)
label(s.s, 450, 548, 390, 60, "runs over", size=15, color=MUTED, align="right")
box(s.s, 43, 630, 1194, 44, YEL_DK, stroke=YEL, radius=0.3,
    body="staging only · build with SYM_GENK=1 · then opt-in", size=15)

# ------------------------------------------------------------------ 2. EFA: which backend offers each signal type
s = d.slide()
title(s.s, "On EFA: which GIN backend offers each signal type",
      "Green: users of GIN.  Yellow: signal they need.  Blue: backends on EFA")
users = [("GENK (Flow over GIN)", "strong"),
         ("DeepEP ordered\n(upstream hybrid)", "strong + VA"),
         ("DeepEP unordered\n(amazon-contributing fork)", "weak (counting)")]
y = 140
uy = []
for name, need in users:
    box(s.s, 43, y, 360, 72, GRN_DK, stroke=GRN, body=name, size=16)
    box(s.s, 433, y + 12, 250, 48, YEL_DK, stroke=YEL, body=need, size=15)
    sh.arrow(s.s, t, 403, y + 36, 433, y + 36, color=WHITE, width=2)
    uy.append(y + 36)
    y += 120
box(s.s, 800, 140, 437, 140, LINK_DK, stroke=LINK,
    body="NCCL GIN Proxy\nover aws-ofi-nccl RMA\nCPU thread posts\nstrong · weak · indexed · VA", size=15)
box(s.s, 800, 390, 437, 120, LINK_DK, stroke=LINK,
    body="EFA GDA (NCCL_GIN_TYPE=5)\nGPU kernel posts\nindexed · weak only", size=15)
sh.arrow(s.s, t, 683, uy[0], 800, 190, color=WHITE, width=2)
label(s.s, 686, 196, 112, 24, "ginType = Proxy", size=11, color=MUTED)
sh.arrow(s.s, t, 683, uy[1], 800, 230, color=WHITE, width=2)
sh.arrow(s.s, t, 683, uy[2], 800, 262, color=WHITE, width=2)
sh.arrow(s.s, t, 683, uy[2], 800, 450, color=WHITE, width=2)
label(s.s, 800, 520, 437, 30, "≤ 512 signals + counters / device", size=14, color=MUTED)
box(s.s, 43, 600, 1194, 46, None, stroke=EDGE, radius=0.3, color=MUTED,
    body="arrow = backend offers this signal (per code and docs)", size=14)

# ------------------------------------------------------------------ 3. barrier slots
s = d.slide()
title(s.s, "Signals one GIN barrier uses (example: 8 ranks)",
      "Blue: inside NCCL.  Yellow: EFA limit and status")
box(s.s, 43, 120, 572, 380, CHIP, stroke=EDGE, radius=0.04)
box(s.s, 665, 120, 572, 380, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 43, 130, 572, 36, "Default: 8 slots, one per sender", size=20, bold=True)
label(s.s, 665, 130, 572, 36, "Signal-efficient (staging)", size=20, bold=True)
for i in range(8):
    x = 73 + (i % 4) * 130
    yy = 200 + (i // 4) * 100
    box(s.s, x, yy, 110, 70, LINK_DK, stroke=LINK, body=f"rank {i}", size=16)
label(s.s, 43, 420, 572, 40, "slots = number of ranks", size=17, color=MUTED)
box(s.s, 735, 210, 190, 100, LINK_DK, stroke=LINK, body="slot 0", size=18)
box(s.s, 975, 210, 190, 100, LINK_DK, stroke=LINK, body="slot 1", size=18)
sh.arrow(s.s, t, 925, 245, 975, 245, color=WHITE, width=2)
sh.arrow(s.s, t, 975, 280, 925, 280, color=WHITE, width=2)
label(s.s, 665, 322, 572, 34, "phase bit alternates the slot", size=16, color=WHITE)
label(s.s, 665, 360, 572, 34, "slots = 2 for any team size", size=16, color=MUTED)
box(s.s, 705, 410, 492, 70, YEL_DK, stroke=YEL, radius=0.2,
    body="EFA GDA device code: uses this\nhost: per peer until the plugin asks (GIN API v15)", size=14)
box(s.s, 43, 530, 1194, 50, YEL_DK, stroke=YEL, radius=0.3,
    body="EFA GDA: ≤ 512 signals + counters / device", size=16)

# ------------------------------------------------------------------ 4. enqueue layers
s = d.slide()
title(s.s, "New enqueue pipeline (dev branch)",
      "Blue: inside NCCL.  Grey: what goes in and comes out.  Yellow: status")
box(s.s, 43, 120, 1194, 50, GREY, stroke=EDGE,
    body="grouped calls: collectives, p2p, put/signal", size=16)
down(s.s, 640, 170, 196)
box(s.s, 43, 196, 260, 300, LINK_DK, stroke=LINK, body="Management\n\ncommunicator jobs\n(init, split,\ndestroy, ...)\nown queue", size=15)
box(s.s, 333, 196, 470, 300, CHIP, stroke=LINK, radius=0.04)
label(s.s, 333, 204, 470, 34, "Preparation", size=19, bold=True)
yy = 246
for st in ["pre-tuning: tuning input per task", "tuning: every collective",
           "classification: route by tuning result", "post-tuning: register, connect"]:
    box(s.s, 353, yy, 430, 48, LINK_DK, stroke=LINK, body=st, size=14)
    yy += 60
box(s.s, 833, 196, 404, 300, CHIP, stroke=LINK, radius=0.04)
label(s.s, 833, 204, 404, 34, "Scheduling (per path)", size=19, bold=True)
yy = 246
for st in ["symmetric kernels", "one-sided: puts before waits", "copy engine", "legacy symmetric (GENK today)"]:
    box(s.s, 853, yy, 364, 48, LINK_DK, stroke=LINK, body=st, size=14)
    yy += 60
sh.arrow(s.s, t, 803, 346, 833, 346, color=WHITE, width=2)
down(s.s, 1035, 496, 520)
box(s.s, 833, 520, 404, 50, GREY, stroke=EDGE, body="each path: one queue per stream", size=15)
box(s.s, 43, 600, 1194, 46, YEL_DK, stroke=YEL, radius=0.3,
    body="framework in 2.31.2 (off by default) · these details: dev", size=15)

# ------------------------------------------------------------------ 5. host API vs device API
s = d.slide()
title(s.s, "NCCL's three APIs",
      "Green: you write it.  Blue: NCCL.  Yellow: plugin.  Grey: hardware")
box(s.s, 43, 112, 572, 440, CHIP, stroke=EDGE, radius=0.04)
box(s.s, 665, 112, 572, 440, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 43, 122, 572, 36, "Host API", size=22, bold=True)
label(s.s, 665, 122, 572, 36, "Device API (since 2.28)", size=22, bold=True)
# left
box(s.s, 83, 172, 492, 56, GRN_DK, stroke=GRN, body="CPU: ncclAllReduce(..., stream)", size=16)
down(s.s, 329, 228, 256)
box(s.s, 83, 256, 492, 70, LINK_DK, stroke=LINK, body="NCCL picks algorithm\nand launches its own kernel", size=16)
down(s.s, 329, 326, 354)
box(s.s, 83, 354, 492, 70, LINK_DK, stroke=LINK, body="NCCL kernel on the GPU\n(code written by NCCL)", size=16)
label(s.s, 83, 440, 492, 40, "your compute: a separate kernel", size=15, color=MUTED)
# right
box(s.s, 705, 172, 492, 56, GRN_DK, stroke=GRN, body="CPU: register window, create devComm", size=16)
down(s.s, 951, 228, 256)
box(s.s, 705, 256, 492, 168, GRN_DK, stroke=GRN, radius=0.06)
label(s.s, 705, 262, 492, 34, "your kernel on the GPU", size=17, bold=True)
box(s.s, 735, 304, 200, 100, GRN_DK, stroke=GRN_HI, body="your compute\n(e.g. MoE routing)", size=14)
box(s.s, 965, 304, 202, 100, LINK_DK, stroke=LINK, body="NCCL device calls\nLSA · GIN · ...", size=14)
label(s.s, 705, 440, 492, 40, "compute and communication in one kernel", size=15, color=MUTED)
box(s.s, 43, 572, 1194, 46, YEL_DK, stroke=YEL, radius=0.3, body="plugin API: NCCL calls plugins, e.g. for the network (net · RMA · GIN · tuner · profiler)", size=15)
box(s.s, 43, 636, 1194, 40, GREY, stroke=EDGE, radius=0.3, body="NVLink · InfiniBand · RoCE · EFA", size=15)

# ------------------------------------------------------------------ 6. device API modules
s = d.slide()
title(s.s, "Device API: one module per path out of your kernel",
      "Green: you write or call it.  Grey: hardware")
box(s.s, 43, 112, 1194, 56, GRN_DK, stroke=GRN, body="your CUDA kernel", size=16)
mods = [("LSA", "load / store to\npeer GPU memory", "CUDA P2P (NVLink, some PCIe)"),
        ("Multimem", "one store or reduce\nto many GPUs", "NVLink SHARP"),
        ("GIN", "put / get / signal\nover the network", "IB · RoCE (built-in) · EFA (plugin)"),
        ("CFT", "put / get / reduce\nto fabric endpoints", "CUDA fabric (Blackwell+)"),
        ("reduce / copy", "building blocks for\nfused kernels", "no link of its own")]
W = 222
x = 43
for name, what, hw in mods:
    down(s.s, x + W // 2, 168, 196)
    box(s.s, x, 196, W, 50, GRN_DK, stroke=GRN, body=name, size=17)
    label(s.s, x, 252, W, 64, what, size=14, color=WHITE)
    box(s.s, x, 326, W, 50, GREY, stroke=EDGE, body=hw, size=14)
    x += W + 21
box(s.s, 43, 420, 1194, 110, GRN_DK, stroke=GRN, radius=0.06)
label(s.s, 63, 428, 1154, 34, "you set up once on the CPU (Host API)", size=17, bold=True)
label(s.s, 63, 468, 1154, 50, "symmetric memory window  →  ncclDevCommCreate(requirements)  →  launch kernel with devComm", size=15)

# ------------------------------------------------------------------ 7. who calls NCCL
s = d.slide()
title(s.s, "Who calls which NCCL API",
      "Green: libraries that call NCCL.  Blue: NCCL.  Yellow: plugin.  Grey: hardware")
# callers row
callers = [("PyTorch\nProcessGroupNCCL (C++)", "host"),
           ("PyTorch \"nccl4py\" backend\n(Python)", "py"),
           ("vLLM PyNccl\n(ctypes)", "host"),
           ("PyTorch symm-mem ops\nDeepEP · NCCL EP", "dev")]
W = 280
x = 43
pos = {}
for name, kind in callers:
    box(s.s, x, 112, W, 72, GRN_DK, stroke=GRN, body=name, size=14)
    pos[name] = x + W // 2
    x += W + 25
# nccl4py box under the experimental backend
xb = 43 + (W + 25)
box(s.s, xb, 220, W, 50, GRN_DK, stroke=GRN, body="nccl4py (Python bindings)", size=14)
down(s.s, xb + W // 2, 184, 220)
# libnccl
box(s.s, 43, 310, 1194, 120, CHIP, stroke=LINK, radius=0.04)
label(s.s, 43, 316, 1194, 30, "libnccl", size=17, bold=True)
box(s.s, 73, 352, 720, 60, LINK_DK, stroke=LINK, body="Host API: communicator · collectives · send/recv · RMA · window", size=14)
box(s.s, 823, 352, 384, 60, LINK_DK, stroke=LINK, body="Device API: called inside your kernel", size=14)
down(s.s, 43 + W // 2, 184, 352)
down(s.s, xb + W // 2, 270, 352)
down(s.s, 43 + 2 * (W + 25) + W // 2, 184, 352)
down(s.s, 43 + 3 * (W + 25) + W // 2, 184, 352)
sh.arrow(s.s, t, 43 + 3 * (W + 25) + 30, 184, 690, 352, color=WHITE, width=1.5, dashed=True)
label(s.s, 860, 262, 90, 24, "setup", size=13, color=MUTED)
# plugins and hardware
down(s.s, 880, 430, 466)
box(s.s, 523, 466, 714, 56, YEL_DK, stroke=YEL, body="plugin API: net · RMA · GIN · tuner · profiler  (e.g. aws-ofi-nccl)", size=14)
down(s.s, 880, 522, 556)
down(s.s, 420, 430, 556)
label(s.s, 432, 480, 150, 30, "built-in IB", size=13, color=MUTED, align="left")
box(s.s, 330, 556, 907, 50, GREY, stroke=EDGE, body="InfiniBand · RoCE · EFA", size=15)
down(s.s, 170, 430, 556)
box(s.s, 43, 556, 260, 50, GREY, stroke=EDGE, body="NVLink · CUDA P2P", size=15)

# ------------------------------------------------------------------ 8. strong vs weak signal
s = d.slide()
title(s.s, "What a GIN signal promises when it arrives",
      "Grey: put from the sender.  Green: data you can read.  Yellow: may still be in flight.  Blue: signal counter")
for px, head in ((43, "weak signal"), (665, "strong signal")):
    box(s.s, px, 112, 572, 470, CHIP, stroke=EDGE, radius=0.04)
    label(s.s, px, 120, 572, 36, head, size=22, bold=True)
    label(s.s, px + 20, 166, 240, 30, "sender", size=16, color=MUTED)
    label(s.s, px + 312, 166, 240, 30, "receiver memory", size=16, color=MUTED)
    for i, name in enumerate(("put A", "put B", "put C + signal")):
        y = 206 + i * 78
        box(s.s, px + 20, y, 240, 56, GREY, stroke=EDGE, body=name, size=15)
        sh.arrow(s.s, t, px + 260, y + 28, px + 312, y + 28, color=WHITE, width=2)
        weak = px == 43
        if i == 2 or not weak:
            box(s.s, px + 312, y, 240, 56, GRN_DK, stroke=GRN, body=("C" if i == 2 else "AB"[i]) + ": readable", size=15)
        else:
            box(s.s, px + 312, y, 240, 56, YEL_DK, stroke=YEL, body="AB"[i] + ": maybe not yet", size=15)
    box(s.s, px + 312, 446, 240, 56, LINK_DK, stroke=LINK, body="signal: 0 → 1", size=15)
    label(s.s, px, 516, 572, 50, "covers only C" if px == 43 else "covers A, B and C (same peer, same context)", size=15, color=MUTED)

# ------------------------------------------------------------------ 9. CFT: address vs logical endpoint, and the team nesting
s = d.slide()
title(s.s, "LSA writes to an address, CFT writes to an endpoint id",
      "Green: your kernel.  Blue: set up by NCCL on the CPU.  Grey: memory.  Yellow: status")
for px, head in ((43, "LSA: store to the peer's address"), (665, "CFT: put to a logical endpoint")):
    box(s.s, px, 112, 572, 330, CHIP, stroke=EDGE, radius=0.04)
    label(s.s, px, 118, 572, 36, head, size=20, bold=True)
    label(s.s, px + 20, 160, 230, 28, "GPU A", size=16, color=GRN_HI)
    label(s.s, px + 322, 160, 230, 28, "GPU B", size=16, color=GRN_HI)
    box(s.s, px + 322, 300, 230, 60, GREY, stroke=EDGE, body="buffer", size=16)
# LSA: one step, the thread itself names B's memory
box(s.s, 63, 196, 230, 80, GRN_DK, stroke=GRN, body="kernel thread\nstore to peer ptr", size=15)
sh.arrow(s.s, t, 293, 236, 365, 318, color=WHITE, width=2.5)
label(s.s, 63, 372, 532, 56, "B's memory is mapped into A\n(only within the LSA team)", size=15, color=MUTED)
# CFT: numbered steps like a protocol
def step(x, y, n):
    sp = sh.rect(s.s, t, x, y, 30, 30, fill=YEL, stroke=None, shape=MSO_SHAPE.OVAL)
    sh._write(sp.text_frame, t, str(n), 14, RGBColor(20, 20, 20), True, "center", "middle")
box(s.s, 685, 196, 530, 52, LINK_DK, stroke=LINK, body="CPU, once: bind each GPU's buffer to an endpoint id", size=14)
step(668, 182, 1)
box(s.s, 685, 266, 230, 94, GRN_DK, stroke=GRN, body="kernel\nstage data in\nshared memory", size=14)
step(668, 252, 2)
sh.arrow(s.s, t, 915, 330, 987, 330, color=WHITE, width=2.5)
step(936, 268, 3)
label(s.s, 916, 296, 80, 30, "put(id, off)", size=12, color=WHITE)
step(668, 378, 4)
label(s.s, 705, 372, 510, 56, "check completion\nthe kernel never holds B's address", size=15, color=MUTED)
# Team nesting: what the hierarchical kernels would split
box(s.s, 43, 462, 1194, 210, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 63, 468, 700, 32, "CFT team (from the CUDA clique, dev, CUDA 13.4+)", size=17, bold=True, align="left")
for gx in (73, 493):
    box(s.s, gx, 510, 380, 110, LINK_DK, stroke=LINK, radius=0.08)
    label(s.s, gx, 512, 380, 26, "LSA team", size=14, color=LINK)
    for i in range(4):
        box(s.s, gx + 18 + i * 90, 546, 74, 50, GREY, stroke=EDGE, body="GPU", size=13)
sh.arrow(s.s, t, 453, 571, 493, 571, color=WHITE, width=2.5)
sh.arrow(s.s, t, 493, 590, 453, 590, color=WHITE, width=2.5)
label(s.s, 73, 628, 800, 32, "one possible split (author's reading): near via LSA · far via CFT", size=14, color=MUTED, align="left")
box(s.s, 913, 516, 304, 104, YEL_DK, stroke=YEL, radius=0.15,
    body="hierarchical kernels:\nroadmap, none found\nin public branches", size=14)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
