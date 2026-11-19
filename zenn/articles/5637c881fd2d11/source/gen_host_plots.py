"""gen_host_plots.py: the charts of the Engram host-table article, from the measured JSON.

    /usr/bin/python3 gen_host_plots.py <results_dir> <out_dir>

results_dir holds host-tables-256m-to-8g.json (256 MiB to 8 GiB, the stride test), host-tables-16g.json (16 GiB) and
model-table-bf16.json (the contiguous-copy reference).

ZN-29: every series differs by colour (Okabe-Ito), by marker and line style, and is named by a label next
to it. Way A (the GPU reads each row from host memory) is bluish green with circles and solid lines; way B
(the CPU gathers the rows, then one copy) is sky blue with squares and dashed lines.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
d = json.loads((src / "host-tables-256m-to-8g.json").read_text())
d["fresh"] += json.loads((src / "host-tables-16g.json").read_text())["fresh"]
d["h2d_contiguous_GBps"] = json.loads((src / "model-table-bf16.json").read_text())["h2d_contiguous_GBps"]

plt.rcParams.update({"figure.facecolor": "#000000", "axes.facecolor": "#0b0f14", "axes.edgecolor": "#5a6270",
                     "axes.labelcolor": "#e8edf2", "xtick.color": "#c9d3dc", "ytick.color": "#c9d3dc",
                     "text.color": "#e8edf2", "grid.color": "#2a323c", "font.size": 15,
                     "font.family": ["Amazon Ember", "Helvetica Neue", "DejaVu Sans"]})
A = dict(color="#009E73", marker="o", ls="-", lw=2.6, ms=9)
B = dict(color="#56B4E9", marker="s", ls="--", lw=2.6, ms=9)
REF = "#8a94a0"


def size_label(mib):
    return f"{mib} MiB" if mib < 1024 else f"{mib // 1024} GiB"


# ---------------------------------------------------------------- read speed against table size
fresh = [r for r in d["fresh"] if r["positions"] == 16384]
sizes = sorted({r["table_mib"] for r in fresh})
a = {r["table_mib"]: r["GBps"] for r in fresh if r["memory"] == "cudaHostAlloc"}
b = {r["table_mib"]: r["GBps"] for r in fresh if r["memory"] == "cpu_gather"}
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.plot(range(len(sizes)), [a[s] for s in sizes], **A)
ax.plot(range(len(sizes)), [b[s] for s in sizes], **B)
h2d = d.get("h2d_contiguous_GBps", 56.5)
ax.axhline(h2d, color=REF, ls=":", lw=1.6)
ax.text(len(sizes) - 1, h2d + 1.2, f"one large contiguous copy: {h2d:.1f} GB/s", color=REF, fontsize=13, ha="right")
for i, s in enumerate(sizes):
    hi_a = a[s] >= b[s]  # the higher value goes above its point, the lower one below
    ax.text(i, a[s] + 2.0 if hi_a else a[s] - 4.2, f"{a[s]:.1f}", color=A["color"], fontsize=12, ha="center", fontweight="bold")
    ax.text(i, b[s] - 4.2 if hi_a else b[s] + 2.0, f"{b[s]:.1f}", color=B["color"], fontsize=12, ha="center", fontweight="bold")
ax.text(2.25, 36, "A: the GPU reads each row", color=A["color"], fontsize=15, fontweight="bold")
ax.text(3.6, 27.5, "B: the CPU gathers, one copy", color=B["color"], fontsize=15, fontweight="bold")
ax.set_xticks(range(len(sizes)), [size_label(s) for s in sizes])
ax.set_xlabel("table size in host memory (rows spread over all of it)")
ax.set_ylabel("read speed (GB/s)")
ax.set_ylim(0, 64)
ax.grid(alpha=0.3)
fig.suptitle("Reading 16,384 positions x 16 random rows (64 MiB), new rows every call", x=0.01, ha="left",
             fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "host-bandwidth.png", dpi=150)

# ---------------------------------------------------------------- read speed against how far apart the rows are
st = [r for r in d["stride"] if r["memory"] == "register_4k"]
fig, ax = plt.subplots(figsize=(12, 6.0))
xs = list(range(len(st)))
ax.plot(xs, [r["GBps"] for r in st], **A)
for i, r in enumerate(st):
    ax.text(i, r["GBps"] + 2.0, f"{r['GBps']:.1f}", color=A["color"], fontsize=12, ha="center", fontweight="bold")
ax.set_xticks(xs, [f"{r['stride_bytes'] // 1024} KiB\n{size_label(int(r['span_mib']))}" if r["stride_bytes"] >= 1024
                   else f"{r['stride_bytes']} B\n{size_label(int(r['span_mib']))}" for r in st], fontsize=12)
ax.set_xlabel("gap between rows (top) and the range they are spread over (bottom)")
ax.set_ylabel("read speed (GB/s)")
ax.set_ylim(0, 64)
ax.grid(alpha=0.3)
fig.suptitle("Way A, the same 262,144 rows (64 MiB) placed further apart in an 8 GiB table", x=0.01, ha="left",
             fontsize=18, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "host-span.png", dpi=150)
print(out)

# ---------------------------------------------------------------- can the read hide behind block 0?
m0 = json.loads((src / "model-table-bf16.json").read_text())["prefill"]
m16 = json.loads((src / "model-table-bf16-max16blocks.json").read_text())["prefill"]
g0, g16 = m0["forward_us"]["gpu_torch"], m16["forward_us"]["gpu_torch"]
rows = [
    ("embedding + block 0\n(time before the Engram layer)", m0["before_engram_us"], dict(color="#8a94a0", hatch=""), None),
    ("A: reading the rows alone", m0["read_alone_us"]["host_zerocopy"], dict(color=A["color"], hatch="//"), None),
    ("extra forward time vs GPU table:\nA read when needed", m0["forward_us"]["host_zerocopy"] - g0, dict(color=A["color"], hatch="//"), "+{:.1f}%".format((m0["forward_us"]["host_zerocopy"] - g0) / g0 * 100)),
    ("extra: A read ahead on a 2nd stream", m0["forward_us"]["host_zerocopy_prefetch"] - g0, dict(color=A["color"], hatch="xx"), "+{:.1f}%".format((m0["forward_us"]["host_zerocopy_prefetch"] - g0) / g0 * 100)),
    ("extra: A read ahead, 16 thread blocks\n(separate run, its own baseline)", m16["forward_us"]["host_zerocopy_prefetch"] - g16, dict(color=A["color"], hatch=".."), "+{:.1f}%".format((m16["forward_us"]["host_zerocopy_prefetch"] - g16) / g16 * 100)),
]
fig, ax = plt.subplots(figsize=(12, 6.0))
for i, (name, us, st, pct) in enumerate(rows):
    ax.barh(i, us, 0.6, color=st["color"] + "55", edgecolor=st["color"], hatch=st["hatch"], lw=1.8)
    ax.text(us + 8, i, f"{us:.0f} µs" + (f"  ({pct})" if pct else ""), va="center", fontsize=14, fontweight="bold",
            color=st["color"])
ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=13)
ax.invert_yaxis()
ax.set_xlabel("microseconds (prefill of 8 x 512 tokens, bfloat16)")
ax.set_xlim(0, 620)
ax.grid(axis="x", alpha=0.3)
fig.suptitle(f"The read fits in block 0's time, but the forward still slows down (forward {g0 / 1000:.2f} ms)",
             x=0.01, ha="left", fontsize=17, fontweight="bold")
fig.tight_layout()
fig.savefig(out / "host-overlap.png", dpi=150)
