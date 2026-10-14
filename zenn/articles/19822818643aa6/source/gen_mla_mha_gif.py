"""gen_mla_mha_gif.py -- page size 1 対 64 で attention のディスパッチが分かれる様子の GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_mla_mha_gif.py

1. 同じ 4-5 トークンの共有プレフィックスが、page size 1 では「数個キャッシュ済み」として
   記録され、page size 64 では 1 ページも満たせず記録されない
2. sum(extend_prefix_lens_cpu) がゼロかどうかの分岐
3. page 1 は MLA (遅い) へ、page 64 は MHA (速い) へ
4. prefill_forward の時間差（disaggregated: 820.8ms 対 348.4ms、実測値）

図の文字は英語。根拠は /Users/akazawt/tmp/riv/issue/review-response/PAGE64-MHA.md、
sglang@5a15cde858ea09b77116212a39356f2fc51b8584 の attention_backend_handler.py:172-176。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "mla-mha-dispatch.gif")
SC = 4 / 3
FPS = 12

GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
YEL_DK = (80, 66, 14)
RED = (220, 38, 88)
RED_DK = (80, 24, 24)
DIM = (46, 50, 56)
CHIP = (22, 26, 30)
GREY = (52, 56, 64)


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, x, y, w, h, fill, outline, text=None, size=15, col=TX):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(2 * SC))
    if text:
        g.multiline_text(P(x + w / 2, y + h / 2), text, font=s.font(size), fill=col, anchor="mm",
                         align="center", spacing=6 * SC)


def arrow(g, x1, y1, x2, y2, color, w=2.5):
    import math
    g.line([P(x1, y1), P(x2, y2)], fill=color, width=int(w * SC))
    ang = math.atan2((y2 - y1), (x2 - x1))
    L = 9
    p1 = (x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4))
    p2 = (x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))
    g.polygon([P(x2, y2), P(*p1), P(*p2)], fill=color)


def base(title_sub):
    img = Image.new("RGB", (int(1280 * SC), int(640 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 36), "Why page 64 skips the slow attention path", font=s.font(24), fill=TX, anchor="lm")
    g.text(P(40, 76), title_sub, font=s.font(14), fill=MUTED, anchor="lm")
    return img, g


def draw_tokens(g, x, y, n_total, n_shared, cell=34):
    for i in range(n_total):
        shared = i < n_shared
        fill = (18, 64, 34) if shared else CHIP
        outline = GRN_HI if shared else DIM
        rbox(g, x + i * (cell + 4), y, cell, cell, fill, outline,
             str(i + 1) if not shared else "S", size=12, col=(GRN_HI if shared else MUTED))


def page_block(g, x, y, w, h, filled_frac, label_text, matched):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=6 * SC, fill=CHIP, outline=DIM, width=int(2 * SC))
    col = GRN_HI if matched else YEL
    fw = w * filled_frac
    if fw > 0:
        g.rounded_rectangle([P(x, y), P(x + fw, y + h)], radius=6 * SC, fill=(18, 64, 34) if matched else YEL_DK)
    g.text(P(x + w / 2, y + h + 20), label_text, font=s.font(13), fill=MUTED, anchor="mm")


frames = []
PX, PY = 60, 130

# Phase 1: show the same 4-5 shared tokens against page size 1 vs page size 64
for f in range(30):
    u = ease(f / 29)
    img, g = base("1.  The same 4 shared tokens, two different page sizes")
    g.text(P(PX, PY - 10), "page size 1  (8 tokens shown)", font=s.font(15), fill=TX, anchor="lm")
    draw_tokens(g, PX, PY + 14, 8, int(4 * u + 0.5))
    g.text(P(PX, PY + 90), "page size 64  (1 page = 64 tokens)", font=s.font(15), fill=TX, anchor="lm")
    page_block(g, PX, PY + 114, 560, 40, 4 / 64 * u, "4 of 64 -- not a full page", matched=False)
    frames.append(img)
for _ in range(10):
    frames.append(frames[-1])

# Phase 2: the dispatch condition
for f in range(30):
    u = ease(f / 29)
    img, g = base("2.  attention_backend_handler.py:172-176  --  sum(extend_prefix_lens_cpu) == 0 ?")
    draw_tokens(g, PX, PY + 14, 8, 4)
    page_block(g, PX, PY + 114, 560, 40, 4 / 64, "4 of 64 -- not a full page", matched=False)
    rbox(g, 760, PY, 420, 60, LINK_DK, LINK, "cached tokens (page 1): 4  ->  nonzero", size=14)
    rbox(g, 760, PY + 90, 420, 60, LINK_DK, LINK, "cached tokens (page 64): 0  ->  zero", size=14)
    if u > 0.3:
        arrow(g, 980, PY + 60, 980, PY + 150 + 70 * min(1, (u - 0.3) / 0.5), YEL)
    frames.append(img)
for _ in range(10):
    frames.append(frames[-1])

# Phase 3: branch to MLA (page1, slow) vs MHA (page64, fast)
for f in range(36):
    u = ease(f / 35)
    img, g = base("3.  page 1 takes MLA (slower on this GPU); page 64 takes MHA (faster)")
    rbox(g, 60, PY, 500, 70, RED_DK, RED, "page 1: nonzero cached tokens\n-> AttnForwardMethod.MLA", size=14)
    rbox(g, 680, PY, 500, 70, (18, 64, 34), GRN_HI, "page 64: zero cached tokens\n-> AttnForwardMethod.MHA", size=14)
    bar_w = 500 * u
    g.rectangle([P(60, PY + 110), P(60 + 500, PY + 150)], fill=CHIP, outline=DIM, width=int(2 * SC))
    g.rectangle([P(60, PY + 110), P(60 + bar_w, PY + 150)], fill=RED)
    g.text(P(60, PY + 170), "prefill_forward (disaggregated): 820.8 ms", font=s.font(13), fill=MUTED, anchor="lm")
    bar_w2 = 500 * u * (348.4 / 820.8)
    g.rectangle([P(680, PY + 110), P(680 + 500, PY + 150)], fill=CHIP, outline=DIM, width=int(2 * SC))
    g.rectangle([P(680, PY + 110), P(680 + bar_w2, PY + 150)], fill=GRN_HI)
    g.text(P(680, PY + 170), "prefill_forward (disaggregated): 348.4 ms", font=s.font(13), fill=MUTED, anchor="lm")
    frames.append(img)
for _ in range(14):
    frames.append(frames[-1])

# Phase 4: caveat
for f in range(18):
    img, g = base("Measured for this traffic's short, accidental prefix overlap -- not a general page-size effect")
    rbox(g, 60, PY, 500, 70, RED_DK, RED, "page 1: nonzero cached tokens\n-> AttnForwardMethod.MLA", size=14)
    rbox(g, 680, PY, 500, 70, (18, 64, 34), GRN_HI, "page 64: zero cached tokens\n-> AttnForwardMethod.MHA", size=14)
    g.rectangle([P(60, PY + 110), P(60 + 500, PY + 150)], fill=RED)
    g.text(P(60, PY + 170), "prefill_forward (disaggregated): 820.8 ms", font=s.font(13), fill=MUTED, anchor="lm")
    g.rectangle([P(680, PY + 110), P(680 + 500 * (348.4 / 820.8), PY + 150)], fill=GRN_HI)
    g.rectangle([P(680 + 500 * (348.4 / 820.8), PY + 110), P(680 + 500, PY + 150)], fill=CHIP, outline=DIM)
    g.text(P(680, PY + 170), "prefill_forward (disaggregated): 348.4 ms", font=s.font(13), fill=MUTED, anchor="lm")
    frames.append(img)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB")
