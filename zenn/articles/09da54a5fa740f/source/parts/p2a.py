
# 6a 通行証のたとえ: 誰が何を受け持つか ---------------------------------------------
s = figslide("通行証のたとえ: ビルの受付と同じ仕事を、サービスごとに分けて受け持つ", "ROLES",
             sub="社員は AI エージェントを代理人に使い、代理人は機密エリアの通行証を持つ。Gateway はその受付")


def roles(sl, t_, x, y, w):
    rows = [
        ("社員の名簿を持つ", "Entra ID の利用者", mine),
        ("代理人として認めた AI エージェントの名簿を持つ", "Entra ID のアプリ登録", mine),
        ("社員証で本人を確かめ、通行証を出す", "Entra ID", other),
        ("受付で通行証を照合する", "Gateway の受け付け時の確認", aws),
        ("入ってよい部屋かを決める", "Policy in AgentCore", aws),
        ("金庫の鍵を預かり、貸し出す", "AgentCore Identity", aws),
        ("出入りを記録帳に書く", "CloudTrail", aws),
    ]
    text(sl, x, y, 560, 32, "ビルの受付でいうと", size=18, bold=True, color=MUTED, align="center")
    text(sl, x + 660, y, 534, 32, "受け持つサービス", size=18, bold=True, color=MUTED, align="center")
    for i, (job, svc, fn) in enumerate(rows):
        yy = y + 40 + i * 52
        box(sl, x, yy, 560, 44, job, size=17, bold=False)
        sh.arrow(sl, t_, x + 570, yy + 22, x + 650, yy + 22, color=WHITE, width=2)
        fn(sl, x + 660, yy, 534, 44, svc, size=17)


s.raw(roles, 410)
s.notes("この構成を、会社のビルの受付にたとえます。Entra ID へのサインインが社員証、Gateway 用のトークンが機密エリアの通行証、Gateway がその受付です。",
        "社員の名簿と、通行証をもらえるアプリの名簿は、お客様が Entra ID で管理します。通行証を出すのは Entra ID です。",
        "受付で通行証を照合し、入ってよい部屋かを決め、金庫の鍵を貸し出し、出入りを記録するのが AWS の部品です。")

# 6b AI エージェントにできないといけないこと --------------------------------------------------
s = figslide("AI エージェントは、通行証をもらって受付に見せ続けられないといけない", "WHAT THE TOOL MUST DO",
             leg=[(GRY, "AI エージェントと Entra ID の仕事"), (BLU, "AWS の仕事"), (RED, "止まりやすい場所")])


def tooljob(sl, t_, x, y, w):
    steps = [(other, "1. サインイン\n画面へ案内"), (other, "2. Entra ID が\n通行証を出す"), (other, "3. 通行証を\n受け取る"),
             (other, "4. 呼ぶたびに\n見せる"), (aws, "5. 照合して\n通す"), (other, "6. 期限前に\nもらい直す")]
    W = 180
    bs = []
    for i, (fn, body) in enumerate(steps):
        cx = x + i * (W + 23)
        bs.append(fn(sl, cx, y + 40, W, 100, body, size=17))
        if i < 5:
            sh.arrow(sl, t_, cx + W, y + 90, cx + W + 23, y + 90, color=WHITE, width=2.5)
    stops = [(0, "A. AI エージェントが自分を\nアプリの名簿に登録できない"), (5, "C. 期限の前に\n通行証を\n更新できない"), (4, "B. 通行証の宛先が\nGateway の照合\n条件と合わない")]
    for i, body in stops:
        cx = x + i * (W + 23)
        bw = 340 if i == 0 else W + 20
        bad(sl, cx - 10, y + 180, bw, 100, body, size=15)
        sh.arrow(sl, t_, cx + W / 2, y + 180, cx + W / 2, y + 142, color=RED, width=2)
    text(sl, x, y + 292, 1194, 56, "A の補足: Entra ID のアプリの名簿は、管理者が前もってアプリを登録する方式。AI エージェントが自分で名簿に登録する方式 (自動登録) しか持たないと、Entra ID が受け付けず、サインイン画面に進めない。", size=16, color=MUTED)
    text(sl, x, y + 352, 1194, 40, "どれか 1 つでも止まると、利用者は受付で止められ、SaaS を使えない。", size=19, bold=True, color=YEL)


s.raw(tooljob, 400)
s.notes("AI エージェントにできないといけないことは 6 つの流れです。利用者をサインイン画面に案内し、Entra ID が出した通行証を受け取り、Gateway を呼ぶたびに見せ、期限が来たらもらい直します。",
        "止まりやすい場所は 3 つです。1 つ目は、AI エージェントが自分を Entra ID のアプリの名簿に自動で登録できないことです。Entra ID の名簿は管理者が前もって登録する方式なので、自分で登録する方式しか持たない AI エージェントは、サインイン画面に進めません。",
        "2 つ目は期限の前に通行証を更新できないこと、3 つ目は通行証の宛先が Gateway の照合条件と合わないことです。")
