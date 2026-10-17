# dataset/ について

`research/r01-meta-llama.md` から `r18-rl-fewer-gpus.md` までの全調査ファイル (r10 は `r10-mfu-goodput.md` と `r10-rl-framework-time-breakdown.md` の 2 本を含む、計 19 ファイル) から、グラフ用に使える数値だけを抜き出して整理したものです。推測で値を埋めた箇所は無く、すべて元ファイルに書かれている一次資料の引用・URL に基づきます。値が無い列は空欄のままにしています。

- `models.csv` — モデルごとの学習計算量 (1 モデル 1 行、297 行)
- `rollout_share.csv` — RL の反復時間のうち rollout が占める割合 (23 行)

作成方法: 19 本の調査ファイルを 12 グループに分けてそれぞれ抽出し (大きいファイルで出力が 16,000 トークン上限を超えて失敗したため、ファイル単位にさらに分割し直した経緯があります)、最後にモデル名を正規化して 1 モデル 1 行にまとめました。正規化やマージの過程で見つかった食い違いは、該当行の `notes` 列に `[食い違い: ...]` という形でそのまま残し、下の「3. 値が食い違った箇所」にも一覧化しています。

## 1. models.csv の列定義

| 列 | 内容 |
| --- | --- |
| model | モデル名 (バージョン・サイズまで含めて一意になるように命名。通し番号ではなく元ファイルの表記をできるだけ尊重) |
| org | 開発組織 |
| region | `china` / `us_eu` / `japan_other` のいずれか。本拠地が一次資料から確定できないものは空欄 (2 行: Nex AGI, IFM) |
| release | リリース月 (YYYY-MM)。日までしか分からない場合は月に丸め、年しか分からない場合は年のみ、不明なら空欄 |
| arch | `dense` / `moe` / `hybrid` のいずれか。Mamba・SSM・Delta Attention・Lightning Attention など非標準の attention を使うものは `hybrid` を優先し (MoE を併用していても)、それ以外で total_b と active_b が異なるものは `moe`、同じものは `dense` とした。判定根拠が無いものは空欄 (23 行) |
| total_b | 総パラメータ数 (10 億単位) |
| active_b | 活性パラメータ数 (10 億単位)。dense モデルは total_b と同じ値 |
| pretrain_tokens_t | 事前学習トークン数 (兆単位) |
| pretrain_gpu | 事前学習で使われた GPU/アクセラレータの種別 (報告された表記のまま。H800, GB200, TPU v6e, AI ASIC など) |
| pretrain_gpu_count | 事前学習の GPU 枚数 |
| pretrain_gpu_hours_m | 事前学習の GPU 時間 (百万 GPU 時間単位) |
| pretrain_gpu_hours_kind | `reported` (本文に明記) / `computed` (他の数値から算出、notes に計算式) / `none` (開示なし) |
| mfu_pct | Model FLOPs Utilization (%) |
| mfu_kind | `reported` / `computed` / `none` |
| post_sft_samples | post-training の SFT サンプル数 (桁数の大きい概数や内訳付きの記述も含む) |
| rl_gpu_hours_k | RL (post-training) の GPU 時間 (千 GPU 時間単位) |
| rl_gpu_hours_kind | `reported` / `allocation` (割り当てられた GPU 時間で実消費ではない) / `computed` / `none` |
| rl_gpu | RL で使われた GPU 種別 |
| rl_gpu_count | RL の GPU 枚数 |
| source_urls | 根拠 URL (セミコロン区切り、複数可。URL が存在しない場合は arXiv 番号などの識別子) |
| notes | 出典の根拠・計算式・曖昧さ・値の食い違いを日本語で記載 |

### 1.1 数値列に「範囲」や「複合値」がそのまま残っている箇所 (4 件)

一次資料が単一の数値ではなく範囲や複数条件の値を報告している場合、単一値に丸めず報告された形のまま残しました。グラフ化する際はパース (`-` で分割、括弧内を除去など) が必要です。

