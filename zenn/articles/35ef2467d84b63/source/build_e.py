import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figs_engram as F
os.makedirs("out", exist_ok=True)
for n in sys.argv[1:] or ["engram_walk", "alex_chart"]:
    h = getattr(F, n)(); open(f"out/{n}.html", "w").write(h); print(n, len(h.encode()), "bytes", len(h), "chars")
