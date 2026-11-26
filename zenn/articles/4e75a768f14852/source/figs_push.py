"""Figures for the push / pull KV transfer article."""
from core import t, bar, radios, frame_inputs, info_panel, select_css, snippet

VL = "github.com/vllm-project/vllm/blob/955f85be04/vllm/distributed/kv_transfer/kv_connector/v1"
SG = "github.com/sgl-project/sglang/blob/0de06898bd/python/sglang/srt/disaggregation"
NX = "github.com/ai-dynamo/nixl/blob/27542ee659/src"
LF = "github.com/ofiwg/libfabric/blob/1a2262446b/prov"


def src(s):
    return f'<span class="src">{s}</span>'


def _seq(title, lanes, modes, mode_labels, lane_info, skin="zenn-dark"):
    """Sequence diagram walked one step at a time, with a switch between scenarios.
    lanes: [(key, label, role)] at 12/50/88 % (3 lanes) or 16/84 % (2 lanes).
    modes: {mode: [(label, from, to, caption, kind)]}; kind '' control, 'd' data.
    A step whose from == to is drawn as a box on that lane (work done locally)."""
    pos = {k: p for (k, _, _), p in zip(lanes, (12, 50, 88) if len(lanes) == 3 else (16, 84))}
    mk = list(modes)
    n = max(len(v) for v in modes.values())
    lk = [k for k, _, _ in lanes if k in lane_info]
    inputs = frame_inputs(radios("m", mk) + radios("st", [str(i) for i in range(1, n + 1)]) + radios("s", ["0"] + lk))
    lane_html = "".join(f'<label for="s-{k}" class="box {r} ln hot b-{k}" style="left:{pos[k]}%">{lab}<span class="q">i</span></label>' for k, lab, r in lanes)
    close = f'<label class="pill" for="s-0">&#10005; {t("back to the steps", "手順に戻る")}</label>'
    linfo = "".join(f'<div class="li i-{k}">{v}<div class="cl">{close}</div></div>' for k, v in lane_info.items())
    arrows, caps, alls, rules = "", "", "", []
    for m, ss in modes.items():
        for i, (lab, a, b, cap, kind) in enumerate(ss, 1):
            top = f"top:calc(var(--rw) * {i-1} + 6px)"
            if a == b:
                arrows += f'<div class="ar m{m} a{i} sf {kind}" style="{top};left:{min(max(pos[a]-(13 if len(lanes) == 3 else 18), 1), 73 if len(lanes) == 3 else 64)}%;width:{26 if len(lanes) == 3 else 35}%"><em><b>{i}</b> {lab}</em></div>'
            else:
                l, r = sorted((pos[a], pos[b]))
                dirc = "r" if pos[b] > pos[a] else "l"
                em = ' style="left:70%"' if len(lanes) == 3 and r - l > 50 else ""
                arrows += f'<div class="ar m{m} a{i} {dirc} {kind}" style="{top};left:{l}%;width:{r-l}%"><span class="ah"></span><em{em}><b>{i}</b> {lab}</em></div>'
            caps += f'<div class="cap m{m} k{i}">{cap}</div>'
    for i in range(1, n + 1):
        later = [f"#st-{i}:checked~.zr .a{j}" for j in range(i + 1, n + 1)]
        if later:
            rules.append(",".join(later) + "{opacity:0}")
        rules.append(f"#st-{i}:checked~.zr .a{i}{{opacity:1;filter:none}}#st-{i}:checked~.zr .a{i}::after{{animation:shine 1.2s linear infinite}}")
        rules.append(f"#st-{i}:checked~.zr .k{i},#st-{i}:checked~.zr .n{i}{{display:flex}}")
    for m in mk:
        others = [o for o in mk if o != m]
        rules.append(",".join(f".zf #m-{m}:checked~.zr .m{o}" for o in others) + "{display:none!important}")
        rules.append(f"#m-{m}:checked~.zr .pm-{m}{{background:var(--fg);color:#000}}")

    def nav(m, i, k):
        if i > k:
            return f'<div class="nav m{m} n{i}"><span></span><label class="pill" for="st-1">&#8634; {t("again", "最初から")}</label></div>'
        return (f'<div class="nav m{m} n{i}">' + (f'<label class="pill" for="st-{i-1}">&#9664; {t("back", "戻る")}</label>' if i > 1 else "<span></span>")
                + f'<span class="hint">{i} / {k}</span>'
                + (f'<label class="pill" for="st-{i+1}">{t("next", "次へ")} &#9654;</label>' if i < k else f'<label class="pill" for="st-1">&#8634; {t("again", "最初から")}</label>')
                + "</div>")
    navs = "".join(nav(m, i, len(ss)) for m, ss in modes.items() for i in range(1, n + 1))
    lifel = "".join(f'<i class="lf" style="left:{p}%"></i>' for p in pos.values())
    switch = '<div class="ctl">' + "".join(f'<label class="pill pm-{m}" for="m-{m}">{lab}</label>' for m, lab in mode_labels.items()) + "</div>"
    body = (inputs + '<div class="zr">' + bar(*title) + switch
            + f'<div class="seq">{lifel}<div class="lanes">{lane_html}</div><div class="msgs">{arrows}</div></div>'
            + f'<div class="info"><div class="caps">{caps}</div>{navs}{linfo}</div></div>')
    css = f"""
.seq{{position:relative;--rw:26px;height:calc(var(--rw) * {n} + 58px)}}
@media (max-width:520px){{.seq{{--rw:27px}}.ar em{{font-size:10.5px}}.ln{{font-size:11.5px;width:30%}}}}
.lf{{position:absolute;top:36px;bottom:0;width:2px;margin-left:-1px;background:var(--line)}}
.lanes{{position:relative;height:36px}}
.ln{{position:absolute;transform:translateX(-50%);width:26%;text-align:center;font-weight:700;padding:6px 0;text-shadow:0 0 3px #000;font-size:13px}}
.msgs{{position:absolute;top:46px;left:0;right:0}}
.ar{{position:absolute;height:24px;opacity:.75}}
.ar::before{{content:"";position:absolute;left:0;right:0;top:11px;border-top:3px dashed var(--fg)}}
.ar.d::before{{border-top:7px solid var(--p4);top:9px}}
.ar.sf::before{{top:0;height:22px;border:2px solid var(--p3);border-radius:6px;background:var(--p3-bg)}}
.ar::after{{content:"";position:absolute;top:9px;height:7px;width:22px;left:0;background:var(--hi);border-radius:4px;opacity:0}}
.ar.sf::after{{display:none}}
@keyframes shine{{0%{{left:0;opacity:0}}15%,85%{{opacity:1}}100%{{left:calc(100% - 22px);opacity:0}}}}
.ar.l::after{{animation-direction:reverse!important}}
.ar em{{position:absolute;top:-8px;left:50%;transform:translateX(-50%);font-style:normal;font-size:12px;background:#000;padding:0 6px;white-space:nowrap}}
.ar.sf em{{top:3px;background:transparent;text-shadow:0 0 3px #000,0 0 3px #000}}.ar.sf em b{{text-shadow:none}}
.ah{{position:absolute;top:4px;width:0;height:0;border:8px solid transparent}}
.r .ah{{right:-6px;border-left-color:var(--fg)}}.l .ah{{left:-6px;border-right-color:var(--fg)}}
.d.r .ah{{border-left-color:var(--p4)}}.d.l .ah{{border-right-color:var(--p4)}}
.cap,.nav{{display:none}}.info>.caps{{display:block}}@media (max-width:520px){{.zf #zs:checked~.zr .caps{{font-size:9.5px;line-height:1.25;column-gap:8px}}#zs:checked~.zr .seq{{--rw:22px}}#zs:checked~.zr .ar.sf::before{{height:18px}}}}.cap{{flex-direction:column}}.cap{{margin-bottom:8px}}.nav{{justify-content:space-between;align-items:center}}
.ln.hot:hover{{transform:translateX(-50%) translateY(-2px)}}.cl{{margin-top:6px}}
.ar em b{{display:inline-block;min-width:15px;height:15px;line-height:15px;border-radius:50%;background:var(--fg);color:#000;font-size:10px;text-align:center;margin-right:3px}}
.lgd{{font-size:11.5px;color:var(--mut);margin:2px 0 0}}
""" + "\n".join(rules) + "\n" + select_css(["0"] + lk) + "".join(f"#s-{k}:checked~.zr .cap,#s-{k}:checked~.zr .nav{{display:none!important}}" for k in lk)
    still = """.ar{opacity:1!important;filter:none!important}
.ar::after{opacity:0!important}
.caps{columns:2;column-gap:18px;font-size:11px;line-height:1.35}
.cap{display:block!important;margin:0;break-inside:avoid}
.cap .src{display:none}
.nav{display:none!important}
.li{display:none!important}
.ln{box-shadow:none!important}"""
    return snippet(body, css, still, skin)


