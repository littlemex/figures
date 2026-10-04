"""gen_utterance_gif.py — XTTS v2 の 1 回の音声生成で、ブリッジが prefill、KV の受け渡し、decode をどう回すかの GIF。

    OUT_DIR=<出力先> /usr/bin/python3 gen_utterance_gif.py

1. store_prefix_emb(): prefix (prompt + text) を prefill_app に一括で流し、prefill 側の KV を埋める
2. sync_kv_cache_prefill_to_decode(): prefill 側の KV を decode 側へ写し、padding をゼロにする
3. generate() のループ: 1 ステップごとに 1 トークンを decode_app に流し、decode 側の KV が 1 つ伸びる。
   Hugging Face にはダミーの past_key_values を返す
4. EOS で止まり、次の発話の前に状態を戻す
図の文字は英語。根拠は littlemex/samples の neuron_xttsv2.py / application_gpt.py (commit b6334ca)。
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.expanduser(
    "~/works/data-science/claudecode/.claude/skills/review-html/packs/zenn-doc/templates"))
import stack3d as s  # noqa: E402
from stack3d import BG, TX, MUTED, mix, ease  # noqa: E402

OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "out"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "xtts-utterance-flow.gif")
SC = 4 / 3
FPS = 12
GRN = (36, 160, 70)
GRN_HI = (59, 209, 111)
LINK = (40, 150, 240)
LINK_DK = (16, 44, 72)
YEL = (251, 211, 50)
DIM = (46, 50, 56)
CHIP = (22, 26, 30)
GREY = (52, 56, 64)

MAXSEQ = 1081
PREFIX = 380        # illustrative prefix length (prompt + text)
AUDIO = 300         # illustrative number of generated audio tokens shown

# layout (logical 960 x 540)
HF = (60, 150, 230, 60)        # x, y, w, h
BR = (60, 280, 230, 80)
PA = (350, 150, 200, 56)
DA = (350, 330, 200, 56)
BX, BW, BH = 590, 330, 26      # KV bars
PY, DY = 165, 345


def P(x, y):
    return (x * SC, y * SC)


def rbox(g, r, fill, outline, text=None, size=16, col=TX):
    x, y, w, h = r
    g.rounded_rectangle([P(x, y), P(x + w, y + h)], radius=8 * SC, fill=fill, outline=outline,
                        width=int(2 * SC))
    if text:
        g.text(P(x + w / 2, y + h / 2), text, font=s.font(size), fill=col, anchor="mm")


def bar(g, y, filled, color, zeroed=0):
    g.rectangle([P(BX, y), P(BX + BW, y + BH)], fill=CHIP, outline=DIM, width=int(1.5 * SC))
    if filled:
        g.rectangle([P(BX, y), P(BX + BW * filled / MAXSEQ, y + BH)], fill=color)
    if zeroed:
        x0 = BX + BW * PREFIX / MAXSEQ
        g.rectangle([P(x0, y), P(BX + BW, y + BH)], fill=(30, 30, 34))


def base(phase, sub):
    img = Image.new("RGB", (int(960 * SC), int(540 * SC)), BG)
    g = ImageDraw.Draw(img)
    g.text(P(40, 40), "One utterance through the bridge", font=s.font(26), fill=TX, anchor="lm")
    g.text(P(40, 84), f"{phase}  {sub}", font=s.font(15), fill=MUTED, anchor="lm")
    rbox(g, HF, CHIP, DIM, "HF generate()", 16)
    rbox(g, BR, LINK_DK, LINK, "Bridge", 18)
    rbox(g, PA, (18, 64, 34), GRN, "prefill_app", 16)
    rbox(g, DA, (18, 64, 34), GRN, "decode_app", 16)
    g.text(P(BX, PY - 14), "prefill KV", font=s.font(13), fill=MUTED, anchor="lm")
    g.text(P(BX, DY - 14), "decode KV", font=s.font(13), fill=MUTED, anchor="lm")
    g.text(P(BX + BW, PY + BH + 12), f"{MAXSEQ} slots", font=s.font(12), fill=MUTED, anchor="rm")
    return img, g


def dot(g, a, b, t, col):
    x = a[0] + (b[0] - a[0]) * t
    y = a[1] + (b[1] - a[1]) * t
    g.ellipse([P(x - 7, y - 7), P(x + 7, y + 7)], fill=col, outline=BG, width=int(2 * SC))


frames = []
# 1. prefill
for f in range(36):
    u = ease(f / 35)
    img, g = base("1.", "store_prefix_emb(): prefix in one shot")
    bar(g, PY, PREFIX * max(0.0, (u - 0.5) * 2), GRN_HI)
    bar(g, DY, 0, YEL)
    if u < 0.5:
        dot(g, (BR[0] + BR[2], BR[1] + 20), (PA[0], PA[1] + 28), u * 2, GRN_HI)
    frames.append(img)
for _ in range(8):
    frames.append(frames[-1])
# 2. copy KV to decode side and zero the padding
for f in range(30):
    u = ease(f / 29)
    img, g = base("2.", "copy prefill KV to decode KV via CPU, zero the padding")
    bar(g, PY, PREFIX, GRN_HI)
    bar(g, DY, PREFIX * u, GRN_HI, zeroed=1 if u > 0.95 else 0)
    dot(g, (BX + BW * PREFIX / MAXSEQ / 2, PY + BH), (BX + BW * PREFIX / MAXSEQ / 2, DY), u, GRN_HI)
    frames.append(img)
for _ in range(8):
    frames.append(frames[-1])
# 3. decode loop: one token per step
steps = AUDIO
ks = list(range(4)) + list(range(4, steps, 6))
for k in ks:
    sub_frames = 6 if k < 4 else 1
    for f in range(sub_frames):
        u = (f + 1) / sub_frames
        img, g = base("3.", f"generate() loop: 1 token per step   (step {k + 1})")
        bar(g, PY, PREFIX, GRN_HI)
        g.rectangle([P(BX, DY), P(BX + BW, DY + BH)], fill=CHIP, outline=DIM, width=int(1.5 * SC))
        g.rectangle([P(BX, DY), P(BX + BW * PREFIX / MAXSEQ, DY + BH)], fill=GRN_HI)
        g.rectangle([P(BX + BW * PREFIX / MAXSEQ, DY),
                     P(BX + BW * (PREFIX + k + u) / MAXSEQ, DY + BH)], fill=YEL)
        if sub_frames > 1:
            if u < 0.34:
                dot(g, (HF[0] + 80, HF[1] + HF[3]), (BR[0] + 80, BR[1]), u * 3, YEL)
            elif u < 0.67:
                dot(g, (BR[0] + BR[2], BR[1] + 60), (DA[0], DA[1] + 28), (u - 0.34) * 3, YEL)
            else:
                dot(g, (BR[0] + 150, BR[1]), (HF[0] + 150, HF[1] + HF[3]), (u - 0.67) * 3, YEL)
        g.text(P(BR[0], BR[1] + BR[3] + 48), "dummy past_key_values to HF",
               font=s.font(12), fill=MUTED, anchor="lm")
        frames.append(img)
# 4. EOS
for f in range(18):
    img, g = base("4.", "EOS: stop, then reset the state for the next utterance")
    bar(g, PY, PREFIX, GRN_HI)
    g.rectangle([P(BX, DY), P(BX + BW, DY + BH)], fill=CHIP, outline=DIM, width=int(1.5 * SC))
    g.rectangle([P(BX, DY), P(BX + BW * PREFIX / MAXSEQ, DY + BH)], fill=GRN_HI)
    g.rectangle([P(BX + BW * PREFIX / MAXSEQ, DY), P(BX + BW * (PREFIX + steps) / MAXSEQ, DY + BH)],
                fill=YEL)
    g.text(P(BX + BW * (PREFIX + steps) / MAXSEQ + 8, DY + BH / 2), "EOS", font=s.font(14), fill=YEL,
           anchor="lm")
    frames.append(img)

pal = [fr.convert("P", palette=Image.ADAPTIVE, colors=64) for fr in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print(OUT, len(frames), os.path.getsize(OUT) // 1024, "KB")
