
# 6 部品の役割 -----------------------------------------------------------------
s = figslide("役割の違う部品を組み合わせる", "COMPONENTS",
             sub="鍵を預かる、入口を 1 本にする、使える人を決める、は別々の部品の仕事")


def parts(sl, t_, x, y, w):
    rows = [(aws, "AgentCore Gateway", "MCP の入口を 1 本にまとめ、SaaS へ中継する", "jwt"),
            (aws, "AgentCore Identity", "MCP で使う SaaS の鍵を預かる。鍵の実体は Secrets Manager にも置ける", "providers"),
            (aws, "Policy in AgentCore", "誰がどのツールを呼べるかを決める", "policy"),
            (mine, "Entra ID のアプリ登録", "Gateway を社内アプリにし、利用者をサインインさせる", None),
            (warn, "AWS Agent Registry", "承認した MCP サーバーの目録。任意の部品で、鍵は預からない", "registry")]
    for i, (fn, name, role, key) in enumerate(rows):
        yy = y + i * 76
        fn(sl, x, yy, 360, 62, name, size=18)
        text(sl, x + 390, yy, 800, 62, role + ("  " + L("資料", key) if key else ""), size=18)


s.raw(parts, 380)
s.notes("部品の役割です。入口の Gateway、鍵を預かる Identity、誰が何を呼べるかを決める Policy の 3 つが AWS の部品です。Entra ID のアプリ登録はお客様の設定です。",
        "Agent Registry は、承認した MCP サーバーを全社で探せるようにする目録です。鍵は預からないので、今回の目的には任意の部品です。")
