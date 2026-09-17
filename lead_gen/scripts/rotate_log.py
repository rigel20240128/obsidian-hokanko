#!/usr/bin/env python3
"""成果.md が無限に伸びるのを防ぐ。

ループは毎回 成果.md を全文読むため、放置すると日々の追記でトークンを食い潰す。
直近 KEEP 回分だけを本体に残し、それより古いセクションは
memories/archive/YYYY-MM.md へ月別に退避する。
"""
import os
import re
import sys

LOG = "lead_gen/memories/成果.md"
ARCHIVE_DIR = "lead_gen/memories/archive"
KEEP = int(os.environ.get("KEEP_ENTRIES", "7"))


def main() -> int:
    if not os.path.exists(LOG):
        print(f"[ERROR] {LOG} が無い", file=sys.stderr)
        return 1

    text = open(LOG, encoding="utf-8").read()
    # 「## 」で始まる行を1エントリの先頭とみなす
    parts = re.split(r"^(?=## )", text, flags=re.M)
    header, entries = parts[0], parts[1:]
    if len(entries) <= KEEP:
        print(f"[OK] {len(entries)}件。KEEP={KEEP} 以内のため退避なし")
        return 0

    keep, archive = entries[:KEEP], entries[KEEP:]
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    moved = 0
    for entry in archive:
        m = re.search(r"(\d{4})-(\d{2})-\d{2}", entry.split("\n", 1)[0])
        month = f"{m.group(1)}-{m.group(2)}" if m else "undated"
        path = os.path.join(ARCHIVE_DIR, f"{month}.md")
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry if entry.endswith("\n") else entry + "\n")
        moved += 1

    open(LOG, "w", encoding="utf-8").write(header + "".join(keep))
    print(f"[OK] {moved}件を {ARCHIVE_DIR}/ へ退避。本体は直近{KEEP}件（{len(text)}→{len(header + ''.join(keep))}バイト）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
