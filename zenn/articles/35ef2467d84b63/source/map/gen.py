import json, re
D = json.load(open("internals.json"))
T = open("/Users/akazawt/works/data-science/claudecode/.claude/skills/html/references/page-template.html").read()
f = lambda x: f"{x:,}"
toks = D["tokens"]; comp = D["compressed"]; ids = D["ids"]; P = D["pos"]
hs = D["heads"]; m = D["multipliers"]; hz = D["hash"]; g = D["gate"]; A = D["attention_block1"]
H7 = A["heads"][7]

# ---------------------------------------------------------------- Engram map (SVG 880 x 640)
def engram_svg():
    o = []
    add = o.append
    # tokens
    x = 20
    pos = {}
    for i, t in enumerate(toks):
        w = 22 + 8.2 * len(t)
        cls = "tk cur" if i == P else ("tk ng" if i >= P - 2 else "tk")
        add(f'<g class="{cls}"><rect x="{x:.0f}" y="18" width="{w:.0f}" height="30" rx="6"/><text x="{x + w/2:.0f}" y="38" text-anchor="middle">{t}</text></g>')
        pos[i] = (x, w); x += w + 6
    add(f'<g class="tk ghost"><rect x="{x:.0f}" y="18" width="70" height="30" rx="6"/><text x="{x+35:.0f}" y="38" text-anchor="middle">␣Hood ?</text></g>')
    cx, cw = pos[P]
    add(f'<text class="lab y" x="{cx + cw/2:.0f}" y="64" text-anchor="middle">現在地</text>')
    # S1 compress
    add('<g class="st s1"><text class="h" x="20" y="96">1. 番号をそろえる</text>')
    for k, i in enumerate(range(P - 2, P + 1)):
        add(f'<rect class="ids" x="{20 + k*94}" y="104" width="88" height="40" rx="6"/><text x="{64 + k*94}" y="120" text-anchor="middle" class="sm">{toks[i]}</text><text x="{64 + k*94}" y="137" text-anchor="middle" class="num">{ids[i]} → {comp[i]}</text>')
    add('</g>')
    # S2 n-grams
    add('<g class="st s2"><text class="h" x="20" y="168">2. n-gram = 番号の並び</text>')
    add(f'<rect class="ids dash" x="20" y="176" width="134" height="30" rx="6"/><text x="87" y="196" text-anchor="middle" class="num tiny">2-gram ({comp[P-1]}, {comp[P]})</text>')
    add(f'<rect class="ids dbl" x="160" y="176" width="170" height="30" rx="6"/><text x="245" y="196" text-anchor="middle" class="num tiny">3-gram ({comp[P-2]}, {comp[P-1]}, {comp[P]})</text>')
    add('</g>')
    # S3 hash
    add('<g class="st s3"><text class="h" x="20" y="230">3. 掛けて XOR、1 つの大きな数に</text>')
    add(f'<text class="num" x="20" y="250">{comp[P]}×m₀ XOR {comp[P-1]}×m₁</text><text class="num b" x="20" y="268">= {f(hz["rolling_2gram"])}</text>')
    add(f'<text class="num" x="20" y="290">さらに XOR {comp[P-2]}×m₂</text><text class="num b" x="20" y="308">= {f(hz["rolling_3gram"])}</text>')
    add('</g>')
    # S4 remainders, one line per head, aligned with the bands
    TY, BH = 340, 18
    add(f'<g class="st s4"><text class="h" x="20" y="{TY-10}">4. 16 個の素数で割った余り = 行番号</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH
        src = "2-gram" if h["ngram"] == 2 else "3-gram"
        add(f'<text class="num tiny" x="20" y="{y+13}">{src} ÷ {f(h["prime"])} 余り {f(h["local_row"])}</text>')
        add(f'<text class="num tiny b" x="228" y="{y+13}">→ 行 {f(h["table_row"])}</text>')
    add('</g>')
    # table column
    X0, X1 = 350, 440
    add(f'<g class="tbl"><text class="h" x="{(X0+X1)/2}" y="{TY-28}" text-anchor="middle">表</text><text class="sm" x="{(X0+X1)/2}" y="{TY-12}" text-anchor="middle">1,049,422 行 × 64</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH
        add(f'<rect class="band {"b2" if h["ngram"]==2 else "b3"}" x="{X0}" y="{y}" width="{X1-X0}" height="{BH-1}"/>')
        add(f'<text class="tiny dim" x="{X1-4}" y="{y+12}" text-anchor="end">{c}</text>')
    add(f'<text class="tiny dim" x="{X0-4}" y="{TY + 16*BH + 14}">行 0 から 1,049,421 まで。右の数字は範囲の番号</text></g>')
    # row ticks and arrows S4 -> table
    add('<g class="st s5a">')
    for c, h in enumerate(hs):
        y = TY + c * BH
        ty = y + 2 + (BH - 5) * h["local_row"] / h["prime"]
        add(f'<line class="ptr" x1="318" y1="{y+9}" x2="{X0-2}" y2="{ty:.1f}" marker-end="url(#ah)"/>')
        add(f'<rect class="tick" x="{X0}" y="{ty-1.5:.1f}" width="{X1-X0}" height="3"/>')
    add('</g>')
    # read rows -> 16 strips
    RX, CW = 500, 5.6
    add(f'<g class="st s5"><text class="h" x="{RX}" y="{TY-28}">5. その 16 行を読む</text><text class="sm" x="{RX}" y="{TY-12}">1 行 = 64 個の数。探さず、番号の行をそのまま読む</text>')
    for c, h in enumerate(hs):
        y = TY + c * BH
        ty = y + 2 + (BH - 5) * h["local_row"] / h["prime"]
        add(f'<line class="pull" x1="{X1}" y1="{ty:.1f}" x2="{RX-4}" y2="{y+8}"/>')
        add(f'<rect class="strip {"b2" if h["ngram"]==2 else "b3"}" x="{RX}" y="{y+2}" width="{64*CW:.0f}" height="{BH-5}"/>')
    v = D["row_values_first6"][0]
    add(f'<text class="num tiny" x="{RX}" y="{TY + 16*BH + 30}">行 15,920 の中身: {", ".join(str(a) for a in v[:3])}, …</text></g>')
    # concat -> e_t
    EY = 700
    add(f'<g class="st s6"><text class="h" x="20" y="{EY-10}">6. 16 行 × 64 個 = 1,024 個を 1 列につなぐ</text>')
    add(f'<path class="pull" d="M{RX+180} {TY+16*BH+36} C {RX+180} {EY-40}, 440 {EY-40}, 440 {EY-2}" fill="none" marker-end="url(#ahg)"/>')
    add(f'<rect class="et" x="20" y="{EY}" width="840" height="22"/>')
    for c in range(1, 16): add(f'<line class="sep" x1="{20 + c*52.5:.1f}" y1="{EY}" x2="{20 + c*52.5:.1f}" y2="{EY+22}"/>')
    for c in range(16): add(f'<text class="tiny dim" x="{20 + c*52.5 + 26:.1f}" y="{EY+15}" text-anchor="middle">範囲 {c}</text>')
    add(f'<text class="num tiny" x="20" y="{EY+36}">e = {", ".join(str(a) for a in D["e_first8"][:6])}, …（1,024 個。先頭の 64 個が範囲 0 の行 15,920 の中身）</text></g>')
    # W_kv -> key | value
    WY = 760
    add(f'<g class="st s7"><text class="h" x="20" y="{WY}">7. 学習した行列 W_kv を掛けて、1,024 個を作り直し、前半と後半に分ける</text>')
    add(f'<text class="sm" x="20" y="{WY+40}">e（1,024 個）×</text>')
    add(f'<rect class="mat" x="120" y="{WY+10}" width="64" height="64"/><text class="tiny" x="152" y="{WY+40}" text-anchor="middle">W_kv</text><text class="tiny" x="152" y="{WY+54}" text-anchor="middle">1,024×1,024</text>')
    add(f'<text class="op" x="196" y="{WY+47}">→</text>')
    add(f'<rect class="key" x="222" y="{WY+28}" width="300" height="24"/><text class="sm" x="372" y="{WY+45}" text-anchor="middle">前半 512 個 = key</text>')
    add(f'<rect class="val" x="528" y="{WY+28}" width="300" height="24"/><text class="sm" x="678" y="{WY+45}" text-anchor="middle">後半 512 個 = value</text>')
    add(f'<text class="num tiny" x="222" y="{WY+68}">key = {", ".join(str(a) for a in D["key_first6"][:4])}, …</text><text class="num tiny" x="528" y="{WY+68}">value = {", ".join(str(a) for a in D["value_first6"][:4])}, …</text></g>')
    # gate
    GY = 860
    add(f'<g class="st s8"><text class="h" x="20" y="{GY}">8. GPT 本体の隠れ状態 h と key を 1 回だけ比べて、足す量（ゲート）を決める</text>')
    add(f'<rect class="hid" x="20" y="{GY+10}" width="200" height="24"/><text class="sm" x="120" y="{GY+27}" text-anchor="middle">h: ブロック 0 の後（512 個）</text>')
    add(f'<text class="op" x="228" y="{GY+28}">·</text><rect class="key" x="244" y="{GY+10}" width="80" height="24"/><text class="sm" x="284" y="{GY+27}" text-anchor="middle">key</text>')
    add(f'<text class="num" x="336" y="{GY+28}">= {g["dot_over_sqrt_d"]:.2f}  → 符号つき √ → {g["signed_sqrt"]:.2f}  → sigmoid → ゲート <tspan class="b">{g["gate"]:.3f}</tspan></text>')
    add('</g>')
    # add
    AY = 930
    add(f'<g class="st s9"><text class="h" x="20" y="{AY-6}">9. value を足す</text><rect class="hid" x="20" y="{AY+2}" width="60" height="24"/><text class="sm" x="50" y="{AY+19}" text-anchor="middle">h</text><text class="op" x="88" y="{AY+20}">+</text><text class="num" x="108" y="{AY+19}">{g["gate"]:.3f} ×</text><rect class="val" x="170" y="{AY+2}" width="90" height="24"/><text class="sm" x="215" y="{AY+19}" text-anchor="middle">value</text><text class="op" x="270" y="{AY+20}">→</text><rect class="hid" x="296" y="{AY+2}" width="110" height="24"/><text class="sm" x="351" y="{AY+19}" text-anchor="middle">ブロック 1 へ</text><text class="num tiny" x="420" y="{AY+19}">h の先頭 {D["h_first6"][0]} → {D["h_plus_first6"][0]}</text></g>')
    add('<defs><marker id="ahg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#1f7a4d"/></marker><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#8a5a12"/></marker></defs>')
    return f'<svg id="emap" viewBox="0 0 880 970" width="100%">{"".join(o)}</svg>'

E_STEPS = [
 ("全体", "表（真ん中の柱）は 1,049,422 行あり、1 行は 64 個の数です。16 の範囲に分かれていて、上の 8 範囲を 2-gram、下の 8 範囲を 3-gram が使います。この記事のモデルの値で、表の中身は学習で書き換わる数です。回数は入っていません。「次へ」で 1 段ずつ進みます。", []),
 ("1. 番号をそろえる", f"大文字と小文字などの違いをまとめた番号に置き換えます。「␣Riding」は GPT-2 の番号 {ids[P]} で、そろえると {comp[P]} になります。「␣riding」も同じ {comp[P]} になります。ここは決まった対応表で置き換えるだけで、学習しません。", ["s1"]),
 ("2. n-gram を作る", f"現在地「␣Riding」で終わる並びを、そろえた番号のまま取ります。2-gram は 1 つ前と現在地の ({comp[P-1]}, {comp[P]})、3-gram は 2 つ前からの ({comp[P-2]}, {comp[P-1]}, {comp[P]}) です。次の「Hood」はまだ読んでいないので入りません。", ["s1", "s2"]),
 ("3. 1 つの大きな数にする", f"番号に、乱数で一度だけ決めた奇数を掛けて、XOR という計算で合わせます。m₀ = {f(m[0])}、m₁ = {f(m[1])}、m₂ = {f(m[2])} です。2-gram の数は {f(hz['rolling_2gram'])}、3-gram の数はそれにもう 1 つ XOR した {f(hz['rolling_3gram'])} です。学習する重みは使いません。", ["s2", "s3"]),
 ("4. 余りが行番号", f"大きな数を、範囲ごとに違う素数で割った余りが、その範囲の中の行番号です。範囲 0 は素数 65,537 で割って余り 15,920、範囲 1 は 65,539 で割って余り 24,423 です。範囲の先頭の行番号を足すと、表全体での行番号になります（範囲 1 は 65,537 から始まるので 89,960）。これを 16 範囲で行い、16 個の行番号を得ます。", ["s3", "s4"]),
 ("5. 16 行を読む", "16 個の行番号の行を、表から直接読みます。配列の何番目を読むのと同じで、表の中を探したり、中身と比べたりはしません。読んだ 1 行は 64 個の数です。図の矢印は、行番号が柱のどの高さを指すかを示しています。", ["s4", "s5a", "s5"]),
 ("6. つなぐ", f"読んだ 16 行を 1 列につなぎます。16 行 × 64 個 = 1,024 個の数になります。これを e と書きます。e の頭の数は {', '.join(str(a) for a in D['e_first8'][:4])} … で、範囲 0 の行 15,920 の中身そのものです。", ["s5", "s6"]),
 ("7. key と value に作り替える", f"e に、学習した行列 W_kv（1,024 × 1,024 個の数）を掛けます。出てきた 1,024 個のうち、前半の 512 個を key、後半の 512 個を value と呼びます。key も value も表から探した値ではなく、読んだ行から計算した値です。", ["s6", "s7"]),
 ("8. ゲートを決める", f"GPT 本体がブロック 0 まで計算した隠れ状態 h（512 個）と key を、同じ番目どうし掛けて足します。大きさをそろえて割ると {g['dot_over_sqrt_d']:.2f}、符号を残して平方根を取ると {g['signed_sqrt']:.2f}、sigmoid で 0 と 1 の間にすると {g['gate']:.3f} です。比べるのはこの 1 回だけです。", ["s7", "s8"]),
 ("9. 足す", f"value の 512 個それぞれに {g['gate']:.3f} を掛けて、h に足します。h の頭の数 {D['h_first6'][0]} は {D['h_plus_first6'][0]} に、{D['h_first6'][2]} は {D['h_plus_first6'][2]} に変わります。足したものがブロック 1 に渡ります。", ["s8", "s9"]),
]

# ---------------------------------------------------------------- Attention map (SVG 880 x 400)
def attn_svg():
    o = []; add = o.append
    n = P + 1; W = 880; cw = 110
    xs = [40 + i * 118 for i in range(n)]
    for i, t in enumerate(toks):
        cls = "tk cur" if i == P else "tk"
        add(f'<g class="{cls}"><rect x="{xs[i]}" y="20" width="{cw-8}" height="30" rx="6"/><text x="{xs[i]+(cw-8)/2}" y="40" text-anchor="middle">{t}</text></g>')
        add(f'<g class="st a1"><rect class="kk" x="{xs[i]}" y="70" width="48" height="24"/><text class="sm" x="{xs[i]+24}" y="87" text-anchor="middle">k{i}</text><rect class="vv" x="{xs[i]+54}" y="70" width="48" height="24"/><text class="sm" x="{xs[i]+78}" y="87" text-anchor="middle">v{i}</text></g>')
    qx = xs[P] + 25
    add(f'<g class="st a1"><rect class="qq" x="{xs[P]}" y="300" width="{cw-8}" height="26"/><text class="sm" x="{xs[P]+(cw-8)/2}" y="318" text-anchor="middle">q（現在地）</text></g>')
    mx = max(H7["weights"])
    for i in range(n):
        wgt = H7["weights"][i]
        add(f'<line class="st a2 cmp" x1="{xs[P]+(cw-8)/2}" y1="300" x2="{xs[i]+24}" y2="94"/>')
        add(f'<text class="st a2 num tiny" x="{xs[i]+24}" y="118" text-anchor="middle">{H7["scores"][i]:.2f}</text>')
        bh = 90 * wgt / mx
        add(f'<g class="st a3"><rect class="wbar" x="{xs[i]+30}" y="{230-bh:.1f}" width="40" height="{bh:.1f}"/><text class="num tiny b" x="{xs[i]+50}" y="{246}" text-anchor="middle">{wgt:.3f}</text></g>')
        add(f'<line class="st a4 mix" x1="{xs[i]+78}" y1="94" x2="{W-90}" y2="360" style="stroke-width:{1 + 9*wgt/mx:.1f}"/>')
    add(f'<g class="st a4"><rect class="vv" x="{W-150}" y="352" width="120" height="28"/><text class="sm" x="{W-90}" y="371" text-anchor="middle">Σ 重み × v</text></g>')
    add('<text class="st a2 tiny dim" x="40" y="136">q · k ÷ √64 の点数</text><text class="st a3 tiny dim" x="40" y="262">softmax の重み（合計 1）</text>')
    return f'<svg id="amap" viewBox="0 0 880 400" width="100%">{"".join(o)}</svg>'

A_STEPS = [
 ("全体", "GPT の各ブロックにある Attention です。ここでは、Engram を足した後のブロック 1 の、8 つのヘッドのうちヘッド 7 を見ます。値はこの記事のモデル（seed 1337）の実測です。", []),
 ("1. q、k、v を作る", "どの位置でも、その位置の隠れ状態に学習した行列を掛けて、q、k、v の 3 組を作ります（このモデルでは 1 ヘッドあたり 64 個ずつ）。k と v は全位置の分を使い、q は現在地「␣Riding」の分を使います。Engram と違って、候補はそれまでの文脈そのものから作られます。", ["a1"]),
 ("2. 全部の k と比べる", "現在地の q を、7 つの位置すべての k と、同じ番目どうし掛けて足し、√64 で割って点数にします。ここが「探す」に当たる部分で、候補の数は文の長さと同じだけあります。", ["a1", "a2"]),
 ("3. softmax で重みを分ける", f"点数を softmax で重みに変えます。重みは合計が 1 になるように分け合います。このヘッドは「␣Red」に {H7['weights'][5]:.3f}、「␣Little」に {H7['weights'][4]:.3f} と、名前の前の語に重みを多く置きました。", ["a1", "a2", "a3"]),
 ("4. v を混ぜる", "それぞれの位置の v に重みを掛けて、全部足します。線の太さが重みです。Attention は多くの v を混ぜ、Engram は 1 つの value を足す量だけ決めます。", ["a1", "a3", "a4"]),
]

CSS = """
.fig{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 12px 6px;margin:16px 0}
.fig svg text{font-family:inherit;fill:#12241c;font-size:12.5px}
.fig .h{font-weight:700;font-size:13px;fill:#0f4a2e}.fig .sm{font-size:11.5px}.fig .tiny{font-size:10.5px}.fig .dim{fill:#5b6f65}
.fig .num{font-family:Menlo,Consolas,monospace;font-size:11.5px}.fig .num.tiny{font-size:10px}.fig .b{font-weight:700;fill:#0f4a2e}
.fig .lab.y{fill:#8a5a12;font-weight:700}.fig .op{font-size:18px;font-weight:700}
.tk rect{fill:#eef2ef;stroke:#5b6f65}.tk.ng rect{stroke:#8a5a12}.tk.cur rect{fill:#fdf3e2;stroke:#8a5a12;stroke-width:2.5}.tk.ghost rect{fill:#fff;stroke:#8a94a0;stroke-dasharray:4 3}.tk.ghost text{fill:#5b6f65}
.ids{fill:#fdf3e2;stroke:#8a5a12}.ids.dash{stroke-dasharray:4 3}.ids.dbl{stroke-width:3}
.band.b2{fill:#e8f4ec;stroke:#1f7a4d}.band.b3{fill:#d4ecdd;stroke:#1f7a4d}
.tick{fill:#8f2f2f}.ptr{stroke:#8a5a12;stroke-width:1}.pull{stroke:#1f7a4d;stroke-width:1}
.strip.b2{fill:url(#none);fill:#e8f4ec;stroke:#1f7a4d}.strip.b3{fill:#d4ecdd;stroke:#1f7a4d}
.et{fill:#e8f4ec;stroke:#1f7a4d}.sep{stroke:#1f7a4d;stroke-width:.6}
.mat{fill:#cfe6d8;stroke:#0f4a2e}.key{fill:#e8f4ec;stroke:#1f7a4d;stroke-width:2}.val{fill:#e8f4ec;stroke:#1f7a4d;stroke-width:2;stroke-dasharray:5 2}
.hid{fill:#e6eef8;stroke:#1d4e8f}
.kk{fill:#e6eef8;stroke:#1d4e8f}.vv{fill:#e6eef8;stroke:#1d4e8f;stroke-dasharray:4 2}.qq{fill:#fdf3e2;stroke:#8a5a12;stroke-width:2}
.cmp{stroke:#8a5a12;stroke-width:1.2}.wbar{fill:#1d4e8f;opacity:.75}.mix{stroke:#1d4e8f;opacity:.55}
.st{transition:opacity .35s}.dimmed .st{opacity:.12}.dimmed .st.on{opacity:1}
.ctl{display:flex;gap:8px;align-items:center;margin:6px 0 4px}.ctl button{border:1px solid var(--line);background:var(--gp);border-radius:999px;padding:4px 14px;cursor:pointer;font-size:13px}
.ctl .cnt{font-size:13px;color:var(--ink2)}.cap{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:14px;min-height:72px}
.cap b{color:var(--gd)}
"""
JS = """
function stepper(id, steps){
  const svg=document.getElementById(id), cap=document.getElementById(id+'-cap'), cnt=document.getElementById(id+'-cnt');
  let i=0;
  function show(){
    const s=steps[i]; svg.classList.toggle('dimmed', s[2].length>0);
    svg.querySelectorAll('.st').forEach(e=>{e.classList.toggle('on', s[2].some(c=>e.classList.contains(c)));});
    cap.innerHTML='<b>'+s[0]+'</b>　'+s[1]; cnt.textContent=(i+1)+' / '+steps.length;
  }
  document.getElementById(id+'-prev').onclick=()=>{i=(i+steps.length-1)%steps.length;show();};
  document.getElementById(id+'-next').onclick=()=>{i=(i+1)%steps.length;show();};
  show();
}
"""
def fig(svg, sid, steps, caption):
    return (f'<div class="fig">{svg}<div class="ctl"><button id="{sid}-prev">◀ 戻る</button><button id="{sid}-next">次へ ▶</button><span class="cnt" id="{sid}-cnt"></span></div>'
            f'<div class="cap" id="{sid}-cap"></div></div><figcaption>{caption}</figcaption>'
            f'<script>stepper("{sid}", {json.dumps(steps, ensure_ascii=False)});</script>')

body = f"""
<p class="nav"><a href="index.html">全体の目次</a> &nbsp;/&nbsp; <a href="engram-ideas.html">Engram の発想をどう良くするか</a> &nbsp;/&nbsp; Engram と Attention の中身を実際の値で追う</p>
<h1>Engram と Attention の中身を、実際の値で 1 歩ずつ追う</h1>
<div class="lead">
<p><b>結論から。</b>Engram は表の中を探しません。トークンの番号から計算だけで 16 個の行番号を出し、その行を直接読みます。読んだ 16 行 × 64 個 = 1,024 個の数に学習した行列を掛けて key と value を作り、key を GPT 本体の隠れ状態と<b>1 回だけ</b>比べて、value を足す量を決めます。Attention は、現在地の q を<b>それまでの全位置の</b> k と比べて重みを分け合い、多くの v を混ぜます。</p>
<p style="margin-bottom:0"><b>このページの値。</b>Zenn の記事「小さな GPT で Engram を試す」で作ったモデル（seed 1337）に、文「The girl was called Little Red Riding」を入れ、現在地「␣Riding」で計算の途中の数をすべて取り出したものです。手で計算し直したゲートは 0.887 で、モデルが記録した値と一致しました。</p>
</div>

<table>
<tr><th>#</th><th>なぜ</th><th>どう測った</th><th>他の選択肢</th><th>結果</th><th>関連</th></tr>
<tr><td>1</td><td>行番号がどこから来るかを見るため</td><td>モデルの番号表、乗数、素数、範囲の先頭から手で計算し、モデルの出す行番号と照合</td><td>コードを読むだけ</td><td>16 個すべて一致。2-gram の数 {f(hz['rolling_2gram'])} を 65,537 で割った余りが 15,920</td><td>1 節</td></tr>
<tr><td>2</td><td>key と value が何かを見るため</td><td>読んだ 16 行を 1,024 個につなぎ、W_kv を掛けて 512 個ずつに分けた</td><td>図の箱だけで説明する</td><td>key と value は表から探した値ではなく、読んだ行から計算した値</td><td>1 節</td></tr>
<tr><td>3</td><td>比べる相手を見るため</td><td>ゲートを式どおりに手で計算</td><td>記録したゲートを使う</td><td>{g['dot_over_sqrt_d']:.2f} → {g['signed_sqrt']:.2f} → {g['gate']:.3f}。記録値 {g['recorded_gate']:.3f} と一致</td><td>1 節</td></tr>
<tr><td>4</td><td>Attention と比べるため</td><td>ブロック 1 の 8 ヘッドの q · k と softmax を手で計算し、PyTorch の計算と照合</td><td>一般論で説明する</td><td>ヘッド 7 は「␣Red」0.345、「␣Little」0.253。差は 0.001 以内</td><td>2 節</td></tr>
</table>

<h2>1. Engram: 番号で行を決め、読み、1 回だけ比べる</h2>
<p>真ん中の柱が表です。左側で、トークンの番号から行番号を計算します。矢印は、16 個の行番号が柱のどの高さを指すかを示しています。右側で、読み出した 16 行が key と value に変わり、ゲートを掛けて足されるまでを示します。「次へ」を押すと、その段だけが濃くなります。</p>
{fig(engram_svg(), "emap", E_STEPS, "この記事のモデル（seed 1337）の実際の値。表の柱の中の赤い線は、行番号が指す行の位置（範囲の中での高さ）。行の中身は最初は乱数で、学習で書き換わる数。")}

<div class="note"><p style="margin:0"><b>よくある誤解。</b>key と value を作ってから表と照合する、のではありません。表を引くのは手順 5 だけで、それは番号の行をそのまま読む操作です。照合に当たる比べる計算は手順 8 の 1 回だけで、その相手は表ではなく、GPT 本体が計算している途中の隠れ状態です。</p></div>

<h2>2. Attention: 全位置の k と比べて、重みを分け合う</h2>
<p>同じ文で、GPT の各ブロックにある Attention を追います。Engram と同じく、比べて、掛けて、足す計算ですが、候補は文脈の全位置から作られ、重みは候補の間で分け合います。</p>
{fig(attn_svg(), "amap", A_STEPS, "ブロック 1、ヘッド 7 の実際の点数と重み。ほかのヘッドは別の位置に重みを置く（ヘッド 0 は文頭の「␣The」に 0.346 など）。")}

<h2>3. 並べて見る</h2>
<table>
<tr><th></th><th>Attention</th><th>Engram</th></tr>
<tr><td>候補の作り方</td><td>文脈の全位置の隠れ状態から k と v を作る</td><td>トークンの番号だけで 16 行を決めて読み、key と value を 1 組作る</td></tr>
<tr><td>候補の数</td><td>現在地までの位置の数（この文では 7）</td><td>1 組</td></tr>
<tr><td>比べる相手</td><td>現在地の q と、全部の k</td><td>現在地の隠れ状態と、1 つの key</td></tr>
<tr><td>重み</td><td>softmax。合計 1 を分け合う</td><td>sigmoid。0 と 1 の間の数 1 つ（ここでは {g['gate']:.3f}）</td></tr>
<tr><td>足すもの</td><td>多くの v の重み付きの和</td><td>1 つの value にゲートを掛けたもの</td></tr>
<tr><td>表や過去の結果</td><td>過去の全位置の k と v を使う</td><td>学習した表を使う。過去に要るのは直前 2 トークンの番号だけ</td></tr>
</table>

<h2>4. このページで扱っていないこと</h2>
<ul>
<li>値は seed 1337 の 1 か所、1 つの文のものです。ゲートや重みは位置と文で変わります。</li>
<li>Attention はブロック 1 の 1 つのヘッドだけを示しました。12 ブロック × 8 ヘッドのそれぞれが、別の重みの分け方をします。</li>
<li>学習で表の行がどう書き換わるかは、ここでは追っていません。</li>
</ul>
<p class="foot">値の取り出しは zenmai-lab の <code>experiments/2026-10-21-engram-nanogpt</code>（commit 7d12d41）の公開モデル（Hugging Face の littlemex/engram-nanogpt-wikitext103、revision e9758158）で行いました。行番号は <code>NgramHash</code> の出力と、ゲートはモデルが記録した値と、Attention は PyTorch の <code>scaled_dot_product_attention</code> と照合しています。</p>
"""
head = T[:T.index("<body>")].replace("PAGE_TITLE", "Engram と Attention の中身を、実際の値で 1 歩ずつ追う")
head = head.replace("</style>", CSS + "</style>")
tail = T[T.index("<script"):] if "<script" in T else "</body></html>"
page = head + "<body>\n<script>" + JS + "</script>\n<div class=\"wrap\">\n" + body + "\n</div>\n" + tail
open("engram-internals.html", "w").write(page)
print(len(page))
