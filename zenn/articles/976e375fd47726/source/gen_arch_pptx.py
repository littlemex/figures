"""gen_arch_pptx.py — Trainium のアーキテクチャ変遷と LNC を、ネイティブ shape の pptx 2 枚で組む。

    /usr/bin/python3 gen_arch_pptx.py <out.pptx>

図の文字は英語。出典は Neuron 公式ドキュメント (2026-10-04 取得)。
- trainium / trainium2 / trainium3.html: コア数、HBM、NeuronLink、CC-Cores
- neuron-core-v2 / v3 / v4.html: 4 エンジン、GPSIMD、sparsity、cFP8 exponent bias、
  near-memory accumulation、Vector Engine の MXFP8 量子化と fast exp
- logical-neuroncore-config.html: 24GB HBM バンク 4 本を 2 コアずつ共有、LNC=2 が既定で 4 論理コア
- trn1-arch / trn2-arch / trn3-arch.html: 2D torus、UltraServer 64、NeuronSwitch-v1 の all-to-all
"""
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "trainium-arch.pptx"

GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
HBM = RGBColor(52, 56, 64)
LINK = RGBColor(40, 150, 240)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)
BG_DARK = RGBColor(0, 0, 0)

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center",
          anchor="middle"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor=anchor)


def box(s, x, y, w, h, fill, stroke=None, body="", size=14, color=WHITE, radius=0.08,
        dash=None, sw=1.0):
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


# ------------------------------------------------------------------ 1. architecture
GENS = [
    dict(name="Trainium", sub="Trn1  |  NeuronCore-v2", cores=2, core="v2",
         hbm=["32 GiB"], link="NeuronLink-v2", cc=6,
         new=["4 engines per core", "GPSIMD custom ops", "Dynamic shapes",
              "Stochastic rounding"],
         topo="torus", topo_label="trn1.32xlarge\n16-chip 2D torus"),
    dict(name="Trainium2", sub="Trn2  |  NeuronCore-v3", cores=8, core="v3",
         hbm=["24 GB"] * 4, link="NeuronLink-v3", cc=16,
         new=["8 cores per chip", "Logical NeuronCore", "Structured sparsity",
              "cFP8 exponent bias"],
         topo="torus", topo_label="16-chip torus\n64 / UltraServer"),
    dict(name="Trainium3", sub="Trn3  |  NeuronCore-v4", cores=8, core="v4",
         hbm=["144 GiB"], link="NeuronLink-v4", cc=16,
         new=["MXFP8 / MXFP4", "Near-memory accumulation", "Fast exp on Vector",
              "NeuronSwitch-v1"],
         topo="switch", topo_label="UltraServer\nGen1: 64 chips\nGen2: 144 chips"),
]

s = d.slide()
title(s.s, "Trainium architecture, generation by generation",
      "Green tags: added in that generation")

