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
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "lustre-fsx.pptx"

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

# Every colour role also carries a pattern or a line weight (ZN-29), so the figures read without colour.
ROLE_PATTERN = {LINK: "diagonal", GRN: "backdiagonal", GRN_HI: "backdiagonal", YEL: "cross", RED: "grid"}
ARROW_WIDTH = {GRN_HI: 4.0, GRN: 4.0, YEL: 2.75, LINK: 2.0, RED: 2.75}

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=16, color=WHITE, radius=0.12,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    kind = ROLE_PATTERN.get(stroke)
    if kind and fill is not None:
        pattern_fill(sp, kind, fill, stroke, strength=0.5)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 22, 1194, 46, head, size=30, bold=True, align="left")
    label(s, 43, 68, 1194, 26, sub, size=16, color=MUTED, align="left")


def arr(s, x1, y1, x2, y2, color=WHITE, width=2.0, dashed=False):
    width = ARROW_WIDTH.get(color, width)
    if color == RED:
        dashed = True
    return sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


# ---------------------------------------------------------------- 2. connection setup
s = d.slide().s
title(s, "kefalnd opens a connection through TCP first",
      "One run, client debug log.  Yellow dashed: over TCP.  Green thick: over EFA.  White thin: first LNet PUT")
CX, SX = 420, 1000
label(s, CX - 230, 100, 460, 30, "client  2.30.0.248@efa / 10.0.2.30@tcp", size=15, bold=True)
label(s, SX - 230, 100, 460, 30, "OSS  1.20.0.248@efa / 10.0.1.20@tcp", size=15, bold=True)
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
label(s, CX + 60, 572, 460, 28, "completion seen by the client: +3.5 ms", size=14, color=MUTED, align="left")
for y, h, name, tm, fill, stroke in states:
    box(s, 43, y, 230, h, fill, stroke=stroke, body=name, size=17)
    label(s, 278, y, 110, h, tm, size=15, color=MUTED, align="left")
box(s, 43, 625, 1194, 50, CHIP, stroke=EDGE, radius=0.3,
    body="OSS opens its own connection back (one per direction)", size=15, color=MUTED)

# ---------------------------------------------------------------- 3. bulk = RDMA READ by the receiver
s = d.slide().s
title(s, "Bulk data moves only as RDMA READ by the receiver",
      "Read = OSS PUT, write = OSS GET.  Green dashed: RDMA READ request.  Green thick: data.  White thin: control")
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
         ("<= 8,900 B", "header + data, CPU memory:", "IMMEDIATE, no RDMA")]
x = 43
for v, k, n in cards:
    box(s, x, 578, 284, 112, GRN_DK if v != "<= 8,900 B" else GREY, stroke=GRN if v != "<= 8,900 B" else EDGE, radius=0.1)
    label(s, x, 584, 284, 40, v, size=24, bold=True)
    label(s, x, 624, 284, 28, k, size=14, color=WHITE)
    label(s, x, 652, 284, 28, n, size=14, color=MUTED)
    x += 303

# ---------------------------------------------------------------- 4. the stall loop (measured)
s = d.slide().s
title(s, "The client keeps choosing a path it cannot receive on",
      "Fault injected on the client LNet input.  Yellow, cross-hatched: the fault.  Blue, hatched: what the client log showed.  Grey: measured values")
cx = 640
nodes = [
    (cx - 170, 112, 340, "Client LNet drops", "everything from @efa", YEL_DK, YEL),
    (cx + 290, 300, 300, "Client peer health 1000", "(tcp, efa), at 10-400 s", LINK_DK, LINK),
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
    body="stalled while the rule was in: ~890 s\n10 s to 400 s: ENA tx +0.3 MB\nreconnect gaps ~35, 40, 45 s", size=16)

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
        bar = sh.rect(s, t, bx, yv(v), 84, Y0 - yv(v), fill=fill, stroke=stroke, sw=1.25)
        pattern_fill(bar, ROLE_PATTERN[stroke], fill, stroke, strength=0.5)
        if tag == "TCP":
            label(s, bx, yv(v) + 4, 84, Y0 - yv(v) - 8, f"{v:,}", size=15, bold=True)
        else:
            off = 52 if abs(v - 4688) < 300 else 30
            label(s, bx - 20, yv(v) - off, 124, 26, f"{v:,}", size=15, bold=True)
        label(s, bx, Y0 + 4, 84, 22, tag, size=13, color=MUTED)
    label(s, gx - 20, Y0 + 28, 224, 26, name, size=15)
    gx += GW + 20
for v, txt, col in ((625, "625 MB/s per pair over ENA (AWS doc)", WHITE), (4688, "provisioned 4,688", MUTED)):
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

