"""gen_pgas_gifs.py — PGAS と BAR1 の記事の GIF 2 本。

    OUT_DIR=<出力先> /usr/bin/python3 gen_pgas_gifs.py

1. peer-map.gif: PE 0 のアドレス空間に、相手 3 つのヒープが 256 GiB おきに写し込まれ、put がただの書き込みになる（g7.48xlarge の実測の値）
2. remote-put.gif: 直接の道を切ると相手のアドレスは空（NULL）になり、put は CPU の代理役と NIC を通り、BAR1 から相手の GPU メモリに届く
図の文字は英語。色: 緑 = GPU メモリ、青 = CPU の代理役、黄 = NIC、桃 = 写し込みと BAR1、灰 = 使えないもの。
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


# ---------------------------------------------------------------- 1. peer map
LEG1 = "Green: GPU memory.  Pink: mapped peer heap.  Yellow: the put"
SLOTS = [("0x10050003600", "own heap (GPU 0)"), ("0x14050003600", "PE 1 heap (GPU 1)"),
         ("0x18050003600", "PE 2 heap (GPU 2)"), ("0x1c050003600", "PE 3 heap (GPU 3)")]


def map_frame(t):
    img, g = canvas()
    ph = [(2.0, "1. PE 0's address space", "its own heap first"),
          (5.0, "2. Peer heaps are mapped in", "one 256 GiB slot per peer"),
          (7.5, "3. A put to PE 1 is a plain store", "the address points into GPU 1's memory"),
          (9.0, "4. GPU 1's a now holds the value", "no NIC, no CPU on the path")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG1)
    text(g, 40, 128, "PE 0 virtual addresses", 14, TX, "lm")
    n_on = 1 if t < 2.0 else min(4, 1 + int((t - 2.0) / 0.9) + 1)
    for k, (addr, lab) in enumerate(SLOTS):
        y = 150 + k * 78
        on = k < n_on
        own = k == 0
        rbox(g, 40, y, 440, 64, GRN_DK if own else (PNK_DK if on else CHIP), GRN if own else (PNK if on else EDGE))
        if on:
            text(g, 60, y + 22, lab, 14, TX, "lm")
            text(g, 60, y + 44, "a = " + addr, 13, MUTED, "lm")
    for k in range(4):
        rbox(g, 640, 150 + k * 78, 260, 64, GRN_DK, GRN)
        text(g, 770, 182 + k * 78, f"GPU {k} memory", 14, TX)
        if 1 <= k < n_on:
            g.line([*P(480, 182 + k * 78), *P(640, 182 + k * 78)], fill=PNK, width=int(2 * R))
    text(g, 560, 128, "PCIe P2P", 12, MUTED)
    if t >= 5.0:
        u = ease(clamp((t - 5.0) / 2.0))
        packet(g, lerp(380, 760, u), lerp(260, 250, u), col=YEL, tag="put 0", w=56)
    if t >= 7.5:
        rbox(g, 700, 240, 140, 30, YEL_DK, YEL)
        text(g, 770, 255, "a[0] = 0", 13, TX)
    text(g, 480, 500, "measured on g7.48xlarge, NVSHMEM 3.8.0, 4 PEs; slot = 256 GiB", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


# ---------------------------------------------------------------- 2. remote put
LEG2 = "Green: GPU.  Blue: CPU proxy.  Yellow: NIC.  Pink: BAR1.  Grey: not available"


def remote_frame(t):
    img, g = canvas()
    ph = [(1.8, "1. Direct path is off", "the peer's address comes back empty (NULL)"),
          (3.6, "2. GPU 4 hands the put to a CPU proxy", "a request in a queue"),
          (5.4, "3. The proxy asks the NIC to send", "libfabric, EFA"),
          (7.4, "4. The NIC writes through BAR1", "into GPU 5's memory (path from driver source)"),
          (9.0, "5. PE 1 received 0", "the same put, a different road")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG2)
    rbox(g, 40, 140, 240, 90, GRN_DK, GRN); text(g, 160, 170, "GPU 4 (PE 0)", 15, TX); text(g, 160, 200, "put 0 to PE 1", 13, MUTED)
    rbox(g, 680, 140, 240, 90, GRN_DK, GRN); text(g, 800, 170, "GPU 5 (PE 1)", 15, TX)
    rbox(g, 330, 160, 300, 50, CHIP, EDGE); text(g, 480, 185, "direct: address = NULL", 13, MUTED)
    g.line([*P(280, 185), *P(330, 185)], fill=EDGE, width=int(2 * R)); g.line([*P(630, 185), *P(680, 185)], fill=EDGE, width=int(2 * R))
    rbox(g, 40, 300, 240, 70, BLU_DK, BLU); text(g, 160, 335, "CPU proxy thread", 14, TX)
    rbox(g, 360, 300, 240, 70, YEL_DK, YEL); text(g, 480, 335, "NIC (EFA)", 15, TX)
    rbox(g, 680, 300, 240, 70, PNK_DK, PNK); text(g, 800, 335, "GPU 5 BAR1", 15, TX)
    pts = [(160, 230), (160, 300), (280, 335), (360, 335), (600, 335), (680, 335), (800, 300), (800, 230)]
    if t >= 1.8:
        u = clamp((t - 1.8) / 6.0)
        px, py = along(pts, ease(u))
        packet(g, px, py, col=YEL, tag="put", w=44)
    if t >= 7.4:
        rbox(g, 730, 205, 140, 24, YEL_DK, YEL); text(g, 800, 217, "a[0] = 0", 12, TX)
    text(g, 480, 440, "one g7.48xlarge, P2P disabled, NVSHMEM libfabric transport over EFA", 14, MUTED)
    text(g, 480, 500, "measured: EFA selected, both PEs got the expected value", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


for name, fn, dur, stills in [("peer-map.gif", map_frame, 9.0, [12, 40, 70, 100]),
                              ("remote-put.gif", remote_frame, 9.0, [12, 30, 52, 76, 100])]:
    save([fn(i / FPS) for i in range(int(dur * FPS))], name, stills)
