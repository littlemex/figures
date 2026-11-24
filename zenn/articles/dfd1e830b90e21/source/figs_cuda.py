"""Figures for the CUDA PTX / runtime article."""
from core import t, bar, radios, frame_inputs, info_panel, snippet, select_css

import json as _json, pathlib as _pl
_J = _json.load(open(_pl.Path.home() / "tmp/cuda/article/stats.json")); _S = _J["stats"]
def M(lab, field, fmt=".3f", stat="med"):
    return format(_S[lab][field][stat], fmt)
DIFF = format(_S["ptx80_nocache"]["launch1"]["med"] - _S["sass89"]["launch1"]["med"], ".1f")

NVCC = "docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html"
PLAT = "docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html"
PTXD = "docs.nvidia.com/cuda/parallel-thread-execution/index.html"
ENV = "docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html"
LAZY = "docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/lazy-loading.html"
src = lambda u: f'<span class="src">{u}</span>'


def _graph(VW, VH, nodes, edges, bands="", over=""):
    """nodes: {key: (x, y, w, h, name_html, sub_html, role)} in viewBox units; edges: {key: svg path d}.
    Boxes are HTML labels placed in % over an SVG that only draws the edges, so the kit's patterned
    boxes and the EN/JA switch work inside the drawing."""
    pct = lambda v, tot: f"{v / tot * 100:.2f}%"
    svg = (f'<svg viewBox="0 0 {VW} {VH}"><defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto"><path d="M0 0L10 5L0 10z"/></marker></defs>'
           + bands + "".join(f'<path class="e eg-{k}" d="{d}"/>' for k, d in edges.items()) + "</svg>")
    boxes = "".join(
        f'<label for="s-{k}" class="box hot nd b-{k} {r}" style="left:{pct(x, VW)};top:{pct(y, VH)};width:{pct(w, VW)};height:{pct(h, VH)}">'
        f'<span class="nm">{nm}</span>' + (f'<span class="sub">{sub}</span>' if sub else "") + "</label>"
        for k, (x, y, w, h, nm, sub, r) in nodes.items())
    top = f'<svg class="ov" viewBox="0 0 {VW} {VH}">{over}</svg>' if over else ""
    return f'<div class="sm">{svg}{boxes}{top}</div>'


GRAPH_CSS = """
.sm{position:relative;width:100%}.sm svg{display:block;width:100%;height:auto}.sm svg.ov{position:absolute;inset:0;height:100%;pointer-events:none;z-index:3}
.nd{position:absolute;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:2px 3px;line-height:1.2;overflow:hidden}
.nd .nm{font-size:12.5px}.nd .sub{font-size:10.5px}
.e{fill:none;stroke:var(--fg);stroke-width:2;marker-end:url(#ah);opacity:.75}
#ah path{fill:var(--fg)}
.bandt{fill:var(--mut);font:700 12px Menlo,Consolas,monospace}
.band{fill:none;stroke:var(--line);stroke-dasharray:4 4}
@media (max-width:520px){.nd .nm{font-size:9.5px}.nd .sub{display:none}.bandt{font-size:15px}}
"""