| モデル | 列 | 値 | 補足 |
| --- | --- | --- | --- |
| INTELLECT-1 | mfu_pct | `36.2-41.4` | 報告された範囲そのまま |
| Marin 535B-A23B | mfu_pct | `21-24` | 報告された範囲そのまま |
| Kimi Linear | pretrain_tokens_t | `1.4(比較実験)/5.7(最終版)` | 比較実験条件と最終版で異なるトークン数が報告されている |
| DeepSeek-V4.1-Flash | active_b | `8(prefill)/16(decode)` | prefill と decode で活性パラメータが異なる(投機的デコード等の実装による)と報告されている |

### 1.2 数値でなく概数・比率だった箇所は空欄にし notes へ退避した例

`AI2 Olmo 3 Think 32B` と `Think 7B` の `rl_gpu_count` には元々「8:20 nodes (ratio)」のような rollout:trainer のノード比が入っていましたが、これは GPU 枚数そのものではないため列を空欄にし、`notes` に比率として記載し直しました。`Kimi K3` の `rl_gpu_count` も「数百」という概数だったため同様に処理しています。

### 1.3 「未公開」等のプレースホルダ文字列の扱い

抽出作業の一部で、値が無い列に `none` という kind とは別に「未公開」という日本語の文字列そのものを値として書き込んでしまったケースが多数ありました (主に r13 由来、DeepSeek-V4 系・Qwen3.6/3.8 系で計 100 件以上)。これは「データが無い」ことを示すだけの文字列であり、CSV として読み込むとグラフ描画の邪魔になるため、すべて空文字列に正規化しました (該当する kind 列は元から `none` になっていたため実質的な情報の変化はありません)。

## 2. rollout_share.csv の列定義

| 列 | 内容 |
| --- | --- |
| system | RL システム/フレームワーク/論文名 |
| model | 評価に使われたモデル名 |
| gpu | GPU 種別 |
| gpu_count | GPU 枚数 |
| rollout_share_min_pct / max_pct | 反復時間のうち rollout が占める割合の下限/上限 (%)。単一値のみ報告されている場合は min=max |
| kind | `reported` (本文に明記) / `computed` (他の秒数等から比率を計算、notes に計算式) |
| source_url | 根拠 URL または arXiv 番号 |
| notes | 測定条件の補足 |

### 2.1 指定されたシステムのうち、直接の数値が見つからなかったもの

調査対象として名前が挙がっていた Seer・ReaL・DistFlow・Laminar・RollPacker・APRIL・HybridFlow (baseline)・OpenRLHF は全て一次資料中に rollout 比率の数値を確認できましたが、以下は見つかりませんでした。

- **MiMo-V2.6** (arXiv:2610.11959): コスト・staleness (=4)・FP8 投機的デコードの高速化率 (10.3%) は報告されているが、「反復時間に占める rollout の割合」という直接の数値は r16 の調査範囲では確認できなかった。
- **HybridFlow 自身の純粋な rollout 単独比率**: 本文にあるのは「actor training + generation の合計で 58.9%」という複合値のみで、生成 (rollout) だけを切り出した比率は報告されていない。そのため本表には比較対象として引用されている NeMo-Aligner baseline (81.2%) のみを採用した。

## 3. 除外したモデルとその理由

「調査に出た全モデル」という指示に対して、行を作らなかった (= models.csv に含めなかった) ものはごく少数です。大半は「値が確認できない」場合でも model/org/region だけ埋めて 1 行作っています (1.2 の方針どおり)。実際に行を作らなかったのは次のケースです。

- **Meta の新版、Apple の新版、Hugging Face SmolLM の新版**: r15 の調査で「2025-10〜2026-10 の期間に該当する新しいモデルが一次資料上で確認できなかった」という結論になったため、行を作成していません (存在しないと断定したわけではなく、調査時点で見つからなかったという意味です)。Meta の "Muse" ブランド (Muse Spark Open / Muse Glimmer) は別系統として r12 で見つかっており、models.csv には含めています。
- **AReaL**: RL の学習基盤 (フレームワーク) であり、単体の事前学習済みモデルではないため、models.csv には行を作っていません。AReaL 論文内で言及される個別モデルの数値は、該当するモデル本体の行の notes に反映しています。
- **01.AI**: 2025-10〜2026-10 の期間に新しい基盤モデルの一次資料が見つからず、企業向け AI 製品へのピボットが調査結果として確認されたため、参考情報 (直前の Yi-Lightning) のみを 1 行にまとめています (完全な除外ではなく代表行での記録)。

