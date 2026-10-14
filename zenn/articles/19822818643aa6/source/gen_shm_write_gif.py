"""gen_shm_write_gif.py -- the shm write, with the receiver doing the actual copy.

    OUT_DIR=<出力先> /usr/bin/python3 gen_shm_write_gif.py

1. 送信側は CUDA IPC ハンドルをエクスポートするだけで、まだ何もコピーしない
2. ハンドル付きのコマンドが受信側のコマンドキューに積まれる (混雑時は積み上がる)
3. 受信側の進行ループ(fi_cq_read の中)が動き、ハンドルを開いて GPU 間コピーを同期的に実行する。
   この間、同じロック(ep_mutex_)を新規書き込みの発行(postWrite)も必要とするため、
   送信側の別スレッドが新しい書き込みを出そうとすると、ロックの取得待ちで止まる
4. コピーが終わると送信側の領域にあるステータスフラグが立つ
5. 送信側自身の次の fi_cq_read がそのフラグに気づき、書き込みを完了させる
色: 緑 = SGLang (アプリ層プロセス)、青 = NIXL / UCX / libfabric、黄 = EFA ハードウェアと注意点、
赤 = ロック待ちで止まっている状態。
根拠: 記事本文、libfabric smr_rma.c#L335 / smr_ep.c#L553-L611 / smr_progress.c#L522-L597、
NIXL libfabric_rail.cpp#L722-L725 / #L1129 (commit 5a13558c2fcea15f1a6c4e8c06dc702e50724cf8 /
05e4243f5ed305a245912361ace20ba354ec0808)。図の文字は英語。
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
OUT = os.path.join(OUT_DIR, "shm-write-sequence.gif")
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
RED = (220, 38, 88)
RED_DK = (80, 24, 24)
CHIP = (22, 26, 30)
EDGE = (70, 74, 80)

SENDER = (60, 100, 280, 56)
EXPORT = (60, 186, 280, 56)
SCOMPLETE = (60, 352, 280, 56)
FLAGBOX = (60, 268, 280, 56)

RECEIVER = (620, 100, 280, 56)
QUEUE = (620, 186, 280, 90)
PROGRESS = (620, 306, 280, 56)
COPY = (620, 392, 280, 60)


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, r, fill, outline, text=None, size=14, col=TX, wd=2):
    x, y, w, h = r
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(wd * SC))
    if text:
        g.multiline_text(P(x + w / 2, y + h / 2), text, font=st.font(size), fill=col,
                         anchor="mm", align="center", spacing=6 * SC)


def dot(g, x, y, col, r=7):
    g.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=col, outline=BG, width=int(2 * SC))


def varrow(g, x, y0, y1, col):
    g.line([P(x, y0), P(x, y1)], fill=col, width=int(2 * SC))
    g.polygon([P(x, y1), P(x - 6, y1 - 10), P(x + 6, y1 - 10)], fill=col)


def harrow(g, x0, x1, y, col, dashed=False):
    tip = -10 if x1 >= x0 else 10
    if dashed:
        n = 10
        for i in range(n):
            if i % 2:
                continue
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            g.line([P(xa, y), P(xb, y)], fill=col, width=int(2 * SC))
    else:
        g.line([P(x0, y), P(x1, y)], fill=col, width=int(2 * SC))
    g.polygon([P(x1, y), P(x1 + tip, y - 6), P(x1 + tip, y + 6)], fill=col)


def base(phase, sub, queue_n=0, blocked=False, copy_lit=False, flag_lit=False, done_lit=False):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 36), "The shm write: who copies, who completes", font=st.font(21), fill=TX, anchor="lm")
    g.text(P(40, 70), f"{phase}  {sub}", font=st.font(13), fill=MUTED, anchor="lm")
    # skeleton
    harrow(g, EXPORT[0] + EXPORT[2], QUEUE[0], EXPORT[1] + EXPORT[3] / 2, (90, 94, 100))
    varrow(g, QUEUE[0] + QUEUE[2] / 2, QUEUE[1] + QUEUE[3], PROGRESS[1], (90, 94, 100))
    varrow(g, PROGRESS[0] + PROGRESS[2] / 2, PROGRESS[1] + PROGRESS[3], COPY[1], (90, 94, 100))
    harrow(g, COPY[0], FLAGBOX[0] + FLAGBOX[2], COPY[1] + COPY[3] / 2, (90, 94, 100), dashed=True)
    varrow(g, FLAGBOX[0] + FLAGBOX[2] / 2, FLAGBOX[1] + FLAGBOX[3], SCOMPLETE[1], (90, 94, 100))
    rbox(g, SENDER, GRN_DK, GRN, "Sender process\nGPU buffer", 13)
    rbox(g, RECEIVER, GRN_DK, GRN, "Receiver process\nGPU buffer", 13)
    rbox(g, EXPORT, (RED_DK if blocked else LINK_DK), (RED if blocked else LINK),
        ("new write blocked\non ep_mutex_" if blocked else "exports IPC handle\n(no copy here)"), 12,
        col=(RED if blocked else TX))
    qx, qy, qw, qh = QUEUE
    rbox(g, QUEUE, CHIP, EDGE, None)
    g.text(P(qx + qw / 2, qy + 14), "command queue (handle + cmd)", font=st.font(11), fill=MUTED, anchor="mm")
    chip_h, chip_gap = 13, 2
    for k in range(queue_n):
        cy = qy + qh - 8 - (k + 1) * (chip_h + chip_gap)
        if cy < qy + 28:
            break
        g.rounded_rectangle([P(qx + 14, cy), P(qx + qw - 14, cy + chip_h)], radius=3 * SC,
                            fill=YEL_DK, outline=YEL, width=int(1.5 * SC))
    rbox(g, PROGRESS, (LINK if copy_lit else LINK_DK), LINK, "receiver's progress loop\n(inside fi_cq_read)", 12,
        col=(CHIP if copy_lit else TX))
    rbox(g, COPY, (YEL if copy_lit else YEL_DK), YEL, "GPU-to-GPU copy\n(synchronous)", 12,
        col=(CHIP if copy_lit else TX))
    rbox(g, FLAGBOX, (GRN_HI if flag_lit else CHIP), (GRN_HI if flag_lit else EDGE),
        "status flag flips\n(sender's own region)", 12, col=(CHIP if flag_lit else MUTED))
    rbox(g, SCOMPLETE, (GRN_HI if done_lit else CHIP), (GRN_HI if done_lit else EDGE),
        "sender's next fi_cq_read\nnotices it, completes", 12, col=(CHIP if done_lit else MUTED))
    return img, g


frames = []

# 1. sender exports a handle (no copy), it travels into the receiver's queue
for f in range(16):
    u = ease(f / 15)
    img, g = base("1.", "sender exports a CUDA IPC handle -- not a copy")
    sx, sy = EXPORT[0] + EXPORT[2], EXPORT[1] + EXPORT[3] / 2
    qx, qy = QUEUE[0], QUEUE[1] + 40
    dot(g, sx + (qx - sx) * u, sy + (qy - sy) * u, LINK)
    frames.append(img)
img1, _ = base("1.", "queue depth: 1", queue_n=1)
for _ in range(6):
    frames.append(img1)

# 2. congestion: more handles arrive, and a second writer thread is blocked on ep_mutex_
for n in range(1, 6):
    img, g = base("2.", f"under load, more handles arrive (queue depth {n})", queue_n=n)
    frames.append(img)
    frames.append(img)
img2, _ = base("2.", "a new write now waits for ep_mutex_", queue_n=5, blocked=True)
for _ in range(10):
    frames.append(img2)

# 3. receiver's own progress loop drains one entry and performs the real copy
for f in range(8):
    u = ease(f / 7)
    img, g = base("3.", "receiver's progress loop opens the handle", queue_n=4, blocked=True)
    frames.append(img)
img3, _ = base("3.", "copying GPU-to-GPU, synchronously -- could be what holds ep_mutex_",
               queue_n=4, blocked=True, copy_lit=True)
for _ in range(14):
    frames.append(img3)

# 4. copy finishes: the status flag flips in the sender's own region, and the blocked writer unblocks
img4, _ = base("4.", "copy done: status flag flips in the sender's region", queue_n=3, flag_lit=True)
for _ in range(8):
    frames.append(img4)
for f in range(14):
    u = ease(f / 13)
    img, g = base("4.", "status flag crosses back to the sender's side", queue_n=3, flag_lit=True)
    x0, y0 = COPY[0], COPY[1] + COPY[3] / 2
    x1, y1 = FLAGBOX[0] + FLAGBOX[2], FLAGBOX[1] + FLAGBOX[3] / 2
    dot(g, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, GRN_HI)
    frames.append(img)
for _ in range(4):
    frames.append(frames[-1])

# 5. sender's own next fi_cq_read notices it and completes; the blocked writer is free again
img5, _ = base("5.", "sender's own progress notices the flag, completes the write", flag_lit=True, done_lit=True)
for _ in range(10):
    frames.append(img5)
img6, _ = base("6.", "ep_mutex_ is free again; the blocked writer can post now", done_lit=True)
for _ in range(10):
    frames.append(img6)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.1f}s")
if os.environ.get("DUMP"):
    for i in (0, len(frames) // 5, 2 * len(frames) // 5, 3 * len(frames) // 5, 4 * len(frames) // 5, len(frames) - 1):
        frames[i].save(os.path.join(OUT_DIR, f"shm-write-m{i}.png"))
