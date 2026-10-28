
from pathlib import Path
import re
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_PATH = BASE_DIR / "phone_image_report.csv"

candidates = [
    DATA_DIR / "data_clean.csv",
    DATA_DIR / "dien_thoai_viet_nam_1021.csv",
    DATA_DIR / "MockData" / "dien_thoai_viet_nam_1021.csv",
]
data_path = next((p for p in candidates if p.exists()), None)

if data_path is None:
    raise FileNotFoundError("Khong tim thay file CSV du lieu.")

df = pd.read_csv(data_path, encoding="utf-8-sig")
if "Ten_may" not in df.columns:
    raise ValueError(f"Khong co cot Ten_may. Cac cot: {list(df.columns)}")

if "Hang" not in df.columns:
    df["Hang"] = ""

phones = df.drop_duplicates(subset=["Ten_may"]).head(5)

session = requests.Session()
session.headers.update({
    "User-Agent": "PhoneHubStudentProject/1.0 (student project)"
})

def search_commons(name, brand):
    queries = [f'"{brand} {name}"', f"{brand} {name} smartphone"]

    for query in queries:
        response = session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,
                "gsrlimit": 10,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 800,
                "format": "json"
            },
            timeout=25
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})

        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            image_url = info.get("thumburl") or info.get("url", "")
            title = page.get("title", "")
            if image_url:
                return {
                    "url": image_url,
                    "title": title,
                    "page": "https://commons.wikimedia.org/wiki/"
                            + title.replace(" ", "_"),
                    "license": info.get("extmetadata", {})
                                  .get("LicenseShortName", {})
                                  .get("value", "")
                }
    return None

results = []

for i, (_, row) in enumerate(phones.iterrows(), start=1):
    name = str(row["Ten_may"]).strip()
    brand = str(row.get("Hang", "")).strip()
    print(f"[{i}/{len(phones)}] Dang tim: {name}")

    result = {
        "Ten_may": name,
        "Hang": brand,
        "Anh_de_xuat": "",
        "Trang_nguon": "",
        "Giay_phep": "",
        "Trang_thai": ""
    }

    try:
        found = search_commons(name, brand)

        if found:
            result["Anh_de_xuat"] = found["url"]
            result["Trang_nguon"] = found["page"]
            result["Giay_phep"] = found["license"]
            result["Trang_thai"] = (
                "Tim thay ung vien - can kiem tra dung mau"
            )
            print("  Tim thay mot ung vien anh")
        else:
            result["Trang_thai"] = "Khong tim thay anh"
            print("  Khong tim thay anh")

    except Exception as e:
        result["Trang_thai"] = f"Loi: {e}"
        print(f"  Loi: {e}")

    results.append(result)
    pd.DataFrame(results).to_csv(
        REPORT_PATH, index=False, encoding="utf-8-sig"
    )

print(f"\nDa ghi bao cao: {REPORT_PATH}")