LANE_INFO = {
    "r": t("<b>Router</b>: receives the client's request and sends it to a prefill instance and a decode instance; when decode is chosen depends on the setup. In vLLM's examples this is a proxy, in SGLang it is sgl-router; in llm-d a scheduler picks the pods and a routing sidecar in the decode pod forwards the requests.",
           "<b>Router</b>: クライアントのリクエストを受け、prefill と decode のインスタンスに届ける。decode をいつ選ぶかは構成で変わる。vLLM の例ではプロキシ、SGLang では sgl-router がこの役を受け持つ。llm-d では、スケジューラが Pod を選び、decode の Pod に付く routing sidecar がリクエストを中継する。"),
    "p": t("<b>Prefill instance</b>: computes the attention keys and values of every prompt token, the KV cache, into its GPU memory; with chunked prefill it does so chunk by chunk.",
           "<b>prefill のインスタンス</b>: プロンプトの各トークンの attention の key と value を、KV キャッシュとして自分の GPU メモリに作る。chunked prefill ではチャンクごとに計算する。"),
    "d": t("<b>Decode instance</b>: needs that KV cache in its own GPU memory, then generates the output one token at a time. It keeps the KV in fixed-size blocks; a block id names where in its GPU memory a block lives.",
           "<b>decode のインスタンス</b>: その KV キャッシュを自分の GPU メモリに受け取ってから、出力を 1 トークンずつ作る。KV は決まった大きさのブロックに分けて持ち、ブロックの番号で GPU メモリの置き場所を指す。"),
}


