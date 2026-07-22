"""
三国志キャラクタ画像の一括抽出スクリプト

概要:
  親フォルダ(このスクリプトの1つ上の階層)にある全てのJPEG/PNG画像から、
  Gemini画像モデル(Nano Banana / gemini-2.5-flash-image)を使って
  メインのキャラクターイラスト(全身+装備品)だけを抽出し、
  真っ黒(0,0,0)背景・中央配置・正方形(1:1)に合成して
  output_images フォルダにキャラクター名で保存する。

事前準備:
  pip install google-genai python-dotenv pillow
  このスクリプトと同じフォルダに .env ファイルを作成し、
  GEMINI_API_KEY=xxxxxxxx を1行書いておく。

使い方:
  python extract_characters.py --test     … 劉備の1枚だけ処理して確認
  python extract_characters.py            … フォルダ内の全画像を処理
"""

import argparse
import os
import re
import sys
import time
import io

from dotenv import load_dotenv
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(SOURCE_DIR, "output_images")
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

TEXT_MODEL = "gemini-flash-latest"
IMAGE_MODEL = "nano-banana-pro-preview"

EXTRACT_PROMPT = (
    "この画像には、メインのキャラクターイラスト(全身・鎧や武器などの装備を含む)と、"
    "縦書きの日本語テキスト、そして背景に大きく引き伸ばされた半透明の顔のクローズアップが写っています。"
    "テキストと背景の顔のクローズアップは完全に無視し、メインのキャラクターイラスト"
    "(全身と、持っている武器などの装備品の先端まで全て)だけを高精度に抽出してください。"
    "抽出したキャラクターを、完全に均一な真っ黒(RGB 0,0,0)の背景の上に配置してください。"
    "頭の先から足先、武器の先端まで、キャラクターに関わる全ての要素が画像の枠内に完全に収まるように、"
    "必要であれば縮小して配置してください。キャラクターは画像の中央に配置し、"
    "周囲に窮屈にならない程度の適度な余白を確保してください。"
    "出力画像は正方形(1:1)にしてください。文字やロゴ、背景の顔は一切含めないでください。"
)

NAME_PROMPT = (
    "この画像には、キャラクターの名前が大きな縦書きの日本語(漢字)で表示されています。"
    "その名前だけを、説明や記号を付けずに出力してください。"
    "例: 劉備 のように、漢字の名前のみを1行で答えてください。"
)


def get_client():
    load_dotenv(ENV_PATH)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"エラー: {ENV_PATH} に GEMINI_API_KEY が見つかりません。")
        print("同じフォルダに .env というファイル名で作成し、")
        print("GEMINI_API_KEY=あなたのキー という行を書いてください。")
        sys.exit(1)
    from google import genai
    return genai.Client(api_key=api_key)


def list_source_images():
    if not os.path.isdir(SOURCE_DIR):
        return []
    files = []
    for name in sorted(os.listdir(SOURCE_DIR)):
        ext = os.path.splitext(name)[1].lower()
        if ext in (".jpg", ".jpeg", ".png"):
            files.append(os.path.join(SOURCE_DIR, name))
    return files


def sanitize_filename(name):
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|\s]+", "", name)
    name = re.sub(r"[^\w぀-ヿ㐀-鿿]", "", name)
    return name or "unknown"


def call_with_retry(fn, retries=2, delay=3):
    last_err = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(delay)
    raise last_err


def detect_name(client, image_path):
    img = Image.open(image_path)

    def _call():
        resp = client.models.generate_content(
            model=TEXT_MODEL,
            contents=[NAME_PROMPT, img],
        )
        return resp.text or ""

    raw = call_with_retry(_call)
    return sanitize_filename(raw)


def extract_character(client, image_path):
    img = Image.open(image_path)

    def _call():
        return client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[EXTRACT_PROMPT, img],
        )

    resp = call_with_retry(_call)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) is not None:
            data = part.inline_data.data
            return Image.open(io.BytesIO(data)).convert("RGB")
    raise RuntimeError("画像モデルの応答に画像データが含まれていませんでした。")


def finalize_square(img, size=1024):
    """出力を厳密な正方形・指定解像度の黒背景キャンバスに収める安全策。"""
    w, h = img.size
    scale = min(size / w, size / h, 1.0) if max(w, h) > size else size / max(w, h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    resized = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), (0, 0, 0))
    canvas.paste(resized, ((size - nw) // 2, (size - nh) // 2))
    return canvas


def process_one(client, image_path, used_names):
    name = detect_name(client, image_path)
    if name in used_names:
        base = name
        i = 2
        while name in used_names:
            name = f"{base}_{i}"
            i += 1
    used_names.add(name)

    extracted = extract_character(client, image_path)
    final_img = finalize_square(extracted)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    final_img.save(out_path, "PNG")
    return name, out_path


def run(test_mode):
    client = get_client()
    files = list_source_images()
    if not files:
        print(f"{SOURCE_DIR} に処理対象の画像が見つかりませんでした。")
        return

    if test_mode:
        target = os.path.join(SOURCE_DIR, "chara_popup_09.jpg")
        if not os.path.exists(target):
            target = files[0]
        files = [target]

    total = len(files)
    used_names = set()
    ok, ng = 0, 0
    for i, path in enumerate(files, start=1):
        fname = os.path.basename(path)
        print(f"[{i}/{total}] 処理中... ({fname})")
        try:
            name, out_path = process_one(client, path, used_names)
            print(f"  -> 完了: {name} ({out_path})")
            ok += 1
        except Exception as e:
            print(f"  -> エラー: {fname} の処理に失敗しました: {e}")
            ng += 1
            continue

    print(f"\n完了: 成功 {ok} 件 / 失敗 {ng} 件 (合計 {total} 件)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="劉備の1枚だけ処理する")
    args = parser.parse_args()
    run(test_mode=args.test)
