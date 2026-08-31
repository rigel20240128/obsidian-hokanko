# 接触NG企業・対象外ドメイン一覧

> ループは探索の初手でこのファイルを読み、該当する企業・ドメインを**カウント対象外でスキップ**する。
> 追記したら理由を必ず書くこと。理由のない行は次回の判断に使えない。

## 1. 個別のNG企業

| 企業名 / ドメイン | 区分 | 理由 |
|---|---|---|
| 株式会社サンエイテック | 取引先 | 代表の前職。設計外注の継続取引先であり、営業対象ではない |
| 株式会社タイショー | 取引先 | 設計外注の継続取引先 |
| 株式会社ホシモト | 除外 | 本社大阪・従業員120名。埼玉は営業所のみで製造拠点ではない |
| 株式会社興電舎 | 提携候補 | 埼玉県北本市・従業員109名。FA設備の自社製造メーカー。顧客ではなく販売代理・提携先として別ルートで扱う |
| 蛇の目ミシン工業 / JANOME | 仕入先 | RTSの中核機材の供給元。営業対象ではない |

## 2. ドメイン単位の除外（探索ノイズ）

求人・企業DBの集約サイトは企業そのものではないため、リードとして登録しない。

```
indeed.com / jp.indeed.com
doda.jp
stanby.com
hellowork.careers / hello-work.info
mynavi.jp / rikunabi.com / en-japan.com / baitoru.com
townwork.net / job-medley.com
wantedly.com / green-japan.com
gbiz.go.jp
imprestore.jp / nikkan.co.jp / monoist.itmedia.co.jp
facebook.com / x.com / twitter.com / note.com
```

## 3. 業種カテゴリの除外

`blueprints/target_industries.md` 第5節を正とする。
判断に迷った企業は登録せず、`memories/成果.md` の「判断保留」に企業名と理由を書き残す。