def pull_push():
    lanes = [("r", "Router", "r3"), ("p", "Prefill", "r2"), ("d", "Decode", "r1")]
    pull = [
        (t("request", "リクエスト"), "r", "p", t("1. The router sends the request to the prefill instance only.", "1. Router は、リクエストを prefill のインスタンスにだけ送る。"), ""),
        (t("compute KV", "KV を計算"), "p", "p", t("2. Prefill computes the KV cache and keeps it in its GPU memory.", "2. prefill が KV キャッシュを作り、自分の GPU メモリに置いておく。"), ""),
        (t("block ids, host, port", "ブロック番号、ホスト、ポート"), "p", "r", t("3. When prefill finishes, its response carries where the KV is: block ids, host and port.", "3. prefill が終わると、KV のブロック番号、ホスト、ポートを応答で返す。"), ""),
        (t("request + KV location", "リクエストと在りか"), "r", "d", t("4. Only now does the router send the request to decode, with that location.", "4. ここで初めて、Router が在りかを付けてリクエストを decode に送る。"), ""),
        (t("allocate blocks", "ブロックを確保"), "d", "d", t("5. Decode reserves free blocks for the KV.", "5. decode が KV を受け取るブロックを確保する。"), ""),
        ("READ", "d", "p", t("6. Decode posts a NIXL READ for prefill's blocks.", "6. decode が、prefill のブロックを指定して NIXL の READ を出す。"), ""),
        (t("KV data", "KV のデータ"), "p", "d", t("7. The KV moves from prefill's GPU memory into decode's. With device RDMA read on EFA, prefill's CPU takes no part.", "7. KV が prefill の GPU メモリから decode の GPU メモリへ移る。EFA のデバイスの RDMA read なら、prefill の CPU は関わらない。"), "d"),
        (t("done notification", "完了の通知"), "d", "p", t("8. Decode tells prefill it has read the blocks, and prefill frees them. Decode starts generating.", "8. decode が読み終えたことを prefill に知らせ、prefill はブロックを解放する。decode が生成を始める。"), ""),
    ]
    push = [
        (t("request", "リクエスト"), "r", "p", t("1. The router sends the request to prefill ...", "1. Router は、リクエストを prefill に送り ..."), ""),
        (t("request (same time)", "リクエスト (同時)"), "r", "d", t("2. ... and, at the same time, to decode.", "2. ... 同時に decode にも送る。"), ""),
        (t("compute KV", "KV を計算"), "p", "p", t("3. Prefill starts computing the KV.", "3. prefill が KV の計算を始める。"), ""),
        (t("allocate blocks", "ブロックを確保"), "d", "d", t("4. While prefill computes, decode reserves blocks for the KV.", "4. prefill が計算している間に、decode が KV を受け取るブロックを確保する。"), ""),
        (t("register block ids", "ブロック番号を登録"), "d", "p", t("5. Decode sends prefill the ids of the blocks to write into. When both the KV and this registration are there, prefill starts the transfer.", "5. decode が、書き込んでほしいブロックの番号を prefill に送る。KV とこの登録がそろった時点で、prefill が転送を始める。"), ""),
        (t("WRITE: KV data", "WRITE: KV のデータ"), "p", "d", t("6. Prefill posts a NIXL WRITE into decode's blocks. With device RDMA write on EFA, decode's CPU takes no part in moving the data.", "6. prefill が NIXL の WRITE を出し、decode のブロックに書く。EFA のデバイスの RDMA write なら、データの移動に decode の CPU は関わらない。"), "d"),
        (t("done notification", "完了の通知"), "p", "d", t("7. Decode's NIXL hands the notification to vLLM only after all writes have landed, and decode starts generating. Prefill frees its copy when its own WRITE completes.", "7. すべての書き込みが届いてから、decode の NIXL が通知を vLLM に渡し、decode が生成を始める。prefill は、自分の WRITE の完了を確かめて自分の分を解放する。"), ""),
    ]
    return _seq(("Pull and push: who starts the transfer", "pull と push: 誰が転送を始めるか"), lanes,
                {"pull": pull, "push": push},
                {"pull": t("pull (decode READs)", "pull (decode が READ)"), "push": t("push (prefill WRITEs)", "push (prefill が WRITE)")},
                LANE_INFO)


