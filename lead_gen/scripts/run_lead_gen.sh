#!/usr/bin/env bash
# RIGEL 新規顧客発掘ループ ヘッドレス実行スクリプト
#
# 使い方（認証はどちらか一方でよい）:
#   CLAUDE_CODE_OAUTH_TOKEN=... bash lead_gen/scripts/run_lead_gen.sh   # サブスク認証（API課金なし）
#   ANTHROPIC_API_KEY=...       bash lead_gen/scripts/run_lead_gen.sh   # API従量課金
#   ローカルPCで `claude` に既にログイン済みなら、どちらも不要
#
# 環境変数:
#   TARGET_LEADS   1日の新規リード目標件数（既定: 10）
#   MAX_ATTEMPTS   検索試行回数の上限（既定: 20）
#   CLAUDE_MODEL   使用モデル（既定: claude-opus-5）
#   MAX_TURNS      モデルのターン数上限（既定: 120／仕様の20試行に対する保険）
#   TIMEOUT_SEC    実時間の強制打ち切り秒数（既定: 2100＝35分）
#   KEEP_ENTRIES   成果.md に残す直近エントリ数（既定: 7）
#   DRY_RUN        1 なら実行せずプロンプトだけ表示する
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# --- 認証の判定 ---------------------------------------------------------
# CLAUDE_CODE_OAUTH_TOKEN が入っていれば、そちらを優先する。
# 両方が環境に居ると claude CLI がどちらを使ったか分からなくなるため、明示的に片方を落とす。
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
  unset ANTHROPIC_API_KEY
  AUTH_MODE="サブスク認証（CLAUDE_CODE_OAUTH_TOKEN／API従量課金なし）"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  AUTH_MODE="APIキー認証（ANTHROPIC_API_KEY／従量課金）"
elif [ -d "$HOME/.claude" ] || [ -f "$HOME/.claude.json" ]; then
  AUTH_MODE="ローカルのログイン情報"
else
  echo "[ERROR] 認証情報が無い。次のいずれかを設定すること：" >&2
  echo "  - CLAUDE_CODE_OAUTH_TOKEN（claude setup-token で発行。サブスクを使う。API課金なし）" >&2
  echo "  - ANTHROPIC_API_KEY（console.anthropic.com で発行。従量課金）" >&2
  exit 1
fi

TARGET_LEADS="${TARGET_LEADS:-10}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-20}"
CLAUDE_MODEL="${CLAUDE_MODEL:-claude-opus-5}"
MAX_TURNS="${MAX_TURNS:-120}"
TIMEOUT_SEC="${TIMEOUT_SEC:-2100}"
TODAY="$(TZ=Asia/Tokyo date +%F)"

for f in lead_gen/CLAUDE.md \
         lead_gen/blueprints/rigel_business_concept.md \
         lead_gen/blueprints/target_industries.md \
         lead_gen/memories/leads_database.json \
         lead_gen/memories/成果.md \
         lead_gen/memories/blacklist.md; do
  [ -f "$f" ] || { echo "[ERROR] 必須ファイルが無い: $f" >&2; exit 1; }
done

if ! python3 -c 'import json,sys; json.load(open("lead_gen/memories/leads_database.json",encoding="utf-8"))'; then
  echo "[ERROR] leads_database.json が壊れている。復旧してから再実行すること" >&2
  exit 1
fi

# 成果.md はループが毎回全文読むため、伸び続けるとトークンを食い潰す。
# 実行前に直近KEEP_ENTRIES件へ切り詰め、古い分は memories/archive/ へ退避する。
KEEP_ENTRIES="${KEEP_ENTRIES:-7}" python3 lead_gen/scripts/rotate_log.py

BEFORE="$(python3 -c 'import json; print(len(json.load(open("lead_gen/memories/leads_database.json",encoding="utf-8"))))')"
echo "[INFO] 開始 ${TODAY} / 既存リード ${BEFORE}件 / 目標 ${TARGET_LEADS}件 / 試行上限 ${MAX_ATTEMPTS}回"
echo "[INFO] 認証: ${AUTH_MODE}"

