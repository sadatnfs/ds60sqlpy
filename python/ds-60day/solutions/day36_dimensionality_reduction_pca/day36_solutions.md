# Day 36 — Solutions: Dimensionality Reduction with PCA

We standardize features, fit PCA, and choose the number of components via cumulative explained variance. We also compare PCA before/after scaling and briefly try SelectKBest.

Contents
- Exercise 1: Plot cumulative explained variance and choose K
- Exercise 2: Compare PCA before vs after scaling
- Exercise 3: Try SelectKBest and compare to PCA

---

Setup
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
import numpy as np, matplotlib.pyplot as plt
X, y = load_iris(return_X_y=True)
```

Worked reference for Exercise 1 — Cumulative explained variance (scree)
```python
sc = StandardScaler()
Xz = sc.fit_transform(X)

pca = PCA().fit(Xz)  # all components
cum = np.cumsum(pca.explained_variance_ratio_)

plt.plot(range(1, len(cum)+1), cum, marker='o')
plt.axhline(0.95, color='r', ls='--', label='95%')
plt.xlabel('n_components'); plt.ylabel('cumulative explained variance')
plt.title('Scree (cumulative)'); plt.legend(); plt.tight_layout(); plt.show()

k95 = int(np.argmax(cum >= 0.95) + 1)
print({'k_95pct': k95, 'cum': cum})
```
Line-by-line
- Standardize first so features contribute comparably
- PCA().fit gets variance ratios; cumulative sum guides K selection

---

Worked reference for Exercise 2 — PCA before vs after scaling
```python
pca_raw = PCA(n_components=2).fit(X)
X2_raw = pca_raw.transform(X)

pca_z = PCA(n_components=2).fit(Xz)
X2_z  = pca_z.transform(Xz)

f, ax = plt.subplots(1,2, figsize=(8,3))
ax[0].scatter(X2_raw[:,0], X2_raw[:,1], c=y, cmap='tab10', s=15)
ax[0].set_title('PCA on raw features')
ax[1].scatter(X2_z[:,0], X2_z[:,1], c=y, cmap='tab10', s=15)
ax[1].set_title('PCA on standardized features')
plt.tight_layout(); plt.show()
```
Observation
- Without scaling, high-variance features dominate components; scaling often yields more balanced PCs

---

Worked reference for Exercise 3 — SelectKBest vs PCA
```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

clf_pca = Pipeline([
    ('sc', StandardScaler()),
    ('pca', PCA(n_components=2, random_state=0)),
    ('lr', LogisticRegression(max_iter=1000))
])

clf_kbest = Pipeline([
    ('sc', StandardScaler()),
    ('k', SelectKBest(score_func=f_classif, k=2)),
    ('lr', LogisticRegression(max_iter=1000))
])

