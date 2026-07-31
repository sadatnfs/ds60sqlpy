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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`KMeans(n_clusters=k, n_init=..., random_state=...)`:** declares cluster count and repeated initialization so a local optimum is not mistaken for truth.
2. **`silhouette_score(X, labels)`:** compares cohesion and separation under the selected distance; it needs at least two nontrivial clusters.
3. **`decision_function(X)`:** returns a continuous anomaly score; inspect ordering before applying a threshold.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Geometry and stability checks establish what the algorithm optimized; domain evidence supplies meaning the objective cannot.

**Useful alternative:** Density-based clustering handles irregular shapes, while robust statistical rules or supervised detection may better match labeled anomalies.

**Trade-off:** More clusters reduce inertia mechanically but increase complexity; stricter anomaly thresholds reduce review volume while missing more unusual cases.

**Edge case to test:** Duplicate points, all-identical data, fewer rows than clusters, high-dimensional distance concentration, or changing contamination break naive interpretations.

**Evidence of correctness:** Compare scaled/unscaled results, repeat seeds, report cluster sizes and stability, retain continuous anomaly scores, and review synthetic plus domain controls.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Try several values of `k` and plot inertia versus `k` (the elbow plot).

**How to reason about it:** Inertia always falls as k increases, so the elbow is a judgment rather than an optimizer. Fit each candidate on the same scaled representation and inspect stability and usefulness alongside the curve.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Try several values of k and plot inertia versus k (the elbow plot)`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Reasoning notes for original Exercise 2

**Prompt:** Compute silhouette scores for `k` from 2 through 6 and discuss the result.

**How to reason about it:** Silhouette requires at least two clusters and rewards compact separation under its distance metric. A maximum is a candidate, not proof that the data contains that many real-world groups.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Compute silhouette scores for k from 2 through 6 and discuss the result`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then show the formula or intermediate quantities and check the final value independently rather than trusting one library call.








### Reasoning notes for original Exercise 3

**Prompt:** Compare Isolation Forest with Local Outlier Factor.

**How to reason about it:** Isolation Forest and LOF use different notions of unusualness. Match contamination, understand LOF's novelty mode, and compare known synthetic outliers or reviewed cases instead of label overlap alone.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Compare Isolation Forest with Local Outlier Factor`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.








### Exercise 4 — Scaling sensitivity

**Prompt:** Create two features with equal structure but scales of 1 and 10,000. Compare K-Means assignments before and after standardization.

**Reasoning before implementation:** Euclidean distance squares numeric differences, so the large-unit feature dominates unless that weighting is intentional.

Scaling changes the geometry, not just presentation. Place the scaler and
K-Means in one pipeline and fit on the intended training/reference population.
Compare cluster centers after inverse transformation so stakeholders can read
them in original units.

Standardization is not automatically correct: a domain-approved unit or
feature weight can be meaningful. State why the chosen metric represents
similarity for this problem.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Create two features with equal structure but scales of 1 and 10,000. Compare K-Means assignme...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Exercise 5 — Cluster stability

**Prompt:** Refit K-Means across at least ten seeds and bootstrap samples. Compare inertia, silhouette, and assignment agreement without assuming numeric cluster labels line up.

**Reasoning before implementation:** Labels can permute. Use adjusted Rand index or align centers before comparing assignments.

A solution that appears only for one initialization is weak evidence of
structure. Summarize score distributions and pairwise adjusted Rand index.
Inspect whether small or ambiguous clusters dissolve across resamples.

High stability still does not prove business meaning; it only shows the
algorithm consistently finds the same geometry. Validate profiles with domain
knowledge and downstream usefulness.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Refit K-Means across at least ten seeds and bootstrap samples. Compare inertia, silhouette, a...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.








### Exercise 6 — Anomaly validation without labels

**Prompt:** Design an evaluation plan for an anomaly detector when historical anomaly labels are incomplete. Include synthetic injection, review capacity, and contamination sensitivity.

**Reasoning before implementation:** Use multiple evidence sources: known incidents, injected anomalies, top-k expert review, and stability across reasonable settings.

Measure recall on carefully designed synthetic anomalies only as a unit test
of detectable patterns—not as full real-world accuracy. Review a bounded top-k
sample with blinded domain experts and track confirmed-yield plus false-alarm
cost. Sweep contamination and report how the review queue changes.

Preserve raw scores so policy thresholds can change without refitting. Never
describe the detector's `-1` output as a confirmed incident.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Design an evaluation plan for an anomaly detector when historical anomaly labels are incomple...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
