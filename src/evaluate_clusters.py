import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "data_clean.csv")

features = [
    "Gia_ban",
    "RAM",
    "ROM",
    "Kich_thuoc_man",
    "Do_sang_nits",
    "Cam_sau_MP",
    "Cam_truoc_MP",
    "Khoi_luong"
]
X = df[features].apply(pd.to_numeric, errors='coerce')
X = X.fillna(X.mean())

wcss = []
silhouette_scores = []
K_range = range(2, 8)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X, kmeans.labels_))

FIGURE_DIR = ROOT / "figures"
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