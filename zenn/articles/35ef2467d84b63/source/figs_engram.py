"""Figures of the Engram hands-on article (35ef2467d84b63) as html-embed blocks.

engram_walk  stepper: the seven steps of one Engram layer at " Riding" of " The girl was called Little Red Riding"
hood_chart   chart:   P(" Hood") after each block for the three variants

Values come from the trace recorded with the published seed-1337 models (redhood.json, written by
zenmai-lab 7d12d41 engram_lm/record_trace.py) and from engram_lm/engram.py at the same commit.
Still rules are one selector per line: core.snippet prefixes each line with the Stop condition.
"""
import json
import os

from core import t, bar, radios, frame_inputs, info_panel, select_css, snippet

TRACE = json.load(open(os.environ.get("TRACE", os.path.expanduser("~/tmp/engram/ex/redhood.json"))))
POS = 6  # " Riding", followed by " Hood"
assert TRACE["tokens"][POS]["text"] == " Riding" and TRACE["tokens"][POS + 1]["text"] == " Hood"


def SRCS(f):
    path, _, note = f.partition(" ")
    if path.endswith(".py"):
        return f'<span class="src">github.com/littlemex/zenmai-lab/blob/7d12d41/experiments/2026-10-21-engram-nanogpt/{path} {note}</span>'
    return f'<span class="src">{f}</span>'


def _rows():
    cols = TRACE["layers"][0]["columns"]
    return [r - c["offset"] for r, c in zip(TRACE["hash_rows"][POS][0], cols)]