COL_W, COL_X0, GAP = 360, 43, 61
for i, gnr in enumerate(GENS):
    x = COL_X0 + i * (COL_W + GAP)
    label(s.s, x, 112, COL_W, 34, gnr["name"], size=24, bold=True)
    label(s.s, x, 144, COL_W, 22, gnr["sub"], size=14, color=MUTED)

    # chip
    cy, ch = 172, 220
    box(s.s, x, cy, COL_W, ch, CHIP, stroke=EDGE, radius=0.04, sw=1.25)
    # HBM banks across the top of the chip
    nb = len(gnr["hbm"])
    bw = (COL_W - 24 - 8 * (nb - 1)) / nb
    for b in range(nb):
        box(s.s, x + 12 + b * (bw + 8), cy + 12, bw, 30, HBM, body=("HBM " if nb == 1 else "") + gnr["hbm"][b],
            size=11 if nb > 1 else 13, color=WHITE)
    # cores
    n = gnr["cores"]
    cols = 2 if n == 2 else 4
    rows = n // cols
    gx, gy, gw, gh = x + 12, cy + 52, COL_W - 24, 100
    cw = (gw - 8 * (cols - 1)) / cols
    chh = (gh - 8 * (rows - 1)) / rows
    for k in range(n):
        r, c = divmod(k, cols)
        box(s.s, gx + c * (cw + 8), gy + r * (chh + 8), cw, chh, GRN_DK, stroke=GRN,
            body="NC-" + gnr["core"], size=13 if n == 2 else 12, color=WHITE)
    # LNC=2 pairing, drawn only where the official page states it (Trainium2)
    if gnr["core"] == "v3":
        # the two cores under one HBM bank form one logical core
        for c in range(cols):
            box(s.s, gx + c * (cw + 8) - 3, gy - 4, cw + 6, 2 * chh + 16, None, stroke=GRN_HI,
                dash=MSO_LINE_DASH_STYLE.DASH, radius=0.1, sw=1.25)
    # bottom strip: link and collective cores
    sy = cy + ch - 56
    box(s.s, x + 12, sy, (COL_W - 32) * 0.58, 44, RGBColor(16, 44, 72), stroke=LINK,
        body=gnr["link"], size=13)
    box(s.s, x + 20 + (COL_W - 32) * 0.58, sy, (COL_W - 32) * 0.42, 44, HBM,
        body=f"{gnr['cc']} CC-Cores", size=13)

    # added in this generation
    ty = 404
    for j, tag in enumerate(gnr["new"]):
        box(s.s, x, ty + j * 34, COL_W, 29, GRN_DK, stroke=GRN_HI, body=tag, size=15,
            color=WHITE, radius=0.3)

    # scale-out topology glyph
    py = 552
    if gnr["topo"] == "torus":
        pts = [(x + 40 + c * 34, py + 14 + r * 34) for r in range(3) for c in range(3)]
        for (ax, ay) in pts:
            for (bx_, by_) in pts:
                if (abs(ax - bx_) < 40 and ay == by_ and bx_ > ax) or \
                        (abs(ay - by_) < 40 and ax == bx_ and by_ > ay):
                    sh.arrow(s.s, t, ax, ay, bx_, by_, color=LINK, width=1.5)
        # torus: the edge nodes wrap around, drawn as stubs leaving the grid
        xs, ys = sorted({p_[0] for p_ in pts}), sorted({p_[1] for p_ in pts})
        for yy in ys:
            sh.rect(s.s, t, xs[0] - 18, yy - 1, 18, 2, fill=LINK)
            sh.rect(s.s, t, xs[-1], yy - 1, 18, 2, fill=LINK)
        for xx in xs:
            sh.rect(s.s, t, xx - 1, ys[0] - 18, 2, 18, fill=LINK)
            sh.rect(s.s, t, xx - 1, ys[-1], 2, 18, fill=LINK)
        for (ax, ay) in pts:
            box(s.s, ax - 9, ay - 9, 18, 18, GRN, radius=0.2)
    else:
        hub = (x + 108, py + 48)
        ring = [(hub[0] + dx, hub[1] + dy) for dx, dy in
                ((-68, -34), (0, -40), (68, -34), (-68, 34), (0, 40), (68, 34))]
        for (ax, ay) in ring:
            sh.arrow(s.s, t, hub[0], hub[1], ax, ay, color=LINK, width=1.5)
        box(s.s, hub[0] - 26, hub[1] - 13, 52, 26, RGBColor(16, 44, 72), stroke=LINK,
            body="SW", size=11)
        for (ax, ay) in ring:
            box(s.s, ax - 9, ay - 9, 18, 18, GRN, radius=0.2)
    label(s.s, x + 196, py + 12, COL_W - 196, 60, gnr["topo_label"], size=14, color=MUTED,
          align="left")

# arrows between generations
for i in range(2):
    ax = COL_X0 + (i + 1) * (COL_W + GAP) - GAP + 10
    sh.arrow(s.s, t, ax, 282, ax + GAP - 20, 282, color=GRN_HI, width=3)

# ------------------------------------------------------------------ 2. LNC
s = d.slide()
title(s.s, "Logical NeuronCore (LNC) on Trainium2",
      "8 physical cores per chip")

