"""gen_figs.py: figures for the Zenn article on Lustre over EFA (kefalnd) vs TCP.

    /usr/bin/python3 gen_figs.py <out.pptx>

Text in the figures is English (ZN-18). Values come from the hands-on run on 2026-10-26 JST
(c7gn.16xlarge client, FSx for Lustre PERSISTENT_2 4.8 TiB at 1000 MB/s/TiB, Lustre 2.15.6,
kefalnd 1.2.6) and from lustre-release at 6325870717c7899f1ba545493ce2a07cb3834a6b.
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "lustre-efa.pptx"

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
RED = RGBColor(240, 90, 80)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=16, color=WHITE, radius=0.12,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 22, 1194, 46, head, size=30, bold=True, align="left")
    label(s, 43, 68, 1194, 26, sub, size=16, color=MUTED, align="left")


def arr(s, x1, y1, x2, y2, color=WHITE, width=2.0, dashed=False):
    return sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


# ---------------------------------------------------------------- 1. two stacks, one device
s = d.slide().s
title(s, "Two stacks share only the RDMA core, efa.ko and the device",
      "Blue: Lustre client in the kernel.  Green: EFA path.  Yellow: TCP path")
label(s, 43, 104, 520, 30, "Training job (user space)", size=18, color=MUTED, align="left")
label(s, 640, 104, 597, 30, "Lustre client (kernel)", size=18, color=MUTED, align="left")
ys = [140, 206, 272, 338]
for y, txt in zip(ys, ["NCCL", "aws-ofi-nccl", "libfabric (efa provider)", "rdma-core (user verbs)"]):
    box(s, 43, y, 520, 50, CHIP, stroke=EDGE, body=txt, size=18)
for a, b in zip(ys, ys[1:]):
    arr(s, 303, a + 50, 303, b)
for y, txt in zip(ys, ["llite (VFS)", "osc / mdc", "ptlrpc (RPC, import)", "LNet: select, health, discovery"]):
    box(s, 640, y, 597, 50, LINK_DK, stroke=LINK, body=txt, size=18)
for a, b in zip(ys, ys[1:]):
    arr(s, 938, a + 50, 938, b)
box(s, 640, 438, 350, 70, GRN_DK, stroke=GRN, body="kefalnd\nkernel verbs, SRD QP", size=16)
box(s, 1010, 438, 227, 70, YEL_DK, stroke=YEL, body="ksocklnd\nTCP sockets", size=16)
arr(s, 815, 388, 815, 438, color=GRN_HI)
arr(s, 1123, 388, 1123, 438, color=YEL)
arr(s, 303, 388, 303, 530, color=GRN_HI)
arr(s, 815, 508, 815, 530, color=GRN_HI)
box(s, 43, 530, 947, 56, GRN_DK, stroke=GRN_HI, body="ib_core + efa.ko  ->  EFA device", size=18)
box(s, 1010, 530, 227, 56, YEL_DK, stroke=YEL, body="ENA", size=18)
arr(s, 1123, 508, 1123, 530, color=YEL)
box(s, 640, 616, 597, 30, CHIP, stroke=GRN, dash=MSO_LINE_DASH_STYLE.DASH,
    body="OSS: 1.20.0.248@efa + 10.0.1.20@tcp", size=15)
box(s, 640, 652, 597, 30, CHIP, stroke=YEL, dash=MSO_LINE_DASH_STYLE.DASH,
    body="MGS / MDS: 10.0.1.40@tcp only", size=15)
label(s, 43, 616, 580, 66, "test file system: OSS reached over EFA and TCP,\nMGS / MDS over TCP only", size=14, color=MUTED, align="left")

# ---------------------------------------------------------------- 2. connection setup
s = d.slide().s
title(s, "kefalnd opens a connection through TCP first",
      "One run, client debug log: 3.0 ms from first send to ACTIVE.  Yellow: TCP.  Green: EFA")
CX, SX = 420, 1000
label(s, CX - 150, 96, 300, 44, "client 2.30.0.248@efa\n10.0.2.30@tcp", size=15, bold=True)
label(s, SX - 160, 96, 320, 44, "OSS 1.20.0.248@efa\n10.0.1.20@tcp", size=15, bold=True)
sh.rule(s, t, CX, 140, 1, color=EDGE)
for x in (CX, SX):
    ln = s.shapes.add_connector(1, sh.U(x), sh.U(140), sh.U(x), sh.U(690))
    ln.line.color.rgb = EDGE
    ln.line.width = sh.Pt(1.5)
msgs = [
    (170, ">", YEL, "LNet ping to 10.0.1.20@tcp", True),
    (215, "<", YEL, "reply: GID + CM QP", True),
    (300, ">", GRN_HI, "CONN_PROBE", False),
    (345, "<", GRN_HI, "PROBE_RESP: epoch, caps", False),
    (430, ">", GRN_HI, "CONN_REQ: data QPs", False),
    (475, "<", GRN_HI, "CONN_REQ_ACK", False),
    (560, ">", WHITE, "first LNet PUT", False),
]
for y, dirn, col, txt, dash in msgs:
    if dirn == ">":
        arr(s, CX, y, SX, y + 18, color=col, width=2.25, dashed=dash)
    else:
        arr(s, SX, y, CX, y + 18, color=col, width=2.25, dashed=dash)
    label(s, CX + 40, y - 26, SX - CX - 80, 24, txt, size=15, color=col)
states = [(150, 80, "PROBE_TCP", "+0.0 ms", YEL_DK, YEL),
          (280, 100, "PROBE_EFA", "+0.7 ms", GRN_DK, GRN),
          (410, 100, "ESTABLISH", "+2.5 ms", GRN_DK, GRN),
          (540, 60, "ACTIVE", "+3.0 ms", GRN_DK, GRN_HI)]
label(s, SX + 15, 562, 220, 30, "PUT done +3.5 ms", size=14, color=MUTED, align="left")
for y, h, name, tm, fill, stroke in states:
    box(s, 43, y, 230, h, fill, stroke=stroke, body=name, size=17)
    label(s, 278, y, 110, h, tm, size=15, color=MUTED, align="left")
box(s, 43, 625, 1194, 50, CHIP, stroke=EDGE, radius=0.3,
    body="OSS opens its own connection back (one per direction)", size=15, color=MUTED)

# ---------------------------------------------------------------- 3. bulk = RDMA READ by the receiver
s = d.slide().s
title(s, "Bulk data moves only as RDMA READ by the receiver",
      "Lustre bulk read = OSS PUT to client.  Lustre bulk write = OSS GET from client")
for px, head in ((43, "Client reads a file"), (655, "Client writes a file (from code)")):
    label(s, px, 104, 582, 32, head, size=20, bold=True)
    box(s, px, 140, 582, 420, CHIP, stroke=EDGE, radius=0.04)
    label(s, px + 20, 148, 160, 26, "client", size=15, color=MUTED)
    label(s, px + 402, 148, 160, 26, "OSS", size=15, color=MUTED)
    for x in (px + 100, px + 482):
        ln = s.shapes.add_connector(1, sh.U(x), sh.U(178), sh.U(x), sh.U(545))
        ln.line.color.rgb = EDGE
        ln.line.width = sh.Pt(1.5)
# read panel
L, R = 143, 525
arr(s, R, 215, L, 233, color=WHITE)
label(s, L + 10, 186, R - L - 20, 24, "PUTR_REQ: addr, key, size", size=15)
arr(s, L, 290, R, 290, color=GRN_HI, dashed=True)
label(s, L + 10, 262, R - L - 20, 24, "RDMA READ request", size=15, color=GRN_HI)
for dy in (0, 10, 20):
    arr(s, R, 330 + dy, L, 360 + dy, color=GRN_HI, width=3.0)
label(s, L + 10, 395, R - L - 20, 24, "data, about 1 MiB per read", size=15, color=GRN_HI)
arr(s, L, 455, R, 473, color=WHITE)
label(s, L + 10, 426, R - L - 20, 24, "PUTR_DONE", size=15)
# write panel
L2, R2 = 755, 1137
arr(s, R2, 200, L2, 218, color=WHITE)
label(s, L2 + 10, 172, R2 - L2 - 20, 24, "GETR_REQ", size=15)
arr(s, L2, 262, R2, 280, color=WHITE)
label(s, L2 + 10, 234, R2 - L2 - 20, 24, "GETR_ACK: addr, key, size", size=15)
arr(s, R2, 330, L2, 330, color=GRN_HI, dashed=True)
label(s, L2 + 10, 302, R2 - L2 - 20, 24, "RDMA READ request", size=15, color=GRN_HI)
for dy in (0, 10, 20):
    arr(s, L2, 370 + dy, R2, 400 + dy, color=GRN_HI, width=3.0)
label(s, L2 + 10, 428, R2 - L2 - 20, 24, "data, RDMA READ by the OSS", size=15, color=GRN_HI)
arr(s, R2, 500, L2, 518, color=WHITE)
label(s, L2 + 10, 472, R2 - L2 - 20, 24, "GETR_DONE", size=15)
# measured counters
cards = [("80 GiB", "client rdma_read_bytes", "= file data read"),
         ("81,921", "client rdma_read_wrs (total)", "bytes / reads = about 1 MiB"),
         ("0", "client rdma_write_wrs", "no RDMA WRITE"),
         ("8,900 B", "header + payload up to this", "IMMEDIATE over EFA, no RDMA")]
x = 43
for v, k, n in cards:
    box(s, x, 578, 284, 112, GRN_DK if v != "8,900 B" else GREY, stroke=GRN if v != "8,900 B" else EDGE, radius=0.1)
    label(s, x, 584, 284, 40, v, size=24, bold=True)
    label(s, x, 624, 284, 28, k, size=14, color=WHITE)
    label(s, x, 652, 284, 28, n, size=14, color=MUTED)
    x += 303

# ---------------------------------------------------------------- 4. the stall loop (measured)
s = d.slide().s
title(s, "The client keeps choosing a path it cannot receive on",
      "Fault injected on the client LNet input.  Yellow: the fault.  Blue: what the client log showed")
cx = 640
nodes = [
    (cx - 170, 112, 340, "Client LNet drops", "everything from @efa", YEL_DK, YEL),
    (cx + 290, 300, 300, "Client peer health", "stays 1000 (tcp, efa)", LINK_DK, LINK),
    (cx - 150, 520, 300, "ptlrpc reconnects", "to 10.0.1.20@tcp", LINK_DK, LINK),
    (cx - 590, 300, 300, "LNet picks", "1.20.0.248@efa", LINK_DK, LINK),
]
H = 92
for x, y, w, a1, b1, fill, stroke in nodes:
    box(s, x, y, w, H, fill, stroke=stroke, body=a1 + "\n" + b1, size=17)
edges = [((cx + 170, 158), (cx + 440, 300)),
         ((cx + 440, 392), (cx + 150, 566)),
         ((cx - 150, 566), (cx - 440, 392)),
         ((cx - 440, 300), (cx - 170, 158))]
for (x1, y1), (x2, y2) in edges:
    arr(s, x1, y1, x2, y2, color=WHITE, width=2.25)
label(s, cx - 600, 150, 330, 26, "messages from OSS arrive over @efa", size=14, color=MUTED, align="left")
box(s, cx - 210, 270, 420, 160, CHIP, stroke=EDGE, radius=0.08,
    body="stalled while the rule was in: ~890 s\nNIC tx +0.3 MB (10 s to 400 s)\nretry ~35 -> 40 -> 45 s, then 56 s", size=16)

# ---------------------------------------------------------------- 5. TCP vs EFA throughput
s = d.slide().s
title(s, "Same client, same file system: TCP vs EFA",
      "One c7gn.16xlarge, 4,800 GiB at 1000 MB/s/TiB, 1 OST, fio 4 MiB direct I/O, MB/s = 10^6 B/s")
X0, Y0, PH = 140, 640, 480   # plot origin and height
YMAX = 9000.0


def yv(v):
    return Y0 - PH * v / YMAX


for v in (0, 3000, 6000, 9000):
    yy = yv(v)
    ln = s.shapes.add_connector(1, sh.U(X0), sh.U(yy), sh.U(1237), sh.U(yy))
    ln.line.color.rgb = GREY
    ln.line.width = sh.Pt(0.75)
    label(s, 43, yy - 12, 90, 24, f"{v:,}", size=13, color=MUTED, align="right")
label(s, 43, 120, 200, 24, "MB/s", size=14, color=MUTED, align="left")
groups = [("1 file, write", 620, 5576), ("1 file, read", 620, 8115),
          ("16 files, write", 620, 4772), ("16 files, read", 620, 7238)]
gx = X0 + 40
GW = 250
for name, tcp, efa in groups:
    for i, (v, fill, stroke, tag) in enumerate(((tcp, YEL_DK, YEL, "TCP"), (efa, GRN_DK, GRN_HI, "EFA"))):
        bx = gx + i * 100
        sh.rect(s, t, bx, yv(v), 84, Y0 - yv(v), fill=fill, stroke=stroke, sw=1.25)
        if tag == "TCP":
            label(s, bx, yv(v) + 4, 84, Y0 - yv(v) - 8, f"{v:,}", size=15, bold=True)
        else:
            off = 52 if abs(v - 4688) < 300 else 30
            label(s, bx - 20, yv(v) - off, 124, 26, f"{v:,}", size=15, bold=True)
        label(s, bx, Y0 + 4, 84, 22, tag, size=13, color=MUTED)
    label(s, gx - 20, Y0 + 28, 224, 26, name, size=15)
    gx += GW + 20
for v, txt, col in ((625, "5 Gbps per client-OSS pair = 625", YEL), (4688, "provisioned 4,688", MUTED)):
    yy = yv(v)
    ln = s.shapes.add_connector(1, sh.U(X0), sh.U(yy), sh.U(1237), sh.U(yy))
    ln.line.color.rgb = col
    ln.line.width = sh.Pt(1.5)
    ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH if v == 625 else MSO_LINE_DASH_STYLE.ROUND_DOT
    lx = 300 if v == 625 else 820
    ln2 = s.shapes.add_connector(1, sh.U(lx), sh.U(132), sh.U(lx + 40), sh.U(132))
    ln2.line.color.rgb = col
    ln2.line.width = sh.Pt(1.5)
    ln2.line.dash_style = MSO_LINE_DASH_STYLE.DASH if v == 625 else MSO_LINE_DASH_STYLE.ROUND_DOT
    label(s, lx + 50, 120, 460, 24, ("dashed: " if v == 625 else "dotted: ") + txt, size=14, color=col, align="left")

# ---------------------------------------------------------------- 6. EFA NID layout (small NID)
s = d.slide().s
title(s, "A small EFA NID is built from the IP and the PCI slot",
      "kefalnd_create_efa_nid. OSS NID seen from the client; bus and devfn inferred from it")
label(s, 43, 120, 1194, 30, "TCP NID   10.0.1.20@tcp", size=22, bold=True, align="left")
box(s, 43, 170, 290, 70, CHIP, stroke=EDGE, body="10.0", size=24, color=MUTED)
box(s, 343, 170, 290, 70, YEL_DK, stroke=YEL, body="1.20", size=24)
label(s, 43, 245, 590, 26, "IPv4: upper 16 bits dropped, lower 16 bits kept", size=14, color=MUTED, align="left")
arr(s, 488, 240, 488, 360, color=YEL, width=2.5)
label(s, 700, 170, 537, 30, "EFA device PCI address", size=18, color=MUTED, align="left")
box(s, 700, 210, 250, 60, GRN_DK, stroke=GRN, body="bus 0x00 (inferred)", size=18)
box(s, 970, 210, 267, 60, GRN_DK, stroke=GRN, body="devfn 0xf8 (inferred)", size=18)
arr(s, 825, 270, 825, 360, color=GRN_HI, width=2.5)
arr(s, 1103, 270, 1103, 360, color=GRN_HI, width=2.5)
label(s, 43, 330, 300, 30, "EFA NID", size=22, bold=True, align="left")
box(s, 343, 370, 290, 80, YEL_DK, stroke=YEL, body="1.20", size=28)
box(s, 700, 370, 250, 80, GRN_DK, stroke=GRN_HI, body="0", size=28)
box(s, 970, 370, 267, 80, GRN_DK, stroke=GRN_HI, body="248", size=28)
label(s, 343, 460, 894, 40, "=  1.20.0.248@efa", size=26, bold=True)
box(s, 43, 540, 1194, 120, CHIP, stroke=EDGE, radius=0.06,
    body="peer TCP NID = my IP upper 16 bits + peer EFA NID upper 16 bits\nunique only inside one /16;  changes if the device moves to another PCI slot", size=17)

# ---------------------------------------------------------------- 7. Lustre basics
s = d.slide().s
title(s, "Who talks to whom in Lustre",
      "Blue: client layers.  White: small requests (RPC).  Green: file data (bulk)")
# client stack
label(s, 43, 104, 380, 30, "client", size=20, bold=True)
layers = ["application", "llite (file system)", "mdc / osc", "ptlrpc (RPC, reconnect)", "LNet (address, path choice)", "LND (kefalnd / ksocklnd)"]
y = 140
for i, name in enumerate(layers):
    box(s, 43, y, 380, 62, CHIP if i == 0 else LINK_DK, stroke=EDGE if i == 0 else LINK, body=name, size=17)
    if i:
        arr(s, 233, y - 12, 233, y)
    y += 74
# servers
box(s, 760, 130, 477, 110, CHIP, stroke=EDGE, radius=0.06, body="MGS\nconfiguration at mount", size=18)
box(s, 760, 270, 477, 130, CHIP, stroke=EDGE, radius=0.06, body="MDS + MDT\nopen, names, layout, metadata locks", size=17)
box(s, 760, 430, 477, 220, CHIP, stroke=EDGE, radius=0.06)
label(s, 760, 440, 477, 34, "OSS + OST: read / write, extent locks", size=17, bold=True)
for i, ox in enumerate((790, 940, 1090)):
    box(s, ox, 490, 120, 70, GREY, stroke=EDGE, body="OST " + str(i), size=16)
label(s, 760, 580, 477, 50, "file contents, striped over OSTs", size=16, color=MUTED)
# arrows: everything leaves the client through the LND
arr(s, 423, 522, 760, 185, color=WHITE, width=2)
arr(s, 423, 530, 760, 335, color=WHITE, width=2)
arr(s, 423, 538, 760, 500, color=WHITE, width=2)
for dy in (0, 10):
    arr(s, 760, 585 + dy, 423, 552 + dy, color=GRN_HI, width=3)
for dy in (0, 10):
    arr(s, 423, 562 + dy, 760, 625 + dy, color=GRN_HI, width=3)
label(s, 430, 650, 330, 26, "file data (bulk): read and write", size=15, color=GRN_HI)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
