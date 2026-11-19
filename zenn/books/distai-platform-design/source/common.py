"""common.py -- shared helpers for the distai-platform-design book figures.

All chapter generators (gen_<prefix>.py) import this module. It wraps pptxkit's
Deck/shapes with the same look as templates/nxd_interfaces_pptx.py: AWS dark
template, native shapes, English labels, role colours with a faint pattern
(ZN-29), legend line under the subtitle (ZN-25), stripped branding (ZN-24).

    python3 gen_00.py            # writes 00-introduction.pptx next to it

Figure kinds used in the book: relation, flow, position. All three are drawn
with the same primitives (box/label/arrow); the kind only guides the layout.
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_ZENN_DOC_TEMPLATES = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, _ZENN_DOC_TEMPLATES)
from patterns import pattern_fill  # noqa: E402
import strip_branding  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"

# -- palette (same roles as nxd_interfaces_pptx.py) --------------------------
GRN = RGBColor(36, 160, 70)
GRN_HI = RGBColor(59, 209, 111)
GRN_DK = RGBColor(18, 64, 34)
LINK = RGBColor(40, 150, 240)
LINK_HI = RGBColor(110, 190, 250)
LINK_DK = RGBColor(16, 44, 72)
YEL = RGBColor(251, 211, 50)
YEL_DK = RGBColor(80, 66, 14)
RED = RGBColor(230, 90, 90)
RED_DK = RGBColor(74, 24, 24)
CHIP = RGBColor(22, 26, 30)
EDGE = RGBColor(70, 74, 80)
GREY = RGBColor(52, 56, 64)
MUTED = RGBColor(150, 150, 158)
WHITE = RGBColor(245, 245, 248)

ROLE_PATTERN = {GRN_DK: "diagonal", LINK_DK: "cross", YEL_DK: "grid", RED_DK: "backdiagonal"}


def new_deck():
    return Deck(TPL, check_layout=False)


def label(s, t, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center",
          anchor="middle"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold,
                       align=align, anchor=anchor)


def box(s, t, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE,
        radius=0.1, dash=None, sw=1.25, pattern=True, align="center"):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if pattern:
        pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, align, "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def diamond(s, t, x, y, w, h, fill, stroke, body="", size=14, color=WHITE):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=1.25,
                 shape=MSO_SHAPE.DIAMOND)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    if body:
        sh._write(sp.text_frame, t, body, size, color, True, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = sh.U(4)
        tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def arrow(s, t, x1, y1, x2, y2, color=WHITE, width=2, dashed=False, head=False,
          both=False):
    """Single-headed by default: the arrowhead lands on (x2, y2).

    pptxkit's sh.arrow always draws a "tail" endcap (which renders at the end
    point) and only adds a second head when `head=True` -- so `head=True` here
    means a double-headed arrow, not "has a head". Use `both=True` for that.
    """
    return sh.arrow(s, t, x1, y1, x2, y2, color=color, width=width, dashed=dashed,
                     head=both or head)


def box2(s, t, x, y, w, h, fill, stroke, head, sub=None, size=16, sub_size=13,
          color=WHITE, sub_color=MUTED, pad=14, align="left", head_bold=True):
    """A frame (with role pattern) plus a bold heading and an optional muted
    sub-line, laid out top-to-bottom so the two texts never overlap."""
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=1.25,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke)
    inner_w = w - pad * 2
    hy = y + pad
    import pptxkit.measure as ms
    hh = ms.text_h(head, inner_w, size)
    label(s, t, x + pad, hy, inner_w, hh, head, size=size, color=color, bold=head_bold,
          align=align, anchor="top")
    if sub:
        sy = hy + hh + 4
        sh_ = ms.text_h(sub, inner_w, sub_size)
        label(s, t, x + pad, sy, inner_w, sh_, sub, size=sub_size, color=sub_color,
              align=align, anchor="top")
    return sp


def title(s, t, head, sub=None):
    label(s, t, 43, 26, 1194, 40, head, size=27, bold=True, align="left")
    if sub:
        label(s, t, 43, 68, 1194, 24, sub, size=15, color=MUTED, align="left")


def legend(s, t, x, y, items, size=13, chip=16, gap=30):
    """items = [(fill, stroke, text), ...] drawn as one line of pattern chips."""
    cx = x
    for fill, stroke, text in items:
        box(s, t, cx, y, chip, chip, fill, stroke=stroke, radius=0.25, sw=1.25)
        tw = max(70, int(len(text) * size * 0.8) + 10)
        label(s, t, cx + chip + 6, y - 3, tw, chip + 6, text, size=size, color=MUTED,
              align="left", anchor="middle")
        cx += chip + 6 + tw + gap
    return cx


def render(pptx_path, names, outdir, dpi=160):
    """Convert pptx -> pdf -> one PNG per slide, named after `names` in order."""
    import subprocess
    base = os.path.splitext(os.path.basename(pptx_path))[0]
    pdf_path = os.path.join(os.path.dirname(pptx_path), base + ".pdf")
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "--convert-to", "pdf",
                     "--outdir", os.path.dirname(pptx_path), pptx_path],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=600)
    stem = os.path.join(outdir, "_page")
    subprocess.run(["/opt/homebrew/bin/pdftoppm", "-png", "-r", str(dpi), pdf_path, stem],
                    check=True)
    pages = sorted(f for f in os.listdir(outdir) if f.startswith("_page"))
    assert len(pages) == len(names), f"{len(pages)} pages vs {len(names)} names: {pages}"
    out = []
    for p, name in zip(pages, names):
        dst = os.path.join(outdir, name + ".png")
        os.replace(os.path.join(outdir, p), dst)
        out.append(dst)
    return out


def save_and_strip(d, pptx_path):
    d.save(pptx_path)
    strip_branding.main(pptx_path, pptx_path)
    return pptx_path