def read_write():
    lanes = [("p", t("Prefill NIXL", "Prefill の NIXL"), "r2"), ("d", t("Decode NIXL", "Decode の NIXL"), "r1")]
    li = {
        "p": t("<b>Prefill side</b>: vLLM's connector calls NIXL; NIXL's LIBFABRIC backend calls libfabric, whose efa provider drives the EFA device.",
               "<b>prefill 側</b>: vLLM のコネクタが NIXL を呼び、NIXL の LIBFABRIC バックエンドが libfabric を呼ぶ。libfabric の efa provider が EFA のデバイスを動かす。") + src(f"{NX}/plugins/libfabric/libfabric_backend.cpp"),
        "d": t("<b>Decode side</b>: the same stack. The KV blocks are GPU memory registered with NIXL, so the NIC reads and writes them directly with GPUDirect RDMA.",
               "<b>decode 側</b>: 同じ構成。KV のブロックは NIXL に登録した GPU メモリなので、GPUDirect RDMA で NIC が直接読み書きできる。") + src(f"{NX}/utils/libfabric/libfabric_rail.cpp"),
    }
    read = [
        ("fi_read", "d", "p", t("1. Decode's NIXL calls fi_read with the remote address and key of prefill's blocks. With device RDMA read, each call is one request to the NIC.", "1. decode の NIXL が、prefill のブロックのアドレスと、そのメモリに触るための鍵を指定して fi_read を呼ぶ。デバイスの RDMA read なら、1 回の呼び出しが NIC への要求 1 つになる。") + src(f"{NX}/utils/libfabric/libfabric_rail.cpp#L1649-L1656"), ""),
        (t("KV data", "KV のデータ"), "p", "d", t("2. The data returns into decode's memory. Only decode's completion queue reports it; prefill's side sees nothing.", "2. データが decode のメモリに返る。完了を知るのは decode の完了キューだけで、prefill 側には何も上がらない。"), "d"),
        (t("local completion", "自分の側で完了"), "d", "d", t("3. Decode sees the read is complete.", "3. decode が、読み終えたことを知る。"), ""),
        (t("notification (send)", "通知 (send)"), "d", "p", t("4. Because prefill cannot see the read, NIXL sends it a separate message (fi_senddata) after completion.", "4. prefill は読まれたことを知れないので、NIXL が完了の後に fi_senddata で別のメッセージを送る。") + src(f"{NX}/plugins/libfabric/libfabric_backend.cpp#L1690-L1702"), ""),
        (t("free blocks", "ブロックを解放"), "p", "p", t("5. vLLM on prefill gets the notification and frees the blocks.", "5. prefill の vLLM が通知を受け取り、ブロックを解放する。"), ""),
    ]
    write = [
        ("fi_writemsg + imm", "p", "d", t("1. Prefill's NIXL calls fi_writemsg with FI_REMOTE_CQ_DATA: each write carries a small number, the immediate data, holding the transfer id.", "1. prefill の NIXL が FI_REMOTE_CQ_DATA 付きで fi_writemsg を呼ぶ。1 回の書き込みごとに、転送の番号を入れた immediate data という小さな値が付く。") + src(f"{NX}/utils/libfabric/libfabric_rail.cpp#L1559-L1573"), "d"),
        (t("notification (send)", "通知 (send)"), "p", "d", t("2. Right after posting, NIXL sends the notification with the number of writes to expect.", "2. 書き込みを出した直後に、NIXL が「何回書くか」を入れた通知を送る。") + src(f"{NX}/plugins/libfabric/libfabric_backend.cpp#L1665-L1678"), ""),
        (t("count arrivals", "届いた数を数える"), "d", "d", t("3. Each write lands with an entry in decode's completion queue carrying the immediate data. Decode's NIXL counts them per sender and transfer id.", "3. 書き込みが届くたびに、immediate data の入った項目が decode の完了キューに上がる。decode の NIXL が、送り手と転送の番号の組ごとに数える。") + src(f"{NX}/plugins/libfabric/libfabric_backend.cpp#L2252-L2276"), ""),
        (t("hand over notification", "通知を渡す"), "d", "d", t("4. Only when the number of arrived writes reaches the expected count and the notification is in does NIXL give it to vLLM, so vLLM never uses a half-written KV.", "4. 届いた書き込みの数が予定の数に達し、通知も届いたときだけ、NIXL が通知を vLLM に渡す。そのため vLLM は書きかけの KV を使わない。") + src(f"{NX}/plugins/libfabric/libfabric_backend.cpp#L2285-L2300"), ""),
    ]
    return _seq(("NIXL READ and WRITE on libfabric", "libfabric の上の NIXL の READ と WRITE"), lanes,
                {"read": read, "write": write},
                {"read": t("READ (pull)", "READ (pull)"), "write": t("WRITE (push)", "WRITE (push)")}, li)


