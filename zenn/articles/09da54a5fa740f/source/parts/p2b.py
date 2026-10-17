
# 6c たとえから実際の仕様へ ---------------------------------------------------------
s = figslide("たとえを実際の仕様に戻す: MCP の認可は OAuth の決まりの組み合わせ", "SPECIFICATIONS", leg=None)
s.table(["たとえ", "実際にやること", "決まり"], [
    ["受付と通行証の発行所の場所を知る", "Gateway が認可サーバーの場所を知らせ、AI エージェントがその設定を読む",
     L("RFC 9728", "rfc9728") + "、" + L("RFC 8414", "rfc8414")],
    ["AI エージェントが自分をアプリの名簿に載せる", "client ID を手に入れる。方法は 3 つで、事前登録、Client ID Metadata Documents、Dynamic Client Registration",
     L("CIMD", "cimd") + "、" + L("RFC 7591", "rfc7591")],
    ["サインインして通行証をもらう", "認可コードの流れで、アクセストークンをもらう。PKCE を使う",
     L("OAuth 2.1", "oauth21") + "、" + L("RFC 7636", "rfc7636")],
    ["通行証に宛先を書いてもらう", "resource で、トークンを使う先が Gateway だと伝える", L("RFC 8707", "rfc8707")],
    ["呼ぶたびに通行証を見せる", "Authorization ヘッダーにトークンを付ける", L("RFC 6750", "rfc6750")],
    ["受付で照合する", "Gateway が発行元、宛先 (aud)、アプリ (client_id)、権限 (scope) を確かめる", L("Gateway の確認", "jwt")],
    ["期限前にもらい直す", "リフレッシュトークンで新しいトークンをもらう", L("OAuth 2.1", "oauth21")],
], fracs=[0.28, 0.52, 0.20], body_size=15, head_size=16)
s.text("全体の決まりは " + L("MCP の認可の仕様 (2026-07-28 版)", "mcpauth") + "。Entra ID とお使いの AI エージェントがどれに対応するかは、各社の資料でご確認ください。", size=16)
s.notes("前のページのたとえを、実際の仕様に戻します。MCP の認可は、OAuth の決まりを組み合わせたものです。",
        "AI エージェントが自分をアプリの名簿に載せる方法は 3 つあります。前もって管理者が登録する事前登録、アプリの情報を URL で示す Client ID Metadata Documents、その場で登録する Dynamic Client Registration です。AI エージェントと Entra ID のどちらもが対応する方法が 1 つもないと、A の場所で止まります。",
        "Entra ID とお使いの AI エージェントがどの方法に対応するかは、それぞれの提供元の資料でご確認ください。")
