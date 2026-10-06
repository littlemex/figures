"""gen_dkms_gif.py -- DKMS がソースを登録し、カーネルごとにビルドして組み込むまでを 5 場面で見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_dkms_gif.py

1 /usr/src/<名前>-<版>/ にソースと dkms.conf を置く
2 dkms add で登録する (/var/lib/dkms/<名前>/<版>/)
3 dkms build -k <カーネル> で、そのカーネルのヘッダ (/lib/modules/<カーネル>/build) を使ってビルドする
4 dkms install で、そのカーネルのモジュールの置き場所 (Ubuntu では updates/dkms) に入れる
5 新しいカーネルが入ると、パッケージのフックから dkms autoinstall が呼ばれ、新しいカーネル向けにも 3 と 4 が走る
根拠: dkms(8) (Ubuntu 24.04)、lustre_installer.sh (littlemex/distributed-ai 52fff76) の dkms add / build / install。
下の帯にその場面のコマンドを、その上に dkms status の出力を出す。図の文字は英語。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "dkms-lifecycle.gif")
SC = 4 / 3
FPS = 4
EDGE = (70, 74, 80)
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL, YEL_DK = (251, 211, 50), (80, 66, 14)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)
MONO = "/System/Library/Fonts/Menlo.ttc"
V = "lustre-client-modules"
K1, K2 = "6.8.0-1057-aws", "7.0.0-1012-aws"

CODE = {
    "1": "/usr/src/lustre-client-modules-2.15.6/   (source + dkms.conf)",
    "2": "dkms add -m lustre-client-modules -v 2.15.6",
    "3": f"dkms build -m lustre-client-modules -v 2.15.6 -k {K1}",
    "4": f"dkms install -m lustre-client-modules -v 2.15.6 -k {K1}",
    "5": "apt install linux-aws  ->  kernel hook  ->  dkms autoinstall",
}
STATUS = {
    "1": [],
    "2": [f"{V}/2.15.6: added"],
    "3": [f"{V}/2.15.6, {K1}, x86_64: built"],
    "4": [f"{V}/2.15.6, {K1}, x86_64: installed"],
    "5": [f"{V}/2.15.6, {K1}, x86_64: installed", f"{V}/2.15.6, {K2}, x86_64: installed"],
}
_MONO = {}


def M(n):
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


def path(g, pts, col, u=1.0, wd=3):
    """折れ線 pts を先頭から割合 u だけ描き、先端に線の向きに合わせた矢じりを付ける。"""
    import math
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    left = sum(lens) * max(0.0, min(1.0, u))
    drawn = [pts[0]]
    for (a, b), L in zip(segs, lens):
        if left <= 0:
            break
        t = min(1.0, left / L) if L else 1.0
        drawn.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        left -= L
    if len(drawn) < 2:
        return
    g.line([P(*q) for q in drawn], fill=col, width=int(wd * SC), joint="curve")
    (xa, ya), (xb, yb) = drawn[-2], drawn[-1]
    ang = math.atan2(yb - ya, xb - xa)
    head = [(xb, yb),
            (xb - 12 * math.cos(ang) + 7 * math.sin(ang), yb - 12 * math.sin(ang) - 7 * math.cos(ang)),
            (xb - 12 * math.cos(ang) - 7 * math.sin(ang), yb - 12 * math.sin(ang) + 7 * math.cos(ang))]
    g.polygon([P(*q) for q in head], fill=col)


SRC = (30, 120, 250, 150)
REG = (320, 120, 250, 150)
MOD1 = (640, 110, 290, 120)
MOD2 = (640, 250, 290, 120)


def panel(g, r, head, sub, on, fill=BLU_DK, edge=BLU):
    x, y, w, h = r
    rbox(g, x, y, w, h, fill if on else CHIP, edge if on else EDGE)
    g.text(P(x + 12, y + 18), head, font=M(12), fill=TX if on else MUTED, anchor="lm")
    for i, line in enumerate(sub):
        g.text(P(x + 12, y + 50 + i * 22), line, font=M(12), fill=TX if on else MUTED, anchor="lm")


def base(g, cap, src=False, reg=False, built=False, mod1=False, mod2=None):
    g.text(P(30, 46), cap, font=F(26), fill=YEL, anchor="lm")
    panel(g, SRC, "/usr/src/", ["lustre-client-", "modules-2.15.6/", "source + dkms.conf"], src, GRN_DK, GRN)
    panel(g, REG, "/var/lib/dkms/", ["registered 2.15.6"] + (["build/  ->  lustre.ko"] if built else []), reg)
    panel(g, MOD1, f"/lib/modules/{K1}/", ["build/  (headers)"] + (["updates/dkms/lustre.ko"] if mod1 else []), True,
          CHIP, EDGE)
    if mod2 is not None:
        panel(g, MOD2, f"/lib/modules/{K2}/", ["build/  (headers)"] + (["updates/dkms/lustre.ko"] if mod2 else []), True,
              YEL_DK, YEL)
    key = cap.split()[0]
    y = 400
    g.text(P(30, y), "$ dkms status", font=M(12), fill=MUTED, anchor="lm")
    for i, line in enumerate(STATUS[key]):
        g.text(P(30, y + 22 + i * 20), line, font=M(12), fill=TX, anchor="lm")
    g.rounded_rectangle([P(30, 480), P(930, 522)], radius=8 * SC, fill=(14, 18, 22), outline=EDGE, width=int(1 * SC))
    g.text(P(46, 501), CODE[key], font=M(13), fill=TX, anchor="lm")


frames = []


def scene(steps, hold, draw):
    for f in range(steps):
        img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
        g = ImageDraw.Draw(img)
        draw(g, f / max(1, steps - 1))
        frames.append(img)
    frames.extend([frames[-1]] * hold)


def s1(g, u):
    base(g, "1  put the source in /usr/src", src=u > 0.3)


def s2(g, u):
    base(g, "2  dkms add: register it", src=True, reg=u > 0.5)
    path(g, [(SRC[0] + SRC[2] + 2, 195), (REG[0] - 4, 195)], WHITE, u)


def s3(g, u):
    base(g, "3  dkms build for one kernel", src=True, reg=True, built=u >= 1)
    path(g, [(MOD1[0] - 2, 205), (REG[0] + REG[2] + 4, 205)], MUTED, u)
    g.text(P((MOD1[0] + REG[0] + REG[2]) / 2, 222), "headers", font=M(11), fill=MUTED, anchor="mm")


def s4(g, u):
    base(g, "4  dkms install into that kernel", src=True, reg=True, built=True, mod1=u >= 1)
    path(g, [(REG[0] + REG[2] + 2, 160), (MOD1[0] - 4, 160)], WHITE, u)
    g.text(P((MOD1[0] + REG[0] + REG[2]) / 2, 143), "lustre.ko", font=M(11), fill=MUTED, anchor="mm")


def s5(g, u):
    base(g, "5  a new kernel arrives: rebuilt", src=True, reg=True, built=True, mod1=True, mod2=u >= 1)
    xm = (MOD2[0] + REG[0] + REG[2]) / 2
    path(g, [(REG[0] + REG[2] + 2, 245), (xm, 245), (xm, 310), (MOD2[0] - 4, 310)], YEL, u)


for fn, steps, hold in ((s1, 4, 10), (s2, 8, 10), (s3, 8, 10), (s4, 8, 10), (s5, 10, 16)):
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
