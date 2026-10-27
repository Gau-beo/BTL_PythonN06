"""
Vẽ HISTOGRAM cho từng thuộc tính số của bộ dữ liệu điện thoại:
  - 1 ảnh "toàn bộ dữ liệu" cho mỗi thuộc tính
  - 1 ảnh "theo từng hãng" (lưới subplot, mỗi hãng một ô) cho mỗi thuộc tính
  - (tuỳ chọn --moi-hang-mot-anh) mỗi hãng một file ảnh riêng

Cách chạy (từ thư mục gốc của repo):
    python src/ve_histogram.py
    python src/ve_histogram.py --csv data_clean.csv --out figures
    python src/ve_histogram.py --moi-hang-mot-anh

Kết quả:
    figures/histogram/all/<thuoc_tinh>_all.png
    figures/histogram/theo_hang/<thuoc_tinh>_theo_hang.png
    figures/histogram/moi_hang/<thuoc_tinh>/<hang>.png   (nếu dùng --moi-hang-mot-anh)
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# (tên cột, nhãn tiếng Việt, đơn vị, kiểu: "cont" liên tục / "disc" rời rạc, số bin)
THUOC_TINH = [
    ("Gia_ban_trieu", "Giá bán", "triệu VND", "cont", 30),
    ("RAM", "RAM", "GB", "disc", None),
    ("ROM", "Bộ nhớ trong (ROM)", "GB", "disc", None),
    ("Dung_luong_pin", "Dung lượng pin", "mAh", "cont", 30),
    ("Cong_suat_sac_W", "Công suất sạc", "W", "cont", 25),
    ("Kich_thuoc_man", "Kích thước màn hình", "inch", "cont", 30),
    ("Tan_so_quet_Hz", "Tần số quét", "Hz", "disc", None),
    ("Khoi_luong", "Khối lượng", "g", "cont", 30),
    ("Cam_sau_MP", "Camera sau", "MP", "cont", 30),
    ("Cam_truoc_MP", "Camera trước", "MP", "cont", 30),
    ("Nam_ra_mat", "Năm ra mắt", "năm", "disc", None),
]

INK, MUTED, GRID, BLUE, MED = "#1f2937", "#6b7280", "#e5e7eb", "#3b6fb6", "#c2410c"
sns.set_theme(style="whitegrid", rc={
    "font.family": "DejaVu Sans", "axes.edgecolor": "#9ca3af", "grid.color": GRID,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def tl(nhan):
    """Viết thường nhãn khi chèn giữa câu, trừ từ viết tắt (RAM)."""
    return nhan if nhan.startswith("RAM") else nhan.lower()


def slug(s):
    return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")


def chuan_bi_bins(s_all, kind, nbins):
    """Tính bin CHUNG cho toàn bộ dữ liệu để các hãng so sánh được với nhau."""
    if kind == "disc":
        gia_tri = np.sort(s_all.unique())
        return gia_tri, np.arange(-0.5, len(gia_tri) + 0.5, 1)
    return None, np.histogram_bin_edges(s_all, bins=nbins)


def ve_hist(ax, s, kind, gia_tri, bins, hien_trung_vi=True):
    """Vẽ histogram lên 1 trục bằng ax.hist."""
    if len(s) == 0:
        ax.text(0.5, 0.5, "Không có dữ liệu", transform=ax.transAxes,
                ha="center", va="center", color=MUTED)
        ax.set_xticks([]); ax.set_yticks([])
        return
    if kind == "disc":
        vi_tri = np.searchsorted(gia_tri, s.values)       # đổi giá trị -> vị trí 0..k-1
        ax.hist(vi_tri, bins=bins, color=BLUE, edgecolor="white", linewidth=0.8)
        ax.set_xticks(range(len(gia_tri)))
        ax.set_xticklabels([f"{v:g}" for v in gia_tri], fontsize=8)
    else:
        ax.hist(s, bins=bins, color=BLUE, edgecolor="white", linewidth=0.8)
        if hien_trung_vi:
            ax.axvline(s.median(), color=MED, ls="--", lw=1.4)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    sns.despine(ax=ax, left=True)
    ax.tick_params(length=0)


def luu(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print("Đã lưu:", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data_clean.csv")
    ap.add_argument("--out", default="figures")
    ap.add_argument("--moi-hang-mot-anh", action="store_true",
                    help="lưu thêm mỗi hãng một file ảnh riêng")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, encoding="utf-8-sig")
    df["Gia_ban_trieu"] = df["Gia_ban"] / 1e6
    hang_list = df["Hang"].value_counts().index.tolist()   # sắp theo số mẫu giảm dần
    print(f"Đọc {len(df)} dòng, {len(hang_list)} hãng")

    for col, nhan, don_vi, kind, nbins in THUOC_TINH:
        # giá trị "N/a" -> NaN -> bỏ
        df[col] = pd.to_numeric(df[col], errors="coerce")
        s_all = df[col].dropna()
        gia_tri, bins = chuan_bi_bins(s_all, kind, nbins)
        ten = f"{nhan} ({don_vi})"

        # ---- (1) Toàn bộ dữ liệu ----
        fig, ax = plt.subplots(figsize=(9, 6))
        ve_hist(ax, s_all, kind, gia_tri, bins)
        ax.set_title(f"Phân bố {tl(nhan)} – toàn bộ dữ liệu", fontsize=15,
                     fontweight="bold", loc="left", pad=14)
        ax.set_xlabel(ten, fontsize=12)
        ax.set_ylabel("Số máy", fontsize=12)
        ax.text(1.0, 1.02, f"n = {len(s_all)} | trung vị = {s_all.median():g}",
                transform=ax.transAxes, ha="right", va="bottom", color=MUTED, fontsize=10)
        fig.tight_layout()
        luu(fig, os.path.join(args.out, "histogram", "all", f"{slug(col)}_all.png"))

        # ---- (2) Theo từng hãng: lưới subplot ----
        n = len(hang_list)
        ncols = 4
        nrows = int(np.ceil(n / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(4.6 * ncols, 3.4 * nrows),
                                 sharex=(kind == "cont"))
        axes = np.atleast_1d(axes).ravel()
        for ax, hang in zip(axes, hang_list):
            s = df.loc[df["Hang"] == hang, col].dropna()
            ve_hist(ax, s, kind, gia_tri, bins)
            ax.set_title(f"{hang} (n = {len(s)})", fontsize=11, fontweight="bold",
                         loc="left", color=INK)
            ax.set_xlabel(ten, fontsize=8, color=MUTED)
            ax.set_ylabel("Số máy", fontsize=8, color=MUTED)
        for ax in axes[n:]:
            ax.axis("off")
        fig.suptitle(f"Phân bố {tl(nhan)} theo từng hãng", fontsize=17,
                     fontweight="bold", x=0.01, ha="left")
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        luu(fig, os.path.join(args.out, "histogram", "theo_hang", f"{slug(col)}_theo_hang.png"))

        # ---- (3) Tuỳ chọn: mỗi hãng một ảnh ----
        if args.moi_hang_mot_anh:
            for hang in hang_list:
                s = df.loc[df["Hang"] == hang, col].dropna()
                fig, ax = plt.subplots(figsize=(8, 5.5))
                ve_hist(ax, s, kind, gia_tri, bins)
                ax.set_title(f"Phân bố {tl(nhan)} – {hang}", fontsize=14,
                             fontweight="bold", loc="left", pad=12)
                ax.set_xlabel(ten, fontsize=11)
                ax.set_ylabel("Số máy", fontsize=11)
                ax.text(1.0, 1.02, f"n = {len(s)}", transform=ax.transAxes,
                        ha="right", va="bottom", color=MUTED, fontsize=10)
                fig.tight_layout()
                luu(fig, os.path.join(args.out, "histogram", "moi_hang", slug(col),
                                      f"{slug(hang)}.png"))


if __name__ == "__main__":
    main()
