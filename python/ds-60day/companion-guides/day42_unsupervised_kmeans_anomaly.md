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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 42 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — unsupervised geometry, cluster stability, and anomaly ranking

### The mental model

Unsupervised algorithms optimize a mathematical objective without known
target labels. K-Means alternates between assigning points to the nearest
centroid and recomputing centroid means. It therefore favors roughly
spherical, similarly scaled clusters under Euclidean distance.

Anomaly detectors produce a score or ranking relative to the fitted
reference distribution. A contamination setting often converts that
ranking into a fixed fraction of labels; it does not prove those cases
are errors or threats. Stability, synthetic controls, and domain review
are essential evidence.

### Worked examples and syntax anatomy

- **`KMeans(n_clusters=k, n_init=..., random_state=...)`:** declares cluster count and repeated initialization so a local optimum is not mistaken for truth.
- **`silhouette_score(X, labels)`:** compares cohesion and separation under the selected distance; it needs at least two nontrivial clusters.
- **`decision_function(X)`:** returns a continuous anomaly score; inspect ordering before applying a threshold.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — show that feature scale changes K-Means geometry

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(4201)
left = np.column_stack([rng.normal(-2, 0.4, 80), rng.normal(0, 100, 80)])
right = np.column_stack([rng.normal(2, 0.4, 80), rng.normal(0, 100, 80)])
X = np.vstack([left, right])

raw_labels = KMeans(n_clusters=2, n_init=10, random_state=4201).fit_predict(X)
scaled_labels = KMeans(n_clusters=2, n_init=10, random_state=4201).fit_predict(
    StandardScaler().fit_transform(X)
)
print({"raw_agreement_with_x_sign": np.mean(raw_labels == (X[:, 0] > 0)),
       "scaled_unique_labels": np.unique(scaled_labels).size})
```

**Expected observation:** The large-unit noise dimension can dominate raw Euclidean distance; scaling changes assignments.

**Assumption to name:** Standard-deviation scaling represents the intended similarity, rather than erasing meaningful units.

### Focused example B — treat anomaly output as a ranking, not a verdict

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.ensemble import IsolationForest

rng = np.random.default_rng(4202)
ordinary = rng.normal(size=(200, 2))
obvious = np.array([[8.0, 8.0], [-8.0, -8.0]])
X = np.vstack([ordinary, obvious])
detector = IsolationForest(contamination=0.02, random_state=4202).fit(X)
scores = detector.decision_function(X)
most_unusual = np.argsort(scores)[:5]
print({"lowest_score_indices": most_unusual.tolist(),
       "injected_indices": [200, 201]})
assert {200, 201}.issubset(set(most_unusual))
```

**Expected observation:** The injected extremes rank among the lowest scores, but the threshold also labels a configured fraction of ordinary data.

**Assumption to name:** The synthetic extremes are only a control; domain review determines whether a real unusual case is harmful or valuable.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define unsupervised geometry, cluster stability, and anomaly ranking in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Naming clusters as real customer types or anomalies as fraud solely because the algorithm produced labels.

**Debug it deliberately:** Check scaling, seed/init stability, cluster sizes, centroid movement, score distribution, synthetic controls, and representative reviewed cases.

**Stop condition:** Do not operationalize unsupervised labels without a semantic validation and false-positive handling plan.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Try several values of `k` and plot inertia versus `k` (the elbow plot).

**Verify:** For task `Try several values of k and plot inertia versus k (the elbow plot)`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Compute silhouette scores for `k` from 2 through 6 and discuss the result.

**Verify:** For task `Compute silhouette scores for k from 2 through 6 and discuss the result`, show the formula or intermediate quantities and check the final value independently rather than trusting one library call.






3. Compare Isolation Forest with Local Outlier Factor.

**Verify:** For task `Compare Isolation Forest with Local Outlier Factor`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Progressive hints

1. Include `k=1` for inertia, but not for silhouette. Record the same fitted
   model's `inertia_` rather than fitting again accidentally.
2. The maximum is a candidate, not an unquestionable answer. Compare the plot
   and whether known generated structure is recovered.
3. Both label outliers as `-1`, but LOF usually uses `fit_predict` for the
   training set. Match their `contamination` values before comparing counts.

### Additional mastery practice

Make unsupervised assumptions observable through scaling, stability, domain checks, and synthetic controls. A cluster ID or anomaly label is not ground truth.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Scaling sensitivity:** Create two features with equal structure but scales of 1 and 10,000. Compare K-Means assignments before and after standardization.
   **Progressive hint:** Euclidean distance squares numeric differences, so the large-unit feature dominates unless that weighting is intentional.

**Verify:** For task `Scaling sensitivity: Create two features with equal structure but scales of 1 and 10,000. Com...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







5. **Cluster stability:** Refit K-Means across at least ten seeds and bootstrap samples. Compare inertia, silhouette, and assignment agreement without assuming numeric cluster labels line up.
   **Progressive hint:** Labels can permute. Use adjusted Rand index or align centers before comparing assignments.

**Verify:** For task `Cluster stability: Refit K-Means across at least ten seeds and bootstrap samples. Compare ine...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







6. **Anomaly validation without labels:** Design an evaluation plan for an anomaly detector when historical anomaly labels are incomplete. Include synthetic injection, review capacity, and contamination sensitivity.
   **Progressive hint:** Use multiple evidence sources: known incidents, injected anomalies, top-k expert review, and stability across reasonable settings.

**Verify:** For task `Anomaly validation without labels: Design an evaluation plan for an anomaly detector when his...`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-42` — Day 42 — K-Means and Anomaly Detection.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize unsupervised geometry, cluster stability, and anomaly ranking. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day42_unsupervised_kmeans_anomaly.md`
- learner artifact: `python/ds-60day/notebooks/day42_unsupervised_kmeans_anomaly.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
