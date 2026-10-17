
# 接続図: 直す前と直した後 ------------------------------------------------------
LEG_WIRE = [(RED, "止まる線"), (GRN, "直した後に通る線"), (BLU, "AWS"), (GRY, "他社の製品")]


def before_after(sl, t_, x, y, before, after):
    text(sl, x, y, 140, 40, "直す前", size=19, bold=True, color=RED)
    text(sl, x, y + 170, 140, 40, "直した後", size=19, bold=True, color=GRN)
    before(sl, t_, x + 150, y)
    after(sl, t_, x + 150, y + 170)


def wirepage(title, eyebrow, before, after, notes, h=400):
    s_ = figslide(title, eyebrow, leg=LEG_WIRE)
    s_.raw(lambda sl, t_, x, y, w: before_after(sl, t_, x, y, before, after), h)
    s_.notes(*notes)
    return s_


def a1_before(sl, t_, x, y):
    tl = other(sl, x, y + 20, 220, 64, "AI エージェント")
    en = other(sl, x + 420, y + 20, 260, 64, "Entra ID の\nアプリの名簿", size=16)
    line(sl, tl, 3, en, 1, color=RED, dashed=True, width=2.5)
    text(sl, x + 225, y - 10, 200, 30, "自分を登録したい", size=15, color=RED, align="center")
    bad(sl, x + 720, y + 20, 320, 64, "受け付けられず止まる", size=16)


def a1_after(sl, t_, x, y):
    adm = mine(sl, x, y, 220, 60, "管理者", size=17)
    en = other(sl, x + 300, y, 260, 60, "Entra ID の\nアプリの名簿", size=16)
    tl = other(sl, x, y + 110, 220, 60, "AI エージェント", size=17)
    si = other(sl, x + 300, y + 110, 260, 60, "Entra ID で\nサインイン", size=16)
    gw = aws(sl, x + 640, y + 110, 200, 60, "Gateway", size=17)
    sa = other(sl, x + 900, y + 110, 150, 60, "SaaS", size=17)
    line(sl, adm, 3, en, 1, color=GRN, width=2.5)
    line(sl, en, 2, tl, 0, color=GRN, dashed=True)
    text(sl, x + 470, y + 66, 320, 30, "client ID を AI エージェントに設定", size=14, color=GRN)
    line(sl, tl, 3, si, 1, color=GRN, width=2.5)
    line(sl, si, 3, gw, 1, color=GRN, width=2.5)
    line(sl, gw, 3, sa, 1, color=GRN, width=2.5)


wirepage("A の直し方 1: 管理者が前もって AI エージェントをアプリの名簿に載せる", "WIRING A-1", a1_before, a1_after,
         ("直す前は、AI エージェントが自分を Entra ID のアプリの名簿に登録しようとして、受け付けられずに止まります。",
          "直した後は、管理者が前もってアプリの名簿に AI エージェントを載せ、もらった client ID を AI エージェントに設定します。AI エージェントはサインインして Gateway を呼べるようになります。"))


def a2_after(sl, t_, x, y):
    tl = other(sl, x, y + 110, 200, 60, "AI エージェント", size=17)
    px = mine(sl, x + 270, y, 300, 70, "中継サーバー: 登録の依頼に\n登録済みの client ID を返す", size=14)
    en = other(sl, x + 640, y, 220, 70, "Entra ID で\nサインイン", size=16)
    px2 = mine(sl, x + 270, y + 110, 300, 60, "中継サーバーが\n呼び出しを渡す", size=14)
    gw = aws(sl, x + 640, y + 110, 220, 60, "Gateway", size=17)
    sa = other(sl, x + 920, y + 110, 130, 60, "SaaS", size=17)
    line(sl, tl, 0, px, 1, color=GRN, width=2.5)
    line(sl, px, 3, en, 1, color=GRN, dashed=True)
    line(sl, tl, 3, px2, 1, color=GRN, width=2.5)
    line(sl, px2, 3, gw, 1, color=GRN, width=2.5)
    line(sl, gw, 3, sa, 1, color=GRN, width=2.5)