PAN = [
    dict(x=43, head="LNC = 1", group=1, foot="8 logical cores per chip",
         inst="trn2.48xlarge: 128 cores"),
    dict(x=665, head="LNC = 2  (default)", group=2, foot="4 logical cores per chip",
         inst="trn2.48xlarge: 64 cores"),
]
for p in PAN:
    x, w = p["x"], 572
    label(s.s, x, 118, w, 36, p["head"], size=24, bold=True,
          color=GRN_HI if p["group"] == 2 else WHITE)
    box(s.s, x, 160, w, 330, CHIP, stroke=EDGE, radius=0.04, sw=1.25)
    bw = (w - 24 - 3 * 12) / 4
    for b in range(4):
        bx = x + 12 + b * (bw + 12)
        box(s.s, bx, 176, bw, 44, HBM, body="HBM 24 GB", size=14)
        cw = (bw - 8) / 2
        for c in range(2):
            cx = bx + c * (cw + 8)
            sh.arrow(s.s, t, cx + cw / 2, 220, cx + cw / 2, 262, color=MUTED, width=1.25)
            box(s.s, cx, 262, cw, 110, GRN_DK, stroke=GRN, body="NC\nv3", size=15)
        if p["group"] == 1:
            for c in range(2):
                cx = bx + c * (cw + 8)
                box(s.s, cx - 3, 382, cw + 6, 34, None, stroke=GRN_HI, body="NC_v3", size=13,
                    color=GRN_HI, radius=0.2, sw=1.5)
        else:
            box(s.s, bx - 5, 254, bw + 10, 126, None, stroke=GRN_HI,
                dash=MSO_LINE_DASH_STYLE.DASH, radius=0.08, sw=2)
            box(s.s, bx - 5, 382, bw + 10, 34, None, stroke=GRN_HI, body="NC_v3d", size=13,
                color=GRN_HI, radius=0.2, sw=1.5)
    label(s.s, x, 430, w, 30, p["foot"], size=20, bold=True)
    label(s.s, x, 500, w, 28, p["inst"], size=18, color=MUTED)

box(s.s, 43, 560, 1194, 54, RGBColor(16, 20, 24), stroke=EDGE, radius=0.2,
    body="Runtime setting   =   Compiler setting", size=18,
    color=WHITE)


# ------------------------------------------------------------------ 3. near-memory accumulation
s = d.slide()
title(s.s, "Near-memory accumulation on NeuronCore-v4",
      "Adding incoming B into A in SRAM")

ACC = RGBColor(251, 211, 50)


def lane(y, head, head_color, steps):
    label(s.s, 43, y, 600, 34, head, size=22, bold=True, color=head_color, align="left")
    src = box(s.s, 43, y + 60, 170, 120, HBM, body="Source\nB", size=18)
    dma = box(s.s, 283, y + 90, 120, 60, RGBColor(16, 44, 72), stroke=LINK, body="DMA", size=18)
    sh.arrow(s.s, t, 213, y + 120, 283, y + 120, color=LINK, width=2)
    sram = box(s.s, 473, y + 46, 500, 148, CHIP, stroke=GRN, radius=0.06, sw=1.5)
    label(s.s, 485, y + 52, 200, 24, "SRAM", size=15, color=GRN_HI, align="left")
    return sram, dma


# without: land B in a spare buffer, then an engine reads A and B, adds, writes A back
sram, dma = lane(108, "Generic: copy, then add", MUTED, None)
b = box(s.s, 503, 190, 150, 70, HBM, stroke=MUTED, body="B  (copy)", size=18,
        dash=MSO_LINE_DASH_STYLE.DASH)
a = box(s.s, 793, 190, 150, 70, GRN_DK, stroke=GRN, body="A", size=22)
eng = box(s.s, 503, 320, 440, 52, HBM, stroke=EDGE, body="Engine:  A + B", size=18)
sh.arrow(s.s, t, 403, 225, 503, 225, color=LINK, width=2)
sh.arrow(s.s, t, 578, 260, 578, 320, color=MUTED, width=2)
sh.arrow(s.s, t, 838, 260, 838, 320, color=MUTED, width=2)
sh.arrow(s.s, t, 898, 320, 898, 260, color=MUTED, width=2)
for n_, (bx_, by_) in (("1", (439, 186)), ("2", (594, 276)), ("2", (854, 276)),
                       ("3", (914, 276))):
    sh.badge(s.s, t, bx_, by_, 28, n_, color=WHITE, fill=RGBColor(90, 90, 98), size=14)

# NeuronCore-v4: DMA does read-add-write into A in a single transfer
sram, dma = lane(400, "NeuronCore-v4", GRN_HI, None)
a = box(s.s, 643, 482, 220, 70, GRN_DK, stroke=ACC, body="A  \u2190  A + B", size=22, sw=2)
sh.arrow(s.s, t, 403, 520, 643, 517, color=ACC, width=3)
sh.badge(s.s, t, 439, 482, 28, "1", color=BG_DARK, fill=ACC, size=14)
label(s.s, 1003, 476, 234, 80, "read-add-write\nin one transfer", size=18, color=ACC,
      align="left")

d.save(OUT)
sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
