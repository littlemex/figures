"""gen_dcp_gifs.py — DCP の記事の GIF 3 本。

    OUT_DIR=<出力先> /usr/bin/python3 gen_dcp_gifs.py

1. ffn-tp-ep.gif: Dense の FFN を TP で分ける場合と、MoE の FFN を EP で分ける場合を並べる
2. dcp-decode.gif: DCP の decode の 1 ステップ。Q を集め、各 GPU が自分の KV で attention を計算し、
   LSE で部分の結果をまとめ、新しい token の KV を次の GPU に足す
3. afd-layers.gif: P/D で KV を 1 回だけ渡し、decode では AFD で層ごとに activation を往復させる
図の文字は英語。色: 緑 = 重み、青 = token と KV、黄 = expert。
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/Users/akazawt/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates")
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, R, ease, lerp, mix  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OW, OH = 960, 540
FPS = 12
GRN = (36, 160, 70)
GRN_DK = (18, 64, 34)
BLU = (40, 150, 240)
BLU_DK = (16, 44, 72)
YEL = (251, 211, 50)
YEL_DK = (80, 66, 14)
CHIP = (22, 26, 30)
EDGE = (70, 74, 80)
TOK = [(65, 179, 255), (255, 120, 160), (80, 225, 200)]


def canvas():
    img = Image.new("RGB", (int(OW * R), int(OH * R)), BG)
    return img, ImageDraw.Draw(img)


def P(x, y):
    return (x * R, y * R)


def rbox(g, x, y, w, h, fill, outline, width=2, radius=10):
    g.rounded_rectangle([*P(x, y), *P(x + w, y + h)], radius=radius * R, fill=fill,
                        outline=outline, width=int(width * R))


def text(g, x, y, t, size=18, col=TX, anchor="mm"):
    g.text(P(x, y), t, font=s.font(size), fill=col, anchor=anchor)


def dot(g, x, y, col, r=9, ring=None, tag=None):
    g.ellipse([*P(x - r, y - r), *P(x + r, y + r)], fill=col, outline=ring or BG, width=int(2 * R))
    if tag is not None:
        text(g, x, y, str(tag), max(9, int(r * 1.1)), BG)


def caption(g, head, sub):
    text(g, 32, 34, head, 26, TX, "lm")
    text(g, 32, 68, sub, 17, MUTED, "lm")


def clamp(u):
    return max(0.0, min(1.0, u))


def save(frames, name, stills):
    pal = frames[len(frames) // 2].convert("P", palette=Image.ADAPTIVE, colors=64)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(OUT_DIR, name)
    out[0].save(path, save_all=True, append_images=out[1:], duration=int(1000 / FPS), loop=0,
                optimize=True)
    for i, k in enumerate(stills):
        frames[k].save(os.path.join(OUT_DIR, f"{name[:-4]}-still{i}.png"))
    print("wrote", path, len(frames), "frames", round(os.path.getsize(path) / 1e6, 2), "MB")


# ---------------------------------------------------------------- 1. FFN: TP vs EP
def ffn_frame(t):
    img, g = canvas()
    if t < 1.2:
        head, sub = "Splitting the FFN", "tokens 0, 1, 2 enter"
    elif t < 3.4:
        head, sub = "Send tokens", "TP: all tokens to all.  EP: one expert each"
    elif t < 4.8:
        head, sub = "Compute", "TP: a slice per GPU.  EP: tokens per expert"
    elif t < 7.0:
        head, sub = "Combine", "TP: all-reduce.  EP: all-to-all back"
    else:
        head, sub = "Done", "Same FFN layer, two different splits"
    caption(g, head, sub)
    for side, (x0, title) in enumerate([(24, "Dense FFN, TP = 4"), (496, "MoE FFN, EP = 4")]):
        text(g, x0 + 220, 112, title, 19, TX)
        busy = 1.0 if 3.4 <= t < 4.8 else 0.0
        for i in range(4):
            x = x0 + i * 112
            col = GRN if side == 0 else YEL
            dk = GRN_DK if side == 0 else YEL_DK
            rbox(g, x, 250, 100, 120, mix(CHIP, dk, 0.4 + 0.6 * busy), col)
            text(g, x + 50, 268, f"GPU {i}", 14, MUTED)
            text(g, x + 50, 350, f"W slice {i}" if side == 0 else f"expert {i}", 14, col)
        if side == 1:
            rbox(g, x0 + 150, 160, 140, 44, BLU_DK, BLU)
            text(g, x0 + 220, 182, "router", 16, BLU)
        # tokens
        dest = [1, 3, 0]
        for k in range(3):
            hx, hy = x0 + 180 + k * 40, 150 if side == 0 else 140
            if side == 1:
                hx, hy = x0 + 140 + k * 80, 228
            col = TOK[k]
            if t < 1.2:
                dot(g, hx, hy, col, tag=k)
                continue
            if side == 0:
                for i in range(4):
                    tx, ty = x0 + i * 112 + 24 + k * 26, 305
                    if t < 3.4:
                        u = ease(clamp((t - 1.2 - 0.1 * k) / 1.6))
                        dot(g, lerp(hx, tx, u), lerp(hy, ty, u), col, 9, tag=k)
                    elif t < 4.8:
                        dot(g, tx, ty, col, 9 + 1.5 * math.sin((t - 3.4) * 7), tag=k)
                    elif t < 7.0:
                        u = ease(clamp((t - 4.8) / 1.6))
                        ox, oy = x0 + 180 + k * 40, 430
                        dot(g, lerp(tx, ox, u), lerp(ty, oy, u), col, 9, tag=k)
                    else:
                        dot(g, x0 + 180 + k * 40, 430, col, 11, ring=TX, tag=k)
            else:
                i = dest[k]
                tx, ty = x0 + i * 112 + 50, 305
                if t < 3.4:
                    u = ease(clamp((t - 1.2 - 0.15 * k) / 1.6))
                    dot(g, lerp(hx, tx, u), lerp(hy, ty, u) - math.sin(math.pi * u) * 30, col, tag=k)
                elif t < 4.8:
                    dot(g, tx, ty, col, 9 + 2 * math.sin((t - 3.4) * 7), tag=k)
                elif t < 7.0:
                    u = ease(clamp((t - 4.8 - 0.15 * k) / 1.6))
                    ox, oy = x0 + 140 + k * 80, 430
                    dot(g, lerp(tx, ox, u), lerp(ty, oy, u), col, tag=k)
                else:
                    dot(g, x0 + 140 + k * 80, 430, col, 11, ring=TX, tag=k)
        if t >= 4.8:
            label = "all-reduce" if side == 0 else "all-to-all"
            rbox(g, x0 + 150, 456, 140, 40, CHIP, BLU)
            text(g, x0 + 220, 476, label, 16, BLU)
    return img.resize((OW, OH), Image.LANCZOS)


frames = [ffn_frame(i / FPS) for i in range(int(9.0 * FPS))]
save(frames, "ffn-tp-ep.gif", [6, 30, 48, 70, 100])


# ---------------------------------------------------------------- 2. DCP decode step
N_TOK = 12


def kv_pos(tok):
    g_ = tok % 4
    slot = tok // 4
    return 60 + g_ * 220 + 30 + slot * 40, 250


def dcp_frame(t):
    img, g = canvas()
    phases = [(1.4, "New token", "q: the new token's query"),
              (3.0, "1. All-gather q", "full q on every GPU"),
              (5.2, "2. Attend to local KV", "q against local KV only"),
              (7.6, "3. Merge with LSE", "rescale by LSE, then add"),
              (9.6, "4. Store the new KV", "Token 12 goes to GPU 12 mod 4 = 0"),
              (11.0, "Next step", "about 1/4 of the tokens per GPU")]
    head, sub = phases[-1][1:]
    for end, h, sb in phases:
        if t < end:
            head, sub = h, sb
            break
    caption(g, head, sub)
    for i in range(4):
        x = 60 + i * 220
        rbox(g, x, 150, 200, 220, CHIP, EDGE)
        text(g, x + 100, 170, f"GPU {i}", 16, MUTED)
        text(g, x + 100, 210, "KV of tokens", 13, MUTED)
    # KV squares
    show_new = t >= 7.6
    for tok in range(N_TOK + (1 if show_new else 0)):
        x, y = kv_pos(tok)
        if tok == N_TOK:
            u = ease(clamp((t - 7.8) / 1.4))
            sx, sy = lerp(480, x, u), lerp(110, y, u)
        else:
            sx, sy = x, y
        lit = 3.0 <= t < 5.2
        fill = mix(BLU_DK, BLU, 0.7 if lit else 0.0)
        g.rectangle([*P(sx - 14, sy - 14), *P(sx + 14, sy + 14)], fill=fill, outline=BLU, width=int(2 * R))
        text(g, sx, sy, str(tok), 12, TX)
    # query
    if t < 1.4:
        dot(g, 480, 110, YEL, 12)
        text(g, 480, 110, "q", 13, BG)
    elif t < 3.0:
        u = ease(clamp((t - 1.4) / 1.3))
        for i in range(4):
            qx = lerp(480, 60 + i * 220 + 170, u)
            qy = lerp(110, 180, u)
            dot(g, qx, qy, YEL, 11, tag='q')
    elif t < 5.2:
        for i in range(4):
            dot(g, 60 + i * 220 + 170, 180, YEL, 11, tag='q')
    # partials
    if 3.6 <= t < 7.6:
        for i in range(4):
            x = 60 + i * 220
            if t < 5.2:
                a = clamp((t - 3.6) / 0.8)
                rbox(g, x + 30, 318, 140, 40, mix(CHIP, GRN_DK, a), GRN)
                text(g, x + 100, 338, f"o{i}, lse{i}", 15, mix(CHIP, TX, a))
            else:
                u = ease(clamp((t - 5.2) / 1.6))
                cx, cy = lerp(x + 100, 480, u), lerp(338, 440, u)
                rbox(g, cx - 70, cy - 20, 140, 40, GRN_DK, GRN)
                text(g, cx, cy, f"o{i}, lse{i}", 15, TX)
    if t >= 6.6:
        rbox(g, 330, 420, 300, 50, GRN_DK, GRN, width=3)
        text(g, 480, 445, "o = sum of rescaled o_i", 17, TX)
    text(g, 480, 510, "token i on GPU i mod 4", 15, MUTED)
    return img.resize((OW, OH), Image.LANCZOS)


frames = [dcp_frame(i / FPS) for i in range(int(11.0 * FPS))]
save(frames, "dcp-decode.gif", [8, 26, 50, 80, 110, 128])


# ---------------------------------------------------------------- 3. P/D then AFD per layer
def afd_frame(t):
    img, g = canvas()
    if t < 2.4:
        head, sub = "P/D: hand over the KV once", "prefill KV goes to decode"
    else:
        head, sub = "AFD: back and forth per layer", "attention, then experts, every layer"
    caption(g, head, sub)
    rbox(g, 30, 140, 230, 300, CHIP, GRN)
    text(g, 145, 165, "Prefill pool", 17, GRN)
    text(g, 145, 285, "attention", 16, TX)
    text(g, 145, 315, "+ FFN", 16, TX)
    rbox(g, 330, 140, 270, 300, CHIP, BLU)
    text(g, 465, 165, "attention pool", 17, BLU)
    rbox(g, 660, 140, 270, 300, CHIP, YEL)
    text(g, 795, 165, "FFN pool (experts)", 17, YEL)
    g.line([*P(330, 128), *P(930, 128)], fill=MUTED, width=int(2 * R))
    text(g, 630, 116, "decode", 15, MUTED)
    # KV block
    u = ease(clamp((t - 0.5) / 1.6))
    kx = lerp(145, 465, u)
    g.rectangle([*P(kx - 50, 360), *P(kx + 50, 400)], fill=BLU_DK, outline=BLU, width=int(2 * R))
    text(g, kx, 380, "KV", 15, TX)
    if t >= 2.4:
        layer_t = (t - 2.4) / 1.6
        layer = min(4, int(layer_t) + 1)
        f = layer_t - int(layer_t) if layer_t < 4 else 1.0
        if f < 0.5:
            u = ease(f / 0.5)
            x, y = lerp(465, 795, u), 270 - math.sin(math.pi * u) * 40
        else:
            u = ease((f - 0.5) / 0.5)
            x, y = lerp(795, 465, u), 300 + math.sin(math.pi * u) * 40
        dot(g, x, y, TOK[0], 16)
        text(g, 480, 480, f"layer {layer} of 4 (example)", 18, TX)
        text(g, x, y, "act", 11, BG)
    return img.resize((OW, OH), Image.LANCZOS)


frames = [afd_frame(i / FPS) for i in range(int(9.2 * FPS))]
save(frames, "afd-layers.gif", [10, 40, 70])
