"""gen_ssd_hw_gif.py -- chunked SSD の 1 つの塊を、NeuronCore の上でデータがどう運ばれ、どこで計算されるかを
バケツの説明 (階段、漏れ、h) と同じ言葉で 1 段ずつ見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_ssd_hw_gif.py

根拠: vllm_neuron/model/nemotron_h/ssd_prefill_kernel.py (littlemex/vllm-neuron fdc9802)。
1 load a chunk          HBM -> SBUF に x, dt, B, C (128 トークン分)
2 staircase shape       Tensor Engine: B を固定、C を流す -> PSUM に 128x128、三角形だけ残す
3 add the leak          Scalar Engine の exp で減衰、Vector Engine で掛ける -> 重み M
4 inside the chunk      Tensor Engine: M を固定、dt x を流す -> 塊の中の分の y
5 from h                Tensor Engine: C を固定、h (状態) を流す -> 前の塊からの分、減衰を掛けて足す
6 write y               SBUF -> HBM
7 new h stays on chip   Tensor Engine で新しい h を作り、SBUF に置いたまま次の塊へ
図の文字は英語。色は役割の目印で、各部品には名前のラベルを付ける (ZN-29)。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "ssd-hw.gif")
SC = 4 / 3
FPS = 4
EDGE = (70, 74, 80)
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL, YEL_DK = (251, 211, 50), (80, 66, 14)
ORG = (255, 160, 60)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)

# layout (logical 960 x 540)
HBM = (30, 110, 140, 330)
SB = (200, 100, 270, 360)     # SBUF
TE = (500, 100, 250, 230)     # Tensor Engine
PS = (500, 360, 250, 100)     # PSUM
SE = (780, 100, 160, 120)     # Scalar Engine
VE = (780, 250, 160, 120)     # Vector Engine
SLOTS = {"x": 0, "dt": 1, "B": 2, "C": 3, "M": 4, "y": 5, "h": 6}


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def rbox(g, r, fill, outline, w=2):
    x, y, ww, hh = r
    g.rounded_rectangle([P(x, y), P(x + ww, y + hh)], radius=8 * SC, fill=fill, outline=outline, width=int(w * SC))


def slot_xy(name):
    k = SLOTS[name]
    return SB[0] + 20, SB[1] + 40 + k * 44


def tile(g, x, y, name, fill, outline, w=110, h=34):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=6 * SC, fill=fill, outline=outline, width=int(2 * SC))
    g.text(P(x + w / 2, y + h / 2), name, font=F(15), fill=TX, anchor="mm")


def tri(g, r, fill, outline):
    x, y, w, h = r
    g.polygon([P(x, y), P(x, y + h), P(x + w, y + h)], fill=fill, outline=outline)


FORM = {
    "1": "x, dt, B, C  for tokens 1..128",
    "2": "G[i, j] = C_i \u00b7 B_j     (keep j <= i)",
    "3": "L[i, j] = exp(cs_i - cs_j),   M = G \u00d7 L",
    "4": "y_i = sum_j  M[i, j] \u00b7 dt_j \u00b7 x_j",
    "5": "y_i += exp(cs_i) \u00b7 C_i \u00b7 h  +  D \u00b7 x_i",
    "6": "y  ->  HBM",
    "7": "h = exp(cs_Q)\u00b7h + sum_j exp(cs_Q - cs_j)\u00b7dt_j\u00b7x_j\u00b7B_j",
}


def base(g, cap, active=(), present=()):
    g.text(P(30, 50), cap, font=F(26), fill=YEL, anchor="lm")
    g.rounded_rectangle([P(30, 540), P(930, 588)], radius=8 * SC, fill=(14, 18, 22), outline=EDGE, width=int(1 * SC))
    g.text(P(48, 564), FORM[cap.split()[0]], font=F(16), fill=TX, anchor="lm")
    for r, nm in ((HBM, "HBM"), (SB, "SBUF"), (TE, "Tensor Engine"), (PS, "PSUM"), (SE, "Scalar (exp)"), (VE, "Vector")):
        on = nm in active
        rbox(g, r, CHIP, WHITE if on else EDGE, w=3 if on else 1.5)
        g.text(P(r[0] + r[2] / 2, r[1] + 16), nm, font=F(14), fill=TX if on else MUTED, anchor="mm")
    g.text(P(HBM[0] + HBM[2] / 2, HBM[1] + HBM[3] + 16), "far, big", font=F(12), fill=MUTED, anchor="mm")
    g.text(P(SB[0] + SB[2] / 2, SB[1] + SB[3] + 16), "near, small", font=F(12), fill=MUTED, anchor="mm")
    g.text(P(TE[0] + 18, TE[1] + TE[3] - 16), "fixed", font=F(12), fill=MUTED, anchor="lm")
    g.text(P(TE[0] + TE[2] - 14, TE[1] + TE[3] - 16), "flows in", font=F(12), fill=MUTED, anchor="rm")
    for nm in present:
        x, y = slot_xy(nm)
        col = {"h": (GRN_DK, GRN), "M": (YEL_DK, YEL), "y": (BLU_DK, BLU)}.get(nm, (BLU_DK, BLU))
        tile(g, x, y, nm if nm != "h" else "h (state)", *col, w=230)


def lerp(a, b, u):
    return a + (b - a) * u


def mover(g, src, dst, u, name, col):
    x = lerp(src[0], dst[0], u)
    y = lerp(src[1], dst[1], u)
    tile(g, x, y, name, *col)


frames = []


def scene(cap, steps, hold, draw):
    for f in range(steps):
        img = Image.new("RGB", (int(960 * SC), int(600 * SC)), BG)
        g = ImageDraw.Draw(img)
        draw(g, f / max(1, steps - 1))
        frames.append(img)
    frames.extend([frames[-1]] * hold)


ALL_IN = ("x", "dt", "B", "C")


def s1(g, u):
    shown = [n for k, n in enumerate(ALL_IN) if u >= (k + 1) / 4]
    base(g, "1  load one chunk", active=("HBM", "SBUF"), present=tuple(shown) + ("h",))
    for k, n in enumerate(ALL_IN):
        a = min(1, max(0, u * 4 - k))
        if 0 < a < 1:
            mover(g, (HBM[0] + 10, HBM[1] + 60 + k * 40), slot_xy(n), a, n, (BLU_DK, BLU))
    g.text(P(HBM[0] + HBM[2] / 2, HBM[1] + 62), "128 tokens", font=F(13), fill=MUTED, anchor="mm")


def s2(g, u):
    base(g, "2  C \u00d7 B: the staircase shape", active=("Tensor Engine", "PSUM", "Vector"), present=ALL_IN + ("h",))
    tile(g, TE[0] + 10, TE[1] + 40, "B", BLU_DK, BLU, w=90)
    mover(g, (TE[0] + 210, TE[1] + 90), (TE[0] + 115, TE[1] + 90), u, "C", (BLU_DK, BLU))
    if u > 0.6:
        tri(g, (PS[0] + 90, PS[1] + 34, 70, 56), mix(BG, GRN, 0.6), GRN)


def s3(g, u):
    base(g, "3  add the leak (exp)", active=("Scalar (exp)", "Vector"), present=ALL_IN + ("h",) + (("M",) if u > 0.7 else ()))
    tri(g, (SE[0] + 55, SE[1] + 34, 50, 50), mix(BG, ORG, 0.6), ORG)
    g.text(P(SE[0] + 80, SE[1] + 102), "leak", font=F(13), fill=MUTED, anchor="mm")
    tri(g, (VE[0] + 55, VE[1] + 34, 50, 50), mix(BG, YEL, 0.6), YEL)
    g.text(P(VE[0] + 80, VE[1] + 102), "weights M", font=F(13), fill=MUTED, anchor="mm")


def s4(g, u):
    base(g, "4  inside the chunk", active=("Tensor Engine", "PSUM"), present=ALL_IN + ("h", "M"))
    tile(g, TE[0] + 10, TE[1] + 40, "M", YEL_DK, YEL, w=90)
    mover(g, (TE[0] + 210, TE[1] + 90), (TE[0] + 115, TE[1] + 90), u, "dt\u00b7x", (BLU_DK, BLU))
    if u > 0.6:
        tile(g, PS[0] + 25, PS[1] + 40, "y (inside)", BLU_DK, BLU, w=200)


def s5(g, u):
    base(g, "5  from earlier chunks: h", active=("Tensor Engine", "PSUM", "Vector"), present=ALL_IN + ("h", "M"))
    tile(g, TE[0] + 10, TE[1] + 40, "C", BLU_DK, BLU, w=90)
    src = slot_xy("h")
    mover(g, (src[0] + 100, src[1]), (TE[0] + 115, TE[1] + 90), u, "h", (GRN_DK, GRN))
    if u > 0.6:
        tile(g, PS[0] + 25, PS[1] + 40, "y (inside + h)", BLU_DK, BLU, w=200)


def s6(g, u):
    base(g, "6  write y", active=("SBUF", "HBM"), present=ALL_IN + ("h", "M", "y"))
    src = slot_xy("y")
    mover(g, src, (HBM[0] + 10, HBM[1] + 220), u, "y", (BLU_DK, BLU))


def s7(g, u):
    base(g, "7  new h stays on chip", active=("Tensor Engine", "SBUF"), present=ALL_IN + ("M",) + (("h",) if u <= 0.5 else ()))
    tile(g, TE[0] + 10, TE[1] + 40, "B", BLU_DK, BLU, w=90)
    mover(g, (TE[0] + 210, TE[1] + 90), (TE[0] + 115, TE[1] + 90), min(1, u * 1.6), "dt\u00b7x", (BLU_DK, BLU))
    if u > 0.5:
        x, y = slot_xy("h")
        a = (u - 0.5) * 2
        mover(g, (TE[0] + 40, TE[1] + 150), (x, y), a, "new h", (GRN_DK, GRN))
    g.text(P(SB[0] + SB[2] / 2, SB[1] + SB[3] + 44), "-> next chunk", font=F(15), fill=GRN, anchor="mm")


for cap_fn, steps, hold in ((s1, 12, 6), (s2, 8, 8), (s3, 6, 8), (s4, 8, 8), (s5, 8, 8), (s6, 6, 6), (s7, 10, 10)):
    scene(None, steps, hold, cap_fn)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    k = 0
    for i in range(1, len(frames)):
        if frames[i] is frames[i - 1] and (i + 1 == len(frames) or frames[i + 1] is not frames[i]):
            frames[i].save(os.path.join(OUT_DIR, f"w{k}.png"))
            k += 1
