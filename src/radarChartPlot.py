import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "data_clean.csv"
DEFAULT_OUTPUT = ROOT / "figures" / "radar_2may.png"

# Demo: bỏ dấu # ở hai dòng dưới để ghi đè đường dẫn mặc định.
#DEFAULT_CSV = ROOT / "data" / "test" / "data_clean.csv"
#DEFAULT_OUTPUT = ROOT / "data" / "test" / "figures" / "radar_2may.png"


def tim_may(df, ten):
    ten_cot = df["Ten_may"].str.lower().str.strip()
    khop = df[ten_cot == ten.lower().strip()]
    if khop.empty:
        khop = df[ten_cot.str.contains(ten.lower().strip(), regex=False)]
    if khop.empty:
        raise SystemExit(f"Không tìm thấy máy '{ten}' trong dữ liệu.")
    if len(khop) > 1:
        raise SystemExit(f"Tên '{ten}' khớp nhiều máy. Hãy nhập tên đầy đủ: {khop['Ten_may'].tolist()}")
    return khop.iloc[0]


def main():
    ap = argparse.ArgumentParser(description="Radar so sánh hai điện thoại")
    ap.add_argument("--p1", required=True, help="Tên máy thứ nhất")
    ap.add_argument("--p2", required=True, help="Tên máy thứ hai")
    ap.add_argument("--Attribute", required=True,
                    help="Danh sách thuộc tính, cách nhau bằng dấu phẩy (vd: RAM,ROM,Gia_ban)")
    ap.add_argument("--input", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    a = ap.parse_args()

    df = pd.read_csv(a.input, encoding="utf-8-sig", na_values=["N/a"])
    attrs = [x.strip() for x in a.Attribute.split(",") if x.strip()]
    sai = [x for x in attrs if x not in df.columns]
    if sai or len(attrs) < 3:
        raise SystemExit(f"Cần >= 3 thuộc tính hợp lệ. Cột sai: {sai}. Cột số có thể dùng: "
                         f"{list(df.select_dtypes('number').columns)}")
    for c in attrs:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    m1, m2 = tim_may(df, a.p1), tim_may(df, a.p2)
    for m in (m1, m2):
        missing = [c for c in attrs if pd.isna(m[c])]
        if missing:
            raise SystemExit(f"Máy {m['Ten_may']} thiếu thuộc tính: {missing}. Hãy chọn thuộc tính khác.")
    lo, hi = df[attrs].min(), df[attrs].max()
    def chuan_hoa(m):
        return ((m[attrs].astype(float) - lo) / (hi - lo)).fillna(0).tolist()

    ang = np.linspace(0, 2 * np.pi, len(attrs), endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for m, mau in [(m1, "tab:blue"), (m2, "tab:red")]:
        v = chuan_hoa(m); v += v[:1]
        ax.plot(ang, v, color=mau, linewidth=2, label=m["Ten_may"])
        ax.fill(ang, v, color=mau, alpha=0.15)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(attrs)
    ax.set_ylim(0, 1)
    ax.set_title("So sánh hai điện thoại (thang 0-1 theo min-max)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.output, dpi=200, bbox_inches="tight")
    print(f"Đã lưu: {a.output}")


if __name__ == "__main__":
    main()
