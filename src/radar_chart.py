from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


FEATURES = [
    "Gia_ban",
    "RAM",
    "ROM",
    "Ho_tro_5G",
    "Kich_thuoc_man",
    "Do_sang_nits",
    "Cam_sau_MP",
    "Cam_truoc_MP",
    "Khoi_luong",
]

FEATURE_LABELS = {
    "Gia_ban": "Giá bán",
    "RAM": "RAM",
    "ROM": "ROM",
    "Ho_tro_5G": "Hỗ trợ 5G",
    "Kich_thuoc_man": "Màn hình",
    "Do_sang_nits": "Độ sáng",
    "Cam_sau_MP": "Camera sau",
    "Cam_truoc_MP": "Camera trước",
    "Khoi_luong": "Khối lượng",
}


def plot_cluster_radar(
    df: pd.DataFrame,
    cluster_col: str = "Cluster",
    output_path: str = "figures/radar_chart.png",
) -> Path:
    """Vẽ Radar so sánh giá trị trung bình các thông số giữa những cụm có sẵn.

    Hàm này KHÔNG tự chạy K-means. DataFrame cần có cột nhãn cụm do bước
    phân cụm tạo ra, cùng các cột số trong FEATURES.
    """
    if cluster_col not in df.columns:
        raise ValueError(
            f"Không tìm thấy cột nhãn cụm '{cluster_col}'. "
            "Hãy dùng CSV kết quả phân cụm và truyền đúng tên cột nhãn cụm."
        )

    features = [column for column in FEATURES if column in df.columns]
    if len(features) < 3:
        raise ValueError(
            "Cần ít nhất 3 cột thông số phù hợp để vẽ Radar. "
            f"Các cột tìm thấy: {features}"
        )

    data = df[[cluster_col] + features].copy()
    data = data.dropna(subset=[cluster_col])
    for column in features:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=features, how="all")
    if data.empty:
        raise ValueError("Không có dữ liệu hợp lệ để vẽ Radar.")

    # Điền giá trị thiếu bằng trung vị của từng thông số.
    data[features] = data[features].fillna(data[features].median())
    data = data.dropna(subset=features, how="all")

    # Trung bình từng thông số theo cụm.
    cluster_means = data.groupby(cluster_col, dropna=True)[features].mean()
    if len(cluster_means) < 2:
        raise ValueError(
            "Cần ít nhất 2 cụm trong dữ liệu để so sánh bằng biểu đồ Radar."
        )

    # Đưa trung bình các thông số về cùng thang 0–1 để tránh đơn vị khác nhau
    # (ví dụ giá bán và RAM) làm biểu đồ khó đọc.
    scaler = MinMaxScaler()
    scaled_means = pd.DataFrame(
        scaler.fit_transform(cluster_means),
        index=cluster_means.index,
        columns=features,
    )

    labels = [FEATURE_LABELS.get(feature, feature) for feature in features]
    number_of_axes = len(features)
    angles = np.linspace(0, 2 * np.pi, number_of_axes, endpoint=False).tolist()
    angles += angles[:1]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={"polar": True})
    color_map = plt.get_cmap("tab10")

    for index, (cluster_name, row) in enumerate(scaled_means.iterrows()):
        values = row.tolist()
        values += values[:1]
        label = f"Cụm {cluster_name}"
        color = color_map(index % 10)
        ax.plot(angles, values, linewidth=2, color=color, label=label)
        ax.fill(angles, values, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=8)
    ax.grid(alpha=0.35)
    ax.set_title(
        "Biểu đồ Radar so sánh thông số trung bình giữa các cụm điện thoại",
        fontsize=13,
        pad=24,
    )
    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1.08), title="Các cụm")
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Vẽ biểu đồ Radar từ CSV đã có nhãn cụm; không chạy K-means."
    )
    parser.add_argument(
        "--input",
        default="data/phones_kmeans.csv",
        help="Đường dẫn CSV kết quả phân cụm.",
    )
    parser.add_argument(
        "--cluster-col",
        default="Cluster",
        help="Tên cột nhãn cụm trong CSV.",
    )
    parser.add_argument(
        "--output",
        default="figures/radar_chart.png",
        help="Đường dẫn lưu ảnh PNG.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(
            f"Không tìm thấy file: {input_path}\n"
            "Hãy thay --input bằng đường dẫn CSV kết quả phân cụm."
        )

    df = pd.read_csv(input_path)
    try:
        output = plot_cluster_radar(
            df,
            cluster_col=args.cluster_col,
            output_path=args.output,
        )
    except ValueError as error:
        raise SystemExit(f"Lỗi dữ liệu: {error}") from error

    print(f"Đã lưu biểu đồ Radar tại: {output}")


if __name__ == "__main__":
    main()
