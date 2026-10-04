"""gen_gif.py — EFA の SRD が 1 つの通信を複数経路に散らす様子と、TCP の 1 本道との比較 GIF。

    cd <このディレクトリ>
    OUT_DIR=<出力先> /usr/bin/python3 gen_srd_mp4.py

流れ
1. スパインとリーフの木。A と B は EFA を持つホスト
2. A から B への経路を 4 本、色を変えて 1 本ずつ引く
3. 木の配置を、A を左、B を右にした横並びへ組み替える。経路に関係しない箱は消える
4. EFA の SRD がパケットを 4 本に散らして流す
5. その図を左へ寄せ、右に TCP の 1 本道を並べる
6. 流れを増やすと、SRD は 4 本に散って流れ続け、TCP は 1 本の道が詰まって L1 の手前に列ができる

描画は PIL だけ。論理座標 960x540 で組み、高い倍率で描いてから 1280x720 に縮める。
"""
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "srd-multipath-en.mp4")
SNAP = os.path.join(OUT_DIR, "stills")
os.makedirs(SNAP, exist_ok=True)

W, H = 960, 540                 # 論理座標
OW, OH = 1920, 1080             # 出力
R = 8 / 3                       # 描画倍率。OW の 2 倍で描いて縮める
FPS = 20

BG = (0, 0, 0)
NODE = (22, 29, 38)
EDGE = (92, 92, 92)
TX = (243, 243, 247)
MUTED = (140, 140, 140)
PATHS = [(65, 179, 255), (132, 206, 255), (59, 209, 111), (251, 211, 50)]
TCP = (205, 205, 210)
HOT = (235, 75, 75)
EFA_TAG = (65, 179, 255)

JA = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
EN = "/Library/Fonts/AmazonEmber_Bd.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(size * R))


F_NODE = font(EN, 20)
F_TAG = font(EN, 13)
F_CAP = font(EN, 24)
F_HEAD = font(EN, 22)

# ------------------------------------------------------------------ 配置
SPINES = ["S1", "S2", "S3", "S4"]
LEAVES = ["L1", "L2", "L3", "L4"]
HOSTS = ["A", "h2", "h3", "h4", "h5", "h6", "B"]
HOST_LEAF = {"A": "L1", "h2": "L1", "h3": "L2", "h4": "L2", "h5": "L3",
             "h6": "L4", "B": "L4"}

TREE = {}
for i, s in enumerate(SPINES):
    TREE[s] = (240 + i * 160, 130)
for i, l in enumerate(LEAVES):
    TREE[l] = (150 + i * 220, 290)
TREE["A"], TREE["h2"] = (110, 440), (190, 440)
TREE["h3"], TREE["h4"] = (330, 440), (410, 440)
TREE["h5"] = (590, 440)
TREE["h6"], TREE["B"] = (770, 440), (850, 440)

GRAPH = dict(TREE)
GRAPH["A"], GRAPH["L1"] = (90, 290), (270, 290)
for i, s in enumerate(SPINES):
    GRAPH[s] = (480, 140 + i * 100)
GRAPH["L4"], GRAPH["B"] = (690, 290), (870, 290)

ON_PATH = {"A", "L1", "L4", "B", *SPINES}
EDGES = [(s, l) for s in SPINES for l in LEAVES]
EDGES += [(h, HOST_LEAF[h]) for h in HOSTS]
ROUTES = [["A", "L1", s, "L4", "B"] for s in SPINES]
TCP_ROUTE = ["A", "L1", "S2", "L4", "B"]

#: 並べたときの左右の置き場。(倍率, x のずらし, y のずらし)
FULL = (1.0, 0.0, 0.0)
LEFT = (0.52, -5.0, 124.0)
RIGHT = (0.52, 475.0, 124.0)


# ------------------------------------------------------------------ 補助
def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def xf_lerp(a, b, t):
    return tuple(lerp(a[i], b[i], t) for i in range(3))


def node_pos(name, m):
    (x0, y0), (x1, y1) = TREE[name], GRAPH[name]
    return lerp(x0, x1, m), lerp(y0, y1, m)


def T(p, xf):
    """論理座標を置き場に移し、描画倍率を掛ける"""
    k, dx, dy = xf
    return ((p[0] * k + dx) * R, (p[1] * k + dy) * R)