def engram_walk(skin="zenn-dark"):
    toks = TRACE["tokens"][POS - 2:POS + 1]
    gate = TRACE["gates"][POS][0][0]
    rows = _rows()
    chip = lambda s, cls="": f'<span class="ch {cls}">{s}</span>'
    tag = lambda x: f'<span class="tg">{x}</span>'
    sp = lambda x: "␣" + x[1:] if x.startswith(" ") else x
    cid = TRACE["tokens"][POS]["compressed_id"]
    steps = [
        ("r3", t("compress", "番号をそろえる"), f"{cid:,}",
         "".join(chip(f'{sp(x["text"])}<small>{x["id"]} → {x["compressed_id"]}</small>') for x in toks),
         t("<b>1. Compress the token ids.</b> Tokens that differ only in case, a leading space (␣) or similar normalisation share one id: \"␣Riding\" (36032) and \"␣riding\" (10311) both become 7,780. The id is used only to pick rows; the GPT still reads the 50,257 GPT-2 tokens.",
           "<b>1. 番号をそろえる。</b>大文字と小文字、前の空白 (␣) などだけが違うトークンを 1 つの番号にまとめます。「␣Riding」(36032) と「␣riding」(10311) は、どちらも 7,780 になります。この番号は行を選ぶためだけに使い、GPT 本体は GPT-2 の 50,257 個のトークンのまま読みます。") + SRCS("engram_lm/tokenizer.py")),
        ("r3", "n-gram", "2 + 3",
         '<span class="nw">' + tag("2-gram") + chip("Red Riding", "w2") + '</span><span class="nw">' + tag("3-gram") + chip("Little Red Riding", "w3") + "</span>",
         t("<b>2. Take the n-grams that end here.</b> An n-gram is n tokens in a row. This model uses the 2-gram and the 3-gram ending at the current position, never the next token. At the start of a window, missing earlier tokens are filled with the compressed id of <|endoftext|>.",
           "<b>2. ここで終わる n-gram を取る。</b>n-gram は、続けて並んだ n 個のトークンです。このモデルは、現在地で終わる 2-gram と 3-gram を使い、次のトークンは使いません。窓の先頭で前のトークンが足りないときは、文章の終わりを表す <|endoftext|> の、そろえた後の番号で埋めます。") + SRCS("engram_lm/engram.py (NgramHash)")),
        ("r3", t("hash", "ハッシュ"), "8 + 8",
         '<span class="rs">' + tag("2-gram") + "".join(chip(f"{r:,}", "rw w2") for r in rows[:8]) + "</span>"
         + '<span class="rs">' + tag("3-gram") + "".join(chip(f"{r:,}", "rw w3") for r in rows[8:]) + "</span>",
         t("<b>3. Hash each n-gram to 8 rows.</b> Each n-gram becomes one large number by a fixed calculation. The remainders after dividing it by 8 different primes pick 8 rows, one in each of 8 ranges (one head per range): 8 + 8 = 16 row ids, counted within each range.",
           "<b>3. 各 n-gram を 8 行にハッシュする。</b>決まった計算で n-gram を 1 つの大きな数にし、8 個の違う素数で割った余りで、8 個の範囲から 1 行ずつ選びます (範囲ごとに 1 つのヘッド)。8 + 8 = 16 行で、数字は範囲の中での行番号です。") + SRCS("engram_lm/engram.py (NgramHash)")),
        ("r1", t("read rows", "行を読む"), "1,024",
         '<span class="et">' + "".join('<i></i>' for _ in range(16)) + '</span>' + chip("16 × 64 = 1,024 → e_t"),
         t("<b>4. Read the 16 rows and join them.</b> In this model the table has 1,049,422 rows of 64 numbers; the rows start random and are learned with the rest of the model. Joined, the 16 rows make e_t, a vector of 1,024 numbers.",
           "<b>4. 16 行を読んでつなぐ。</b>この記事のモデルの表は 1,049,422 行で、1 行は 64 個の数です。行の値は最初は乱数で、モデルのほかの重みと一緒に学習します。16 行をつなぐと、1,024 個の数のベクトル e_t になります。") + SRCS("engram_lm/engram.py (Engram)")),
        ("r1", "key, value", "512 + 512",
         chip("e_t (1,024)") + '<span class="arw">→</span>' + chip("key 512", "kv") + chip("value 512", "kv kv2"),
         t("<b>5. Make a key and a value.</b> Learned weights turn e_t into two vectors of 512 numbers, the size of the hidden state. The key is compared with the context; the value is what gets added.",
           "<b>5. key と value を作る。</b>学習した重みで、e_t から隠れ状態と同じ 512 個の数のベクトルを 2 本作ります。key は今の文脈と比べるため、value は足す中身です。") + SRCS("engram_lm/engram.py (Engram.forward)")),
        ("r1", t("gate", "ゲート"), f"α {gate:.2f}",
         chip(t("h after block 0", "ブロック 0 の後の h"), "bk") + chip("key", "kv") + '<span class="arw">→</span>' + chip(t("score", "点数"))
         + '<span class="arw">→</span>' + f'<span class="gauge"><i style="width:{gate*100:.0f}%"></i></span>' + chip(f"α = {gate:.2f}"),
         t(f"<b>6. Decide how much to add.</b> The normalised hidden state after block 0 and the normalised key are compared with learned weights into a score; a signed square root and a sigmoid turn it into a gate α between 0 and 1. Here α = {gate:.2f}. The gate scales the whole value, not single rows.",
           f"<b>6. 足す量を決める。</b>大きさをそろえたブロック 0 の後の隠れ状態と key を、学習した重みで比べて点数にし、符号付きの平方根とシグモイドで 0〜1 のゲート α にします。ここでは α = {gate:.2f} です。ゲートは value 全体の量を決め、1 行ずつは見分けません。") + SRCS("engram_lm/engram.py (Engram.forward)")),
        ("r1", t("add", "足す"), t("→ block 1", "→ ブロック 1"),
         chip("h", "bk") + '<span class="arw">+</span>' + chip(f"{gate:.2f} × value", "kv kv2") + '<span class="arw">→</span>' + chip(t("block 1", "ブロック 1"), "bk"),
         t("<b>7. Add to the hidden state.</b> h + α · value goes on to block 1, the second block of the 12-block GPT.",
           "<b>7. 隠れ状態に足す。</b>h + α · value が、12 ブロックの GPT の 2 番目のブロック 1 に渡ります。") + SRCS("engram_lm/model.py (GPT.forward)")),
    ]
    n = len(steps)
    keys = [str(i) for i in range(1, n + 1)]
    inputs = frame_inputs(radios("st", keys))
    strip = "".join(f'<label for="st-{i}" class="box hot {r} sp b{i}"><span class="no">{i}</span><span class="nm">{nm}</span><span class="sub">{val}</span></label>'
                    for i, (r, nm, val, _, _) in enumerate(steps, 1))
    stage = "".join(f'<div class="dt d{i}"><span class="dn">{i}</span>{vis}</div>' for i, (_, _, _, vis, _) in enumerate(steps, 1))
    caps = "".join(f'<div class="cap k{i}">{cap}</div>' for i, (*_, cap) in enumerate(steps, 1))

    def nav(i):
        return (f'<div class="nav n{i}">' + (f'<label class="pill" for="st-{i-1}">&#9664; {t("back", "戻る")}</label>' if i > 1 else "<span></span>")
                + f'<span class="hint">{i} / {n}</span>'
                + (f'<label class="pill" for="st-{i+1}">{t("next", "次へ")} &#9654;</label>' if i < n else f'<label class="pill" for="st-1">&#8634; {t("again", "最初から")}</label>')
                + "</div>")
    legend = ('<div class="legend">' + t("seed 1337 · ", "seed 1337 ・ ") + '<span class="sw r3"></span>' + t("from token ids only", "トークンの番号だけで決まる")
              + ' &nbsp; <span class="sw r1"></span>' + t("Engram (learned)", "Engram (学習する)")
              + ' &nbsp; <span class="sw bk"></span>' + t("GPT backbone", "GPT 本体")
              + ' &nbsp; ' + t("chips: dashed = 2-gram, double = 3-gram or value", "枠: 破線 = 2-gram、二重線 = 3-gram か value") + "</div>")
    body = (inputs + '<div class="zr">' + bar("Engram, step by step", "Engram を 1 歩ずつ")
            + f'<div class="strip">{strip}</div><div class="stage">{stage}</div>{legend}'
            + f'<div class="info">{caps}{"".join(nav(i) for i in range(1, n + 1))}</div></div>')
    rules = []
    for i in range(1, n + 1):
        rules.append(f"#st-{i}:checked~.zr .d{i}{{display:flex}}#st-{i}:checked~.zr .k{i}{{display:block}}#st-{i}:checked~.zr .n{i}{{display:flex}}")
        rules.append(f"#st-{i}:checked~.zr .b{i}{{box-shadow:0 0 0 3px var(--fg);opacity:1}}")
        done = ",".join(f"#st-{i}:checked~.zr .b{j}" for j in range(1, i))
        if done:
            rules.append(done + "{opacity:1}")
    css = """
.strip{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}
.sp{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:16px 2px 6px;min-height:70px;opacity:.7}
.sp .nm{font-size:12px;line-height:1.2}.sp .sub{font-size:11px;margin-top:2px}
.no{position:absolute;top:3px;left:5px;font-size:11px;font-weight:700;background:#000;border-radius:50%;width:16px;height:16px;line-height:16px;text-align:center}
.stage{height:112px;border:1px solid var(--line);border-radius:10px;margin-top:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px}
.dt{display:none;flex-wrap:wrap;gap:6px;align-items:center;justify-content:center}
.ch{display:inline-flex;flex-direction:column;align-items:center;border:2px solid var(--fg);border-radius:8px;padding:3px 9px;font-weight:700;background:#000;opacity:0;animation:in .5s ease forwards}
.ch small{font-weight:400;font-size:11px;color:var(--mut)}
.ch.w2{border-style:dashed}.ch.w3{border-style:double;border-width:4px}
.ch.kv{border-color:var(--p1)}.ch.kv2{border-style:double;border-width:4px}
.ch.bk{border-color:var(--p2);background:var(--p2-bg)}
.ch.rw{font-size:11px;padding:1px 5px;border-width:1px}.ch.rw.w3{border-width:3px}
.tg{font-size:11px;color:var(--mut);margin-right:2px}.nw{white-space:nowrap;display:inline-flex;align-items:center;gap:4px}
.rs{display:flex;flex-wrap:wrap;gap:3px;align-items:center;justify-content:center;width:100%}
.dn{display:none;font-weight:700;font-size:11px;width:16px;height:16px;line-height:16px;text-align:center;border-radius:50%;background:var(--fg);color:#000}
.dt .ch:nth-child(2){animation-delay:.25s}.dt .ch:nth-child(3){animation-delay:.5s}.dt .ch:nth-child(4){animation-delay:.75s}
.dt .ch:nth-child(5){animation-delay:1s}.dt .ch:nth-child(n+6){animation-delay:1.25s}
@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.arw{font-size:18px;font-weight:700}
.et{display:flex;gap:2px}.et i{width:12px;height:30px;background:var(--p1-bg);border:1px solid var(--p1)}
.gauge{display:inline-block;width:90px;height:14px;border:1px solid var(--fg);border-radius:7px;overflow:hidden}
.gauge i{display:block;height:100%;background:var(--p1);animation:fill 1s ease}
@keyframes fill{from{width:0}}
.sw{display:inline-block;width:18px;height:11px;vertical-align:middle;border:1px solid var(--fg)}
.sw.r3{background:var(--p3-bg);border-color:var(--p3);border-style:dashed}.sw.r1{background:var(--p1-bg);border-color:var(--p1)}.sw.bk{background:var(--p2-bg);border-color:var(--p2)}
.cap,.nav{display:none}.cap{margin-bottom:6px}.cap .src{display:block}.nav{justify-content:space-between;align-items:center}
@media (max-width:520px){.strip{gap:2px}.sp{min-height:42px;padding:14px 0 3px}.sp .nm{font-size:9px}.sp .sub{display:none}.no{width:13px;height:13px;line-height:13px;font-size:9px;top:1px;left:2px}.stage{height:auto;min-height:84px;padding:5px}.info{font-size:12px;padding:6px 9px}.legend{font-size:11px}.ch{font-size:12px;padding:2px 6px}.ch.rw{font-size:10px;padding:0 3px}.dt{gap:3px}}
@media (max-width:520px){#zs:checked~.zr .ch{font-size:10px;padding:0 3px;border-width:1px}#zs:checked~.zr .ch.rw{font-size:9px;padding:0 2px}#zs:checked~.zr .et i{width:7px;height:16px}#zs:checked~.zr .dt{gap:2px}#zs:checked~.zr .stage{gap:2px}#zs:checked~.zr .info{display:none}#zs:checked~.zr .ch.w3,#zs:checked~.zr .ch.kv2{border-width:3px}#zs:checked~.zr .rs{width:100%;min-width:0}}
""" + "\n".join(rules)
    still = """.sp{opacity:1!important;box-shadow:none!important}
.ch{opacity:1!important;transform:none!important;padding:1px 6px;font-size:12px}
.ch small{display:none}
.stage{height:auto!important;align-items:stretch;gap:4px}
.dt{display:flex!important;justify-content:flex-start;gap:4px}
.dn{display:inline-block}
.rs{width:auto}
.gauge i{animation:none}
.info{display:none}"""
    return snippet(body, css, still, skin)


