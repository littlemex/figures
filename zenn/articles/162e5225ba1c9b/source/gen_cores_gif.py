"""gen_cores_gif.py -- trn2.3xlarge の 1 チップで、物理コア・論理コア (LNC=2)・TP=4・Mamba2 のグループ (B と C を共有する
ヘッドのまとまり) がどう対応し、2 つの物理コアがなぜデータをやり取りせずに済むかを 1 段ずつ見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_cores_gif.py

数: 物理コア 8 / 論理コア 4 (LNC=2) / TP=4 / Mamba2 のヘッド 64 = グループ 8 x 8 ヘッド。
1 ランク = 16 ヘッド = 2 グループ。物理コア 1 つに 1 グループ。MoE と matvec は半分ずつ。
図の文字は英語。各要素にラベルを付け、色だけに頼らない (ZN-29)。
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
OUT = os.path.join(OUT_DIR, "cores.gif")
SC = 4 / 3
FPS = 2
EDGE = (70, 74, 80)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)
YEL = (251, 211, 50)
RANK = [(40, 150, 240), (240, 110, 150), (60, 200, 170), (240, 190, 60)]
GRP = [(150, 110, 230), (255, 160, 60)]   # the 2 groups of a rank


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def rbox(g, x, y, w, h, fill, outline, wd=2, r=8):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=r * SC, fill=fill, outline=outline, width=int(wd * SC))


def canvas(cap):
    img = Image.new("RGB", (int(960 * SC), int(560 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(30, 46), cap, font=F(26), fill=YEL, anchor="lm")
    return img, g


# chip: 8 physical cores in 4 pairs
CX, CY = 32, 100
PW, PH, GAP = 92, 120, 10


def core_xy(k):
    pair, side = divmod(k, 2)
    return CX + pair * (2 * PW + GAP + 40) + side * (PW + GAP), CY + 40


def chip(g, logical=False, ranks=False, hl_pair=None):
    rbox(g, CX - 16, CY, 4 * (2 * PW + GAP) + 3 * 40 + 32, PH + 110, CHIP, EDGE, wd=1.5, r=12)
    g.text(P(CX, CY + 16), "Trainium2 chip (trn2.3xlarge)", font=F(14), fill=MUTED, anchor="lm")
    for k in range(8):
        x, y = core_xy(k)
        pair = k // 2
        dim = hl_pair is not None and pair != hl_pair
        col = RANK[pair] if ranks else EDGE
        fill = mix(BG, col, 0.25 if not dim else 0.08) if ranks else (30, 34, 40)
        rbox(g, x, y, PW, PH, fill, col if not dim else EDGE, wd=2)
        g.text(P(x + PW / 2, y + 22), f"core {k}", font=F(13), fill=TX if not dim else MUTED, anchor="mm")
    if logical:
        for p in range(4):
            x, y = core_xy(2 * p)
            dim = hl_pair is not None and p != hl_pair
            g.rounded_rectangle([P(x - 6, y - 6), P(x + 2 * PW + GAP + 6, y + PH + 6)], radius=10 * SC,
                                outline=WHITE if not dim else EDGE, width=int((3 if not dim else 1) * SC))
            g.text(P(x + PW + GAP / 2, y + PH + 22), f"logical core {p}", font=F(14), fill=TX if not dim else MUTED, anchor="mm")
            if ranks:
                g.text(P(x + PW + GAP / 2, y + PH + 48), f"TP rank {p}", font=F(14), fill=RANK[p] if not dim else MUTED, anchor="mm")


def heads_row(g, y, upto_rank=None, show_groups=False, hl_rank=None):
    """64 Mamba2 heads in a row, colored by TP rank, grouped by 8."""
    x0, w = 40, 13.6
    g.text(P(x0, y - 18), "64 Mamba2 heads", font=F(14), fill=MUTED, anchor="lm")
    for h in range(64):
        r = h // 16
        gr = (h // 8) % 2
        on = upto_rank is not None and r <= upto_rank
        dim = hl_rank is not None and r != hl_rank
        col = RANK[r] if on else EDGE
        if on and show_groups and not dim:
            col = GRP[gr]
        fill = mix(BG, col, 0.5 if not dim else 0.12)
        g.rectangle([P(x0 + h * w, y), P(x0 + h * w + w - 2, y + 30)], fill=fill, outline=None)
    if show_groups:
        for gi in range(8):
            xa = x0 + gi * 8 * w
            dim = hl_rank is not None and gi // 2 != hl_rank
            g.text(P(xa + 4 * w, y + 46), f"group {gi}", font=F(12), fill=MUTED if dim else TX, anchor="mm")
            g.line([P(xa, y + 34), P(xa + 8 * w - 3, y + 34)], fill=MUTED, width=int(1 * SC))


frames = []


def hold(img, n):
    frames.extend([img] * n)


img, g = canvas("8 physical cores on one chip")
chip(g)
hold(img, 6)

img, g = canvas("LNC=2: 2 physical cores = 1 logical core")
chip(g, logical=True)
hold(img, 6)

img, g = canvas("TP=4: one logical core per TP rank")
chip(g, logical=True, ranks=True)
hold(img, 6)

for r in range(4):
    img, g = canvas(f"rank {r} gets 16 of the 64 heads")
    chip(g, logical=True, ranks=True, hl_pair=r)
    heads_row(g, 400, upto_rank=r, hl_rank=r)
    hold(img, 3)

img, g = canvas("8 heads share one B and C: a group")
chip(g, logical=True, ranks=True)
heads_row(g, 400, upto_rank=3, show_groups=True)
hold(img, 8)

# rank 0 close-up: group 0 -> core 0, group 1 -> core 1
img, g = canvas("Mamba2 layer: one group per core")
chip(g, logical=True, ranks=True, hl_pair=0)
heads_row(g, 400, upto_rank=3, show_groups=True, hl_rank=0)
for k, gi in ((0, 0), (1, 1)):
    x, y = core_xy(k)
    rbox(g, x + 5, y + 44, PW - 10, 60, mix(BG, GRP[gi], 0.5), GRP[gi], wd=2)
    g.text(P(x + PW / 2, y + 64), f"8 heads", font=F(12), fill=TX, anchor="mm")
    g.text(P(x + PW / 2, y + 86), f"B, C of g{gi}", font=F(10), fill=TX, anchor="mm")
hold(img, 8)

img, g = canvas("Mamba2 layer: no data between cores")
chip(g, logical=True, ranks=True, hl_pair=0)
for k, gi in ((0, 0), (1, 1)):
    x, y = core_xy(k)
    rbox(g, x + 5, y + 44, PW - 10, 60, mix(BG, GRP[gi], 0.5), GRP[gi], wd=2)
    g.text(P(x + PW / 2, y + 64), f"8 heads", font=F(12), fill=TX, anchor="mm")
    g.text(P(x + PW / 2, y + 86), f"B, C of g{gi}", font=F(10), fill=TX, anchor="mm")
x0, y0 = core_xy(0)
g.text(P(40, y0 + PH + 100), "no transfer between core 0 and core 1", font=F(15), fill=WHITE, anchor="lm")
g.text(P(40, 420), "a head only needs its own group's B and C", font=F(18), fill=TX, anchor="lm")
hold(img, 8)

img, g = canvas("MoE layer: same 6 experts, half each")
chip(g, logical=True, ranks=True, hl_pair=0)
for k, lab in ((0, "half"), (1, "half")):
    x, y = core_xy(k)
    rbox(g, x + 10, y + 46, PW - 20, 56, (30, 34, 40), WHITE, wd=2)
    g.text(P(x + PW / 2, y + 74), lab, font=F(14), fill=TX, anchor="mm")
g.text(P(40, 420), "each core: half of each chosen expert's inner size", font=F(17), fill=TX, anchor="lm")
g.text(P(40, 452), "then add the two halves", font=F(17), fill=TX, anchor="lm")
hold(img, 10)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=96) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    k = 0
    for i in range(1, len(frames)):
        if frames[i] is frames[i - 1] and (i + 1 == len(frames) or frames[i + 1] is not frames[i]):
            frames[i].save(os.path.join(OUT_DIR, f"c{k:02d}.png"))
            k += 1
