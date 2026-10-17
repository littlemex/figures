
# 9b Agent Registry の位置と連携 ----------------------------------------------------
s = figslide("Agent Registry は社内の案内板: 使ってよい MCP サーバーを載せ、探せるようにする", "AGENT REGISTRY",
             sub="案内板で使える MCP サーバーを見つけるが、実際の呼び出しは Gateway を通る")


def registry(sl, t_, x, y, w):
    frame = box(sl, x + 290, y, 580, 250, "", fill=None, stroke=BLU, radius=0.04)
    text(sl, x + 300, y + 8, 560, 34, "AWS Agent Registry", size=19, bold=True, color=BLU, align="center")
    st = [("下書き", GRY_DK, GRY), ("承認待ち", YEL_DK, YEL), ("承認済み", GRN_DK, GRN)]
    bs = []
    for k, (lab, f, e) in enumerate(st):
        bs.append(box(sl, x + 310 + k * 180, y + 56, 160, 60, lab, fill=f, stroke=e, size=17))
        if k < 2:
            sh.arrow(sl, t_, x + 470 + k * 180, y + 86, x + 490 + k * 180, y + 86, color=WHITE, width=2)
    text(sl, x + 300, y + 128, 560, 30, "承認済みだけが検索に出る", size=16, color=MUTED, align="center")
    srch = aws(sl, x + 310, y + 172, 540, 54, "Registry 自身の MCP の窓口で検索", size=16)
    pub = mine(sl, x, y + 10, 240, 70, "管理者が\nレコードを登録", size=17)
    idt = aws(sl, x, y + 150, 240, 60, "Identity: 取り込みの鍵", size=15)
    gw = aws(sl, x, y + 310, 240, 70, "AgentCore Gateway", size=17)
    eb = aws(sl, x + 930, y + 10, 260, 60, "EventBridge で通知", size=17)
    cur = mine(sl, x + 930, y + 110, 260, 60, "承認する人", size=17)
    tool = other(sl, x + 930, y + 310, 260, 70, "利用者と\nAI エージェント", size=16)
    line(sl, pub, 3, bs[0], 1)
    line(sl, idt, 3, frame, 1, color=BLU, dashed=True)
    line(sl, gw, 0, frame, 2, color=GRN, dashed=True)
    line(sl, frame, 3, eb, 1, color=MUTED)
    line(sl, eb, 2, cur, 0)
    line(sl, cur, 1, bs[2], 3)
    line(sl, tool, 0, srch, 3, dashed=True)
    line(sl, tool, 1, gw, 3, color=WHITE, width=3)
    text(sl, x + 560, y + 256, 400, 30, "MCP サーバーの中身を自動で取り込む", size=14, color=GRN)
    text(sl, x + 560, y + 300, 440, 30, "見つけた MCP サーバーを呼ぶ", size=15, color=WHITE, align="center")
    text(sl, x + 1090, y + 236, 100, 30, "探す", size=15, color=MUTED)


s.raw(registry, 400)
s.text("点線: 登録内容の自動取り込み (" + L("同期", "regsync") + ")、鍵の受け取り、検索。承認の流れ: " + L("レコードの状態", "reglife") + "、" + L("通知", "regeb"), size=16, muted=True)
s.notes("Agent Registry は、社内の案内板のようなものです。管理者が Gateway につないだ MCP サーバーなどをレコードとして登録し、承認する人が承認すると、利用者や AI エージェントが検索できるようになります。",
        "登録した MCP サーバーの URL から中身を自動で取り込むこともでき、そのときに要る鍵は Identity から受け取ります。承認を頼まれると EventBridge で通知が出ます。",
        "利用者は案内板で使える MCP サーバーを見つけますが、実際の呼び出しは Gateway を通ります。Registry は鍵を預からず、呼び出しも中継しません。")
