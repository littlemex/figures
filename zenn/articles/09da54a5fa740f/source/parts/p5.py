
# 17 見張る操作 ------------------------------------------------------------------
s = d.slide("危険な操作は、GitHub の操作の名前で絞り込めば見つけられる", eyebrow="AUDIT LOG",
            sub="決めた危険な操作を見つける仕組みで、すべての不正を見つけるものではない")
s.table(["見張りたいこと", "操作の名前の例"], [
    ["リポジトリが公開された、削除された", "repo.access、repo.destroy"],
    ["メンバーが加わった、権限が変わった", "org.add_member、org.update_member"],
    ["2 段階認証の必須設定が外された", "org.disable_two_factor_requirement"],
    ["大事なブランチの保護が外された", "protected_branch.destroy"],
    ["いつもより多い clone やダウンロード", "git.clone、repo.download_zip"],
], fracs=[0.5, 0.5], body_size=18, head_size=18)
s.text("操作の名前は " + L("GitHub の一覧", "ghevents") + " にある。git の操作の記録は画面に出ず、API では 7 日分しか取れないので、見張るなら S3 への送信を止めない。", size=17)
s.notes("見張る操作の例です。リポジトリの公開や削除、権限の変更、2 段階認証の解除などは、操作の名前で絞り込めば見つけられます。",
        "clone の量は、普段の量を基準にして比べます。")

# 18 費用 ----------------------------------------------------------------------
s = d.slide("費用の目安: 主な料金は使った量に応じて決まる", eyebrow="COST",
            sub="2026 年 10 月 13 日に料金ページで確かめた値")
s.table(["項目", "料金", "出典"], [
    ["AgentCore Gateway", "ツールの呼び出し 1,000 回あたり 0.005 ドル", L("料金", "acprice")],
    ["Policy in AgentCore", "判定 1,000 回あたり 0.025 ドル", L("料金", "acprice")],
    ["AgentCore Identity", "Gateway 経由なら追加料金なし", L("料金", "acprice")],
    ["CloudTrail のデータイベント", "記録した件数に応じた料金", L("料金", "ctprice")],
    ["Athena", "SQL が読んだデータの量に応じた料金", L("料金", "athprice")],
    ["Secrets Manager", "鍵の数と呼び出しの回数に応じた料金", L("料金", "smprice")],
    ["(比べる相手) AppFabric", "利用者 1 人あたり月 3 ドル", L("料金", "afprice")],
], fracs=[0.34, 0.52, 0.14], body_size=17, head_size=17)
s.text("例: ツールを月 100 万回呼ぶと、呼び出しは 5 ドル、Policy の判定は 25 ドル。Gateway にはツールの検索と登録の料金もある。", size=17)
s.notes("主な料金は使った量に応じて決まります。たとえばツールを月に 100 万回呼ぶと、呼び出しの料金は 5 ドル、Policy の判定は 25 ドルです。",
        "利用者の数、呼び出しの回数、ログの量、保管期間をいただければ、月額を試算します。")

# 19 ご判断と次の一歩 --------------------------------------------------------------
s = figslide("ご判断いただきたいことと、次の一歩", "NEXT",
             leg=[(YEL, "ご判断いただくこと"), (GRN, "次の一歩")])


def nexts(sl, t_, x, y, w):
    ds = ["MCP の接続先を Gateway にそろえる案で検証するか",
          "監査ログを S3 と Athena から始めるか",
          "ログの保管期間と専用アカウント",
          "freee 社への問い合わせの担当"]
    ns = ["お使いのツールで Gateway につながるかを試す",
          "GitHub を登録し、Policy と記録を確かめる",
          "GitHub の監査ログを S3 へ送る",
          "見張る操作を決め、SQL と通知を作る"]
    text(sl, x, y, 574, 36, "ご判断いただくこと", size=21, bold=True, align="center")
    text(sl, x + 620, y, 574, 36, "次の一歩", size=21, bold=True, align="center")
    for i, (a, b) in enumerate(zip(ds, ns)):
        warn(sl, x, y + 50 + i * 80, 574, 64, a, size=17)
        mine(sl, x + 620, y + 50 + i * 80, 574, 64, b, size=17)


s.raw(nexts, 380)
s.text("構築と運用はお客様のアカウントで行います。AWS は AWS のサービスの設計を支援します。各ツールの設定は提供元にご確認ください。", size=17)
s.notes("ご判断いただきたいことは 4 つです。まず、MCP の接続先を Gateway にそろえる案で検証を始めるかをお決めください。",
        "次の一歩は、お使いのツールで Gateway につながるかを試すことです。ここが通れば、GitHub の登録と監査ログの設定に進みます。")

out = d.save(os.path.join(HERE, "devin-keys-and-saas-audit.pptx"))
print("wrote", out, len(d.slides), "slides")
