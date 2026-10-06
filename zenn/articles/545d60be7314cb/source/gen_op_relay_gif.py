"""gen_op_relay_gif.py -- Tiny の forward の 3 行が、FX graph のノード、HLO の演算へと姿を変える様子を 1 行ずつ見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_op_relay_gif.py

1 Python の 3 行
2 FX graph: 1 行 = 1 ノード (linear, relu, add)。PyTorch の語彙のまま
3 HLO: より小さな演算へ (dot + add, maximum, add + broadcast)
4 名前 (a, b) は消え、形 (f32[2,3]) で追う
根拠: 記事の CPU 観察 (vLLM Neuron v0.21.0.1.0.0) の fxgraph.txt と graph.hlo。図の文字は英語。
行には 1〜3 の番号を振り、色だけに頼らない (ZN-29)。
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
OUT = os.path.join(OUT_DIR, "op-relay.gif")
SC = 4 / 3
FPS = 4
EDGE = (70, 74, 80)
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL = (251, 211, 50)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)
MONO = "/System/Library/Fonts/Menlo.ttc"

COLS = (("Python", 30), ("FX graph", 320), ("HLO", 610))
CW = 250
ROWS = (150, 270, 390)
RH = 76
PY = ("a = self.fc(x)", "b = torch.relu(a)", "return b + 1.0")
FX = ("linear", "relu", "add")
HLO = (("dot(x, Wᵀ)", "add(+ broadcast bias)"), ("maximum(·, 0)",), ("add(+ broadcast 1.0)",))
SHAPE = "f32[2,3]"

_MONO = {}


def M(n):
    from PIL import ImageFont
    k = round(n * SC)
    if k not in _MONO:
        _MONO[k] = ImageFont.truetype(MONO, k)
    return _MONO[k]


def P(x, y):
    return (x * SC, y * SC)


def F(n):
    return s.font(n)


def rbox(g, x, y, w, h, fill, outline, wd=2):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline, width=int(wd * SC))


def arrow(g, x0, y0, x1, y1, col, wd=3):
    g.line([P(x0, y0), P(x1, y1)], fill=col, width=int(wd * SC))
    g.polygon([P(x1, y1), P(x1 - 12, y1 - 7), P(x1 - 12, y1 + 7)], fill=col)


def vdown(g, x, y0, y1, col):
    g.line([P(x, y0), P(x, y1)], fill=col, width=int(2 * SC))
    g.polygon([P(x, y1), P(x - 6, y1 - 10), P(x + 6, y1 - 10)], fill=col)


def base(g, cap, on):
    g.text(P(30, 46), cap, font=F(26), fill=YEL, anchor="lm")
    for i, (nm, x) in enumerate(COLS):
        g.text(P(x + CW / 2, 110), nm, font=F(18), fill=TX if i <= on else MUTED, anchor="mm")


def tag(g, x, y, k):
    g.ellipse([P(x - 13, y - 13), P(x + 13, y + 13)], fill=CHIP, outline=MUTED, width=int(1.5 * SC))
    g.text(P(x, y), str(k + 1), font=F(14), fill=TX, anchor="mm")


def py_col(g, u, dim=False):
    x = COLS[0][1]
    for k, line in enumerate(PY):
        y = ROWS[k]
        rbox(g, x, y, CW, RH, GRN_DK, GRN if not dim else EDGE)
        g.text(P(x + 22, y + RH / 2), line, font=M(17), fill=TX if not dim else MUTED, anchor="lm")
        tag(g, x, y, k)


def fx_col(g, u, dim=False):
    x = COLS[1][1]
    for k, nm in enumerate(FX):
        y = ROWS[k]
        t = max(0.0, min(1.0, u * 3 - k))
        if t <= 0:
            continue
        rbox(g, x, y, CW, RH, mix(BG, BLU_DK, t), mix(BG, BLU if not dim else EDGE, t))
        g.text(P(x + CW / 2, y + RH / 2), nm, font=M(20), fill=mix(BG, TX if not dim else MUTED, t), anchor="mm")
        tag(g, x, y, k)
        arrow(g, COLS[0][1] + CW + 4, y + RH / 2, COLS[0][1] + CW + 4 + (x - COLS[0][1] - CW - 10) * t, y + RH / 2,
              mix(BG, MUTED, t))
        if k > 0 and t >= 1:
            vdown(g, x + CW / 2, ROWS[k - 1] + RH, y, MUTED)


def hlo_col(g, u, shapes=False):
    x = COLS[2][1]
    for k, ops in enumerate(HLO):
        y = ROWS[k]
        t = max(0.0, min(1.0, u * 3 - k))
        if t <= 0:
            continue
        h = (RH - 8 * (len(ops) - 1)) / len(ops)
        for j, op in enumerate(ops):
            yy = y + j * (h + 8)
            rbox(g, x, yy, CW, h, mix(BG, BLU_DK, t), mix(BG, BLU, t))
            g.text(P(x + CW / 2, yy + h / 2), op, font=M(16), fill=mix(BG, TX, t), anchor="mm")
        tag(g, x, y, k)
        arrow(g, COLS[1][1] + CW + 4, y + RH / 2, COLS[1][1] + CW + 4 + (x - COLS[1][1] - CW - 10) * t, y + RH / 2,
              mix(BG, MUTED, t))
        if shapes:
            g.text(P(x + CW + 8, y + RH / 2), SHAPE, font=M(13), fill=YEL, anchor="lm")


frames = []


def scene(steps, hold, draw):
    for f in range(steps):
        img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
        g = ImageDraw.Draw(img)
        draw(g, f / max(1, steps - 1))
        frames.append(img)
    frames.extend([frames[-1]] * hold)


def s1(g, u):
    base(g, "1  three lines of forward", 0)
    py_col(g, u)


def s2(g, u):
    base(g, "2  FX graph of Tiny: one node per line", 1)
    py_col(g, 1)
    fx_col(g, u)


def s3(g, u):
    base(g, "3  HLO: smaller, basic ops", 2)
    py_col(g, 1)
    fx_col(g, 1)
    hlo_col(g, u)


def s4(g, u):
    base(g, "4  names fade, shapes stay", 2)
    py_col(g, 1, dim=True)
    fx_col(g, 1, dim=True)
    hlo_col(g, 1, shapes=u > 0.3)


for fn, steps, hold in ((s1, 2, 8), (s2, 12, 10), (s3, 12, 12), (s4, 6, 12)):
    scene(steps, hold, fn)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.0f}s")
if os.environ.get("DUMP"):
    k = 0
    for i in range(1, len(frames)):
        if frames[i] is frames[i - 1] and (i + 1 == len(frames) or frames[i + 1] is not frames[i]):
            frames[i].save(os.path.join(OUT_DIR, f"m{k}.png"))
            k += 1
