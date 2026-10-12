"""gen_gdr_gifs.py — GPUDirect RDMA 入門の GIF 3 本。

    OUT_DIR=<出力先> /usr/bin/python3 gen_gdr_gifs.py

1. rdma-path.gif: Buffer -> NIC -> NIC -> Buffer。送り手の NIC が DMA で読み、受け手の NIC が DMA で書く。受け手の CPU は関わらない
2. tcp-vs-rdma.gif: TCP/IP はカーネルでコピーと処理と割り込みが入り、RDMA はアプリのバッファから NIC へ直接
3. work-request.gif: ワークリクエストをキューに書く、ドアベル、NIC が DMA で読んで送る、完了キュー、poll
図の文字は英語。色: 緑 = アプリとバッファ、灰 = カーネル、黄 = NIC とネットワーク、青 = CPU の処理、桃 = 運ぶデータ。
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, R, ease, lerp, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OW, OH = 960, 540
FPS = 12
GRN, GRN_DK = (36, 160, 70), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL, YEL_DK = (251, 211, 50), (80, 66, 14)
PNK = (255, 120, 160)
CHIP, EDGE = (22, 26, 30), (70, 74, 80)


def canvas():
    img = Image.new("RGB", (int(OW * R), int(OH * R)), BG)
    return img, ImageDraw.Draw(img)


def P(x, y):
    return (x * R, y * R)


def rbox(g, x, y, w, h, fill, outline, width=2, radius=10):
    g.rounded_rectangle([*P(x, y), *P(x + w, y + h)], radius=radius * R, fill=fill,
                        outline=outline, width=int(width * R))


def text(g, x, y, t, size=16, col=TX, anchor="mm"):
    g.text(P(x, y), t, font=s.font(size), fill=col, anchor=anchor)


def chip(g, x, y, w, h, label_, col, dk, lit=0.0):
    rbox(g, x, y, w, h, mix(CHIP, dk, 0.35 + 0.65 * lit), col)
    text(g, x + w / 2, y + 16, label_, 14, TX)


def packet(g, x, y, col=PNK, tag=None, w=34, h=20):
    g.rounded_rectangle([*P(x - w / 2, y - h / 2), *P(x + w / 2, y + h / 2)], radius=4 * R, fill=col,
                        outline=BG, width=int(2 * R))
    if tag:
        text(g, x, y, tag, 11, BG)


def along(pts, u):
    """折れ線 pts の上を u (0..1) だけ進んだ点"""
    if u <= 0:
        return pts[0]
    if u >= 1:
        return pts[-1]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = u * sum(seg)
    for i, L in enumerate(seg):
        if d <= L:
            t = d / L
            return (lerp(pts[i][0], pts[i + 1][0], t), lerp(pts[i][1], pts[i + 1][1], t))
        d -= L
    return pts[-1]


def legend(g, txt):
    text(g, 32, 92, txt, 13, MUTED, "lm")


def arrow_v(g, x, y0, y1, col=EDGE):
    g.line([*P(x, y0), *P(x, y1 - 6)], fill=col, width=int(2 * R))
    g.polygon([P(x - 5, y1 - 8), P(x + 5, y1 - 8), P(x, y1)], fill=col)


def arrow_h(g, x0, x1, y, col=EDGE):
    g.line([*P(x0, y), *P(x1 - 6, y)], fill=col, width=int(2 * R))
    g.polygon([P(x1 - 8, y - 5), P(x1 - 8, y + 5), P(x1, y)], fill=col)


def clamp(u):
    return max(0.0, min(1.0, u))


def save(frames, name, stills):
    pal = frames[len(frames) // 2].convert("P", palette=Image.ADAPTIVE, colors=64)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(OUT_DIR, name)
    out[0].save(path, save_all=True, append_images=out[1:], duration=int(1000 / FPS), loop=0,
                optimize=True)
    for i, k in enumerate(stills):
        frames[k].save(os.path.join(OUT_DIR, f"{name[:-4]}-still{i}.png"))
    print("wrote", path, len(frames), "frames", round(os.path.getsize(path) / 1e6, 2), "MB")



def legend(g, txt):
    text(g, 32, 92, txt, 13, MUTED, "lm")


def head(g, h, sub, leg):
    text(g, 32, 34, h, 26, TX, "lm")
    text(g, 32, 68, sub, 17, MUTED, "lm")
    legend(g, leg)


def phase(t, phases):
    for end, h, sb in phases:
        if t < end:
            return h, sb
    return phases[-1][1:]



PNK_DK = (80, 30, 46)

# ---------------------------------------------------------------- 1. RDMA path
LEG1 = "Green: app and registered buffer.  Yellow: NIC and network.  Grey: CPU not involved.  Pink: data"


def path_frame(t):
    img, g = canvas()
    ph = [(1.6, "1. NIC A reads the buffer", "DMA: the NIC reads memory itself"),
          (3.6, "2. Over the network", "no kernel on the data path"),
          (5.2, "3. NIC B writes the buffer", "DMA into the registered buffer"),
          (7.0, "4. CPU B was not involved", "one-sided RDMA Write")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG1)
    for x, name in ((40, "Machine A (sender)"), (520, "Machine B (receiver)")):
        rbox(g, x, 120, 400, 340, CHIP, EDGE)
        text(g, x + 200, 140, name, 15, TX)
    # A
    rbox(g, 70, 170, 160, 50, GRN_DK, GRN); text(g, 150, 195, "app", 14, TX)
    rbox(g, 70, 250, 160, 60, GRN_DK, GRN); text(g, 150, 280, "registered buffer", 13, TX)
    rbox(g, 260, 340, 150, 60, YEL_DK, YEL); text(g, 335, 370, "NIC", 15, TX)
    # B
    rbox(g, 550, 340, 150, 60, YEL_DK, YEL); text(g, 625, 370, "NIC", 15, TX)
    rbox(g, 730, 250, 180, 60, GRN_DK, GRN); text(g, 820, 280, "registered buffer", 13, TX)
    rbox(g, 730, 170, 180, 50, CHIP, EDGE); text(g, 820, 195, "CPU B: idle", 13, MUTED)
    g.line([*P(410, 370), *P(550, 370)], fill=YEL, width=int(3 * R))
    text(g, 480, 390, "network", 12, YEL)
    pts = [(150, 280), (335, 370), (625, 370), (820, 280)]
    if t < 1.6:
        u = ease(clamp(t / 1.4)); a, b = pts[0], pts[1]
    elif t < 3.6:
        u = ease(clamp((t - 1.6) / 1.8)); a, b = pts[1], pts[2]
    elif t < 5.2:
        u = ease(clamp((t - 3.6) / 1.4)); a, b = pts[2], pts[3]
    else:
        u = 1.0; a, b = pts[3], pts[3]
    packet(g, lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 30, tag="data", w=50, h=22)
    text(g, 480, 500, "conceptual: RDMA Write, Buffer -> NIC -> NIC -> Buffer", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


# ---------------------------------------------------------------- 2. TCP vs RDMA
LEG2 = "Green: app.  Grey: OS kernel.  Yellow: NIC.  Pink: data"


def tcp_frame(t):
    img, g = canvas()
    ph = [(3.0, "Same message, two paths", "TCP/IP goes through the kernel twice"),
          (6.5, "RDMA skips the kernel", "no copy, no per-packet kernel work")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG2)
    lanes = [(150, "TCP/IP", True), (360, "RDMA", False)]
    for y, name, tcp in lanes:
        text(g, 40, y + 25, name, 16, TX, "lm")
        xs = [120, 230, 380, 530, 680, 830] if tcp else [120, 380, 530, 830]
        labs = ["app A", "kernel", "NIC", "NIC", "kernel", "app B"] if tcp else ["app A", "NIC", "NIC", "app B"]
        for x, lb in zip(xs, labs):
            col = GRN if "app" in lb else (EDGE if lb == "kernel" else YEL)
            dk = GRN_DK if "app" in lb else (CHIP if lb == "kernel" else YEL_DK)
            rbox(g, x, y, 100, 50, dk, col); text(g, x + 50, y + 25, lb, 14, TX)
        for k in range(len(xs) - 1):
            g.line([*P(xs[k] + 100, y + 25), *P(xs[k + 1], y + 25)], fill=EDGE, width=int(2 * R))
        if tcp:
            text(g, 280, y + 70, "copy + TCP/IP + interrupt", 12, MUTED)
            text(g, 730, y + 70, "interrupt + TCP/IP + copy", 12, MUTED)
        dur = 6.0 if tcp else 2.6
        u = ease(clamp((t - 0.3) / dur))
        pts = [(x + 50, y + 25) for x in xs]
        seg = u * (len(pts) - 1); k = min(int(seg), len(pts) - 2); f = seg - k
        packet(g, lerp(pts[k][0], pts[k + 1][0], f), lerp(pts[k][1], pts[k + 1][1], f) - 34, tag="data", w=50, h=22)
        if u >= 1:
            text(g, 880, y + 70, "arrived", 13, YEL)
    text(g, 480, 500, "conceptual: speeds are not to scale", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


# ---------------------------------------------------------------- 3. work request
LEG3 = "Blue: CPU work.  Green: memory.  Yellow: NIC.  Pink: what moves"


def wr_frame(t):
    img, g = canvas()
    ph = [(1.6, "1. App writes a work request", "into the send queue in memory"),
          (3.0, "2. App rings the doorbell", "an MMIO write, not a system call"),
          (4.8, "3. NIC reads the request and the buffer", "DMA, then sends packets"),
          (6.4, "4. NIC posts a completion", "into the completion queue (CQ)"),
          (8.0, "5. App polls the CQ", "reads the completion in user space")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG3)
    rbox(g, 60, 140, 220, 70, BLU_DK, BLU); text(g, 170, 175, "app (CPU)", 15, TX)
    rbox(g, 380, 130, 220, 60, GRN_DK, GRN); text(g, 490, 160, "send queue (SQ)", 14, TX)
    rbox(g, 380, 220, 220, 60, GRN_DK, GRN); text(g, 490, 250, "data buffer", 14, TX)
    rbox(g, 380, 310, 220, 60, GRN_DK, GRN); text(g, 490, 340, "completion queue (CQ)", 14, TX)
    rbox(g, 680, 200, 200, 90, YEL_DK, YEL); text(g, 780, 230, "NIC", 16, TX)
    rbox(g, 700, 255, 160, 26, CHIP, YEL if 1.6 <= t < 3.0 else EDGE, width=3 if 1.6 <= t < 3.0 else 2)
    text(g, 780, 268, "doorbell register", 11, TX)
    g.line([*P(880, 245), *P(940, 245)], fill=YEL, width=int(3 * R)); text(g, 910, 225, "network", 12, YEL)
    if t < 1.6:
        u = ease(clamp(t / 1.4)); packet(g, lerp(280, 380, u), lerp(175, 160, u), tag="WR", w=40)
    elif t < 3.0:
        u = ease(clamp((t - 1.6) / 1.2)); px, py = along([(280, 175), (330, 112), (640, 112), (780, 255)], u); packet(g, px, py, col=YEL, tag="ring", w=44)
    elif t < 4.8:
        u = ease(clamp((t - 3.0) / 1.6))
        packet(g, lerp(600, 680, u), lerp(160, 220, u), tag="WR", w=40)
        packet(g, lerp(600, 680, u), lerp(250, 260, u), tag="data", w=46)
    elif t < 6.4:
        u = ease(clamp((t - 4.8) / 1.4)); packet(g, lerp(680, 600, u), lerp(280, 340, u), tag="done", w=46)
    else:
        u = ease(clamp((t - 6.4) / 1.4)); packet(g, lerp(380, 280, u), lerp(340, 190, u), tag="done", w=46)
        text(g, 170, 230, "ibv_poll_cq()", 13, BLU)
    text(g, 480, 440, "no system call in any of these steps", 15, MUTED)
    text(g, 480, 500, "conceptual: verbs posting model", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


for name, fn, dur, stills in [("rdma-path.gif", path_frame, 7.0, [10, 30, 50, 75]),
                              ("tcp-vs-rdma.gif", tcp_frame, 7.0, [20, 50, 80]),
                              ("work-request.gif", wr_frame, 8.0, [10, 28, 46, 66, 90])]:
    save([fn(i / FPS) for i in range(int(dur * FPS))], name, stills)
