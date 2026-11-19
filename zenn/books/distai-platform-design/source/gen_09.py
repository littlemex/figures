"""Figures for 09-verification-operations.md."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (new_deck, title, box, box2, label, arrow, legend, save_and_strip,
                     render, GRN, GRN_DK, GRN_HI, LINK, LINK_DK, LINK_HI, YEL, YEL_DK,
                     RED, RED_DK, GREY, CHIP, EDGE, MUTED, WHITE)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "09-verification-operations.pptx")
d = new_deck()
NAMES = []
t = d.theme

# -------------------------------------------------------------------------- 09-problems
s = d.slide().s
title(s, t, "One label can't carry plan, approval and purchase at once")
box2(s, t, 43, 150, 460, 380, RED_DK, RED, "status: verifying  (1 label)",
     "same account as the AI\nnot bound to a commit\nplan can change after approval\nno purchase step for queued capacity",
     size=16, sub_size=14, color=RED, align="left", pad=20)
arrow(s, t, 523, 340, 603, 340, color=WHITE)
box2(s, t, 603, 150, 180, 120, LINK_DK, LINK, "plan comment", "head_sha", size=14,
     sub_size=13, color=LINK_HI, align="center")
box2(s, t, 803, 150, 180, 120, YEL_DK, YEL, "status: verifying", "approval", size=14,
     sub_size=13, color=YEL, align="center")
box2(s, t, 1003, 150, 196, 120, GRN_DK, GRN, "purchase approval", "MFA", size=14,
     sub_size=13, color=GRN_HI, align="center")
arrow(s, t, 783, 210, 803, 210, color=WHITE)
arrow(s, t, 983, 210, 1003, 210, color=WHITE)
box(s, t, 603, 300, 596, 70, CHIP, stroke=EDGE,
    body="plan is the truth; label is a derived display; approval binds to commit + plan; purchase needs MFA",
    size=13, color=MUTED, pattern=False)
NAMES.append("09-problems")

# ------------------------------------------------------------------------------ 09-gate
s = d.slide().s
title(s, t, "Go requires four things to line up, every time")
box2(s, t, 43, 170, 350, 80, LINK_DK, LINK, "plan comment", "head_sha", size=15,
     sub_size=13, color=LINK_HI, align="center")
box2(s, t, 423, 170, 350, 80, LINK_DK, LINK, "PR", "current head", size=15, sub_size=13,
     color=LINK_HI, align="center")
box2(s, t, 803, 170, 350, 80, LINK_DK, LINK, "checked out", "SHA", size=15, sub_size=13,
     color=LINK_HI, align="center")
arrow(s, t, 218, 250, 598, 330, color=LINK_HI)
arrow(s, t, 598, 250, 598, 330, color=LINK_HI)
arrow(s, t, 978, 250, 598, 330, color=LINK_HI)
box2(s, t, 418, 330, 360, 80, YEL_DK, YEL, "all three SHAs match", "status: verifying is set",
     size=15, sub_size=13, color=YEL, align="center")
arrow(s, t, 598, 410, 598, 460, color=WHITE)
box2(s, t, 418, 460, 360, 90, GRN_DK, GRN, "tier re-derived from main policy",
     "matches the plan's tier -> gate passes", size=15, sub_size=13, color=GRN_HI,
     align="center")
NAMES.append("09-gate")

# -------------------------------------------------------------------------------- 09-run
s = d.slide().s
title(s, t, "One run: gate to evidence")
steps = ["gate", "preflight\n(no cost)", "set\nexpireAfter", "try capacity\nin order",
         "apply +\ntraffic"]
x = 43
w = 205
gap = 16
for i, st in enumerate(steps):
    box(s, t, x, 160, w, 90, LINK_DK, stroke=LINK, body=st, size=14, color=LINK_HI)
    if i < len(steps) - 1:
        arrow(s, t, x + w, 205, x + w + gap, 205, color=WHITE)
    x += w + gap
arrow(s, t, x - gap - w // 2, 250, x - gap - w // 2, 300, color=WHITE)
outcomes = [("pass", GRN_DK, GRN, GRN_HI), ("fail", RED_DK, RED, RED),
            ("inconclusive", YEL_DK, YEL, YEL)]
ox = 243
for name, fill, stroke, col in outcomes:
    box(s, t, ox, 300, 220, 70, fill, stroke=stroke, body=name, size=15, color=col)
    arrow(s, t, ox + 110, 370, 653, 430, color=col)
    ox += 260
box2(s, t, 403, 430, 500, 90, CHIP, EDGE, "evidence comment  (one, on the PR)",
     "run-id, SHA, result + reason, region/AZ, type, timings, cost -- no account IDs or ARNs",
     size=15, sub_size=12, color=WHITE, align="center")
box(s, t, 43, 550, 1156, 50, CHIP, stroke=EDGE,
    body="cleanup always runs: delete workload, delete NodePool, confirm 0 instances by tag, return to baseline",
    size=13, color=MUTED, pattern=False)
NAMES.append("09-run")

save_and_strip(d, OUT)
if __name__ == "__main__":
    outdir = os.path.dirname(OUT)
    for p in render(OUT, NAMES, outdir):
        print(p)
