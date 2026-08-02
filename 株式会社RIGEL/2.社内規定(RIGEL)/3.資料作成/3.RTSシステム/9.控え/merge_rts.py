# -*- coding: utf-8 -*-
"""3.RTSシステム 内の md を1本に統合する。本文はメモリ上で連結のみ（内容は読まない）。"""
import os, re, io, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\株式会社 RIGEL\Documents\保管庫\株式会社RIGEL\2.社内規定(RIGEL)\3.資料作成\3.RTSシステム"
OUT = os.path.join(BASE, "RTS事業_統合マスター.md")

# 統合順（章立ての論理順）
ORDER = [
    ("基本概念.md",                                   "RTSとは何か（製品・運用の正本）"),
    ("RTS事業_戦略ロードマップ.md",                    "戦略・方向性"),
    ("RTS_商品・料金プラン体系表.md",                  "商品・料金プラン"),
    ("RTS競合調査報告書.md",                          "競合調査"),
    ("RTS新規顧客攻略_上奏文.md",                      "新規顧客攻略（上奏文）"),
    ("RTS新規顧客攻略_評定議事録.md",                  "評定議事録 1"),
    ("RTS新規顧客攻略_評定議事録２.md",                "評定議事録 2"),
    ("RTS新規顧客攻略_評定議事録３（関東全域深掘り）.md", "評定議事録 3（関東全域深掘り）"),
    ("RTS新規顧客リスト_企業マスターリスト.md",         "新規顧客リスト（企業マスター）"),
]

def strip_frontmatter(text):
    """YAMLフロントマターを除去し、(本文, フロントマター) を返す"""
    if text.startswith('---'):
        m = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n', text, re.S)
        if m:
            return text[m.end():], m.group(1)
    return text, None

def demote(text, levels=1):
    """コードフェンス外の見出しを levels 段下げる"""
    out, in_fence = [], False
    for line in text.split('\n'):
        if re.match(r'^\s*(```|~~~)', line):
            in_fence = not in_fence
            out.append(line); continue
        if not in_fence:
            m = re.match(r'^(#{1,6})(\s)', line)
            if m:
                new = '#' * min(6, len(m.group(1)) + levels)
                line = new + line[len(m.group(1)):]
        out.append(line)
    return '\n'.join(out)

today = datetime.date.today().isoformat()
parts = []

# ── ヘッダ ──────────────────────────────────────
parts.append(f"""---
name: RTS事業_統合マスター
type: master
status: v1.0 ({today})
tags: [RTS, 統合, マスター]
---

# RTS事業 統合マスター

> **本ファイルは `3.RTSシステム` フォルダ内の全Markdownを1本に統合したものである。**
> 統合日：{today}
> **原本は削除していない。**各章の更新は原本側で行い、本ファイルは再生成する運用とする（生成スクリプト：`merge_rts.py`）。
> 提供形態は **リース（月額）専業** に一本化済み（2026-08-01 裁可）。

---

## 目次

""")

# 目次
for i, (fn, label) in enumerate(ORDER, 1):
    if os.path.exists(os.path.join(BASE, fn)):
        parts.append(f"{i}. **{label}** — `{fn}`\n")
parts.append(f"{len(ORDER)+1}. **Google Keep 由来メモ** — 未取込（下記参照）\n")
parts.append("\n---\n\n")

# ── 本文 ────────────────────────────────────────
missing = []
for i, (fn, label) in enumerate(ORDER, 1):
    path = os.path.join(BASE, fn)
    if not os.path.exists(path):
        missing.append(fn); continue
    raw = open(path, encoding='utf-8').read()
    body, fm = strip_frontmatter(raw)
    body = demote(body.strip(), 1)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d')
    parts.append(f"# {i:02d}　{label}\n\n")
    parts.append(f"> 出典：`{fn}`（最終更新 {mtime}）\n\n")
    if fm:
        parts.append("<!-- 原本フロントマター\n" + fm + "\n-->\n\n")
    parts.append(body + "\n\n---\n\n")

# ── Keep 取込枠 ──────────────────────────────────
parts.append(f"""# {len(ORDER)+1:02d}　Google Keep 由来メモ

> **状態：未取込（{today} 時点）**
>
> Google Takeout（2026-08-01 エクスポート／`rigel.20240128@gmail.com`）で **Keep 39ファイルが書き出し済み**だが、
> ダウンロードされた `takeout-20260801T112951Z-001.zip`（47KB）には目次 `archive_browser.html` しか含まれておらず、
> 実データ（`Takeout/Keep/`）が欠落している。**分割zipの2つ目以降を取得する必要がある。**
>
> zip が揃い次第、下表のメモ本文をこの章に取り込む。

## 取込対象メモ一覧（目次より判明・19メモ）

| # | メモ名 | 想定内容 | 優先度 |
|---|---|---|---|
| 1 | RTS事業・教育システム計画 | RTS事業の計画そのもの | **最優先** |
| 2 | LTS事業に関する全ての記録統合ファイル | 統合済み記録 | **最優先** |
| 3 | LTS・リース事業計画メモ（更新版） | リース事業計画の最新版 | **最優先** |
| 4 | LTS・リース事業計画メモ | 同上（旧版） | 高 |
| 5 | LTS事業に関する全ての会話履歴 | 検討経緯の生ログ | 高 |
| 6 | 技術力学習システム概要 | RTSコンセプトの原型 | 高 |
| 7 | 納品・セットアップ関連資料一覧 | 運用フロー | 中 |
| 8 | ロボット組み立て・調整作業編マニュアル構成案 | マニュアル設計 | 中 |
| 9 | マニュアル作成における重要注意点まとめ | マニュアル設計 | 中 |
| 10 | 商品紹介動画の構成案10項目 | PR動画 | 中 |
| 11 | 動画構成案10項目 | PR動画（重複の可能性） | 中 |
| 12 | ローコードについての要約 | 会員サイト実装関連か | 低 |
| 13 | 自己プロフィール（RIGEL設立・FA設備設計） | 代表者経歴 | 低 |
| 14 | これまでの会話の記録 | 生ログ | 低 |
| 15 | これまでの全会話の記録 | 生ログ | 低 |
| 16 | 注意点: ノートの読み込み機能について | Keep運用メモ | 対象外 |
| 17 | 2026-08-01T20_25_30.088+09_00 | 無題メモ | 要確認 |
| 18 | Labels.txt | Keepラベル一覧 | 対象外 |
| 19 | 今週の天気予報／日本ラグビーの現状と課題 | RTS無関係 | 対象外 |

> **注**「LTS」はRTSの旧称または別表記と推測される。取り込み時に呼称を統一すること。

---

## 統合対象外のファイル（同フォルダ内・md以外）

| ファイル | 内容 |
|---|---|
| `RTS競合調査_一覧.csv` | 競合一覧の表データ（報告書の元データ） |
| `RTS設備仕様書_基本フォーマット.xlsx` | 設備仕様書の雛形 |
| `1.営業資料/` | 空フォルダ |
| `SET設備原価表(2012-2026)/` | 前職の設備原価実績（2012〜2026） |

---

*本ファイルは自動生成。原本を編集したうえで再生成すること。*
""")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write(''.join(parts))

size = os.path.getsize(OUT)
lines = open(OUT, encoding='utf-8').read().count('\n') + 1
print(f"OK: {OUT}")
print(f"   {size:,} bytes / {lines:,} lines")
if missing:
    print("   [欠落] " + ", ".join(missing))