def overview(skin="zenn-dark"):
    VW, VH = 720, 330
    N = {
        "src": (10, 38, 100, 46, "vadd.cu", t("CUDA C++", "CUDA C++"), "r1"),
        "cicc": (130, 38, 100, 46, "cicc", t("C++ → PTX", "C++ → PTX"), ""),
        "ptx": (250, 38, 100, 46, "PTX", t("virtual ISA", "仮想の命令"), "r1"),
        "ptxas": (370, 38, 100, 46, "ptxas", t("PTX → SASS", "PTX → SASS"), ""),
        "cubin": (490, 38, 100, 46, "cubin", t("SASS for sm_89", "sm_89 の SASS"), "r1"),
        "exe": (610, 38, 100, 46, t("executable", "実行ファイル"), t("fatbin inside", "fatbin を同梱"), "r1"),
        "app": (10, 170, 120, 50, t("host code", "CPU 側のコード"), "vadd<<<…>>>", "r1"),
        "rt": (160, 170, 130, 50, "CUDA Runtime", t("statically linked", "静的リンク"), ""),
        "drv": (320, 170, 130, 50, "CUDA Driver", "libcuda.so.1", "r3"),
        "kd": (470, 170, 135, 50, t("driver in the OS kernel", "OS カーネル内のドライバー"), "/dev/nvidia*", "r3"),
        "gpu": (630, 170, 80, 50, "GPU", "L4 · sm_89", "r4"),
        "jit": (300, 262, 165, 50, t("PTX JIT compiler", "PTX の JIT コンパイラ"), "libnvidia-ptxjitcompiler", "r3"),
        "cache": (490, 262, 150, 50, "compute cache", "~/.nv/ComputeCache", "r1"),
    }
    E = {
        "b1": "M110 61 L128 61", "b2": "M230 61 L248 61", "b3": "M350 61 L368 61", "b4": "M470 61 L488 61", "b5": "M590 61 L608 61", "bp": "M300 84 L300 97 L640 97 L640 86",
        "x": "M660 84 L660 120 L70 120 L70 168",
        "r1": "M130 195 L158 195", "r2": "M290 195 L318 195", "r3": "M450 195 L468 195", "r4": "M605 195 L628 195",
        "j1": "M370 220 L370 260", "j2": "M400 260 L400 222", "j3": "M465 287 L488 287",
    }
    bands = ('<text class="bandt" x="10" y="24">BUILD · CUDA Toolkit (nvcc -arch=sm_89)</text>'
             '<text class="bandt" x="84" y="156">RUN · CUDA Runtime + NVIDIA Driver</text>'
             '<text class="bandt" x="200" y="245">no usable cubin →</text><rect class="band" x="4" y="6" width="712" height="102" rx="8"/><rect class="band" x="4" y="138" width="712" height="186" rx="8"/>')
    toks = "".join(f'<circle class="tk tk{i}" r="6" style="offset-path:path(\'{d}\')"/>' for i, d in enumerate(
        ["M60 61 L660 61 L660 120 L70 120 L70 195 L665 195", "M370 195 L370 287 L400 287 L400 195 L665 195"]))
    graph = _graph(VW, VH, N, E, bands)
    info = {
        "0": t("Top: what nvcc makes at build time. Bottom: what runs when the program starts. Click a box.", "上はビルドのときに nvcc が作るもの、下はプログラムを動かすときに働くもの。箱を押すと説明が出る。"),
        "src": t("<b>vadd.cu</b>: a CUDA C++ file. One file holds both the CPU code (host code) and the GPU function (kernel). nvcc splits the two and compiles each.", "<b>vadd.cu</b>: CUDA C++ のファイル。CPU で動くコード (ホストのコード) と GPU で動く関数 (カーネル) が 1 つのファイルに入っている。nvcc が 2 つに分けて、それぞれをコンパイルする。") + src(NVCC + "#the-cuda-compilation-trajectory"),
        "cicc": t("<b>cicc</b>: the command nvcc calls to turn the kernel's C++ into PTX. You normally do not run it yourself.", "<b>cicc</b>: nvcc の中で、カーネルの C++ を PTX に変える段。nvcc が呼ぶもので、自分で直接は動かさない。"),
        "ptx": t("<b>PTX</b> (Parallel Thread Execution): a virtual instruction set for NVIDIA GPUs, a layer above the real GPU's machine code. PTX for compute capability 8.9 is called compute_89; separately, the PTX ISA itself has versions (.version 9.0). It is text you can open and read. nvcc puts it into the executable as well as the cubin.", "<b>PTX</b> (Parallel Thread Execution): NVIDIA の GPU 向けの仮想の命令セットで、実際の GPU の機械語の一段上にある層。compute capability 8.9 向けの PTX を compute_89 と呼ぶ。これとは別に PTX ISA 自体のバージョン (.version 9.0) がある。テキストなので開いて読める。nvcc は cubin と一緒に実行ファイルに入れる。") + src(PLAT + "#parallel-thread-execution-ptx"),
        "ptxas": t("<b>ptxas</b>: the assembler that turns PTX into SASS for one SM version such as sm_89. It picks real instructions and assigns real registers.", "<b>ptxas</b>: PTX を、sm_89 のような 1 つの SM のバージョン向けの SASS に変えるアセンブラ。実際の命令を選び、本物のレジスタを割り当てる。"),
        "cubin": t("<b>cubin</b> (CUDA binary): a binary file that holds SASS, the machine code for one SM version such as sm_89. A compatible GPU runs it as is, without JIT compilation.", "<b>cubin</b> (CUDA binary): sm_89 のような 1 つの SM のバージョン向けの機械語 (SASS) を入れたバイナリのファイル。互換のある GPU が、JIT コンパイルなしでそのまま実行できる。") + src(PLAT + "#cubins-and-fatbins"),
        "exe": t("<b>Executable</b>: CPU code plus a <b>fatbin</b>, a container that can hold several cubins and PTX. Here it sits in the ELF section .nv_fatbin.", "<b>実行ファイル</b>: CPU のコードと、<b>fatbin</b> (複数の cubin と PTX を入れられる入れ物) を持つ。ここでは ELF の .nv_fatbin というセクションに入っている。") + src(PLAT + "#cubins-and-fatbins"),
        "app": t("<b>Host code</b>: the CPU part of the program. nvcc rewrote vadd<<<…>>> into calls to the CUDA Runtime.", "<b>CPU 側のコード</b>: プログラムの CPU の部分。vadd<<<…>>> は nvcc によって CUDA Runtime の呼び出しに書き換えられている。"),
        "rt": t("<b>CUDA Runtime</b> (cudart): the library behind cudaMalloc and <<<…>>>. It ships with the CUDA Toolkit and nvcc links it statically by default, so it is inside the executable. It is built on the Driver API.", "<b>CUDA Runtime</b> (cudart): cudaMalloc や <<<…>>> を受け持つライブラリ。CUDA Toolkit に付属し、nvcc は既定で静的にリンクするので、実行ファイルの中に入っている。中では Driver API を呼ぶ。") + src(PLAT + "#cuda-runtime-api-and-cuda-driver-api"),
        "drv": t("<b>CUDA Driver</b> (libcuda.so.1): the library of the NVIDIA driver that CUDA programs call. It comes with the driver, not the toolkit. It creates contexts, loads modules, picks the cubin or JIT-compiles the PTX, and launches kernels.", "<b>CUDA Driver</b> (libcuda.so.1): NVIDIA ドライバーのうち、CUDA のプログラムが呼ぶライブラリ。Toolkit ではなくドライバーに付属する。コンテキストを作り、モジュールを読み込み、cubin を選ぶか PTX を JIT コンパイルし、カーネルを起動する。") + src(PLAT + "#cuda-toolkit-and-nvidia-driver"),
        "kd": t("<b>OS-side driver</b>: the part of the NVIDIA driver inside the OS kernel. libcuda talks to it through the device files /dev/nvidiactl, /dev/nvidia0 and /dev/nvidia-uvm.", "<b>OS 側のドライバー</b>: NVIDIA ドライバーのうち、OS のカーネルの中で動く部分。libcuda は /dev/nvidiactl、/dev/nvidia0、/dev/nvidia-uvm というデバイスファイルを通して話す。"),
        "gpu": t("<b>GPU</b>: NVIDIA L4 here, compute capability 8.9 (sm_89), 58 SMs. An SM (streaming multiprocessor) is the unit that runs threads.", "<b>GPU</b>: ここでは NVIDIA L4。compute capability は 8.9 (sm_89) で、SM が 58 個ある。SM (streaming multiprocessor) はスレッドを実行する単位。") + src(PLAT + "#compute-capability-and-streaming-multiprocessor-versions"),
        "jit": t("<b>PTX JIT compiler</b>: a library of the driver. When no usable cubin is found, the driver compiles the PTX into SASS for this GPU at run time.", "<b>PTX の JIT コンパイラ</b>: ドライバーのライブラリ。使える cubin が無いとき、ドライバーが実行時に PTX をこの GPU の SASS にコンパイルする。") + src(PLAT + "#just-in-time-compilation"),
        "cache": t("<b>Compute cache</b>: where the driver keeps SASS it JIT-compiled, so the next run skips the compilation. On Linux the default is ~/.nv/ComputeCache; it is invalidated when the driver is upgraded.", "<b>compute cache</b>: ドライバーが JIT コンパイルした SASS を置く場所。次の実行ではコンパイルを省く。Linux の既定は ~/.nv/ComputeCache で、ドライバーを更新すると無効になる。") + src(ENV + "#cuda-cache-path"),
    }
    keys = ["0"] + list(N)
    legend = t('<i class="lg r1"></i> file &nbsp; <i class="lg"></i> CUDA Toolkit &nbsp; <i class="lg r3"></i> NVIDIA Driver &nbsp; <i class="lg r4"></i> hardware',
               '<i class="lg r1"></i> ファイル &nbsp; <i class="lg"></i> CUDA Toolkit &nbsp; <i class="lg r3"></i> NVIDIA ドライバー &nbsp; <i class="lg r4"></i> ハードウェア')
    body = (frame_inputs(radios("s", keys)) + '<div class="zr">' + bar("From vadd.cu to the GPU", "vadd.cu から GPU まで")
            + graph + f'<div class="legend">{legend}</div>' + info_panel(info) + "</div>")
    sel = "\n".join(f"#s-{k}:checked~.zr .i-{k}{{display:block}}" + (f"#s-{k}:checked~.zr .b-{k}{{box-shadow:0 0 0 3px var(--fg)}}" if k != "0" else "") for k in keys)
    css = GRAPH_CSS + """
.tk{fill:var(--hi);offset-rotate:0deg;animation:run 7s ease-in-out infinite}
.tk1{animation-name:run2}
@keyframes run{0%{offset-distance:0%;opacity:0}5%{opacity:1}70%{offset-distance:100%;opacity:1}75%,100%{offset-distance:100%;opacity:0}}
@keyframes run2{0%,62%{offset-distance:0%;opacity:0}66%{opacity:1}95%{offset-distance:100%;opacity:1}100%{offset-distance:100%;opacity:0}}
.lg{display:inline-block;width:18px;height:11px;vertical-align:middle;border:2px solid var(--p2);background:var(--p2-bg)}
.lg.r1{border-color:var(--p1);background:var(--p1-bg)}.lg.r3{border-color:var(--p3);background:var(--p3-bg);border-style:dashed}.lg.r4{border-color:var(--p4);background:var(--p4-bg)}
""" + sel
    still = """.tk{offset-distance:38%!important;opacity:1!important}
.tk1{offset-distance:12%!important}"""
    return snippet(body, css, still, skin)