def timing():
    """When to start sending: three schedules on one time axis (conceptual, not to scale)."""
    keys = ["0", "after", "chunk", "layer"]
    # bars: (row, start%, width%, label, cls)
    C = [(0, 0, 22, "compute"), (0, 22, 22, "compute"), (0, 44, 22, "compute")]
    modes = {
        "after": C + [(1, 66, 24, t("all KV", "KV 全部"), "x")],
        "chunk": C + [(1, 22, 8, "1", "x"), (1, 44, 8, "2", "x"), (1, 66, 8, "3", "x")],
        "layer": [(0, c * 22 + i * 5.5, 5.5, f"L{i+1}", "ly") for c in range(3) for i in range(4)]
                 + [(1, c * 22 + (i + 1) * 5.5, 3, "", "x") for c in range(3) for i in range(4)],
    }
    tok = {"after": 90, "chunk": 74, "layer": 69}
    labels = {"after": t("after the whole prefill", "全部終わってから"), "chunk": t("per chunk", "チャンクごと"), "layer": t("per layer", "層ごと")}
    who = {
        "after": t("<b>After the whole prefill</b>: the KV is sent once every chunk is done. The whole transfer sits between the end of prefill and the first token. vLLM's NixlConnector, pull and push alike, sends at this point.",
                   "<b>全部終わってから</b>: すべてのチャンクを計算し終えてから KV を送る。転送の全体が、prefill の終わりと最初のトークンの間に入る。vLLM の NixlConnector は、pull でも push でもこの時点で送る。") + src(f"{VL}/nixl/connector.py#L323-L335"),
        "chunk": t("<b>Per chunk</b>: with chunked prefill, the KV of each finished chunk is sent while the next chunk is computed. If each transfer ends during the next chunk, only the last chunk's transfer is left before the first token. SGLang's prefill sends this way once decode has registered. For vLLM, an RFC and an unmerged PR propose it as of 2026-11-27.",
                   "<b>チャンクごと</b>: chunked prefill で、終わったチャンクの KV を、次のチャンクを計算している間に送る。各転送が次のチャンクの計算の間に終われば、最初のトークンの前に残るのは最後のチャンクの転送だけになる。SGLang の prefill は、decode の登録が済んでいればこの形で送る。vLLM では、2026 年 11 月 27 日の時点で提案と取り込み前の PR の段階にある。") + src(f"{SG}/prefill.py#L1414-L1420"),
        "layer": t("<b>Per layer</b>: the KV of each layer is sent as soon as that layer is computed. If each transfer keeps up, only the last layer's transfer is left. vLLM calls a connector function after each layer, and LMCache's connector has a layer-wise save option; whether it sends KV to decode layer by layer in disaggregated mode is not confirmed.",
                   "<b>層ごと</b>: 層を 1 つ計算するたびに、その層の KV を送る。転送が計算に追いつけば、残るのは最後の層の転送だけになる。vLLM は層ごとにコネクタの関数を呼び、LMCache のコネクタは層ごとに保存する設定を持つ。分離推論で層ごとに decode へ送れるかは確かめていない。") + src(f"{VL}/lmcache_connector.py#L169-L199"),
    }
    info = {"0": t("Pick when to send. The hooked line under the transfers is the transfer time left before the first token.", "送り始める時点を選ぶ。転送の下のかぎ形の線が、最初のトークンの前に残る転送の時間。")}
    info.update({k: who[k] for k in modes})
    rows = [t("prefill compute", "prefill の計算"), t("KV transfer", "KV の転送")]
    body_modes = ""
    for m, bars in modes.items():
        bs = ""
        for row, s, w, lab, *c in bars:
            cls = c[0] if c else "cp"
            bs += f'<span class="br {cls} rw{row}" style="left:{s}%;width:{w}%">{lab}</span>'
        tl = tok[m]
        bs += "".join(f'<span class="chl" style="left:{c*22}%;width:22%">chunk {c+1}</span>' for c in range(3))
        bs += f'<span class="gap" style="left:66%;width:{tl-66}%"></span><span class="tk{' lf2' if tl > 80 else ''}" style="left:{tl}%">{t("first token", "最初のトークン")}</span>'
        body_modes += f'<div class="tl md md-{m}">{bs}</div>'
    body = (frame_inputs(radios("mo", list(modes)) + radios("s", keys)) + '<div class="zr">'
            + bar("When to start sending the KV", "KV を送り始める時点")
            + '<div class="ctl">' + "".join(f'<label class="pill pm-{m}" for="mo-{m}">{labels[m]}</label>' for m in modes) + "</div>"
            + '<div class="gr"><div class="rn">' + "".join(f"<span>{r}</span>" for r in rows) + '</div><div class="pl">' + body_modes
            + '<span class="cov"></span></div></div>'
            + '<div class="lgd">' + t("conceptual, not to scale", "概念図、縮尺は実際の値ではない") + "</div>"
            + '<div class="ctl" style="margin-top:6px">' + "".join(f'<label class="pill hot b-{m}" for="s-{m}">{t("who sends this way", "この形で送る実装")}: {labels[m]}</label>' for m in modes) + "</div>"
            + info_panel(info) + "</div>")
    css = """
.gr{display:grid;grid-template-columns:22% 1fr;gap:8px;height:120px}
.rn{display:flex;flex-direction:column;justify-content:space-around;font-size:12px;color:var(--mut)}
.pl{position:relative;border-left:1px solid var(--line);border-bottom:1px solid var(--line)}
.md{position:absolute;inset:0;display:none}
.br{position:absolute;height:30px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;
 border:2px solid var(--p2);background:var(--p2-bg);border-radius:5px;text-shadow:0 0 3px #000}
.rw0{top:20px}.rw1{top:66px}
.chl{position:absolute;top:2px;height:14px;border-top:1px solid var(--mut);font-size:10px;color:var(--mut);text-align:center;line-height:14px}
.br.ly{border-color:var(--p2);border-style:dotted}
.br.x{border-color:var(--p4);background:var(--p4-bg)}
.gap{position:absolute;top:100px;height:10px;border:2px solid var(--hi);border-top:none}
.tk.lf2{border-left:none;border-right:2px dashed var(--p1);transform:translateX(-100%);padding:0 3px 0 0}.tk{position:absolute;top:18px;bottom:0;border-left:2px dashed var(--p1);font-size:11px;color:var(--p1);padding-left:3px;white-space:nowrap}
.tk i{display:none}
.cov{position:absolute;top:0;bottom:1px;right:0;background:#000;border-left:2px solid var(--fg);animation:cov 8s linear infinite}
@keyframes cov{0%{width:100%}85%,100%{width:0}}
.lgd{font-size:11px;color:var(--mut);text-align:right;margin-top:2px}
#mo-after:checked~.zr .md-after,#mo-chunk:checked~.zr .md-chunk,#mo-layer:checked~.zr .md-layer{display:block}
#mo-after:checked~.zr .pm-after,#mo-chunk:checked~.zr .pm-chunk,#mo-layer:checked~.zr .pm-layer{background:var(--fg);color:#000}
@media (max-width:520px){.gr{grid-template-columns:24% 1fr}.br{font-size:9.5px}.tk{font-size:9.5px}}
""" + select_css(keys)

    still = """.cov{display:none}"""
    return snippet(body, css, still)


