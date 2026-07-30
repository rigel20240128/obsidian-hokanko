#!/usr/bin/env python3
"""HTMLから生成したA4縦PDFの全ページ右上に、RIGELロゴを重ねる。

Chromiumの--print-to-pdfは position:fixed を描画しないため、
プレゼンフォーマット規定「ロゴは全ページ右上に固定」を満たすには
生成後にオーバーレイで焼き込む必要がある。
"""
import io
import sys

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

MM = 72.0 / 25.4
LOGO_SRC = "/home/user/obsidian-hokanko/RIGEL/会社概要・資料/logo/RIGEL(Jubilee Blue).png"

RIGHT_MARGIN_MM = 18.0   # 規定の右マージンに合わせる
TOP_MARGIN_MM = 9.0      # 用紙上端からロゴ上端まで
LOGO_H_MM = 12.0         # ロゴ高さ（クリアスペースを確保できる控えめな寸法）


def load_logo():
    """透明背景を保ったまま、ほぼ不可視のアーティファクトを除去して返す。"""
    im = Image.open(LOGO_SRC).convert("RGBA")
    alpha = im.getchannel("A")
    visible = alpha.point(lambda p: 255 if p > 25 else 0)
    return im.crop(visible.getbbox())


def build_overlay(logo, page_w, page_h):
    """1ページ分のロゴのみのPDFを作る。"""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    h = LOGO_H_MM * MM
    w = h * logo.width / logo.height
    x = page_w - RIGHT_MARGIN_MM * MM - w
    y = page_h - TOP_MARGIN_MM * MM - h
    c.drawImage(ImageReader(logo), x, y, width=w, height=h, mask="auto")
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def stamp(path):
    logo = load_logo()
    reader = PdfReader(path)
    writer = PdfWriter()
    overlays = {}
    for page in reader.pages:
        box = page.mediabox
        size = (round(float(box.width), 1), round(float(box.height), 1))
        if size not in overlays:
            overlays[size] = build_overlay(logo, *size)
        page.merge_page(overlays[size])
        writer.add_page(page)
    with open(path, "wb") as fh:
        writer.write(fh)
    return len(reader.pages)


if __name__ == "__main__":
    for target in sys.argv[1:]:
        n = stamp(target)
        print(f"stamped {n} pages: {target}")
