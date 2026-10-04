"""gen_aliases_gif.py — NxD Inference の aliases が KV キャッシュを書き戻す様子の GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_aliases_gif.py

forward() は (hidden, cache_k_0..29, cache_v_0..29) のタプルを返し、aliases が「出力の何番目を
どの nn.Parameter に書き戻すか」を決める。トレース後のグラフは外から書き換えられないので、
新しい KV は torch.scatter で作った新しいテンソルとして返し、ランタイムが書き戻す。
図では 30 層のうち 3 層だけを描く。図の文字は英語。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "aliases-writeback.gif")
SC = 4 / 3
FPS = 12
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
DIM = (46, 50, 56)
CHIP = (22, 26, 30)
GREY = (52, 56, 64)

SLOTS = 16
LAYERS = 3


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, x, y, w, h, fill, outline, text=None, size=15, col=TX):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=7 * SC, fill=fill, outline=outline,
                        width=int(2 * SC))
    if text:
        g.text(P(x + w / 2, y + h / 2), text, font=s.font(size), fill=col, anchor="mm")


# outputs row: index 0 = hidden, 1..3 = k, 4..6 = v
OUT_Y = 210
OUT_X0, OUT_W, OUT_GAP = 60, 96, 10
CACHE_Y0 = 330
CACHE_X = 420


def out_x(i):
    return OUT_X0 + i * (OUT_W + OUT_GAP)


def frame(step, phase, u):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 40), "KV write-back with aliases", font=s.font(26), fill=TX, anchor="lm")
    g.text(P(40, 84), {0: "1. forward() returns hidden + new KV (torch.scatter)",
                       1: "2. aliases map output index -> nn.Parameter",
                       2: "3. next step reads the updated KV"}[phase] + f"   (decode step {step})",
           font=s.font(15), fill=MUTED, anchor="lm")
    rbox(g, 60, 120, 270, 50, (18, 64, 34), GRN, "forward()", 15)
    # output tuple
    names = ["h", "k0", "k1", "k2", "v0", "v1", "v2"]
    IDX = [0, 1, 2, 3, 31, 32, 33]
    for i, n in enumerate(names):
        hot = phase == 0 and i > 0
        rbox(g, out_x(i), OUT_Y, OUT_W, 40, mix(CHIP, YEL, 0.45 * hot) if i else LINK_DK,
             YEL if hot else (LINK if i == 0 else DIM), f"[{IDX[i]}] {n}", 13)
    g.text(P(out_x(0), OUT_Y + 58), "first 3 of 30 layers shown (k: 1..30, v: 31..60)", font=s.font(12), fill=MUTED, anchor="lm")
    # caches (nn.Parameter): rows in the same order as the outputs (k0..k2, then v0..v2)
    g.text(P(60, CACHE_Y0 - 12), "nn.Parameter (KV cache)", font=s.font(13), fill=MUTED, anchor="lm")
    filled = step + (1 if phase >= 1 else 0)
    for r in range(6):
        y = CACHE_Y0 + r * 30
        g.text(P(60, y + 11), names[r + 1], font=s.font(13), fill=TX, anchor="lm")
        for c in range(SLOTS):
            x = 120 + c * 18
            col = GRN_HI if c < filled - 1 else (YEL if c == filled - 1 and phase >= 1 else CHIP)
            g.rectangle([P(x, y), P(x + 14, y + 22)], fill=col, outline=DIM, width=int(1 * SC))
    # write-back arrows: output [i] -> row i-1
    if phase == 1:
        for i in range(1, 7):
            src = (out_x(i) + OUT_W / 2, OUT_Y + 40)
            dst = (120 + step * 18 + 7, CACHE_Y0 + (i - 1) * 30 + 11)
            tt = min(1.0, u * 1.4)
            g.line([P(*src), P(src[0] + (dst[0] - src[0]) * tt, src[1] + (dst[1] - src[1]) * tt)],
                   fill=YEL, width=int(2 * SC))
    rbox(g, 520, 120, 380, 50, CHIP, DIM, "aliases: Parameter -> index", 13, MUTED)
    return img


frames = []
for step in range(1, 5):
    for ph, n in ((0, 10), (1, 14), (2, 8)):
        for f in range(n):
            frames.append(frame(step, ph, ease(f / max(1, n - 1))))
pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB")
