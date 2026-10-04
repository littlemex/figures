"""gen_torus_switch_gif.py — MoE の dispatch と combine を、4x4 の 2D トーラスとスイッチで比べる GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_torus_switch_gif.py

場面 1: 1 つのトークンが (0,0) から (2,2) のエキスパートへ行き、結果が戻る。トーラスでは途中のチップが中継し、
スイッチではスイッチを 1 回通るだけ。
場面 2: 16 チップ全員が全員へ同じ量を送る (偏りのない dispatch)。チップ 1 枚が出せる帯域を両方で同じにすると、
トーラスでは 1 つのデータが平均 2.13 本の線を通るので、終わるまでの時間はスイッチの約 2.1 倍になる
(torus_model.py: 最も混む線の負荷 8.0 / 1 本あたり 1/4 = 32、スイッチは 15)。
図の文字は英語。
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "torus-vs-switch-dispatch.gif")

SC = 4 / 3                      # 960x540 logical -> 1280x720
FPS = 12
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
LINK = (40, 150, 240)
TOK = (251, 211, 50)
RET = (255, 140, 40)
DIM = (46, 50, 56)
CHIP = (22, 26, 30)

K = 4
# left panel: torus grid
TX0, TY0, TP = 120, 175, 68
# right panel: switch
SX0, SY = 522, 330
SW = (737, 215)


def P(x, y):
    return (x * SC, y * SC)


def tpos(x, y):
    return (TX0 + x * TP, TY0 + y * TP)


def spos(i):
    return (SX0 + i * 27, SY)


def sport(i):
    """where chip i's own link meets the switch"""
    return (SX0 + i * 27, SW[1] + 24)


def chip(g, c, hot=0.0, src=False, dst=False, relay=False, r=15):
    col = GRN_HI if (src or dst) else (TOK if relay else GRN)
    fill = mix(CHIP, col, 0.25 + 0.55 * hot) if (src or dst or relay) else mix(CHIP, GRN, 0.35)
    g.rounded_rectangle([P(c[0] - r, c[1] - r), P(c[0] + r, c[1] + r)], radius=5 * SC, fill=fill,
                        outline=col, width=int(1.6 * SC))


def torus_links(g, load=None):
    for y in range(K):
        for x in range(K):
            a = tpos(x, y)
            for b, key in ((tpos((x + 1) % K, y), ('x', x, y)), (tpos(x, (y + 1) % K), ('y', x, y))):
                v = 0.0 if load is None else load
                col = mix(DIM, LINK, 0.55 + 0.45 * v)
                if (key[0] == 'x' and x == K - 1) or (key[0] == 'y' and y == K - 1):
                    # wrap-around link: stubs leaving both edges
                    if key[0] == 'x':
                        g.line([P(a[0], a[1]), P(a[0] + 30, a[1])], fill=col, width=int(2 * SC))
                        g.line([P(tpos(0, y)[0] - 30, a[1]), P(*tpos(0, y))], fill=col, width=int(2 * SC))
                    else:
                        g.line([P(a[0], a[1]), P(a[0], a[1] + 30)], fill=col, width=int(2 * SC))
                        g.line([P(a[0], tpos(x, 0)[1] - 30), P(*tpos(x, 0))], fill=col, width=int(2 * SC))
                else:
                    g.line([P(*a), P(*b)], fill=col, width=int(2 * SC))


def switch_links(g, load=None):
    v = 0.0 if load is None else load
    for i in range(16):
        c = spos(i)
        g.line([P(c[0], c[1] - 11), P(*sport(i))],
               fill=mix(DIM, LINK, 0.55 + 0.45 * v), width=int(2 * SC))
    g.rounded_rectangle([P(SX0 - 20, SW[1] - 24), P(SX0 + 15 * 27 + 20, SW[1] + 24)], radius=8 * SC,
                        fill=(16, 44, 72), outline=LINK, width=int(2 * SC))
    g.text(P(SX0 + 7.5 * 27, SW[1]), "SW", font=s.font(18), fill=TX, anchor="mm")


def frame_base(phase_label):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 40), "MoE dispatch and combine", font=s.font(26), fill=TX, anchor="lm")
    g.text(P(40, 86), phase_label, font=s.font(15), fill=MUTED, anchor="lm")
    g.text(P(TX0 + 1.5 * TP, 128), "4x4 2D torus", font=s.font(18), fill=TX, anchor="mm")
    g.text(P(SW[0], 128), "Switch", font=s.font(18), fill=TX, anchor="mm")
    return img, g


def along(pts, t):
    """position at fraction t of a polyline"""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1
    d = t * total
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L:
            u = d / L if L else 0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        d -= L
    return pts[-1]