一方で、次のモデルは「一次資料調査を実施したが学習計算量に関する数値が一切確認できなかった」もので、除外はせず model/org/region など分かる範囲だけを埋めた行として残しています (計 20 行): Qwen3.5-27B、QwQ-32B-Preview、StepFun Step-2、Mistral Large (初代)、Magistral Medium、xAI Grok-2、OpenAI o1、ERNIE-5.1、Tencent Hunyuan-T1、Kwai KAT-Coder-V2/V2.5、iFlytek Spark、OpenAI gpt-oss-safeguard-20b (20b 版自体の total/active は本文に記載が無く、120b 版と同一重みの再利用と明記されている)、LLM-jp-4.1 (単一のパラメータ規模を持たない post-training 改訂版のリリース名)、NTT tsuzumi、富士通 Takane、GLM-5.1/5.2 (GLM-5 系列と推定されるが本文未読)、Thinking Machines Inkling。

また、**closed-weight (非公開重み) のモデルも除外せず含めています**。Qwen3-Max・Qwen3.8-Max など API 専用モデルは、オープンウェイトモデルとの比較の参考値として notes に「closed-weight」「closed発表名」と明記したうえで行を残しました。グラフ化の際にオープンウェイトだけに絞る場合は、notes 列に "closed" を含む行を除外してください (なお Cohere Command A+ は旧 Command A の非商用ライセンスから Apache 2.0 へ転換したと報告されており、closed ではなくオープンウェイト側です)。

## 4. 値が食い違った箇所 (どちらを採ったか)

同じモデルが複数の調査ファイルに登場し、報告されている数値が食い違っていたケースを一覧にします。方針は「両方の値を保持し、より詳細・より新しい一次資料側の値を主たる値として残し、もう一方は notes の `[食い違い: ...]` に記録する」です (どちらかが明確に誤りだと判断できる場合を除き、切り捨てていません)。個別の判断根拠は各行の notes に残っています。

