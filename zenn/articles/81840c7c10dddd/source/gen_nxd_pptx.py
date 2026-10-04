"""gen_nxd_pptx.py — NxD Inference にカスタムモデルを載せる前編の図を、ネイティブ shape の pptx 3 枚で組む。

    /usr/bin/python3 gen_nxd_pptx.py <out.pptx>

1. 3 つのインタフェース (BaseModelInstance / ModelWrapper / NeuronApplicationBase) と、書くもの / NxD が持つもの
2. compile -> load -> load_weights -> forward の流れと、get_state_dict の 2 段階 (0 の重み / 実際の重み)
3. prefill と decode の分け方: 1 つの Application に 2 つの ModelWrapper (方法 A) と、2 つの Application (方法 B)
図の文字は英語。根拠は記事本文と neuronx-distributed-inference v0.7.14366、littlemex/samples (commit b6334ca)。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "nxd-figures.pptx"

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


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


# ------------------------------------------------------------------ 1. three interfaces
s = d.slide()
title(s.s, "Three interfaces you implement", "Green: you write it.  Blue: NxD Inference does the rest")
rows = [
    ("NeuronApplicationBase", "Application", "forward, get_state_dict, config",
     "compile, load, load_weights, TP sharding"),
    ("ModelWrapper", "Input shapes", "input_generator, get_model_instance",
     "buckets, compile loop"),
    ("BaseModelInstance", "Module + aliases", "load_module, get (aliases)",
     "trace with aliases, KV write-back"),
]
label(s.s, 43, 112, 300, 30, "Interface", size=15, color=MUTED, align="left")
label(s.s, 360, 112, 400, 30, "You write", size=15, color=GRN_HI, align="left")
label(s.s, 800, 112, 437, 30, "NxD Inference does", size=15, color=LINK, align="left")
y = 148
for name, role, mine, nxd in rows:
    box(s.s, 43, y, 300, 82, CHIP, stroke=EDGE, radius=0.08)
    label(s.s, 55, y + 6, 280, 36, name, size=18, bold=True, align="left")
    label(s.s, 55, y + 42, 280, 30, role, size=14, color=MUTED, align="left")
    box(s.s, 360, y + 10, 420, 62, GRN_DK, stroke=GRN, body=mine, size=15, radius=0.2)
    box(s.s, 800, y + 10, 437, 62, LINK_DK, stroke=LINK, body=nxd, size=15, radius=0.2)
    y += 100
# what it wraps
box(s.s, 43, 456, 300, 70, GREY, stroke=EDGE, body="nn.Module\nNeuronGPTTransformer", size=15)
sh.arrow(s.s, t, 193, 430, 193, 456, color=WHITE, width=2)
label(s.s, 360, 456, 877, 70, "KV cache: nn.Parameter  +  torch.scatter  +  output tuple", size=15, color=MUTED, align="left")
box(s.s, 43, 552, 1194, 52, YEL_DK, stroke=YEL, radius=0.3,
    body="Coordinator (plain class): prefill_app + decode_app + explicit KV sync", size=15)

# ------------------------------------------------------------------ 2. lifecycle
s = d.slide()
title(s.s, "Compile once, load and fill weights every time", "Blue: NxD Inference.  Green: you write it")
steps = [("compile()", "trace with sample inputs\nfrom input_generator", "once per configuration"),
         ("load()", "read the compiled model\ninto traced_model", "every start"),
         ("load_weights()", "shard and inject\nthe real weights", "every start"),
         ("forward()", "run; KV is written back\nby aliases", "every step")]
x = 43
W = 280
for i, (name, what, when) in enumerate(steps):
    box(s.s, x, 140, W, 64, LINK_DK if i < 3 else GRN_DK, stroke=LINK if i < 3 else GRN, body=name, size=20)
    label(s.s, x, 214, W, 60, what, size=14, color=WHITE)
    label(s.s, x, 278, W, 26, when, size=13, color=MUTED)
    if i < 3:
        sh.arrow(s.s, t, x + W, 172, x + W + 25, 172, color=WHITE, width=2)
    x += W + 25
# ------------------------------------------------------------------ 3. prefill / decode split
s = d.slide()
title(s.s, "Two ways to split prefill and decode", "One input shape per ModelWrapper (no buckets)")
for x, head, sub in ((43, "A. One Application", "e.g. Whisper decoder"),
                     (665, "B. Two Applications", "XTTS v2 GPT in this series")):
    label(s.s, x, 112, 572, 34, head, size=22, bold=True)
    label(s.s, x, 144, 572, 24, sub, size=14, color=MUTED)
    box(s.s, x, 178, 572, 330, CHIP, stroke=EDGE, radius=0.04)
# A
box(s.s, 73, 200, 512, 50, GRN_DK, stroke=GRN, body="Application", size=16)
box(s.s, 73, 270, 240, 56, GRN_DK, stroke=GRN, body="ModelWrapper\nprefill [B, S, D]", size=13)
box(s.s, 345, 270, 240, 56, GRN_DK, stroke=GRN, body="ModelWrapper\ndecode [B, 1, D]", size=13)
box(s.s, 73, 350, 512, 56, GREY, stroke=EDGE, body="one nn.Module, shared KV cache", size=15)
box(s.s, 73, 430, 512, 56, GRN_DK, stroke=GRN_HI, body="no KV copy needed", size=15)
# B
box(s.s, 695, 200, 240, 50, GRN_DK, stroke=GRN, body="prefill Application", size=14)
box(s.s, 967, 200, 240, 50, GRN_DK, stroke=GRN, body="decode Application", size=14)
box(s.s, 695, 270, 240, 56, GRN_DK, stroke=GRN, body="ModelWrapper\n[B, 1081, 1024]", size=13)
box(s.s, 967, 270, 240, 56, GRN_DK, stroke=GRN, body="ModelWrapper\n[B, 1, 1024]", size=13)
box(s.s, 695, 350, 240, 56, GREY, stroke=EDGE, body="KV cache", size=15)
box(s.s, 967, 350, 240, 56, GREY, stroke=EDGE, body="KV cache", size=15)
sh.arrow(s.s, t, 935, 378, 967, 378, color=YEL, width=2.5)
box(s.s, 695, 430, 512, 56, YEL_DK, stroke=YEL, body="explicit KV copy via CPU (.state) after prefill", size=15)
box(s.s, 43, 524, 572, 40, None, stroke=EDGE, body="relies on the order of self.models", size=14, color=MUTED, radius=0.3)
box(s.s, 665, 524, 572, 40, None, stroke=EDGE, body="named Applications; KV transfer is explicit", size=14, color=MUTED, radius=0.3)


def arrow(s, x1, y1, x2, y2, color=WHITE, w=1.75):
    sh.arrow(s, t, x1, y1, x2, y2, color=color, width=w)


def legend(s, y=600):
    box(s, 43, y + 4, 24, 18, GRN_DK, stroke=GRN)
    label(s, 74, y, 120, 26, "you write", size=13, color=MUTED, align="left")
    box(s, 200, y + 4, 24, 18, LINK_DK, stroke=LINK)
    label(s, 231, y, 160, 26, "NxD Inference", size=13, color=MUTED, align="left")


YOU = (GRN_DK, GRN)
NXD = (LINK_DK, LINK)

# ------------------------------------------------------------------ 4. compile, step by step
s = d.slide()
title(s.s, "app.compile(), step by step", "NxD asks; your methods answer.  Example: XTTS v2 prefill")
STEPS = [
    ("1", "Application", "ModelWrapper.input_generator()", "sample inputs\nhidden [1, 1081, 1024], last_pos, mask"),
    ("2", "Application", "ModelWrapper.get_model_instance()", "a BaseModelInstance: knows how to build the module"),
    ("3", "ModelBuilder", "BaseModelInstance.load_module()", "builds NeuronGPTTransformer (30 layers)"),
    ("4", "ModelBuilder", "BaseModelInstance.get()", "module + aliases\ncache_k -> outputs 1..30, cache_v -> 31..60"),
]
y = 128
for num, who, fn, ans in STEPS:
    box(s.s, 43, y, 44, 64, YEL_DK, stroke=YEL, body=num, size=20, radius=0.3)
    box(s.s, 100, y, 190, 64, *NXD, body=who + " asks", size=14)
    arrow(s.s, 290, y + 32, 320, y + 32)
    box(s.s, 320, y, 360, 64, *YOU, body=fn, size=14)
    arrow(s.s, 680, y + 32, 710, y + 32)
    label(s.s, 715, y, 522, 64, ans, size=14, color=WHITE, align="left")
    y += 84
box(s.s, 43, y, 44, 64, YEL_DK, stroke=YEL, body="5", size=20, radius=0.3)
box(s.s, 100, y, 580, 64, *NXD, body="ModelBuilder runs the sample once (trace) and compiles", size=15)
arrow(s.s, 680, y + 32, 710, y + 32)
box(s.s, 715, y, 522, 64, GREY, stroke=EDGE, body="compiled model, no weights yet", size=14)
legend(s.s)

# ------------------------------------------------------------------ 5. one inference step
s = d.slide()
title(s.s, "app(x): one decode step", "Only the hidden state comes back to you; K and V stay on the device")
box(s.s, 43, 150, 300, 80, *YOU, body="1  your forward()\nhidden, last_pos, mask", size=15)
arrow(s.s, 343, 190, 393, 190)
box(s.s, 393, 150, 340, 80, *NXD, body="2  compiled model on NeuronCores", size=15)
arrow(s.s, 733, 190, 783, 190)
# output tuple
label(s.s, 783, 120, 454, 26, "outputs", size=13, color=MUTED, align="left")
box(s.s, 783, 150, 110, 80, LINK_DK, stroke=LINK, body="[0]\nhidden", size=14)
box(s.s, 903, 150, 160, 80, YEL_DK, stroke=YEL, body="[1..30]\nnew K", size=14)
box(s.s, 1073, 150, 164, 80, YEL_DK, stroke=YEL, body="[31..60]\nnew V", size=14)
# K/V back to the device
box(s.s, 953, 470, 284, 80, GRN_DK, stroke=GRN_HI, body="KV cache on the device\ncache_k / cache_v", size=14)
sh.arrow(s.s, t, 1070, 230, 1070, 470, color=YEL, width=2)
label(s.s, 1080, 320, 160, 50, "3  aliases\ncopy back", size=13, color=YEL, align="left")
sh.arrow(s.s, t, 953, 510, 563, 510, color=GRN_HI, width=1.5)
sh.arrow(s.s, t, 563, 510, 563, 230, color=GRN_HI, width=1.5)
label(s.s, 573, 516, 340, 26, "read on the next step", size=13, color=GRN_HI, align="left")
# hidden back to you
sh.arrow(s.s, t, 838, 230, 838, 300, color=LINK, width=1.5)
box(s.s, 703, 300, 270, 70, *YOU, body="4  return outputs[0]", size=15)
legend(s.s)

# ------------------------------------------------------------------ 5. get_state_dict
s = d.slide()
title(s.s, "get_state_dict(): full-shape weights for NxD to split", "Who calls it depends on save_sharded_checkpoint")
for k, (head, a1, a2, a3) in enumerate([
    ("save_sharded_checkpoint=False  (default)", "load_weights()\nevery start", "split per rank", "initialize on device"),
    ("save_sharded_checkpoint=True", "compile()\nonce", "split + save to disk", "load_weights() reads it"),
]):
    y = 130 + k * 200
    label(s.s, 43, y, 800, 32, head, size=19, bold=True, color=YEL, align="left")
    box(s.s, 43, y + 44, 230, 70, *NXD, body=a1, size=15)
    arrow(s.s, 273, y + 79, 303, y + 79)
    box(s.s, 303, y + 44, 300, 70, *YOU, body="get_state_dict()\nfull (pre-split) shapes", size=14)
    arrow(s.s, 603, y + 79, 633, y + 79)
    box(s.s, 633, y + 44, 300, 70, *NXD, body=a2, size=15)
    arrow(s.s, 933, y + 79, 963, y + 79)
    box(s.s, 963, y + 44, 274, 70, *NXD, body=a3, size=15)
label(s.s, 43, 446, 600, 26, "this sample: set the checkpoint path before compile", size=13, color=YEL, align="left")
label(s.s, 303, 540, 300, 26, "this sample, path empty:", size=13, color=MUTED)
box(s.s, 303, 568, 300, 40, CHIP, stroke=EDGE, body="placeholder (zeros, LN = 1)", size=13)
label(s.s, 633, 540, 300, 26, "path set:", size=13, color=MUTED)
box(s.s, 633, 568, 300, 40, GRN_DK, stroke=GRN, body="real weights", size=13)

# ------------------------------------------------------------------ 6. KV cache on the device
s = d.slide()
title(s.s, "The KV cache lives on the device between calls", "Registered as a parameter, updated through the outputs")
box(s.s, 43, 150, 380, 110, GRN_DK, stroke=GRN_HI, sw=2, body="cache_k, cache_v\nnn.Parameter(requires_grad=False)", size=16)
label(s.s, 43, 266, 380, 24, "on the device, like the weights  |  no gradients", size=13, color=MUTED)
box(s.s, 520, 150, 330, 110, CHIP, stroke=EDGE, body="forward()\ntorch.scatter -> new K, V", size=16)
box(s.s, 940, 150, 297, 110, CHIP, stroke=EDGE, body="outputs\n(hidden, K..., V...)", size=16)
arrow(s.s, 423, 205, 520, 205, color=WHITE)
label(s.s, 423, 172, 97, 26, "read", size=13, color=MUTED)
arrow(s.s, 850, 205, 940, 205, color=WHITE)
box(s.s, 520, 380, 330, 80, *NXD, body="aliases: output i -> parameter", size=16)
sh.arrow(s.s, t, 1088, 260, 1088, 420, color=YEL, width=2)
sh.arrow(s.s, t, 1088, 420, 850, 420, color=YEL, width=2)
sh.arrow(s.s, t, 520, 420, 233, 420, color=YEL, width=2)
sh.arrow(s.s, t, 233, 420, 233, 290, color=YEL, width=2)
label(s.s, 240, 430, 270, 26, "overwrite for the next step", size=13, color=YEL, align="left")
legend(s.s)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
