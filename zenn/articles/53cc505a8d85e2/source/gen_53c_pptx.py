"""gen_53c_pptx.py — 「XTTS v2 を AWS Neuron で動かす」(初学者向け) の図を、ネイティブ shape の pptx で組む。

    /usr/bin/python3 gen_53c_pptx.py <out.pptx>

1. XTTS v2 の部品と CPU / Neuron の分担 (GPT.forward だけを Neuron に載せる)
2. nn.Module: 重みと forward() を持つ部品で、部品の中に部品が入る
3. torch_neuronx.trace: 例の入力で一度流して記録し、その形専用の NEFF にする
4. 固定の形に合わせる: 足りない分を埋め、出力を実データの長さに切る。wav_lengths は音声コード数 x 1024
5. forward の差し替え: Coqui のコードは変えず、model.gpt.forward の行き先だけを変える
6. NxD Inference へ: この記事で手で書いたことを、NxD Inference ではどの部品が受け持つか
図の文字は英語。根拠は coqui-ai/TTS (commit eef419b) の xtts.py / gpt.py / hifigan_decoder.py と元記事の手順。
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: E402
from pptx.util import Pt  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "53c-figures.pptx"

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


def seg(s, x1, y1, x2, y2, color=MUTED, w=1.5):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, sh.U(x1), sh.U(y1), sh.U(x2), sh.U(y2))
    c.shadow.inherit = False
    c.line.color.rgb = color
    c.line.width = Pt(w)


def title(s, head, sub):
    label(s, 43, 26, 1190, 46, head, size=30, bold=True, align="left")
    label(s, 43, 72, 1190, 26, sub, size=16, color=MUTED, align="left")


def legend(s, y=596):
    box(s, 43, y + 4, 24, 18, *CPU)
    label(s, 74, y, 80, 26, "CPU", size=13, color=MUTED, align="left")
    box(s, 150, y + 4, 24, 18, *NEU)
    label(s, 181, y, 160, 26, "NeuronCores", size=13, color=MUTED, align="left")


CPU = (GREY, EDGE)
NEU = (GRN_DK, GRN_HI)

# ------------------------------------------------------------------ 1. pipeline
s = d.slide()
title(s.s, "XTTS v2 at a glance", "Two models in a row: GPT makes latents, HifiDecoder makes the waveform")
box(s.s, 43, 160, 180, 60, CHIP, stroke=EDGE, body="Reference audio", size=16)
box(s.s, 43, 380, 180, 60, CHIP, stroke=EDGE, body="Text", size=16)
box(s.s, 265, 160, 210, 60, *CPU, body="speaker features", size=15)
seg(s.s, 370, 160, 370, 112)
seg(s.s, 370, 112, 1150, 112)
sh.arrow(s.s, t, 1150, 112, 1150, 330, color=MUTED, width=1.5)
label(s.s, 960, 116, 190, 22, "speaker embedding", size=12, color=MUTED)
box(s.s, 265, 380, 210, 60, *CPU, body="text tokens", size=15)
arrow(s.s, 223, 190, 265, 190)
arrow(s.s, 223, 410, 265, 410)
# GPT
box(s.s, 520, 130, 400, 340, CHIP, stroke=LINK, sw=2, radius=0.04)
label(s.s, 520, 136, 400, 34, "GPT  (396M params)", size=20, bold=True, color=LINK)
box(s.s, 550, 184, 340, 110, *CPU, body="generate()\none audio code at a time", size=17)
box(s.s, 550, 330, 340, 110, *NEU, body="forward()\nall codes -> latents at once", size=17, sw=2)
arrow(s.s, 720, 294, 720, 330, color=YEL)
label(s.s, 730, 298, 170, 30, "audio codes", size=13, color=YEL, align="left")
arrow(s.s, 475, 190, 550, 230)
arrow(s.s, 475, 410, 550, 250)
arrow(s.s, 475, 418, 550, 385)
arrow(s.s, 475, 204, 550, 365)
# Hifi
box(s.s, 965, 330, 270, 110, *CPU, body="HifiDecoder  (12M)\nlatents -> waveform", size=16)
arrow(s.s, 890, 385, 965, 385, color=YEL)
label(s.s, 885, 345, 90, 30, "latents", size=13, color=YEL)
box(s.s, 1015, 500, 170, 56, CHIP, stroke=EDGE, body="24 kHz audio", size=16)
arrow(s.s, 1100, 440, 1100, 500)
legend(s.s)

# ------------------------------------------------------------------ 2. nn.Module
s = d.slide()
title(s.s, "nn.Module: weights + forward()", "Calling a module runs its forward(). Modules nest")
box(s.s, 43, 130, 700, 470, CHIP, stroke=EDGE, sw=2, radius=0.03)
label(s.s, 63, 140, 400, 34, "model  (Xtts, nn.Module)", size=18, bold=True, align="left")
box(s.s, 73, 190, 640, 200, LINK_DK, stroke=LINK, sw=2, radius=0.05)
label(s.s, 93, 196, 400, 30, "model.gpt  (GPT, nn.Module)", size=16, bold=True, align="left")
box(s.s, 103, 240, 260, 120, GREY, stroke=EDGE, body="weights\n(parameters)", size=16)
box(s.s, 403, 240, 280, 120, GRN_DK, stroke=GRN_HI, body="forward(inputs)\n-> outputs", size=16)
box(s.s, 73, 420, 640, 150, LINK_DK, stroke=LINK, sw=2, radius=0.06)
label(s.s, 93, 426, 500, 30, "model.hifigan_decoder  (HifiDecoder, nn.Module)", size=16, bold=True,
      align="left")
box(s.s, 103, 470, 260, 80, GREY, stroke=EDGE, body="weights", size=16)
box(s.s, 403, 470, 280, 80, GRN_DK, stroke=GRN_HI, body="forward(latents)", size=16)
box(s.s, 820, 240, 410, 70, CHIP, stroke=YEL, body="model.gpt(...)", size=20, color=YEL)
arrow(s.s, 820, 275, 683, 300, color=YEL)
label(s.s, 820, 320, 410, 30, "runs  model.gpt.forward(...)", size=15, color=MUTED)

# ------------------------------------------------------------------ 3. trace
s = d.slide()
title(s.s, "torch_neuronx.trace(): run once, record, compile", "The compiled model only accepts the shapes it was traced with")
box(s.s, 43, 170, 220, 120, LINK_DK, stroke=LINK, body="nn.Module\n+ example inputs\n[1, 50]  [1, 128]", size=15)
arrow(s.s, 263, 230, 313, 230)
box(s.s, 313, 170, 220, 120, CHIP, stroke=EDGE, body="record the ops\nthat ran", size=16)
arrow(s.s, 533, 230, 583, 230)
box(s.s, 583, 170, 220, 120, CHIP, stroke=EDGE, body="neuronx-cc", size=17)
arrow(s.s, 803, 230, 853, 230)
box(s.s, 853, 170, 380, 120, *NEU, body="compiled module (NEFF inside)\nfixed shapes", size=16, sw=2)
box(s.s, 853, 360, 380, 64, GRN_DK, stroke=GRN_HI, body="[1, 50]  [1, 128]   ->  runs", size=16)
box(s.s, 853, 450, 380, 64, RED_DK, stroke=RED, body="[1, 38]   ->  shape error", size=16)
arrow(s.s, 1043, 290, 1043, 360, color=GRN_HI)
label(s.s, 43, 360, 760, 150,
      "if / for: the example's path only",
      size=18, color=MUTED, align="left")

# ------------------------------------------------------------------ 4. pad and trim
s = d.slide()
title(s.s, "Fit real lengths into the fixed shape", "Pad to the bucket, run, then cut the output back")
UNIT = 7.0
X0 = 250


def row(y, name, n_real, n_pad, real_col, pad_col, txt):
    label(s.s, 43, y, 200, 50, name, size=16, bold=True, align="left")
    box(s.s, X0, y, n_real * UNIT, 50, real_col, stroke=EDGE, body=txt, size=15, radius=0.05)
    if n_pad:
        box(s.s, X0 + n_real * UNIT, y, n_pad * UNIT, 50, CHIP, stroke=pad_col,
            dash=MSO_LINE_DASH_STYLE.DASH, body="pad to 128", size=13, color=MUTED, radius=0.05)


row(150, "audio codes", 110, 0, LINK_DK, EDGE, "110 real")
row(240, "Neuron input", 110, 18, LINK_DK, EDGE, "110 real")
row(330, "Neuron output", 128, 0, GRN_DK, EDGE, "latents  [1, 128, 1024]")
row(420, "after trim", 109, 0, GRN_DK, EDGE, "first 110 kept")
arrow(s.s, X0 + 64 * UNIT, 200, X0 + 64 * UNIT, 240)
arrow(s.s, X0 + 64 * UNIT, 290, X0 + 64 * UNIT, 330)
arrow(s.s, X0 + 64 * UNIT, 380, X0 + 64 * UNIT, 420)
box(s.s, 250, 530, 900, 70, YEL_DK, stroke=YEL, body="trace example:  wav_lengths  =  128  x  1024", size=19)

# ------------------------------------------------------------------ 5. forward override
s = d.slide()
title(s.s, "Swap where model.gpt.forward goes", "Coqui TTS source files stay unchanged")
box(s.s, 43, 150, 360, 80, CHIP, stroke=EDGE, body="Coqui inference()\ncalls  self.gpt(...)", size=16)
arrow(s.s, 403, 190, 463, 190)
box(s.s, 463, 150, 300, 80, LINK_DK, stroke=LINK, sw=2, body="forward  (replaced)", size=17)

arrow(s.s, 763, 190, 833, 150, color=GRN_HI)
arrow(s.s, 763, 190, 833, 300, color=MUTED)
box(s.s, 833, 110, 400, 90, *NEU, sw=2, body="forward_neuron\ncompiled GPT", size=17)
box(s.s, 833, 260, 400, 90, *CPU, body="forward_original\nthe class's own forward", size=17)
label(s.s, 763, 112, 80, 26, "if set", size=13, color=GRN_HI)
label(s.s, 833, 204, 400, 26, "pad -> run -> trim", size=13, color=GRN_HI)
label(s.s, 763, 330, 80, 26, "else", size=13, color=MUTED)
box(s.s, 43, 420, 1190, 150, CHIP, stroke=EDGE, radius=0.04)
label(s.s, 63, 426, 600, 30, "Before trace", size=16, bold=True, color=YEL, align="left")
box(s.s, 73, 470, 520, 80, YEL_DK, stroke=YEL, body="forward  ->  forward_original\nwith return_latent=True fixed", size=15)
arrow(s.s, 593, 510, 663, 510, color=YEL)
box(s.s, 663, 470, 540, 80, CHIP, stroke=EDGE, body="trace(model.gpt, 5 tensors)", size=16)
legend(s.s)

# ------------------------------------------------------------------ 6. to NxD Inference
s = d.slide()
title(s.s, "From one trace to NxD Inference", "What this article does by hand, and who takes it over")
label(s.s, 300, 120, 440, 30, "This article  (torch_neuronx.trace)", size=16, bold=True, color=LINK)
label(s.s, 790, 120, 440, 30, "NxD Inference  (maintenance mode)", size=16, bold=True, color=GRN_HI)
rows6 = [
    ("Compiled part", "GPT.forward() only", "the decoder, every step"),
    ("Token loop", "generate() on CPU", "decode on Neuron with a KV cache"),
    ("Shapes", "one bucket, pad + trim", "buckets by length + mask"),
    ("Your code", "forward swap", "BaseModelInstance, ModelWrapper,\nNeuronApplicationBase"),
]
for k, (name, a, b) in enumerate(rows6):
    y = 160 + k * 112
    label(s.s, 43, y, 240, 90, name, size=17, bold=True, align="left")
    box(s.s, 300, y, 440, 90, LINK_DK, stroke=LINK, body=a, size=16)
    arrow(s.s, 740, y + 45, 790, y + 45)
    box(s.s, 790, y, 440, 90, GRN_DK, stroke=GRN_HI, body=b, size=16)

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