| モデル | 食い違った列 | 採用した値 | もう一方の値 | 出典 | 補足 |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4.1-Flash | active_b | `8(prefill)/16(decode)` | `16` | r13 vs r12 | r13 はモデルカード本文の prefill/decode 別の値、r12 は Artificial Analysis の単一値。より詳細な r13 側を採用 |
| DeepSeek-V4.1-Flash | arch | `moe` (正規化後) | `moe` | r13 vs r12 | 元の r13 の記述はアーキテクチャの詳細記述だったため `moe` に正規化、r12 はもともと `moe` で一致 |
| Qwen3.6-35B-A3B | arch | `hybrid` (正規化後) | `moe` | r13 vs r12 | r13 は Gated DeltaNet 等の非標準 attention の記述があったため `hybrid` に正規化。r12 は `moe` のみ |
| Kimi K3 | arch | `hybrid` (正規化後) | `moe` | r13 vs r12 | KDA (Kimi Delta Attention) の記述により `hybrid` を採用 |
| Kimi K3 | rl_gpu_hours_kind | `allocation` | `none` | r13 vs r12 | r13 が「colocated RL で 1M ctx 実験を数百 GPU に収める」という割り当ての記述を確認できたため `allocation` を採用 |
| MiniMax-M2 | model / total_b / active_b | `MiniMax-M2`、`230`、`10` | `MiniMax-M2系(M2/M2.1/M2.5/M2.7)`、`229.9`、`9.8` | r04(rest) vs r14 | r04(rest) が GitHub/HF README の報告値 (230B/10B) を先に確定させていたため主値として残し、r14 が持つ config.json 実測の精緻値 (229.9B/9.8B) と「M2.1/M2.5/M2.7 は同アーキで post-training のみ更新」という注記は notes に統合した。精緻な数値を使う場合は notes 側の 229.9B/9.8B を参照 |
| Gemma 4 (26B-A4B) | total_b | `25.2` | `26` | r05 vs r15 | r05 はモデルカード表の精緻値、r15 は arXiv 本文の近似値。精緻な方を主値とした |
| Gemma 4 (31B) | total_b / active_b | `30.7` | `31` | r05 vs r15 | 同上の理由で精緻値を採用 |
| Nemotron 3 Ultra | arch | `hybrid` (正規化後) | `moe` | r06 vs r12 | r06 は「LatentMoE (Mamba-2 + MoE + Attention hybrid)」という記述から `hybrid` を採用、r12 は `moe` のみ |
| Nemotron 3.5 Super VL | arch | `hybrid` (正規化後) | `moe` | r06 vs r12 | 同上 |
| Liquid AI LFM2.5-24B-A2B | active_b / pretrain_tokens_t | `2.45` / `33` | `2` / `36` | r15 vs r12 | r15 はモデルカードの正確な活性パラメータ値、r12 は丸めた値と学習予算の合計値 (33T の pre-training 分のみ vs 36T の総学習予算)。どちらも一次資料に基づく正しい値だが指している範囲が異なるため、notes 内訳を必ず参照すること |
| Reflection AI Beam-1.0-501B-A23B | pretrain_gpu_hours_kind / rl_gpu_hours_kind | `computed` | `none` | r15 vs r12 | r15 が GPU 台数と期間から GPU 時間を算出していたため `computed` を採用。計算式は notes 参照 |
| INTELLECT-3 | rl_gpu_hours_kind / rl_gpu_count | `computed` / `480` | (元は`none`+512枚の情報が未統合) | r06 vs r08 | r06 (RL専用配分480枚) と r08 (737.28 千GPU時間の計算値、512枚は複数ablationを含む全体確保枚数) を統合する際、値だけ埋めて kind を `none` のままにしてしまう不整合がマージ処理にあったため手動で `computed` に修正した。480 枚 (RL専用) と 512 枚 (全体確保) は意味が異なる数字であり、どちらも notes に残している |
| Cohere Command A | — | (Command A+ と統合しない) | — | r05 vs r15 | 文字列正規化で `+` を誤って除去すると "Command A" と "Command A+" が同一キーに潰れてしまうバグを検出・修正した。最終的には **別モデルとして 2 行に分離** している (111B dense の Command A と 218B/25B MoE の Command A+) |

その他、組織名の表記揺れ (`DeepSeek-AI` vs `DeepSeek`、`Zhipu(Z.ai)` vs `Z.ai` vs `Zhipu AI` など) や release の精度の違い (`2026` vs `2026-09` など) も同様に notes に記録していますが、実質的な数値への影響が無いため上表には含めていません。該当行の notes を検索すると全件確認できます。

## 5. 注意点 (グラフ作成者向け)

- source_urls はセミコロン区切りで複数入っていることがあります。
- 1 つの研究ファイルから複数の下位エージェントが並行して抽出したため、同じモデルについて記述の詳しさが異なる場合があります (notes の最初の文がどのファイル由来かは `[r*出典]` という接頭辞、または conflicts の記録から判別できます)。
- 本データセットは「報告されている値をそのまま集める」ことを目的にしており、モデル間で前提条件 (シーケンス長、精度 bf16/fp8、GPU 世代) が揃っていません。グラフで比較する際は notes を必ず確認してください。


## 抜き取り検査 (2026-10-17)

グラフに描いた 59 モデル、297 項目を一次資料で確かめ、誤り 4 件を直した。StarCoder2-15B のトークン数 (4.3T → 4.1T)、DBRX の GPU 時間 (事前学習以外を含む確保の換算なので削除)、LLM-jp-3 MoE 8x1.8B のトークン数 (別モデルの値なので削除)、Olmo 3 / 3.1 Think のトークン数 (9.31T → 5.93T)。GPT-3 と Gemma 3n E2B の出典 URL も直した。Llama 3.1 8B / 70B と Llama 3.3 70B の 15T は公式の「15T+」の下限、Nemotron-4 340B と Reflection AI Beam の GPU 時間は報告の枚数と期間からの計算値。検査の結果は verify/part1〜3_result.csv。