print('PCA acc:', cross_val_score(clf_pca, X, y, cv=5).mean())
print('KBest acc:', cross_val_score(clf_kbest, X, y, cv=5).mean())
```
Notes
- PCA is unsupervised; SelectKBest uses label information
- Pick based on validation performance and downstream interpretability

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`StandardScaler()`:** centers and scales features when equalized variance, rather than raw units, is the intended geometry.
2. **`PCA(n_components=...).fit(X_train)`:** learns training-only means, axes, and explained variance.
3. **`.transform()` / `.inverse_transform()`:** moves between feature and component spaces, enabling reconstruction-error checks.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** The solution treats PCA as a fitted transformation with a declared geometry and validates both variance retention and downstream consequences.

**Useful alternative:** Supervised feature selection can preserve target-relevant original columns, while regularization may avoid a separate reduction step.

**Trade-off:** Fewer components reduce dimension and noise but sacrifice information and make feature-level explanations less direct.

**Edge case to test:** Constant columns, missing values, very sparse inputs, or requesting more components than rank require preprocessing or an explicit failure.

**Evidence of correctness:** Fit scaling/PCA on training data only, assert transformed shapes, report cumulative explained variance and reconstruction error, and compare downstream validation against a no-PCA baseline.

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

### Exercise 1 — Original lesson practice

**Prompt:** Plot cumulative explained variance and choose a component count.

**How to reason about it:** Fit the maximum useful component count first, compute cumulative explained variance, and choose a threshold before reading the answer. Variance retained is not the same as predictive signal retained.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — PCA geometry, scaling, variance, and reconstruction — fit PCA on training data only, print cumulative explained variance by component, and choose the smallest count reaching a declared threshold such as 95%; assert transformed train/test column counts match that choice.

### Exercise 2 — Original lesson practice

**Prompt:** Compare PCA before and after feature standardization.

**How to reason about it:** PCA is driven by variance, so features with larger units can dominate without scaling. Compare both variance ratios and downstream validation using pipelines; never scale from the full dataset before the split.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — PCA geometry, scaling, variance, and reconstruction — on one frozen split, report feature scales and PCA explained-variance ratios before and after StandardScaler; verify each scaler/PCA pair is fitted on training rows only.

### Exercise 3 — Original lesson practice

**Prompt:** Try `SelectKBest` on a classification dataset and compare its validated performance with PCA.

**How to reason about it:** SelectKBest sees the target while PCA does not. Both must be fitted inside each training fold, and the comparison should include stability and interpretability rather than only the largest score.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — PCA geometry, scaling, variance, and reconstruction — evaluate SelectKBest and scaled PCA with identical folds, component/feature counts, estimator, and metric; print every fold score plus mean/std and keep the final test labels unopened.

### Exercise 4 — Reconstruction analysis

**Prompt:** Fit scaled PCA with several component counts, inverse-transform the representations, and plot mean squared reconstruction error versus retained components.

**Reasoning before implementation:** Call transform then inverse_transform on the same fitted PCA and compare in scaled space. Error should not increase as components are added.

Reconstruction error measures information discarded in the coordinate system
PCA optimized. It should be non-increasing as components are added, apart from
tiny floating-point noise.

```python
import numpy as np
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

X, _ = load_iris(return_X_y=True)
scaled = StandardScaler().fit_transform(X)
errors = []
for components in range(1, scaled.shape[1] + 1):
    pca = PCA(n_components=components, random_state=36)
    reconstructed = pca.inverse_transform(pca.fit_transform(scaled))
    errors.append(float(np.mean((scaled - reconstructed) ** 2)))
assert all(a + 1e-12 >= b for a, b in zip(errors, errors[1:]))
```

Low reconstruction error does not guarantee good class separation. Evaluate
the reduced representation against the actual downstream objective.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Reconstruction analysis — for each retained-component count, print reconstruction MSE and save the labeled curve; assert inverse-transformed shape equals the scaled input shape and MSE is non-increasing up to floating-point tolerance.

### Exercise 5 — Interpretation edge case

**Prompt:** Fit PCA twice to equivalent data and explain why a component and all of its loadings may appear with the opposite sign while the projection remains equivalent.

**Reasoning before implementation:** Eigenvectors are direction axes: v and -v describe the same axis. Compare subspaces or absolute loading patterns, not raw signs alone.

PCA's sign is not identifiable. If a component vector is multiplied by -1,
its projected scores are also multiplied by -1, so reconstruction and explained
variance are unchanged. Libraries may choose different signs across versions
or equivalent fits.

When monitoring a pipeline, align component signs before comparing loadings or
compare invariant quantities such as absolute cosine similarity and projection
matrices. Do not interpret a sign flip as learned behavioral drift.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Interpretation edge case — fit the equivalent PCA inputs, align component signs by dot product, and assert transformed coordinates/loadings match after sign alignment within 1e-10 while explained-variance ratios are unchanged.

### Exercise 6 — Leakage debugging

**Prompt:** Create a dataset with many noise features, run SelectKBest once before cross-validation, and then correctly inside a Pipeline. Explain the expected score difference.

**Reasoning before implementation:** Selection performed globally can choose noise features that happen to correlate with all labels, including validation labels.

The globally selected feature set has already inspected every target, so the
fold score is contaminated even if the classifier itself is refit. The correct
object is:

```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

pipeline = Pipeline(
    [
        ("select", SelectKBest(score_func=f_classif, k=10)),
        ("model", LogisticRegression(max_iter=1_000)),
    ]
)
```

Pass raw features and this complete pipeline to cross-validation. Repeat the
simulation across seeds; one dataset can understate or overstate the leakage.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Leakage debugging — print fold scores for SelectKBest fitted globally and inside Pipeline on the same seeded noise dataset; assert the pipeline owns fit within each fold and retain the observed optimism gap without promising its exact size.
