"""gen_basics.py: figures for the beginner article on Lustre architecture and LNet.

    /usr/bin/python3 gen_basics.py <out.pptx>

Text in figures is English (ZN-18). Facts come from the Lustre Operations Manual
(doc.lustre.org, fetched 2026-11-05) and lustre-release at 6325870717c7899f1ba545493ce2a07cb3834a6b.
"""
import sys
sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptxkit import Deck, shapes as sh  # noqa: E402
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "lustre-basics.pptx"

GRN = RGBColor(36, 160, 70); GRN_HI = RGBColor(59, 209, 111); GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30); EDGE = RGBColor(70, 74, 80); GREY = RGBColor(52, 56, 64)
LINK = RGBColor(40, 150, 240); LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50); YEL_DK = RGBColor(80, 66, 14)
MUTED = RGBColor(150, 150, 158); WHITE = RGBColor(245, 245, 248); RED = RGBColor(240, 90, 80)
CH = [RGBColor(59, 209, 111), RGBColor(40, 150, 240), RGBColor(251, 211, 50),
      RGBColor(240, 140, 60), RGBColor(190, 120, 240), RGBColor(240, 90, 150)]

d = Deck(TPL, check_layout=False)
t = d.theme


# Every colour role also carries a pattern (ZN-29), so the figure reads without colour.
ROLE_PATTERN = {LINK: "diagonal", GRN: "backdiagonal", GRN_HI: "backdiagonal", YEL: "cross", RED: "grid"}


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align, anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=16, color=WHITE, radius=0.12, dash=None, sw=1.25):
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
    # line weight also tells the roles apart (ZN-29): green thick, yellow medium, red dashed, others thin
    width = {GRN_HI: 4.0, GRN: 4.0, YEL: 2.75, LINK: 2.0, RED: 2.75}.get(color, width)
    if color == RED:
        dashed = True
    return sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed)


def vline(s, x, y1, y2, color=EDGE, w=1.5):
    ln = s.shapes.add_connector(1, sh.U(x), sh.U(y1), sh.U(x), sh.U(y2))
    ln.line.color.rgb = color
    ln.line.width = sh.Pt(w)


def badge(s, x, y, n, color=YEL):
    sh.badge(s, t, x, y, 30, str(n), color=color, size=15)


def seq(s, xs, names, y0=112, y1=690, colors=None):
    for i, (x, nm) in enumerate(zip(xs, names)):
        c = (colors or [LINK] * len(xs))[i]
        box(s, x - 90, y0, 180, 44, CHIP, stroke=c, body=nm, size=16)
        vline(s, x, y0 + 44, y1)


def msg(s, xa, xb, y, text, color=WHITE, dashed=False, width=2.25, dy=0):
    arr(s, xa, y, xb, y + dy, color=color, width=width, dashed=dashed)
    label(s, min(xa, xb) + 10, y - 28, abs(xb - xa) - 20, 24, text, size=14, color=color)


# 1 ------------------------------------------------------------- overview
s = d.slide().s
title(s, "Lustre: clients, three kinds of servers, one network",
      "Blue: client side.  Grey: servers.  Green: the server that holds file data")
cy = (185, 335, 485)
for i, nm in enumerate(["client 1", "client 2", "client 3"]):
    box(s, 43, cy[i] - 50, 250, 100, LINK_DK, stroke=LINK, body=nm + "\nmounts the file system", size=17)
    arr(s, 293, cy[i], 400, cy[i], color=WHITE, width=1.75)
box(s, 400, 130, 90, 440, CHIP, stroke=YEL, body="LNet", size=19, radius=0.2)
arr(s, 490, 185, 640, 185, color=WHITE, width=2)
arr(s, 490, 330, 640, 330, color=WHITE, width=2)
arr(s, 490, 480, 640, 480, color=GRN_HI, width=3)
box(s, 640, 130, 590, 110, CHIP, stroke=EDGE, radius=0.06, body="MGS (management server)\nholds the configuration of the file systems", size=17)
box(s, 640, 270, 590, 120, CHIP, stroke=EDGE, radius=0.06, body="MDS (metadata server) with MDT (metadata target)\nholds names, directories, permissions, file layout", size=17)
box(s, 640, 420, 590, 220, CHIP, stroke=GRN, radius=0.06)
label(s, 640, 428, 590, 34, "OSS (object storage server) with OSTs", size=17, bold=True, color=GRN_HI)
for i in range(4):
    box(s, 670 + i * 140, 480, 120, 70, GRN_DK, stroke=GRN, body="OST %d" % i, size=17)
