
# 1 表紙 ---------------------------------------------------------------------
s = d.title_slide("AI エージェントの MCP 接続と SaaS の鍵を AWS で中央管理し、SaaS の監査ログを検索する")
s.notes("本日いただいた 2 つのご相談について、AWS の立場から構成案をまとめました。",
        "MCP は、AI エージェントが外部のサービスを呼び出すための共通の約束事です。Devin に限らず、MCP を使うどの AI エージェントにも当てはまる形でまとめています。")

# 2 答え ---------------------------------------------------------------------
s = figslide("2 つのご相談への答え", "SUMMARY")


def answers(sl, t_, x, y, w):
    for cx, head, rows in (
            (x, "1. MCP で使う SaaS の鍵の中央管理",
             [(aws, "鍵は AgentCore Identity が預かる"), (aws, "入口は AgentCore Gateway の 1 本"),
              (mine, "利用者は Entra ID で本人確認"), (warn, "Agent Registry は目録で、鍵は預からない")]),
            (x + 614, "2. GitHub と freee の監査ログ",
             [(mine, "GitHub Enterprise Cloud なら S3 へ直接送る"), (aws, "S3 と Athena の定型 SQL を定期実行"),
              (warn, "AppFabric は freee に対応していない"), (warn, "freee は監査ログの取り方を確認する")])):
        box(sl, cx, y, 580, 350, radius=0.04)
        text(sl, cx + 24, y + 12, 540, 40, head, size=21, bold=True, color=BLU)
        for i, (fn, body) in enumerate(rows):
            fn(sl, cx + 24, y + 66 + i * 70, 532, 56, body, size=18)


s.raw(answers, 350)
s.text("どの AI エージェントでも、MCP の接続先を Gateway にそろえれば同じ形で管理できます。", size=19)
s.notes("結論です。MCP で使う SaaS の鍵は AgentCore Identity が預かり、入口を Gateway の 1 本にして、利用者は Entra ID で本人確認します。ご質問の Agent Registry は MCP サーバーの目録で、鍵は預かりません。",
        "監査ログは、GitHub は S3 へ直接送れるので AppFabric は要りません。検索は S3 と Athena の定型 SQL を定期実行する形から始めます。freee は取り方の確認が先です。")

# 3 範囲 ---------------------------------------------------------------------
s = figslide("この資料は、どの AI エージェントにもよらない MCP の管理を扱う", "SCOPE",
             sub="各 AI エージェントの設定は、その AI エージェントの提供元にご確認ください")


def scope(sl, t_, x, y, w):
    cols = [(x, "MCP を使う AI エージェント", other, ["Devin", "Claude Code", "Kiro", "社内のエージェント"], "設定は各社にご確認"),
            (x + 410, "AWS で用意する入口", aws, ["AgentCore Gateway", "AgentCore Identity", "Policy in AgentCore"], "この資料の主題"),
            (x + 820, "使われる SaaS", other, ["GitHub", "freee", "その他の SaaS"], "SaaS 側の制限も使う")]
    for cx, head, fn, items, foot in cols:
        text(sl, cx, y, 374, 40, head, size=21, bold=True, align="center")
        for i, it in enumerate(items):
            fn(sl, cx + 20, y + 50 + i * 66, 334, 54, it)
        text(sl, cx, y + 320, 374, 34, foot, size=17, color=MUTED, align="center")
    for k in range(2):
        sh.arrow(sl, t_, x + 378 + k * 410, y + 150, x + 410 + k * 410, y + 150, color=WHITE, width=3)


s.raw(scope, 360)
s.notes("この資料は、特定の AI エージェントによらない MCP の管理を扱います。Devin のほか、Claude Code や Kiro、ほかの Coding Agent でも、MCP の接続先を AWS の Gateway にそろえれば同じ形で管理できます。",
        "それぞれの AI エージェントで接続先をどう制限するかは、その AI エージェントの提供元にご確認ください。")