# ---------------------------------------------------------------- 7. which servers have an EFA NID (measured)
s = d.slide().s
title(s, "The client saw an EFA NID only on the OSS",
      "Green, hatched: EFA NID.  Yellow, cross-hatched: TCP NID.  Measured with lnetctl peer show")
box(s, 43, 250, 300, 200, LINK_DK, stroke=LINK, body="client\n10.0.2.30@tcp\n2.30.0.248@efa", size=18)
box(s, 760, 130, 477, 150, CHIP, stroke=EDGE, radius=0.06)
label(s, 760, 138, 477, 34, "MGS + MDS (MDT 0)", size=18, bold=True)
box(s, 830, 190, 340, 56, YEL_DK, stroke=YEL, body="10.0.1.40@tcp", size=17)
box(s, 760, 330, 477, 230, CHIP, stroke=EDGE, radius=0.06)
label(s, 760, 338, 477, 34, "OSS (OST 0)", size=18, bold=True)
box(s, 830, 392, 340, 56, YEL_DK, stroke=YEL, body="10.0.1.20@tcp", size=17)
box(s, 830, 470, 340, 56, GRN_DK, stroke=GRN_HI, body="1.20.0.248@efa", size=17)
arr(s, 343, 300, 830, 218, color=YEL)
label(s, 360, 196, 420, 26, "to the MDS (open, names, layout): TCP", size=15, color=YEL)
arr(s, 343, 400, 830, 498, color=GRN_HI)
label(s, 300, 520, 440, 26, "to the OSS (read / write, bulk): EFA (the TCP NID got only 21 sends)", size=15, color=GRN_HI)
label(s, 43, 600, 1194, 60, "One file system: 1 MDT, 1 OST, PERSISTENT_2 SSD, metadata in AUTOMATIC mode.\nMore MDS (metadata IOPS above 12,000) were not tested.", size=15, color=MUTED)

# ---------------------------------------------------------------- 8. metadata IOPS scaling adds MDS
s = d.slide().s
title(s, "Metadata IOPS above 12,000 add metadata servers",
      "Hatched: added servers and new metadata.  Plain: the original server and the existing directories")
box(s, 43, 140, 520, 420, CHIP, stroke=EDGE, radius=0.05)
label(s, 43, 150, 520, 34, "up to 12,000 metadata IOPS (one MDS)", size=18, bold=True)
box(s, 103, 220, 400, 70, GREY, stroke=EDGE, body="MDS 0 / MDT 0", size=18)
box(s, 103, 320, 400, 60, GREY, stroke=EDGE, body="/data, /ckpt (existing)", size=16)
box(s, 717, 140, 520, 420, CHIP, stroke=EDGE, radius=0.05)
label(s, 717, 150, 520, 34, "after: more MDS (up to 192,000 IOPS)", size=18, bold=True)
box(s, 747, 220, 140, 70, GREY, stroke=EDGE, body="MDS 0", size=17)
box(s, 907, 220, 140, 70, LINK_DK, stroke=LINK, body="MDS 1", size=17)
box(s, 1067, 220, 140, 70, LINK_DK, stroke=LINK, body="MDS ...", size=17)
box(s, 747, 320, 140, 60, GREY, stroke=EDGE, body="/data\n/ckpt", size=14)
box(s, 747, 392, 460, 44, LINK_DK, stroke=LINK, body="new metadata: on all servers", size=15)
arr(s, 563, 350, 717, 350, color=WHITE, width=2.5)
label(s, 747, 450, 460, 90, "existing directories stay on MDS 0\nand get no more metadata IOPS", size=16, color=MUTED)
label(s, 43, 590, 1194, 70, "Increase only (no decrease), at least 6 hours apart, may be unavailable for a few minutes while scaling.\nIntelligent-Tiering: the maximum went from 12,000 to 192,000 on 2026-11-05.", size=15, color=MUTED)

# ---------------------------------------------------------------- 8. which failures reach health
s = d.slide().s
title(s, "Which failures reach the health of a NID?",
      "Green thick arrow: reaches health.  Red dashed arrow: never reaches health.  Blue: what kefalnd reports")
for x, w, h in ((43, 370, "what happens"), (470, 370, "what reaches LNet from kefalnd"), (897, 340, "what LNet does")):
    label(s, x, 98, w, 28, h, size=16, color=MUTED)
rows = [("a send completes with an error", "REMOTE_DROPPED", "peer NI health down, resend", True),
        ("memory registration fails", "LOCAL_DROPPED", "own NI health down, may resend", True),
        ("connection torn down while sends wait", "LOCAL_ABORTED", "own NI health down", True),
        ("no completion by the send deadline (cleanup-list connections only)", "NETWORK_TIMEOUT", "both NIs down, no resend", True),
        ("received message fails the check, for example a wrong epoch", "dropped, nothing reported", "nothing happens", False),
        ("a send stalls on a connection used within 200 s", "never reaches the deadline check", "nothing happens", False),
        ("LNet drops it at its receive entry (the fault in this article)", "nothing: the drop is in LNet, above kefalnd", "nothing happens", False)]