label(s, 640, 570, 590, 50, "OST = object storage target: holds the contents of files", size=16, color=MUTED)
label(s, 43, 590, 450, 70, "many clients, many OSSs;\nthe number of each can grow", size=15, color=MUTED, align="left")

# 2 ------------------------------------------------------------- metadata vs data
s = d.slide().s
title(s, "A file is split in two: its record and its contents",
      "Grey and yellow: metadata on the MDT.  Green: file contents on OSTs")
box(s, 43, 120, 470, 330, CHIP, stroke=EDGE, radius=0.05)
label(s, 63, 128, 430, 34, "MDT: the record of  result.bin", size=18, bold=True, align="left")
rows = ["name and parent directory", "owner, permissions, times", "layout: which OSTs hold the contents"]
for i, r in enumerate(rows):
    box(s, 70, 180 + i * 80, 416, 62, GREY if i < 2 else YEL_DK, stroke=EDGE if i < 2 else YEL, body=r, size=16)
label(s, 640, 118, 590, 34, "OSTs: the contents, in objects", size=18, bold=True, color=GRN_HI)
for i, n in enumerate((1, 4, 7)):
    box(s, 760, 170 + i * 100, 470, 80, GRN_DK, stroke=GRN, body="OST %d: one object of result.bin" % n, size=17)
    arr(s, 486, 372, 760, 210 + i * 100, color=YEL, width=2)
label(s, 520, 130, 230, 56, "the layout points\nto the objects", size=15, color=YEL)
box(s, 43, 480, 1194, 150, CHIP, stroke=EDGE, radius=0.05,
    body="The MDS answers (from the MDT): where is this name, who may open it, which OSTs hold the contents.\nThe OSSs answer (from the OSTs): here are bytes 0..N of this object.", size=18)

# 3 ------------------------------------------------------------- striping
s = d.slide().s
title(s, "Striping: chunks of one file go round-robin to several OSTs",
      "Example: stripe count 3, stripe size 1 MiB.  Same color = same OST")
label(s, 43, 112, 400, 30, "file  result.bin", size=18, bold=True, align="left")
for i in range(9):
    box(s, 43 + i * 130, 150, 120, 70, GREY, stroke=CH[i % 3], body="chunk %d\n1 MiB" % (i + 1), size=15, sw=2.5)
for k in range(3):
    ox = 120 + k * 400
    box(s, ox, 420, 300, 130, GRN_DK, stroke=CH[k], sw=2.5)
    label(s, ox, 426, 300, 34, "OST %s" % (1, 4, 7)[k], size=18, bold=True)
    chunks = [k + 1, k + 4, k + 7]
    for j, c in enumerate(chunks):
        box(s, ox + 14 + j * 92, 475, 84, 56, GREY, stroke=CH[k], body="chunk %d" % c, size=14)
    for c in chunks:
        arr(s, 43 + (c - 1) * 130 + 60, 220, ox + 150, 420, color=CH[k], width=1.5)
label(s, 43, 590, 1194, 80, "Chunks 1, 4, 7 go to OST 1, chunks 2, 5, 8 to OST 4, chunks 3, 6, 9 to OST 7.\nThe default is 1 stripe of 1 MiB; users can change it per file, per directory, or for the whole file system.", size=16, color=MUTED)

# 4 ------------------------------------------------------------- read flow
s = d.slide().s
title(s, "Reading a file: ask the MDS once, then talk to the OSSs directly",
      "White: small requests.  Yellow: the layout.  Green: file data")
box(s, 43, 300, 210, 360, LINK_DK, stroke=LINK, body="client", size=22)
box(s, 520, 118, 300, 90, CHIP, stroke=EDGE, body="MDS + MDT", size=19)
arr(s, 253, 320, 520, 150, color=WHITE, width=2.5); badge(s, 330, 200, 1)
label(s, 360, 130, 150, 24, "open result.bin", size=14)
arr(s, 520, 185, 253, 350, color=YEL, width=2.5); badge(s, 440, 270, 2, color=YEL)
label(s, 830, 130, 400, 70, "replies with the layout:\nOST 1, OST 4, OST 7", size=15, color=YEL, align="left")
for i in range(3):
    y = 330 + i * 115
    box(s, 930, y, 300, 100, CHIP, stroke=GRN, body="OSS %d  (OST %s)" % (i + 1, (1, 4, 7)[i]), size=18)
    arr(s, 253, y + 30, 930, y + 30, color=WHITE, width=2)
    arr(s, 930, y + 75, 253, y + 75, color=GRN_HI, width=3)