def seg_lengths(pts):
    return [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def at(pts, t):
    segs = seg_lengths(pts)
    d = t * sum(segs)
    for i, L in enumerate(segs):
        if d <= L or i == len(segs) - 1:
            u = 0 if L == 0 else d / L
            return (lerp(pts[i][0], pts[i + 1][0], u),
                    lerp(pts[i][1], pts[i + 1][1], u))
        d -= L
    return pts[-1]


def partial(pts, t):
    if t >= 1:
        return pts
    segs = seg_lengths(pts)
    d = t * sum(segs)
    out = [pts[0]]
    for i, L in enumerate(segs):
        if d >= L:
            out.append(pts[i + 1])
            d -= L
        else:
            u = 0 if L == 0 else d / L
            out.append((lerp(pts[i][0], pts[i + 1][0], u),
                        lerp(pts[i][1], pts[i + 1][1], u)))
            break
    return out


def shifted(pts, k, n, gap):
    off = (k - (n - 1) / 2) * gap
    return [(x, y + off) for x, y in pts]


# ------------------------------------------------------------------ 描画部品
def draw_boxes(g, m, fade, xf, names):
    k = xf[0]
    for n in names:
        keep = n in ON_PATH
        if not keep and fade >= 0.99:
            continue
        x, y = node_pos(n, m)
        rw = (34 if n in ("A", "B") else 28)
        cx, cy = T((x, y), xf)
        hw, hh = rw * k * R, 22 * k * R
        fill = NODE if keep else mix(NODE, BG, fade)
        edge = (TX if n in ("A", "B") else EDGE) if keep else mix(EDGE, BG, fade)
        g.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh],
                            radius=8 * k * R, fill=fill, outline=edge,
                            width=max(2, int(2 * R * k)))
        if n.startswith("h"):
            continue
        col = TX if keep else mix(MUTED, BG, fade)
        fnt = F_NODE if k > 0.9 else font(EN, 20 * max(k, 0.75))
        g.text((cx, cy), n, font=fnt, fill=col, anchor="mm")


def draw_efa_tag(g, m, xf, alpha, label="EFA"):
    """A と B の下に、そのホストが EFA を持つことを示す札を付ける"""
    if alpha <= 0:
        return
    k = xf[0]
    for n in ("A", "B"):
        x, y = node_pos(n, m)
        cx, cy = T((x, y + 34), xf)
        w, h = 22 * max(k, 0.75) * R, 10 * max(k, 0.75) * R
        col = mix(BG, EFA_TAG, alpha)
        g.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=h,
                            fill=col)
        g.text((cx, cy), label, font=font(EN, 13 * max(k, 0.75)),
               fill=mix(BG, BG, 0), anchor="mm")


def draw_dot(g, p, col, k):
    r = 8 * max(k, 0.7) * R
    g.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=BG,
              width=max(2, int(2 * R * k)))


def srd_panel(g, m, draw_t, fade, packets, xf, tag):
    """SRD の図。packets = (位相, 1 本あたりの粒の数) か None"""
    k = xf[0]
    for a, b in EDGES:
        if fade >= 0.99:
            break
        g.line([T(node_pos(a, m), xf), T(node_pos(b, m), xf)],
               fill=mix(EDGE, BG, fade), width=max(2, int(2 * R * k)))
    for i, route in enumerate(ROUTES):
        ti = max(0.0, min(1.0, draw_t * len(ROUTES) - i))
        if ti <= 0:
            continue
        pts = shifted([node_pos(n, m) for n in route], i, len(ROUTES), 5 * m)
        g.line([T(p, xf) for p in partial(pts, ease(ti))], fill=PATHS[i],
               width=max(3, int(5 * R * k)), joint="curve")
    if packets is not None:
        phase, per = packets
        for i, route in enumerate(ROUTES):
            pts = shifted([node_pos(n, m) for n in route], i, len(ROUTES),
                          5 * m)
            for j in range(per):
                t = (phase + i * 0.13 + j / per) % 1.0
                draw_dot(g, T(at(pts, t), xf), PATHS[i], k)
    draw_boxes(g, m, fade, xf, SPINES + LEAVES + HOSTS)
    draw_efa_tag(g, m, xf, tag)