def _stepper2(title, lanes, steps, legend="", skin="zenn-dark", modes=None, lane_info=None):
    """Sequence diagram walked one message at a time. lanes: [(key, label, role)] placed at 10/50/90 %.
    steps: [(label, from, to, caption, kind)] kind '' = control message, 'd' = data.
    modes: optional {mode: steps}; then a switch picks the scenario and steps is ignored."""
    pos = {k: p for (k, _, _), p in zip(lanes, (12, 50, 88) if len(lanes) == 3 else (14, 86))}
    modes = modes or {"x": steps}
    legend = legend or {}
    mk = list(modes)
    n = max(len(v) for v in modes.values())
    lane_info = lane_info or {}
    lk = [k for k, _, _ in lanes if k in lane_info]
    inputs = frame_inputs((radios("m", mk) if len(mk) > 1 else "") + radios("st", [str(i) for i in range(1, n + 1)]) + (radios("s", ["0"] + lk) if lk else ""))
    lane_html = "".join(
        f'<label for="s-{k}" class="box {r} ln hot b-{k}" style="left:{pos[k]}%">{lab}</label>' if k in lane_info
        else f'<div class="box {r} ln" style="left:{pos[k]}%">{lab}</div>' for k, lab, r in lanes)
    close = f'<label class="pill" for="s-0">&#10005; {t("back to the steps", "手順に戻る")}</label>'
    alls = {m: "".join(f'<div>{cap}</div>' for _, _, _, cap, _ in ss) for m, ss in modes.items()}
    linfo = "".join(f'<div class="li i-{k}">{v}<div class="cl">{close}</div></div>' for k, v in lane_info.items())
    arrows, caps, rules = "", "", []
    for m, ss in modes.items():
        for i, (lab, a, b, cap, kind) in enumerate(ss, 1):
            l, r = sorted((pos[a], pos[b]))
            dirc = "r" if pos[b] > pos[a] else "l"
            em = ' style="left:72%"' if len(lanes) == 3 and r - l > 50 else ""
            arrows += f'<div class="ar m{m} a{i} {dirc} {kind}" style="top:calc(var(--rw) * {i-1} + 6px);left:{l}%;width:{r-l}%"><span class="ah"></span><em{em}><b>{i}</b> {lab}</em></div>'
            caps += f'<div class="cap m{m} k{i}">{cap}</div>'
    for i in range(1, n + 1):
        later = [f"#st-{i}:checked~.zr .a{j}" for j in range(i + 1, n + 1)]
        if later:
            rules.append(",".join(later) + "{opacity:0}")
        rules.append(f"#st-{i}:checked~.zr .a{i}{{opacity:1;filter:none}}#st-{i}:checked~.zr .a{i}::after{{animation:shine 1s linear infinite}}")
        rules.append(f"#st-{i}:checked~.zr .k{i},#st-{i}:checked~.zr .n{i}{{display:flex}}")
    if len(mk) > 1:
        for m in mk:
            others = [o for o in mk if o != m]
            rules.append(",".join(f"#m-{m}:checked~.zr .m{o}" for o in others) + "{display:none!important}")
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
    switch = ""
    if len(mk) > 1:
        switch = '<div class="ctl">' + "".join(f'<label class="pill pm-{m}" for="m-{m}">{lab}</label>' for m, lab in (legend or {}).items()) + "</div>"
    body = (inputs + '<div class="zr">' + bar(*title) + switch
            + f'<div class="seq">{lifel}<div class="lanes">{lane_html}</div><div class="msgs">{arrows}</div></div>'
            + f'<div class="info">{caps}{navs}{linfo}{"".join(f'<div class="all m{m}">{v}</div>' for m, v in alls.items())}</div></div>')
    css = f"""
.seq{{position:relative;--rw:32px;height:calc(var(--rw) * {n} + 60px)}}
@media (max-width:520px){{.seq{{--rw:27px}}.ar em{{font-size:11px}}.ln{{font-size:12px;width:27%}}.all{{font-size:11px;line-height:1.4}}}}
.lf{{position:absolute;top:36px;bottom:0;width:2px;margin-left:-1px;background:var(--line)}}
.lanes{{position:relative;height:36px}}
.ln{{position:absolute;transform:translateX(-50%);width:23%;text-align:center;font-weight:700;padding:6px 0;text-shadow:0 0 3px #000}}
.msgs{{position:absolute;top:46px;left:0;right:0}}
.ar{{position:absolute;height:24px;opacity:.7}}
.ar::before{{content:"";position:absolute;left:0;right:0;top:11px;border-top:3px dashed var(--fg)}}
.ar.d::before{{border-top:7px solid var(--p4);top:9px}}
.ar::after{{content:"";position:absolute;top:9px;height:7px;width:22px;left:0;background:var(--hi);border-radius:4px;opacity:0}}
@keyframes shine{{0%{{left:0;opacity:0}}15%,85%{{opacity:1}}100%{{left:calc(100% - 22px);opacity:0}}}}
.ar.l::after{{animation-direction:reverse!important}}
.ar em{{position:absolute;top:-8px;left:50%;transform:translateX(-50%);font-style:normal;font-size:12px;background:#000;padding:0 6px;white-space:nowrap}}
.ah{{position:absolute;top:4px;width:0;height:0;border:8px solid transparent}}
.r .ah{{right:-6px;border-left-color:var(--fg)}}.l .ah{{left:-6px;border-right-color:var(--fg)}}
.cap,.nav,.all{{display:none}}.all div{{display:block}}.cap{{margin-bottom:8px}}.nav{{justify-content:space-between;align-items:center}}
.ln.hot:hover{{transform:translateX(-50%) translateY(-2px)}}.cl{{margin-top:6px}}
.ar em b{{display:inline-block;min-width:15px;height:15px;line-height:15px;border-radius:50%;background:var(--fg);color:#000;font-size:10px;text-align:center;margin-right:3px}}
""" + "\n".join(rules) + ("\n" + select_css(["0"] + lk) + "".join(f"#s-{k}:checked~.zr .cap,#s-{k}:checked~.zr .nav{{display:none!important}}" for k in lk) if lk else "")
    css += "@media (max-width:520px){#zs:checked~.zr .seq.seq{--rw:21px!important}#zs:checked~.zr .all.all{font-size:10.5px;line-height:1.3}}"
    still = """.ar{opacity:1!important;filter:none!important}
.ar::after{opacity:0!important}
.cap{display:none!important}
.nav{display:none!important}
.all{display:block!important}
.li{display:none!important}
.ln{box-shadow:none!important}
.seq{--rw:25px!important}
.all{font-size:12px;line-height:1.45}"""
    return snippet(body, css, still, skin)



