"""gen_tp1_sar_gif.py -- TP1's transfer threads silently fall back to SAR, and the one-line fix.

    OUT_DIR=<出力先> /usr/bin/python3 gen_tp1_sar_gif.py

1. Prefill TP0: transfer_worker thread -> cudaIpcGetMemHandle succeeds -> IPC protocol
2. Prefill TP1 (before the fix): transfer_worker thread never calls cuda.set_device() ->
   cuMemGetAddressRange fails (CUDA_ERROR_NOT_FOUND, once per layer) -> smr_do_ipc() catches
   it inline and substitutes SAR, chunks bounce through host memory instead
3. The fix lands: one line, torch.cuda.set_device(self.kv_args.gpu_id), at the top of
   transfer_worker
4. After the fix: TP1 takes the same IPC path as TP0; the SAR fallback goes idle
色: 緑 = SGLang (アプリ層プロセス)、青 = NIXL / UCX / libfabric、黄 = EFA ハードウェアと注意点、
赤 = 失敗・ホストメモリ経由のフォールバック。
根拠: 記事本文、SGLang conn.py#L291-L295 / #L563、libfabric smr_ep.c#L697-L729
(commit 5a15cde858ea09b77116212a39356f2fc51b8584 / 5a13558c2fcea15f1a6c4e8c06dc702e50724cf8)。
図の文字は英語。
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
OUT = os.path.join(OUT_DIR, "tp1-sar-fallback.gif")
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

L_THREAD = (50, 130, 310, 56)
L_HANDLE = (50, 222, 310, 56)
L_IPC = (50, 314, 310, 56)

R_THREAD = (590, 130, 310, 56)
R_FAIL = (590, 222, 310, 56)
R_SAR = (590, 314, 310, 56)
R_HOST = (590, 406, 310, 64)

PATCH = (50, 404, 850, 60)


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, r, fill, outline, text=None, size=14, col=TX, wd=2):
    x, y, w, h = r
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(wd * SC))
    if text:
        g.multiline_text(P(x + w / 2, y + h / 2), text, font=st.font(size), fill=col,
                         anchor="mm", align="center", spacing=6 * SC)


def varrow(g, x, y0, y1, col):
    g.line([P(x, y0), P(x, y1)], fill=col, width=int(2 * SC))
    g.polygon([P(x, y1), P(x - 6, y1 - 10), P(x + 6, y1 - 10)], fill=col)


def mark(g, x, y, ok, r=10):
    if ok:
        g.line([P(x - r, y), P(x - 2, y + r - 2)], fill=GRN_HI, width=int(3 * SC))
        g.line([P(x - 2, y + r - 2), P(x + r, y - r + 2)], fill=GRN_HI, width=int(3 * SC))
    else:
        g.line([P(x - r, y - r), P(x + r, y + r)], fill=RED, width=int(3 * SC))
        g.line([P(x - r, y + r), P(x + r, y - r)], fill=RED, width=int(3 * SC))


def base(phase, sub, patched=False, fail_n=0, show_patch=False, host_lit=False):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 36), "TP1 was quietly taking a different path", font=st.font(20), fill=TX, anchor="lm")
    g.text(P(40, 70), f"{phase}  {sub}", font=st.font(13), fill=MUTED, anchor="lm")
    g.text(P(50, 108), "Prefill TP0", font=st.font(14), fill=MUTED, anchor="lm")
    g.text(P(590, 108), "Prefill TP1" + (" (patched)" if patched else ""), font=st.font(14),
          fill=(GRN_HI if patched else MUTED), anchor="lm")
    varrow(g, L_THREAD[0] + L_THREAD[2] / 2, L_THREAD[1] + L_THREAD[3], L_HANDLE[1], (90, 94, 100))
    varrow(g, L_HANDLE[0] + L_HANDLE[2] / 2, L_HANDLE[1] + L_HANDLE[3], L_IPC[1], (90, 94, 100))
    varrow(g, R_THREAD[0] + R_THREAD[2] / 2, R_THREAD[1] + R_THREAD[3], R_FAIL[1], (90, 94, 100))
    varrow(g, R_FAIL[0] + R_FAIL[2] / 2, R_FAIL[1] + R_FAIL[3], R_SAR[1], (90, 94, 100))
    if not patched:
        varrow(g, R_SAR[0] + R_SAR[2] / 2, R_SAR[1] + R_SAR[3], R_HOST[1], (90, 94, 100))
    rbox(g, L_THREAD, LINK_DK, LINK, "transfer_worker thread\n(no set_device, matches)", 10)
    rbox(g, L_HANDLE, GRN_DK, GRN_HI, "cudaIpcGetMemHandle\nsucceeds", 11)
    rbox(g, L_IPC, LINK_DK, LINK, "IPC protocol\n(previous section)", 11)
    mark(g, L_HANDLE[0] + L_HANDLE[2] + 18, L_HANDLE[1] + L_HANDLE[3] / 2, True, r=9)

    if show_patch:
        rbox(g, PATCH, GRN_DK, GRN_HI,
            "+ torch.cuda.set_device(self.kv_args.gpu_id)\nat the top of transfer_worker", 13)
        return img, g

    rbox(g, R_THREAD, LINK_DK, LINK,
        ("transfer_worker thread\n(explicit set_device)" if patched
         else "transfer_worker thread\n(no set_device, wrong GPU)"), 10)
    if patched:
        rbox(g, R_FAIL, GRN_DK, GRN_HI, "cudaIpcGetMemHandle\nsucceeds", 11)
        rbox(g, R_SAR, LINK_DK, LINK, "IPC protocol\n(same as TP0)", 11)
        rbox(g, R_HOST, CHIP, EDGE, "SAR / host bounce\nbuffer (idle)", 11, col=MUTED)
        mark(g, R_FAIL[0] + R_FAIL[2] + 18, R_FAIL[1] + R_FAIL[3] / 2, True, r=9)
    else:
        rbox(g, R_FAIL, RED_DK, RED, "cuMemGetAddressRange\nfails: CUDA_ERROR_NOT_FOUND", 10)
        rbox(g, R_SAR, YEL_DK, YEL, "smr_do_ipc() catches it,\nfalls back to SAR inline", 10)
        rbox(g, R_HOST, (YEL if host_lit else CHIP), (YEL if host_lit else EDGE),
            "host bounce buffer\n(27 writes, 1 cold-start req.)", 10, col=(CHIP if host_lit else MUTED))
        mark(g, R_FAIL[0] + R_FAIL[2] + 18, R_FAIL[1] + R_FAIL[3] / 2, False, r=9)
        if fail_n:
            g.text(P(R_FAIL[0] + R_FAIL[2] - 8, R_FAIL[1] - 2),
                  f"x{fail_n}", font=st.font(11), fill=RED, anchor="rm")
    return img, g


frames = []

# 1. TP0's own path succeeds, repeated to establish the baseline
img0, _ = base("1.", "TP0: cuda.set_device happened implicitly, IPC export succeeds")
for _ in range(14):
    frames.append(img0)

# 2. TP1 (unpatched): every write fails the handle export and bounces through SAR
for n in (1, 4, 9, 16, 23, 27):
    img, g = base("2.", f"TP1: cuMemGetAddressRange fails ({n} of 27 layers so far)", fail_n=n)
    frames.append(img)
    frames.append(img)
img_host, _ = base("2.", "every failing write bounces through the host instead", fail_n=27, host_lit=True)
for _ in range(10):
    frames.append(img_host)

# 3. the fix lands
img_patch, _ = base("3.", "the fix: one line, no rebuild, shm stays on", show_patch=True)
for _ in range(16):
    frames.append(img_patch)

# 4. TP1 now matches TP0
img_fixed, _ = base("4.", "TP1 now exports the handle and takes the IPC path, like TP0", patched=True)
for _ in range(16):
    frames.append(img_fixed)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.1f}s")
if os.environ.get("DUMP"):
    for i in (0, len(frames) // 5, 2 * len(frames) // 5, 3 * len(frames) // 5, 4 * len(frames) // 5, len(frames) - 1):
        frames[i].save(os.path.join(OUT_DIR, f"tp1-sar-m{i}.png"))