def tcp_panel(g, phase, moving, queue, heat, xf, alpha):
    """TCP の図。1 本の道だけを使う。queue は L1 の手前にたまった粒の数"""
    if alpha <= 0:
        return
    k = xf[0]
    pts = [node_pos(n, 1) for n in TCP_ROUTE]
    for s in SPINES:
        if s == "S2":
            continue
        for a, b in (("L1", s), (s, "L4")):
            g.line([T(node_pos(a, 1), xf), T(node_pos(b, 1), xf)],
                   fill=mix(BG, (60, 60, 60), alpha),
                   width=max(2, int(2 * R * k)))
    # 道の色。詰まるほど赤くする
    body = mix(TCP, HOT, heat)
    g.line([T(p, xf) for p in pts], fill=mix(BG, body, alpha),
           width=max(3, int(5 * R * k)), joint="curve")
    # 流れている粒は道の容量ぶんだけ、一定の間隔で進む
    for j in range(moving):
        t = (phase + j / moving) % 1.0
        draw_dot(g, T(at(pts, t), xf), mix(BG, body, alpha), k)
    # L1 の手前の列。A から L1 の区間に後ろ向きに積む
    lx, ly = node_pos("S2", 1)
    for q in range(queue):
        row, col = divmod(q, 6)
        x = lx - 44 - col * 18
        y = ly - 24 - row * 18
        draw_dot(g, T((x, y), xf), mix(BG, HOT, alpha), k)
    draw_boxes(g, 1, 1, xf, ["A", "L1", "L4", "B"] + SPINES)


def caption(g, text, alpha=1.0):
    if text:
        g.text((40 * R, 505 * R), text, font=F_CAP, fill=mix(BG, TX, alpha),
               anchor="lm")


def heads(g, alpha):
    if alpha <= 0:
        return
    for xf, text, col in ((LEFT, "EFA (SRD)", EFA_TAG), (RIGHT, "TCP", TCP)):
        cx = (480 * xf[0] + xf[1]) * R
        g.text((cx, 70 * R), text, font=F_HEAD, fill=mix(BG, col, alpha),
               anchor="mm")
    g.line([(480 * R, 90 * R), (480 * R, 460 * R)],
           fill=mix(BG, (60, 60, 60), alpha), width=int(R))


def canvas():
    img = Image.new("RGB", (int(W * R), int(H * R)), BG)
    return img, ImageDraw.Draw(img)


def done(img):
    return img.resize((OW, OH), Image.LANCZOS)


# ------------------------------------------------------------------ 台本
def sec(s):
    return int(round(s * FPS))


FF = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
     "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
     "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)
COUNT = [0]
SNAPS = {}


def emit(img, snap=None):
    """1 コマを書き出す。snap に名前を渡すと、そのコマを PNG でも残す"""
    out = done(img)
    FF.stdin.write(out.tobytes())
    if snap:
        out.save(os.path.join(SNAP, f"{snap}.png"))
    COUNT[0] += 1



cap1 = "Hosts A and B have EFA; spine-leaf switches in between"
for i in range(sec(1.6)):
    img, g = canvas()
    srd_panel(g, 0, 0, 0, None, FULL, ease(i / sec(0.8)))
    caption(g, cap1)
    emit(img)

cap2 = "Four paths from A to B"
n = sec(2.4)
for i in range(n + sec(0.6)):
    img, g = canvas()
    srd_panel(g, 0, min(1.0, (i + 1) / n), 0, None, FULL, 1)
    caption(g, cap2)
    emit(img)

cap3 = "Lay A on the left, B on the right"
n = sec(2.0)
for i in range(n + sec(0.5)):
    t = min(1.0, (i + 1) / n)
    img, g = canvas()
    srd_panel(g, ease(t), 1, ease(min(1.0, 2.5 * t)), None, FULL, 1)
    caption(g, cap3)
    emit(img)