def launch(skin="zenn-dark"):
    lanes = [("h", t("host code", "CPU 側のコード"), "r1"), ("r", "CUDA Runtime", "r2"), ("d", t("CUDA Driver · GPU", "CUDA Driver · GPU"), "r3")]
    steps = [
        (t("register fatbin", "fatbin を登録"), "h", "r", t("1. Before main(), a constructor made by nvcc registers the fatbin with the CUDA Runtime.", "1. main() より前に、nvcc が作った初期化の関数が fatbin を CUDA Runtime に登録します。"), ""),
        ("cudaFree(0)", "h", "r", t("2. The first CUDA call.", "2. 最初の CUDA の呼び出しです。"), ""),
        (t("set up a context", "コンテキストを用意"), "r", "d", t("3. The driver sets up a context (the GPU-side state of this process). " + M("sass89", "context_init", ".0f") + " ms for steps 2 and 3.", "3. ドライバーがコンテキスト (このプロセスの GPU 側の状態) を用意します。2 からここまでで " + M("sass89", "context_init", ".0f") + " ms です。"), ""),
        ("vadd<<<…>>>", "h", "r", t("4. The rewritten call passes the grid and block sizes to the CUDA Runtime; the stub lines up the four arguments and calls cudaLaunchKernel.", "4. 書き換えた呼び出しが大きさを CUDA Runtime に渡し、stub が 4 つの引数で cudaLaunchKernel を呼びます。"), ""),
        (t("load and launch", "読み込んで起動"), "r", "d", t("5. Lazy loading: the module is loaded now and the sm_89 cubin is launched. " + M("sass89", "launch1") + " ms for steps 4 and 5.", "5. lazy loading なので、ここでモジュールを読み込み、sm_89 の cubin を起動します。4 からここまでで " + M("sass89", "launch1") + " ms です。"), ""),
        (t("2nd launch", "2 回目の起動"), "h", "r", t("6. The second launch goes through the same stub and the CUDA Runtime.", "6. 2 回目も同じ stub と CUDA Runtime を通ります。"), ""),
        (t("launch", "起動"), "r", "d", t("7. Already loaded, so the driver only launches the kernel. " + M("sass89", "launch2") + " ms for steps 6 and 7.", "7. 読み込み済みなので、ドライバーは起動するだけです。6 からここまでで " + M("sass89", "launch2") + " ms です。"), ""),
    ]
    li = {"h": t("<b>Host code</b>: the CPU-side part of vadd.cu after nvcc rewrote it.", "<b>CPU 側のコード</b> (host code) は、nvcc が書き換えたあとの vadd.cu の CPU で動く部分です。"),
          "r": t("<b>CUDA Runtime</b>: statically linked into the executable; ldd lists no libcudart.so. It is built on the Driver API.", "<b>CUDA Runtime</b> は実行ファイルに静的にリンクされていて、ldd に libcudart.so は出ません。中では Driver API を呼びます。") + src(NVCC + "#cudart-none-shared-static-hybrid-cudart"),
          "d": t("<b>CUDA Driver</b>: libcuda.so.1, installed with the NVIDIA driver on the machine. ldd does not list it either; it is opened while the program runs (seen with strace).", "<b>CUDA Driver</b> は libcuda.so.1 で、マシンの NVIDIA ドライバーと一緒に入ります。これも ldd には出ず、実行中に開かれます (strace で確認)。")}
    return _stepper2(("From program start to the 2nd launch", "開始から 2 回目の起動まで"), lanes, steps, skin=skin, lane_info=li)