badge(s, 540, 296, 3)
label(s, 580, 296, 520, 24, "read requests, sent to the three OSSs at once", size=14, align="left")
badge(s, 540, 420, 4, color=GRN_HI)
label(s, 580, 416, 520, 24, "file data comes back from each OSS", size=14, color=GRN_HI, align="left")
label(s, 270, 665, 700, 28, "The MDS is not on the data path.", size=16, color=MUTED, align="left")

# 5 ------------------------------------------------------------- DNE
s = d.slide().s
title(s, "More than one MDT: directories can live on different MDTs",
      "Color = the MDT that holds the directory.  Clients see one tree")
def node(x, y, name, k):
    box(s, x, y, 170, 56, GREY, stroke=CH[k], body=name, size=16, sw=2.5)
node(540, 120, "/", 0)
node(200, 270, "/projA", 0); node(540, 270, "/projB", 1); node(880, 270, "/projC", 2)
for x in (285, 625, 965):
    arr(s, 625, 176, x, 270, color=EDGE, width=1.75)
node(120, 420, "/projA/run1", 0); node(330, 420, "/projA/run2", 0)
node(540, 420, "/projB/data", 1); node(880, 420, "/projC/data", 2)
for a, b in ((285, 205), (285, 415), (625, 625), (965, 965)):
    arr(s, a, 326, b, 420, color=EDGE, width=1.75)
for i, nm in enumerate(("MDT 0", "MDT 1", "MDT 2")):
    box(s, 160 + i * 340, 560, 240, 70, CHIP, stroke=CH[i], body=nm, size=18, sw=2.5)
label(s, 43, 650, 1194, 30, "A directory can also be split over several MDTs (striped directory).", size=15, color=MUTED)

# 6 ------------------------------------------------------------- lock
s = d.slide().s
title(s, "Locks: the server asks a client to give up its lock",
      "Yellow: lock traffic.  Red: the request to give the lock back.  A silent client is evicted")
xs = [200, 640, 1080]
seq(s, xs, ["client A", "OSS", "client B"], colors=[LINK, GRN, LINK])
msg(s, xs[0], xs[1], 210, "write lock request", YEL); badge(s, 60, 190, 1)
msg(s, xs[1], xs[0], 270, "granted; A caches its dirty data", YEL); badge(s, 60, 250, 2)
msg(s, xs[2], xs[1], 350, "read lock request (same range)", YEL); badge(s, 1190, 330, 3)
msg(s, xs[1], xs[0], 420, "give the lock back", RED); badge(s, 60, 400, 4)
msg(s, xs[0], xs[1], 490, "write dirty data, release", YEL); badge(s, 60, 470, 5)
msg(s, xs[1], xs[2], 560, "granted to B", YEL); badge(s, 1190, 540, 6)
box(s, 700, 600, 530, 70, YEL_DK, stroke=YEL, body="If A does not answer step 4 in time,\nthe server evicts client A", size=16)

# 7 ------------------------------------------------------------- client layers
s = d.slide().s
title(s, "Inside a client: layers from the application down to the wire",
      "Blue: Lustre client software.  Yellow: LNet")
layers = [("application", "reads and writes files", CHIP, EDGE),
          ("llite", "looks like a normal file system to Linux", LINK_DK, LINK),
          ("lmv, mdc / lov, osc", "lmv and lov gather the MDTs and the stripes; mdc and osc build the requests", LINK_DK, LINK),
          ("ptlrpc", "sends requests, waits for replies, reconnects", LINK_DK, LINK),
          ("LNet", "address and path choice", YEL_DK, YEL),
          ("LND", "driver for one network type", YEL_DK, YEL),
          ("network card", "", CHIP, EDGE)]
y = 118
for nm, what, fill, st in layers:
    box(s, 43, y, 330, 66, fill, stroke=st, body=nm, size=19)
    label(s, 400, y, 800, 66, what, size=17, color=MUTED, align="left")
    y += 80
    if nm != "network card":
        arr(s, 208, y - 14, 208, y, color=WHITE, width=1.75)

