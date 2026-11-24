"""Core of the Zenn html-embed figure kit (v2).

Every figure gets the same frame: a title, an EN / 日本語 switch (English by default), a Stop switch,
the drawing, and an info panel that shows the basics of whatever component is clicked. Zenn runs the
block without JavaScript, so all of it is CSS: radio and checkbox inputs placed as siblings of the
figure body (.zr) and :checked ~ selectors.

Stop: checking #zs removes every animation and applies the figure's STATIC rules, which put the
drawing in its complete, still state (the picture you would draw as a static image) so readers can
copy it. prefers-reduced-motion applies the same still state.

Skins: the colours, fonts and line feel come from a skin. "zenn-dark" is the default; the other six
follow review-html/packs/figstyles (excalidraw-sketch, illustrated-flat, whiteboard-sketch,
academic-serif, corporate-technical, matplotlib-xkcd), re-coloured for the black background. Roles,
not colours, are what figures use: p1 primary (diagonal hatch), p2 secondary (cross hatch),
p3 tertiary (dotted grid), p4 accent (dots), bad (dashed double line). Each role has a border colour,
a fill and a pattern, so roles stay distinguishable without colour.
"""

SKINS = {
    "zenn-dark": dict(font='"Hiragino Sans","Noto Sans JP","Segoe UI",system-ui,sans-serif', ink="#f2f2f5", mut="#a2a2ab",
                      card="#111317", line="#3c3f46", radius="12px", bw="2px", hand="0",
                      p1=("#3bd16f", "#0f2a19", "#16402a"), p2=("#4aa3ff", "#0d1b2b", "#14304d"),
                      p3=("#fbd332", "#221d06", "#3a3210"), p4=("#ff9e4a", "#2a1708", "#4a2a10"),
                      bad=("#ff6fb1", "#2c0d1d", "#4a1830"), hi="#fbd332"),
    "excalidraw-sketch": dict(font='Virgil,"Comic Sans MS","Segoe Print","Hiragino Maru Gothic ProN",cursive', ink="#f1f1f1", mut="#b8b8b8",
                              card="#121212", line="#5a5a5a", radius="14px 4px 12px 5px / 5px 13px 4px 12px", bw="2.5px", hand="1",
                              p1=("#a5d8ff", "#14242f", "#1d3646"), p2=("#b2f2bb", "#132619", "#1d3a25"),
                              p3=("#ffec99", "#2a2612", "#403a1c"), p4=("#ffc9c9", "#2c1717", "#442424"),
                              bad=("#ff8787", "#2c1212", "#4a1d1d"), hi="#ff6b6b"),
    "illustrated-flat": dict(font='"Helvetica Neue",Arial,"Hiragino Sans",sans-serif', ink="#f4f4f4", mut="#b0b0b0",
                             card="#141414", line="#444", radius="22px", bw="0px", hand="0",
                             p1=("#6aa9ff", "#1a2a40", "#22364f"), p2=("#69db7c", "#18301d", "#1f3d26"),
                             p3=("#ffa94d", "#3a2614", "#4a3119"), p4=("#f783ac", "#3a1726", "#4a1e31"),
                             bad=("#ff6b6b", "#3a1414", "#4a1a1a"), hi="#f783ac"),
    "whiteboard-sketch": dict(font='"Marker Felt","Bradley Hand","Comic Sans MS","Hiragino Maru Gothic ProN",cursive', ink="#f7f7f2", mut="#bdbdb4",
                              card="#0c0c0c", line="#6a6a66", radius="6px 3px 7px 2px", bw="3.5px", hand="1",
                              p1=("#f7f7f2", "#0c0c0c", "#1a1a18"), p2=("#f7f7f2", "#0c0c0c", "#1a1a18"),
                              p3=("#f7f7f2", "#0c0c0c", "#1a1a18"), p4=("#17b2d1", "#06222a", "#0b3540"),
                              bad=("#17b2d1", "#06222a", "#0b3540"), hi="#17b2d1"),
    "academic-serif": dict(font='Georgia,"Times New Roman","Hiragino Mincho ProN",serif', ink="#ececec", mut="#a8a8a8",
                           card="#101010", line="#4a4a4a", radius="3px", bw="1.2px", hand="0",
                           p1=("#fde0dd", "#2a1f1f", "#3a2b2b"), p2=("#fa9fb5", "#2e1a20", "#40242c"),
                           p3=("#d9d9d9", "#1c1c1c", "#2a2a2a"), p4=("#c51b8a", "#2a0a1e", "#40102d"),
                           bad=("#c51b8a", "#2a0a1e", "#40102d"), hi="#c51b8a"),
    "corporate-technical": dict(font='"Helvetica Neue",Arial,"Hiragino Sans",sans-serif', ink="#f0f0f0", mut="#9a9a9a",
                                card="#121212", line="#3a3a3a", radius="4px", bw="2px", hand="0",
                                p1=("#76b900", "#152100", "#203300"), p2=("#d0d0d0", "#1a1a1a", "#262626"),
                                p3=("#8fa3b8", "#141b22", "#1e2833"), p4=("#76b900", "#152100", "#203300"),
                                bad=("#ff5f5f", "#2a1010", "#3d1616"), hi="#76b900"),
    "matplotlib-xkcd": dict(font='"Humor Sans","Comic Sans MS","Hiragino Maru Gothic ProN",cursive', ink="#f2f2f2", mut="#b0b0b0",
                            card="#121212", line="#555", radius="12px 6px 10px 7px / 7px 10px 6px 12px", bw="2.6px", hand="1",
                            p1=("#9a7fc7", "#1d1729", "#2a213b"), p2=("#74c3c4", "#122626", "#1b3838"),
                            p3=("#f2d06b", "#2a2410", "#3d3418"), p4=("#f4a3c0", "#2c1820", "#40232f"),
                            bad=("#b5179e", "#28081f", "#3d0c2f"), hi="#b5179e"),
}
DEFAULT_SKIN = "zenn-dark"

