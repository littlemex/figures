"""gen_figs.py — Zenn 686da5f92f511f の図 5 枚を、ネイティブ shape の pptx で組む。

    /usr/bin/python3 gen_figs.py <out.pptx>

1. Trainium 向けの推論コードの置き場所 (エンジン / プラグイン / contrib / nki-library)
2. GPU: 1 つの演算に多数のカーネル、実行時に選ぶ (vLLM の MoE oracle、SGLang の KernelSpec)
3. Neuron: 1 モデルに複数のカーネル (GPT-OSS の例)
4. 差分の測り方: FP32 を共通の基準にした three-way 比較
5. 提案: 共有の単位を 3 段に分ける
見た目は nxd_interfaces_pptx.py と同じ (ZN-25)。根拠は記事本文の permalink。
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.dml import MSO_LINE  # noqa: E402

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


# ------------------------------------------------------------------ 1. where the code lives
s = d.slide()
title(s.s, "Where Trainium inference code lives",
      "Grey: engine.  Blue: plugin.  Green: community contrib.  Yellow: nkilib.  Dashed: not public or temporary")
box(s.s, 43, 116, 580, 56, GREY, stroke=EDGE, body="vLLM", size=19)
box(s.s, 657, 116, 580, 56, GREY, stroke=EDGE, body="SGLang", size=19)
# vllm-neuron
box(s.s, 43, 190, 580, 300, LINK_DK, stroke=LINK, radius=0.04)
label(s.s, 59, 196, 548, 32, "vllm-neuron plugin", size=18, bold=True, color=LINK, align="left")
box(s.s, 59, 236, 268, 74, CHIP, stroke=LINK, body="vllm_neuron/model/\nofficial models", size=15)
box(s.s, 339, 236, 268, 74, GRN_DK, stroke=GRN, body="contrib/models/<m>/\nmodel + own kernels", size=15)
box(s.s, 59, 322, 548, 70, CHIP, stroke=LINK, body="functional/  nn/   shared operators\n_kernels/   in-tree NKI kernels, some ported from nkilib", size=15)
box(s.s, 59, 404, 548, 70, CHIP, stroke=YEL, dash=MSO_LINE.DASH,
    body="functional/vendored_kernels/\ntemporary copies of nkilib", size=15)
# sglang plugin
box(s.s, 657, 190, 580, 300, LINK_DK, stroke=LINK, radius=0.04, dash=MSO_LINE.DASH)
label(s.s, 673, 196, 548, 32, "SGLang Trainium plugin (beta)", size=18, bold=True, color=LINK, align="left")
box(s.s, 673, 236, 548, 238, CHIP, stroke=EDGE, dash=MSO_LINE.DASH,
    body="built on TorchNeuron\nSGLang model components carried over\nNKI for custom kernels\n\nno repository link in the announcement", size=15, color=MUTED)
# nkilib
box(s.s, 43, 512, 1194, 86, YEL_DK, stroke=YEL, radius=0.12,
    body="nki-library (nkilib):  core/   experimental/   models/\nbundled in neuronx-cc;  pip-installed nki-library takes precedence", size=16)
for x in (180, 470):
    sh.arrow(s.s, t, x, 490, x, 512, color=YEL, width=2)

# ------------------------------------------------------------------ 2. GPU: one op, many kernels
s = d.slide()
title(s.s, "GPU: under shared layers, the engine picks the kernel",
      "Green: model code.  Blue: engine selection.  Grey: kernel implementations")
# vLLM side
label(s.s, 43, 110, 580, 30, "vLLM: FP8 MoE, 8 of 15 candidates", size=18, bold=True, color=LINK, align="left")
box(s.s, 43, 146, 580, 56, GRN_DK, stroke=GRN, body="model.py  ->  FusedMoE layer", size=16)
box(s.s, 43, 216, 580, 56, LINK_DK, stroke=LINK, body="oracle: priority list by platform and config", size=16)
ks = ["FlashInfer TRT-LLM", "FlashInfer CUTLASS", "DeepGEMM", "vLLM CUTLASS", "Triton", "Marlin", "AITER (ROCm)", "XPU / CPU"]
for i, k in enumerate(ks):
    x, y = 43 + (i % 2) * 295, 290 + (i // 2) * 58
    box(s.s, x, y, 285, 48, CHIP, stroke=EDGE, body=k, size=15)
# SGLang side
label(s.s, 657, 110, 580, 30, "SGLang: sglang.kernels, 4 of the sources", size=18, bold=True, color=LINK, align="left")
box(s.s, 657, 146, 580, 56, GRN_DK, stroke=GRN, body="model.py  ->  ops.<group> facade", size=16)
box(s.s, 657, 216, 580, 56, LINK_DK, stroke=LINK, body="KernelSpec + CapabilityRequirement -> select", size=16)
ks2 = [("JIT / AOT", "CUDA and ROCm"), ("Triton", "device set per kernel"), ("aiter / torch_npu", "one device each"),
       ("PLUGIN", "one model, config, platform")]
for i, (k, v) in enumerate(ks2):
    y = 290 + i * 58
    box(s.s, 657, y, 280, 48, CHIP, stroke=EDGE, body=k, size=15)
    label(s.s, 947, y, 290, 48, v, size=15, color=MUTED, align="left")
box(s.s, 43, 534, 1194, 56, YEL_DK, stroke=YEL, radius=0.3,
    body="Used by both engines: FlashInfer (vLLM pins 0.7.2.post1, SGLang pins 0.7.2)", size=16)
label(s.s, 43, 596, 1194, 30, "Newer vLLM models also keep per-hardware code: vllm/models/<model>/{common, nvidia, amd, cpu, xpu}",
      size=15, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. Neuron: one model, many kernels
s = d.slide()
title(s.s, "Neuron: one model already has several kernels",
      "nkilib core attention and GPT-OSS, 2026-10.  Yellow: nkilib.  Blue: vllm-neuron")
cols = [(43, "by phase (core, all models)", YEL_DK, YEL, ["core attention_cte\nprefill", "core attention_tkg\ndecode"]),
        (448, "decode kernels for GPT-OSS", YEL_DK, YEL, ["models/gpt_oss/\nc128_giga_kernel", "c128spec_giga_kernel", "c512_giga_kernel"]),
        (853, "by weight format and goal", LINK_DK, LINK, ["model_bf16.py", "model_mxfp4.py", "model_mxfp4_perf.py"])]
for x, head, fill, stroke, items in cols:
    label(s.s, x, 112, 384, 34, head, size=20, bold=True, color=stroke, align="left")
    for i, it in enumerate(items):
        box(s.s, x, 156 + i * 96, 384, 80, fill, stroke=stroke, body=it, size=16)
box(s.s, 43, 470, 1194, 100, CHIP, stroke=EDGE, radius=0.12,
    body="The GPT-OSS C128 decode kernel is a hand-maintained copy,\n"
         "kept apart on purpose from the core kernels other models use", size=17)

# ------------------------------------------------------------------ 4. three-way comparison
s = d.slide()
title(s.s, "Do not ask for equal bits; ask for no extra error",
      "vllm-neuron module tests.  Grey: CPU runs.  Blue: the run under test.  BF16 as an example")
box(s.s, 470, 120, 340, 70, GREY, stroke=WHITE, body="FP32 on CPU\nbaseline", size=17)
box(s.s, 120, 300, 340, 70, GREY, stroke=EDGE, body="BF16 on CPU\ndtype reference", size=17)
box(s.s, 820, 300, 340, 70, LINK_DK, stroke=LINK, body="BF16 on Neuron\ntarget", size=17)
sh.arrow(s.s, t, 290, 300, 560, 190, color=MUTED, width=2)
sh.arrow(s.s, t, 990, 300, 720, 190, color=LINK, width=2)
label(s.s, 150, 220, 330, 30, "reference error", size=16, color=MUTED)
label(s.s, 800, 220, 330, 30, "target error", size=16, color=LINK)
box(s.s, 120, 410, 1040, 64, GRN_DK, stroke=GRN, radius=0.3,
    body="pass if ( BC >= 0.99 (default)  or  sigma-ratio <= 1.0 )  and the per-input guards", size=19)
label(s.s, 120, 482, 1040, 60,
      "BC: overlap of the two error distributions.   sigma-ratio: RMS(target error) / RMS(reference error)",
      size=15, color=MUTED)
box(s.s, 120, 548, 1040, 50, YEL_DK, stroke=YEL, radius=0.3,
    body="per-input guards (defaults):  worst L-inf ratio < 5   and   worst L2 ratio < 3", size=16)

# ------------------------------------------------------------------ 5. RFC proposal
s = d.slide()
title(s.s, "Proposal: an RFC for three missing pieces",
      "Grey: today, 2026-10-31.  Green: what the RFC would write down")
label(s.s, 43, 104, 300, 28, "topic", size=15, color=MUTED, align="left")
label(s.s, 357, 104, 400, 28, "today", size=15, color=MUTED, align="left")
label(s.s, 771, 104, 466, 28, "RFC proposes", size=15, color=GRN_HI, align="left")
rows = [("path into nkilib", "PRs move to internal review;\nrelease timing hard to follow", "publish the intake path and the SDK\nthat ships it; copies record their source", YEL_DK, YEL),
        ("placement and\ncontract versions", "contrib folder per model;\nMRv2 asked in a PR comment", "split by dependency and owner;\nversion runner, nkilib and SDK", LINK_DK, LINK),
        ("reviewer group", "Neuron team reviews;\nno CODEOWNERS, no contrib merged", "reviewers earned by track record;\nNeuron team keeps the merge", GRN_DK, GRN)]
y = 138
for name, now, rfc, fill, stroke in rows:
    box(s.s, 43, y, 300, 124, fill, stroke=stroke, body=name, size=19)
    box(s.s, 357, y, 400, 124, CHIP, stroke=EDGE, body=now, size=16, color=MUTED)
    box(s.s, 771, y, 466, 124, CHIP, stroke=GRN, body=rfc, size=16)
    y += 140
label(s.s, 43, 562, 1194, 36, "Shared yardstick in the same RFC: three-way per module, Transformers comparison per model, SDK / nkilib / instance recorded",
      size=15, color=MUTED, align="left")

d.save(OUT)
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