# 8 ------------------------------------------------------------- RPC + bulk
s = d.slide().s
title(s, "RPC and bulk: a small request, then the data moves",
      "White: RPC.  Green: bulk data.  Dashed: the OSS asks for the data (GET).  The OSS moves the data")
for px, head in ((43, "Read"), (655, "Write")):
    box(s, px, 112, 582, 430, CHIP, stroke=EDGE, radius=0.03)
    label(s, px, 118, 582, 32, head, size=22, bold=True)
    label(s, px + 70, 156, 120, 26, "client", size=15, color=MUTED)
    label(s, px + 392, 156, 120, 26, "OSS", size=15, color=MUTED)
    vline(s, px + 130, 186, 525); vline(s, px + 452, 186, 525)
L, R = 43 + 130, 43 + 452
msg(s, L, R, 240, "1  read RPC (buffer is ready)", WHITE)
for dy in (0, 12, 24):
    arr(s, R, 330 + dy, L, 340 + dy, color=GRN_HI, width=3)
label(s, L + 10, 300, R - L - 20, 24, "2  OSS puts the data", 14, GRN_HI)
msg(s, R, L, 470, "3  reply RPC", WHITE)
L2, R2 = 655 + 130, 655 + 452
msg(s, L2, R2, 240, "1  write RPC (data is ready)", WHITE)
label(s, L2 + 10, 285, R2 - L2 - 20, 24, "2  OSS gets the data", 14, GRN_HI)
arr(s, R2, 320, L2, 320, color=GRN_HI, width=2, dashed=True)
for dy in (0, 12, 24):
    arr(s, L2, 360 + dy, R2, 370 + dy, color=GRN_HI, width=3)
msg(s, R2, L2, 470, "3  reply RPC", WHITE)
label(s, 43, 565, 1194, 60, "On the wire these are LNet messages: the OSS sends a PUT for a read and a GET for a write.", size=15, color=MUTED)

# 9 ------------------------------------------------------------- NID
s = d.slide().s
title(s, "NID: the address LNet uses", "Top: yellow is the network part, green the address part.  Bottom: yellow is tcp0, green is o2ib0")
box(s, 43, 130, 360, 90, GRN_DK, stroke=GRN, body="10.0.1.20", size=30)
label(s, 403, 130, 60, 90, "@", size=34, bold=True)
box(s, 463, 130, 200, 90, YEL_DK, stroke=YEL, body="tcp0", size=30)
label(s, 43, 225, 360, 28, "address of the network card", size=15, color=GRN_HI)
label(s, 463, 225, 240, 28, "LNet network name", size=15, color=YEL)
label(s, 740, 120, 500, 110, "= LND type + a number\ntcp0, o2ib0, o2ib1 ...", size=18, color=MUTED, align="left")
box(s, 43, 310, 1194, 330, CHIP, stroke=EDGE, radius=0.04)
label(s, 63, 318, 600, 30, "One node can have several NIDs", size=18, bold=True, align="left")
box(s, 83, 370, 260, 230, LINK_DK, stroke=LINK, body="a server\n(one machine)", size=18)
for i, (nid, c) in enumerate((("10.0.1.20@tcp0", YEL), ("192.168.5.20@o2ib0", GRN_HI), ("192.168.6.20@o2ib0", GRN_HI))):
    box(s, 520, 370 + i * 80, 400, 64, GREY, stroke=c, body=nid, size=18)
    arr(s, 343, 485, 520, 402 + i * 80, color=c, width=2)
label(s, 940, 380, 290, 200, "two networks,\nthree network cards;\nLNet picks one NID\nfor each message", size=17, color=MUTED, align="left")

# 10 ------------------------------------------------------------- LND
s = d.slide().s
title(s, "LNet and LNDs: one front, one driver per network type",
      "Yellow: LNet.  Blue: drivers (LNDs)")
box(s, 43, 130, 1194, 110, YEL_DK, stroke=YEL, body="LNet\nsends and receives messages by NID; connectionless, asynchronous", size=20)
for i, (nm, net, c) in enumerate((("ksocklnd", "TCP networks", LINK), ("o2iblnd", "InfiniBand, RoCE", LINK), ("kefalnd", "AWS EFA", LINK), ("others", "other vendors' networks", LINK))):
    x = 43 + i * 305
    arr(s, x + 140, 240, x + 140, 300, color=WHITE, width=2)
    box(s, x, 300, 280, 100, LINK_DK if c == LINK else CHIP, stroke=c, body=nm, size=22)
    arr(s, x + 140, 400, x + 140, 450, color=WHITE, width=2)
    box(s, x, 450, 280, 90, CHIP, stroke=EDGE, body=net, size=17)
