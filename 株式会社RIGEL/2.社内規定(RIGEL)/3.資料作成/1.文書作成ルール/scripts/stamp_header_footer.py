#!/usr/bin/env python3
"""A4文書PDFの全ページへ、RIGEL規定のヘッダー／フッターを焼き込む。

RIGEL資料作成ルール_統合版 v1.3 準拠
  1.1  ロゴは RIGEL_logo.png のみ。全ページ右上に固定。原本のまま使用（再配色・変形禁止）
       A4文書のヘッダーは 高さ15mm以上／幅28mm以上
  4.2  ヘッダー＝右上にロゴのみ＋直下に区切り線（#026881）
       フッター＝文書名／日付を小さく（#6B6E73）

Chromiumの --print-to-pdf は position:fixed を各ページへ正しく描画しないため、
HTML側では持たせず、生成後に本スクリプトで重ねる。

使い方:
  stamp_header_footer.py <pdf> <文書名> <日付>
"""
import io
import sys

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

MM = 72.0 / 25.4

LOGO = ("/home/user/obsidian-hokanko/株式会社RIGEL/2.社内規定(RIGEL)"
        "/1.プロフィール/ロゴ/RIGEL_logo.png")

MAIN = HexColor("#026881")   # ジュビリーブルー（変更不可）
SUB = HexColor("#6B6E73")    # サブ文字

SIDE_MM = 14.0      # 左右マージン（@page と一致させる）
LOGO_TOP_MM = 8.0   # 用紙上端からロゴ上端まで
LOGO_H_MM = 16.0    # 規定下限15mmに対し余裕を持たせる
RULE_GAP_MM = 2.5   # ロゴ下端から区切り線まで
FOOT_MM = 12.0      # 用紙下端からフッター文字のベースラインまで
JP_FONT = "HeiseiKakuGo-W5"


def build_overlay(page_w, page_h, logo, doc_name, doc_date):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))

    # --- ヘッダー：ロゴ（右上・原本のまま）---
    h = LOGO_H_MM * MM
    w = h * logo.width / logo.height
    x = page_w - SIDE_MM * MM - w
    y = page_h - LOGO_TOP_MM * MM - h
    c.drawImage(ImageReader(logo), x, y, width=w, height=h, mask="auto")

    # --- ヘッダー：直下の区切り線 ---
    c.setStrokeColor(MAIN)
    c.setLineWidth(1.2)
    ry = y - RULE_GAP_MM * MM
    c.line(SIDE_MM * MM, ry, page_w - SIDE_MM * MM, ry)

    # --- フッター：文書名（左）／日付（右）---
    c.setFont(JP_FONT, 7.5)
    c.setFillColor(SUB)
    fy = FOOT_MM * MM
    c.drawString(SIDE_MM * MM, fy, doc_name)
    c.drawRightString(page_w - SIDE_MM * MM, fy, doc_date)

    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def stamp(path, doc_name, doc_date):
    pdfmetrics.registerFont(UnicodeCIDFont(JP_FONT))
    logo = Image.open(LOGO).convert("RGBA")

    reader = PdfReader(path)
    writer = PdfWriter()
    overlays = {}
    for page in reader.pages:
        box = page.mediabox
        size = (round(float(box.width), 1), round(float(box.height), 1))
        if size not in overlays:
            overlays[size] = build_overlay(*size, logo, doc_name, doc_date)
        page.merge_page(overlays[size])
        writer.add_page(page)
    with open(path, "wb") as fh:
        writer.write(fh)
    return len(reader.pages)


if __name__ == "__main__":
    pdf, name, date = sys.argv[1], sys.argv[2], sys.argv[3]
    print(f"stamped {stamp(pdf, name, date)} pages: {pdf}")