def hood_chart(skin="zenn-dark"):
    vals = TRACE["lens"]["values"]
    series = [("e", "engram"), ("o", "engram_off"), ("b", "baseline")]
    W, H = 600, 150
    X = lambda b: 24 + b * (W - 44) / 11
    Y = lambda p: H - 10 - p * (H - 20)
    paths, marks, fin = "", "", {}
    for k, v in series:
        ps = [blk["p_next"] for blk in vals[v][POS]]
        fin[k] = ps
        paths += f'<path class="ln l{k}" d="M' + " L".join(f"{X(b):.1f} {Y(p):.1f}" for b, p in enumerate(ps)) + '"/>'
        for b, p in enumerate(ps):
            x, y = X(b), Y(p)
            marks += {"e": f'<circle class="mk m{k}" cx="{x:.1f}" cy="{y:.1f}" r="4"/>',
                      "o": f'<path class="mk m{k}" d="M{x:.1f} {y-5:.1f} L{x+5:.1f} {y+4:.1f} L{x-5:.1f} {y+4:.1f} Z"/>',
                      "b": f'<rect class="mk m{k}" x="{x-4:.1f}" y="{y-4:.1f}" width="8" height="8"/>'}[k]
    grid = "".join(f'<path class="gl" d="M24 {Y(p):.1f}H{W-20}"/><text class="ax" x="20" y="{Y(p)+4:.1f}" text-anchor="end">{p:g}</text>' for p in (0, 0.5, 1))
    xt = "".join(f'<text class="ax" x="{X(b):.1f}" y="{H+14}" text-anchor="middle">{b}</text>' for b in range(12))
    keys = ["0", "e", "o", "b", "lens"]
    info = {
        "0": t("Click a label below the chart.", "図の下のラベルを押すと、説明が出ます。"),
        "e": t("<b>With Engram</b>: the model trained together with Engram, read with the lookup added before block 1.",
               "<b>Engram あり</b>: Engram と一緒に学習したモデルを、ブロック 1 の前で表引きを足して読んだものです。") + SRCS("engram_lm/record_trace.py (trace of seed 1337)"),
        "o": t("<b>Lookup skipped (same weights)</b>: the weights of the model with Engram, with the Engram step left out at evaluation only.",
               "<b>表引きを外す (同じ重み)</b>: Engram ありのモデルの重みのまま、評価のときだけ Engram の足し込みを飛ばしたものです。") + SRCS("engram_lm/model.py (engram_off)"),
        "b": t("<b>Trained without Engram</b>: the same backbone trained on the same data in the same order, without Engram.",
               "<b>Engram なしで学習</b>: 同じ本体を、Engram なしで、同じ文章を同じ順番で学習したモデルです。") + SRCS("engram_lm/train.py"),
        "lens": t("<b>LogitLens</b>: passes the hidden state after a block through the final norm and output head to read out a provisional prediction, while all 12 blocks still run.",
                  "<b>LogitLens</b>: ブロックの後の隠れ状態を、最後の正規化と出力の計算に通して、12 ブロックをすべて計算するモデルの途中の仮の予想を読み出します。") + '<span class="src">lesswrong.com/posts/AcKRB8wDpdaN6v6ru (logit lens)</span>',
    }
    lab = lambda k, en, ja, cls: f'<label class="pill hot b-{k} {cls}" for="s-{k}">{t(en, ja)}</label>'
    ax = (X(0) + X(1)) / 2
    body = (frame_inputs(radios("s", keys)) + '<div class="zr">' + bar("P(\"␣Hood\") after each block", "各ブロックの後の「␣Hood」の確率")
            + f'<svg class="plot" viewBox="0 0 {W} {H+20}">{grid}{xt}'
            + f'<path class="add" d="M{ax:.1f} 4V{H-10}"/>'
            + f'{paths}{marks}<rect class="cov" x="26" y="0" width="{W-22}" height="{H}"/>'
            + f'<text class="ax add-t ten" x="{ax+5:.1f}" y="16">Engram added</text><text class="ax add-t tja" x="{ax+5:.1f}" y="16">Engram を足す</text></svg>'
            + '<div class="ctl lg">' + lab("e", "● with Engram", "● Engram あり", "le") + lab("o", "▲ lookup skipped (same weights)", "▲ 表引きを外す (同じ重み)", "lo")
            + lab("b", "■ trained without Engram", "■ Engram なしで学習", "lb") + lab("lens", "LogitLens", "LogitLens", "") + "</div>"
            + f'<div class="hint">{t("Seed 1337, at \"␣Riding\" of \"The girl was called Little Red Riding\". x: block (0 = first) · y: probability of the next token \"␣Hood\" · dashed vertical line: where Engram is added", "seed 1337、「The girl was called Little Red Riding」の「␣Riding」の位置。横: ブロック (0 が最初) ・ 縦: 次のトークン「␣Hood」の確率 ・ 縦の破線: Engram を足す場所")}</div>'
            + info_panel(info) + "</div>")
    css = """
.plot{width:100%;height:auto;display:block}
.gl{stroke:var(--line);stroke-width:1}
.ax{fill:var(--mut);font-size:13px}
#zl-en:checked~.zr .tja{display:none}
#zl-ja:checked~.zr .ten{display:none}
.add{stroke:var(--p3);stroke-width:1.5;stroke-dasharray:4 3}.add-t{fill:var(--p3)}
.ln{fill:none;stroke-width:2.5}
.le,.lo,.lb{font-weight:700}.le{border-color:var(--p1);color:var(--p1)}.lo{border-color:var(--p4);color:var(--p4)}.lb{border-color:var(--p2);color:var(--p2)}
.ln.le{stroke:var(--p1)}.ln.lo{stroke:var(--p4);stroke-dasharray:2 4}.ln.lb{stroke:var(--p2);stroke-dasharray:8 4}
.mk{stroke:#000;stroke-width:1}.mk.me{fill:var(--p1)}.mk.mo{fill:var(--p4)}.mk.mb{fill:var(--p2)}
.cov{fill:#000;transform-box:fill-box;transform-origin:100% 50%;animation:draw 3s ease forwards}
@keyframes draw{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.lg{margin-top:4px}
""" + select_css(keys)
    still = """.cov{transform:scaleX(0)}"""
    return snippet(body, css, still, skin)
