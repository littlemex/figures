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
    lab_y = {"e": Y(0.80), "b": Y(0.68), "o": Y(0.56)}
    names = {"e": "● with Engram, last", "b": "■ trained without Engram, last", "o": "▲ lookup skipped (same weights), last"}
    marks += "".join(f'<text class="ax el e{k}" x="{X(2):.1f}" y="{lab_y[k]:.1f}" text-anchor="start">{names[k]} {fin[k][-1]:.3f}</text>' for k in ("e", "b", "o"))
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
.mk{stroke:#000;stroke-width:1}.el{font-weight:700}.el.ee{fill:var(--p1)}.el.eb{fill:var(--p2)}.el.eo{fill:var(--p4)}.mk.me{fill:var(--p1)}.mk.mo{fill:var(--p4)}.mk.mb{fill:var(--p2)}
.cov{fill:#000;transform-box:fill-box;transform-origin:100% 50%;animation:draw 3s ease forwards}
@keyframes draw{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.lg{margin-top:4px}
""" + select_css(keys)
    still = """.cov{transform:scaleX(0)}"""
    return snippet(body, css, still, skin)


# ---------------------------------------------------------------- the value map (stepper, table fixed in the middle)
_INT = json.load(open(os.path.expanduser("~/tmp/engram/ex/internals.json")))


def engram_map(skin="zenn-dark"):
    D = _INT; P = D["pos"]; toks = D["tokens"]; comp = D["compressed"]; ids = D["ids"]; hs = D["heads"]
    hz = D["hash"]; g = D["gate"]
    f = lambda x: f"{x:,}"
    o = []; add = o.append
    W, H = 760, 400
    x = 4
    for i, tk in enumerate(toks + ["␣Hood ?"]):
        w = 16 + 7.2 * len(tk)
        cls = "tk cur" if i == P else ("tk gh" if i > P else ("tk ng" if i >= P - 2 else "tk"))
        add(f'<g class="{cls}"><rect x="{x:.0f}" y="4" width="{w:.0f}" height="24" rx="5"/><text x="{x + w/2:.0f}" y="21" text-anchor="middle">{tk}</text></g>')
        if i == P: add(f'<text class="yl" x="{x + w/2:.0f}" y="40" text-anchor="middle">current position</text>')
        x += w + 4
    # 1-3 left top
    add('<g class="gx g1"><text class="hd" x="4" y="58">1 compress the ids</text>')
    for k, i in enumerate(range(P - 2, P + 1)):
        add(f'<rect class="id" x="{4 + k*82}" y="64" width="78" height="20" rx="4"/><text class="nm" x="{43 + k*82}" y="78" text-anchor="middle">{ids[i]}→{comp[i]}</text>')
    add('</g><g class="gx g2"><text class="hd" x="4" y="100">2 n-grams</text>')
    add(f'<rect class="id d" x="4" y="106" width="96" height="18" rx="4"/><text class="nm" x="52" y="119" text-anchor="middle">({comp[P-1]}, {comp[P]})</text>')
    add(f'<rect class="id w" x="106" y="106" width="140" height="18" rx="4"/><text class="nm" x="176" y="119" text-anchor="middle">({comp[P-2]}, {comp[P-1]}, {comp[P]})</text></g>')
    add(f'<g class="gx g3"><text class="hd" x="4" y="138">3 × odd, XOR → one number</text><text class="nm" x="4" y="150">2-gram {f(hz["rolling_2gram"])}</text><text class="nm" x="4" y="161">3-gram {f(hz["rolling_3gram"])}</text></g>')
    TY, BH = 186, 13.5
    add(f'<g class="gx g4"><text class="hd" x="4" y="{TY-6}">4 mod a prime = row id</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH
        add(f'<text class="tn" x="4" y="{y+10}">{"2" if h["ngram"]==2 else "3"}-gram ÷{f(h["prime"])} → {f(h["local_row"])}</text><text class="tn b" x="160" y="{y+10}">row {f(h["table_row"])}</text>')
    add('</g>')
    X0, X1 = 262, 318
    add(f'<text class="hd" x="{(X0+X1)/2}" y="{TY-18}" text-anchor="middle">table</text><text class="tn" x="{(X0+X1)/2}" y="{TY-6}" text-anchor="middle">1,049,422 × 64</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH
        add(f'<rect class="bd {"b2" if h["ngram"]==2 else "b3"}" x="{X0}" y="{y}" width="{X1-X0}" height="{BH-1}"/>')
    add('<g class="gx g4 g5">')
    for c, h in enumerate(hs):
        y = TY + c * BH; ty = y + 1.5 + (BH - 4) * h["local_row"] / h["prime"]
        add(f'<line class="pt" x1="248" y1="{y+6.5}" x2="{X0}" y2="{ty:.1f}"/><rect class="tc" x="{X0}" y="{ty-1:.1f}" width="{X1-X0}" height="2.2"/>')
    add('</g>')
    RX, CW = 338, 3
    add(f'<g class="gx g5"><text class="hd" x="{RX+4}" y="{TY-6}">5 read the 16 rows</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH; ty = y + 1.5 + (BH - 4) * h["local_row"] / h["prime"]
        add(f'<line class="pl" x1="{X1}" y1="{ty:.1f}" x2="{RX}" y2="{y+6}"/><rect class="sp {"b2" if h["ngram"]==2 else "b3"}" x="{RX}" y="{y+1.5}" width="{64*CW}" height="{BH-4}"/>')
    add(f'<text class="tn" x="{RX}" y="{TY + 16*BH + 10}">64 numbers per row, read by id</text></g>')
    FX = 548
    add(f'<g class="gx g6"><path class="pl" d="M{RX+192} {TY+100} C {RX+204} {TY+100}, {FX-14} {TY+16}, {FX} {TY+16}" fill="none"/><text class="hd" x="{FX}" y="{TY-6}">6 join</text><rect class="et" x="{FX}" y="{TY+4}" width="208" height="22"/>')
    for c in range(1, 16): add(f'<line class="sep" x1="{FX + c*13:.0f}" y1="{TY+4}" x2="{FX + c*13:.0f}" y2="{TY+26}"/>')
    add(f'<text class="tn" x="{FX}" y="{TY+38}">16 rows × 64 = 1,024 numbers</text></g>')
    add(f'<g class="gx g7"><text class="hd" x="{FX}" y="{TY+60}">7 × W_kv (1,024 × 1,024), split</text><rect class="ky" x="{FX}" y="{TY+66}" width="102" height="22"/><text class="nm" x="{FX+51}" y="{TY+81}" text-anchor="middle">key 512</text><rect class="vl" x="{FX+106}" y="{TY+66}" width="102" height="22"/><text class="nm" x="{FX+157}" y="{TY+81}" text-anchor="middle">value 512</text></g>')
    add(f'<g class="gx g8"><text class="hd" x="{FX}" y="{TY+112}">8 compare h with key, once</text><rect class="hb" x="{FX}" y="{TY+118}" width="70" height="22"/><text class="nm" x="{FX+35}" y="{TY+133}" text-anchor="middle">h</text><text class="nm" x="{FX+76}" y="{TY+133}">·</text><rect class="ky" x="{FX+86}" y="{TY+118}" width="40" height="22"/><text class="nm" x="{FX+106}" y="{TY+133}" text-anchor="middle">key</text><text class="nm" x="{FX+132}" y="{TY+133}">→ gate</text><text class="nm b" x="{FX+176}" y="{TY+133}">{g["gate"]:.3f}</text></g>')
    add(f'<g class="gx g9"><text class="hd" x="{FX}" y="{TY+164}">9 add</text><text class="nm" x="{FX}" y="{TY+184}">h + {g["gate"]:.3f} × value → block 1</text><text class="tn" x="{FX}" y="{TY+200}">h[0]: {D["h_first6"][0]} → {D["h_plus_first6"][0]}</text></g>')
    svg = f'<svg class="mp" viewBox="0 0 {W} {H}">{"".join(o)}</svg>'
    m = D["multipliers"]
    caps = [
     t("<b>The map.</b> The table in the middle has 1,049,422 rows of 64 numbers in 16 ranges: 8 for the 2-gram, 8 for the 3-gram. Its numbers are learned, not counts. Step through with next.",
       "<b>全体。</b>真ん中の柱が表で、1,049,422 行、1 行 64 個の数が 16 の範囲に分かれています。上の 8 範囲を 2-gram、下の 8 範囲を 3-gram が使います。表の中身は回数ではなく、学習で決まる数です。「次へ」で 1 段ずつ進みます。"),
     t(f"<b>1. Compress the ids.</b> Tokens that differ only in case and the like share one id: ␣Riding {ids[P]} becomes {comp[P]}, as ␣riding does. Fixed, not learned.",
       f"<b>1. 番号をそろえる。</b>大文字と小文字などだけが違うトークンを 1 つの番号にまとめます。「␣Riding」の {ids[P]} は {comp[P]} になり、「␣riding」も同じです。決まった対応表で、学習しません。"),
     t(f"<b>2. Take the n-grams.</b> The 2-gram ({comp[P-1]}, {comp[P]}) and the 3-gram ({comp[P-2]}, {comp[P-1]}, {comp[P]}) end at the current position; the next token is not in them.",
       f"<b>2. n-gram を作る。</b>CP で終わる 2-gram は ({comp[P-1]}, {comp[P]})、3-gram は ({comp[P-2]}, {comp[P-1]}, {comp[P]}) です。次の「Hood」は入りません。"),
     t(f"<b>3. One big number each.</b> Each id is multiplied by a fixed odd number for its place and the products are XORed. Order now matters, and n-grams one token apart land far apart. m₀ = {f(m[0])}.",
       f"<b>3. 1 つの大きな数にする。</b>番号に位置ごとの固定の奇数を掛けて、ビットごとに混ぜる XOR で合わせます。順番が区別され、1 語だけ違う並びも遠い数になります。m₀ = {f(m[0])}。"),
     t("<b>4. Remainder = row.</b> Each big number is divided by 8 different primes, one per range; the remainder is the row in that range. Two n-grams can share a row in one range, but they share all 8 only if their big numbers are equal.",
       "<b>4. 余りが行番号。</b>大きな数を範囲ごとに違う 8 個の素数で割り、余りをその範囲の行番号にします。1 つの範囲では別の並びと同じ行になりえますが、8 範囲すべてで同じになるのは、割る前の数が同じときだけです。"),
     t("<b>5. Read the rows.</b> The 16 rows are read by their numbers. Nothing is searched or matched. The row numbers come from the token ids alone, so they are known before any block runs and can be fetched from outside GPU memory.",
       "<b>5. 16 行を読む。</b>番号の行をそのまま読みます。探しも照合もしません。行番号はトークンの番号だけで決まるので、ブロックの計算の前に分かり、GPU の外に置いた表からも先に取ってこられます。"),
     t("<b>6. Join.</b> 16 rows × 64 numbers = 1,024 numbers.", "<b>6. つなぐ。</b>16 行 × 64 個 = 1,024 個の数にします。"),
     t("<b>7. Key and value.</b> The learned matrix W_kv turns the 1,024 numbers into 1,024 new ones; the first 512 are the key, the last 512 the value. Both are computed from the rows, not looked up.",
       "<b>7. key と value。</b>学習した行列 W_kv で 1,024 個を作り直し、前半の 512 個を key、後半の 512 個を value にします。どちらも表から探した値ではなく、読んだ行から計算した値です。"),
     t(f"<b>8. Gate.</b> The hidden state after block 0 and the key are compared once and turned into a number between 0 and 1: {g['gate']:.3f}.",
       f"<b>8. ゲート。</b>ブロック 0 の後の隠れ状態と key を 1 回だけ比べて、0 と 1 の間の数にします。ここでは {g['gate']:.3f} です。"),
     t(f"<b>9. Add.</b> The value times {g['gate']:.3f} is added to the hidden state, which goes on to block 1.",
       f"<b>9. 足す。</b>value を {g['gate']:.3f} 倍して隠れ状態に足し、ブロック 1 に渡します。"),
    ]
    n = len(caps); keys = [str(i) for i in range(n)]
    def nav(i):
        return (f'<div class="nav n{i}">' + (f'<label class="pill" for="st-{i-1}">&#9664; {t("back", "戻る")}</label>' if i > 0 else "<span></span>")
                + f'<span class="hint">{i} / {n-1}</span>'
                + (f'<label class="pill" for="st-{i+1}">{t("next", "次へ")} &#9654;</label>' if i < n - 1 else f'<label class="pill" for="st-0">&#8634; {t("again", "最初から")}</label>') + "</div>")
    body = (frame_inputs(radios("st", keys)) + '<div class="zr">' + bar("One Engram lookup, with the real values", "Engram の表引きを実際の値で追う")
            + svg + '<div class="info">' + "".join(f'<div class="cap k{i}">{c}</div>' for i, c in enumerate(caps)) + "".join(nav(i) for i in range(n)) + "</div></div>")
    rules = []
    for i in range(1, n):
        rules.append(f"#st-{i}:checked~.zr .gx{{opacity:.16}}")
        rules.append(f"#st-{i}:checked~.zr .g{i}{{opacity:1}}")
    for i in range(n):
        rules.append(f"#st-{i}:checked~.zr .k{i}{{display:block}}#st-{i}:checked~.zr .n{i}{{display:flex}}")
    css = """
.mp{width:100%;height:auto;display:block}
.mp text{fill:var(--fg);font-size:11px}.mp .hd{font-weight:700;font-size:11.5px}.mp .nm{font-family:Menlo,Consolas,monospace;font-size:9.5px}
.mp .tn{font-family:Menlo,Consolas,monospace;font-size:8.2px;fill:var(--mut)}.mp .b{fill:var(--p1);font-weight:700}.mp .yl{fill:var(--p3);font-weight:700;font-size:10px}
.tk rect{fill:#1b1e23;stroke:var(--line)}.tk.ng rect{stroke:var(--p3)}.tk.cur rect{fill:var(--p3-bg);stroke:var(--p3);stroke-width:2}.tk.gh rect{fill:#000;stroke:var(--mut);stroke-dasharray:3 3}
.id{fill:var(--p3-bg);stroke:var(--p3)}.id.d{stroke-dasharray:3 2}.id.w{stroke-width:2.5}
.bd{stroke:var(--p1)}.bd.b2{fill:var(--p1-bg)}.bd.b3{fill:#0a2416}
.tc{fill:#ff7a6e}.pt{stroke:var(--p3);stroke-width:.8}.pl{stroke:var(--p1);stroke-width:.8}
.sp{stroke:var(--p1)}.sp.b2{fill:var(--p1-bg)}.sp.b3{fill:#0a2416}
.et{fill:var(--p1-bg);stroke:var(--p1)}.sep{stroke:var(--p1);stroke-width:.6}
.ky{fill:var(--p1-bg);stroke:var(--p1);stroke-width:2}.vl{fill:var(--p1-bg);stroke:var(--p1);stroke-width:2;stroke-dasharray:4 2}.hb{fill:var(--p2-bg);stroke:var(--p2)}
.gx{transition:opacity .3s}
.cap,.nav{display:none}.cap{margin-bottom:6px}.nav{justify-content:space-between;align-items:center}
""" + "\n".join(rules)
    still = """.gx{opacity:1!important}
.info{display:none}"""
    return snippet(body, css, still, skin)
