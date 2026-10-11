"""gen_gin_gifs.py — NCCL Roadmap 記事の GIN の GIF 2 本。

    OUT_DIR=<出力先> /usr/bin/python3 gen_gin_gifs.py

1. gin-paths.gif: 1 回の put が NIC に届くまでの経路を、従来の NCCL、GIN Proxy、GIN GDAKI で並べる
2. gin-put-signal.gif: put に signal を付けて送り、受け手が waitSignal で到着を知り、送り手が counter で
   送信元のバッファを再利用してよいと知る流れ（arXiv:2511.15076 の Listing 2 の ring exchange を 2 rank で描く）
図の文字は英語。色: 緑 = GPU、青 = CPU、黄 = NIC とネットワーク、桃 = データ。
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


# ---------------------------------------------------------------- 1. three paths to the NIC
LANES = [
    (40, "Host-initiated (classic NCCL)", "CPU drives the network"),
    (340, "GIN Proxy backend", "GPU writes a 64-byte descriptor"),
    (640, "GIN GDAKI backend", "GPU rings the NIC doorbell"),
]
GPU_Y, CPU_Y, NIC_Y, NET_Y = 140, 250, 360, 460


def lane_boxes(g, x, kind, t):
    w = 280
    text(g, x + w / 2, 112, LANES[kind][1], 16, TX)
    gpu_lit = 1.0 if t < 1.6 else 0.0
    cpu_lit = 1.0 if (kind < 2 and 1.6 <= t < 4.0) else 0.0
    nic_lit = 1.0 if t >= 4.0 else 0.0
    chip(g, x + 20, GPU_Y, w - 40, 56, "GPU kernel", GRN, GRN_DK, gpu_lit)
    if kind == 0:
        chip(g, x + 20, CPU_Y, w - 40, 56, "CPU proxy thread", BLU, BLU_DK, cpu_lit)
    elif kind == 1:
        chip(g, x + 20, CPU_Y, 110, 56, "queue", BLU, BLU_DK, cpu_lit)
        text(g, x + 75, CPU_Y + 40, "64B descriptor", 10, MUTED)
        chip(g, x + 150, CPU_Y, 110, 56, "CPU proxy", BLU, BLU_DK, cpu_lit)
    else:
        rbox(g, x + 150, CPU_Y, 110, 56, CHIP, EDGE)
        text(g, x + 205, CPU_Y + 28, "CPU: off path", 13, MUTED)
    chip(g, x + 20, NIC_Y, w - 40, 56, "NIC", YEL, YEL_DK, nic_lit)
    if kind == 2:
        text(g, x + 72, CPU_Y + 28, "doorbell", 12, MUTED, "rm")
    rbox(g, x + 20, NET_Y, w - 40, 40, CHIP, YEL)
    text(g, x + 225, NET_Y + 20, "network", 13, MUTED)


def lane_route(x, kind):
    cx = x + 140
    if kind == 0:
        return [(cx, GPU_Y + 40), (cx, CPU_Y + 40), (cx, NIC_Y + 40), (cx, NET_Y + 20)]
    if kind == 1:
        return [(cx, GPU_Y + 40), (x + 75, CPU_Y + 40), (x + 205, CPU_Y + 40), (cx, NIC_Y + 40),
                (cx, NET_Y + 20)]
    return [(x + 80, GPU_Y + 40), (x + 80, NIC_Y + 40), (x + 80, NET_Y + 20)]


def paths_frame(t):
    img, g = canvas()
    if t < 1.6:
        head, sub = "A put starts in the GPU", "same request, three paths"
    elif t < 4.0:
        head, sub = "Who hands the operation to the NIC", "CPU proxy, queue + proxy, or the GPU itself"
    else:
        head, sub = "NIC sends it", "RDMA goes out on the network"
    text(g, 32, 34, head, 26, TX, "lm")
    text(g, 32, 68, sub, 17, MUTED, "lm")
    legend(g, "Green: GPU.  Blue: CPU on the path.  Yellow: NIC / network.  Pink tag: what is handed over")
    for kind, (x, _, _) in enumerate(LANES):
        lane_boxes(g, x, kind, t)
        route = lane_route(x, kind)
        if kind == 0:
            arrow_v(g, x + 140, GPU_Y + 56, CPU_Y); arrow_v(g, x + 140, CPU_Y + 56, NIC_Y)
        elif kind == 1:
            arrow_v(g, x + 75, GPU_Y + 56, CPU_Y); arrow_h(g, x + 130, x + 150, CPU_Y + 28)
            arrow_v(g, x + 205, CPU_Y + 56, NIC_Y)
        else:
            arrow_v(g, x + 80, GPU_Y + 56, NIC_Y)
        arrow_v(g, x + 140 if kind != 2 else x + 80, NIC_Y + 56, NET_Y, col=YEL)
        speed = [5.0, 5.0, 3.0][kind]
        u = ease(clamp((t - 0.8) / speed))
        px, py = along(route, u)
        tag = ["op", "64B", "WQE"][kind]
        if py >= NIC_Y + 30:
            tag = "RDMA"
        packet(g, px, py, tag=tag, w=44)
    text(g, 480, 520, "conceptual: who hands the operation to the NIC", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


frames = [paths_frame(i / FPS) for i in range(int(8.0 * FPS))]
save(frames, "gin-paths.gif", [10, 40, 80])


# ---------------------------------------------------------------- 2. put with signal, counter
def ps_frame(t):
    img, g = canvas()
    phases = [(1.4, "1. put with SignalInc", "rank 0 writes into rank 1's window"),
              (3.4, "2. data and signal arrive", "signal done: earlier puts are visible"),
              (7.0, "3. two completions, no fixed order", "signal: remote (rank 1).  counter: local (rank 0)"),
              (8.6, "4. resetSignal", "ready for the next round")]
    head, sub = phases[-1][1:]
    for end, h, sb in phases:
        if t < end:
            head, sub = h, sb
            break
    text(g, 32, 34, head, 26, TX, "lm")
    text(g, 32, 68, sub, 17, MUTED, "lm")
    legend(g, "Green: GPU.  Yellow border: value changed.  Grey: unchanged.  Pink tag: data written by put")
    for r, x in enumerate((60, 520)):
        rbox(g, x, 120, 380, 330, CHIP, GRN)
        text(g, x + 190, 140, f"rank {r} (GPU)", 16, GRN)
        rbox(g, x + 20, 170, 200, 70, GRN_DK, GRN)
        text(g, x + 120, 190, "send window" if r == 0 else "recv window", 14, TX)
        # signal and counter
    # values
    sig = 1 if 3.0 <= t < 7.6 else 0
    cnt = 1 if t >= 3.4 else 0
    for r, x in enumerate((60, 520)):
        hot_s = r == 1 and sig
        hot_c = r == 0 and cnt
        rbox(g, x + 240, 170, 120, 70, CHIP, YEL if hot_s else EDGE, width=4 if hot_s else 2)
        text(g, x + 300, 186, "signal 0" + ("  updated" if hot_s else ""), 12, MUTED)
        rbox(g, x + 240, 260, 120, 70, CHIP, YEL if hot_c else EDGE, width=4 if hot_c else 2)
        text(g, x + 300, 276, "counter 0" + ("  updated" if hot_c else ""), 12, MUTED)
    text(g, 820, 218, str(sig), 22, YEL if sig else TX)
    text(g, 360, 308, str(cnt), 22, YEL if cnt else TX)
    text(g, 820, 308, "0", 22, TX)
    text(g, 360, 218, "0", 22, TX)
    # data packet: send window -> recv window
    if t < 1.4:
        packet(g, 180, 226, tag="data", w=60, h=24)
    elif t < 3.0:
        u = ease(clamp((t - 1.4) / 1.4))
        x = lerp(180, 640, u)
        y = lerp(205, 226, u) - math.sin(math.pi * u) * 70
        packet(g, x, y, tag="data", w=60, h=24)
    else:
        packet(g, 640, 226, tag="data", w=60, h=24)
    # signal increment travelling just after the data
    if 2.2 <= t < 3.0:
        u = ease(clamp((t - 2.2) / 0.8))
        x = lerp(440, 800, u)
        packet(g, x, 255 - math.sin(math.pi * u) * 20, col=YEL, tag="+1", w=34)
    # waitSignal
    if 3.4 <= t < 7.0:
        rbox(g, 540, 360, 340, 60, GRN_DK, GRN)
        text(g, 710, 390, "waitSignal(0, 1) returns", 15, TX)
        rbox(g, 80, 360, 340, 60, GRN_DK, GRN)
        text(g, 250, 390, "readCounter(0) = 1", 15, TX)
        text(g, 480, 470, "completion order: unspecified", 14, YEL)
    if 7.0 <= t:
        rbox(g, 540, 360, 340, 60, CHIP, EDGE)
        text(g, 710, 390, "resetSignal(0)", 15, TX)
    text(g, 480, 500, "adapted from Listing 2 (arXiv:2511.15076): rank 0 -> rank 1 only, counter added", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


frames = [ps_frame(i / FPS) for i in range(int(8.6 * FPS))]
save(frames, "gin-put-signal.gif", [8, 30, 60, 98])
