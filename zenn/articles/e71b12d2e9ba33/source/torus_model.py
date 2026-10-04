"""Uniform all-to-all on a k x k 2D torus (dimension-order, shortest path, ties split) vs a
non-blocking switch, with the same total injection bandwidth per chip."""
import itertools, collections
def ring_moves(a, b, k):
    d = (b - a) % k
    if d == 0: return [[]]
    if d < k - d: return [[+1] * d]
    if d > k - d: return [[-1] * (k - d)]
    return [[+1] * d, [-1] * d]          # tie: half the traffic each way
def torus(k):
    load = collections.Counter(); hops = 0; n = k * k
    for (sx, sy), (dx, dy) in itertools.product(itertools.product(range(k), repeat=2), repeat=2):
        if (sx, sy) == (dx, dy): continue
        xs, ys = ring_moves(sx, dx, k), ring_moves(sy, dy, k)
        w = 1 / (len(xs) * len(ys))
        for mx in xs:
            for my in ys:
                x, y = sx, sy
                for m in mx:
                    load[('x', x, y, m)] += w; x = (x + m) % k
                for m in my:
                    load[('y', x, y, m)] += w; y = (y + m) % k
                hops += w * (len(mx) + len(my))
    links_per_chip = 4
    # each chip injects at total rate 1 split across its 4 links -> each link 1/4
    t_torus = max(load.values()) / (1 / links_per_chip)
    t_switch = n - 1                      # each chip sends n-1 units through one port of rate 1
    return dict(chips=n, avg_hops=hops / (n * (n - 1)), max_link=max(load.values()),
                t_torus=t_torus, t_switch=t_switch, ratio=t_torus / t_switch)
for k in (4,):
    print(torus(k))