PATTERNS = {  # role -> CSS background built from (border, base, stripe)
    "p1": "repeating-linear-gradient(45deg,{b} 0 7px,{s} 7px 12px)",
    "p2": "repeating-linear-gradient(45deg,{b} 0 7px,{s} 7px 9px),repeating-linear-gradient(-45deg,transparent 0 7px,{s} 7px 9px)",
    "p3": "radial-gradient({s} 1.5px,transparent 1.6px) 0 0/8px 8px,{b}",
    "p4": "radial-gradient({s} 2.4px,transparent 2.5px) 0 0/10px 10px,{b}",
    "bad": "repeating-linear-gradient(90deg,{b} 0 6px,{s} 6px 10px)",
}


def skin_css(name):
    k = SKINS[name]
    v = [f"--fg:{k['ink']};--mut:{k['mut']};--card:{k['card']};--line:{k['line']};--rad:{k['radius']};--bw:{k['bw']};--hi:{k['hi']};--font:{k['font']}"]
    for role in ("p1", "p2", "p3", "p4", "bad"):
        bd, base, stripe = k[role]
        v.append(f"--{role}:{bd};--{role}-bg:{PATTERNS[role].format(b=base, s=stripe)}")
    return ".zf{" + ";".join(v) + "}"


BASE_CSS = """
.zf{font:14px/1.55 var(--font);color:var(--fg);background:#000;padding:12px 14px 10px;box-sizing:border-box;position:relative;min-height:470px}
.zf *{box-sizing:border-box}
.zf input{position:absolute;opacity:0;pointer-events:none;width:0;height:0}
.zf code{font-family:Menlo,Consolas,monospace;font-size:.92em}
.bar{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px}
.ttl{font-weight:700;font-size:15px}
.tools{display:flex;gap:4px;flex:none}
.pill{cursor:pointer;border:1px solid var(--line);border-radius:999px;padding:2px 11px;font-size:12px;color:var(--mut);user-select:none;white-space:nowrap;display:inline-block}
.pill:hover{border-color:var(--fg);color:var(--fg)}
#zl-en:checked~.zr .p-en,#zl-ja:checked~.zr .p-ja,#zs:checked~.zr .p-stop{background:var(--fg);color:#000;border-color:var(--fg)}
#zl-en:checked~.zr x-j,#zl-ja:checked~.zr x-e{display:none!important}
.p-stop .on{display:none}#zs:checked~.zr .p-stop .on{display:inline}#zs:checked~.zr .p-stop .off{display:none}
.hint{color:var(--mut);font-size:12px}
.info{border:1px solid var(--line);border-radius:10px;background:var(--card);padding:9px 12px;min-height:92px;margin-top:10px;font-size:13px}
.info>div{display:none}
.info b{font-size:14px}
.src{display:block;margin-top:4px;color:var(--mut);font-size:12px;word-break:break-all}
.src::before{content:"\\2197  "}
.hot{cursor:pointer;transition:transform .2s,box-shadow .2s}
.hot:hover{transform:translateY(-2px);box-shadow:0 0 0 2px var(--fg)}
.box{border:var(--bw) solid var(--p2);border-radius:var(--rad);background:var(--p2-bg);position:relative}
.box.r1{border-color:var(--p1);background:var(--p1-bg)}
.box.r3{border-color:var(--p3);background:var(--p3-bg);border-style:dashed}
.box.r4{border-color:var(--p4);background:var(--p4-bg)}
.box.bad{border-color:var(--bad);background:var(--bad-bg);border-style:double;border-width:calc(var(--bw) + 2px)}
.box.r0{border-color:var(--mut);background:var(--card)}
.nm{font-weight:700;font-size:14px;text-shadow:0 0 3px #000,0 0 3px #000}.sub{font-size:12px;color:var(--fg);opacity:.85;text-shadow:0 0 3px #000,0 0 3px #000}
.q{position:absolute;top:5px;right:7px;width:16px;height:16px;border-radius:50%;border:1px solid currentColor;font-size:11px;line-height:14px;text-align:center;opacity:.75;background:#000}
.dot{display:inline-block;width:10px;height:10px;background:var(--hi);vertical-align:middle}
.blk{display:inline-block;width:20px;height:11px;background:var(--p4-bg);border:1px solid var(--p4);vertical-align:middle}
.legend{font-size:12px;color:var(--mut);margin-top:6px}
.tip{display:none;position:absolute;width:0;height:0;border:6px solid transparent}
@media (max-width:520px){.zf{font-size:13px;padding:10px 10px 8px}.ttl{font-size:14px}.info{font-size:12px;min-height:0;padding:7px 10px;line-height:1.45}.info b{font-size:13px}}
.ctl{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px}
"""

