
# 7 推奨構成 -------------------------------------------------------------------
s = figslide("推奨構成: 入口は Gateway、鍵は Identity", "ARCHITECTURE")


def arch(sl, t_, x, y, w):
    tools = [other(sl, x, y + 70 + i * 90, 200, 60, n, size=16) for i, n in enumerate(["Devin", "Claude Code", "その他の\nAI エージェント"])]
    en = mine(sl, x + 300, y, 300, 56, "Entra ID でサインイン", size=17)
    gw = aws(sl, x + 300, y + 130, 300, 84, "AgentCore Gateway\nPolicy で判定", size=18)
    idt = aws(sl, x + 300, y + 290, 300, 64, "AgentCore Identity\n鍵の保管庫", size=16)
    gh = other(sl, x + 760, y + 70, 260, 60, "GitHub MCP", size=17)
    ot = other(sl, x + 760, y + 160, 260, 60, "その他の SaaS")
    ct = aws(sl, x + 760, y + 290, 260, 64, "CloudTrail\n呼び出しの記録", size=16)
    for a in tools:
        line(sl, a, 3, gw, 1)
    line(sl, gw, 0, en, 2, dashed=True, color=GRN)
    line(sl, idt, 0, gw, 2, color=BLU, head=True)
    for b in (gh, ot):
        line(sl, gw, 3, b, 1)
    line(sl, gw, 3, ct, 1, color=MUTED, width=1.25)
    text(sl, x + 1050, y + 60, 160, 200, "実線: 呼び出し\n点線: 本人確認\n灰色: 記録", size=15, color=MUTED)


s.raw(arch, 360)
s.bullets(["Gateway への呼び出しは、" + L("CloudTrail のデータイベント", "gwtrail") + "を有効にすると 1 件ずつ記録できる。GitHub は " + L("GitHub 公式の MCP サーバー", "ghmcp") + "を先に試す",
           "どの部品も東京リージョンで使える (" + L("対応リージョン", "regions") + ")"], size=18)
s.notes("推奨する構成です。どの AI エージェントも、MCP の接続先は Gateway の 1 本だけにします。",
        "Gateway は来た人を Entra ID のトークンで確かめ、Policy でその人が呼んでよいツールかを判定します。そのうえで Identity から鍵を受け取り、GitHub などへ中継します。Gateway への呼び出しは CloudTrail に 1 件ずつ記録できます。")

