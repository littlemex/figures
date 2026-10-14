"""gen_kv_same_node_pptx.py -- 同じノード内 KV キャッシュ転送の記事用の静止図 13 枚。

    /usr/bin/python3 gen_kv_same_node_pptx.py <out.pptx>

テンプレートの見た目 (ZN-25): 黒地、英語の短いラベル、緑 = SGLang (アプリ層)、
青 = NIXL / UCX / libfabric (転送ライブラリ層)、黄 = ハードウェアと注意点。
各スライドの題の下に 1 行で凡例を置く。

1. overview-map        3 つの経路の全体地図と持ち主
2. decision-point      EFA provider がローカルの相手を検出して shm に渡す分岐点
3. shm-write-sequence  shm 書き込みの一連の流れ (ハンドルの受け渡し -> 受信側が実際にコピー -> 送信側の記帳)
4. tp1-sar-fallback    TP1 だけ IPC ハンドルのエクスポートに失敗し SAR へ黙って切り替わっていた経路と、1 行の修正
5. matched-ab          修正の前後、および NIXL 1.4.0 単体を同じ条件で測った転送ステージ時間
6. shm-off-path        shm off: EFA デバイスへの RDMA WRITE とループバック
7. ucx-cuda-ipc        UCX の cuda_ipc 自動選択
8. three-paths-compare 3 経路の並び
9. measurement-setup   ステージ別カウンタ + ホスト側 EFA カウンタ、Pod の死角
10. transfer-stage-times 混雑時の転送時間の比較
11. byte-proof          期待バイト数と実測バイト数の一致
12. ruled-out-hypotheses ディスクリプタ数とスレッド数の介入結果
13. decode-ipc-stall    NIXL 1.4.0 でも shm オンだと残る、受信側の同期コピーによる decode のストール

根拠: 記事本文 (articles/19822818643aa6.md)、/Users/akazawt/tmp/riv/issue/kvx/SHM-MECHANISM.md
(section 1-2, 11, 12)、/Users/akazawt/tmp/riv/issue/gitlab/ISSUE-RFC.md の Appendix E、
/Users/akazawt/tmp/riv/issue/kvx/NIXL14-SWEEP.md (NIXL 1.4.0 の計測、follow-up の item 4)。

2026-10-14 修正: スライド 12 (ruled-out-hypotheses) を APPENDIX-E-FACTS.md の item (a)/(b) で
更新。ディスクリプタ数は「ほぼ 27 のまま」が成り立つのは毎回新しいプロンプトを使う測り方
限定で、同じタスクを繰り返す別の測り方(3 seeds x 3 rates)では平均 143.9(page1/shm-on)
対 41.2(page64/shm-off)まで上がる(ページサイズ/バージョン/キャッシュ状態は未分離)。
スレッドプールは bpftrace で postWrite() の投稿スレッド数が 4 本(無効)/8 本(有効)に
なることを直接確認したが、転送ステージ時間への効果は 3 seeds x 2 rates で符号が揺れ
inconclusive (not "no change")。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "kv-same-node.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
LINK = RGBColor(40, 150, 240)
LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)
BG_DARK = RGBColor(0, 0, 0)
RED = RGBColor(220, 38, 88)

d = Deck(TPL, check_layout=False)
t = d.theme

SLIDE_NAMES = []


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25, bold=True):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, bold, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def title(s, head, sub):
    label(s, 43, 24, 1194, 42, head, size=28, bold=True, align="left")
    label(s, 43, 66, 1194, 24, sub, size=15, color=MUTED, align="left")


def legend(s, y=96):
    items = [("SGLang", GRN), ("NIXL / UCX / libfabric", LINK), ("EFA hardware / caveat", YEL)]
    x = 43
    for name, col in items:
        box(s, x, y, 16, 16, col, radius=0.3, sw=0)
        label(s, x + 22, y - 3, 230, 22, name, size=13, color=MUTED, align="left")
        x += 24 + sh.ms.text_w_safe(name, 13) + 36


def new_slide(name):
    s = d.slide()
    SLIDE_NAMES.append(name)
    return s


# ------------------------------------------------------------------ 1. overview map
s = new_slide("overview-map")
title(s.s, "Three same-node transfer paths", "Who owns which part of the copy")
legend(s.s)
COLS = [
    ("Path 1: UCX default", "EFA device not reached", LINK),
    ("Path 2: LIBFABRIC default", "EFA device not reached", LINK),
    ("Path 3: LIBFABRIC, shm off", "EFA device reached (loopback)", YEL),
]
CW, GAP, X0 = 372, 36, 43
OY = 14  # extra clearance below the 3-item legend row
for i, (head, sub, accent) in enumerate(COLS):
    x = X0 + i * (CW + GAP)
    box(s.s, x, 144 + OY, CW, 36, GRN_DK, stroke=GRN, body="SGLang", size=15)
    sh.arrow(s.s, t, x + CW / 2, 180 + OY, x + CW / 2, 204 + OY, color=MUTED, width=1.5)
    box(s.s, x, 204 + OY, CW, 56, LINK_DK, stroke=LINK, body="NIXL", size=15)
    sh.arrow(s.s, t, x + CW / 2, 260 + OY, x + CW / 2, 284 + OY, color=MUTED, width=1.5)
    label(s.s, x, 130 + OY, CW, 14, head, size=15, bold=True, align="left")
    lib = "UCX" if i == 0 else "libfabric (efa provider)"
    box(s.s, x, 284 + OY, CW, 56, LINK_DK, stroke=LINK, body=lib, size=14)
    sh.arrow(s.s, t, x + CW / 2, 340 + OY, x + CW / 2, 364 + OY, color=MUTED, width=1.5)
    used = i == 2
    if i == 0:
        box(s.s, x, 364 + OY, CW, 56, LINK_DK, stroke=LINK, body="cuda_ipc\n(GPU direct copy)", size=14)
    elif i == 1:
        box(s.s, x, 364 + OY, CW, 56, LINK_DK, stroke=LINK,
            body="shm provider\n(IPC when export succeeds)", size=13)
    else:
        box(s.s, x, 364 + OY, CW, 56, YEL_DK, stroke=YEL, body="EFA device\n(RDMA WRITE)", size=14)
    if used:
        sh.arrow(s.s, t, x + CW / 2, 420 + OY, x + CW / 2, 444 + OY, color=accent, width=2)
        box(s.s, x, 444 + OY, CW, 56, GRN_DK, stroke=GRN_HI, body="Receiver GPU buffer", size=14,
            color=WHITE)
    else:
        box(s.s, x, 444 + OY, CW, 56, None, stroke=EDGE, dash=MSO_LINE_DASH_STYLE.DASH,
            body="EFA device: not reached", size=13, color=MUTED)
    label(s.s, x, 512 + OY, CW, 60, sub, size=14, color=MUTED)
box(s.s, 43, 592 + OY, 1194, 56, None, stroke=EDGE, radius=0.2,
    body="Path 2's IPC and path 3 skip the host CPU for the data; path 2 falls back to a host-memory "
         "bounce buffer when the IPC handle export fails (see TP1, later in this article)", size=14, color=MUTED)

# ------------------------------------------------------------------ 2. decision point
s = new_slide("decision-point")
title(s.s, "Where the path gets decided", "At connection setup, not per transfer: inserting a peer address decides shm vs hardware")
legend(s.s)
box(s.s, 43, 150, 300, 60, GRN_DK, stroke=GRN, body="SGLang\nFI_PROVIDER=efa", size=15)
sh.arrow(s.s, t, 343, 180, 410, 180, color=MUTED, width=2)
box(s.s, 410, 150, 340, 60, LINK_DK, stroke=LINK, body="NIXL (LIBFABRIC backend)", size=15)
sh.arrow(s.s, t, 750, 180, 817, 180, color=MUTED, width=2)
box(s.s, 817, 150, 377, 60, LINK_DK, stroke=LINK, body="fi_av_insert(): register peer", size=14)
sh.arrow(s.s, t, 1005, 210, 1005, 250, color=LINK, width=2.5)
box(s.s, 580, 250, 614, 70, LINK_DK, stroke=LINK,
    body="efa_conn_rdm_insert_shm_av()", size=16)
sh.arrow(s.s, t, 887, 320, 887, 360, color=YEL, width=2.5)
box(s.s, 707, 360, 360, 80, YEL_DK, stroke=YEL,
    body="calls efa_is_local_peer():\nis the peer on this node?", size=14)
sh.arrow(s.s, t, 760, 440, 480, 500, color=YEL, width=2.5)
label(s.s, 160, 468, 300, 20, "yes, and shm_av exists", size=12, color=YEL, align="left")
sh.arrow(s.s, t, 980, 440, 1070, 500, color=MUTED, width=1.5, dashed=True)
label(s.s, 880, 468, 300, 20, "no (or no shm_av)", size=12, color=MUTED, align="right")
box(s.s, 160, 500, 480, 70, YEL_DK, stroke=YEL,
    body="registered in shm provider's address table\n(shm handles this peer from now on)", size=14)
box(s.s, 880, 500, 300, 70, CHIP, stroke=EDGE,
    body="stays on efa_rdm_rma\n(hardware path)", size=14, color=MUTED)
label(s.s, 43, 600, 1194, 46,
      "Source: efa_conn.c#L14-L31 (is_local_peer) and #L104-L148 (insert_shm_av), at commit 5a13558c2fcea15f1a6c4e8c06dc702e50724cf8",
      size=13, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. shm write sequence
s = new_slide("shm-write-sequence")
title(s.s, "The shm write: the receiver copies, not the sender", "NIXL always sets FI_REMOTE_CQ_DATA, so shm skips its sender-copy fast path and uses the IPC protocol")
legend(s.s)
box(s.s, 43, 140, 500, 60, GRN_DK, stroke=GRN, body="Sender process\nGPU buffer", size=15)
box(s.s, 737, 140, 500, 60, GRN_DK, stroke=GRN, body="Receiver process\nGPU buffer", size=15)
box(s.s, 43, 224, 500, 56, LINK_DK, stroke=LINK, body="exports a CUDA IPC handle\n(no copy here)", size=13)
sh.badge(s.s, t, 230, 210, 26, "1", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
sh.arrow(s.s, t, 543, 252, 737, 300, color=LINK, width=2.5)
label(s.s, 555, 284, 220, 16, "handle + command, not data", size=12, color=MUTED, align="left")
box(s.s, 737, 300, 500, 56, YEL_DK, stroke=YEL, body="command queue (receiver's side)", size=13)
sh.badge(s.s, t, 924, 286, 26, "2", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
sh.arrow(s.s, t, 987, 356, 987, 390, color=YEL, width=2.5)
box(s.s, 737, 390, 500, 56, LINK_DK, stroke=LINK, body="receiver's own progress loop\n(inside fi_cq_read)", size=13)
sh.badge(s.s, t, 924, 376, 26, "3", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
sh.arrow(s.s, t, 987, 446, 987, 480, color=YEL, width=2.5)
box(s.s, 737, 480, 500, 60, YEL_DK, stroke=YEL, body="opens the handle, copies\nGPU-to-GPU, synchronously", size=13)
sh.badge(s.s, t, 924, 466, 26, "4", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
sh.arrow(s.s, t, 737, 500, 580, 480, color=MUTED, width=1.5, dashed=True)
box(s.s, 43, 480, 480, 60, LINK_DK, stroke=LINK, body="status flag flips in the\nsender's own memory region", size=13)
sh.badge(s.s, t, 260, 466, 26, "5", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
box(s.s, 43, 390, 480, 56, LINK_DK, stroke=LINK, body="sender's own next fi_cq_read\nnotices the flag, completes", size=13)
sh.badge(s.s, t, 260, 376, 26, "6", color=WHITE, fill=RGBColor(90, 90, 98), size=13)
sh.arrow(s.s, t, 283, 480, 283, 446, color=MUTED, width=1.5, dashed=True)
box(s.s, 43, 572, 1194, 60, RGBColor(80, 24, 24), stroke=RED,
    body="fi_cq_read and postWrite share one lock (ep_mutex_): writer threads were seen waiting on it "
         "under load, never at low load -- whether progress was inside a copy at that moment is unconfirmed",
    size=14, color=WHITE)
label(s.s, 43, 640, 1194, 30,
      "Source: smr_rma.c#L335, smr_ep.c#L553-L611 (IPC protocol), smr_progress.c#L522-L597, libfabric_rail.cpp#L722-L725 / #L1129",
      size=12, color=MUTED, align="left")

# ------------------------------------------------------------------ 4. TP1 SAR fallback
s = new_slide("tp1-sar-fallback")
title(s.s, "TP1 was quietly taking a different path", "SGLang's transfer threads never pick a GPU, so TP1's IPC handle export fails on every write")
legend(s.s)
PANELS2 = [
    ("Prefill TP0", [("transfer_worker thread\n(no cuda.set_device, happens to match)", LINK_DK, LINK),
                     ("cudaIpcGetMemHandle\nsucceeds", GRN_DK, GRN_HI),
                     ("IPC protocol\n(previous slide)", LINK_DK, LINK)], "fast path, every write", False),
    ("Prefill TP1", [("transfer_worker thread\n(no cuda.set_device, wrong device)", LINK_DK, LINK),
                     ("cuMemGetAddressRange\nfails: CUDA_ERROR_NOT_FOUND", RGBColor(80, 24, 24), RED),
                     ("smr_do_ipc() catches it,\nfalls back to SAR inline", YEL_DK, YEL)],
     "host bounce buffers (measured: every write in one cold-start request)", True),
]
COLW, COLGAP, COLX0 = 579, 36, 43
for i, (head, chain, foot, bad) in enumerate(PANELS2):
    x = COLX0 + i * (COLW + COLGAP)
    label(s.s, x, 118, COLW, 30, head, size=16, bold=True, align="left")
    box(s.s, x, 158, COLW, 350, CHIP, stroke=EDGE, radius=0.04)
    y = 182
    for j, (nm, fill, stroke) in enumerate(chain):
        box(s.s, x + 24, y, COLW - 48, 86, fill, stroke=stroke, body=nm, size=13, color=WHITE)
        if j < len(chain) - 1:
            sh.arrow(s.s, t, x + COLW / 2, y + 86, x + COLW / 2, y + 112, color=stroke, width=2.5)
        y += 112
    box(s.s, x, 516, COLW, 40, (RGBColor(80, 24, 24) if bad else CHIP), stroke=(RED if bad else EDGE),
        body=foot, size=13, color=WHITE if bad else MUTED)
label(s.s, 43, 566, 1194, 24,
      "27 failures in one cold-start request (1 per model layer); FI_WARN_ONCE prints the fallback warning only once per process",
      size=13, color=MUTED, align="left")
box(s.s, 43, 602, 1194, 60, GRN_DK, stroke=GRN_HI,
    body="The fix: one line -- torch.cuda.set_device(self.kv_args.gpu_id) -- at the top of transfer_worker. "
         "shm stays on the whole time; TP1 now takes the same IPC path as TP0.",
    size=15, color=WHITE)
label(s.s, 43, 668, 1194, 24,
      "Source: conn.py#L291-L295 / #L563 (SGLang), smr_ep.c#L697-L729 (smr_do_ipc fallback), at the pinned commits",
      size=12, color=MUTED, align="left")

# ------------------------------------------------------------------ 5. matched A/B
s = new_slide("matched-ab")
title(s.s, "Same traffic, the SGLang patch, and NIXL 1.4.0 alone",
      "prefill_transfer_kv_cache mean -- top 3 rows per panel: shm on; bottom row: shm-off reference")
legend(s.s)
GROUPS = [
    ("1 req/s  (bars scaled to 1,900 ms)", 1900, [
        ("NIXL 1.1.0, unpatched (TP1 -> SAR)", 1886.2, RED),
        ("NIXL 1.1.0, patched (torch.cuda.set_device)", 461.4, GRN_HI),
        ("NIXL 1.4.0, shm on, no SGLang patch", 533.1, LINK),
        ("reference: shm off", 196.2, MUTED),
    ]),
    ("2 req/s  (bars scaled to 13,000 ms)", 13000, [
        ("NIXL 1.1.0, unpatched (TP1 -> SAR)", 12625.4, RED),
        ("NIXL 1.1.0, patched (torch.cuda.set_device)", 576.7, GRN_HI),
        ("NIXL 1.4.0, shm on, no SGLang patch", 663.9, LINK),
        ("reference: shm off", 495.0, MUTED),
    ]),
]
GX, GW, GGAP = 43, 520, 90
BARMAX = 330
for gi, (gname, maxv, rows) in enumerate(GROUPS):
    gx = GX + gi * (GW + GGAP)
    label(s.s, gx, 128, GW, 24, gname, size=15, bold=True, align="left")
    y = 166
    for name, val, col in rows:
        label(s.s, gx, y, GW, 26, name, size=13, color=WHITE, align="left")
        box(s.s, gx, y + 28, BARMAX, 30, CHIP, stroke=EDGE, radius=0.3, sw=1)
        w = max(6, BARMAX * val / maxv)
        box(s.s, gx, y + 28, w, 30, col, radius=0.3, sw=0)
        label(s.s, gx + w + 10, y + 24, GW - w - 10, 36, f"{val:,.1f} ms", size=14, bold=True, color=col, align="left")
        y += 112
box(s.s, 43, 650, 1194, 60, None, stroke=EDGE, radius=0.2,
    body="NIXL 1.4.0 alone, with no SGLang-side patch, lands close to the patched row at both rates "
         "(each panel has its own bar scale; bars are not comparable across panels)", size=14, color=MUTED)

# ------------------------------------------------------------------ 6. shm-off path
s = new_slide("shm-off-path")
title(s.s, "FI_EFA_ENABLE_SHM_TRANSFER=0: the hardware path", "No shm endpoint is created; writes go to the one EFA device, which loops back")
legend(s.s)
box(s.s, 43, 150, 420, 70, GRN_DK, stroke=GRN, body="Sender process\nGPU buffer", size=16)
sh.arrow(s.s, t, 463, 185, 560, 185, color=LINK, width=2.5)
box(s.s, 560, 150, 300, 70, LINK_DK, stroke=LINK, body="efa_rdm_rma_post_write()", size=14)
sh.arrow(s.s, t, 710, 220, 710, 270, color=YEL, width=2.5)
box(s.s, 560, 270, 300, 95, YEL_DK, stroke=YEL,
    body="RDMA WRITE\nhw completion:\nIBV_WC_RDMA_WRITE", size=13)
sh.arrow(s.s, t, 710, 365, 710, 400, color=YEL, width=2.5)
box(s.s, 460, 400, 500, 80, YEL_DK, stroke=YEL,
    body="EFA device (1 of 2 on the node)\nloopback to itself", size=16)
sh.arrow(s.s, t, 710, 480, 710, 530, color=YEL, width=2.5)
box(s.s, 560, 530, 300, 70, GRN_DK, stroke=GRN, body="Receiver process\nGPU buffer", size=16)
box(s.s, 43, 400, 350, 80, CHIP, stroke=EDGE,
    body="shm_ep never created:\nefa_shm_info_create() returns early", size=14, color=MUTED)
sh.arrow(s.s, t, 393, 440, 460, 440, color=MUTED, width=1.5, dashed=True)
label(s.s, 43, 648, 1194, 46,
      "Source: efa_shm.c#L68-L77, efa_rdm_rma.c, efa_rdm_rma.h#L30-L66 at the same commit",
      size=13, color=MUTED, align="left")

# ------------------------------------------------------------------ 7. UCX cuda_ipc
s = new_slide("ucx-cuda-ipc")
title(s.s, "UCX: cuda_ipc chosen automatically", "Real data is zero-copy; tcp / cma carry only small control messages")
legend(s.s)
box(s.s, 43, 160, 500, 90, GRN_DK, stroke=GRN, body="Sender process\nGPU 0", size=18)
box(s.s, 737, 160, 500, 90, GRN_DK, stroke=GRN, body="Receiver process\nGPU (dev 0)", size=18)
sh.arrow(s.s, t, 543, 190, 737, 190, color=LINK, width=3.5)
label(s.s, 560, 150, 400, 20, "cuda_ipc  zero-copy write", size=14, color=LINK, align="left")
sh.arrow(s.s, t, 543, 240, 737, 240, color=MUTED, width=1.5, dashed=True)
label(s.s, 560, 248, 400, 20, "tcp / cma  control messages only", size=13, color=MUTED, align="left")
box(s.s, 500, 330, 280, 60, CHIP, stroke=EDGE, body="EFA device\n(not used on this path)", size=14, color=MUTED)
box(s.s, 43, 440, 1194, 90, None, stroke=EDGE, radius=0.2,
    body='Startup log with UCX_PROTO_INFO=y:\n"device(cuda_ipc/cuda)  remote memory write by ucp_put* from cuda/GPU0 to cuda/dev[0] | zero-copy | cuda_ipc/cuda"',
    size=14, color=MUTED)

# ------------------------------------------------------------------ 8. three paths side by side
s = new_slide("three-paths-compare")
title(s.s, "Three paths, side by side", "Same request, three ways the bytes can move inside one node")
legend(s.s)
PANELS = [
    ("Path 1: UCX (default)", [("Sender GPU", GRN_DK, GRN), ("cuda_ipc\nzero-copy", LINK_DK, LINK),
                               ("Receiver GPU", GRN_DK, GRN)], "EFA device: not used"),
    ("Path 2: LIBFABRIC (default, shm)", [("Sender GPU", GRN_DK, GRN), ("shm provider\nIPC when export succeeds", LINK_DK, LINK),
                                          ("Receiver GPU", GRN_DK, GRN)], "EFA device: not used"),
    ("Path 3: LIBFABRIC, shm off", [("Sender GPU", GRN_DK, GRN), ("EFA device\nRDMA WRITE", YEL_DK, YEL),
                                    ("Receiver GPU", GRN_DK, GRN)], "EFA device: used (loopback)"),
]
CW, GAP, X0 = 372, 36, 43
for i, (head, chain, foot) in enumerate(PANELS):
    x = X0 + i * (CW + GAP)
    label(s.s, x, 118, CW, 34, head, size=15, bold=True, align="left")
    box(s.s, x, 160, CW, 400, CHIP, stroke=EDGE, radius=0.04)
    y = 184
    for j, (nm, fill, stroke) in enumerate(chain):
        box(s.s, x + 20, y, CW - 40, 90, fill, stroke=stroke, body=nm, size=14)
        if j < len(chain) - 1:
            sh.arrow(s.s, t, x + CW / 2, y + 90, x + CW / 2, y + 120, color=stroke, width=2.5)
        y += 120
    used = i == 2
    box(s.s, x, 580, CW, 44, (YEL_DK if used else CHIP), stroke=(YEL if used else EDGE),
        body=foot, size=13, color=(WHITE if used else MUTED))

# ------------------------------------------------------------------ 9. measurement setup
s = new_slide("measurement-setup")
title(s.s, "How the transfer was measured", "Stage counters inside SGLang and the EFA device's own hardware counters")
legend(s.s)
box(s.s, 43, 150, 560, 90, GRN_DK, stroke=GRN,
    body="SGLang --enable-metrics\nstage counter: prefill_transfer_kv_cache", size=15)
box(s.s, 677, 150, 560, 90, YEL_DK, stroke=YEL,
    body="EFA hardware counters\nsysfs hw_counters, read before/after", size=15)
label(s.s, 43, 260, 1194, 24, "Where the counters are visible", size=16, bold=True, align="left")
box(s.s, 43, 296, 560, 140, GRN_DK, stroke=GRN,
    body="Host-network pod\nhw_counters visible\ncounters read correctly", size=15)
box(s.s, 677, 296, 560, 140, RGBColor(80, 24, 24), stroke=RED,
    body="In-pod, no host network\nhw_counters directory absent\nvalue unavailable, not a measured 0", size=15)
label(s.s, 43, 460, 1194, 70,
      "The blind spot follows the pod's hostNetwork setting, not whether the EFA device was used.",
      size=16, color=MUTED, align="left")

# ------------------------------------------------------------------ 10. transfer stage times
s = new_slide("transfer-stage-times")
title(s.s, "Transfer stage time under load", "prefill_transfer_kv_cache, page size 1 unless noted; path 2 rows are the unpatched TP1-bug state")
legend(s.s)
ROWS = [
    ("Path 2: shm, unpatched (1 req/s)", 1886.2, YEL),
    ("Path 2: shm, unpatched (2 req/s)", 12625.4, YEL),
    ("Path 2: shm, 1-seed reference (1 req/s)", 1775.5, MUTED),
    ("Path 3: shm off (1 req/s)", 196.2, GRN_HI),
    ("Path 3: shm off, page 64 (1 req/s)", 60.0, GRN_HI),
    ("Path 3: shm off (2 req/s)", 495.0, GRN_HI),
    ("Path 3: shm off, page 64 (2 req/s)", 187.1, GRN_HI),
]
MAXV = 15000
x0, bw_total = 460, 620
y = 148
for name, val, col in ROWS:
    label(s.s, 43, y, 400, 36, name, size=13, color=WHITE, align="left")
    box(s.s, x0, y + 2, bw_total, 30, CHIP, stroke=EDGE, radius=0.3, sw=1)
    w = max(6, bw_total * val / MAXV)
    box(s.s, x0, y + 2, w, 30, col, radius=0.3, sw=0)
    label(s.s, x0 + w + 10, y - 2, 220, 36, f"{val:,.1f} ms", size=14, bold=True, color=col, align="left")
    y += 52
label(s.s, 43, y + 10, 1194, 40,
      "Path 2's unpatched rows are the matched A/B's own run (37/67 observations); its 1-seed row below is an "
      "older, separate reference. Path 3 rows are each a single bracketed run (not seed-averaged), 33-63 requests.",
      size=13, color=MUTED, align="left")
label(s.s, 43, y + 80, 1194, 36,
      "Caveat added later: this traffic's own 4-5 token shared prefix hits the cache at page 1 but never at "
      "page 64 (see the cached-token-confound slide) -- part of the page-64 rows' speedup may be that, not page size itself.",
      size=12, color=YEL, align="left")

# ------------------------------------------------------------------ 11. byte proof
s = new_slide("byte-proof")
title(s.s, "The byte-level proof", "EFA hardware counter rdma_write_bytes, before vs after 17 requests at TP 2")
COLS2 = [
    ("Path 1: UCX", "0", "~0", MUTED),
    ("Path 2: shm", "0", "~0", MUTED),
    ("Path 3: shm off", "8,663,389,312", "8,663,334,912", GRN_HI),
]
CW, GAP, X0b = 372, 36, 43
for i, (head, measured, expected, col) in enumerate(COLS2):
    x = X0b + i * (CW + GAP)
    label(s.s, x, 130, CW, 30, head, size=16, bold=True, align="left")
    box(s.s, x, 168, CW, 90, CHIP, stroke=EDGE,
        body=f"measured\n{measured}", size=16, color=col)
    box(s.s, x, 270, CW, 70, CHIP, stroke=EDGE,
        body=f"expected\n{expected}", size=14, color=MUTED)
label(s.s, 43, 380, 1194, 30, "Expected bytes = 254,803,968 (1 request × 1 rank) × 2 ranks × 17 requests", size=15, color=MUTED, align="left")
label(s.s, 43, 416, 1194, 30, "shm off ratio: measured / expected = 1.0000063 (about 54 KB over, 0.0006%)", size=15, color=GRN_HI, align="left")
box(s.s, 43, 470, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="A 20-second idle window right before the shm-off transfer showed zero counter movement", size=15, color=MUTED)

# ------------------------------------------------------------------ 12. ruled-out hypotheses
s = new_slide("ruled-out-hypotheses")
title(s.s, "Three factors examined", "Descriptor count: fresh-prompt (2 req/s) vs reused-traffic (3 seeds x 3 rates); thread interventions tested at 1 req/s, page size 1")
legend(s.s)
FACTORS = [
    ("Descriptor count", "fresh-prompt protocol: ~27 for 77/80 calls;\nreused-traffic protocol (3 seeds x 3 rates):\nmean 143.9 (1.1.0/page1/shm-on) vs 41.2 (1.4.0/page64/shm-off)"),
    ("UCX progress threads: 8 -> 0", "130.0 ms -> 132.9 ms\n(no improvement in this probe --\nnot supported as the main factor)"),
    ("NIXL 1.4.0 posting pool: off/on", "postWrite TIDs/rank: 4 -> 8 (confirmed by\nbpftrace, matches config). Stage time across\n3 seeds x 2 rates: sign flips per seed -- inconclusive"),
]
FCW, FGAP, FX0 = 372, 36, 43
for i, (head, body_text) in enumerate(FACTORS):
    x = FX0 + i * (FCW + FGAP)
    box(s.s, x, 150, FCW, 190, CHIP, stroke=EDGE, radius=0.04)
    label(s.s, x + 20, 166, FCW - 40, 26, head, size=16, bold=True, color=WHITE, align="left")
    label(s.s, x + 20, 206, FCW - 40, 128, body_text, size=13, color=MUTED, align="left")
box(s.s, 43, 370, 1194, 50, None, stroke=EDGE, radius=0.2,
    body="LIBFABRIC and UCX logged the same ~27 descriptors on this run, yet the stage time still differed "
         "~5x (1,772.8 ms vs 344.9 ms) -- occasional fragmentation is real but does not explain the gap", size=15, color=MUTED)
label(s.s, 43, 440, 1194, 70,
      "The 1,772.8 ms LIBFABRIC/shm value above still carries TP1's SAR fallback (earlier in this article); "
      "UCX is a different backend and is not subject to that bug. The reused-traffic descriptor-count sweep and the "
      "fresh-prompt one are different protocols (cache state is a live confound), not a contradiction. The posting-pool "
      "run carries NIXL's own context-restore fix by default; posting-thread counts are directly confirmed, stage-time benefit is not.",
      size=13, color=MUTED, align="left")

# ------------------------------------------------------------------ 13. decode-side IPC stall
s = new_slide("decode-ipc-stall")
title(s.s, "A candidate for the remaining stall",
      "gdb caught the decode engine's NIXL progress thread inside this chain, 6 of 32 TP0 samples")
legend(s.s)
CHAIN = [
    ("decode engine: progressThread()", LINK_DK, LINK, WHITE),
    ("progressActiveRails()", LINK_DK, LINK, WHITE),
    ("progressCompletionQueue() -- holds NIXL's rail mutex", LINK_DK, LINK, WHITE),
    ("libfabric shm provider progress chain (8 frames, not resolved by name in this build)", CHIP, EDGE, MUTED),
    ("cuMemcpy()/cudaMemcpy() or cudaIpcCloseMemHandle(): IPC progress calls", YEL_DK, YEL, WHITE),
    ("blocked: pthread_rwlock_wrlock (CUDA driver's own lock)", RGBColor(80, 24, 24), RED, WHITE),
]
CX, CW = 43, 620
y = 140
for i, (nm, fill, stroke, col) in enumerate(CHAIN):
    box(s.s, CX, y, CW, 64, fill, stroke=stroke, body=nm, size=13, color=col)
    if i < len(CHAIN) - 1:
        sh.arrow(s.s, t, CX + CW / 2, y + 64, CX + CW / 2, y + 82, color=stroke, width=2.5)
    y += 82
RX, RW = 707, 530
box(s.s, RX, 140, RW, 100, RGBColor(80, 24, 24), stroke=RED,
    body="IPC-path catches: 6 of 32 TP0 samples (18.75%)\ncopy call: 3 / handle-close call: 3\n"
         "deployments: 2, ramps: 4 total", size=14, color=WHITE)
box(s.s, RX, 256, RW, 100, YEL_DK, stroke=YEL,
    body="same load run's own ITL metric (not this\nblock's own duration): worst_itl_ms_p50 3,756.5 ms\n"
         "slo_attainment_fraction 0.0, rate = 1 req/s", size=14, color=WHITE)
box(s.s, RX, 372, RW, 70, CHIP, stroke=EDGE,
    body="not the SAR path: 0 cuMemGetAddressRange\nfailures, 0 SAR-fallback lines in this same log",
    size=14, color=MUTED)
box(s.s, 43, 630, 1194, 60, None, stroke=EDGE, radius=0.2,
    body="Observed: the decode engine's NIXL progress thread blocking inside this IPC progress path under load -- "
         "share of total stall time not established", size=14, color=MUTED)
label(s.s, 43, 696, 1194, 24,
      "Source: gdb -p <decode pid> -batch -ex 'thread apply all bt', unfiltered captures, NIXL14-SWEEP.md item 4",
      size=12, color=MUTED, align="left")

# ------------------------------------------------------------------ 14. cached-token confound
s = new_slide("cached-token-confound")
title(s.s, "Page 64's speedup is confounded by a cache hit",
      "A 4-5 token shared prefix can hit the cache at page 1; it structurally cannot at page 64")
legend(s.s)
box(s.s, 43, 150, 590, 110, GRN_DK, stroke=GRN,
    body="attention_backend_handler.py:172-176 (simplified)\n"
         "if is_extend and sum(extend_prefix_lens_cpu) == 0:\n    return MHA\nelse:\n    return MLA  (slower, on this GPU)",
    size=13, color=WHITE)
box(s.s, 43, 276, 590, 90, CHIP, stroke=EDGE,
    body="This traffic's prompts share a 4-5 token chat-template\nprefix (confirmed by decoding) -> can register as cached\nat page 1; needs a full 64-token match at page 64 (never happens here)",
    size=13, color=MUTED)
RX, RW = 657, 580
box(s.s, RX, 150, RW, 90, CHIP, stroke=EDGE,
    body="prefill_forward (rate 1): unified 453-481 -> 253-258 ms "
         "cache off / 267-282 ms page 64;\ndisaggregated 820.8 -> 338.1 ms cache off / 348.4 ms page 64",
    size=13, color=WHITE)
box(s.s, RX, 250, RW, 70, CHIP, stroke=EDGE,
    body="disaggregated transfer stage (rate 1, page 1): 265.6 ms with the\ncache hit vs 71.7 ms without vs 70.0 ms at page 64 -- follows "
         "cached_tokens too (mechanism inside the stage not identified)", size=13, color=WHITE)
box(s.s, 43, 390, 1194, 60, None, stroke=EDGE, radius=0.2,
    body="Disabling the prefix cache at page 1 closely matches page 64's numbers on both stacks, at every rate tested (0.25-2 req/s, 1 seed) -- "
         "part of the page-1-vs-64 gaps measured elsewhere in this article may carry this confound, not page size alone", size=14, color=YEL)
label(s.s, 43, 456, 1194, 24,
      "Source: attention_backend_handler.py:172-176 (sglang@5a15cde8); one seed, both stacks, rates 0.25/0.5/1/2 req/s",
      size=12, color=MUTED, align="left")

d.save(OUT)
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
print("\n".join(SLIDE_NAMES))