LEG2 = t('<i class="lg r3"></i> NVIDIA Driver &nbsp; <i class="lg r4"></i> hardware &nbsp; <i class="lg bad"></i> error &nbsp; <i class="dot"></i> this case',
          '<i class="lg r3"></i> NVIDIA ドライバー &nbsp; <i class="lg r4"></i> ハードウェア &nbsp; <i class="lg bad"></i> エラー &nbsp; <i class="dot"></i> この場合の道')


def select(skin="zenn-dark"):
    VW, VH = 720, 270
    N = {
        "launch": (8, 112, 100, 46, t("first launch", "最初の起動"), "", "r0"),
        "cub": (138, 112, 150, 46, t("usable cubin?", "使える cubin?"), t("sm_89 / sm_80 (tested)", "sm_89 / sm_80 (試した範囲)"), "r3"),
        "load": (330, 20, 140, 46, t("load the cubin", "cubin を読み込む"), "", "r3"),
        "run": (590, 20, 120, 46, t("run on the GPU", "GPU で実行"), "", "r4"),
        "ptx": (330, 204, 140, 46, t("PTX in the fatbin?", "fatbin に PTX?"), "compute_XX ≤ 89", "r3"),
        "cachek": (500, 112, 110, 46, t("in the cache?", "キャッシュに?"), "compute cache", "r3"),
        "jit": (630, 204, 82, 46, "JIT", "PTX → SASS", "r3"),
        "err": (138, 210, 150, 46, t("error", "エラー"), "no kernel image", "bad"),
    }
    E = {
        "lc": "M108 135 L136 135",
        "cl": "M250 112 L250 43 L328 43",
        "lr": "M470 43 L588 43",
        "cp": "M270 158 L270 190 L360 190 L360 202",
        "pc": "M440 204 L440 135 L498 135",
        "cj": "M610 135 L670 135 L670 202",
        "jr": "M690 204 L690 68",
        "cr": "M555 112 L555 66 L588 55",
        "pe": "M330 233 L290 233",
    }
    word = lambda x, y, en, ja: f'<text class="lb le" x="{x}" y="{y}">{en}</text><text class="lb lj" x="{x}" y="{y}">{ja}</text>'
    bands = word(256, 82, "yes", "ある") + word(276, 182, "no", "ない") + word(446, 176, "yes", "ある") + word(616, 128, "miss", "ない") + word(560, 92, "hit", "ある") + word(292, 248, "no", "ない")
    modes = {
        "s89": ("sm_89 cubin", ["lc", "cl", "lr"], t("Only an sm_89 cubin (-gencode arch=compute_89,code=sm_89): the driver loads it. First launch " + M("sass89", "launch1") + " ms (median of 10). The -arch=sm_89 build, which also holds PTX, took the same path.", "sm_89 の cubin だけ (-gencode arch=compute_89,code=sm_89): ドライバーはこの cubin を読み込みます。最初の起動は " + M("sass89", "launch1") + " ms でした (10 回の中央値)。PTX も入る -arch=sm_89 の実行ファイルでも、同じ道を通りました。")),
        "s80": ("sm_80 cubin", ["lc", "cl", "lr"], t("Only an sm_80 cubin: same major version 8 and 0 ≤ 9, so the L4 runs it as is. First launch " + M("sass80", "launch1") + " ms, close to the sm_89 cubin.", "sm_80 の cubin だけ: メジャーが同じ 8 で 0 ≤ 9 なので、L4 はそのまま実行できます。最初の起動は " + M("sass80", "launch1") + " ms で、sm_89 の cubin に近い値でした。")),
        "p1": (t("PTX only · no cache", "PTX だけ · キャッシュなし"), ["lc", "cp", "pc", "cj", "jr"], t("Only compute_80 PTX, compute cache disabled (CUDA_CACHE_DISABLE=1): the driver JIT-compiles the PTX on every run. First launch " + M("ptx80_nocache", "launch1", ".2f") + " ms (median of 10), about " + DIFF + " ms more than the sm_89 cubin.", "compute_80 の PTX だけで、compute cache を使わない設定 (CUDA_CACHE_DISABLE=1): ドライバーは実行のたびに PTX を JIT コンパイルします。最初の起動は " + M("ptx80_nocache", "launch1", ".2f") + " ms でした (10 回の中央値)。sm_89 の cubin より約 " + DIFF + " ms 長くなります。")),
        "p2": (t("PTX only · cached", "PTX だけ · キャッシュあり"), ["lc", "cp", "pc", "cr"], t("Same executable with the compute cache on, runs 2 to 10 after emptying the cache: the SASS made in run 1 is found in ~/.nv/ComputeCache. First launch " + M("ptx80_cache", "launch1") + " ms (median of 9).", "同じ実行ファイルで compute cache を使う設定にし、キャッシュを空にしてから動かした 2〜10 回目: 1 回目に作った SASS が ~/.nv/ComputeCache に見つかります。最初の起動は " + M("ptx80_cache", "launch1") + " ms でした (9 回の中央値)。")),
        "s90": ("sm_90 cubin", ["lc", "cp", "pe"], t("Only an sm_90 cubin: major 9 differs from 8 and there is no PTX, so the launch fails with cudaErrorNoKernelImageForDevice.", "sm_90 の cubin だけ: メジャーが 9 と 8 で違い、PTX も無いので、起動は cudaErrorNoKernelImageForDevice で失敗します。")),
    }
    mk = list(modes)
    toks = "".join(f'<circle class="tk tk-{m}" r="6" style="offset-path:path(\'{_join([E[e] for e in es])}\')"/>' for m, (_, es, _) in modes.items())
    graph = _graph(VW, VH, N, E, bands, toks)
    info = {
        "0": "".join(f'<span class="mc mc-{m}">{cap}</span>' for m, (_, _, cap) in modes.items()),
        "launch": t("<b>First launch</b>: with lazy loading (on by default on Linux since CUDA 12.2, on all platforms since 12.3) the choice in this figure happens at the first launch of the kernel, not at program start-up.", "<b>最初の起動</b>: lazy loading (Linux では CUDA 12.2 から、全環境では 12.3 から既定) では、この図の選択は、プログラムの開始時ではなく、そのカーネルを最初に起動したときに起きます。") + src(LAZY),
        "cub": t("<b>Binary compatibility</b>: a cubin runs on GPUs with the same major compute capability and an equal or higher minor one. On this L4 (8.9) the sm_80 cubin ran and the sm_90 cubin did not. For cubins of 10.0 and later, the driver re-finalizes the cubin at run time (off-target finalization) when it is loaded on a different, compatible GPU of the same family. The order drawn here is what we saw with three fatbins: cubin only, PTX only, and an sm_89 cubin plus PTX.", "<b>バイナリの互換</b>: cubin は、compute capability のメジャーが同じで、マイナーが同じか大きい GPU で動きます。この L4 (8.9) では、sm_80 の cubin は動き、sm_90 は動きませんでした。10.0 以降の cubin は、同じ GPU ファミリーの中で作った先と違う GPU に読み込むと、ドライバーが実行時に finalize し直します (off-target finalization)。この図の順番は、cubin だけ、PTX だけ、sm_89 の cubin と PTX の両方、の 3 通りで試した結果です。") + src(PLAT + "#binary-compatibility"),
        "load": t("<b>Load the cubin</b>: no JIT compilation; the fastest path we measured on the L4.", "<b>cubin を読み込む</b>: JIT コンパイルが無く、L4 で測った中でいちばん速い道です。"),
        "ptx": t("<b>PTX compatibility</b>: PTX for compute_XX can be JIT-compiled for any GPU of that compute capability or higher. This is how a program can run on GPUs that did not exist when it was built.", "<b>PTX の互換</b>: compute_XX の PTX は、その compute capability 以上のどの GPU 向けにも JIT コンパイルできます。作ったときに無かった GPU でもプログラムが動くのはこのためです。") + src(PLAT + "#ptx-compatibility"),
        "cachek": t("<b>Compute cache</b>: SASS the driver compiled before. CUDA_CACHE_DISABLE=1 turns it off.", "<b>compute cache</b>: 前にドライバーがコンパイルした SASS です。CUDA_CACHE_DISABLE=1 で使わなくなります。") + src(ENV + "#cuda-cache-disable"),
        "jit": t("<b>JIT</b>: the driver compiles the PTX with libnvidia-ptxjitcompiler.so.1 (strace: opened by the PTX-only build, not by the sm_89-cubin-only build) and stores the result in the cache.", "<b>JIT</b>: ドライバーが libnvidia-ptxjitcompiler.so.1 で PTX をコンパイルし、結果をキャッシュに置きます (strace では、PTX だけの実行ファイルで開かれ、sm_89 の cubin だけの実行ファイルでは開かれませんでした)。") + src(PLAT + "#just-in-time-compilation"),
        "run": t("<b>Run on the GPU</b>: the result is the same on every path (c[12345] = 37035).", "<b>GPU で実行</b>: どの道でも結果は同じでした (c[12345] = 37035)。"),
        "err": t("<b>no kernel image is available for execution on the device</b>: neither a compatible cubin nor usable PTX was in the fatbin.", "<b>no kernel image is available for execution on the device</b>: fatbin に、互換のある cubin も使える PTX もありませんでした。"),
    }
    keys = ["0"] + list(N)
    switch = '<div class="ctl"><span class="hint">' + t("the fatbin holds", "fatbin の中身") + "</span>" + "".join(f'<label class="pill pm-{m}" for="m-{m}">{lab}</label>' for m, (lab, _, _) in modes.items()) + "</div>"
    body = (frame_inputs(radios("m", mk) + radios("s", keys)) + '<div class="zr">' + bar("What the driver used on the L4: cubin, PTX JIT or an error", "L4 でドライバーが使ったもの: cubin、PTX の JIT、エラー")
            + switch + graph + f'<div class="legend">{LEG2}</div>' + info_panel(info) + "</div>")
    rules = []
    for m, (_, es, _) in modes.items():
        rules.append(",".join(f"#m-{m}:checked~.zr .eg-{e}" for e in es) + "{opacity:1;stroke-width:3.5;stroke-dasharray:none}")
        rules.append(f"#m-{m}:checked~.zr .tk-{m}{{display:block}}#m-{m}:checked~.zr .mc-{m}{{display:inline}}#m-{m}:checked~.zr .pm-{m}{{background:var(--fg);color:#000}}")
    sel = "\n".join(f"#s-{k}:checked~.zr .i-{k}{{display:block}}" + (f"#s-{k}:checked~.zr .b-{k}{{box-shadow:0 0 0 3px var(--fg)}}" if k != "0" else "") for k in keys)
    css = GRAPH_CSS + """
.e{opacity:.3;stroke-dasharray:5 5}
.lb{fill:var(--mut);font:11px Menlo,Consolas,monospace}
.lg{display:inline-block;width:18px;height:11px;vertical-align:middle;border:2px solid var(--p2);background:var(--p2-bg)}
.lg.r1{border-color:var(--p1);background:var(--p1-bg)}.lg.r3{border-color:var(--p3);background:var(--p3-bg);border-style:dashed}.lg.r4{border-color:var(--p4);background:var(--p4-bg)}.lg.bad{border-color:var(--bad);background:var(--bad-bg);border-style:double}
#zl-en:checked~.zr .lj,#zl-ja:checked~.zr .le{display:none}
.mc{display:none}
.tk{fill:var(--hi);display:none;offset-rotate:0deg;animation:run 5s ease-in-out infinite}
@keyframes run{0%{offset-distance:0%;opacity:0}6%{opacity:1}85%{offset-distance:100%;opacity:1}92%,100%{offset-distance:100%;opacity:0}}
""" + "\n".join(rules) + "\n" + sel
    still = """.tk{offset-distance:50%!important;opacity:1!important}"""
    return snippet(body, css, still, skin)


