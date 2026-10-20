"""cuda_ipc_gif.py: how libfabric's shm provider moves one GPU write with CUDA IPC, step by step.

    OUT_DIR=<dir> /usr/bin/python3 cuda_ipc_gif.py

Writes cuda-ipc.gif (animated) and cuda-ipc.png (all steps on one frame).
Figure text is English. Source: libfabric 5a13558c (prov/shm/src/smr_rma.c, smr_ep.c,
smr_progress.c, src/hmem_cuda.c, src/hmem_ipc_cache.c).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
SC = 4 / 3
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
GRN_DK = (18, 64, 34)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
YEL_DK = (80, 66, 14)
RED = (230, 80, 70)
RED_DK = (80, 24, 22)
DIM = (70, 74, 80)
CHIP = (22, 26, 30)

# logical layout 960 x 540
SND = (40, 108, 400)        # x, y, w of the sender column
RCV = (520, 108, 400)
THR_Y, THR_H = 128, 64      # thread boxes
SHM_Y, SHM_H = 252, 70      # host shared memory band
GPU_Y, GPU_H = 360, 84      # GPU memory boxes
CAP_Y = 462                 # step caption


_F = {}


def font(size):
    if size not in _F:
        _F[size] = ImageFont.truetype(s.EN, round(size * SC))
    return _F[size]


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, x, y, w, h, fill, outline, width=2):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(width * SC))


def text(g, x, y, body, size=14, col=TX, anchor="mm"):
    g.text(P(x, y), body, font=font(size), fill=col, anchor=anchor)


def arrow(g, a, b, col, width=3, dashed=False):
    ax, ay = a
    bx, by = b
    if dashed:
        n = 14
        for i in range(n):
            if i % 2 == 0:
                t0, t1 = i / n, (i + 1) / n
                g.line([P(ax + (bx - ax) * t0, ay + (by - ay) * t0),
                        P(ax + (bx - ax) * t1, ay + (by - ay) * t1)], fill=col, width=int(width * SC))
    else:
        g.line([P(ax, ay), P(bx, by)], fill=col, width=int(width * SC))
    import math
    ang = math.atan2(by - ay, bx - ax)
    L = 12
    p1 = (bx - L * math.cos(ang - 0.45), by - L * math.sin(ang - 0.45))
    p2 = (bx - L * math.cos(ang + 0.45), by - L * math.sin(ang + 0.45))
    g.polygon([P(bx, by), P(*p1), P(*p2)], fill=col)


def badge(g, x, y, n, show):
    if show is not None and n not in show:
        return
    g.ellipse([P(x - 11, y - 11), P(x + 11, y + 11)], fill=YEL, outline=BG, width=int(1.5 * SC))
    text(g, x, y, str(n), 12, BG)


def chip(g, x, y, body, fill=YEL_DK, outline=YEL, size=12, w=118, h=26):
    rbox(g, x - w / 2, y - h / 2, w, h, fill, outline, 1.5)
    text(g, x, y, body, size, TX)


def scene(step, sub, active=(), handle=False, cmd_pos=None, mapped=False, copy_t=None,
          copied=False, resp=False, done=False, fail=False, show=None):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    text(g, 40, 40, "CUDA IPC in libfabric's shm provider", 26, TX, "lm")
    text(g, 40, 74, "One RMA write of a GPU buffer from the sender to the receiver", 15, MUTED, "lm")

    # column titles
    text(g, SND[0] + SND[2] / 2, 108, "sender process (prefill TP rank)", 15, GRN_HI)
    text(g, RCV[0] + RCV[2] / 2, 108, "receiver process (decode TP rank)", 15, LINK)

    # thread boxes
    sa = "send" in active
    ra = "recv" in active
    rbox(g, SND[0], THR_Y, SND[2], THR_H, GRN_DK if sa else CHIP, GRN_HI if sa else DIM)
    text(g, SND[0] + SND[2] / 2, THR_Y + 20, "posting thread", 14, TX)
    text(g, SND[0] + SND[2] / 2, THR_Y + 44, "fi_writemsg -> smr_generic_rma", 12, MUTED)
    rbox(g, RCV[0], THR_Y, RCV[2], THR_H, LINK_DK if ra else CHIP, LINK if ra else DIM)
    text(g, RCV[0] + RCV[2] / 2, THR_Y + 20, "progress loop", 14, TX)
    text(g, RCV[0] + RCV[2] / 2, THR_Y + 44, "smr_progress_cmd -> smr_progress_ipc", 12, MUTED)

    # host shared memory band
    rbox(g, 30, SHM_Y - 18, 900, SHM_H + 26, BG, DIM, 1.5)
    text(g, 480, SHM_Y - 8, "host shared memory (mapped into both processes)", 12, MUTED)
    rbox(g, SND[0] + 20, SHM_Y + 8, SND[2] - 40, SHM_H - 16, CHIP, YEL if resp else DIM)
    text(g, SND[0] + SND[2] / 2, SHM_Y + 22, "sender's region: response queue", 12, MUTED)
    rbox(g, RCV[0] + 20, SHM_Y + 8, RCV[2] - 40, SHM_H - 16, CHIP, YEL if cmd_pos == 1.0 else DIM)
    text(g, RCV[0] + RCV[2] / 2, SHM_Y + 22, "receiver's region: command queue", 12, MUTED)

    # GPU boxes
    rbox(g, SND[0], GPU_Y, SND[2], GPU_H, CHIP, GRN)
    text(g, SND[0] + 14, GPU_Y + 14, "sender's GPU memory", 12, MUTED, "lm")
    rbox(g, RCV[0], GPU_Y, RCV[2], GPU_H, CHIP, LINK)
    text(g, RCV[0] + 14, GPU_Y + 14, "receiver's GPU memory", 12, MUTED, "lm")
    # sender allocation with the KV range inside
    ax, aw = SND[0] + 30, SND[2] - 60
    g.rectangle([P(ax, GPU_Y + 34), P(ax + aw, GPU_Y + 66)], fill=CHIP,
                outline=YEL if step in ("1", "1x") else DIM, width=int(1.5 * SC))
    kx, kw = ax + 110, 150
    g.rectangle([P(kx, GPU_Y + 38), P(kx + kw, GPU_Y + 62)], fill=GRN)
    text(g, kx + kw / 2, GPU_Y + 50, "KV cache (ptr, len)", 12, TX)
    text(g, ax, GPU_Y + 76, "base", 11, YEL if step in ("1", "1x") else MUTED, "lm")
    text(g, ax + aw, GPU_Y + 76, "allocation", 11, MUTED, "rm")
    # receiver destination
    dx, dw = RCV[0] + 125, 150
    g.rectangle([P(dx, GPU_Y + 38), P(dx + dw, GPU_Y + 62)],
                fill=LINK if copied else CHIP, outline=LINK, width=int(1.5 * SC))
    text(g, dx + dw / 2, GPU_Y + 50, "destination buffer", 12, TX)

    if step in ("1", "1x"):
        arrow(g, (SND[0] + 120, THR_Y + THR_H), (ax + 6, GPU_Y + 34), YEL if step == "1" else RED)
    if step in ("1", "1-6"):
        badge(g, ax - 12, GPU_Y + 50, 1, show)
    if handle:
        chip(g, SND[0] + SND[2] - 70, THR_Y + THR_H + 20, "IPC handle")
        badge(g, SND[0] + SND[2] - 140, THR_Y + THR_H + 20, 2, show)
    if cmd_pos is not None:
        x0, y0 = SND[0] + SND[2] - 70, THR_Y + THR_H + 20
        x1, y1 = RCV[0] + RCV[2] / 2, SHM_Y + 44
        t = cmd_pos
        chip(g, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, "cmd: handle+offset", w=150)
        if t == 1.0:
            badge(g, x1 - 92, y1, 3, show)
    if mapped:
        arrow(g, (RCV[0] + 60, THR_Y + THR_H), (kx + kw, GPU_Y + 40), LINK, 2.5, dashed=True)
        text(g, 560, GPU_Y - 16, "the opened handle maps the sender's buffer into the receiver", 11, LINK, "lm")
        badge(g, RCV[0] + 40, THR_Y + THR_H + 22, 4, show)
    if copy_t is not None:
        x0, x1 = kx + kw + 36, dx - 36
        y = GPU_Y + 50
        g.line([P(kx + kw, y), P(dx, y)], fill=LINK, width=int(2 * SC))
        cx = x0 + (x1 - x0) * copy_t
        rbox(g, cx - 34, y - 11, 68, 22, GRN, GRN_HI, 1.5)
        text(g, cx, y, "len bytes", 11, TX)
        badge(g, 480, y + 26, 5, show)
    if resp:
        chip(g, SND[0] + SND[2] / 2, SHM_Y + 46, "status: done", fill=GRN_DK, outline=GRN_HI)
        badge(g, SND[0] + SND[2] / 2 - 76, SHM_Y + 46, 6, show)
        if done:
            text(g, SND[0] + 90, THR_Y + THR_H + 20, "write complete", 13, GRN_HI)
    if fail:
        rbox(g, SND[0] + 10, THR_Y + THR_H + 4, SND[2] - 20, 30, RED_DK, RED, 1.5)
        text(g, SND[0] + SND[2] / 2, THR_Y + THR_H + 19, "CUDA_ERROR_NOT_FOUND", 13, TX)
        chip(g, RCV[0] + RCV[2] / 2, SHM_Y + 44, "switch to SAR", fill=RED_DK, outline=RED, w=140)

    # caption
    rbox(g, 30, CAP_Y, 900, 66, CHIP, YEL if step != "1x" else RED, 1.5)
    text(g, 50, CAP_Y + 20, step if step != "1x" else "1 fails", 16, YEL if step != "1x" else RED, "lm")
    text(g, 130, CAP_Y + 20, sub[0], 15, TX, "lm")
    text(g, 130, CAP_Y + 46, sub[1], 12, MUTED, "lm")
    return img


STEPS = [
    ("1", ("cuMemGetAddressRange(ptr): find the allocation's base and length",
           "runs in the posting thread's current CUDA context"), dict(active=("send",))),
    ("2", ("cudaIpcGetMemHandle(base): export a handle for that allocation",
           "the handle names the allocation; the offset of ptr is kept beside it"),
     dict(active=("send",), handle=True)),
    ("3", ("commit the command (handle, offset, size) in the receiver's command queue",
           "the slot was reserved first; the sender does not copy any data"), dict(active=("send",), cmd=True)),
    ("4", ("the receiver's progress loop opens the handle",
           "ofi_ipc_cache_search -> cudaIpcOpenMemHandle (cached per peer)"),
     dict(active=("recv",), cmd_at=1.0, mapped=True)),
    ("5", ("cudaMemcpy(dst, mapped + offset, len): read straight from the sender's buffer",
           "done by the receiver's thread inside its progress loop"), dict(active=("recv",), mapped=True, copy=True)),
    ("6", ("the receiver writes 'done' into the sender's response queue",
           "the sender's progress sees it, and only then is the write complete"),
     dict(active=("send",), copied=True, resp=True, done=True)),
]


def frames_for(step, sub, kw):
    out = []
    n = 14
    for f in range(n):
        u = ease(f / (n - 1))
        args = dict(active=kw.get("active", ()))
        if step in ("2", "3"):
            args["handle"] = True
        if kw.get("cmd"):
            args["cmd_pos"] = u
        if kw.get("cmd_at") is not None:
            args["cmd_pos"] = kw["cmd_at"]
        if kw.get("mapped"):
            args["mapped"] = True
        if kw.get("copy"):
            args["copy_t"] = u
            args["copied"] = u > 0.98
        for k in ("copied", "resp", "done"):
            if kw.get(k):
                args[k] = True
        args["show"] = {int(step)}
        out.append(scene(step, sub, **args))
    out += [out[-1]] * 10
    return out


frames = []
for step, sub, kw in STEPS:
    frames += frames_for(step, sub, kw)
fail_sub = ("if the posting thread's current context does not own the buffer",
            "cuMemGetAddressRange fails, and smr_do_ipc switches this write to SAR (next section)")
fail = scene("1x", fail_sub, active=("send",), fail=True)
frames += [fail] * 24

pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]
pal[0].save(os.path.join(OUT_DIR, "cuda-ipc.gif"), save_all=True, append_images=pal[1:],
            duration=100, loop=0, optimize=True, disposal=1)

# static frame: the copy step with the command and the response visible
static = scene("1-6", ("1 base and length  2 handle  3 command  4 open  5 copy  6 done",
                       "the sender only passes a handle; the receiver's thread does the copy"),
               active=("send", "recv"), handle=True, cmd_pos=1.0, mapped=True, copy_t=0.5,
               resp=True, show={1, 2, 3, 4, 5, 6})
static.save(os.path.join(OUT_DIR, "cuda-ipc.png"))
print("frames", len(frames))
