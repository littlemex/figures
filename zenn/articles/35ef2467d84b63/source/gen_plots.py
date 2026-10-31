"""gen_plots.py: the charts of the Engram hands-on article, from the published results and trace.

    /usr/bin/python3 gen_plots.py <dir with summary.json, settling.json, nanogpt-hastings.json> <out_dir>

ZN-29: every series differs by colour (Okabe-Ito, safe for the common colour-vision deficiencies) and
also by marker, line style or hatch, and is named by a label next to it, so no chart is read by colour
alone. Engram is bluish green with circles and solid lines or "/" hatches; the model trained without
Engram is sky blue with squares and dashed lines or "x" hatches; the Engram model with the lookup
skipped is orange with triangles and dotted lines or "." hatches.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
summary = json.loads((src / "summary.json").read_text())
settling = json.loads((src / "settling.json").read_text())
trace = json.loads((src / "nanogpt-hastings.json").read_text())
TOKENS_PER_STEP = 65_536

plt.rcParams.update({"figure.facecolor": "#000000", "axes.facecolor": "#0b0f14", "axes.edgecolor": "#5a6270",
                     "axes.labelcolor": "#e8edf2", "xtick.color": "#c9d3dc", "ytick.color": "#c9d3dc",
                     "text.color": "#e8edf2", "grid.color": "#2a323c", "legend.facecolor": "#0b0f14",
                     "legend.edgecolor": "#5a6270", "font.size": 15, "hatch.linewidth": 1.2,
                     "font.family": ["Amazon Ember", "Helvetica Neue", "DejaVu Sans"]})
STYLE = {
    "engram": dict(color="#009E73", marker="o", ls="-", hatch="//", label="with Engram"),
    "baseline": dict(color="#56B4E9", marker="s", ls="--", hatch="xx", label="trained without Engram"),
    "engram_off": dict(color="#E69F00", marker="^", ls=":", hatch="..", label="with Engram, lookup skipped"),
}
SEED_MARK = {"1337": "o", "1338": "s", "1339": "^"}
SEED_LS = {"1337": "-", "1338": "--", "1339": ":"}


def line(ax, xs, ys, v, **kw):
    st = STYLE[v]
    kw = {"lw": 2.4, "ms": 7, **kw}
    return ax.plot(xs, ys, color=st["color"], marker=st["marker"], ls=st["ls"], **kw)


def tag(ax, x, y, v, text=None, **kw):
    ax.annotate(text or STYLE[v]["label"], (x, y), color=STYLE[v]["color"], fontsize=15, fontweight="bold", **kw)


def bars(ax, x, h, v, width, **kw):
    st = STYLE[v]
    return ax.bar(x, h, width, color=st["color"] + "55", edgecolor=st["color"], hatch=st["hatch"], lw=1.8, **kw)


# ---------------------------------------------------------------- validation loss during training
fig, (ax, gap) = plt.subplots(2, 1, figsize=(12, 8.4), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
curves = {}
for v in ("baseline", "engram"):
    for seed, pts in sorted(summary[v]["val_loss_curve"].items()):
        xy = [(step * TOKENS_PER_STEP / 1e6, loss) for step, loss in pts if step > 0]
        curves[(v, seed)] = dict(xy)
        line(ax, *zip(*xy), v, alpha=0.85, ms=5)
ax.set_ylabel("validation loss\n(lower is better)")
ax.set_ylim(3.2, 6.0)
ax.grid(alpha=0.3)
tag(ax, 39.3, 4.45, "engram", xytext=(16, 4.15), arrowprops=dict(arrowstyle="-", color=STYLE["engram"]["color"]))
tag(ax, 39.3, 4.63, "baseline", xytext=(48, 5.0), arrowprops=dict(arrowstyle="-", color=STYLE["baseline"]["color"]))
for seed in sorted(summary["engram"]["val_loss_curve"]):
    e, b = curves[("engram", seed)], curves[("baseline", seed)]
    xs = sorted(set(e) & set(b))
    gap.plot(xs, [e[x] - b[x] for x in xs], color="#F0E442", marker=SEED_MARK[seed], ls=SEED_LS[seed], lw=1.8, ms=6,
             alpha=0.9, label=f"seed {seed}")
gap.axhline(0, color="#8a94a0", lw=1.2)
gap.set_ylabel("with − without\n(below 0: Engram lower)")
gap.legend(fontsize=13, ncol=3, loc="lower right")
gap.grid(alpha=0.3)
gap.set_xlabel("training tokens (millions)")
fig.suptitle('Validation loss during training (3 seeds each)', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "val-loss.png", dpi=150)

# ---------------------------------------------------------------- Engram skipped at evaluation
e, b = summary["engram"], summary["baseline"]
vals = [("engram", "with Engram", e["val_ppl"]["mean"]),
        ("engram_off", "same weights,\nlookup skipped", e["val_ppl_engram_off"]["mean"]),
        ("baseline", "trained without\nEngram", b["val_ppl"]["mean"])]
fig, ax = plt.subplots(figsize=(12, 5.8))
for i, (v, name, val) in enumerate(vals):
    bars(ax, i, val, v, 0.55)
    ax.text(i, val + 1.2, f"{val:.2f}", ha="center", fontsize=17, fontweight="bold")
ax.set_xticks(range(3), [n for _, n, _ in vals])
ax.set_ylabel("validation perplexity\n(lower is better)")
ax.set_ylim(0, 70)
ax.grid(axis="y", alpha=0.3)
fig.suptitle('Validation perplexity (mean of 3 seeds)', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "engram-off.png", dpi=150)

# ---------------------------------------------------------------- LogitLens KL per block
fig, ax = plt.subplots(figsize=(12, 6.0))
for v in ("baseline", "engram"):
    kl = summary[v]["kl_final_to_layer"][:-1]  # the last block's KL is zero by definition
    st = STYLE[v]
    ax.errorbar(np.arange(len(kl)), [s["mean"] for s in kl], yerr=[s["std"] for s in kl], color=st["color"],
                marker=st["marker"], ls=st["ls"], lw=2.4, ms=8, capsize=3)
ax.axvline(0.5, color="#F0E442", ls="--", lw=1.5)
ax.text(0.58, 5.35, "Engram added here", color="#F0E442", fontsize=14)
tag(ax, 1, 2.91, "engram", xytext=(1.6, 1.9))
tag(ax, 5, 3.36, "baseline", xytext=(5.3, 3.75))
ax.set_xlabel("after block (0 = first)")
ax.set_ylabel("KL to the model's own\nfinal prediction (lower = closer)")
ax.set_ylim(0, 5.8)
ax.set_xticks(range(11))
ax.grid(alpha=0.3)
fig.suptitle('KL(final ‖ block), first 200 validation windows', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "logit-lens-kl.png", dpi=150)

# ---------------------------------------------------------------- where the top-1 stops changing
fig, ax = plt.subplots(figsize=(12, 6.0))
w = 0.27
order = ("engram", "engram_off", "baseline")
for k, v in enumerate(order):
    share = [s["mean"] * 100 for s in settling["variants"][v]["settled_block_share"]]
    bars(ax, np.arange(12) + (k - 1) * w, share, v, w)
for k, v in enumerate(order):
    val = settling["variants"][v]["settled_block_share"][1]["mean"] * 100
    ax.text(1 + (k - 1) * w, val + 0.5 + k * 1.6, f"{val:.1f}", ha="center", fontsize=13, color=STYLE[v]["color"],
            fontweight="bold")
for k, v in enumerate(order):
    ax.text(3.2, 26 - k * 2.6, STYLE[v]["label"], color=STYLE[v]["color"], fontsize=15, fontweight="bold")
    ax.bar(2.95, 1.6, 0.3, bottom=26 - k * 2.6 + 0.1, color=STYLE[v]["color"] + "55",
           edgecolor=STYLE[v]["color"], hatch=STYLE[v]["hatch"], lw=1.5)
ax.set_xticks(range(12))
ax.set_xlabel("block from which the top-1 next token no longer changes")
ax.set_ylabel("share of positions (%)")
ax.set_ylim(0, 30)
ax.grid(axis="y", alpha=0.3)
fig.suptitle('Where the top-1 stops changing (247,296 positions per seed)', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "settling.png", dpi=150)

# ---------------------------------------------------------------- the gate along one text
n_prompt = trace["generation"]["prompt_tokens"]
toks = [t["text"] for t in trace["tokens"]][:n_prompt]
gates = [g[0][0] for g in trace["gates"]][:n_prompt]
fig, ax = plt.subplots(figsize=(15, 6.2))
st = STYLE["engram"]
ax.bar(range(len(gates)), gates, 0.75, color=st["color"] + "55", edgecolor=st["color"], hatch=st["hatch"], lw=1.4)
low = [i for i, g in enumerate(gates) if g < 0.3]
for i in low:
    ax.bar(i, gates[i], 0.75, color=st["color"] + "55", edgecolor="#ffffff", hatch=st["hatch"], lw=2.2)
    ax.text(i, gates[i] + 0.03, f"{gates[i]:.2f}", ha="center", fontsize=13, color="#ffffff", fontweight="bold")
ax.axhline(0.5, color="#8a94a0", ls="--", lw=1.2)
ax.set_xticks(range(len(toks)), [t.replace(" ", "") or "␣" for t in toks], rotation=70, fontsize=12)
ax.set_xlim(-0.6, len(toks) - 0.4)
ax.set_ylim(0, 1.05)
ax.set_ylabel("gate α")
ax.grid(axis="y", alpha=0.3)
fig.suptitle('Gate α per token (seed 1337, 44 prompt tokens)', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "gate-text.png", dpi=150)

# ---------------------------------------------------------------- one position, block by block
alex = json.loads((src / "alexander.json").read_text())
POS = 2  # " the" of "Only Alexander the", followed by " Great"
assert alex["tokens"][POS]["text"] == " the" and alex["tokens"][POS + 1]["text"] == " Great"
fig, ax = plt.subplots(figsize=(12, 6.0))
for v in ("engram", "engram_off", "baseline"):
    line(ax, range(12), [blk["p_next"] for blk in alex["lens"]["values"][v][POS]], v)
ax.axvline(0.5, color="#F0E442", ls="--", lw=1.5)
ax.text(0.58, 1.02, "Engram added here", color="#F0E442", fontsize=14)
tag(ax, 0, 0, "engram", xytext=(6.3, 0.72))
tag(ax, 0, 0, "baseline", xytext=(6.0, 0.25))
tag(ax, 0, 0, "engram_off", xytext=(2.4, 0.07))
ax.set_xticks(range(12))
ax.set_xlabel("after block (0 = first)")
ax.set_ylabel('probability of the next token " Great"')
ax.set_ylim(0, 1.1)
ax.grid(alpha=0.3)
fig.suptitle('P(" Great") after each block at " the" (seed 1337)', x=0.01, ha="left", fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "alexander-blocks.png", dpi=150)
print(out)
