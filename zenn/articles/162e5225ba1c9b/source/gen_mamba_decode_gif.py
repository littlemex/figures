"""gen_mamba_decode_gif.py -- NemotronH の Mamba2 の decode のカーネルが、1 ステップ (全リクエストが 1 トークンずつ進む) を
NeuronCore の上でどう計算するかを、タイル (行 = 128 チャネル = 2 ヘッド x 64、列 = リクエスト) と一緒に 1 段ずつ見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_mamba_decode_gif.py

根拠: vllm_neuron/model/nemotron_h/mamba_decode_kernel.py (littlemex/vllm-neuron fdc9802)。
1 全リクエストの入力を 1 回の転送で [128 x R] のタイルに
2 直前 3 トークンと今の 4 つで畳み込み + SiLU (列ごとに同時)
3 ヘッドごとの dt と減衰を [ヘッド x R] で求め、0/1 の表との行列積 1 回で 64 行に配る
4 状態の更新だけはリクエストごと: HBM の状態の行を読み、h = h dA + dt x B、書き戻す
5 出力 y = h . C + D x
6 SiLU(gate) を掛けて正規化し、HBM へ
図の文字は英語。部品には名前を付け、色だけに頼らない (ZN-29)。
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
OUT = os.path.join(OUT_DIR, "mamba-decode.gif")
SC = 4 / 3
FPS = 4
EDGE = (70, 74, 80)
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL, YEL_DK = (251, 211, 50), (80, 66, 14)
ORG = (255, 160, 60)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)
R = 8

HBM = (30, 100, 140, 380)
TL = (320, 110)              # tile origin
CW, RH = 44, 40              # tile cell
TE = (690, 100, 250, 110)
SE = (690, 230, 250, 90)
VE = (690, 340, 250, 90)

FORM = {
    "1": "tile[p, r] = input of request r, channel p",
    "2": "xBC = silu(w \u00b7 [3 kept inputs, now])",
    "3": "dt = softplus(dt_raw + bias),   dA = exp(dt A)",
    "4": "h = h\u00b7dA + dt\u00b7x\u00b7B     (h: the request's state row)",
    "5": "y = h \u00b7 C + D\u00b7x",
    "6": "y = rmsnorm(y \u00d7 silu(gate)) \u00d7 w   ->  HBM",
}


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def rbox(g, r, fill, outline, w=2):
    x, y, ww, hh = r
    g.rounded_rectangle([P(x, y), P(x + ww, y + hh)], radius=8 * SC, fill=fill, outline=outline, width=int(w * SC))


def tile(g, fill_fn):
    x0, y0 = TL
    g.text(P(x0 + R * CW / 2, y0 - 20), "SBUF tile: 128 rows (2 heads \u00d7 64 values) \u00d7 8 requests", font=F(14), fill=MUTED, anchor="mm")
    for r in range(R):
        g.text(P(x0 + r * CW + CW / 2, y0 + 4 * RH + 16), f"r{r}", font=F(13), fill=MUTED, anchor="mm")
        for k in range(4):
            fill, out = fill_fn(r, k)
            g.rectangle([P(x0 + r * CW, y0 + k * RH), P(x0 + r * CW + CW - 4, y0 + k * RH + RH - 4)],
                        fill=fill, outline=out, width=int(1.5 * SC))
    for k, lab in ((0, "head 0: 64 rows"), (2, "head 1: 64 rows")):
        hd, rows = lab.split(": ")
        g.text(P(x0 - 8, y0 + k * RH + RH - 9), hd, font=F(13), fill=MUTED, anchor="rm")
        g.text(P(x0 - 8, y0 + k * RH + RH + 9), rows, font=F(12), fill=MUTED, anchor="rm")


def base(g, cap, active=()):
    g.text(P(30, 46), cap, font=F(26), fill=YEL, anchor="lm")
    for r, nm in ((HBM, "HBM"), (TE, "Tensor Engine"), (SE, "Scalar Engine"), (VE, "Vector Engine")):
        on = nm in active
        rbox(g, r, CHIP, WHITE if on else EDGE, w=3 if on else 1.5)
        g.text(P(r[0] + r[2] / 2, r[1] + 16), nm, font=F(14), fill=TX if on else MUTED, anchor="mm")
    g.text(P(HBM[0] + HBM[2] / 2, HBM[1] + 60), "inputs", font=F(13), fill=MUTED, anchor="mm")
    g.text(P(HBM[0] + HBM[2] / 2, HBM[1] + 200), "state pool", font=F(13), fill=MUTED, anchor="mm")
    for k in range(R):
        g.rectangle([P(HBM[0] + 20, HBM[1] + 216 + k * 16), P(HBM[0] + HBM[2] - 20, HBM[1] + 228 + k * 16)],
                    fill=mix(BG, GRN, 0.35), outline=None)
    g.rounded_rectangle([P(30, 540), P(930, 588)], radius=8 * SC, fill=(14, 18, 22), outline=EDGE, width=int(1 * SC))
    g.text(P(48, 564), FORM[cap.split()[0]], font=F(16), fill=TX, anchor="lm")


frames = []


def scene(steps, hold, draw):
    for f in range(steps):
        img = Image.new("RGB", (int(960 * SC), int(600 * SC)), BG)
        g = ImageDraw.Draw(img)
        draw(g, f / max(1, steps - 1))
        frames.append(img)
    frames.extend([frames[-1]] * hold)


EMPTY = lambda r, k: (BG, EDGE)  # noqa: E731


def s1(g, u):
    base(g, "1  load every request in one transfer", active=("HBM",))
    tile(g, lambda r, k: (mix(BG, BLU, 0.45), BLU) if u > 0.5 else (BG, EDGE))
    x = HBM[0] + HBM[2]
    g.line([P(x, TL[1] + 2 * RH), P(x + (TL[0] - x - 10) * min(1, u * 2), TL[1] + 2 * RH)], fill=BLU, width=int(10 * SC))


def s2(g, u):
    base(g, "2  conv: 3 kept + now, then SiLU", active=("Vector Engine", "Scalar Engine"))
    tile(g, lambda r, k: (mix(BG, ORG, 0.45 * u + 0.1), ORG))
    g.text(P(TL[0] + R * CW / 2, TL[1] + 4 * RH + 44), "all 8 columns at once", font=F(15), fill=TX, anchor="mm")


def s3(g, u):
    base(g, "3  dt and decay per head", active=("Scalar Engine", "Tensor Engine"))
    tile(g, lambda r, k: (mix(BG, YEL, 0.15 + 0.4 * u), YEL))
    g.text(P(TE[0] + TE[2] / 2, TE[1] + 50), "0/1 table matmul", font=F(13), fill=TX, anchor="mm")
    g.text(P(TE[0] + TE[2] / 2, TE[1] + 76), "head -> its 64 rows", font=F(13), fill=TX, anchor="mm")


def s4(g, u):
    r_on = min(R - 1, int(u * R))
    base(g, f"4  update the state: request r{r_on}", active=("Vector Engine", "HBM"))
    tile(g, lambda r, k: ((mix(BG, GRN, 0.6), WHITE) if r == r_on else (mix(BG, YEL, 0.15), EDGE)))
    y = HBM[1] + 216 + r_on * 16
    g.rectangle([P(HBM[0] + 16, y - 3), P(HBM[0] + HBM[2] - 16, y + 15)], outline=WHITE, width=int(2 * SC))
    g.line([P(HBM[0] + HBM[2] - 16, y + 6), P(TL[0] + r_on * CW + CW / 2, TL[1] + 4 * RH + 4)], fill=GRN, width=int(2 * SC))
    g.text(P(TL[0] + R * CW / 2, TL[1] + 4 * RH + 44), "one request at a time", font=F(15), fill=TX, anchor="mm")


def s5(g, u):
    base(g, "5  output from the new state", active=("Vector Engine",))
    tile(g, lambda r, k: (mix(BG, BLU, 0.2 + 0.4 * u), BLU))


def s6(g, u):
    base(g, "6  normalize and write y", active=("Tensor Engine", "Scalar Engine", "HBM"))
    tile(g, lambda r, k: (mix(BG, BLU, 0.6), BLU))
    x = HBM[0] + HBM[2]
    g.line([P(TL[0] - 10, TL[1] + 2 * RH), P(TL[0] - 10 - (TL[0] - 10 - x) * u, TL[1] + 2 * RH)], fill=BLU, width=int(10 * SC))


for fn, steps, hold in ((s1, 8, 8), (s2, 6, 8), (s3, 6, 8), (s4, 24, 6), (s5, 6, 6), (s6, 8, 10)):
    scene(steps, hold, fn)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    k = 0
    for i in range(1, len(frames)):
        if frames[i] is frames[i - 1] and (i + 1 == len(frames) or frames[i + 1] is not frames[i]):
            frames[i].save(os.path.join(OUT_DIR, f"m{k}.png"))
            k += 1
    frames[len(frames) // 2].save(os.path.join(OUT_DIR, "mid.png"))
