"""gen_figs.py -- figures for the Zenn article on EKS isolated / confidential pods (Nitro Sandbox).

    /usr/bin/python3 gen_figs.py <out.pptx>

One slide per figure, native shapes, English labels. Every number in a figure is a value measured
on the test cluster (EKS Auto Mode, ap-northeast-1, Kubernetes 1.37, m9g.xlarge) or a value quoted
from the public AWS documentation and the Nitro Isolation Engine whitepaper.

Roles carry a colour and a faint pattern, so they read without colour (ZN-29):
  green + diagonal  = the workload, your pod
  blue  + cross     = provided by AWS (Nitro, the sandbox runtime)
  yellow + grid     = visible to the node / caution
Arrows that mean different things differ in width and dash as well as colour.
"""
import os
import sys

sys.path.insert(0, "/Users/akazawt/works/data-science/tools/pptxkit")
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402

from pptxkit import Deck, shapes as sh  # noqa: E402

TPL_DIR = "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"
sys.path.insert(0, TPL_DIR)
from patterns import pattern_fill  # noqa: E402

TPL = "/Users/akazawt/works/data-science/tools/pptxkit/templates/aws-dark-2024.pptx"
OUT = sys.argv[1] if len(sys.argv) > 1 else "nitro-sandbox-figures.pptx"

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
MUTED = RGBColor(160, 160, 168)
WHITE = RGBColor(245, 245, 248)

ROLE_PATTERN = {GRN_DK: "diagonal", LINK_DK: "cross", YEL_DK: "grid"}

d = Deck(TPL, check_layout=False)
t = d.theme


def label(s, x, y, w, h, body, size=16, color=WHITE, bold=False, align="center"):
    return sh.textbox(s, t, x, y, w, h, body, size=size, color=color, bold=bold, align=align,
                      anchor="middle")


