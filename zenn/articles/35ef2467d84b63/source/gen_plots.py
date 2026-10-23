"""gen_plots.py: draw val-loss.png and logit-lens-kl.png from the published results/summary.json.

Each evaluation is recorded as [step, loss]; one step reads 65,536 tokens (128 windows of 512).
  python3 gen_plots.py <summary.json> <out_dir>
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TOKENS_PER_STEP = 65_536
summary = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.facecolor": "#000000", "axes.facecolor": "#0d1117", "axes.edgecolor": "#5a6270",
                     "axes.labelcolor": "#e8edf2", "xtick.color": "#c9d3dc", "ytick.color": "#c9d3dc",
                     "text.color": "#e8edf2", "grid.color": "#2a323c", "legend.facecolor": "#0d1117",
                     "legend.edgecolor": "#5a6270", "font.size": 13})
colors = {"engram": "#3bd16f", "baseline": "#2f9bff"}
styles = ["-", "--", ":"]

fig, (ax, gap) = plt.subplots(2, 1, figsize=(10, 7.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
curves = {}
for variant in ("baseline", "engram"):
    for i, (seed, pts) in enumerate(sorted(summary[variant]["val_loss_curve"].items())):
        xy = [(step * TOKENS_PER_STEP / 1e6, loss) for step, loss in pts if step > 0]
        curves[(variant, seed)] = dict(xy)
        ax.plot(*zip(*xy), color=colors[variant], ls=styles[i % 3], alpha=0.9, lw=2, label=f"{variant} {seed}")
ax.set_ylabel("validation loss (lower is better)")
ax.set_ylim(3.2, 6.0)
ax.legend(ncol=2, fontsize=11)
ax.grid(alpha=0.3)
for i, seed in enumerate(sorted(summary["engram"]["val_loss_curve"])):
    e, b = curves[("engram", seed)], curves[("baseline", seed)]
    xs = sorted(set(e) & set(b))
    gap.plot(xs, [e[x] - b[x] for x in xs], color="#fbd332", ls=styles[i % 3], alpha=0.9, lw=2, label=seed)
gap.axhline(0, color="#5a6270", lw=1)
gap.set_ylabel("engram − baseline\n(below 0: engram lower)")
gap.legend(fontsize=11, title="seed", ncol=3)
gap.grid(alpha=0.3)
gap.set_xlabel("training tokens (millions)")
fig.tight_layout()
fig.savefig(out / "val-loss.png", dpi=150)

fig, ax = plt.subplots(figsize=(10, 5.6))
for variant in ("baseline", "engram"):
    kl = summary[variant]["kl_final_to_layer"][:-1]  # the last block's KL is zero by definition
    ax.errorbar(np.arange(len(kl)), [s["mean"] for s in kl], yerr=[s["std"] for s in kl], marker="o", capsize=3,
                lw=2, color=colors[variant], label=variant)
ax.set_xlabel("block (0 = first)")
ax.set_ylabel("KL to the model's own final prediction\n(lower = closer)")
ax.set_ylim(0, None)
ax.set_xticks(range(11))
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out / "logit-lens-kl.png", dpi=150)

# Engram off at evaluation: the trained Engram model with its lookup skipped, against the two trained models
e, b = summary["engram"], summary["baseline"]
vals = [("Engram model", e["val_ppl"]["mean"]), ("same model,\nEngram off at eval", e["val_ppl_engram_off"]["mean"]),
        ("baseline model", b["val_ppl"]["mean"])]
fig, ax = plt.subplots(figsize=(10, 5.2))
bars = ax.bar([v[0] for v in vals], [v[1] for v in vals], color=["#3bd16f", "#fbd332", "#2f9bff"], width=0.55)
for r, (_, v) in zip(bars, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 1.0, f"{v:.2f}", ha="center", fontsize=14)
ax.set_ylabel("validation perplexity (lower is better)")
ax.set_ylim(0, 70)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(out / "engram-off.png", dpi=150)
print(out)
