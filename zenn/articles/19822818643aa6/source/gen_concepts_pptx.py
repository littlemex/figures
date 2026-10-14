"""gen_concepts_pptx.py -- 同じノード KV 転送記事の「基礎知識」側の静止図 13 枚。

    /usr/bin/python3 gen_concepts_pptx.py <out.pptx>

gen_kv_same_node_pptx.py が作る調査固有の 14 枚（経路・バグ・計測結果）の手前に置く、
一般的な前提知識の図。配色とテンプレートの見た目 (ZN-25) は gen_kv_same_node_pptx.py と
揃える: 黒地、英語の短いラベル、緑 = ソフトウェア（アプリ層。後の節で SGLang になる）、
青 = ライブラリ / ミドルウェア（CUDA ドライバ、libfabric、NIXL、UCX）、
黄 = ハードウェアと注意点。各スライドの題の下に 1 行で凡例を置く。

1.  kv-cache-basics            KV キャッシュとは何か、なぜ prefill と decode の間で引き渡すか
2.  gpu-memory-isolation       2 つのプロセスは別々の GPU メモリ空間を持つ
3.  cuda-ipc-handle-basics     CUDA IPC: コピーせずハンドルを渡す
4.  cuda-context-device-basics スレッドは触る前に GPU を選ぶ必要がある
5.  libfabric-providers-basics  1 つの API、複数のプロバイダ（efa、shm、tcp）
6.  shm-ipc-basics             shm プロバイダが GPU メモリに対してやること（一般形）
7.  sar-fallback-basics        うまくいかない時のホスト経由のバックアッププラン（一般形）
8.  progress-loop-cq-basics    進行ループと完了キュー（fi_cq_read の役割）
9.  nixl-lock-basics           進行と新規発行が同じロックを使う
10. rdma-write-basics          RDMA WRITE とループバック
11. kv-page-size-prefix-cache-basics  ページサイズと prefix cache の一致条件
12. nixl-version-fix-basics    NIXL 1.4.0: 発行側のスレッドに登録時のコンテキストを戻す
13. nixl14-sweep-result        スイープで確かめた、フォールバック消失と TTFT

2026-10-14 修正: スライド 12 は当初「ディスクリプタごとにデバイスを選び直す」という
説明だったが、ソースの正確な再読で誤りと判明した (APPENDIX-E-FACTS.md E20)。既定で効くのは
登録時 (registerMem) に記憶したコンテキストを呼び出し元スレッドへ cuCtxSetCurrent() で
戻すセッション単位の経路 (cudaSetCtx(), libfabric_backend.cpp#L284/#L1220) で、
ディスクリプタごとの cudaSetDevice() 経路 (#L1226 のラムダ、#L1230) は
use_cuda_addr_wa=true (既定) では実行されない。スライド 13 の見出しも
「device-selection fix」から誤解を避ける表現に直した。

根拠: 本記事の本文（一般的な CUDA / libfabric / RDMA の仕組みの説明は教科書的事実）、
/Users/akazawt/tmp/riv/issue/kvx/NIXL14-SWEEP.md（スイープの数値）、
/Users/akazawt/tmp/riv/issue/review-response/PAGE64-MHA.md（ページサイズと cached_tokens）。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "kv-concepts.pptx"

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
    items = [("Software (app layer)", GRN), ("Library / middleware", LINK), ("Hardware / caveat", YEL)]
    x = 43
    for name, col in items:
        box(s, x, y, 16, 16, col, radius=0.3, sw=0)
        label(s, x + 22, y - 3, 230, 22, name, size=13, color=MUTED, align="left")
        x += 24 + sh.ms.text_w_safe(name, 13) + 36


def new_slide(name):
    s = d.slide()
    SLIDE_NAMES.append(name)
    return s


# ------------------------------------------------------------------ 1. KV cache basics
s = new_slide("kv-cache-basics")
title(s.s, "What the KV cache is", "Prefill builds it once from the prompt; decode reads it and appends one token at a time")
legend(s.s)
box(s.s, 43, 150, 300, 70, GRN_DK, stroke=GRN, body="Prompt tokens", size=16)
sh.arrow(s.s, t, 343, 185, 420, 185, color=MUTED, width=2)
box(s.s, 420, 150, 380, 70, GRN_DK, stroke=GRN, body="Prefill: attention over\nthe whole prompt, once", size=14)
sh.arrow(s.s, t, 800, 185, 877, 185, color=MUTED, width=2)
box(s.s, 877, 150, 360, 70, GRN_DK, stroke=GRN_HI, body="KV cache\n(one slot per layer, per token)", size=14)
sh.arrow(s.s, t, 1057, 220, 1057, 280, color=GRN_HI, width=2.5)
box(s.s, 877, 280, 360, 90, GRN_DK, stroke=GRN_HI,
    body="Decode: read the whole KV cache\n+ 1 new token -> next token,\nthen append it to the cache", size=13)
sh.arrow(s.s, t, 877, 350, 1130, 230, color=GRN_HI, width=2, dashed=True)
label(s.s, 460, 335, 400, 20, "appended token loops back, once per output token", size=13, color=MUTED, align="left")
box(s.s, 43, 440, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="If prefill and decode are two separate processes, the KV cache has to leave prefill's GPU "
         "memory and arrive in decode's -- that handover is what the rest of this article follows.",
    size=15, color=MUTED)

# ------------------------------------------------------------------ 2. GPU memory isolation
s = new_slide("gpu-memory-isolation")
title(s.s, "Two processes, two separate GPU memory spaces", "A pointer that is valid in process A means nothing when read in process B")
legend(s.s)
box(s.s, 43, 150, 540, 150, GRN_DK, stroke=GRN, radius=0.04)
label(s.s, 63, 160, 500, 24, "Process A", size=16, bold=True, align="left")
box(s.s, 83, 200, 460, 70, CHIP, stroke=GRN_HI, body="GPU buffer at address 0x7f2a...\n(valid only inside A's own CUDA context)", size=13)
box(s.s, 697, 150, 540, 150, GRN_DK, stroke=GRN, radius=0.04)
label(s.s, 717, 160, 500, 24, "Process B", size=16, bold=True, align="left")
box(s.s, 737, 200, 460, 70, CHIP, stroke=EDGE, body="Its own, unrelated address space\n(0x7f2a... resolves to something else, or nothing)", size=13)
sh.arrow(s.s, t, 583, 235, 697, 235, color=MUTED, width=2, dashed=True)
label(s.s, 583, 340, 650, 40, "handing B the raw address 0x7f2a... gives it no way to reach A's memory", size=14, color=MUTED, align="left")
box(s.s, 43, 420, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="Each process owns its own CUDA context and its own virtual-to-physical mapping, even on the same "
         "physical GPU. This is the same isolation ordinary CPU processes have for host memory, just extended "
         "to GPU memory -- it is why handing over a KV cache needs an explicit mechanism, not a bare pointer.",
    size=15, color=MUTED)

# ------------------------------------------------------------------ 3. CUDA IPC handle basics
s = new_slide("cuda-ipc-handle-basics")
title(s.s, "CUDA IPC: hand over a handle, not the data", "Only the receiving process can turn the handle into a pointer it can use")
legend(s.s)
box(s.s, 43, 150, 500, 60, GRN_DK, stroke=GRN, body="Process A: GPU buffer", size=15)
sh.arrow(s.s, t, 293, 210, 293, 250, color=LINK, width=2.5)
box(s.s, 43, 250, 500, 60, LINK_DK, stroke=LINK, body="cuIpcGetMemHandle()\n-> opaque handle (bytes)", size=14)
sh.arrow(s.s, t, 543, 280, 737, 280, color=MUTED, width=2.5)
label(s.s, 555, 258, 220, 18, "sent over any channel", size=12, color=MUTED, align="left")
box(s.s, 737, 250, 500, 60, LINK_DK, stroke=LINK, body="cuIpcOpenMemHandle()\n-> usable pointer in B's context", size=14)
sh.arrow(s.s, t, 987, 310, 987, 350, color=YEL, width=2.5)
box(s.s, 737, 350, 500, 60, YEL_DK, stroke=YEL, body="whoever holds the open pointer:\nGPU-to-GPU memcpy, a protocol's choice", size=13)
box(s.s, 43, 350, 500, 60, CHIP, stroke=EDGE, body="A still has not copied\nanything at this point", size=14, color=MUTED)
box(s.s, 43, 460, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="CUDA IPC itself only answers \"how does B get a usable pointer\" -- who actually calls memcpy with "
         "it is a protocol decision made by whatever is built on top. The investigation later in this article "
         "shows which side NIXL's own transport makes do that copy.", size=15, color=MUTED)

# ------------------------------------------------------------------ 4. CUDA context / current device
s = new_slide("cuda-context-device-basics")
title(s.s, "A thread must pick a GPU before it can touch it", "cudaSetDevice() tells CUDA which GPU a thread's calls should resolve against")
legend(s.s)
box(s.s, 43, 150, 1194, 70, GRN_DK, stroke=GRN, body="One process, two GPUs (device 0 and device 1)", size=15)
box(s.s, 43, 260, 580, 170, CHIP, stroke=LINK, radius=0.04)
label(s.s, 63, 272, 540, 22, "Thread 1: calls cudaSetDevice(1)", size=14, bold=True, align="left")
box(s.s, 63, 310, 540, 50, LINK_DK, stroke=LINK, body="current device = 1", size=14)
box(s.s, 63, 370, 540, 50, GRN_DK, stroke=GRN_HI, body="buffer lookup on device 1: succeeds", size=14)
box(s.s, 657, 260, 580, 170, CHIP, stroke=RED, radius=0.04)
label(s.s, 677, 272, 540, 22, "Thread 2: never calls cudaSetDevice()", size=14, bold=True, align="left")
box(s.s, 677, 310, 540, 50, LINK_DK, stroke=LINK, body="current device = 0 (the default)", size=14)
box(s.s, 677, 370, 540, 50, RGBColor(80, 24, 24), stroke=RED,
    body="buffer actually lives on device 1: lookup fails", size=14, color=WHITE)
box(s.s, 43, 460, 1194, 80, None, stroke=EDGE, radius=0.2,
    body="This is a general CUDA rule, not specific to any one library: an API call that resolves a buffer only "
         "looks at the calling thread's current device. The real transfer thread that hits exactly this failure "
         "appears later in this article.", size=15, color=MUTED)

# ------------------------------------------------------------------ 5. libfabric providers
s = new_slide("libfabric-providers-basics")
title(s.s, "libfabric: one API, several providers underneath", "FI_PROVIDER picks which network transport implements the same fi_* calls")
legend(s.s)
box(s.s, 43, 150, 500, 60, GRN_DK, stroke=GRN, body="Application (NIXL)", size=16)
sh.arrow(s.s, t, 293, 210, 293, 250, color=LINK, width=2.5)
box(s.s, 43, 250, 500, 60, LINK_DK, stroke=LINK, body="libfabric API (fi_av_insert, fi_writedata, fi_cq_read, ...)", size=13)
PROVS = [("efa", "talks to the EFA NIC hardware", YEL),
         ("shm", "same-node shortcut, no NIC", LINK),
         ("tcp", "generic fallback", MUTED)]
PX0, PW, PGAP = 43, 360, 36
for i, (nm, sub, col) in enumerate(PROVS):
    x = PX0 + i * (PW + PGAP)
    sh.arrow(s.s, t, 293, 310, x + PW / 2, 360, color=col, width=2)
    box(s.s, x, 360, PW, 90, CHIP, stroke=col, body=nm, size=20, color=col)
    label(s.s, x, 456, PW, 40, sub, size=13, color=MUTED)
box(s.s, 43, 530, 1194, 80, None, stroke=EDGE, radius=0.2,
    body="FI_PROVIDER=efa only picks the efa provider's code path. Whether a given write ends up going through "
         "the NIC or gets redirected to the shm provider is a decision the efa provider itself makes when it "
         "learns about a peer -- the next section in this article follows that decision.", size=15, color=MUTED)

# ------------------------------------------------------------------ 6. shm IPC basics (generic)
s = new_slide("shm-ipc-basics")
title(s.s, "What the shm provider does with GPU memory", "A same-node shortcut: skip the NIC, move the data through CUDA IPC instead")
legend(s.s)
box(s.s, 43, 150, 500, 60, GRN_DK, stroke=GRN, body="Sender process", size=16)
box(s.s, 737, 150, 500, 60, GRN_DK, stroke=GRN, body="Receiver process", size=16)
sh.arrow(s.s, t, 543, 180, 737, 180, color=LINK, width=2.5)
label(s.s, 555, 128, 300, 18, "1. export a handle for this write", size=12, color=MUTED, align="left")
box(s.s, 337, 250, 606, 70, LINK_DK, stroke=LINK, body="shm provider: hands the handle to the\nreceiver as a small command, not the data", size=14)
sh.arrow(s.s, t, 640, 320, 640, 360, color=YEL, width=2.5)
box(s.s, 337, 360, 606, 70, YEL_DK, stroke=YEL, body="receiver opens the handle and\ncopies GPU-to-GPU itself", size=14)
sh.arrow(s.s, t, 640, 430, 640, 470, color=GRN_HI, width=2.5)
box(s.s, 337, 470, 606, 60, GRN_DK, stroke=GRN_HI, body="a flag is set so the sender\ncan tell the write is done", size=14)
box(s.s, 43, 570, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="This is the general shape of a shm-style IPC transfer: the sender only exports a handle, and the "
         "receiver is the one that actually moves the bytes. The exact function names and the real timing "
         "of this handoff, as NIXL and libfabric implement it, are covered later in this article.", size=15, color=MUTED)

# ------------------------------------------------------------------ 7. SAR fallback basics (generic)
s = new_slide("sar-fallback-basics")
title(s.s, "When the shortcut fails: SAR, a bounce through host memory", "One of several shm protocols; this is the one used when the direct GPU-to-GPU setup fails")
legend(s.s)
box(s.s, 43, 150, 500, 60, GRN_DK, stroke=GRN, body="Sender GPU buffer", size=16)
sh.arrow(s.s, t, 293, 210, 293, 260, color=GRN_HI, width=2.5)
box(s.s, 43, 260, 500, 60, GRN_DK, stroke=GRN_HI, body="direct GPU-to-GPU copy (preferred)", size=14)
box(s.s, 737, 150, 500, 60, GRN_DK, stroke=GRN, body="Receiver GPU buffer", size=16)
sh.arrow(s.s, t, 293, 320, 293, 360, color=MUTED, width=1.5, dashed=True)
label(s.s, 310, 326, 400, 24, "setup fails here, e.g. a handle export error", size=13, color=MUTED, align="left")
box(s.s, 43, 360, 500, 60, YEL_DK, stroke=YEL, body="SAR instead: copy GPU -> host buffer", size=14)
sh.arrow(s.s, t, 543, 390, 737, 390, color=YEL, width=2.5)
box(s.s, 737, 360, 500, 60, YEL_DK, stroke=YEL, body="then host buffer -> GPU on the other side", size=14)
box(s.s, 43, 470, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="This is how libfabric's shm provider behaves in general when the direct path cannot be set up -- it "
         "quietly uses a slower, CPU-mediated path instead of failing outright. Which real transfer thread "
         "takes this path, and why, is covered later in this article.", size=15, color=MUTED)

# ------------------------------------------------------------------ 8. progress loop + completion queue
s = new_slide("progress-loop-cq-basics")
title(s.s, "Nothing moves until something calls the progress function", "fi_cq_read() both drives queued work forward and reports what finished")
legend(s.s)
box(s.s, 43, 160, 400, 60, GRN_DK, stroke=GRN, body="post a write (queue it)", size=15)
sh.arrow(s.s, t, 443, 190, 500, 190, color=MUTED, width=2)
box(s.s, 500, 160, 300, 60, CHIP, stroke=EDGE, body="work queue", size=15, color=MUTED)
sh.arrow(s.s, t, 800, 190, 857, 190, color=LINK, width=2.5)
box(s.s, 857, 160, 380, 60, LINK_DK, stroke=LINK, body="fi_cq_read(), called repeatedly", size=15)
sh.arrow(s.s, t, 977, 220, 870, 280, color=YEL, width=2.5)
box(s.s, 700, 280, 400, 60, YEL_DK, stroke=YEL, body="(a) executes queued work", size=15)
sh.arrow(s.s, t, 1067, 220, 1067, 360, color=YEL, width=2.5)
box(s.s, 700, 360, 400, 60, YEL_DK, stroke=YEL, body="(b) reports finished work", size=15)
box(s.s, 43, 460, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="libfabric itself has no dedicated background thread -- whichever thread calls fi_cq_read() is the "
         "one that both makes progress on queued work and finds out what has completed. If nothing calls it, "
         "nothing happens, no matter how long the data has been ready.", size=15, color=MUTED)

# ------------------------------------------------------------------ 9. NIXL lock basics
s = new_slide("nixl-lock-basics")
title(s.s, "One lock, two jobs: reading completions and posting new work", "A thread posting a new transfer can block behind another thread's progress call")
legend(s.s)
box(s.s, 500, 260, 194, 110, RGBColor(80, 24, 24), stroke=RED, body="shared lock", size=18, color=WHITE)
box(s.s, 43, 150, 400, 70, LINK_DK, stroke=LINK, body="Thread 1: fi_cq_read()\n(progress loop)", size=14)
sh.arrow(s.s, t, 243, 220, 500, 290, color=LINK, width=2.5)
label(s.s, 150, 230, 300, 18, "holds the lock while progressing", size=12, color=MUTED, align="left")
box(s.s, 843, 450, 394, 70, LINK_DK, stroke=LINK, body="Thread 2: postWrite()\n(new transfer)", size=14)
sh.arrow(s.s, t, 843, 480, 694, 350, color=YEL, width=2.5, dashed=True)
label(s.s, 843, 410, 394, 18, "waits for the same lock", size=12, color=YEL, align="left")
box(s.s, 43, 560, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="This is a common pattern when a single-threaded-style API is wrapped for multi-threaded use: one "
         "lock protects both \"make progress\" and \"queue new work\". Whether this actually shows up as a "
         "real delay, and how large, is a question for measurement -- taken up later in this article.",
    size=15, color=MUTED)

# ------------------------------------------------------------------ 10. RDMA write basics
s = new_slide("rdma-write-basics")
title(s.s, "RDMA WRITE: the NIC writes into remote memory directly", "No CPU copy on either side; completion is a hardware event")
legend(s.s)
box(s.s, 43, 170, 350, 70, GRN_DK, stroke=GRN, body="Sender GPU buffer", size=16)
sh.arrow(s.s, t, 393, 205, 460, 205, color=YEL, width=2.5)
box(s.s, 460, 170, 280, 70, YEL_DK, stroke=YEL, body="Sender's NIC", size=16)
sh.arrow(s.s, t, 740, 195, 897, 195, color=YEL, width=3, head=True)
sh.arrow(s.s, t, 897, 225, 740, 225, color=MUTED, width=1.5, dashed=True)
label(s.s, 740, 150, 300, 20, "RDMA WRITE over the wire", size=13, color=YEL, align="center")
box(s.s, 897, 170, 280, 70, YEL_DK, stroke=YEL, body="Receiver's NIC", size=16)
sh.arrow(s.s, t, 1037, 240, 1037, 300, color=YEL, width=2.5)
box(s.s, 827, 300, 420, 70, GRN_DK, stroke=GRN, body="Receiver GPU buffer\n(written to directly)", size=15)
box(s.s, 43, 410, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="\"Loopback\" means both ends of this hardware path happen to be the same physical NIC, talking to "
         "itself over the wire because sender and receiver are on the same node. The completion the sender "
         "sees is a real hardware event in its own completion queue, not a software signal.", size=15, color=MUTED)

# ------------------------------------------------------------------ 11. KV page size + prefix cache
s = new_slide("kv-page-size-prefix-cache-basics")
title(s.s, "KV page size and the prefix cache", "The cache can only reuse a page if every token inside it matches")
legend(s.s)
label(s.s, 43, 150, 560, 24, "page size 1: each token is its own page", size=16, bold=True, align="left")
PX, PW2, PN = 43, 60, 8
for i in range(PN):
    fill = GRN_DK if i < 4 else CHIP
    stroke = GRN_HI if i < 4 else EDGE
    box(s.s, PX + i * (PW2 + 6), 190, PW2, 60, fill, stroke=stroke, body=str(i + 1), size=14,
        color=(GRN_HI if i < 4 else MUTED))
label(s.s, 43, 258, 560, 24, "4 shared tokens -> 4 pages register as cached", size=14, color=GRN_HI, align="left")
label(s.s, 657, 150, 580, 24, "page size 64: 64 tokens share one page", size=16, bold=True, align="left")
box(s.s, 657, 190, 580, 60, CHIP, stroke=EDGE, body="tokens 1-64 (only 4 of them match the other request)", size=13, color=MUTED)
label(s.s, 657, 258, 580, 24, "not a full match -> 0 pages register as cached", size=14, color=YEL, align="left")
box(s.s, 43, 340, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="The same short, accidental token overlap can register as \"a few tokens cached\" at page size 1, "
         "but structurally cannot register as cached at all at page size 64, because no single page is fully "
         "matched. Whether that difference, by itself, changes anything downstream is covered later in this article.",
    size=15, color=MUTED)

# ------------------------------------------------------------------ 12. NIXL version fix
s = new_slide("nixl-version-fix-basics")
title(s.s, "NIXL 1.4.0: restores the context captured at registration", "Not a per-descriptor device pick -- a session-level cuCtxSetCurrent() on whichever thread calls in")
legend(s.s)
box(s.s, 43, 160, 560, 150, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 63, 172, 500, 22, "NIXL 1.1.0", size=16, bold=True, align="left")
box(s.s, 63, 206, 520, 50, LINK_DK, stroke=LINK, body="postXferDescriptors(): relies on the\ncaller's own current device", size=13)
box(s.s, 63, 262, 520, 40, RGBColor(80, 24, 24), stroke=RED, body="wrong device -> handle export can fail", size=13, color=WHITE)
box(s.s, 657, 160, 580, 150, CHIP, stroke=GRN, radius=0.04)
label(s.s, 677, 172, 520, 22, "NIXL 1.4.0 (default: use_cuda_addr_wa=true)", size=16, bold=True, align="left")
box(s.s, 677, 206, 540, 50, GRN_DK, stroke=GRN_HI, body="postXferDescriptors(): restores the context\nsaved at registerMem() time, on the caller", size=13)
box(s.s, 677, 262, 540, 40, GRN_DK, stroke=GRN_HI, body="handle export succeeds regardless of caller", size=13)
label(s.s, 43, 340, 1194, 24, "Source: cudaSetCtx() libfabric_backend.cpp#L284, called at #L1220 (PR #1581, commit c0a1102, merged 2026-06-26)", size=13, color=MUTED, align="left")
box(s.s, 43, 400, 1194, 90, None, stroke=EDGE, radius=0.2,
    body="A second, per-descriptor cudaSetDevice() path exists at the same call site (#L1226 lambda, "
         "cudaSetDevice at #L1230), but returns early and never runs while use_cuda_addr_wa stays true "
         "(the default; no config in this investigation sets NIXL_DISABLE_CUDA_ADDR_WA). The session-level "
         "restore above is the one that actually runs.", size=14, color=MUTED)

# ------------------------------------------------------------------ 13. NIXL 1.4.0 sweep result
s = new_slide("nixl14-sweep-result")
title(s.s, "The context-restore fix removes the fallback across a full sweep", "3 seeds x 5 arrival rates, 0.25-4 req/s, SGLang left unpatched")
legend(s.s)
box(s.s, 43, 160, 560, 150, RGBColor(80, 24, 24), stroke=RED, radius=0.04)
label(s.s, 63, 172, 500, 22, "NIXL 1.1.0 baseline", size=16, bold=True, align="left")
label(s.s, 63, 230, 500, 60, "20,361", size=44, bold=True, color=WHITE, align="left")
label(s.s, 63, 290, 500, 20, "handle-export failures logged", size=14, color=MUTED, align="left")
box(s.s, 657, 160, 580, 150, GRN_DK, stroke=GRN_HI, radius=0.04)
label(s.s, 677, 172, 520, 22, "NIXL 1.4.0, same sweep", size=16, bold=True, align="left")
label(s.s, 677, 230, 520, 60, "0", size=44, bold=True, color=GRN_HI, align="left")
label(s.s, 677, 290, 520, 20, "handle-export failures logged", size=14, color=MUTED, align="left")
label(s.s, 43, 340, 1194, 24, "TTFT at 2 req/s, 3 seeds pooled, p50/p99", size=16, bold=True, align="left")
ROWS2 = [("NIXL 1.1.0 + SGLang 1-line patch", 8143.1, 19582.3, GRN_HI),
         ("NIXL 1.4.0 alone, SGLang unpatched", 8050.0, 19843.0, LINK)]
y = 380
for nm, p50, p99, col in ROWS2:
    label(s.s, 43, y, 400, 50, nm, size=14, color=WHITE, align="left")
    label(s.s, 460, y, 380, 50, f"p50 {p50:,.0f} ms", size=15, bold=True, color=col, align="left")
    label(s.s, 820, y, 380, 50, f"p99 {p99:,.0f} ms", size=15, bold=True, color=col, align="left")
    y += 60
box(s.s, 43, 520, 1194, 70, None, stroke=EDGE, radius=0.2,
    body="Upgrading NIXL alone, with no change on the caller's side, reaches almost the same TTFT as patching "
         "the caller under NIXL 1.1.0 -- either fix removes the same fallback.", size=15, color=MUTED)

d.save(OUT)
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
print("\n".join(SLIDE_NAMES))
