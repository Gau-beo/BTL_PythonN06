import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PHONES = ROOT / "data" / "phones.csv"

# Demo: bỏ dấu # ở dòng dưới để gộp vào file dữ liệu thô của luồng demo.
# PHONES = ROOT / "data" / "test" / "phones_crawled.csv"


def main():
    if len(sys.argv) < 2:
        sys.exit("Cách dùng: python src/merge_phones.py <file_cào_thêm.csv> [...]")
    base = pd.read_csv(PHONES, encoding="utf-8-sig", dtype=str)
    n0 = len(base)
    parts = [base] + [pd.read_csv(f, encoding="utf-8-sig", dtype=str) for f in sys.argv[1:]]
    merged = pd.concat(parts, ignore_index=True, sort=False)
    merged = merged.drop_duplicates(subset=["URL"], keep="first")
    cols = ["URL", "Ten_may", "Gia_ban"] + [c for c in merged.columns if c not in ("URL", "Ten_may", "Gia_ban")]
    merged[cols].to_csv(PHONES, index=False, encoding="utf-8-sig")
    print(f"{PHONES.name}: {n0} -> {len(merged)} dòng. Hãy chạy lại: python src/process.py")


if __name__ == "__main__":
    main()
