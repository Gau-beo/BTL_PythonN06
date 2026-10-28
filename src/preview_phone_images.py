
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
import re
import unicodedata

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "assets" / "phones"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

candidates = [
    BASE_DIR / "data" / "data_clean.csv",
    BASE_DIR / "data" / "dien_thoai_viet_nam_1021.csv",
    BASE_DIR / "data" / "MockData" / "dien_thoai_viet_nam_1021.csv",
]

csv_path = next((p for p in candidates if p.exists()), None)

if csv_path is None:
    raise FileNotFoundError(
        "Khong tim thay file CSV trong thu muc data."
    )

df = pd.read_csv(csv_path, encoding="utf-8-sig")

name_col = next(
    (c for c in ["Ten_may", "TenMay", "Ten_dien_thoai"]
     if c in df.columns),
    None
)
brand_col = next(
    (c for c in ["Hang", "Thuong_hieu", "Brand"]
     if c in df.columns),
    None
)

if name_col is None:
    raise ValueError(f"Khong tim thay cot ten may: {list(df.columns)}")

if brand_col is None:
    df["Hang"] = ""
    brand_col = "Hang"


def slugify(value):
    text = unicodedata.normalize(
        "NFKD", str(value)
    ).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()[:120]


phones = df[[name_col, brand_col]].drop_duplicates()
results = []

for _, row in phones.iterrows():
    name = str(row[name_col]).strip()
    brand = str(row[brand_col]).strip()

    if not name or name.lower() == "nan":
        continue

    filename = slugify(name)

    existing = [
        IMAGE_DIR / f"{filename}.{ext}"
        for ext in ["jpg", "jpeg", "png", "webp"]
        if (IMAGE_DIR / f"{filename}.{ext}").is_file()
    ]

    keyword = f"{name} {brand} official phone".strip()
    search_url = (
        "https://www.google.com/search?tbm=isch&q="
        + quote_plus(keyword)
    )

    if existing:
        status = "Da co anh"
        direct_image = ""
        search_url = ""
    else:
        status = "Chua co anh"
        direct_image = ""

    results.append({
        "Ten_may": name,
        "Hang": brand,
        "Tu_khoa_tim_kiem": keyword,
        "Link_tim_anh": search_url,
        "Anh_truc_tiep": direct_image,
        "Trang_thai": status,
        "File_da_co": existing[0].name if existing else ""
    })

output = BASE_DIR / "preview_phone_images.csv"
result_df = pd.DataFrame(results)
result_df.to_csv(output, index=False, encoding="utf-8-sig")

print(f"\nDa tao danh sach: {output}")
print(f"Tong so mau: {len(result_df)}")
print(f"Da co anh: {(result_df['Trang_thai'] == 'Da co anh').sum()}")
print(f"Chua co anh: {(result_df['Trang_thai'] == 'Chua co anh').sum()}")
