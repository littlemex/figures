"""ブログ用の図: 通行証のたとえのまま、実際の構成と流れを 1 枚で示す。p1.py の部品を使う。"""
import pathlib
import sys

PARTS = pathlib.Path(sys.argv[1])
OUT = sys.argv[2]
src = (PARTS / "p1.py").read_text().replace('d = Deck(TPL, footer="page", check_layout=False)', 'd = Deck(TPL, footer=None, check_layout=False)')
g = {"__name__": "fig", "__file__": str(PARTS / "x.py")}
exec(compile(src, "p1", "exec"), g)
globals().update({k: v for k, v in g.items() if not k.startswith("__")})

s = figslide("通行証のたとえで見る構成: 誰がどこで何をするか", "ANALOGY TO ARCHITECTURE",
             leg=[(GRY, "他社の製品"), (BLU, "AWS が提供"), (GRN, "通行証をもらう流れ"), (WHITE, "呼び出しの流れ")])


def fig(sl, t_, x, y, w):
    box(sl, x + 350, y, 616, 160, "", fill=CHIP, stroke=GRY)
    text(sl, x + 366, y + 4, 300, 32, "Entra ID", size=17, bold=True, color=MUTED)
    iss = other(sl, x + 366, y + 46, 180, 96, "認可サーバー\n= 発行所", size=17)
    ppl = other(sl, x + 566, y + 46, 180, 96, "利用者の一覧\n= 社員の名簿", size=17)
    app = other(sl, x + 766, y + 46, 180, 96, "アプリ登録\n= アプリの名簿", size=15)
    emp = box(sl, x, y + 20, 200, 80, "利用者\n= 社員", size=17)
    tl = other(sl, x, y + 240, 220, 96, "AI エージェント\n= 社員の代理人", size=16)
    gw = aws(sl, x + 420, y + 240, 320, 96, "AgentCore Gateway\n= 機密エリアの受付", size=17)
    sa = other(sl, x + 990, y + 240, 200, 96, "SaaS の\nMCP サーバー", size=17)
    po = aws(sl, x + 250, y + 385, 250, 80, "Policy\n= 入ってよい部屋", size=16)
    idt = aws(sl, x + 530, y + 385, 260, 80, "AgentCore Identity\n= 金庫", size=16)
    ct = aws(sl, x + 990, y + 385, 200, 80, "CloudTrail\n= 記録帳", size=16)
    line(sl, emp, 3, iss, 1, color=GRN, dashed=True, width=2.5)
    line(sl, tl, 0, iss, 2, color=GRN, width=2.5)
    line(sl, iss, 3, ppl, 1, color=GRN, dashed=True)
    line(sl, ppl, 3, app, 1, color=GRN, dashed=True)
    line(sl, tl, 3, gw, 1, color=WHITE, width=2.5)
    line(sl, po, 0, gw, 2, color=BLU)
    line(sl, idt, 0, gw, 2, color=BLU)
    line(sl, gw, 3, sa, 1, color=WHITE, width=2.5)
    line(sl, gw, 3, ct, 1, color=MUTED, width=1.25)
    text(sl, x + 200, y + 96, 170, 56, "1. 社員証で\nサインイン", size=15, color=GRN)
    text(sl, x, y + 116, 200, 60, "2. 代理人用の\n通行証をもらう", size=15, color=GRN)
    text(sl, x + 560, y + 4, 400, 32, "3. 名簿を 2 つ確かめて出す", size=15, color=GRN)
    text(sl, x + 226, y + 198, 200, 40, "4. 通行証を見せる", size=15)
    text(sl, x + 30, y + 395, 210, 60, "5. 入ってよい\n部屋かを判定", size=15, color=BLU)
    text(sl, x + 795, y + 405, 170, 60, "6. 金庫の鍵を\n受付に渡す", size=15, color=BLU)
    text(sl, x + 770, y + 198, 220, 40, "7. 鍵を使って呼ぶ", size=15)
    text(sl, x + 880, y + 310, 160, 34, "8. 記録する", size=15, color=MUTED)


s.raw(fig, 470)
d.save(OUT)
print("wrote", OUT)
