"""gen_fig_pptx.py — 「XTTS v2 を vllm-neuron で動かす」の図を、ネイティブ shape の pptx 2 枚で組む。

    /usr/bin/python3 gen_fig_pptx.py <out.pptx>

1. NxD Inference 版と vllm-neuron 版で、誰が何を受け持つか (自分で書く部分と plugin / vLLM が受け持つ部分)
2. prefill で flash_attention が k と v をどこから読むか。射影の直後の k, v を使うと壊れ、書き込み後のキャッシュから読み戻すと直る
3. エンジンだけが渡すもの (prompt_is_token_ids、系列全体の位置、block 0 を予約した block_table) と、その直し方
図の文字は英語。根拠は investigations/xtts-vllm-neuron の docs/STATUS.md (Step 19, 28, 32, 35, 36, 37) と results/measurements.md。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures.pptx"

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
RED = RGBColor(220, 38, 88)
RED_DK = RGBColor(70, 16, 32)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def arrow(s, x1, y1, x2, y2, color=WHITE, w=2.0):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=w)


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


YOU = (GRN_DK, GRN_HI)      # you write it
FW = (LINK_DK, LINK)        # framework provides it

# ------------------------------------------------------------------ 1. who writes what
s = d.slide()
title(s.s, "Who writes what", "Same GPT decoder, two ways onto Trainium")
label(s.s, 300, 116, 440, 30, "NxD Inference", size=17, bold=True, color=MUTED)
label(s.s, 790, 116, 440, 30, "vLLM Neuron plugin", size=17, bold=True, color=MUTED)
rows = [
    ("generate() loop", ("bridge class for\nHugging Face generate()", YOU), ("vLLM scheduler", FW)),
    ("prefill / decode", ("2 applications,\nKV copied via CPU", YOU), ("1 model, branch on\nattn_metadata", YOU)),
    ("KV cache", ("aliases", FW), ("paged cache by vLLM\n+ your scatter / gather", YOU)),
    ("Layers", ("attention, MLP, norms", YOU), ("projections, MLP, norms,\nembeddings, decode mask", YOU)),
    ("NKI kernels", ("-", (CHIP, EDGE)), ("flash_attention,\nmerge_prompt_embeds", FW)),
]
for k, (name, a, b) in enumerate(rows):
    y = 150 + k * 90
    label(s.s, 43, y, 240, 76, name, size=17, bold=True, align="left")
    box(s.s, 300, y, 440, 76, a[1][0], stroke=a[1][1], body=a[0], size=15)
    box(s.s, 790, y, 440, 76, b[1][0], stroke=b[1][1], body=b[0], size=15)
box(s.s, 43, 616, 24, 18, *YOU)
label(s.s, 74, 612, 140, 26, "you write it", size=13, color=MUTED, align="left")
box(s.s, 230, 616, 24, 18, *FW)
label(s.s, 261, 612, 200, 26, "framework provides it", size=13, color=MUTED, align="left")

# ------------------------------------------------------------------ 2. the prefill fix
s = d.slide()
title(s.s, "Prefill: where flash_attention reads k and v from",
      "30 layers, real weights, one torch.compile, vs CPU fp32 (first token 225)")


def chain(y, steps):
    x = 43
    for i, (txt, kind) in enumerate(steps):
        fill, st = {"op": (CHIP, EDGE), "kv": (YEL_DK, YEL), "fa": (GRN_DK, GRN_HI)}[kind]
        box(s.s, x, y, 150, 56, fill, stroke=st, body=txt, size=14)
        if i < len(steps) - 1:
            arrow(s.s, x + 150, y + 28, x + 174, y + 28)
        x += 174


label(s.s, 43, 118, 800, 28, "k, v straight from the projection", size=17, bold=True, color=RED, align="left")
chain(156, [("q, k, v", "op"), ("KV write", "kv"), ("flash_attention", "fa"), ("o_proj", "op")])
sh.arrow(s.s, t, 118, 212, 118, 240, color=RED, width=1.5)
sh.arrow(s.s, t, 118, 240, 440, 240, color=RED, width=1.5)
sh.arrow(s.s, t, 440, 240, 440, 212, color=RED, width=1.5)
box(s.s, 960, 156, 270, 56, RED_DK, stroke=RED, body="cosine 0.814, token 1023", size=15)
label(s.s, 43, 290, 800, 28, "k, v read back from the cache after the write", size=17, bold=True, color=GRN_HI, align="left")
chain(328, [("q, k, v", "op"), ("KV write", "kv"), ("read back", "kv"), ("flash_attention", "fa"), ("o_proj", "op")])
box(s.s, 960, 328, 270, 56, GRN_DK, stroke=GRN_HI, body="cosine 0.999988, token 225", size=15)
label(s.s, 43, 450, 800, 28, "Decode", size=17, bold=True, color=MUTED, align="left")
chain(488, [("q, k, v", "op"), ("KV write", "kv"), ("gather", "kv"), ("matmul + softmax", "op")])
box(s.s, 960, 488, 270, 56, CHIP, stroke=EDGE, body="no flash_attention", size=15)

# ------------------------------------------------------------------ 3. what only the engine sends
s = d.slide()
title(s.s, "What the engine sends that a hand-written loop did not",
      "Each one breaks generation; each fix is small")
label(s.s, 43, 112, 230, 30, "", size=14)
label(s.s, 290, 112, 450, 30, "engine sends", size=15, color=MUTED)
label(s.s, 790, 112, 450, 30, "fix", size=15, color=MUTED)
rows3 = [
    ("prompt_is_token_ids", "dropped by the plugin\nprefix replaced by token 0", ("1-line patch to the\ninstalled plugin", FW)),
    ("positions", "global index\nfirst audio token = 69", ("local index =\ncumsum(is_token_ids) - 1", YOU)),
    ("block_table", "[1, 2, 3, -1]\nblock 0 reserved, -1 = none", ("clamp -1 to 0,\nmask from block_table[0]", YOU)),
]
for k, (name, sent, (fix, col)) in enumerate(rows3):
    y = 150 + k * 120
    label(s.s, 43, y, 240, 90, name, size=17, bold=True, align="left")
    box(s.s, 290, y, 450, 90, CHIP, stroke=EDGE, body=sent, size=15)
    arrow(s.s, 740, y + 45, 790, y + 45)
    box(s.s, 790, y, 440, 90, col[0], stroke=col[1], body=fix, size=15)
box(s.s, 43, 616, 24, 18, *YOU)
label(s.s, 74, 612, 140, 26, "model code", size=13, color=MUTED, align="left")
box(s.s, 230, 616, 24, 18, *FW)
label(s.s, 261, 612, 200, 26, "plugin", size=13, color=MUTED, align="left")

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