STILL_ALL = "#zs:checked~.zr *,#zs:checked~.zr *::before,#zs:checked~.zr *::after{animation:none!important;transition:none!important}#zs:checked~.zr .q{display:none}"


def t(en, ja):
    return f'<x-e>{en}</x-e><x-j>{ja}</x-j>'


def bar(title_en, title_ja):
    return (f'<div class="bar"><div class="ttl">{t(title_en, title_ja)}</div><div class="tools">'
            '<label class="pill p-stop" for="zs"><span class="off">&#9208; Stop</span><span class="on">&#9654; Play</span></label>'
            '<label class="pill p-en" for="zl-en">EN</label><label class="pill p-ja" for="zl-ja">日本語</label></div></div>')


def radios(name, keys, first=None):
    first = keys[0] if first is None else first
    return "".join(f'<input type="radio" name="{name}" id="{name}-{k}"{" checked" if k == first else ""}>' for k in keys)


import os as _os
# ZK_STILL=1 renders the figure for a PNG: Stop is on and the controls are hidden. Used for figures
# that do not gain from moving (structures, maps, layers); the article embeds the PNG instead.
STILL_EXPORT = _os.environ.get("ZK_STILL") == "1"


def frame_inputs(extra=""):
    zs = " checked" if STILL_EXPORT else ""
    return f'<input type="radio" name="zl" id="zl-en" checked><input type="radio" name="zl" id="zl-ja"><input type="checkbox" id="zs"{zs}>' + extra