cap4 = "SRD sprays the packets of one flow over all four paths"
n = sec(4.0)
for i in range(n):
    img, g = canvas()
    srd_panel(g, 1, 1, 1, ((i / n) * 2 % 1.0, 3), FULL, 1)
    caption(g, cap4)
    emit(img, "flow" if i == n // 2 else None)

# 5. 左へ寄せ、右に TCP を並べる
cap5 = "TCP keeps one flow on one path"
n = sec(1.6)
for i in range(n):
    t = ease((i + 1) / n)
    img, g = canvas()
    xf = xf_lerp(FULL, LEFT, t)
    srd_panel(g, 1, 1, 1, ((i / FPS) * 0.5 % 1.0, 1), xf, 1)
    tcp_panel(g, (i / FPS) * 0.5 % 1.0, 4, 0, 0, RIGHT, t)
    heads(g, t)
    caption(g, cap5, t)
    emit(img)
base = COUNT[0]
for i in range(sec(1.6)):
    ph = ((base + i) / FPS) * 0.5 % 1.0
    img, g = canvas()
    srd_panel(g, 1, 1, 1, (ph, 1), LEFT, 1)
    tcp_panel(g, ph, 4, 0, 0, RIGHT, 1)
    heads(g, 1)
    caption(g, cap5)
    emit(img)

# 6. 流れを増やす。SRD は散って流れ続け、TCP は 1 本が詰まって列ができる
cap6 = "More traffic: the spine on the TCP path queues up, SRD keeps flowing"
n = sec(5.0)
base = COUNT[0]
for i in range(n + sec(1.2)):
    ph = ((base + i) / FPS) * 0.5 % 1.0
    load = ease(min(1.0, i / n))
    per = 1 + int(round(load * 3))            # SRD は 1 本あたり 1 から 4 粒
    queue = int(round(load * 18))             # TCP は道に乗り切らない分が列になる
    img, g = canvas()
    srd_panel(g, 1, 1, 1, (ph, per), LEFT, 1)
    tcp_panel(g, ph, 4, queue, load, RIGHT, 1)
    heads(g, 1)
    caption(g, cap6)
    emit(img, "jam" if i == n else None)

# 7. B の受け側を拡大し、順番が崩れて届く様子と並べ直しを見せる
ZOOM = (0.70, -20.0, 50.0)
SLOT0, SLOTW = 672.0, 31.0
ROW_IN, ROW_OUT = 205.0, 335.0
F_NUM = font(EN, 13)
F_LBL = font(JA, 17)

#: 番号ごとの経路と出発時刻。S1 と S4 は遠回り、S2 と S3 は近道
SEQ = list(range(1, 9))
VIA = {1: 0, 2: 2, 3: 3, 4: 1, 5: 0, 6: 2, 7: 3, 8: 1}
DUR = {0: 2.2, 1: 1.2, 2: 1.2, 3: 2.2}
DEP = {q: (q - 1) * 0.3 for q in SEQ}
ARR = {q: DEP[q] + DUR[VIA[q]] for q in SEQ}
LAND = 0.35                      # B から「届いた順」の列へ移る時間
MOVE = 0.45                      # 「届いた順」から「並べ直した順」へ移る時間
RANK = {q: r for r, q in enumerate(sorted(SEQ, key=lambda q: ARR[q]))}
REL = {q: max(ARR[p] for p in SEQ if p <= q) + LAND + 0.15 for q in SEQ}
T_OUT = max(REL.values()) + MOVE + 0.6


def slot(row_y, i):
    return (SLOT0 + i * SLOTW, row_y)


def num_dot(g, p, col, q, k=1.0):
    r = 12 * R
    g.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col,
              outline=BG, width=int(2 * R))
    g.text(p, str(q), font=F_NUM, fill=BG, anchor="mm")


def buffer_frame(g, alpha):
    if alpha <= 0:
        return
    head = mix(BG, TX, alpha)
    g.text(T((800, 128), FULL), "Receiver B", font=F_HEAD, fill=head,
           anchor="mm")
    for row_y, label, dy in ((ROW_IN, "arrived", -32), (ROW_OUT, "reordered", 32)):
        g.text(T((SLOT0 - 18, row_y + dy), FULL), label, font=F_LBL,
               fill=mix(BG, MUTED, alpha), anchor="lm")
        for i in range(8):
            cx, cy = T(slot(row_y, i), FULL)
            r = 14 * R
            g.rounded_rectangle([cx - r, cy - r, cx + r, cy + r],
                                radius=4 * R, outline=mix(BG, (70, 70, 70),
                                                          alpha),
                                width=int(1.5 * R))
    bx0, by0 = T((node_pos("B", 1)[0] + 36, node_pos("B", 1)[1]), ZOOM)
    sx, sy = T((SLOT0 - 20, ROW_IN), FULL)
    g.line([(bx0, by0), (sx, sy)], fill=mix(BG, (70, 70, 70), alpha),
           width=int(1.5 * R))
    # 2 つの列をつなぐ矢印と、その役割
    ax, ay = T((800, ROW_IN + 24), FULL)
    bx, by = T((800, ROW_OUT - 48), FULL)
    g.line([(ax, ay), (bx, by)], fill=mix(BG, EFA_TAG, alpha),
           width=int(2 * R))
    g.polygon([(bx - 7 * R, by - 9 * R), (bx + 7 * R, by - 9 * R), (bx, by)],
              fill=mix(BG, EFA_TAG, alpha))
    g.text(T((812, (ROW_IN + ROW_OUT) / 2 - 12), FULL), "reorder",
           font=F_LBL, fill=mix(BG, EFA_TAG, alpha), anchor="lm")


