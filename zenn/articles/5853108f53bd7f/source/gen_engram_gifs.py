"""gen_engram_gifs.py — Engram 記事の GIF 3 本。

    OUT_DIR=<出力先> /usr/bin/python3 gen_engram_gifs.py

1. engram-lookup.gif: 位置 t で終わる 2/3/4-gram を取り、8 個のハッシュで 24 行を引き、ゲートを通して残差に足す
2. engram-prefetch.gif: 行の番号は入力のトークンだけで決まるので、前の層を計算している間に行を取りに行ける
3. engram-get.gif: DeepEP の Engram。番号から持ち主のランクと行を出し、get で読み、相手ごとに flush_async し、別のカーネルで wait する
図の文字は英語。色: 緑 = GPU の計算、桃 = 番号（アドレス）、黄 = 表の行とメモリ、灰 = 何もしていない。
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


# ---------------------------------------------------------------- 1. lookup
TOK = ["the", "cat", "sat", "on"]
NG = [(2, "sat on"), (3, "cat sat on"), (4, "the cat sat on")]
LEG1 = "Green: GPU compute.  Pink: n-gram and its row ids.  Yellow: table rows"


def lookup_frame(t):
    img, g = canvas()
    ph = [(1.5, "1. N-grams ending at t", "2-, 3- and 4-grams of normalized ids"),
          (3.5, "2. Hash each n-gram 8 ways", "8 heads per order: 3 x 8 = 24 row ids"),
          (5.3, "3. Read 24 rows", "one row per (order, head)"),
          (7.0, "4. Gate with the hidden state", "how well the rows match h_t"),
          (8.8, "5. Add to the residual", "h_t + gate · value")]
    h, sb = phase(t, ph)
    head(g, h, sb.replace(" x ", " × "), LEG1)
    # tokens
    for i, w in enumerate(TOK):
        x = 120 + i * 92
        lit = i == 3
        rbox(g, x, 120, 80, 40, GRN_DK if lit else CHIP, GRN if lit else EDGE, width=3 if lit else 2)
        text(g, x + 40, 140, w, 15, TX)
    text(g, 120 + 3 * 92 + 40, 172, "position t", 12, MUTED)
    # n-gram brackets
    show_n = 3 if t >= 1.5 else min(3, int(t / 0.5) + 1)
    for k in range(show_n):
        n, lab = NG[k]
        x0 = 120 + (4 - n) * 92
        y = 192 + k * 34
        g.line([*P(x0, y), *P(120 + 3 * 92 + 80, y)], fill=PNK, width=int(3 * R))
        text(g, x0 - 8, y, f"{n}-gram", 12, PNK, "rm")
    # hash heads -> 24 row ids
    if t >= 1.5:
        u = clamp((t - 1.5) / 1.6)
        n_lit = int(24 * u + 0.999)
        for j in range(24):
            k, hh = divmod(j, 8)
            x = 520 + hh * 50
            y = 120 + k * 46
            on = j < n_lit
            rbox(g, x, y, 42, 34, mix(CHIP, PNK_DK, 0.9) if on else CHIP, PNK if on else EDGE)
            if on:
                text(g, x + 21, y + 17, f"h{hh}", 11, TX)
        for k in range(3):
            text(g, 512, 137 + k * 46, f"n={k + 2}", 12, PNK, "rm")
    # table with lit rows
    tx, ty, tw, th = 520, 280, 400, 120
    rbox(g, tx, ty, tw, th, CHIP, YEL)
    text(g, tx + tw / 2, ty - 12, "Engram table: one prime-sized range per (order, head)", 12, MUTED)
    for k in range(1, 3):
        g.line([*P(tx, ty + k * 40), *P(tx + tw, ty + k * 40)], fill=EDGE, width=int(1 * R))
    for c in range(1, 8):
        g.line([*P(tx + 50 * c, ty), *P(tx + 50 * c, ty + th)], fill=EDGE, width=int(1 * R))
    if t >= 3.5:
        u = clamp((t - 3.5) / 1.4)
        for j in range(int(24 * u + 0.999)):
            k, hh = divmod(j, 8)
            x = tx + hh * 50 + 8 + ((j * 17 + 5) % 4) * 8
            y = ty + k * 40 + 6
            g.rectangle([*P(x, y), *P(x + 8, y + 28)], fill=YEL)
    # gate and residual
    if t >= 5.3:
        rbox(g, 60, 300, 400, 60, GRN_DK, GRN)
        text(g, 260, 330, "gate = σ(norm(h_t) · norm(k_t) / √d)", 16, TX)
    if t >= 7.0:
        rbox(g, 60, 390, 400, 60, GRN_DK, GRN, width=3)
        text(g, 260, 420, "h_t + gate · value", 16, TX)
    text(g, 480, 500, "DeepSeek-V4.1-Flash: orders 2-4, 8 heads (tech report 2.4.2)", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


# ---------------------------------------------------------------- 2. prefetch
LEG2 = "Pink: hash -> row ids.  Green: GPU compute.  Yellow: rows in flight.  Grey: idle"


def prefetch_frame(t):
    img, g = canvas()
    ph = [(1.6, "1. Row ids from token ids", "computed before layer 0"),
          (4.6, "2. Fetch while layer 0 runs", "rows travel in the background"),
          (6.4, "3. Rows ready at the Engram layer", "no wait for the address"),
          (8.0, "4. Engram layer uses the rows", "layer 1 in DeepSeek-V4.1-Flash")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG2)
    x0, x1 = 160, 900
    def X(sec):
        return x0 + (x1 - x0) * sec / 8.0
    text(g, 140, 190, "GPU", 15, TX, "rm")
    text(g, 140, 300, "copy / RDMA", 15, TX, "rm")
    segs = [(0.0, 1.0, "hash", PNK_DK, PNK), (1.0, 5.6, "layer 0", GRN_DK, GRN), (5.6, 8.0, "Engram, layer 1", GRN_DK, GRN)]
    for a, b, lab, f, o in segs:
        if t >= a:
            bb = min(b, max(a, t))
            rbox(g, X(a), 165, X(bb) - X(a) + 1, 50, f, o)
            if t >= (a + b) / 2:
                text(g, (X(a) + X(b)) / 2, 190, lab, 15, TX)
    if t >= 1.0:
        bb = min(4.6, t)
        rbox(g, X(1.0), 275, X(bb) - X(1.0) + 1, 50, YEL_DK, YEL)
        if t >= 2.6:
            text(g, (X(1.0) + X(4.6)) / 2, 300, "fetch 24 rows per token", 15, TX)
    if t >= 4.6:
        rbox(g, X(4.6), 275, X(7.95) - X(4.6), 50, CHIP, EDGE)
        text(g, (X(4.6) + X(8.0)) / 2, 300, "idle", 14, MUTED)
        g.line([*P(X(4.6), 222), *P(X(4.6), 268)], fill=YEL, width=int(2 * R))
        text(g, X(4.6) + 8, 245, "rows ready", 12, YEL, "lm")
    # time axis
    g.line([*P(x0, 360), *P(x1, 360)], fill=EDGE, width=int(2 * R))
    text(g, x1, 378, "time", 12, MUTED, "rm")
    cx = X(min(t, 8.0))
    g.line([*P(cx, 150), *P(cx, 360)], fill=TX, width=int(1 * R))
    text(g, 480, 440, "rows come from host memory: PCIe (paper), RDMA (V4.1, DeepEP)", 15, MUTED)
    text(g, 480, 500, "conceptual timeline, not to scale", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


# ---------------------------------------------------------------- 3. DeepEP get
LEG3 = "Green: GPU work.  Pink: row id.  Yellow: row data.  Grey: not involved"
E = 4  # entries per rank in the drawing
IDX = [5, 9, 6]


def get_frame(t):
    img, g = canvas()
    ph = [(1.8, "1. owner = id / E, row = id % E", "E = rows per rank (4 here)"),
          (4.4, "2. get each row", "the reader pulls; owner GPUs do nothing"),
          (5.8, "3. flush_async per peer", "one request per (QP, RDMA peer)"),
          (7.6, "4. wait kernel, then GEMM", "values + FP8 scales go to the next GEMM")]
    h, sb = phase(t, ph)
    head(g, h, sb, LEG3)
    # reader rank 0
    rbox(g, 40, 120, 300, 340, CHIP, GRN)
    text(g, 190, 140, "rank 0 (reader GPU)", 15, GRN)
    for i, v in enumerate(IDX):
        rbox(g, 60 + i * 90, 160, 80, 40, PNK_DK, PNK)
        text(g, 100 + i * 90, 180, f"id {v}", 14, TX)
    if t >= 0.6:
        for i, v in enumerate(IDX):
            text(g, 100 + i * 90, 215, f"r{v // E}, row {v % E}", 12, PNK)
    # recv slots
    for i in range(3):
        got = t >= 2.4 + i * 0.6
        rbox(g, 60 + i * 90, 250, 80, 40, YEL_DK if got else CHIP, YEL if got else EDGE)
        if got:
            text(g, 100 + i * 90, 270, f"row {IDX[i]}", 12, TX)
    # requests
    if t >= 4.4:
        for k, o in enumerate((1, 2)):
            rbox(g, 60 + k * 140, 320, 120, 40, GRN_DK, GRN)
            text(g, 120 + k * 140, 340, f"req: peer {o}", 13, TX)
    if t >= 5.8:
        rbox(g, 60, 390, 260, 50, GRN_DK, GRN, width=3)
        text(g, 190, 415, "wait()  ->  GEMM", 15, TX)
    # owners
    for k, o in enumerate((1, 2)):
        y = 120 + k * 180
        rbox(g, 600, y, 320, 160, CHIP, EDGE)
        text(g, 760, y + 20, f"rank {o} (owner): GPU idle", 14, MUTED)
        for r in range(E):
            gid = o * E + r
            want = gid in IDX
            rbox(g, 620 + r * 74, y + 50, 66, 40, YEL_DK if want else CHIP, YEL if want else EDGE)
            text(g, 653 + r * 74, y + 70, f"{gid}", 13, TX)
        text(g, 760, y + 118, f"rows {o * E}-{o * E + E - 1} in host memory", 12, MUTED)
    text(g, 470, 300, "RDMA", 13, MUTED)
    # packets owner -> reader
    for i, v in enumerate(IDX):
        st = 1.8 + i * 0.6
        if st <= t < st + 0.6:
            u = ease((t - st) / 0.6)
            o, r = divmod(v, E)
            sx, sy = 653 + r * 74, 120 + (o - 1) * 180 + 70
            ex, ey = 100 + i * 90, 270
            packet(g, lerp(sx, ex, u), lerp(sy, ey, u), col=YEL, tag="row", w=44)
    text(g, 480, 500, "after engram_fetch.cuh in DeepEP: world team, 1 rank = 1 RDMA peer", 13, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


PNK_DK = (80, 30, 46)
for name, fn, dur, stills in [("engram-lookup.gif", lookup_frame, 8.8, [12, 36, 58, 78, 104]),
                              ("engram-prefetch.gif", prefetch_frame, 8.0, [12, 40, 70, 94]),
                              ("engram-get.gif", get_frame, 7.6, [14, 40, 62, 88])]:
    save([fn(i / FPS) for i in range(int(dur * FPS))], name, stills)