def _join(paths):
    """Chain edge paths into one token path (each edge starts where the previous one ended, roughly)."""
    out = []
    for i, d in enumerate(paths):
        out.append(d if i == 0 else "L" + d[1:])
    return " ".join(out)


def frontends(skin="zenn-dark"):
    VW, VH = 720, 300
    rows = [("cu", "CUDA C++", "one thread at a time", "nvcc (cicc)", 14),
            ("tr", "Triton (Python)", "one block (tile) at a time", "Triton compiler", 84),
            ("cd", "CuTe DSL (Python)", "layouts, copies, MMAs as parts", "CUTLASS Python compiler", 154),
            ("tl", "TLX (Python)", "Triton + warp-group roles", "fbtriton compiler", 224)]
    N, E = {}, {}
    for k, nm, sub, comp, y in rows:
        N[k] = (10, y, 170, 52, nm, sub, "r1")
        N[k + "c"] = (215, y, 170, 52, comp, "", "")
        E["a" + k] = f"M180 {y + 26} L213 {y + 26}"
        E["b" + k] = f"M385 {y + 26} L{430} {y + 26} L{430} 150 L448 150" if y not in (84, 154) else f"M385 {y + 26} L{430} {y + 26} L{430} 150"
    E["bcu"] = "M385 40 L430 40 L430 128 L448 128"
    E["btr"] = "M385 110 L430 110 L430 140 L448 140"
    E["bcd"] = "M385 180 L430 180 L430 160 L448 160"
    E["btl"] = "M385 250 L430 250 L430 172 L448 172"
    N["ptx"] = (450, 100, 90, 100, "PTX", "", "r1")
    N["as"] = (575, 70, 130, 56, "PTX to cubin", "", "")
    N["ld"] = (575, 150, 130, 56, "libcuda.so.1 loads the cubin", "", "r3")
    E["p1"] = "M540 130 L573 100"
    E["p2"] = "M640 126 L640 148"
    E["gpu"] = "M640 206 L640 262"
    N["g"] = (575, 262, 130, 34, "GPU", "", "r4")
    bands = '<text class="bandt" x="10" y="9">you write</text><text class="bandt" x="215" y="9">compiler</text>'
    graph = _graph(VW, VH, N, E, bands)
    body = (frame_inputs() + '<div class="zr">' + bar("Four ways to write a kernel, all through PTX", "4 通りの書き方、どれも PTX を通る")
            + graph + '<div class="legend">' + t('<i class="lg r1"></i> source or PTX text &nbsp; <i class="lg"></i> compiler &nbsp; <i class="lg r3"></i> NVIDIA driver &nbsp; <i class="lg r4"></i> hardware', '<i class="lg r1"></i> ソースと PTX &nbsp; <i class="lg"></i> コンパイラ &nbsp; <i class="lg r3"></i> NVIDIA ドライバー &nbsp; <i class="lg r4"></i> ハードウェア') + "</div></div>")
    css = GRAPH_CSS + ".lg{display:inline-block;width:18px;height:11px;vertical-align:middle;border:2px solid var(--p2);background:var(--p2-bg)}.lg.r1{border-color:var(--p1);background:var(--p1-bg)}.lg.r3{border-color:var(--p3);background:var(--p3-bg);border-style:dashed}.lg.r4{border-color:var(--p4);background:var(--p4-bg)}"
    return snippet(body, css, "", skin)


