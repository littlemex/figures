"""gen_decode_stall_gif.py -- 受信側(decode)の同期コピーが decode のトークン出力を止める様子。

    OUT_DIR=<出力先> /usr/bin/python3 gen_decode_stall_gif.py

上段: decode エンジンがトークンを 1 つずつ出す様子をティックで表す。
下段: decode の進行スレッド(sglang::scheduler_TP0)の状態を 1 本のボックスで表す。
      idle(進行ループを回しているだけ) -> progressCompletionQueue() -> shm provider の
      進行チェーン(8 フレーム、このビルドでは未解決) -> cuMemcpy()/cudaMemcpy()(同期コピー、
      ブロック) -> 完了して idle に戻る、の順に遷移する。
下段が cuMemcpy の間、上段のトークンは出ない(ティックが赤く途切れる)ことを時間方向に見せる。
これは gdb のスナップショットから起こした概念図で、実測のタイミングそのものではない。
色: 緑 = SGLang、青 = NIXL、灰 = libfabric の未解決フレーム、黄 = CUDA ドライバ/ハードウェア、
赤 = ブロック中。
根拠: NIXL14-SWEEP.md 追加ラウンドの item 4 (gdb -p <decode pid> -batch -ex 'thread apply all bt'、
6/32 サンプル、worst_itl_ms_p50 3,756.5 ms、slo_attainment_fraction 0.0、rate=1 req/s)。
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
OUT = os.path.join(OUT_DIR, "decode-ipc-stall.gif")
SC = 4 / 3
FPS = 12
BG = (0, 0, 0)
GRN_HI = (59, 209, 111)
GRN_DK = (18, 64, 34)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
YEL_DK = (80, 66, 14)
RED = (220, 38, 88)
CHIP = (22, 26, 30)
EDGE = (70, 74, 80)

TL_X0, TL_Y, TL_X1 = 70, 150, 890
N_SLOTS = 14
STATE_BOX = (70, 236, 820, 96)

STATES = [
    ("idle: fi_cq_read() polling\ntokens streaming normally", LINK_DK, LINK, False),
    ("progressCompletionQueue()\nholds NIXL's rail mutex", LINK_DK, LINK, False),
    ("shm provider progress chain\n(8 frames, unresolved in this build)", CHIP, EDGE, False),
    ("cuMemcpy(): GPU-to-GPU copy\nsynchronous -- mutex held", YEL_DK, YEL, True),
    ("copy done: flag flips\ndecode resumes", GRN_DK, GRN_HI, False),
]


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, r, fill, outline, text=None, size=15, col=TX, wd=2):
    x, y, w, h = r
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=10 * SC, fill=fill, outline=outline,
                        width=int(wd * SC))
    if text:
        g.multiline_text(P(x + w / 2, y + h / 2), text, font=st.font(size), fill=col,
                         anchor="mm", align="center", spacing=6 * SC)


def base(phase, sub, filled, stalled_idx=None, state_i=0):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 32), "Decode streaming stalls on the receiver's copy", font=st.font(20), fill=TX, anchor="lm")
    g.text(P(40, 62), f"{phase} {sub}", font=st.font(13), fill=MUTED, anchor="lm")
    g.text(P(40, 108), "decode output: one token per tick", font=st.font(13), fill=MUTED, anchor="lm")
    step = (TL_X1 - TL_X0) / (N_SLOTS - 1)
    g.line([P(TL_X0, TL_Y), P(TL_X1, TL_Y)], fill=EDGE, width=int(2 * SC))
    for i in range(N_SLOTS):
        x = TL_X0 + i * step
        if i < filled:
            col = RED if (stalled_idx is not None and i == stalled_idx) else GRN_HI
            r = 11 if i == filled - 1 else 8
        else:
            col = (60, 64, 70)
            r = 6
        g.ellipse([P(x - r, TL_Y - r), P(x + r, TL_Y + r)], fill=col, outline=BG, width=int(2 * SC))
    if stalled_idx is not None:
        x = TL_X0 + stalled_idx * step
        g.text(P(x, TL_Y + 26), "gap", font=st.font(12), fill=RED, anchor="mm")
    name, fill_c, stroke_c, blocked = STATES[state_i]
    rbox(g, STATE_BOX, fill_c, stroke_c, name, 15, col=(TX if not blocked else RED))
    g.text(P(40, 358), "sglang::scheduler_TP0 (decode's own progress thread)",
           font=st.font(13), fill=MUTED, anchor="lm")
    g.text(P(40, 396), "gdb caught this chain in 6 of 32 TP0 samples (18.75%)",
           font=st.font(13), fill=MUTED, anchor="lm")
    g.text(P(40, 426), "same bracket: worst_itl_ms_p50 3,756.5 ms", font=st.font(13), fill=MUTED, anchor="lm")
    g.text(P(40, 456), "slo_attainment_fraction 0.0 (rate = 1 req/s, shm on)",
           font=st.font(13), fill=MUTED, anchor="lm")
    return img, g


frames = []

# 1. normal streaming: tokens tick in one by one, state = idle/polling
for i in range(1, 6):
    img, _ = base("1.", "decode streams tokens normally", filled=i, state_i=0)
    frames.append(img)
    frames.append(img)

# 2. the progress thread descends into the shm provider's own chain
for s_i in (1, 2):
    img, _ = base("2.", "progress thread enters the shm provider chain", filled=5, state_i=s_i)
    for _ in range(5):
        frames.append(img)

# 3. inside cuMemcpy: blocked. no new token appears -- the gap is the stall this round caught live.
img_block, _ = base("3.", "cuMemcpy(): copying GPU-to-GPU, mutex held", filled=6, stalled_idx=5, state_i=3)
for _ in range(18):
    frames.append(img_block)

# 4. copy completes, the gap stays visible, decode resumes
img_done, _ = base("4.", "copy done -- decode resumes after the gap", filled=6, state_i=4)
for _ in range(8):
    frames.append(img_done)
for i in range(7, N_SLOTS + 1):
    img, _ = base("5.", "decode streams tokens normally again", filled=i, state_i=0)
    frames.append(img)
    frames.append(img)
for _ in range(10):
    frames.append(frames[-1])

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB", f"{len(frames)/FPS:.1f}s")
if os.environ.get("DUMP"):
    for i in (0, len(frames) // 5, 2 * len(frames) // 5, 3 * len(frames) // 5, len(frames) - 1):
        frames[i].save(os.path.join(OUT_DIR, f"decode-stall-m{i}.png"))
