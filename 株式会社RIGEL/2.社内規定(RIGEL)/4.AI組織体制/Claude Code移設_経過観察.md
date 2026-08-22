# Claude Code 移設の経過観察

**目的**：2026-08-21 に実施した Claude Code データ移設（ジャンクション方式）が
一週間安定して動作したかを自動点検し、控え（`_控え`・484MB）の処分可否を陛下へ上奏する。

**陛下ご下命（2026-08-21）**：
> 一週間経過して問題がない場合は自動で上奏しなさい。削除指示します。

---

## 監視対象の構成

| 区分 | 場所 |
|---|---|
| 近道（ジャンクション） | `C:\Users\RIGEL\.claude` |
| 実体 | `C:\Users\RIGEL\Documents\Claude code\.claude` |
| 控え（処分候補） | `C:\Users\RIGEL\Documents\Claude code\_控え`（8点・484MB） |
| 帝国ルール正本の指紋 | `24f79b8691d427b2c11c6b07adf8ce6e...`（移設時点・SHA256先頭32桁） |

## 点検の判定基準

**すべて満たせば「異常なし」**とする。

1. `C:\Users\RIGEL\.claude` がジャンクションであり、実体を指している
2. リンク経由で `CLAUDE.md` `settings.json` `statusline.sh` `hooks\unreported-watch.py` が読める
3. 会話履歴（`projects\*.jsonl`）が 64セッション以上ある（減っていない）
4. `C:\Users\RIGEL\.claude.json` が存在し、1000バイト以上ある（初期化されていない）
5. 控え `_控え` が 8点そろっている

---

## 点検記録

（スケジュール実行タスク `claude-migration-observation` が 2026-08-28 に追記する）

