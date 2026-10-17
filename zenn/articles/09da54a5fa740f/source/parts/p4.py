
# 13 AppFabric ------------------------------------------------------------------
s = figslide("AppFabric は freee に対応しておらず、GitHub だけなら使わなくて済む", "AUDIT LOG")


def appfabric(sl, t_, x, y, w):
    text(sl, x, y, 574, 36, "AppFabric を通す", size=21, bold=True, align="center")
    text(sl, x + 620, y, 574, 36, "今回の案: GitHub から直接送る", size=21, bold=True, align="center")
    g1 = other(sl, x + 20, y + 60, 220, 60, "GitHub")
    f1 = other(sl, x + 20, y + 150, 220, 60, "freee")
    af = aws(sl, x + 300, y + 60, 240, 60, "AppFabric")
    s1 = aws(sl, x + 300, y + 200, 240, 60, "S3")
    line(sl, g1, 3, af, 1)
    line(sl, af, 2, s1, 0)
    bad(sl, x + 20, y + 240, 220, 50, "非対応", size=17)
    warn(sl, x + 20, y + 310, 520, 56, "利用者 1 人あたり月 3 ドル", size=17)
    g2 = other(sl, x + 640, y + 60, 220, 60, "GitHub")
    s2 = aws(sl, x + 940, y + 60, 230, 60, "S3")
    line(sl, g2, 3, s2, 1)
    mine(sl, x + 640, y + 150, 530, 60, "Enterprise Cloud の送信機能を使う", size=17)
    warn(sl, x + 640, y + 230, 530, 56, "freee は取り方を確認する", size=17)
    mine(sl, x + 640, y + 310, 530, 56, "AppFabric の利用者ごとの料金はない", size=17)
    _ = f1


s.raw(appfabric, 370)
s.text("出典: " + L("AppFabric の対応アプリ", "afapps") + "、" + L("GitHub の設定", "afgh") + "、" + L("AppFabric の料金", "afprice") + "、" + L("GitHub の送信機能", "ghstream"), size=16, muted=True)
s.notes("AppFabric は freee に対応していません。GitHub には対応していますが、利用者 1 人あたり月 3 ドルかかり、200 人なら月 600 ドルです。",
        "GitHub Enterprise Cloud には監査ログを S3 へ直接送る機能があるので、GitHub と freee の 2 つだけなら、こちらを第一候補にします。")

# 14 freee ---------------------------------------------------------------------
s = figslide("freee は、監査ログの取り方を freee 社に確かめるのが先", "AUDIT LOG",
             leg=[(YEL, "確かめること"), (GRN, "取れなかったときの案")])


def freee(sl, t_, x, y, w):
    qs = ["ログイン、権限の変更、帳票の作成・修正・削除の記録が取れるか",
          "取り方は API か、画面からの書き出しか",
          "何日分さかのぼれるか、保管される期間",
          "必要なプランと料金"]
    for i, q in enumerate(qs):
        warn(sl, x, y + i * 72, 760, 58, q, size=17)
    mine(sl, x + 810, y, 384, 130, "書き出ししかなければ\n人が定期的に S3 へ置く", size=17)
    mine(sl, x + 810, y + 158, 384, 130, "取れなければ\n見張らないことを\nお客様が判断する", size=17)


s.raw(freee, 300)
s.text(L("freee の開発者向け資料", "freee") + "には、監査ログを取る API が見当たりません。", size=18)
s.notes("freee は、公開されている開発者向けの資料に監査ログを取る API が見当たりません。ここに並べた 4 つを freee 社にご確認ください。",
        "書き出ししかなければ、人が定期的に S3 へ置く手順にします。取れなければ、見張らないことを受け入れるかをお客様にご判断いただきます。")

# 15 ログの構成 ------------------------------------------------------------------
s = figslide("推奨構成: S3 に集め、定型 SQL を定期実行して通知", "AUDIT LOG")


def logarch(sl, t_, x, y, w):
    gh = other(sl, x, y + 20, 230, 60, "GitHub")
    ct = aws(sl, x, y + 110, 230, 60, "CloudTrail", size=17)
    box(sl, x + 280, y - 6, 270, 200, "", fill=None, stroke=MUTED, dash=None, radius=0.05)
    text(sl, x + 290, y + 150, 250, 34, "ログ専用のアカウント", size=15, color=MUTED, align="center")
    s3 = aws(sl, x + 310, y + 50, 210, 80, "S3\nログの原本", size=18)
    at = aws(sl, x + 640, y + 50, 230, 80, "Athena\n定型 SQL", size=18)
    sc = aws(sl, x + 300, y + 260, 240, 64, "EventBridge\nScheduler", size=16)
    sf = aws(sl, x + 640, y + 260, 230, 64, "Step Functions", size=17)
    sn = aws(sl, x + 960, y + 210, 230, 60, "SNS で通知", size=17)
    db = aws(sl, x + 960, y + 300, 230, 60, "通知済みの記録", size=16)
    line(sl, gh, 3, s3, 1)
    line(sl, ct, 3, s3, 1)
    line(sl, s3, 3, at, 1)
    line(sl, sc, 3, sf, 1)
    line(sl, sf, 0, at, 2)
    line(sl, sf, 3, sn, 1)
    line(sl, sf, 3, db, 1, color=MUTED, width=1.25)
    box(sl, x + 620, y + 30, 590, 350, "", fill=None, stroke=GRN, radius=0.04)
    text(sl, x + 900, y + 30, 300, 34, "お客様が作る部分", size=15, color=GRN, align="right")


s.raw(logarch, 390)
s.text(L("Step Functions", "sfnathena") + " が SQL の完了を待って判定し、失敗も通知します。日付で" + L("読む範囲を区切る", "athpart") + "と速く安くなります。", size=17)
s.notes("S3 に集めて、Athena の定型 SQL を定期的に実行する形をおすすめします。Gateway の呼び出しの記録も同じ場所に集めます。",
        "EventBridge Scheduler だけでは SQL の完了を待って判定するところまでつながらないので、最初から Step Functions を入れます。緑の枠の中は、お客様が作って持ち続ける部分です。")

# 16 証拠として残す ---------------------------------------------------------------
s = figslide("ログを証拠として残すための 3 つの備え", "AUDIT LOG", leg=None)


def evidence(sl, t_, x, y, w):
    cards = [("消されない", ["ログ専用のアカウントに置く", "Object Lock で決めた期間は消せない", "暗号化の鍵を消す権限も分ける"]),
             ("止まったら気づく", ["最後に成功した時刻を見張る", "見張りが止まっても別の経路で知らせる", "試しのログで通しを確かめる"]),
             ("重ならない・見逃さない", ["ログの ID で重なりを除く", "時刻は世界標準時で持つ", "遅れて届く分も検索する"])]
    for i, (h_, rows) in enumerate(cards):
        cx = x + i * 404
        box(sl, cx, y, 386, 380, radius=0.04)
        text(sl, cx + 20, y + 14, 346, 40, h_, size=21, bold=True, color=GRN, align="center")
        for j, r in enumerate(rows):
            mine(sl, cx + 20, y + 74 + j * 98, 346, 80, r, size=17)


s.raw(evidence, 380)
s.text(L("Object Lock", "objlock") + " の期間は後から縮められないので先に決めます。GitHub の組織の監査ログ画面は" + L("直近 180 日分", "ghorglog") + "です。", size=17)
s.notes("ログを集めるだけでは、消された、止まった、重なった、の 3 つに気づけません。",
        "ログは専用のアカウントに置いて決めた期間は消せないようにし、最後に成功した時刻を見張り、ログの ID で重なりを除いてから数えます。")