def token(g, p, col):
    r = 8
    g.ellipse([P(p[0] - r, p[1] - r), P(p[0] + r, p[1] + r)], fill=col, outline=BG, width=int(2 * SC))


frames = []

# scene 1: one token from (0,0) to (2,2) and back
SRC, DST = (0, 0), (2, 2)
tpath = [tpos(0, 0), tpos(1, 0), tpos(2, 0), tpos(2, 1), tpos(2, 2)]
relays = [(1, 0), (2, 0), (2, 1)]
si, di = 0, 10
spath = [spos(si), sport(si), sport(di), spos(di)]


def scene1(t, back):
    img, g = frame_base("1 token: dispatch, then combine" if not back else "1 token: combine")
    torus_links(g)
    switch_links(g)
    reached = t * 4
    for y in range(K):
        for x in range(K):
            src = (x, y) == SRC
            dst = (x, y) == DST
            rel = (x, y) in relays and (reached >= (relays.index((x, y)) + 1) if not back
                                         else reached >= (3 - relays.index((x, y))))
            chip(g, tpos(x, y), hot=1.0, src=src, dst=dst, relay=rel)
    for i in range(16):
        chip(g, spos(i), hot=1.0, src=i == si, dst=i == di, r=11)
    col = RET if back else TOK
    tp = tpath[::-1] if back else tpath
    sp = spath[::-1] if back else spath
    token(g, along(tp, t), col)
    token(g, along(sp, min(1.0, t * 2)), col)
    nrel = sum(1 for rr in relays if (reached >= relays.index(rr) + 1))
    g.text(P(TX0 + 1.5 * TP, 450), f"relay chips: {min(3, nrel)}", font=s.font(18), fill=TOK, anchor="mm")
    g.text(P(SW[0], 450), "relay chips: 0", font=s.font(18), fill=TOK, anchor="mm")
    return img


for back in (False, True):
    for f in range(30):
        frames.append(scene1(ease(f / 29), back))
    for _ in range(8):
        frames.append(frames[-1])

# scene 2: all 16 chips send to all, same bandwidth per chip
T_TORUS, T_SWITCH = 32.0, 15.0


def scene2(t_units, label):
    img, g = frame_base(label)
    busy_t = 1.0 if t_units < T_TORUS else 0.0
    busy_s = 1.0 if t_units < T_SWITCH else 0.0
    torus_links(g, load=busy_t)
    switch_links(g, load=busy_s)
    for y in range(K):
        for x in range(K):
            chip(g, tpos(x, y), hot=busy_t, relay=busy_t > 0)
    for i in range(16):
        chip(g, spos(i), r=11)
    # progress bars on a shared time axis
    # traffic pulses on every busy link
    ph = (t_units * 0.35) % 1.0
    if busy_t:
        for y in range(K):
            for x in range(K):
                a = tpos(x, y)
                ends = (tpos(x + 1, y) if x < K - 1 else (a[0] + 30, a[1]),
                        tpos(x, y + 1) if y < K - 1 else (a[0], a[1] + 30))
                for b in ends:
                    q = (a[0] + (b[0] - a[0]) * ph, a[1] + (b[1] - a[1]) * ph)
                    g.ellipse([P(q[0] - 4, q[1] - 4), P(q[0] + 4, q[1] + 4)], fill=TOK)
    if busy_s:
        for i in range(16):
            a, b = spos(i), sport(i)
            q = (a[0] + (b[0] - a[0]) * ph, a[1] + (b[1] - a[1]) * ph)
            g.ellipse([P(q[0] - 4, q[1] - 4), P(q[0] + 4, q[1] + 4)], fill=TOK)
    bx, by, bw = 130, 455, 700
    scale = bw / T_TORUS
    for row, (name, T, col) in enumerate((("torus", T_TORUS, LINK), ("switch", T_SWITCH, GRN_HI))):
        yy = by + row * 26 - 13
        g.text(P(bx - 12, yy), name, font=s.font(15), fill=TX, anchor="rm")
        g.rectangle([P(bx, yy - 8), P(bx + T * scale, yy + 8)], outline=DIM, width=int(1 * SC))
        fill = min(t_units, T)
        g.rectangle([P(bx, yy - 8), P(bx + fill * scale, yy + 8)], fill=col)
        if t_units >= T:
            g.text(P(bx + T * scale + 10, yy), "1.0x" if T == T_TORUS else f"{T / T_TORUS:.2f}x",
                   font=s.font(15), fill=col, anchor="lm")
    return img


for label in ("All 16 chips dispatch at once (bandwidth model)", "All 16 chips combine at once (bandwidth model)"):
    for f in range(44):
        frames.append(scene2(T_TORUS * 1.05 * f / 43, label))
    for _ in range(14):
        frames.append(frames[-1])

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB")