def info_panel(items):
    """items: {key: html}. Key '0' is the default text shown before anything is clicked."""
    return '<div class="info">' + "".join(f'<div class="i-{k}">{v}</div>' for k, v in items.items()) + "</div>"


def select_css(keys, group="s"):
    show = ",".join(f"#{group}-{k}:checked~.zr .i-{k}" for k in keys)
    ring = ",".join(f"#{group}-{k}:checked~.zr .b-{k}" for k in keys if k != "0")
    return show + "{display:block}" + (ring + "{box-shadow:0 0 0 3px var(--fg)}" if ring else "")


import re as _re


def _blocks(css):
    """Split CSS into top-level (prelude, body) pairs; body is the text inside the braces."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while depth and k < n:
            depth += {"{": 1, "}": -1}.get(css[k], 0); k += 1
        out.append((css[i:j].strip(), css[j + 1:k - 1]))
        i = k
    return out


def _prune(css, classes, ids):
    """Drop rules whose selectors name a class or id that the figure's HTML never uses, then drop
    keyframes no remaining rule refers to. Zenn counts every character of the block toward the
    article's 80,000-character limit, so the shared BASE_CSS must not ship unused rules."""
    def keep_sel(sel):
        return all(c in classes for c in _re.findall(r"\.([A-Za-z_][\w-]*)", sel)) and \
            all(i in ids for i in _re.findall(r"#([A-Za-z_][\w-]*)", sel))
    def walk(text):
        rules = []
        for pre, body in _blocks(text):
            if pre.startswith("@keyframes"):
                rules.append((pre, body))
            elif pre.startswith("@media"):
                inner = walk(body)
                if inner:
                    rules.append((pre, "".join(f"{p}{{{b}}}" for p, b in inner)))
            else:
                sels = [x for x in pre.split(",") if keep_sel(x)]
                if sels:
                    rules.append((",".join(x.strip() for x in sels), body))
        return rules
    rules = walk(css)
    used = " ".join(b for p, b in rules if not p.startswith("@keyframes"))
    rules = [(p, b) for p, b in rules if not p.startswith("@keyframes") or _re.search(r"\b" + _re.escape(p.split()[1]) + r"\b", used)]
    return "".join(f"{p}{{{b}}}" for p, b in rules)


def _minify(css):
    css = _re.sub(r"\s+", " ", css)
    css = _re.sub(r"\s*([{};,>~])\s*", r"\1", css)
    return css.replace(";}", "}")


def snippet(body, css, still="", skin=DEFAULT_SKIN):
    """One self-contained html-embed block. `still` holds the figure's complete, motionless state."""
    still_rules = STILL_ALL + "\n" + "\n".join(
        f"#zs:checked~.zr {r}" for r in still.strip().splitlines() if r.strip())
    reduced = "@media (prefers-reduced-motion:reduce){.zf *,.zf *::before,.zf *::after{animation:none!important;transition:none!important}" + \
        "\n".join(r for r in still.strip().splitlines() if r.strip()) + "}"
    if STILL_EXPORT:
        css += ".tools,.ctl{display:none}.zf{min-height:0}" + ("" if 'class="all' in body else ".info{display:none}")
    html = f'<div class="zf">{body}</div>'
    classes = set(" ".join(_re.findall(r'class="([^"]*)"', html)).split()) | {"zf", "zr"}
    ids = set(_re.findall(r'id="([^"]+)"', html))
    full = _prune(_minify(f"{skin_css(skin)}{BASE_CSS}{css}\n{still_rules}\n{reduced}"), classes, ids)
    html, full = _mangle(html, full)
    return f"{html}\n<style>{full}</style>\n"


