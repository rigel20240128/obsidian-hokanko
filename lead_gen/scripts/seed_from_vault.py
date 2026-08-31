#!/usr/bin/env python3
"""RTS顧客リスト.md から既存企業を抽出し、leads_database.json の初期値を作る。

重複マスターの初期投入用。既に接触対象として台帳化されている企業を
ループが「新規リード」として再取得してしまうのを防ぐ。
2回目以降の実行では既存JSONを読み込み、未登録の企業だけを追記する。
"""
import json
import os
import re
import sys
from datetime import date

VAULT_LIST = "株式会社RIGEL/2.社内規定(RIGEL)/3.資料作成/3.RTSシステム/2.営業資料/RTS顧客リスト.md"
OUT = "lead_gen/memories/leads_database.json"

# 「### 埼玉県川越市（26社）」のような見出しから都道府県を拾う
PREF = "東京都|神奈川県|埼玉県|千葉県|茨城県|栃木県|群馬県"
HEADING = re.compile(r"^###\s+(" + PREF + r")([^（(]*)")
# 表の1列目が企業名、2列目が従業員数の行だけを拾う
ROW = re.compile(r"^\|\s*\**([^|*]+?)\**\s*\|\s*(?:約)?(\d+)\s*[人名]\s*\|")
# 「| 企業名 | 所在地 | 15名 |」形式（04章・Web検索確認済みの表）
ROW3 = re.compile(r"^\|\s*\**([^|*]+?)\**\s*\|\s*\**(" + PREF + r"|さいたま市)([^|*]*?)\**\s*\|\s*(?:約)?(\d+)\s*[人名]\s*\|")


# 04章「裏取りが必要な候補」は従業員数が「未確認」で表から機械抽出できないが、
# 代表者が既に候補として把握している企業であるため、重複マスターには必ず載せる。
# （2026-08-31 ループ試験で、株式会社相模工機所を新規リードとして再取得しかけたため追加）
SUPPLEMENTAL = [
    ("極東精機製作所", "東京都"),
    ("合同会社Eメタル", "東京都"),
    ("株式会社相模工機所", "神奈川県"),
    ("株式会社町田工業", "東京都"),
    ("町田工機株式会社", "東京都"),
]


def normalize(name: str) -> str:
    """全角英数を半角に寄せ、法人格と空白を落とした照合キーを作る。"""
    name = name.translate(str.maketrans(
        "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ０１２３４５６７８９",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    name = re.sub(r"株式会社|有限会社|合同会社|\s|　", "", name)
    return name.upper()


def main() -> int:
    if not os.path.exists(VAULT_LIST):
        print(f"[ERROR] 顧客リストが見つからない: {VAULT_LIST}", file=sys.stderr)
        return 1

    existing = []
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            existing = json.load(f)
    seen = {e.get("name_key") for e in existing}

    pref = ""
    added = 0
    today = date.today().isoformat()
    with open(VAULT_LIST, encoding="utf-8") as f:
        for line in f:
            h = HEADING.match(line)
            if h:
                pref = h.group(1)
                continue
            m3 = ROW3.match(line)
            if m3:
                name, row_pref, emp = m3.group(1).strip(), m3.group(2), int(m3.group(4))
                if row_pref == "さいたま市":
                    row_pref = "埼玉県"
            else:
                m = ROW.match(line)
                if not m or not pref:
                    continue
                name, row_pref, emp = m.group(1).strip(), pref, int(m.group(2))
            if name in ("企業名", "学校名"):
                continue
            key = normalize(name)
            if key in seen:
                continue
            seen.add(key)
            existing.append({
                "name_key": key,
                "company": name,
                "domain": "",
                "pref": row_pref,
                "address": "",
                "url": "",
                "employees": emp,
                "score": "",
                "issue": "",
                "contact": {"type": "", "value": ""},
                "email_draft": "",
                "source_query": "RTS顧客リスト.md（gBizINFO抽出分）からの初期投入",
                "found_at": today,
                "status": "existing",
                "note": "既存台帳。ループの新規判定では重複としてスキップする",
            })
            added += 1

    for name, row_pref in SUPPLEMENTAL:
        key = normalize(name)
        if key in seen:
            continue
        seen.add(key)
        existing.append({
            "name_key": key, "company": name, "domain": "", "pref": row_pref,
            "address": "", "url": "", "employees": None, "score": "", "issue": "",
            "contact": {"type": "", "value": ""}, "email_draft": "",
            "source_query": "RTS顧客リスト.md 第04章「裏取りが必要な候補」からの初期投入",
            "found_at": today, "status": "existing",
            "note": "既存台帳（従業員数未確認）。ループの新規判定では重複としてスキップする",
        })
        added += 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[OK] {added}件を追加、合計{len(existing)}件 -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