# 4 今の課題 -------------------------------------------------------------------
s = figslide("今は、鍵が利用者ひとりひとりの手元に散らばっている", "PROBLEM",
             leg=[(RED, "今の問題"), (GRY, "他社の製品")])


def now(sl, t_, x, y, w):
    us = [other(sl, x, y + i * 84, 300, 64, f"利用者 {c} の\nAI エージェント", size=16) for i, c in enumerate("ABC")]
    ks = [bad(sl, x + 340, y + i * 84, 200, 64, "自分の鍵") for i in range(3)]
    ss = [other(sl, x + 700, y + 30 + i * 110, 260, 64, n) for i, n in enumerate(["GitHub", "その他の SaaS"])]
    for u, k in zip(us, ks):
        line(sl, u, 3, k, 1, color=MUTED)
        for v in ss:
            line(sl, k, 3, v, 1, color=MUTED, width=1.25)
    text(sl, x + 990, y, 210, 240, "鍵の数だけ\n管理の穴が\n増える", size=22, bold=True, color=RED)
    for i, (h_, b_) in enumerate([("止められない", "退職や漏えいのとき\nすぐに無効にできない"),
                                  ("入れ替えられない", "入れ替えを\n利用者まかせにするしかない"),
                                  ("追えない", "誰の鍵での操作かを\n1 か所で確かめられない")]):
        box(sl, x + i * 400, y + 270, 380, 120, "", radius=0.06)
        text(sl, x + i * 400 + 20, y + 280, 340, 36, h_, size=20, bold=True, color=RED)
        text(sl, x + i * 400 + 20, y + 318, 340, 64, b_, size=17)


s.raw(now, 400)
s.notes("今の状態です。利用者ひとりひとりが自分で鍵を発行し、自分の AI エージェントに登録しています。",
        "この形では、鍵を止める、入れ替える、使われ方を追う、の 3 つがどれも利用者まかせになります。目指すのは、利用者が SaaS の鍵を持たない形です。")

# 5 目指す形 -------------------------------------------------------------------
s = figslide("目指す形: 利用者は鍵を持たず、入口を 1 本にする", "TARGET")


def target(sl, t_, x, y, w):
    text(sl, x, y, 560, 36, "今", size=21, bold=True, align="center")
    text(sl, x + 640, y, 560, 36, "これから", size=21, bold=True, align="center")
    for i in range(3):
        a = other(sl, x, y + 50 + i * 80, 170, 60, "AI エージェント", size=15)
        k = bad(sl, x + 200, y + 50 + i * 80, 130, 60, "鍵")
        line(sl, a, 3, k, 1, color=MUTED)
        g = other(sl, x + 380, y + 50 + i * 80, 180, 60, "SaaS")
        line(sl, k, 3, g, 1, color=MUTED)
    ts = [other(sl, x + 640, y + 50 + i * 80, 170, 60, "AI エージェント", size=15) for i in range(3)]
    gw = aws(sl, x + 860, y + 110, 170, 80, "Gateway")
    vault = aws(sl, x + 860, y + 250, 170, 60, "Identity\n鍵はここだけ", size=15)
    sa = [other(sl, x + 1080, y + 70 + i * 120, 120, 60, "SaaS") for i in range(2)]
    for a in ts:
        line(sl, a, 3, gw, 1)
    for b in sa:
        line(sl, gw, 3, b, 1)
    line(sl, vault, 0, gw, 2, color=BLU, head=True)
    mine(sl, x + 640, y + 320, 390, 50, "利用者は Entra ID でサインイン", size=16)


s.raw(target, 380)
s.notes("目指す形です。利用者の AI エージェントは鍵を持たず、MCP の接続先を Gateway の 1 本にします。SaaS の鍵は AgentCore Identity だけが持ちます。",
        "利用者は Entra ID でサインインし、その証明だけで Gateway を使います。")