def overview():
    keys = ["0", "r", "p", "d", "kv", "nixl", "lf", "efa", "q1", "q2", "q3"]
    info = {
        "0": t("Click a box or a numbered question.", "箱や番号の付いた問いを押す。"),
        "r": LANE_INFO["r"], "p": LANE_INFO["p"], "d": LANE_INFO["d"],
        "kv": t("<b>KV cache</b>: the attention keys and values of every token so far. Decode reads it at every step instead of recomputing the prompt, so it must sit in decode's GPU memory before the first output token.",
                "<b>KV キャッシュ</b>: これまでの各トークンの attention の key と value。Decode はプロンプトを計算し直す代わりに毎ステップこれを読むので、最初の出力トークンの前に decode の GPU メモリに置かれている必要がある。"),
        "nixl": t("<b>NIXL</b>, the NVIDIA Inference Xfer Library: a library that moves data between the memory of two processes. Its two operations are READ and WRITE, named from the side that calls them; the actual sending is done by a backend plugin such as UCX or LIBFABRIC.",
                  "<b>NIXL</b>: NVIDIA Inference Xfer Library の略。2 つのプロセスのメモリの間でデータを運ぶライブラリ。操作は READ と WRITE の 2 つで、呼んだ側から見た名前になっている。実際の送受信は UCX や LIBFABRIC などのバックエンドのプラグインが受け持つ。") + src("github.com/ai-dynamo/nixl"),
        "lf": t("<b>libfabric</b>: a common API in front of network drivers called providers. NIXL's LIBFABRIC backend uses it; the efa provider drives EFA, the shm provider handles peers on the same node, and the tcp provider uses sockets.",
                "<b>libfabric</b>: provider と呼ぶネットワークのドライバの前に立つ共通の API。NIXL の LIBFABRIC バックエンドがこれを使う。efa provider が EFA を、shm provider が同じノードの相手を、tcp provider がソケットを受け持つ。") + src("github.com/ofiwg/libfabric"),
        "efa": t("<b>EFA</b>, the Elastic Fabric Adapter: the network device of EC2 for RDMA. With GPUDirect RDMA it reads and writes GPU memory directly. Whether it can do RDMA read and RDMA write in hardware depends on the instance type.",
                 "<b>EFA</b>: Elastic Fabric Adapter の略。EC2 の RDMA 用のネットワークのデバイス。GPUDirect RDMA で GPU メモリを直接読み書きする。RDMA read と RDMA write をハードウェアでできるかは、インスタンスの種類で決まる。") + src("docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html"),
        "q1": t("<b>1. Who starts the transfer</b>: decode READs the KV from prefill (pull), or prefill WRITEs it into decode (push).", "<b>1. 誰が転送を始めるか</b>: decode が prefill から READ する pull か、prefill が decode に WRITE する push か。"),
        "q2": t("<b>2. When to start sending</b>: after the whole prefill, after each chunk, or after each layer.", "<b>2. いつから送るか</b>: prefill が全部終わってから、チャンクごと、層ごと。"),
        "q3": t("<b>3. Which path carries it</b>: device RDMA on EFA, an emulation by the efa provider when device RDMA cannot be used, shared memory on the same node, or TCP.", "<b>3. どの経路で運ぶか</b>: EFA のデバイスの RDMA、デバイスの RDMA で出せないときに efa provider が代わりに行う模倣、同じノードの共有メモリ、TCP。"),
    }

    def inst(k, name, role):
        return (f'<div class="inst"><label for="s-{k}" class="box hot {role} ih b-{k}"><span class="nm">{name}</span><span class="q">i</span></label>'
                + f'<label for="s-nixl" class="lay hot b-nixl">NIXL</label><label for="s-lf" class="lay hot b-lf">libfabric: efa / shm / tcp</label>'
                + f'<label for="s-efa" class="lay hot b-efa">{t("EFA device", "EFA のデバイス")}</label>'
                + f'<label for="s-kv" class="box hot r4 mem b-kv">{t("GPU memory: KV blocks", "GPU メモリ: KV のブロック")}</label></div>')
    req = t("request", "リクエスト")
    body = (frame_inputs(radios("s", keys)) + '<div class="zr">' + bar("One KV transfer, three questions", "1 回の KV の転送と 3 つの問い")
            + '<div class="top"><label for="s-r" class="box hot r3 rt b-r"><span class="nm">Router</span><span class="q">i</span></label></div>'
            + f'<div class="rq"><span class="ra l">&#8601; {req}</span><label for="s-q1" class="qq hot b-q1">1 ' + t("who starts the transfer?", "誰が転送を始める?") + f'</label><span class="ra r">{req} &#8600;</span></div>'
            + '<div class="mid">' + inst("p", "Prefill", "r2")
            + '<div class="wire"><label for="s-q2" class="qq hot b-q2">2 ' + t("when to start?", "いつから送る?") + '</label>'
            + '<div class="ln"><i></i><i class="b2"></i></div>'
            + '<label for="s-q3" class="qq hot b-q3">3 ' + t("which path?", "どの経路?") + '</label></div>'
            + inst("d", "Decode", "r1") + "</div>"
            + '<div class="legend"><i class="blk"></i> ' + t("KV cache moving from prefill to decode", "prefill から decode へ移る KV キャッシュ") + "</div>"
            + info_panel(info) + "</div>")
    css = """
.top{display:flex;justify-content:center;margin-bottom:4px}.rt{padding:6px 30px}
.rq{display:grid;grid-template-columns:30% 1fr 30%;align-items:center;gap:6px;margin-bottom:6px}
.ra{font-size:12px;color:var(--mut);border-top:2px dashed var(--fg);padding-top:2px}.ra.l{text-align:left}.ra.r{text-align:right}
.mid{display:grid;grid-template-columns:34% 1fr 34%;align-items:end;gap:6px}
.inst{display:flex;flex-direction:column;gap:4px}
.ih{padding:6px 10px}
.lay{display:block;text-align:center;border:1px solid var(--line);border-radius:6px;padding:2px;font-size:12px;background:var(--card);cursor:pointer}
.mem{padding:6px;text-align:center;font-size:12px;font-weight:700}
.wire{display:flex;flex-direction:column;align-items:stretch;gap:6px;padding-bottom:6px}
.ln{height:4px;background:var(--line);position:relative}
.ln i{position:absolute;top:-6px;width:22px;height:16px;background:var(--p4-bg);border:1px solid var(--p4);animation:mv 2.4s linear infinite}
.ln i.b2{animation-delay:-1.2s}
@keyframes mv{0%{left:0;opacity:0}10%,90%{opacity:1}100%{left:calc(100% - 22px);opacity:0}}
.qq{display:block;text-align:center;font-size:12px;font-weight:700;border:2px dashed var(--hi);border-radius:999px;padding:2px 6px;color:var(--hi);cursor:pointer;background:#000}
@media (max-width:520px){.qq,.lay,.mem{font-size:10.5px}.mid{grid-template-columns:36% 1fr 36%}}
""" + select_css(keys)
    still = """.ln::after{content:"";position:absolute;right:-8px;top:-6px;border:8px solid transparent;border-left-color:var(--fg)}
.ln i{left:20%;opacity:1}
.ln i.b2{left:60%}"""
    return snippet(body, css, still)


