
# 8 呼び出しの流れ ---------------------------------------------------------------
s = figslide("SaaS の鍵は Gateway の中だけで使い、利用者には渡さない", "FLOW", sub="1 回の呼び出しの流れ")


def flow(sl, t_, x, y, w):
    steps = [(mine, "1", "Entra ID で\nサインイン"), (other, "2", "Gateway を\n呼ぶ"),
             (aws, "3", "本人と権限を\n確かめる"), (aws, "4", "Identity から\n鍵を受け取る"),
             (aws, "5", "SaaS を呼んで\n結果を返す"), (aws, "6", "呼び出しを\n記録する")]
    W = 180
    for i, (fn, n, body) in enumerate(steps):
        cx = x + i * (W + 23)
        fn(sl, cx, y + 40, W, 110, body, size=17)
        text(sl, cx, y, W, 36, n, size=22, bold=True, align="center", color=MUTED)
        if i < 5:
            sh.arrow(sl, t_, cx + W, y + 95, cx + W + 23, y + 95, color=WHITE, width=2.5)
    warn(sl, x, y + 190, 1194, 60, "利用者の手元に残るのは Entra ID のトークンだけ。SaaS の鍵は残らない", size=18)


s.raw(flow, 260)
s.bullets(["3 で使う確認: " + L("受け付け時の確認", "jwt") + "と " + L("Policy", "policy") + "。4 と 5: " + L("送り先ごとの認証方式", "outbound"),
           "Entra ID で利用者を止めると、トークンの期限が切れたあとは Gateway 経由の経路がすべて止まる"], size=18)
s.notes("1 回の呼び出しの流れです。利用者が Entra ID でサインインし、AI エージェントはそのトークンを付けて Gateway を呼びます。",
        "Gateway は本人と権限を確かめ、Identity から鍵を受け取って SaaS を呼び、結果を返します。SaaS の鍵が利用者の手元に渡る場面はありません。")

# 9 credential provider の分け方 ------------------------------------------------
s = figslide("鍵の登録は、社内利用なら SaaS ごとに 1 つから始められる", "CREDENTIAL PROVIDER",
             sub="Identity に鍵を登録する単位 (credential provider) は、使い方で決まる")


def granularity(sl, t_, x, y, w):
    for cx, head, fn, rows, foot in (
            (x, "今回: 社内で使う", mine, ["GitHub 用 1 つ", "freee 用 1 つ", "その他の SaaS ごとに 1 つ"], "SaaS の数だけ"),
            (x + 620, "参考: 他社に提供する場合", warn, ["会社 X 用の OAuth アプリ", "会社 Y 用の OAuth アプリ", "会社ごとに分かれる鍵"], "会社ごとに別の鍵が要るときだけ")):
        box(sl, cx, y, 574, 310, radius=0.04)
        text(sl, cx + 20, y + 10, 534, 40, head, size=21, bold=True, align="center")
        for i, r in enumerate(rows):
            fn(sl, cx + 40, y + 60 + i * 68, 494, 56, r, size=18)
        text(sl, cx + 20, y + 268, 534, 34, foot, size=17, color=MUTED, align="center")


s.raw(granularity, 310)
s.bullets(["本番と検証を分ける、権限の違う鍵を分ける、といった場合は、その数だけ登録する",
           "利用者ごとのトークンは、Identity の " + L("token vault", "vault") + " に保管される",
           "登録できる数は 1 アカウント 1 リージョンあたり種類ごとに 50 個で、申請で増やせる (" + L("上限", "limits") + ")"], size=17)
s.notes("Identity に鍵を登録する単位を credential provider と呼びます。登録は、SaaS に作ったアプリや鍵 1 つにつき 1 つです。今回は社内でのご利用なので、まずは SaaS ごとに 1 つから始められます。本番と検証を分けるときなどは、その数だけ足します。",
        "複数の会社に提供するサービスで、会社ごとに別の OAuth アプリや鍵が要る場合は、会社ごとに分けます。",
        "利用者ごとの OAuth を使う場合も、登録は SaaS ごとに 1 つです。利用者が同意して得たトークンは token vault に保管されます。")

# 10 鍵の持ち方と入れ替え ---------------------------------------------------------
s = figslide("鍵は預けるだけでなく、入れ替えと停止まで決めておく", "ROTATION",
             sub="送り先の認証方式は送り先ごとに選ぶ。会社のアプリとしての OAuth も選べる")


def rotation(sl, t_, x, y, w):
    text(sl, x, y, 574, 36, "利用者ごとの鍵 (OAuth)", size=21, bold=True, align="center")
    text(sl, x + 620, y, 574, 36, "共有の API キー", size=21, bold=True, align="center")
    o = [(mine, "会社が承認した OAuth アプリ"), (other, "利用者が最初に同意"), (aws, "トークンは Identity が保管"),
         (mine, "退職時は同意を取り消す")]
    for i, (fn, b) in enumerate(o):
        fn(sl, x + 60, y + 50 + i * 74, 454, 58, b, size=17)
        if i < 3:
            sh.arrow(sl, t_, x + 287, y + 108 + i * 74, x + 287, y + 124 + i * 74, color=WHITE, width=2)
    k = [(mine, "1. SaaS で新しい鍵を発行"), (aws, "2. Secrets Manager を更新"), (mine, "3. 動くことを確かめる"),
         (mine, "4. SaaS で古い鍵を無効化")]
    for i, (fn, b) in enumerate(k):
        fn(sl, x + 680, y + 50 + i * 74, 454, 58, b, size=17)
        if i < 3:
            sh.arrow(sl, t_, x + 907, y + 108 + i * 74, x + 907, y + 124 + i * 74, color=WHITE, width=2)


