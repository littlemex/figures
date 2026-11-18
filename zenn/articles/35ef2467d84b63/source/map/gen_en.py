import re, importlib.util, json
spec = importlib.util.spec_from_file_location("g", "gen.py")
src = open("gen.py").read()
# reuse the SVG builder only
ns = {}
code = src.split("E_STEPS = [")[0]
exec(code, ns)
svg = ns["engram_svg"]()
R = [
 ("現在地", "current position"), ("1. 番号をそろえる", "1. compress the token ids"), ("2. n-gram = 番号の並び", "2. n-grams: the ids in a row"),
 ("3. 掛けて XOR、1 つの大きな数に", "3. multiply and XOR into one big number"), ("さらに XOR", "then XOR"),
 ("4. 16 個の素数で割った余り = 行番号", "4. remainder by a prime = row id"), (" 余り ", " → "), ("→ 行 ", "row "),
 (">表<", ">table<"), ("1,049,422 行 × 64", "1,049,422 rows × 64"), ("行 0 から 1,049,421 まで。右の数字は範囲の番号", "16 ranges, rows 0 to 1,049,421"),
 ("5. その 16 行を読む", "5. read those 16 rows"), ("1 行 = 64 個の数。探さず、番号の行をそのまま読む", "64 numbers per row · read by id, no search"),
 ("行 15,920 の中身:", "row 15,920:"), ("6. 16 行 × 64 個 = 1,024 個を 1 列につなぐ", "6. join: 16 rows × 64 = 1,024 numbers"),
 ("（1,024 個。先頭の 64 個が範囲 0 の行 15,920 の中身）", "(1,024; the first 64 are row 15,920)"),
 ("7. 学習した行列 W_kv を掛けて、1,024 個を作り直し、前半と後半に分ける", "7. multiply by the learned W_kv, split in two"),
 ("e（1,024 個）×", "e (1,024) ×"), ("前半 512 個 = key", "first 512 = key"), ("後半 512 個 = value", "last 512 = value"),
 ("8. GPT 本体の隠れ状態 h と key を 1 回だけ比べて、足す量（ゲート）を決める", "8. compare the hidden state h with key, once → gate"),
 ("h: ブロック 0 の後（512 個）", "h after block 0 (512)"), ("→ 符号つき √ →", "→ signed √ →"), ("→ ゲート", "→ gate"),
 ("9. value を足す", "9. add the value"), ("ブロック 1 へ", "to block 1"), ("h の先頭", "h[0]:"),
]
for a, b in R:
    assert a in svg, a
    svg = svg.replace(a, b)
svg = re.sub(r">範囲 (\d+)<", r">range \1<", svg)
left = re.findall(r"[ぁ-んァ-ン一-龥]", svg)
assert not left, "".join(sorted(set(left)))
css = """
body{margin:0;background:#000}
svg text{font-family:"Amazon Ember","Helvetica Neue",Arial,sans-serif;fill:#e8edf2;font-size:12.5px}
.h{font-weight:700;font-size:13.5px;fill:#ffffff}.sm{font-size:11.5px}.tiny{font-size:10.5px}.dim{fill:#a0a8b4}
.num{font-family:Menlo,Consolas,monospace;font-size:11.5px}.num.tiny{font-size:10px}.b{font-weight:700;fill:#7ee2a0}
.lab.y{fill:#fbd332;font-weight:700}.op{font-size:18px;font-weight:700}
.tk rect{fill:#343840;stroke:#6e747c}.tk.ng rect{stroke:#fbd332}.tk.cur rect{fill:#50420e;stroke:#fbd332;stroke-width:2.5}.tk.ghost rect{fill:#000;stroke:#8a94a0;stroke-dasharray:4 3}.tk.ghost text{fill:#a0a8b4}
.ids{fill:#50420e;stroke:#fbd332}.ids.dash{stroke-dasharray:4 3}.ids.dbl{stroke-width:3}
.band.b2{fill:#12402a;stroke:#24a046}.band.b3{fill:#0f3322;stroke:#24a046}
.tick{fill:#ff7a6e}.ptr{stroke:#fbd332;stroke-width:1}.pull{stroke:#24a046;stroke-width:1}
.strip.b2{fill:#12402a;stroke:#24a046}.strip.b3{fill:#0f3322;stroke:#24a046}
.et{fill:#12402a;stroke:#24a046}.sep{stroke:#24a046;stroke-width:.6}
.mat{fill:#1d5a35;stroke:#7ee2a0}.key{fill:#12402a;stroke:#24a046;stroke-width:2}.val{fill:#12402a;stroke:#24a046;stroke-width:2;stroke-dasharray:5 2}
.hid{fill:#102c48;stroke:#2896f0}
"""
svg = svg.replace('fill="#8a5a12"', 'fill="#fbd332"').replace('fill="#1f7a4d"', 'fill="#24a046"')
open("map_en.html", "w").write(f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body><div style='width:1320px'>{svg}</div></body></html>")
print("ok")