def box(s, x, y, w, h, fill, stroke=None, body="", size=15, color=WHITE, radius=0.1,
        dash=None, sw=1.25, bold=True):
    sp = sh.rect(s, t, x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    pattern_fill(sp, ROLE_PATTERN.get(fill), fill, stroke, strength=0.45)
    if body:
        sh._write(sp.text_frame, t, body, size, color, bold, "center", "middle")
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = sh.U(2)
    return sp


def frame(s, x, y, w, h, title=None, size=15):
    box(s, x, y, w, h, CHIP, stroke=EDGE, radius=0.03)
    if title:
        label(s, x + 14, y + 6, w - 28, 26, title, size=size, color=MUTED, align="left", bold=True)


def num(s, x, y, n):
    sp = sh.rect(s, t, x, y, 30, 30, fill=WHITE, stroke=WHITE, shape=MSO_SHAPE.OVAL)
    sh._write(sp.text_frame, t, str(n), 15, CHIP, True, "center", "middle")
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0


def title(s, head, sub):
    label(s, 43, 22, 1190, 46, head, size=28, bold=True, align="left")
    label(s, 43, 66, 1190, 26, sub, size=16, color=MUTED, align="left")


DEFAULT_LEGEND = [(GRN_DK, GRN, "your workload"), (LINK_DK, LINK, "provided by AWS"),
                  (YEL_DK, YEL, "seen by the node / refused")]


def legend(s, y=650, items=None):
    items = items or DEFAULT_LEGEND
    x = 43
    for fill, stroke, text in items:
        box(s, x, y, 34, 24, fill, stroke=stroke, radius=0.2)
        label(s, x + 42, y - 2, max(300, 10 * len(text)), 28, text, size=14, color=MUTED, align="left")
        x += max(330, 60 + 10 * len(text))


# ------------------------------------------------------------------ 1. shared kernel vs own kernel
s = d.slide().s
title(s, "Regular pods share the node's kernel; sandboxed pods do not",
      "Read inside each pod on one m9g.xlarge node. Compare boot_id (drawn at every boot); the version can coincide")
for x, head in ((43, "Regular pods (no runtimeClassName)"), (655, "Pods with runtimeClassName: isolated-sandbox")):
    frame(s, x, 108, 582, 520, head, size=17)
# left: pods on the node kernel, all on the hypervisor
for i, name in enumerate(["regular-a", "regular-b"]):
    box(s, 73 + i * 270, 160, 250, 140, GRN_DK, stroke=GRN, body=f"{name}\nboot_id cd6f...\nkernel 6.18.56", size=16)
box(s, 73, 316, 520, 110, GREY, stroke=EDGE,
    body="node kernel 6.18.56, boot_id cd6f...\nruns the containers of both pods", size=16)
box(s, 73, 448, 520, 60, LINK_DK, stroke=LINK, body="Nitro Hypervisor", size=16)
label(s, 73, 524, 520, 80, "A kernel bug or a container escape\nreaches every pod on the node", size=16)
# right: the node and three sandboxes side by side, each on the hypervisor
box(s, 685, 160, 150, 266, GREY, stroke=EDGE,
    body="node\nkernel 6.18.56\nboot_id cd6f...\n\nruns kubelet;\none shim and\none firecracker\nper pod", size=13)
ids = [("iso-a", "eb25..."), ("iso-b", "a43e..."), ("iso-c\n(no network)", "4452...")]
for i, (name, bid) in enumerate(ids):
    x = 847 + i * 124
    box(s, x, 160, 116, 266, LINK_DK, stroke=LINK, radius=0.06)
    label(s, x, 164, 116, 26, "Nitro Sandbox", size=12, color=LINK, bold=True)
    box(s, x + 6, 194, 104, 98, GRN_DK, stroke=GRN, body=f"{name}\ncontainer", size=13)
    box(s, x + 6, 302, 104, 114, LINK_DK, stroke=LINK_DK, body=f"own kernel\n6.18.54\nboot_id\n{bid}", size=13)
box(s, 685, 448, 520, 60, LINK_DK, stroke=LINK, body="Nitro Hypervisor: isolates CPU and memory", size=16)
label(s, 685, 524, 520, 80, "Each pod boots its own kernel;\nthe node kernel no longer runs the containers", size=16)
legend(s, items=[(GRN_DK, GRN, "pod / container"), (GREY, EDGE, "node (EC2 instance)"), (LINK_DK, LINK, "Nitro (provided by AWS)")])

# ------------------------------------------------------------------ 2. components and start-up flow
s = d.slide().s
title(s, "What starts when a pod sets runtimeClassName",
      "Process names as seen on the node and inside the guest; numbers match the steps in the text")
frame(s, 43, 108, 560, 430, "EKS node (EC2 instance)", size=17)
box(s, 73, 150, 230, 64, GREY, stroke=EDGE, body="kubelet", size=17)
box(s, 73, 240, 230, 64, GREY, stroke=EDGE, body="containerd", size=17)
box(s, 73, 330, 230, 80, LINK_DK, stroke=LINK, body="containerd-shim-\nnitro-sandbox-v2", size=15)
box(s, 73, 436, 230, 72, LINK_DK, stroke=LINK, body="firecracker\n(one per pod)", size=15)
sh.arrow(s, t, 188, 214, 188, 240, color=WHITE, width=2)
sh.arrow(s, t, 188, 304, 188, 330, color=WHITE, width=2)
sh.arrow(s, t, 188, 410, 188, 436, color=WHITE, width=2)
num(s, 320, 166, 1)
label(s, 356, 150, 230, 64, "pod spec with\nruntimeClassName", size=15, align="left")
num(s, 320, 404, 2)
label(s, 356, 388, 230, 64, "shim starts\nfirecracker", size=15, align="left")
# guest, beside the node, not inside it
frame(s, 640, 108, 597, 430, "Nitro Sandbox (own kernel, own memory)", size=17)
box(s, 670, 150, 537, 62, LINK_DK, stroke=LINK, body="nitro-sandbox-agent (runs its own containerd)", size=15)
box(s, 670, 230, 537, 62, LINK_DK, stroke=LINK, body="    Cedar policy check: images, exec, logs, mounts", size=15)
num(s, 680, 246, 4)
box(s, 670, 310, 260, 200, GRN_DK, stroke=GRN, body="container\n(your image)", size=15)
box(s, 947, 310, 260, 200, GRN_DK, stroke=GRN, body="container\n(same pod)", size=15)
num(s, 680, 320, 5)
sh.arrow(s, t, 303, 472, 640, 472, color=LINK, width=3, dashed=True)
label(s, 330, 478, 280, 30, "virtio devices + vsock", size=14, color=LINK)
box(s, 43, 556, 1194, 64, LINK_DK, stroke=LINK,
    body="    Nitro Hypervisor (under both): creates the VM from memory the node donates; the guest kernel boots", size=16)
num(s, 60, 573, 3)
legend(s, y=640, items=[(GREY, EDGE, "Kubernetes on the node"), (LINK_DK, LINK, "sandbox runtime and Nitro"), (GRN_DK, GRN, "your containers")])
label(s, 43, 672, 600, 28, "solid arrow: request order; dashed arrow: shim to agent, through firecracker", size=14, color=MUTED, align="left")

# ------------------------------------------------------------------ 3. what the node could read
s = d.slide().s
title(s, "What a root process on the node could find",
      "A marker computed inside each pod, searched for from a privileged pod on the same node")
cols = ["Regular pod", "isolated-sandbox", "confidential-sandbox"]
rows = [
    ("Container processes", ["visible", "not visible\n(firecracker + shim only)", "not measured"]),
    ("Marker in readable\nprocess memory", ["129,072 hits", "0 hits in 3,162 MiB\n(36 processes)", "0 hits in 3,209 MiB\n(32 processes)"]),
    ("Guest memory region\nin firecracker", ["(no guest)", "no read/write\npermission (---s)", "no read/write\npermission (---s)"]),
    ("Marker written\nto disk", ["not measured", "258,111 hits\nin overlay.img", "0 hits\nin overlay.img"]),
    ("Kernel log line", ["not measured", "not in node log", "not measured"]),
]
FOUND = ("visible", "129", "258")
x0, cw, y0, rh = 300, 312, 108, 98
for j, c in enumerate(cols):
    label(s, x0 + j * cw, y0, cw - 12, 34, c, size=17, bold=True)
for i, (name, cells) in enumerate(rows):
    y = y0 + 42 + i * rh
    label(s, 43, y, 250, rh - 12, name, size=16, bold=True, align="left")
    for j, cell in enumerate(cells):
        if cell in ("not measured", "(no guest)"):
            box(s, x0 + j * cw, y, cw - 12, rh - 14, GREY, stroke=EDGE, body=cell, size=15, color=WHITE)
            continue
        if cell.startswith("no read"):
            box(s, x0 + j * cw, y, cw - 12, rh - 14, LINK_DK, stroke=LINK, body=cell, size=15)
            continue
        fill, stroke = (YEL_DK, YEL) if cell.startswith(FOUND) else (GRN_DK, GRN)
        box(s, x0 + j * cw, y, cw - 12, rh - 14, fill, stroke=stroke, body=cell, size=15)
legend(s, y=650, items=[(YEL_DK, YEL, "found by the node"), (GRN_DK, GRN, "searched, not found"), (LINK_DK, LINK, "not readable"), (GREY, EDGE, "not measured")])

# ------------------------------------------------------------------ 4. attestation gate
s = d.slide().s
title(s, "KMS decrypts only for a pod with the approved policy",
      "One KMS key, one ciphertext, one IAM role with no policies of its own; three pods")
box(s, 83, 120, 290, 84, GREY, stroke=EDGE, body="before: genpolicy\nmanifest -> Cedar policy", size=15)
box(s, 83, 230, 290, 84, GREY, stroke=EDGE, body="predicted PCR17\n= hash of the policy", size=15)
sh.arrow(s, t, 208, 204, 208, 230, color=WHITE, width=2)
box(s, 450, 120, 400, 194, LINK_DK, stroke=LINK, radius=0.05)
label(s, 470, 126, 360, 30, "before: KMS key policy", size=16, color=LINK, bold=True)
box(s, 462, 162, 376, 140, LINK_DK, stroke=LINK_DK,
    body="allow Decrypt only if\nPCR17 = approved value and\nPCR8 signer = eks.amazonaws.com;\ndeny every other Decrypt", size=15)
sh.arrow(s, t, 373, 272, 450, 272, color=WHITE, width=2)
box(s, 900, 120, 337, 194, LINK_DK, stroke=LINK, radius=0.05)
label(s, 920, 126, 310, 30, "at run time: in the sandbox", size=16, color=LINK, bold=True)
box(s, 910, 162, 317, 140, LINK_DK, stroke=LINK_DK,
    body="policy hash in PCR17\nNitro signs an attestation\n(/dev/nsm), sent with\nkms:Decrypt", size=15)
sh.arrow(s, t, 900, 230, 850, 230, color=LINK, width=3, dashed=True)
cases = [
    ("A  confidential-sandbox\napproved policy", "decrypted\nplaintext sha256 matches", GRN_DK, GRN),
    ("B  confidential-sandbox, one env value\nchanged, policy regenerated to match", "denied as intended: AccessDeniedException\npredicted PCR17 differs from approved", GREY, EDGE),
    ("C  regular pod, same IAM role", "denied as intended: AccessDeniedException\nno /dev/nsm, no attestation", GREY, EDGE),
]
for i, (who, res, fill, stroke) in enumerate(cases):
    y = 350 + i * 92
    box(s, 90, y, 560, 76, GREY, stroke=EDGE, body=who, size=15)
    sh.arrow(s, t, 650, y + 38, 700, y + 38, color=WHITE, width=2)
    box(s, 700, y, 537, 76, fill, stroke=stroke, body=res, size=15)
legend(s, y=640, items=[(LINK_DK, LINK, "KMS and Nitro"), (GRN_DK, GRN, "decrypt allowed"), (GREY, EDGE, "input / decrypt denied")])

# ------------------------------------------------------------------ 5. isolation engine
s = d.slide().s
title(s, "Nitro Isolation Engine: the hypervisor split in two",
      "Arm exception levels (EL): EL1 kernel, EL2 hypervisor. Source: the public whitepaper")
for x, head in ((43, "Before: one Nitro Hypervisor"), (655, "Graviton5: Isolation Engine at EL2")):
    frame(s, x, 108, 582, 520, head, size=17)
label(s, 672, 180, 60, 60, "EL1", size=15, color=MUTED)
label(s, 672, 450, 60, 60, "EL2", size=15, color=MUTED)
# left
for i in range(3):
    box(s, 130 + i * 160, 150, 145, 120, GRN_DK, stroke=GRN, body="guest VM", size=16)
box(s, 130, 300, 465, 160, GREY, stroke=EDGE,
    body="Nitro Hypervisor\nmechanism (page tables, CPU state)\n+ operational decisions (scheduling,\ndevice emulation)", size=15)
label(s, 130, 480, 465, 56, "too large to prove correct", size=15, color=MUTED)
# right
box(s, 742, 150, 150, 120, GREY, stroke=EDGE, body="Nitro\nHypervisor\n(decisions only)", size=14)
for i in range(2):
    box(s, 906 + i * 150, 150, 138, 120, GRN_DK, stroke=GRN, body="guest VM", size=16)
sh.arrow(s, t, 817, 270, 817, 420, color=WHITE, width=2.5, head=True)
label(s, 826, 320, 200, 50, "restricted\nhypercall API", size=14, color=WHITE, align="left")
box(s, 742, 420, 452, 120, LINK_DK, stroke=LINK,
    body="Nitro Isolation Engine (Rust)\nmechanism only: page tables,\nsaved CPU state, IOMMU", size=15)
label(s, 742, 544, 452, 50, "model and proofs: about 330,000\nmachine-checked lines in Isabelle/HOL", size=14)
label(s, 742, 596, 452, 26, "I/O device management is not in the proof scope", size=13, color=MUTED)
legend(s, y=650, items=[(GRN_DK, GRN, "guest VM"), (LINK_DK, LINK, "model verified for VM setup, vCPU, memory"), (GREY, EDGE, "not formally verified")])

# ------------------------------------------------------------------ 6. noninterference
s = d.slide().s
title(s, "Confidentiality as noninterference",
      "After the example in the public blog: one public and one private register; the middle column is added")
label(s, 43, 104, 1194, 30, "The observer sees only the public register. Two machines that differ only in the private register look the same.",
      size=15, color=MUTED, align="left")
heads = ("Before: machines A and B", "A step that does not leak", "A step that leaks (the blog example)")
progs = ("", "public := 1", "if private = 1:\n    public := 1")
for x, h in zip((43, 448, 853), heads):
    frame(s, x, 144, 384, 440, h, size=16)


def machine(x, y, name, pub, priv):
    label(s, x, y, 160, 28, name, size=16, bold=True)
    box(s, x + 5, y + 34, 150, 56, YEL_DK, stroke=YEL, body=f"public: {pub}", size=16)
    box(s, x + 5, y + 100, 150, 56, GRN_DK, stroke=GRN, body=f"private: {priv}", size=16)


machine(68, 186, "A", 0, 0)
machine(248, 186, "B", 0, 1)
machine(473, 260, "A'", 1, 0)
machine(653, 260, "B'", 1, 1)
machine(878, 260, "A'", 0, 0)
machine(1058, 260, "B'", 1, 1)
for x, p in ((448, progs[1]), (853, progs[2])):
    box(s, x + 30, 186, 324, 62, GREY, stroke=EDGE, body=p, size=15)
label(s, 63, 500, 344, 70, "public registers match:\nthe observer cannot tell A from B", size=15)
box(s, 468, 500, 344, 70, GREY, stroke=EDGE, body="result: still indistinguishable,\nnothing learned", size=15)
box(s, 873, 500, 344, 70, GREY, stroke=EDGE, body="result: public now differs, the\nobserver learns the private value", size=15)
label(s, 43, 596, 1194, 40, "The proof shows every step in scope behaves like the middle column, except for the enumerated disclosures.",
      size=15, color=MUTED, align="left")
legend(s, y=650, items=[(GRN_DK, GRN, "private (hidden from the observer)"), (YEL_DK, YEL, "public (seen by the observer)")])

d.save(OUT)
import strip_branding  # noqa: E402
strip_branding.main(OUT, OUT)
print(OUT)
