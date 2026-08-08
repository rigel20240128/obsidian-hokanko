---
name: RIGEL画像生成_基本プロンプト
type: format-prompt
status: v1.0 (2026-08-08 陛下ご下命により制定)
更新日時: 2026-08-08 12:40
related: [[RIGEL資料作成ルール_統合版]], [[RIGEL資料作成_基本プロンプト]], [[プレゼンフォーマット]]
---

# RIGEL 画像生成 基本プロンプト（v1.0）

> **RIGEL帝国全体のルール（正本）。** 写真・実機画像を「イラスト化」する全ての作業は、
> 使用するツール（Stable Diffusion／Gemini／その他）を問わず本プロンプトに従う。
> 姉妹ファイル [[RIGEL資料作成_基本プロンプト]]（文書）・[[プレゼンフォーマット]]（pptx）と一体でRIGELのブランド基準を成す。
> 作画スタイルの細目（線・配色・視点等）は [[RIGEL資料作成ルール_統合版]] 第2.4章「イラスト・図版の作画統一規定」が優先する。

---

## 0. 位置づけ（最重要）

- 本プロンプトは **「創作」ではなく「トレース（複製）」の規定**である。イラスト化とは、写真を**線画に翻訳する作業**であって、描き直すことではない。
- 本文（第2章）は **一字一句改変しない**。改訂が必要な場合は陛下のご裁可を得た上で、版数を上げて履歴に残す。
- 適用対象：RTSマニュアルの機器イラスト、カタログ・提案書の図版、ホームページ用イラスト等、**実物写真をもとにした全てのイラスト生成**。

## 1. 適用手順

| 手段 | 使い方 |
|---|---|
| **Stable Diffusion + ControlNet**（推奨・ローカル） | `C:\Users\株式会社 RIGEL\Documents\RIGEL画像生成\rigel_illust.py` を使用。本プロンプトは規定として自動的に成果物ノートへ記録される。構造の忠実性はControlNet（構造ロック）と低denoiseで機械的に担保する |
| **Gemini／その他マルチモーダル生成** | 第2章の全文をそのまま貼り付けて指示する |

**技術的注記（諸葛亮）**：Stable DiffusionのテキストエンコーダはCLIP（実効77トークン）であり、第2章の長文の禁止条項は**そのままでは大半が無視される**。SDにおける「ZERO deviation」は文章ではなく、以下のパラメータで実現する。

- ControlNet（Canny／Lineart）**strength = 1.0、適用区間 0〜100%** → 輪郭・幾何・物体数のロック
- img2img **denoise = 0.55前後** → 元画像の配置・比率の保持（上げるほど創作が混入する＝規定違反）
- ネガティブプロンプトで追加要素・装飾・スタイル化を抑制

## 2. 本文（Master Version・改変禁止）

```text
Ultimate High-Precision Image-to-Illustration Prompt (Master Version)
[TASK]
Convert the uploaded image into an illustration.
[PRIMARY OBJECTIVE]
This task is NOT creative.
This is a strict reproduction task.
The goal is to reproduce the original image as an illustration with pixel-level accuracy, without any interpretation, modification, or imagination.
[ABSOLUTE RULES — NON-NEGOTIABLE]

* Do NOT add any elements that are not present in the original image
* Do NOT remove any elements from the original image
* Do NOT change shapes, proportions, or structure
* Do NOT alter layout, composition, or positioning
* Do NOT redesign, enhance, or simplify any part
* Do NOT replace elements with alternatives
* Do NOT infer or complete missing or unclear areas
* Do NOT apply any artistic creativity or stylistic interpretation

[STRUCTURE LOCK]

* Preserve exact geometry
* Preserve exact spatial relationships
* Preserve exact object count
* Preserve exact silhouettes and outlines
* Preserve exact alignment and spacing

[STYLE CONSTRAINTS]

* Clean and simple illustration style
* Uniform line thickness
* Minimal shading only if necessary
* No exaggeration or stylization
* No decorative elements

[BACKGROUND RULE]

* Maintain the original background exactly
* If simplification is required, reduce detail only without changing structure

[PRECISION ENFORCEMENT]

* Pixel-perfect consistency required
* Even the smallest difference is unacceptable
* Differences are considered failure
* Accuracy takes priority over aesthetics

[UNCERTAINTY CONTROL]

* Do not guess missing information
* Do not assume or interpret unclear areas
* Do not proceed if uncertainty exists

[SELF-VALIDATION PROCESS — MANDATORY]
Before final output, perform a strict comparison:

* Compare generated image with original image
* Confirm NO added elements
* Confirm NO missing elements
* Confirm NO shape differences
* Confirm NO layout differences
* Confirm NO proportion differences

If ANY inconsistency is found:
→ Regenerate and correct until fully matched
[FINAL INSTRUCTION]
This is a trace-level faithful illustration task.
The output must be visually equivalent to the original image,
only translated into a clean illustration format.
ZERO deviation is allowed.
```

## 3. 検収規定（SELF-VALIDATION の運用）

第2章の `[SELF-VALIDATION PROCESS — MANDATORY]` は生成AI任せにせず、**人（または比較スクリプト）が納品前に必ず実施**する。

1. 元画像と生成イラストを**同一サイズで重ねて**比較する
2. 以下のいずれかに該当した時点で**不合格・再生成**とする
   - 元画像に無い要素が増えている（ケーブル・ボタン・文字・影の追加）
   - 元画像にある要素が消えている
   - 形状・比率・配置・物体数が変わっている
3. 合格した版のみを [[RIGEL資料作成ルール_統合版]] 第2.4章の配色・線規定に従って仕上げ、資料へ採用する
4. 不合格版も**削除しない**（[[feedback_no_delete_only_organize]]）。`9.控え` 相当の場所へ退避する

## 4. 実在メーカー・型番の扱い

第2章は「元画像の忠実な複製」を求めるが、[[RIGEL資料作成ルール_統合版]] 第2.4章の
**「実在メーカーのロゴ・型番は描かない」** が上位規定として優先する。
他社ロゴ・型番が写り込んだ写真をイラスト化する場合、**当該部分のみ無地に落とす**（形状・配置は保持したまま、文字情報だけを除く）。これは唯一許される「除去」であり、それ以外の除去は規定違反とする。

## 改訂履歴

| 版 | 日付 | 内容 |
|---|---|---|
| v1.0 | 2026-08-08 | 陛下ご下命により制定。Master Version 本文を正本として登録。Stable Diffusion + ControlNet 運用手順・検収規定・他社ロゴの例外規定を付す |