s.raw(rotation, 350)
s.text("鍵は " + L("Secrets Manager に置ける", "providers") + "。" + L("入れ替え", "smrot") + "は定期的に動かせるが、SaaS で鍵を発行・無効化する処理はお客様が作る。", size=17)
s.notes("鍵の預け方は 2 通りです。GitHub のように OAuth に対応する SaaS は、会社が承認したアプリを使い、利用者ごとのトークンを Identity に預けます。本人の権限で操作されるので、SaaS 側の記録で本人を見分けやすくなります。記録のされ方は各 SaaS にご確認ください。",
        "API キーしかない SaaS は、会社の鍵を預けます。入れ替えは Secrets Manager の仕組みで定期的に動かせますが、SaaS で鍵を発行して無効にする処理は SaaS ごとに作る必要があります。")

# 11 抜け道を狭める ---------------------------------------------------------------
s = figslide("抜け道は、AI エージェントの管理機能と SaaS 側の制限で狭める", "GUARDRAILS",
             sub="AI エージェントごとの設定方法は、各 AI エージェントの提供元にご確認ください")


def guard(sl, t_, x, y, w):
    tool = other(sl, x, y + 120, 260, 80, "MCP を使う\nAI エージェント", size=17)
    gw = aws(sl, x + 460, y + 40, 280, 70, "Gateway")
    saas = other(sl, x + 940, y + 120, 254, 80, "SaaS")
    line(sl, tool, 0, gw, 1, color=GRN, width=3)
    line(sl, gw, 3, saas, 0, color=GRN, width=3)
    line(sl, tool, 3, saas, 1, color=RED, dashed=True, width=3)
    text(sl, x + 300, y + 175, 600, 34, "個人の鍵で直接つなぐ抜け道", size=17, color=RED, align="center")
    mine(sl, x, y + 240, 574, 96, "AI エージェント側: 接続先を Gateway だけに\n絞れるかを提供元にご確認", size=16)
    mine(sl, x + 620, y + 240, 574, 96, "SaaS 側: 個人で発行した鍵を制限する\n例: GitHub の組織設定", size=17)


s.raw(guard, 340)
s.text("絞る機能が無い AI エージェントは、SaaS 側の制限と端末側の通信の制御で補います。GitHub の例: " + L("個人用トークンの制限", "patpol"), size=17)
s.notes("Gateway を用意しても、個人の鍵で SaaS に直接つなげる抜け道が残っていては意味がありません。",
        "AI エージェント側では管理機能で MCP の接続先を Gateway だけに絞り、SaaS 側では個人で発行した鍵を制限します。AI エージェントごとの設定方法は、それぞれの提供元にご確認ください。")

# 12 最初に確かめる ---------------------------------------------------------------
s = figslide("AI エージェントが Entra ID のトークンで Gateway につながるかを、最初に確かめる", "VERIFY")


def verify(sl, t_, x, y, w):
    warn(sl, x, y, 1194, 70, "1. お使いの AI エージェントで、トークンを取って更新しながら Gateway を呼べるか", size=19)
    rows = ["2. 利用者ごとの OAuth なら、初回の同意画面を AI エージェントが利用者に出せるか",
            "3. Policy で、利用者や役割ごとに呼べるツールを分けられるか",
            "4. 鍵の入れ替え、同意の取り消し、退職時の停止ができるか"]
    for i, r in enumerate(rows):
        mine(sl, x, y + 86 + i * 66, 1194, 54, r, size=18)


s.raw(verify, 320)
s.bullets(["1 が通らない例: AI エージェントが自分を Entra ID のアプリの名簿に自動で登録する方式しか持たない場合",
           "参考記事: " + L("Cognito の例", "z_cog") + "、" + L("Auth0 の例", "z_dcr"),
           "代わりの案: 自動登録を受け付ける認証の仕組みを Entra ID の手前に 1 つ足す"], size=17)
s.notes("いちばん大事なのは 1 つ目です。お使いの AI エージェントが Entra ID のトークンを取得し、更新しながら Gateway を呼べるかで、この構成が成り立つかが決まります。",
        "AI エージェントが接続用のアプリを自動で登録する方式を前提にしている場合は、つながらないことがあります。お使いの AI エージェントの対応は提供元にご確認ください。その場合は、自動登録に対応した認証の仕組みを Entra ID の前に足す案があります。")

# 12b 止まった場所で切り分ける ------------------------------------------------------
s = figslide("止まった場所で、どこが足りないかを切り分ける", "TROUBLESHOOT",
             leg=[(RED, "止まった場所"), (YEL, "足りないもの"), (GRN, "直し方")])