def warp_roles(skin="zenn-dark"):
    VW, VH = 720, 300
    N = {"ld": (30, 30, 150, 58, "Load task (1 warp)", "issues TMA copies", "r1"),
         "mm": (285, 30, 150, 58, "MMA task (1 warp)", "issues tensor-core MMAs", "r1"),
         "ep": (540, 30, 150, 58, "Epilogue (default task)", "convert and store", "r1"),
         "sm": (130, 190, 170, 58, "shared memory buffers", "NUM_STAGES of them", "r3"),
         "tm": (420, 190, 170, 58, "TMEM (accumulator)", "Blackwell tensor memory", "r3")}
    E = {"fa": "M180 46 L283 46", "fb": "M283 72 L180 72", "fc": "M435 59 L538 59",
         "d1": "M105 88 L105 150 L170 150 L170 188", "d2": "M260 190 L260 150 L330 150 L330 90",
         "d3": "M380 90 L380 150 L450 150 L450 188", "d4": "M570 190 L570 150 L615 150 L615 90"}
    txt = lambda x, y, s: f'<text class="lb" x="{x}" y="{y}" text-anchor="middle">{s}</text>'
    bands = (txt(232, 38, "full") + txt(232, 90, "empty") + txt(487, 51, "done")
             + '<text class="bandt" x="10" y="14">3 tasks (warp groups) in one thread block</text>')
    graph = _graph(VW, VH, N, E, bands)
    body = (frame_inputs() + '<div class="zr">' + bar("Warp specialization in a Blackwell GEMM", "Blackwell の GEMM での warp specialization")
            + graph + '<div class="legend">' + t('<i class="lg r1"></i> task &nbsp; <i class="lg r3"></i> memory &nbsp; solid arrow: data &nbsp; dashed arrow: mbarrier signal', '<i class="lg r1"></i> task &nbsp; <i class="lg r3"></i> メモリ &nbsp; 実線: データ &nbsp; 破線: mbarrier の合図') + "</div></div>")
    css = GRAPH_CSS + ".lb{fill:var(--fg);font:12px Menlo,Consolas,monospace}.eg-fa,.eg-fb,.eg-fc{stroke-dasharray:6 5}.lg{display:inline-block;width:18px;height:11px;vertical-align:middle;border:2px solid var(--p2);background:var(--p2-bg)}.lg.r1{border-color:var(--p1);background:var(--p1-bg)}.lg.r3{border-color:var(--p3);background:var(--p3-bg);border-style:dashed}"
    return snippet(body, css, "", skin)