def lerp_pt(a, b, t):
    t = ease(t)
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def packets_at(g, t, out_shift):
    b_pos = node_pos("B", 1)
    for q in SEQ:
        i = VIA[q]
        col = PATHS[i]
        if t < DEP[q]:
            continue
        if t < ARR[q]:
            pts = shifted([node_pos(n, 1) for n in ROUTES[i]], i, 4, 5)
            num_dot(g, T(at(pts, (t - DEP[q]) / DUR[i]), ZOOM), col, q)
            continue
        land = T(slot(ROW_IN, RANK[q]), FULL)
        if t < ARR[q] + LAND:
            src = T(b_pos, ZOOM)
            num_dot(g, lerp_pt(src, land, (t - ARR[q]) / LAND), col, q)
            continue
        dst = T((slot(ROW_OUT, q - 1)[0] + out_shift, ROW_OUT), FULL)
        if t < REL[q]:
            num_dot(g, land, col, q)
        elif t < REL[q] + MOVE:
            num_dot(g, lerp_pt(land, T(slot(ROW_OUT, q - 1), FULL),
                               (t - REL[q]) / MOVE), col, q)
        else:
            num_dot(g, dst, col, q)


def app(g, a):
    """並べ直した列から、アプリへ渡す矢印"""
    x0, y0 = T((SLOT0 + 7 * SLOTW + 18, ROW_OUT), FULL)
    x1 = T((952, ROW_OUT), FULL)[0]
    col = mix(BG, TX, a)
    g.line([(x0, y0), (x1, y0)], fill=col, width=int(2 * R))
    g.polygon([(x1, y0), (x1 - 9 * R, y0 - 6 * R), (x1 - 9 * R, y0 + 6 * R)],
              fill=col)
    g.text(T((952, ROW_OUT - 30), FULL), "to app", font=F_LBL, fill=col,
           anchor="rm")


cap7a = "SRD does not keep packet order. Look at B"
n = sec(1.4)
for i in range(n):
    t = ease((i + 1) / n)
    img, g = canvas()
    srd_panel(g, 1, 1, 1, None, xf_lerp(LEFT, ZOOM, t), 1)
    tcp_panel(g, 0, 4, int(18 * (1 - t)), 1 - t, RIGHT, 1 - t)
    heads(g, 1 - t)
    buffer_frame(g, t)
    caption(g, cap7a)
    emit(img)

cap7b = "Paths differ in delay; packets arrive out of order"
cap7c = "The receiver reorders by sequence number, then hands data to the app"
total = T_OUT + 1.4
for i in range(sec(total)):
    t = i / FPS
    img, g = canvas()
    srd_panel(g, 1, 1, 1, None, ZOOM, 1)
    buffer_frame(g, 1)
    packets_at(g, t, 0.0)
    if t > T_OUT:
        app(g, ease((t - T_OUT) / 0.6))
    caption(g, cap7c if t > min(REL.values()) else cap7b)
    emit(img, "reorder" if i == sec(3.0) else None)

for i in range(sec(1.2)):
    img, g = canvas()
    srd_panel(g, 1, 1, 1, None, ZOOM, 1)
    buffer_frame(g, 1)
    packets_at(g, total, 0.0)
    app(g, 1)
    caption(g, cap7c)
    emit(img, "end" if i == 0 else None)

FF.stdin.close()
FF.wait()
print("wrote", OUT, COUNT[0], "frames", round(COUNT[0] / FPS, 1), "s",
      round(os.path.getsize(OUT) / 1e6, 2), "MB")
