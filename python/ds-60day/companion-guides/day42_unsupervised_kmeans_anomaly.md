# Day 42 — Unsupervised Learning: KMeans and Anomaly Detection (Companion Guide)

## Learning objectives
- Cluster with KMeans and evaluate with silhouette and inertia
- Understand initialization, scaling, and k selection
- Detect anomalies with IsolationForest and OneClassSVM

## Why this matters
Clustering reveals latent structure; anomaly detection flags rare patterns when labels are scarce.

## Core concepts and examples
### KMeans
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

km = KMeans(n_clusters=6, n_init='auto', random_state=0)
labels = km.fit_predict(X_scaled)
sil = silhouette_score(X_scaled, labels)
```

### Anomaly detection
```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.02, random_state=0)
score = iso.fit_predict(X)
```

## Common pitfalls
- Running KMeans on unscaled features; always scale
- Over-interpreting clusters without domain validation
- Treating anomaly detector scores as calibrated probabilities

## Practice exercises
1) Elbow plot and silhouette analysis to pick k
2) Compare IsolationForest vs LocalOutlierFactor
3) Label cluster centroids and interpret top features

## Further reading
- Clustering: https://scikit-learn.org/stable/modules/clustering.html
- Outlier detection: https://scikit-learn.org/stable/modules/outlier_detection.html