def _short(n):
    a = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = a[n % 52]; n //= 52
    while n:
        out += "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36]; n //= 36
    return out


def _mangle(html, css):
    """Rename every class, id, custom property and keyframes name to the shortest free token, most
    frequent first, in the HTML and the CSS together. The source keeps readable names; only the
    shipped block is short, because Zenn counts every character toward the article limit."""
    from collections import Counter
    cnt = Counter()
    for v in _re.findall(r'class="([^"]*)"', html):
        cnt.update(v.split())
    cnt.update(_re.findall(r'(?:id|for)="([^"]+)"', html))
    cnt.update(m for m in _re.findall(r"url\(#([\w-]+)\)", css + html))
    sel_text = "".join(p for p, _ in _blocks_deep(css))
    cnt.update(_re.findall(r"[.#]([A-Za-z_][\w-]*)", sel_text))
    names = [k for k, _ in cnt.most_common()]
    kf = _re.findall(r"@keyframes ([\w-]+)", css)
    vars_ = Counter(_re.findall(r"--([\w-]+)", css + " ".join(_re.findall(r'style="([^"]*)"', html)))).most_common()
    pool = (n for n in map(_short, range(10**6)) if n not in ("x", ))
    m = {}
    for k in names:
        m.setdefault(("c", k), next(pool))
    for k in kf:
        m.setdefault(("k", k), next(pool))
    for k, _ in vars_:
        m.setdefault(("v", k), next(pool))
    C = lambda k: m.get(("c", k), k)
    html = _re.sub(r'class="([^"]*)"', lambda x: 'class="' + " ".join(C(c) for c in x.group(1).split()) + '"', html)
    html = _re.sub(r'(id|for)="([^"]+)"', lambda x: f'{x.group(1)}="{C(x.group(2))}"', html)
    html = _re.sub(r"url\(#([\w-]+)\)", lambda x: f"url(#{C(x.group(1))})", html)
    html = _re.sub(r'(class|id|for)="([\w-]+)"', r"\1=\2", html)
    html = _re.sub(r'style="([^"]*)"', lambda x: 'style="' + _re.sub(r"--([\w-]+)", lambda y: "--" + m.get(("v", y.group(1)), y.group(1)), x.group(1)) + '"', html)

    def fix_decl(body):
        body = _re.sub(r"url\(#([\w-]+)\)", lambda x: f"url(#{C(x.group(1))})", body)
        body = _re.sub(r"--([\w-]+)", lambda x: "--" + m.get(("v", x.group(1)), x.group(1)), body)
        return _re.sub(r"(animation(?:-name)?:)([^;}]*)", lambda x: x.group(1) + _re.sub(r"[\w-]+", lambda y: m.get(("k", y.group(0)), y.group(0)), x.group(2)), body)

    def fix_sel(sel):
        return _re.sub(r"([.#])([A-Za-z_][\w-]*)", lambda x: x.group(1) + C(x.group(2)), sel)

    def walk(text):
        out = []
        for pre, body in _blocks(text):
            if pre.startswith("@keyframes"):
                name = pre.split()[1]
                out.append(f"@keyframes {m.get(('k', name), name)}{{{body}}}")
            elif pre.startswith("@media"):
                out.append(f"{pre}{{{walk(body)}}}")
            else:
                out.append(f"{fix_sel(pre)}{{{fix_decl(body)}}}")
        return "".join(out)
    return html, walk(css)


def _blocks_deep(css):
    out = []
    for pre, body in _blocks(css):
        if pre.startswith("@media"):
            out += _blocks_deep(body)
        elif not pre.startswith("@keyframes"):
            out.append((pre, body))
    return out