label(s, 43, 580, 1194, 90, "An LND talks to its own network and checks that data was transmitted (connection oriented).\nUpper layers do not change when the network changes.", size=16, color=MUTED)

# 11 ------------------------------------------------------------- messages
s = d.slide().s
title(s, "LNet moves data with five kinds of message (four shown)",
      "White: messages.  Green: carries data.  Dashed: optional (ACK)")
for px, head in ((43, "PUT: push data to the target"), (655, "GET: pull data from the target")):
    box(s, px, 112, 582, 400, CHIP, stroke=EDGE, radius=0.03)
    label(s, px, 118, 582, 34, head, size=20, bold=True)
    label(s, px + 70, 160, 120, 26, "sender", size=15, color=MUTED)
    label(s, px + 392, 160, 120, 26, "target", size=15, color=MUTED)
    vline(s, px + 130, 190, 495); vline(s, px + 452, 190, 495)
msg(s, 173, 495, 270, "PUT  (carries the data)", GRN_HI)
msg(s, 495, 173, 400, "ACK  (if the sender asked)", WHITE, dashed=True)
msg(s, 785, 1107, 270, "GET  (names what is wanted)", WHITE)
msg(s, 1107, 785, 400, "REPLY  (carries the data)", GRN_HI)
box(s, 43, 540, 1194, 110, CHIP, stroke=EDGE, radius=0.05,
    body="HELLO, the fifth kind, is used by the TCP driver when a connection starts.\nLustre builds RPC and bulk transfer out of these messages.", size=17)

# 12 ------------------------------------------------------------- multi-rail + health
s = d.slide().s
title(s, "Multi-Rail and health: LNet picks a path for every message",
      "Thick line: the path LNet picked.  Thin grey lines: other candidates.  Hatched bars: health")
box(s, 43, 130, 250, 300, LINK_DK, stroke=LINK, body="client", size=20)
box(s, 987, 130, 250, 300, GRN_DK, stroke=GRN, body="server", size=20)
for i, nm in enumerate(("NID a", "NID b")):
    box(s, 300, 180 + i * 130, 120, 60, GREY, stroke=LINK, body=nm, size=16)
    box(s, 860, 180 + i * 130, 120, 60, GREY, stroke=GRN, body="NID " + "cd"[i], size=16)
for yy in (210, 340):
    for y2 in (210, 340):
        hi = (yy, y2) == (210, 210)
        arr(s, 420, yy, 860, y2, color=GRN_HI if hi else EDGE, width=3 if hi else 1.5)
label(s, 440, 125, 400, 30, "every pair is a possible path", size=15, color=MUTED)
label(s, 560, 168, 330, 26, "thick: picked for this message", size=14, color=GRN_HI)
box(s, 43, 460, 1194, 210, CHIP, stroke=EDGE, radius=0.04)
label(s, 63, 466, 700, 30, "health of a NID: a number from 0 to 1000", size=17, bold=True, align="left")
for i, (v, c, cap) in enumerate(((1000, GRN_HI, "at the start"), (900, YEL, "after a failure (it is lowered by 100)"), (902, YEL, "each successful ping adds 1 (900, 901, 902 ...)"))):
    y = 510 + i * 50
    box(s, 70, y, 700 * v / 1000, 36, GRN_DK if c == GRN_HI else YEL_DK, stroke=c, body="", size=14)
    label(s, 70, y, 700 * v / 1000, 36, str(v), size=16, bold=True)
    label(s, 790, y, 440, 36, cap, size=15, color=c, align="left")

# 13 ------------------------------------------------------------- router
s = d.slide().s
title(s, "LNet router: carry messages from one LNet network to another",
      "A router has a NID on each network")
