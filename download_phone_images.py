
from pathlib import Path
from urllib.parse import urlparse
import re
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "preview_phone_images.csv"
IMAGE_DIR = BASE_DIR / "assets" / "phones"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH)

def slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 PhoneHubStudentProject/1.0"
})

for _, row in df.iterrows():
    name = str(row["Ten_may"]).strip()
    url = str(row.get("Anh_truc_tiep", "")).strip()

    if not url or url.lower() == "nan":
        print(f"Bo qua {name}: chua co URL anh")
        continue

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        ext = next(
            (e for mime, e in extensions.items() if mime in content_type),
            None
        )

        if not ext:
            print(f"Bo qua {name}: URL khong tra ve file anh")
            continue

        filename = slugify(name) + ext
        output = IMAGE_DIR / filename
        output.write_bytes(response.content)

        print(f"Da tai: {filename}")

    except Exception as e:
        print(f"Loi voi {name}: {e}")

print("Hoan tat.")
