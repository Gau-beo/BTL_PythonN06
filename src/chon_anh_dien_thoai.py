
from pathlib import Path
import pandas as pd
import requests
import re
import webbrowser

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "preview_phone_images.csv"
IMAGE_DIR = BASE_DIR / "assets" / "phones"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 PhoneHub/1.0"})

def slugify(text):
    text = str(text).lower().strip()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")

for i, row in df.iterrows():
    name = str(row["Ten_may"]).strip()
    search_url = str(row.get("Link_tim_anh", "")).strip()

    filename = slugify(name)
    existing = [
        p for p in IMAGE_DIR.glob(filename + ".*")
        if p.is_file()
    ]
    if existing:
        print(f"\nDa co anh: {name} -> {existing[0].name}")
        continue

    print(f"\n{i + 1}/{len(df)}: {name}")
    print("Mo trang tim anh...")
    if search_url.startswith("http"):
        webbrowser.open(search_url)

    url = input("Dan URL anh truc tiep (Enter de bo qua): ").strip()
    if not url:
        print("Bo qua.")
        continue

    try:
        r = session.get(url, timeout=25)
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "").lower()
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        ext = next(
            (v for k, v in extensions.items() if k in content_type),
            None
        )

        if not ext:
            print("URL nay khong tra ve file anh truc tiep.")
            continue

        output = IMAGE_DIR / (filename + ext)
        output.write_bytes(r.content)
        print(f"Da tai: {output.name}")

    except Exception as e:
        print(f"Tai that bai: {e}")

print("\nDa xu ly xong danh sach.")
