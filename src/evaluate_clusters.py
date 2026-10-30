import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "data_clean.csv"
FIGURE_DIR = ROOT / "figures"

#INPUT_FILE = ROOT / "data" / "test" / "data_clean.csv"
#FIGURE_DIR = ROOT / "data" / "test" / "figures"

df = pd.read_csv(INPUT_FILE)

features = [
    "Gia_ban",
    "RAM",
    "ROM",
    "Kich_thuoc_man",
    "Cam_sau_MP",
    "Cam_truoc_MP",
    "Khoi_luong"
]

X = df[features].apply(pd.to_numeric, errors='coerce')
X = X.fillna(X.median())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

wcss = []
silhouette_scores = []
K_range = range(2, 8)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    print(f"k={k}: WCSS={kmeans.inertia_:.0f}  silhouette={silhouette_scores[-1]:.3f}")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(8, 5))
plt.plot(K_range, wcss, marker='o', linestyle='-')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of clusters (k)')
plt.ylabel('WCSS')
plt.grid(True, alpha=0.3)
plt.savefig(FIGURE_DIR / 'elbow.png', dpi=300)
plt.close()

plt.figure(figsize=(8, 5))
plt.plot(K_range, silhouette_scores, marker='o', color='orange', linestyle='-')
plt.title('Silhouette Scores for Optimal k')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Silhouette Score')
plt.grid(True, alpha=0.3)
plt.savefig(FIGURE_DIR / 'silhouette.png', dpi=300)
plt.close()
