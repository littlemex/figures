"""gen_ring_gif.py -- NVSHMEM のリング通信 (ring.cu) を、コードの行の順に 5 場面で見せる GIF。

    OUT_DIR=<出力先> DUMP=1 /usr/bin/python3 gen_ring_gif.py

1 nvshmem_init と cudaSetDevice: PE k がノードの中の GPU k を選ぶ
2 nvshmem_malloc: 全 PE に dst が確保される (出口でバリア)
3 ring_put カーネル: PE k が自分の番号を PE (k+1) % npes の dst に put する
4 cudaDeviceSynchronize と nvshmem_barrier_all: 全 PE がそろうまで待つ
5 cudaMemcpy で dst を CPU に写して表示する
4 PE で描く。下の帯に、その場面で動くコードの行を出す。図の文字は英語。
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
OUT = os.path.join(OUT_DIR, "ring-put.gif")
SC = 4 / 3
FPS = 4
EDGE = (70, 74, 80)
GRN, GRN_DK = (59, 209, 111), (18, 64, 34)
BLU, BLU_DK = (40, 150, 240), (16, 44, 72)
YEL, YEL_DK = (251, 211, 50), (80, 66, 14)
CHIP = (22, 26, 30)
WHITE = (255, 255, 255)
MONO = "/System/Library/Fonts/Menlo.ttc"
N = 4
PX, PW, PY, PH = 60, 180, 120, 230
STEP = 220

CODE = {
    "1": "nvshmem_init();  cudaSetDevice(nvshmem_team_my_pe(NVSHMEMX_TEAM_NODE));",
    "2": "int *dst = (int *)nvshmem_malloc(sizeof(int));",
    "3": "nvshmem_int_p(dst, mype, peer);     peer = (mype + 1) % npes",
    "4": "cudaDeviceSynchronize();  nvshmem_barrier_all();",
    "5": "cudaMemcpy(&value, dst, ...);  printf(\"PE %d ... %d\", mype, value);",
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


def arrow(g, pts, col, wd=3):
    g.line([P(*p) for p in pts], fill=col, width=int(wd * SC), joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    if x1 != x0:
        dx = 12 if x1 > x0 else -12
        g.polygon([P(x1, y1), P(x1 - dx, y1 - 7), P(x1 - dx, y1 + 7)], fill=col)
    else:
        dy = 12 if y1 > y0 else -12
        g.polygon([P(x1, y1), P(x1 - 7, y1 - dy), P(x1 + 7, y1 - dy)], fill=col)


def px(k):
    return PX + k * STEP


def base(g, cap, gpu=True, dst=None, recv=None):
    g.text(P(30, 46), cap, font=F(26), fill=YEL, anchor="lm")
    for k in range(N):
        x = px(k)
        rbox(g, x, PY, PW, PH, BLU_DK if gpu else CHIP, BLU if gpu else EDGE)
        g.text(P(x + PW / 2, PY + 22), f"PE {k}", font=F(18), fill=TX, anchor="mm")
        if gpu:
            g.text(P(x + PW / 2, PY + 66), f"GPU {k}", font=F(14), fill=MUTED, anchor="mm")
        if dst is not None:
            t = dst
            rbox(g, x + 25, PY + 120, PW - 50, 70, mix(BG, GRN_DK, t), mix(BG, GRN, t))
            g.text(P(x + PW / 2, PY + 138), "dst", font=F(14), fill=mix(BG, MUTED, t), anchor="mm")
            if recv is not None and recv[k] is not None:
                g.text(P(x + PW / 2, PY + 168), str(recv[k]), font=M(22), fill=TX, anchor="mm")
    g.rounded_rectangle([P(30, 470), P(930, 515)], radius=8 * SC, fill=(14, 18, 22), outline=EDGE, width=int(1 * SC))
    g.text(P(46, 492), CODE[cap.split()[0]], font=M(13), fill=TX, anchor="lm")


frames = []


def scene(steps, hold, draw):
    for f in range(steps):
        img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
        g = ImageDraw.Draw(img)
        draw(g, f / max(1, steps - 1))
        frames.append(img)
    frames.extend([frames[-1]] * hold)


def s1(g, u):
    base(g, "1  each PE picks its GPU", gpu=u > 0.4)


def s2(g, u):
    base(g, "2  dst on every PE", dst=u)
    if u >= 1:
        g.text(P(480, 420), "same call on every PE; returns after a barrier", font=F(15), fill=MUTED, anchor="mm")


def recv_at(u):
    k_done = int(u * N + 1e-6)
    r = [None] * N
    for k in range(min(k_done, N)):
        r[(k + 1) % N] = k
    return r, k_done


def s3(g, u):
    r, k_done = recv_at(u)
    base(g, "3  kernel: put mype into the next PE", dst=1)
    k = min(N - 1, k_done) if u < 1 else N - 1
    for j in range(N):
        on = j == k and u < 1
        col = WHITE if on else (MUTED if j < k_done else None)
        if col is None:
            continue
        if j < N - 1:
            arrow(g, [(px(j) + PW - 20, PY + 155), (px(j + 1) + 20, PY + 155)], col)
        else:
            y = PY + PH + 30
            arrow(g, [(px(j) + PW / 2, PY + PH), (px(j) + PW / 2, y), (px(0) + PW / 2, y), (px(0) + PW / 2, PY + PH + 2)], col)
    g.text(P(480, 430), "puts in flight; PE 3 wraps to PE 0", font=F(15), fill=MUTED, anchor="mm")


def s4(g, u):
    base(g, "4  wait for every PE", dst=1)
    y = PY + PH + 40
    g.line([P(px(0), y), P(px(0) + (px(N - 1) + PW - px(0)) * u, y)], fill=YEL, width=int(4 * SC))
    if u >= 1:
        g.text(P(480, y + 24), "barrier", font=F(15), fill=YEL, anchor="mm")


def s5(g, u):
    base(g, "5  copy dst to the host and print", dst=1, recv=[3, 0, 1, 2] if u > 0 else None)
    for k, v in enumerate([3, 0, 1, 2]):
        if u > k / N:
            g.text(P(px(k) + PW / 2, PY + PH + 40), f"PE {k} got {v}", font=M(14), fill=TX, anchor="mm")


for fn, steps, hold in ((s1, 4, 10), (s2, 6, 12), (s3, 16, 12), (s4, 6, 10), (s5, 8, 14)):
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
    frames[44].save(os.path.join(OUT_DIR, "mid.png"))