def triage(sl, t_, x, y, w):
    rows = [("サインイン画面が出ない", "A. AI エージェントが自分を\nアプリの名簿に自動で登録できない", "事前登録するか、\n中継サーバーを手前に置く"),
            ("サインインはできたが\nGateway が通さない", "B. 通行証の宛先が\nGateway の照合条件と合わない", "Entra ID のアプリ登録と\nGateway の照合条件を合わせる"),
            ("最初は動くが\n期限のころに止まる", "C. AI エージェントが期限前に\n通行証をもらい直せない", "AI エージェントの\n提供元に確認する")]
    text(sl, x, y, 360, 32, "止まった場所", size=18, bold=True, color=MUTED, align="center")
    text(sl, x + 420, y, 380, 32, "足りないもの", size=18, bold=True, color=MUTED, align="center")
    text(sl, x + 860, y, 334, 32, "直し方", size=18, bold=True, color=MUTED, align="center")
    for i, (a, b, c) in enumerate(rows):
        yy = y + 44 + i * 110
        ba = bad(sl, x, yy, 360, 92, a, size=17)
        bb = warn(sl, x + 420, yy, 380, 92, b, size=16)
        bc = mine(sl, x + 860, yy, 334, 92, c, size=16)
        line(sl, ba, 3, bb, 1)
        line(sl, bb, 3, bc, 1)


s.raw(triage, 380)
s.text("B は設定を合わせれば直ることが多い。A と C は、それぞれ認証の仕組みと AI エージェントの作りの問題です。", size=17)
s.notes("実際に試して止まったときは、止まった場所で原因を切り分けます。",
        "サインイン画面が出なければ、AI エージェントが自分を Entra ID のアプリの名簿に自動で登録できていないことが原因の候補です。サインインできたのに Gateway が通さなければ、通行証の宛先や権限の書き方のずれで、設定で直ることが多いです。トークンの期限のころに止まるなら、AI エージェントが通行証をもらい直せていません。")

# 16a A の直し方 ---------------------------------------------------------------
s = figslide("A の直し方: 名簿に載る方法を、AI エージェントに合わせて 2 通りから選ぶ", "FIX A")


def fixa(sl, t_, x, y, w):
    text(sl, x, y, 574, 34, "方法 1: 管理者が前もって名簿に載せる", size=19, bold=True, align="center")
    text(sl, x + 620, y, 574, 34, "方法 2: 自動登録に応える中継サーバーを置く", size=19, bold=True, align="center")
    adm = mine(sl, x + 20, y + 50, 250, 60, "管理者が Entra ID に\nAI エージェントを登録", size=15)
    cid = mine(sl, x + 300, y + 50, 250, 60, "client ID を\nAI エージェントに設定", size=15)
    t1 = other(sl, x + 20, y + 160, 250, 60, "AI エージェント", size=17)
    en1 = other(sl, x + 300, y + 160, 250, 60, "Entra ID", size=17)
    gw1 = aws(sl, x + 160, y + 270, 250, 60, "Gateway", size=17)
    line(sl, adm, 3, cid, 1)
    line(sl, cid, 2, t1, 0, color=GRN, dashed=True)
    line(sl, t1, 3, en1, 1)
    line(sl, t1, 2, gw1, 1)
    warn(sl, x + 20, y + 350, 530, 50, "条件: AI エージェントに client ID の設定欄がある", size=15)
    t2 = other(sl, x + 640, y + 50, 230, 60, "AI エージェント", size=17)
    az = mine(sl, x + 940, y + 50, 250, 60, "中継サーバー\nAPI Gateway+Lambda", size=14)
    en2 = other(sl, x + 940, y + 160, 250, 60, "Entra ID で\nサインイン", size=15)
    gw2 = aws(sl, x + 640, y + 270, 230, 60, "Gateway", size=17)
    line(sl, t2, 3, az, 1)
    line(sl, az, 2, en2, 0, color=GRN, dashed=True)
    line(sl, t2, 2, gw2, 0)
    text(sl, x + 890, y + 270, 300, 60, "トークンは Entra ID が出す\nGateway の照合はそのまま", size=15, color=BLU)
    warn(sl, x + 640, y + 350, 550, 50, "中継サーバーはお客様が作って運用する", size=15)


s.raw(fixa, 400)
s.text("方法 2 の実装例: " + L("Entra ID と Gateway のサンプル", "s_entra") + "。どちらが使えるかは、AI エージェントの提供元にご確認ください。", size=16)
s.notes("A の直し方は 2 通りです。",
        "1 つ目は、管理者が前もって Entra ID に AI エージェントを登録し、もらった client ID を AI エージェントに設定する方法です。AI エージェントに client ID の設定欄があれば、いちばん簡単です。",
        "2 つ目は、自動登録を受け付ける認可サーバーを窓口として手前に置き、利用者のサインインは Entra ID に任せる方法です。Gateway は窓口が出すトークンを照合します。窓口を運用する手間と、登録を乱用されないための備えが要ります。")