y = 130
for a, b, c, ok in rows:
    box(s, 43, y, 370, 68, GREY, stroke=EDGE, body=a, size=15)
    box(s, 470, y, 370, 68, LINK_DK, stroke=LINK, body=b, size=15)
    box(s, 897, y, 340, 68, GRN_DK if ok else RGBColor(90, 30, 28), stroke=GRN_HI if ok else RED, body=c, size=15)
    arr(s, 413, y + 34, 470, y + 34, color=GRN_HI if ok else RED)
    arr(s, 840, y + 34, 897, y + 34, color=GRN_HI if ok else RED)
    y += 77

# ---------------------------------------------------------------- 9. how LNet picks EFA or TCP
s = d.slide().s
title(s, "LNet compares EFA and TCP in this order",
      "The first row with a difference decides.  Green thick: EFA wins.  Red, grid-hatched: why EFA can stay chosen")
rows = [("peer network health", "tcp 1000 / efa 1000", "tie", False),
        ("peer network priority", "not set", "tie", False),
        ("own network health", "tcp 1000 / efa 1000", "tie", False),
        ("own network priority (UDSP)", "tcp not set / efa 0", "EFA wins", True)]
label(s, 43, 100, 810, 28, "the test configuration, compared top to bottom", size=16, color=MUTED, align="left")
y = 140
for nm, val, res, win in rows:
    box(s, 43, y, 300, 84, GREY, stroke=EDGE, body=nm, size=16)
    box(s, 363, y, 270, 84, CHIP, stroke=EDGE, body=val, size=16)
    arr(s, 633, y + 42, 690, y + 42, color=GRN_HI if win else WHITE)
    box(s, 690, y, 163, 84, GRN_DK if win else GREY, stroke=GRN_HI if win else EDGE, body=res, size=17)
    y += 100
label(s, 897, 100, 340, 28, "why EFA can stay chosen", size=16, color=MUTED)
for k, txt in enumerate(("A: the failure never reaches health",
                         "B: another efa NI of the peer holds the maximum (not in this test)",
                         "C: health may recover before the next send")):
    box(s, 897, 140 + k * 130, 340, 108, RGBColor(90, 30, 28), stroke=RED, body=txt, size=16)
label(s, 43, 560, 1194, 60, "TCP wins only if the health of efa falls below that of tcp. This test never observed that.", size=16, color=MUTED, align="left")

# ---------------------------------------------------------------- 10. bandwidth one node needs vs TCP
s = d.slide().s
title(s, "Bandwidth one node needs, and what TCP gives",
      "Blue hatched: need per node (calculation, not measured).  Yellow dashed: 0.62 GB/s measured for one client-OSS pair")
X0, SC = 430, 260
for k in range(4):
    xx = X0 + k * SC
    ln = s.shapes.add_connector(1, sh.U(xx), sh.U(130), sh.U(xx), sh.U(520))
    ln.line.color.rgb = GREY
    ln.line.width = sh.Pt(0.75)
    label(s, xx - 40, 524, 80, 24, f"{k}", size=14, color=MUTED)
label(s, X0 + 3 * SC - 60, 548, 200, 24, "GB/s", size=14, color=MUTED)
for i, (nm, v, osss) in enumerate((("sync checkpoint save (18 s)", 2.49, "5 OSSs"),
                                   ("restart read", 2.05, "4 OSSs"),
                                   ("RL weight read", 2.05, "4 OSSs"))):
    yy = 160 + i * 110
    label(s, 43, yy, 370, 70, nm, size=17, align="left")
    box(s, X0, yy, v * SC, 70, LINK_DK, stroke=LINK)
    label(s, X0 + 0.62 * SC + 16, yy, v * SC - 0.62 * SC - 24, 70, f"{v:.2f} GB/s: {osss} at 0.62 each", size=16, bold=True, align="left")
xx = X0 + 0.62 * SC
ln = s.shapes.add_connector(1, sh.U(xx), sh.U(126), sh.U(xx), sh.U(520))
ln.line.color.rgb = YEL
ln.line.width = sh.Pt(2.5)
ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
label(s, xx + 8, 128, 340, 24, "0.62 GB/s measured", size=14, color=YEL, align="left")
label(s, 43, 590, 1194, 70, "32B parameters, 10 nodes, 14 bytes per parameter, file system 20.5 GB/s.  One client over ENA can take 12.5 GB/s in total.", size=15, color=MUTED, align="left")

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