PROMPT=$(cat <<PROMPT_EOF
本日（${TODAY}）の RIGEL 新規顧客発掘ループを1回実行せよ。

まず lead_gen/CLAUDE.md を読み、その仕様に厳密に従うこと。仕様と本指示が食い違う場合は仕様を優先する。

実行手順:
1. lead_gen/blueprints/ の2ファイルと lead_gen/memories/ の3ファイルをすべて読む。
2. memories/成果.md の「次回方針」を読み、そこから探索を始める。
3. researcher サブエージェントで候補を探索し、lead-filter で重複除外とスコアリング、
   スコアA/Bの企業にのみ copywriter でメール下書きを作る。
4. 新規適格リード（スコアA/B）が ${TARGET_LEADS} 件に達するか、検索試行が ${MAX_ATTEMPTS} 回に達したら停止する。
   試行するたびに memories/成果.md の試行ログへ1行追記し、それを試行回数の正本とすること。
5. 新規リードを lead_gen/memories/leads_database.json へ追記する（既存要素を消さない・並び替えない）。
6. lead_gen/memories/成果.md の先頭へ当日分のセクションを追記する。
   ヒットしたクエリ・不調だったクエリ・次回方針・停止ステータスを必ず書く。
   獲得0件または致命的エラーの場合は [WARNING] と原因を明記する。
7. **学習の起票**：今回の結果から、次のいずれかに該当する構造的な発見があった場合は、
   memories/成果.md の末尾に「### researcher.md への追記案（要裁可）」の節を設け、
   **変更案をそのまま貼り付けられる形で書き出す**こと。
   - 収穫の大きかった入口ドメイン（自治体・産業振興公社の企業DB等）を見つけた
   - 空振りを繰り返すドメインを特定した（blocked_domains 追加候補）
   - 構造的に成果の出ないクエリ型を特定した（「やらないクエリ」追加候補）
   各案には**根拠（どのクエリで何件取れた／取れなかったか）を必ず添える**こと。
   該当する発見が無ければ本節は作らない。**毎回書く必要はない。**

   🔴 **.claude/agents/ 配下のファイルを書き換えてはならない。**
   探索戦略の変更は代表者が採否を判断する。ループは提案までとする。

厳守事項:
- メールの送信、問い合わせフォームへの投稿は絶対に行わない。下書きの生成までとする。
- 公開情報で裏取りできない情報を推測で埋めない。不明な欄は空文字のままにする。
- 1回の実行で ${TARGET_LEADS} 件を超えて新規登録しない。
- 保管庫側のファイル（株式会社RIGEL/ 配下、katosumi/ 配下）は読むだけで、書き換えない。
PROMPT_EOF
)

if [ "${DRY_RUN:-0}" = "1" ]; then
  echo "--- DRY_RUN: 以下のプロンプトで起動する ---"
  echo "$PROMPT"
  exit 0
fi

set +e
timeout --signal=INT "$TIMEOUT_SEC" \
  claude -p "$PROMPT" \
    --model "$CLAUDE_MODEL" \
    --max-turns "$MAX_TURNS" \
    --permission-mode acceptEdits \
    --allowed-tools "WebSearch,WebFetch,Read,Write,Edit,Glob,Grep,Task,Bash(python3:*)" \
    --output-format text
RC=$?
set -e
if [ "$RC" -eq 124 ]; then
  echo "[WARNING] ${TIMEOUT_SEC}秒のハード上限で打ち切った。成果.md の試行ログを確認すること" >&2
fi

AFTER="$(python3 -c 'import json; print(len(json.load(open("lead_gen/memories/leads_database.json",encoding="utf-8"))))' 2>/dev/null || echo "$BEFORE")"
ADDED=$((AFTER - BEFORE))
echo "[INFO] 終了 rc=${RC} / 新規登録 ${ADDED}件 / 累計 ${AFTER}件"

if [ "$ADDED" -eq 0 ]; then
  echo "[WARNING] 新規リードが0件だった。memories/成果.md の原因記載を確認すること" >&2
fi
exit "$RC"
