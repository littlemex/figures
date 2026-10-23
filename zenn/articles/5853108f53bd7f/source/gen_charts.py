"""gen_charts.py: the chart in the Engram article (paper Table 1, MoE-27B vs Engram-27B).
  python3 gen_charts.py <out_dir>"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.facecolor": "#000000", "axes.facecolor": "#0d1117", "axes.edgecolor": "#5a6270",
                     "axes.labelcolor": "#e8edf2", "xtick.color": "#c9d3dc", "ytick.color": "#c9d3dc",
                     "text.color": "#e8edf2", "grid.color": "#2a323c", "legend.facecolor": "#0d1117",
                     "legend.edgecolor": "#5a6270", "font.size": 14})
# arXiv:2601.07372 Table 1: MoE-27B and Engram-27B (same total and activated parameters)
rows = [("MMLU", 57.4, 60.4), ("CMMLU", 57.9, 61.9), ("ARC-Challenge", 70.1, 73.8),
        ("BBH", 50.9, 55.9), ("HumanEval", 37.8, 40.8), ("MATH", 28.3, 30.7)]
x = np.arange(len(rows)); w = 0.38
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.bar(x - w / 2, [r[1] for r in rows], w, color="#2f9bff", label="MoE-27B")
ax.bar(x + w / 2, [r[2] for r in rows], w, color="#3bd16f", label="Engram-27B")
for i, (_, a, b) in enumerate(rows):
    ax.text(i + w / 2, b + 0.8, f"+{b - a:.1f}", ha="center", color="#e8edf2", fontsize=13)
ax.set_xticks(x, [r[0] for r in rows])
ax.set_ylabel("score (paper Table 1)")
ax.set_ylim(0, 85)
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
ax.set_title("Same total and activated parameters: MoE-27B vs Engram-27B", loc="left", fontsize=15)
fig.tight_layout(); fig.savefig(out / "paper-gains.png", dpi=150)
print(out / "paper-gains.png")