def paths():
    """Static matrix: what one NIXL READ / WRITE becomes on each libfabric path. Exported as PNG."""
    cols = [("EFA, device RDMA", "p5en etc."), ("EFA, emulated write", "p4d, p4de, or unmet conditions"), ("shm provider", "same node"), ("tcp provider", "TCP transport")]
    # each cell: list of (direction 'r' caller->peer or 'l' peer->caller, kind 'c' control/'d' data, label), note
    R = "r"; L = "l"
    read = [
        ([(R, "c", "RDMA read (NIC)"), (L, "d", "KV")], "peer CPU idle"),
        ([(R, "c", "RDMA read (NIC)"), (L, "d", "KV")], "peer CPU idle"),
        ([(L, "d", "caller copies directly")], "if the fast-path conditions hold"),
        ([(R, "c", "read request"), (L, "d", "response + KV")], "peer software replies"),
    ]
    write = [
        ([(R, "d", "RDMA write + imm")], "peer CQ gets an entry"),
        ([(R, "c", "write request"), (L, "c", "RDMA read (NIC)"), (R, "d", "KV")], "one of the emulations"),
        ([(R, "c", "request to peer"), (R, "d", "peer process copies")], "imm data: no direct copy"),
        ([(R, "d", "1 message with KV")], "imm data rides in the header"),
    ]

    def cell(items, note):
        h = 30 * len(items) + 8
        svg = f'<svg viewBox="0 0 200 {h}" class="cs">'
        svg += f'<line x1="18" y1="0" x2="18" y2="{h}" class="lf" /><line x1="182" y1="0" x2="182" y2="{h}" class="lf" />'
        for i, (d, k, lab) in enumerate(items):
            y = 22 + 30 * i
            x1, x2 = (18, 176) if d == R else (182, 24)
            head = f'<path d="M{x2} {y-5} L{x2 + (6 if d == R else -6)} {y} L{x2} {y+5} Z" class="{'chd' if k == 'c' else 'dh'}" />'
            svg += f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="{k}" />{head}<text x="100" y="{y-6}" class="tl">{lab}</text>'
        svg += "</svg>"
        return f'<div class="cell">{svg}<div class="nt">{note}</div></div>'

    head = "".join(f'<div class="ch box r3"><b>{a}</b><span>{b}</span></div>' for a, b in cols)
    rr = "".join(cell(*c) for c in read)
    ww = "".join(cell(*c) for c in write)
    body = (frame_inputs() + '<div class="zr">' + bar("What one NIXL READ or WRITE becomes", "1 回の NIXL の READ と WRITE の中身")
            + '<div class="mx"><div></div>' + head
            + '<div class="rh box r1"><b>READ</b><span>caller = decode</span></div>' + rr
            + '<div class="rh box r2"><b>WRITE</b><span>caller = prefill</span></div>' + ww + "</div>"
            + '<div class="lgd2"><span class="k1"></span> control &nbsp; <span class="k2"></span> data &nbsp; left line = caller, right line = peer</div>'
            + "</div>")
    css = """
.mx{display:grid;grid-template-columns:13% repeat(4,1fr);gap:6px;align-items:stretch}
.ch{padding:5px;text-align:center;display:flex;flex-direction:column}.ch span,.rh span{font-size:11px;color:var(--mut)}
.rh{padding:6px;display:flex;flex-direction:column;justify-content:center;text-align:center}
.cell{border:1px solid var(--line);border-radius:8px;background:var(--card);padding:4px 4px 6px;display:flex;flex-direction:column;justify-content:space-between}
.cs{width:100%;display:block}
.lf{stroke:var(--mut);stroke-width:1.5}
.c{stroke:var(--fg);stroke-width:2;stroke-dasharray:5 4}.ch2{fill:var(--fg)}
.ch,.rh{font-size:13px}
.d{stroke:var(--p4);stroke-width:6}
.dh{fill:var(--p4)}.chh,.ch_{fill:var(--fg)}
.tl{fill:var(--fg);font-size:12px;text-anchor:middle;paint-order:stroke;stroke:#000;stroke-width:3px}
.nt{font-size:11px;color:var(--mut);text-align:center;margin-top:2px}
.lgd2{font-size:11px;color:var(--mut);margin-top:8px}
.lgd2 span{display:inline-block;width:26px;vertical-align:middle}
.k1{border-top:2px dashed var(--fg)}.k2{border-top:6px solid var(--p4)}
"""
    css = css.replace(".chh,.ch_{fill:var(--fg)}", "")
    css += ".chd{fill:var(--fg)}"
    return snippet(body, css, "")
