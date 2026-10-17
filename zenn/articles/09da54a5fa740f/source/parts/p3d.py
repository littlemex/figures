
# 17 番の切り分けの直し方を、A・B・C で 1 ページずつ手順にする -------------------------
OWN = {"お客様": mine, "AWS": aws, "提供元": other}
LEG_STEP = [(RED, "症状"), (YEL, "原因"), (GRN, "お客様の作業"), (BLU, "AWS の設定"), (GRY, "提供元に確認")]


def steps_fig(sl, t_, x, y, symptom, cause, steps, verify, top=0):
    bad(sl, x, y, 580, 50, "症状: " + symptom, size=16)
    warn(sl, x + 614, y, 580, 50, "原因: " + cause, size=16)
    yy = y + 64
    for n, (who, where, body) in enumerate(steps, 1):
        OWN[who](sl, x, yy, 230, 46, f"{n}. {where}", size=15)
        box(sl, x + 246, yy, 948, 46, body, size=16, bold=False, align="left")
        yy += 53
    mine(sl, x, yy + 4, 1194, 48, "直ったかの確かめ方: " + verify, size=16)


def fixpage(title, eyebrow, symptom, cause, steps, verify, foot, notes):
    s_ = figslide(title, eyebrow, leg=LEG_STEP)
    h = 64 + 53 * len(steps) + 54
    s_.raw(lambda sl, t_, x, y, w: steps_fig(sl, t_, x, y, symptom, cause, steps, verify), h)
    if foot:
        s_.text(foot, size=15)
    s_.notes(*notes)
    return s_


fixpage("A の直し方 (方法 1): 管理者が AI エージェントを前もって Entra ID に登録する", "FIX A-1",
        "サインイン画面が出ない", "AI エージェントが自分をアプリの名簿に登録できない",
        [("提供元", "AI エージェント", "client ID を入れる欄と、サインイン後に戻る先 (リダイレクト URI) を確かめる"),
         ("お客様", "Entra ID", "AI エージェント用のアプリを登録し、戻る先を入れる。client ID を控える"),
         ("お客様", "Entra ID", "このアプリで Gateway 用の scope を公開する (公式サンプルは 1 つのアプリで兼ねる)"),
         ("お客様", "AI エージェント", "控えた client ID を AI エージェントの管理画面に入れる"),
         ("AWS", "Gateway", "allowed audiences に、このアプリの client ID を入れる")],
        "サインイン画面が出て、サインイン後に Gateway の AI エージェント一覧が返る",
        "設定の手順は " + L("Entra ID との連携", "entra") + "。AI エージェント側の入れ方は提供元にご確認ください。",
        ("方法 1 は、AI エージェントに client ID を入れる欄がある場合の直し方です。",
         "管理者が Entra ID に AI エージェント用のアプリを登録し、もらった client ID を AI エージェントに入れます。AI エージェントが自分で名簿に登録する必要がなくなるので、サインイン画面に進めます。"))

fixpage("A の直し方 (方法 2): 自動登録の依頼に応える中継サーバーを、Gateway の手前に置く", "FIX A-2",
        "サインイン画面が出ない", "AI エージェントが自動登録しかできない",
        [("お客様", "Entra ID", "AI エージェント用のアプリを前もって登録し、client ID を控える"),
         ("お客様", "中継サーバーを作る", "API Gateway と Lambda で、MCP の呼び出しを Gateway へ渡す中継サーバーを作る"),
         ("お客様", "中継サーバーの案内", "受付と発行所の場所の問い合わせに、Entra ID の場所を答える"),
         ("お客様", "中継サーバーの登録", "AI エージェントの自動登録の依頼に、控えた client ID を返す"),
         ("提供元", "AI エージェント", "MCP の接続先を中継サーバーの URL にできるかを確かめる")],
        "AI エージェントが中継サーバーから client ID を受け取り、Entra ID でサインインして Gateway を呼べる",
        "実装例: " + L("Entra ID と Gateway のサンプル", "s_entra") + "、" + L("中継サーバーの Lambda", "s_proxy") + "。トークンを出すのは Entra ID のままなので、Gateway の照合の設定は変えない。",
        ("方法 2 は、AI エージェントが自動登録しかできない場合の直し方です。AWS の公式サンプルでは、API Gateway と Lambda で作った中継サーバーを Gateway の手前に置きます。",
         "中継サーバーは、AI エージェントの自動登録の依頼に、管理者が前もって Entra ID に登録した client ID を返します。トークンを出すのは Entra ID のままなので、Gateway の照合の設定は変えずに済みます。"))

fixpage("B の直し方: 通行証の中身と、Gateway の照合条件を合わせる", "FIX B",
        "サインインできたが、Gateway が 401 を返す", "通行証の宛先や権限が照合条件と合わない",
        [("お客様", "原因を見る", "AI エージェントが受け取ったトークンの中身を読み、iss、aud、scp の値を控える"),
         ("お客様", "Entra ID", "アプリの manifest で accessTokenAcceptedVersion=2 にする"),
         ("お客様", "Entra ID", "API を公開して scope を作り、AI エージェントがその scope を頼むようにする"),
         ("AWS", "Gateway", "discovery URL を v2.0 のものにし、allowed audiences に scope を公開したアプリの ID を入れる"),
         ("AWS", "Gateway", "allowed scopes に、作った scope を入れる")],
        "控えた iss、aud、scp が Gateway の条件と一致し、Gateway が 200 を返す",
        "設定の値は " + L("Entra ID との連携", "entra") + " と " + L("受け付け時の確認", "jwt") + "。断られた理由は " + L("Gateway のログ", "gwobs") + " でも確かめられる。",
        ("B は、サインインはできたのに Gateway が通さない場合です。通行証の中身と Gateway の照合条件がずれています。",
         "まずトークンの中身を読み、発行元、宛先、権限の値を控えます。そのうえで Entra ID のアプリを v2.0 のトークンを出す設定にし、API と scope を作ります。Gateway の側は、discovery URL、許可する宛先、許可する権限をその値に合わせます。"))

fixpage("C の直し方: AI エージェントが通行証をもらい直せるようにする", "FIX C",
        "最初は動くが、トークンの期限のころに止まる", "AI エージェントが期限前にトークンを更新できていない",
        [("お客様", "原因を見る", "止まった時刻と、トークンの期限 (exp) の時刻が近いかを比べる"),
         ("提供元", "AI エージェント", "リフレッシュトークンで更新できるか、offline_access の scope を頼めるかを確かめる"),
         ("お客様", "Entra ID", "アプリがリフレッシュトークンを出せるよう、offline_access を許可する"),
         ("お客様", "判断", "AI エージェントが更新できないなら、Gateway の対象から外すか、期限ごとに再サインインにする")],
        "トークンの期限を過ぎても、サインインし直さずに Gateway を呼べる",
        "更新の決まりは " + L("MCP の認可の仕様", "mcpauth") + " にある。トークンの期限を長くして逃げるのは、漏れたときの危険が大きいので勧めない。",
        ("C は、最初は動くのにトークンの期限のころに止まる場合です。AI エージェントが期限前にトークンを更新できていません。",
         "止まった時刻とトークンの期限を比べて確かめたら、AI エージェントの提供元にリフレッシュトークンでの更新に対応しているかを確かめます。Entra ID の側では、リフレッシュトークンを出せるように offline_access を許可します。",
         "AI エージェントが更新に対応していなければ、その AI エージェントを Gateway の対象から外すか、期限ごとに再サインインする運用にするかをお決めください。"))