wirepage("A の直し方 2: 自動登録の依頼に応える中継サーバーを、Gateway の手前に置く", "WIRING A-2", a1_before, a2_after,
         ("方法 2 では、API Gateway と Lambda で作った中継サーバーを Gateway の手前に置きます。中継サーバーは、AI エージェントの自動登録の依頼に、管理者が前もって登録した client ID を返します。",
          "AI エージェントはその client ID で Entra ID にサインインし、中継サーバーを通して Gateway を呼びます。トークンを出すのは Entra ID のままです。"))


def c_before(sl, t_, x, y):
    tk = warn(sl, x, y + 20, 360, 64, "通行証の宛先 aud\n= 別のアプリ", size=16)
    gw = aws(sl, x + 470, y + 20, 300, 64, "Gateway の条件\n= 権限を公開したアプリ", size=16)
    line(sl, tk, 3, gw, 1, color=RED, dashed=True, width=2.5)
    bad(sl, x + 820, y + 20, 220, 64, "401 で止まる", size=17)


def c_after(sl, t_, x, y):
    ap = other(sl, x, y + 20, 280, 70, "アプリで Gateway\n用の scope を公開", size=16)
    tk = warn(sl, x + 340, y + 20, 300, 70, "通行証の宛先と権限\n= 公開したアプリと scope", size=16)
    gw = aws(sl, x + 700, y + 20, 200, 70, "Gateway の条件", size=16)
    ok = mine(sl, x + 940, y + 20, 110, 70, "200", size=19)
    line(sl, ap, 3, tk, 1, color=GRN, width=2.5)
    line(sl, tk, 3, gw, 1, color=GRN, width=2.5)
    line(sl, gw, 3, ok, 1, color=GRN, width=2.5)


wirepage("B の直し方: 通行証に書かれた宛先と、受付の条件をそろえる", "WIRING B", c_before, c_after,
         ("直す前は、通行証の宛先が別のアプリになっていて、Gateway の条件と合わずに 401 で止まります。",
          "直した後は、Entra ID のアプリで Gateway 用の scope を公開し、AI エージェントがその scope を頼むようにします。通行証の宛先と権限が Gateway の条件とそろうので、200 が返ります。"))


def b_before(sl, t_, x, y):
    tl = other(sl, x, y + 20, 200, 64, "AI エージェント", size=16)
    t1 = warn(sl, x + 260, y + 20, 260, 64, "通行証\n期限が来る", size=16)
    gw = aws(sl, x + 580, y + 20, 200, 64, "Gateway")
    line(sl, tl, 3, t1, 1, color=MUTED)
    line(sl, t1, 3, gw, 1, color=RED, dashed=True, width=2.5)
    bad(sl, x + 830, y + 20, 210, 64, "期限で止まる", size=17)


def b_after(sl, t_, x, y):
    tl = other(sl, x, y + 70, 200, 64, "AI エージェント", size=16)
    en = other(sl, x + 260, y, 260, 64, "Entra ID\nリフレッシュトークン", size=15)
    t2 = warn(sl, x + 260, y + 100, 260, 64, "新しい通行証", size=16)
    gw = aws(sl, x + 580, y + 100, 200, 64, "Gateway")
    sa = other(sl, x + 840, y + 100, 200, 64, "SaaS")
    line(sl, tl, 0, en, 1, color=GRN, width=2.5)
    line(sl, en, 2, t2, 0, color=GRN, width=2.5)
    line(sl, t2, 3, gw, 1, color=GRN, width=2.5)
    line(sl, gw, 3, sa, 1, color=GRN, width=2.5)
    text(sl, x + 540, y + 10, 300, 40, "期限の前にもらい直す", size=14, color=GRN)


wirepage("C の直し方: 期限の前に、通行証をもらい直す", "WIRING C", b_before, b_after,
         ("直す前は、通行証の期限が来ると、AI エージェントが新しい通行証を持たないまま Gateway を呼び、止まります。",
          "直した後は、AI エージェントが期限の前にリフレッシュトークンで Entra ID から新しい通行証をもらい、そのまま Gateway を呼び続けます。これは AI エージェントの作りによるので、提供元にご確認ください。"))
