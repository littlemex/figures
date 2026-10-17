"""ブログ用の図: スライドの部品から、ページ番号と本文の文章を外して書き出す。"""
import pathlib
import sys

PARTS = pathlib.Path(sys.argv[1])
OUT = sys.argv[2]
names = ["p1", "p2", "p2a", "p2b", "p2c", "p3", "p3a", "p3c", "p3d", "p3e", "p4", "p5"]
src = "\n".join((PARTS / f"{n}.py").read_text() for n in names)
src = src.replace('d = Deck(TPL, footer="page", check_layout=False)', 'd = Deck(TPL, footer=None, check_layout=False)')
src = src.replace("t = d.theme\n", "t = d.theme\nfrom pptxkit.deck import Slide as _S\n_S.text = lambda self, *a, **k: self\n_S.bullets = lambda self, *a, **k: self\n", 1)
import re as _re
src = _re.sub(r'\n    text\(sl, x, y \+ 292, 1194, 56, "A の補足:[^\n]*', "", src)
src = _re.sub(r'\n    text\(sl, x, y \+ 352, 1194, 40, "どれか 1 つでも止まると[^\n]*', "", src)
src = src.replace('"freee 用 1 つ"', '"Slack 用 1 つ"')
src = src.replace('out = d.save(os.path.join(HERE, "devin-keys-and-saas-audit.pptx"))', "out = d.save(OUT_PATH)")
exec(compile(src, "figs", "exec"), {"__name__": "figs", "__file__": str(PARTS / "x.py"), "OUT_PATH": OUT})
