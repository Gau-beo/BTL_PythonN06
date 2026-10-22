from pathlib import Path
import re
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA



ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "data_clean.csv"
OUTPUT_FILE = ROOT / "data" / "phones_kmeans.csv"
MODEL_DIR = ROOT / "models"
MODEL_FILE = MODEL_DIR / "kmeans_pca.pkl"
FIGURE_DIR = ROOT / "figures"
FIGURE_FILE = FIGURE_DIR / "kmeans_pca.png"

FEATURES = [
    "Gia_ban",
    "RAM",
    "ROM",
    "Kich_thuoc_man",
    "Do_sang_nits",
    "Cam_sau_MP",
    "Cam_truoc_MP",
    "Khoi_luong",
]


def chuyen_so(cot):
    """Chuyển dữ liệu có đơn vị về dạng số."""
    cot = cot.astype("string").str.strip()
    cot = cot.str.replace(",", "", regex=False)
    cot = cot.str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
    return pd.to_numeric(cot, errors="coerce")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    
    features = [col for col in FEATURES if col in df.columns]

    if len(features) < 2:
        raise ValueError(
            "Cần ít nhất 2 thuộc tính số để phân cụm."
        )

    X = df[features].copy()

    for col in features:
        X[col] = chuyen_so(X[col])

    
    features = [
        col for col in features
        if X[col].notna().any()
    ]
    X = X[features]

   
    valid_rows = X.notna().any(axis=1)
    df = df.loc[valid_rows].copy()
    X = X.loc[valid_rows]

    if len(features) < 2 or len(df) < 4:
        raise ValueError(
            "Dữ liệu hợp lệ không đủ để phân cụm."
        )

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    X_imputed = imputer.fit_transform(X)
    X_scaled = scaler.fit_transform(X_imputed)

    
    kmeans = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )
    df["Cluster"] = kmeans.fit_predict(X_scaled)

   
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    df["PCA1"] = X_pca[:, 0]
    df["PCA2"] = X_pca[:, 1]

  
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

   
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    joblib.dump(
        {
            "kmeans": kmeans,
            "imputer": imputer,
            "scaler": scaler,
            "pca": pca,
            "features": features,
        },
        MODEL_FILE
    )

   
    plt.figure(figsize=(10, 6))

    for cluster in sorted(df["Cluster"].unique()):
        mask = df["Cluster"] == cluster
        plt.scatter(
            df.loc[mask, "PCA1"],
            df.loc[mask, "PCA2"],
            label=f"Cluster {cluster}",
            alpha=0.75
        )

    plt.title("K-means Clustering of Smartphones using PCA")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIGURE_FILE, dpi=300)
    plt.close()

    print(f"So dien thoai da phan cum: {len(df)}")
    print(f"So cum: {df['Cluster'].nunique()}")
    print(f"Thuoc tinh su dung: {features}")
    print(
        "Tong phuong sai PCA giai thich: "
        f"{pca.explained_variance_ratio_.sum():.2%}"
    )
    print(f"Da luu CSV: {OUTPUT_FILE}")
    print(f"Da luu mo hinh: {MODEL_FILE}")
    print(f"Da luu bieu do: {FIGURE_FILE}")


if __name__ == "__main__":
    main()