# Day 42 — Solutions: Unsupervised Learning (KMeans & Anomaly Detection)

We cluster data with KMeans, evaluate with inertia (elbow) and silhouette (with caveats), and perform simple anomaly detection with IsolationForest and LocalOutlierFactor (LOF).

Contents
- Exercise 1: Elbow method — plot inertia vs K and pick a knee
- Exercise 2: Silhouette score for K in [2..6] and discussion
- Exercise 3: Compare IsolationForest and LOF for anomaly detection

---

Setup
```python
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import matplotlib.pyplot as plt

X, y_true = make_blobs(n_samples=600, centers=3, cluster_std=1.2, random_state=42)
```

Exercise 1 — Elbow (inertia vs K)
```python
Ks = range(1, 10)
inertias = []
for k in Ks:
    km = KMeans(n_clusters=k, n_init='auto', random_state=42).fit(X)
    inertias.append(km.inertia_)

plt.plot(list(Ks), inertias, marker='o')
plt.xlabel('K (clusters)'); plt.ylabel('Inertia (within-cluster SSE)')
plt.title('Elbow method')
plt.tight_layout(); plt.show()
```
Interpretation
- Look for a knee where inertia reduction starts diminishing; that K is a candidate
- Elbow can be ambiguous; use it with other signals (silhouette, domain insight)

---

Exercise 2 — Silhouette for K in [2..6]
```python
sil_scores = {}
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init='auto', random_state=42).fit(X)
    sil = silhouette_score(X, km.labels_)
    sil_scores[k] = sil
sil_scores
```
Notes
- Higher silhouette indicates tighter, well-separated clusters
- Caveats: silhouette assumes convex clusters; non-spherical shapes may mislead

Optional visualization
```python
k_best = max(sil_scores, key=sil_scores.get)
km = KMeans(n_clusters=k_best, n_init='auto', random_state=42).fit(X)
X2 = X  # in 2D already
plt.scatter(X2[:,0], X2[:,1], c=km.labels_, cmap='viridis', s=15)
plt.title(f'KMeans clusters (K={k_best}, silhouette={sil_scores[k_best]:.3f})')
plt.tight_layout(); plt.show()
```

---

Exercise 3 — Anomaly detection: IsolationForest vs LOF
```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# IsolationForest: -1 outlier, 1 inlier
iso = IsolationForest(contamination=0.02, random_state=42).fit(X)
pred_iso = iso.predict(X)
iso_rate = (pred_iso == -1).mean()

# LOF: -1 outlier, 1 inlier (fit_predict required)
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.02)
pred_lof = lof.fit_predict(X)
lof_rate = (pred_lof == -1).mean()

{'iso_outlier_rate': float(iso_rate), 'lof_outlier_rate': float(lof_rate)}
```
Discussion
- IsolationForest works well for high-dimensional data and is model-based
- LOF is density-based and local; can catch local anomalies but is sensitive to neighborhood size
- Always validate detected anomalies with domain knowledge; synthetic labels can be used for benchmarking if available
