"""ブログ用の図: 自動登録に応える中継サーバーが、何をどこへ取り次ぐかを 1 枚で示す。p1.py の部品を使う。"""
import pathlib
import sys

PARTS = pathlib.Path(sys.argv[1])
OUT = sys.argv[2]
src = (PARTS / "p1.py").read_text().replace('d = Deck(TPL, footer="page", check_layout=False)', 'd = Deck(TPL, footer=None, check_layout=False)')
g = {"__name__": "fig", "__file__": str(PARTS / "x.py")}
exec(compile(src, "p1", "exec"), g)
globals().update({k: v for k, v in g.items() if not k.startswith("__")})

s = figslide("中継サーバーの全体像: Entra ID に足りない部分を取り次ぐ", "RELAY SERVER",
             leg=[(GRY, "他社の製品"), (BLU, "AWS が提供"), (GRN, "自社で作る中継サーバー"), (YEL, "Entra ID だけでは足りない部分")])


def fig(sl, t_, x, y, w):
    ag = other(sl, x, y + 170, 200, 96, "AI エージェント", size=17)
    box(sl, x + 280, y, 520, 458, "", fill=CHIP, stroke=GRN, radius=0.03)
    text(sl, x + 300, y + 6, 480, 32, "中継サーバー: API Gateway + Lambda", size=16, bold=True, color=GRN)
    rows = [("1. 案内", "自分を認可サーバーとして案内する"),
            ("2. 登録", "前もって登録した client ID を返す"),
            ("3. サインイン", "宛先の指定を外し、Gateway 用の\n権限を足し、戻り先を自分に替える"),
            ("4. 戻り", "Entra ID からの戻りを\nAI エージェントに返す"),
            ("5. トークン", "Entra ID でトークンに引き換える"),
            ("6. MCP", "呼び出しを Gateway へ渡す")]
    bs, hs = [], []
    for i, (head, body) in enumerate(rows):
        yy = y + 42 + i * 68
        hs.append(mine(sl, x + 296, yy, 150, 60, head, size=14))
        bs.append(box(sl, x + 454, yy, 330, 60, body, size=14, bold=False))
    line(sl, ag, 3, hs[0], 1, color=WHITE, width=2)
    line(sl, ag, 3, hs[5], 1, color=WHITE, width=2)
    text(sl, x + 10, y + 120, 260, 40, "接続先は中継サーバー", size=14, color=MUTED)
    en = other(sl, x + 900, y + 40, 294, 80, "Entra ID", size=18)
    warn(sl, x + 900, y + 132, 294, 150, "Entra ID だけでは足りない\n・自動登録を受け付けない\n・宛先の指定を受け付けない\n・戻り先は前もって登録", size=14)
    gw = aws(sl, x + 900, y + 378, 294, 80, "AgentCore Gateway", size=17)
    line(sl, bs[2], 3, en, 1, color=GRN, width=2)
    line(sl, bs[3], 3, en, 1, color=GRN, dashed=True, width=1.5)
    line(sl, bs[4], 3, en, 1, color=GRN, width=2)
    line(sl, bs[5], 3, gw, 1, color=WHITE, width=2.5)


s.raw(fig, 460)
d.save(OUT)
print("wrote", OUT)
