"""gen_shm_off_gif.py -- FI_EFA_ENABLE_SHM_TRANSFER=0 のときの経路を見せる GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_shm_off_gif.py

1. shm_ep が作られない (efa_shm_info_create() が早期に戻る)
2. 送信側が efa_rdm_rma_post_write() で RDMA WRITE を発行する
3. RDMA WRITE はノードに 2 枚あるうち同じ 1 枚の EFA デバイスへ向かい、ループバックする
4. ハードウェアの完了 (IBV_WC_RDMA_WRITE) が送信側の完了キューに積まれる
色: 緑 = SGLang (アプリ層プロセス)、青 = NIXL / UCX / libfabric、黄 = EFA ハードウェアと注意点。
根拠: 記事本文、libfabric efa_shm.c#L68-L77 / efa_rdm_rma.c / efa_rdm_rma.h#L30-L66
(commit 5a13558c2fcea15f1a6c4e8c06dc702e50724cf8)。図の文字は英語。

レイアウト: 左列 = 送信側プロセスとその完了キュー、右列 = post_write から EFA デバイス、
受信側までの縦の経路。2 列は中心を揃え、右列は常に同じ x 幅で積む。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as st  # noqa: E402
from stack3d import TX, MUTED, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "shm-off-path.gif")
SC = 4 / 3
FPS = 12
BG = (0, 0, 0)
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
GRN_DK = (18, 64, 34)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
YEL_DK = (80, 66, 14)
CHIP = (22, 26, 30)
EDGE = (70, 74, 80)

# left column: sender + its own completion queue + the shm_ep note
SENDER = (60, 110, 300, 60)
CQ = (60, 196, 300, 60)
NOSHM = (60, 282, 300, 78)

# right column: post_write -> RDMA WRITE -> EFA device -> receiver, all centered at x=570
RCOL_X = 420
RCOL_W = 300
POSTWRITE = (RCOL_X, 110, RCOL_W, 60)
RDMA = (RCOL_X, 196, RCOL_W, 60)
EFA = (RCOL_X, 282, RCOL_W, 94)
RECEIVER = (RCOL_X, 412, RCOL_W, 60)


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, r, fill, outline, text=None, size=14, col=TX, wd=2):
    x, y, w, h = r
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(wd * SC))
    if text:
        g.multiline_text(P(x + w / 2, y + h / 2), text, font=st.font(size), fill=col,
                         anchor="mm", align="center", spacing=6 * SC)


def dot(g, x, y, col, r=8):
    g.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=col, outline=BG, width=int(2 * SC))


def varrow(g, x, y0, y1, col, wd=2):
    g.line([P(x, y0), P(x, y1)], fill=col, width=int(wd * SC))
    g.polygon([P(x, y1), P(x - 6, y1 - 10), P(x + 6, y1 - 10)], fill=col)


def loop_arc(g, box, col, frac=1.0, wd=3, pad=14):
    # a growing ellipse hugging the given (x, y, w, h) box, to show it looping back to itself
    x, y, w, h = box
    x0, y0 = P(x - pad, y - pad)
    x1, y1 = P(x + w + pad, y + h + pad)
    start = -90
    end = start + 350 * max(0.0, min(1.0, frac))
    g.arc([x0, y0, x1, y1], start=start, end=end, fill=col, width=int(wd * SC))


def base(phase, sub, cq_lit=False):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 32), "shm off: the hardware path", font=st.font(22), fill=TX, anchor="lm")
    g.text(P(40, 68), f"{phase}  {sub}", font=st.font(13), fill=MUTED, anchor="lm")
    # persistent skeleton: right column is one straight pipeline; left column stacks under sender
    varrow(g, RCOL_X + RCOL_W / 2, POSTWRITE[1] + POSTWRITE[3], RDMA[1], (90, 94, 100))
    varrow(g, RCOL_X + RCOL_W / 2, RDMA[1] + RDMA[3], EFA[1], (90, 94, 100))
    varrow(g, RCOL_X + RCOL_W / 2, EFA[1] + EFA[3], RECEIVER[1], (90, 94, 100))
    varrow(g, SENDER[0] + SENDER[2] / 2, SENDER[1] + SENDER[3], CQ[1], (90, 94, 100))
    rbox(g, SENDER, GRN_DK, GRN, "Sender process\nGPU buffer", 15)
    rbox(g, RECEIVER, GRN_DK, GRN, "Receiver process\nGPU buffer", 15)
    rbox(g, POSTWRITE, LINK_DK, LINK, "efa_rdm_rma_\npost_write()", 13)
    rbox(g, RDMA, YEL_DK, YEL, "RDMA WRITE", 14)
    rbox(g, EFA, YEL_DK, YEL, "EFA device (1 of 2)\nloopback to itself", 14)
    rbox(g, NOSHM, CHIP, EDGE, "shm_ep never created\n(efa_shm_info_create\nreturns early)", 11, col=MUTED)
    rbox(g, CQ, (YEL_DK if cq_lit else CHIP), (YEL if cq_lit else EDGE),
        "sender completion queue\nIBV_WC_RDMA_WRITE", 11, col=(YEL if cq_lit else MUTED))
    return img, g


frames = []

# 1. shm_ep never created (static beat; the causal link is stated in the caption, not drawn)
for f in range(14):
    img, g = base("1.", "no shm endpoint is created for this peer")
    frames.append(img)
for _ in range(6):
    frames.append(frames[-1])

# 2. sender posts the write
for f in range(16):
    u = ease(f / 15)
    img, g = base("2.", "sender posts efa_rdm_rma_post_write()")
    sx, sy = SENDER[0] + SENDER[2], SENDER[1] + SENDER[3] / 2
    px, py = POSTWRITE[0], POSTWRITE[1] + POSTWRITE[3] / 2
    dot(g, sx + (px - sx) * u, sy + (py - sy) * u, LINK)
    frames.append(img)
for _ in range(4):
    frames.append(frames[-1])

# 3. RDMA WRITE flows down to the EFA device and loops back
for f in range(16):
    u = ease(f / 15)
    img, g = base("3.", "RDMA WRITE goes to the node's EFA device")
    x0, y0 = POSTWRITE[0] + POSTWRITE[2] / 2, POSTWRITE[1] + POSTWRITE[3]
    x1, y1 = RDMA[0] + RDMA[2] / 2, RDMA[1] + RDMA[3] / 2
    dot(g, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, YEL)
    frames.append(img)
for f in range(16):
    u = ease(f / 15)
    img, g = base("3.", "the device loops back to itself")
    x0, y0 = RDMA[0] + RDMA[2] / 2, RDMA[1] + RDMA[3]
    x1, y1 = EFA[0] + EFA[2] / 2, EFA[1] + 18
    dot(g, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, YEL)
    if u > 0.5:
        loop_arc(g, EFA, YEL, frac=(u - 0.5) * 2)
    frames.append(img)
for _ in range(6):
    frames.append(frames[-1])

# 4. delivery to receiver + hardware completion on the sender's own completion queue
for f in range(16):
    u = ease(f / 15)
    img, g = base("4.", "the write lands in the receiver GPU buffer")
    x0, y0 = EFA[0] + EFA[2] / 2, EFA[1] + EFA[3]
    x1, y1 = RECEIVER[0] + RECEIVER[2] / 2, RECEIVER[1]
    dot(g, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, GRN_HI)
    frames.append(img)
for f in range(14):
    u = ease(f / 13)
    img, g = base("4.", "hardware completion reaches the sender's own queue",
                  cq_lit=u > 0.4)
    frames.append(img)
for _ in range(10):
    frames.append(frames[-1])

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.1f}s")
if os.environ.get("DUMP"):
    for i in (0, len(frames) // 5, 2 * len(frames) // 5, 3 * len(frames) // 5, 4 * len(frames) // 5, len(frames) - 1):
        frames[i].save(os.path.join(OUT_DIR, f"shm-off-m{i}.png"))