box(s, 43, 150, 330, 380, LINK_DK, stroke=LINK, radius=0.05)
label(s, 43, 156, 330, 34, "network tcp0", size=19, bold=True)
box(s, 83, 220, 250, 90, CHIP, stroke=LINK, body="client\n10.0.1.30@tcp0", size=16)
box(s, 83, 360, 250, 90, CHIP, stroke=LINK, body="client\n10.0.1.31@tcp0", size=16)
box(s, 907, 150, 330, 380, GRN_DK, stroke=GRN, radius=0.05)
label(s, 907, 156, 330, 34, "network o2ib0", size=19, bold=True)
box(s, 947, 220, 250, 90, CHIP, stroke=GRN, body="OSS\n192.168.5.20@o2ib0", size=16)
box(s, 947, 360, 250, 90, CHIP, stroke=GRN, body="MDS\n192.168.5.10@o2ib0", size=16)
box(s, 490, 230, 300, 220, YEL_DK, stroke=YEL, body="LNet router\n10.0.1.5@tcp0\n192.168.5.5@o2ib0", size=18)
arr(s, 333, 265, 490, 300, color=WHITE, width=2.5); arr(s, 790, 300, 947, 265, color=WHITE, width=2.5)
arr(s, 333, 405, 490, 380, color=WHITE, width=2.5); arr(s, 790, 380, 947, 405, color=WHITE, width=2.5)
label(s, 43, 560, 1194, 100, "A client on tcp0 sends to a NID on o2ib0; the router forwards it.\nLNet routing is not the same as IP routing.", size=17, color=MUTED)

# 14 ------------------------------------------------------------- import states
s = d.slide().s
title(s, "A client's link to one server: the states of an import",
      "Green: working.  Yellow: trouble and recovery.  Red: the server had forgotten the client")
def seg(x1, y1, x2, y2, color, w=2.5, dashed=False):
    ln = s.shapes.add_connector(1, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
    ln.line.color.rgb = color
    ln.line.width = sh.Pt(w)
    if dashed:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
box(s, 60, 170, 200, 80, GRN_DK, stroke=GRN_HI, body="FULL", size=21, sw=2.5)
box(s, 360, 170, 200, 80, YEL_DK, stroke=YEL, body="DISCON", size=21)
box(s, 660, 170, 200, 80, YEL_DK, stroke=YEL, body="CONNECTING", size=21)
box(s, 960, 170, 200, 80, YEL_DK, stroke=YEL, body="RECOVER", size=21)
arr(s, 260, 210, 360, 210, color=YEL, width=2.5); label(s, 230, 255, 160, 44, "request\ntimes out", 13, YEL)
arr(s, 560, 210, 660, 210, color=YEL, width=2.5); label(s, 530, 255, 160, 44, "try to\nreconnect", 13, YEL)
arr(s, 860, 210, 960, 210, color=YEL, width=2.5); label(s, 850, 255, 140, 44, "server\nremembers us", 13, YEL)
seg(1060, 170, 1060, 130, GRN_HI); seg(1060, 130, 160, 130, GRN_HI); arr(s, 160, 130, 160, 170, color=GRN_HI, width=2.5)
label(s, 420, 98, 500, 28, "recovery finished: back to FULL", 14, GRN_HI)
box(s, 460, 400, 200, 80, RGBColor(90, 30, 28), stroke=RED, body="EVICTED", size=21)
box(s, 800, 400, 320, 80, YEL_DK, stroke=YEL, body="REPLAY, REPLAY_LOCKS, REPLAY_WAIT", size=15)
arr(s, 740, 250, 590, 400, color=RED, width=2.5, dashed=True); label(s, 320, 320, 240, 50, "the server forgot\nthis client", 13, RED, align="right")
arr(s, 800, 250, 880, 400, color=YEL, width=2.5); label(s, 830, 487, 260, 28, "server is in recovery", 14, YEL)
arr(s, 1010, 400, 1070, 250, color=YEL, width=2.5); label(s, 1090, 335, 150, 50, "requests, then\nlocks replayed", 13, YEL, align="left")
seg(560, 480, 560, 530, RED, 2.5, True); seg(560, 530, 1230, 530, RED, 2.5, True); seg(1230, 530, 1230, 210, RED, 2.5, True); arr(s, 1230, 210, 1160, 210, color=RED, width=2.5, dashed=True)
label(s, 600, 535, 520, 28, "locks and cache are invalidated, then recovery", 13, RED)
box(s, 43, 585, 1194, 100, CHIP, stroke=EDGE, radius=0.05,
    body="An import is one client's link to one target (an MDT or an OST).\nRequests can wait while it reconnects; after an eviction, operations in progress fail.", size=17)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
