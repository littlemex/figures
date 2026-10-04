"""gen_flow_gif.py — XTTS v2 の 1 回の音声合成で、GPT.generate() が音声コードを 1 つずつ作り、
GPT.forward() がそれをまとめて latents に変え、HifiDecoder が波形にする流れの GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_flow_gif.py

1. generate() (CPU): 1 ステップに 1 つの音声コードを足し、終わりのコードで止まる
2. forward() (Neuron): 全部の音声コードを一度に受け取り、コード 1 つに 1 フレームの latents を返す
3. HifiDecoder (CPU): latents を 24 kHz の波形にする
図の文字は英語。根拠は coqui-ai/TTS (commit eef419b) の xtts.py inference()。
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "xtts-flow.gif")
SC = 4 / 3
FPS = 12
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
GRN_DK = (18, 64, 34)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
DIM = (46, 50, 56)
CHIP = (22, 26, 30)
GREY = (52, 56, 64)
EDGE = (70, 74, 80)

N = 12            # audio codes shown
CX, CW = 300, 40  # code cells


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, x, y, w, h, fill, outline, text=None, size=16, col=TX, width=2):
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(width * SC))
    if text:
        g.text(P(x + w / 2, y + h / 2), text, font=s.font(size), fill=col, anchor="mm")


def frame(phase, k, u):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 40), "One XTTS v2 utterance", font=s.font(26), fill=TX, anchor="lm")
    cap = {0: "1. generate() adds one audio code per step   (CPU)",
           1: "2. forward() turns all codes into latents at once   (Neuron)",
           2: "3. HifiDecoder turns latents into a waveform   (CPU)"}[phase]
    g.text(P(40, 84), cap, font=s.font(15), fill=YEL, anchor="lm")
    # stage boxes
    rbox(g, 40, 140, 220, 70, GREY if phase == 0 else CHIP, YEL if phase == 0 else EDGE, "generate()", 18)
    rbox(g, 40, 260, 220, 70, GRN_DK if phase == 1 else CHIP, GRN_HI if phase == 1 else EDGE,
         "forward()", 18)
    rbox(g, 40, 380, 220, 70, GREY if phase == 2 else CHIP, YEL if phase == 2 else EDGE,
         "HifiDecoder", 18)
    # codes row
    g.text(P(CX, 130), "audio codes", font=s.font(14), fill=MUTED, anchor="lm")
    ncodes = k if phase == 0 else N
    for i in range(N):
        x = CX + i * (CW + 8)
        on = i < ncodes
        new = phase == 0 and i == ncodes - 1
        fill = mix(CHIP, YEL, 0.6 * (1 - u)) if new else (LINK_DK if on else CHIP)
        rbox(g, x, 150, CW, 50, fill, YEL if new else (LINK if on else DIM),
             str(i + 1) if on else None, 13, width=2)
    if phase == 0 and k == N:
        g.text(P(CX + N * (CW + 8) + 6, 175), "EOS", font=s.font(14), fill=YEL, anchor="lm")
    # latents row
    g.text(P(CX, 254), "latents  (1 frame per code, 1024 values)", font=s.font(14), fill=MUTED, anchor="lm")
    lat = 0.0 if phase == 0 else (u if phase == 1 else 1.0)
    for i in range(N):
        x = CX + i * (CW + 8)
        a = lat
        rbox(g, x, 270, CW, 50, mix(CHIP, GRN_DK, a), mix(DIM, GRN_HI, a), None, 13, width=2)
        if a > 0:
            for j in range(5):
                yy = 278 + j * 8
                g.line([P(x + 8, yy), P(x + 8 + (CW - 16) * a * (0.4 + 0.6 * ((i * 7 + j * 3) % 5) / 4), yy)],
                       fill=GRN_HI, width=int(2 * SC))
    if phase == 1:
        for i in range(N):
            x = CX + i * (CW + 8) + CW / 2
            g.line([P(x, 202), P(x, 202 + 34 * min(1, u * 1.5))], fill=GRN_HI, width=int(1 * SC))
    # waveform
    g.text(P(CX, 370), "waveform  (24 kHz)", font=s.font(14), fill=MUTED, anchor="lm")
    wl = 0.0 if phase < 2 else u
    W = N * (CW + 8) - 8
    pts = []
    for p in range(int(W * wl)):
        amp = 28 * (0.35 + 0.65 * abs(math.sin(p / 37.0)))
        pts.append(P(CX + p, 420 + amp * math.sin(p / 3.1)))
    if len(pts) > 1:
        g.line(pts, fill=YEL, width=int(2 * SC))
    g.rectangle([P(CX, 390), P(CX + W, 450)], outline=DIM, width=int(1 * SC))
    return img


frames = []
for k in range(1, N + 1):
    for f in range(4):
        frames.append(frame(0, k, ease(f / 3)))
frames += [frame(0, N, 1.0)] * 6
for f in range(18):
    frames.append(frame(1, N, ease(f / 17)))
frames += [frame(1, N, 1.0)] * 6
for f in range(20):
    frames.append(frame(2, N, ease(f / 19)))
frames += [frame(2, N, 1.0)] * 14
pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB")
