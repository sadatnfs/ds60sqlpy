# Day 42 — K-Means and Anomaly Detection

**Lesson ID:** `python-42` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Unsupervised algorithms find structure without target labels. Their outputs are
hypotheses to investigate—not automatically true customer segments, root causes,
or fraud labels.

## Learning objectives

By the end of the lesson, you can:

- fit K-Means with deterministic initialization;
- compare inertia and silhouette score across cluster counts;
- state the geometric assumptions behind K-Means;
- use Isolation Forest and Local Outlier Factor (LOF); and
- validate clusters or anomalies with stability and domain evidence.

## Prerequisites

- Complete `python-41` (class imbalance).
- Recall feature scaling, distance, and held-out evaluation.
- Be able to plot two-dimensional NumPy arrays.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Cluster | Group induced by a similarity rule, not necessarily a natural category |
| Centroid | Mean feature vector assigned to a K-Means cluster |
| Inertia | Sum of squared distances from observations to their assigned centroids |
| Silhouette score | Relative within-cluster cohesion versus nearest-cluster separation |
| Anomaly score | Continuous measure of how unusual an observation appears |
| Contamination | Assumed fraction used to convert scores into outlier labels |
| Global anomaly | Unusual relative to the whole dataset |
| Local anomaly | Unusual relative to a neighborhood |

Inertia always decreases as `k` increases, so its minimum cannot select `k`.
Look for diminishing improvement, stability, and usefulness.

## Worked example: compare candidate cluster counts

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

X, _ = make_blobs(
    n_samples=600,
    centers=3,
    cluster_std=1.2,
    random_state=42,
)
X_scaled = StandardScaler().fit_transform(X)

for k in range(2, 7):
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(X_scaled)
    print(k, model.inertia_, silhouette_score(X_scaled, labels))
```

Scaling is appropriate when each numeric dimension should contribute comparably
to Euclidean distance. Do not scale mechanically when original distances have a
meaningful common unit.

## Learner exercises

1. Try several values of `k` and plot inertia versus `k` (the elbow plot).
2. Compute silhouette scores for `k` from 2 through 6 and discuss the result.
3. Compare Isolation Forest with Local Outlier Factor.

### Progressive hints

1. Include `k=1` for inertia, but not for silhouette. Record the same fitted
   model's `inertia_` rather than fitting again accidentally.
2. The maximum is a candidate, not an unquestionable answer. Compare the plot
   and whether known generated structure is recovered.
3. Both label outliers as `-1`, but LOF usually uses `fit_predict` for the
   training set. Match their `contamination` values before comparing counts.

## Self-check

- Why does K-Means struggle with curved, different-density, or differently
  sized clusters?
- Why are cluster labels `0`, `1`, and `2` not ordered categories?
- What does `contamination=0.02` assume rather than discover?
- How would you verify whether flagged anomalies are useful?

Expected behavior: the synthetic three-blob dataset usually favors a cluster
count near three, while anomaly detectors flag approximately the requested
fraction but may disagree on which points.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Unscaled mixed-range features | Largest-scale feature dominates distance | Standardize when domain geometry supports it |
| Treating an elbow as objective | Ambiguous visual choice | Combine metrics, stability, and domain value |
| Naming clusters from centroids alone | Overconfident semantics | Inspect distributions and representative records |
| Treating every outlier as an error/fraud | Harmful false positives | Review context and downstream cost |
| Fitting LOF for future scoring without `novelty=True` | API cannot score new rows as intended | Choose novelty mode and evaluate separately |

Isolation Forest is often convenient in higher dimensions. LOF captures local
density differences but is sensitive to neighborhood size and scoring mode.

## Next step

- Work in the [Day 42 learner notebook](../notebooks/day42_unsupervised_kmeans_anomaly.ipynb).
- Then review the
  [Day 42 solution](../solutions/day42_unsupervised_kmeans_anomaly/day42_solutions.md).
- Continue to [Day 43 — Model Interpretation](day43_model_interpretation_shap_pdp.md).
