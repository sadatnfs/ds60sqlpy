# Day 36 — Dimensionality Reduction with PCA

**Lesson ID:** `python-36` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Principal component analysis (PCA) rotates numeric data into orthogonal
directions ordered by variance. It can compress correlated features, visualize a
dataset, or denoise measurements, but it does not know the target or preserve
the original feature meanings.

## Learning objectives

By the end of the lesson, you can:

- explain principal components as directions of decreasing variance;
- standardize features before PCA when scale should not determine importance;
- choose a component count from cumulative explained variance;
- compare supervised feature selection with unsupervised feature extraction; and
- place PCA or `SelectKBest` inside cross-validation to avoid leakage.

## Prerequisites

- Complete `python-35` (model evaluation and cross-validation).
- Recall matrix shape, rank, and singular values from `python-33`.
- Be comfortable with scikit-learn pipelines from `python-34`.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Principal component | Unit direction that captures as much remaining variance as possible while staying orthogonal to earlier components |
| Loading | Weight connecting an original feature to a component |
| Score | An observation's coordinate in component space |
| Explained variance ratio | Fraction of dataset variance represented by a component |
| Scree plot | Component index versus individual or cumulative explained variance |
| Feature extraction | Creating new features from combinations of originals |
| Feature selection | Retaining a subset of original features |

PCA preserves variance, not class separation, fairness, causal structure, or
semantic importance. A low-variance feature can still be highly predictive.

## Worked example: scale, fit, inspect

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
projection = make_pipeline(StandardScaler(), PCA())
X_components = projection.fit_transform(X)

pca = projection.named_steps["pca"]
cumulative = np.cumsum(pca.explained_variance_ratio_)
components_for_95 = int(np.searchsorted(cumulative, 0.95) + 1)
print(cumulative, components_for_95)
```

The scaler and PCA must be fitted inside each training fold when measuring model
performance. Fitting them once on the full dataset gives validation folds
information about global means, variances, and component directions.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 36 learner notebook from this guide's **Next
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

## Concept deep dive — PCA geometry, scaling, variance, and reconstruction

### The mental model

Principal component analysis (PCA) rotates centered feature space to
new orthogonal axes ordered by captured variance. A component is a
direction; a score is an observation projected onto that direction;
a loading describes how original features contribute. PCA does not
know the target and does not discover causal factors.

Variance is measured in squared feature units. If one feature is
measured on a much larger numeric scale, unscaled PCA may devote its
first component to that unit rather than to the structure you care
about. Component count is therefore a modeling choice connected to
scaling, reconstruction, and downstream performance.

### Worked examples and syntax anatomy

- **`StandardScaler()`:** centers and scales features when equalized variance, rather than raw units, is the intended geometry.
- **`PCA(n_components=...).fit(X_train)`:** learns training-only means, axes, and explained variance.
- **`.transform()` / `.inverse_transform()`:** moves between feature and component spaces, enabling reconstruction-error checks.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — observe how units change the first component

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(3601)
signal = rng.normal(size=300)
X = np.column_stack([
    signal + rng.normal(scale=0.1, size=300),
    1_000 * rng.normal(size=300),
])

raw = PCA(n_components=1).fit(X)
scaled = PCA(n_components=1).fit(StandardScaler().fit_transform(X))
print({"raw_loading": raw.components_[0],
       "scaled_loading": scaled.components_[0]})
```

**Expected observation:** Raw PCA points almost entirely along the large-unit feature; scaling changes the geometry and loadings.

**Assumption to name:** Equal standard-deviation weighting is scientifically appropriate; scaling is not automatically correct.

### Focused example B — connect retained components to reconstruction error

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

X = StandardScaler().fit_transform(load_iris().data)
errors = {}
for components in (1, 2, 3, 4):
    pca = PCA(n_components=components).fit(X)
    reconstructed = pca.inverse_transform(pca.transform(X))
    errors[components] = np.mean((X - reconstructed) ** 2)
print(errors)
assert all(errors[k] >= errors[k + 1] for k in (1, 2, 3))
```

**Expected observation:** Reconstruction error cannot increase as more components are retained and reaches numerical zero with all components.

**Assumption to name:** Squared reconstruction error is a useful measure of the information relevant to this task.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define PCA geometry, scaling, variance, and reconstruction in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Choosing components from the full dataset and then cross-validating a downstream model.

**Debug it deliberately:** Put scaling and PCA inside the evaluated pipeline; inspect component shapes, cumulative variance, and reconstruction on training versus validation.

**Stop condition:** Do not label a component semantically from one large loading without checking units, correlations, sign ambiguity, and stability.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Plot cumulative explained variance and choose a component count.

**Verify:** Practice 1 — PCA geometry, scaling, variance, and reconstruction — fit PCA on training data only, print cumulative explained variance by component, and choose the smallest count reaching a declared threshold such as 95%; assert transformed train/test column counts match that choice.

2. Compare PCA before and after feature standardization.

**Verify:** Practice 2 — PCA geometry, scaling, variance, and reconstruction — on one frozen split, report feature scales and PCA explained-variance ratios before and after StandardScaler; verify each scaler/PCA pair is fitted on training rows only.

3. Try `SelectKBest` on a classification dataset and compare its validated
   performance with PCA.

**Verify:** Practice 3 — PCA geometry, scaling, variance, and reconstruction — evaluate SelectKBest and scaled PCA with identical folds, component/feature counts, estimator, and metric; print every fold score plus mean/std and keep the final test labels unopened.

### Progressive hints

1. Fit all possible components first, then use `np.cumsum`. Declare a threshold
   such as 95% before looking for the first component count that crosses it.
2. Compare both the variance ratios and two-dimensional scatter plots. Iris
   features use different physical units and spreads.
3. Put each alternative in its own pipeline. `f_classif` sees the target; PCA
   does not, so the comparison includes an interpretability tradeoff.

### Additional mastery practice

Use dimensionality reduction as a fitted transformation with measurable information loss. Keep scaling and supervised feature selection inside validation.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Reconstruction analysis:** Fit scaled PCA with several component counts, inverse-transform the representations, and plot mean squared reconstruction error versus retained components.
   **Progressive hint:** Call transform then inverse_transform on the same fitted PCA and compare in scaled space. Error should not increase as components are added.

**Verify:** Reconstruction analysis — for each retained-component count, print reconstruction MSE and save the labeled curve; assert inverse-transformed shape equals the scaled input shape and MSE is non-increasing up to floating-point tolerance.

5. **Interpretation edge case:** Fit PCA twice to equivalent data and explain why a component and all of its loadings may appear with the opposite sign while the projection remains equivalent.
   **Progressive hint:** Eigenvectors are direction axes: v and -v describe the same axis. Compare subspaces or absolute loading patterns, not raw signs alone.

**Verify:** Interpretation edge case — fit the equivalent PCA inputs, align component signs by dot product, and assert transformed coordinates/loadings match after sign alignment within 1e-10 while explained-variance ratios are unchanged.

6. **Leakage debugging:** Create a dataset with many noise features, run SelectKBest once before cross-validation, and then correctly inside a Pipeline. Explain the expected score difference.
   **Progressive hint:** Selection performed globally can choose noise features that happen to correlate with all labels, including validation labels.

**Verify:** Leakage debugging — print fold scores for SelectKBest fitted globally and inside Pipeline on the same seeded noise dataset; assert the pipeline owns fit within each fold and retain the observed optimism gap without promising its exact size.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why can a component's sign flip without changing the PCA solution?
- When does scaling before PCA change the question being asked?
- Why must target-aware selection happen inside each training fold?
- Can you reconstruct the original data exactly after retaining only two
  components? What determines the reconstruction error?

Expected behavior: cumulative explained variance is nondecreasing and ends near
1 when all components are retained.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Diagnostic | Response |
|---|---|---|
| One high-variance unit dominates | Raw and scaled results differ greatly | Decide whether raw scale has domain meaning |
| PCA fitted before cross-validation | Validation data influenced directions | Put PCA in a pipeline |
| Loadings treated as causal effects | Components are associations | Use cautious, domain-informed interpretation |
| Component count selected from test performance | Test set becomes tuning data | Select in training/CV, evaluate once on holdout |
| PCA applied indiscriminately to categories | Numeric geometry is artificial | Encode with a method suited to the feature and goal |

Compression can reduce runtime and collinearity. It also obscures feature
meaning and may remove predictive low-variance signals. Validate the complete
downstream objective.

## Next step

- Work in the [Day 36 learner notebook](../notebooks/day36_dimensionality_reduction_pca.ipynb).
- Then review the
  [Day 36 solution](../solutions/day36_dimensionality_reduction_pca/day36_solutions.md).
- Continue to [Day 37 — Regularization](day37_regularization_linear_models.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-36` — Day 36 — Dimensionality Reduction with PCA.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize PCA geometry, scaling, variance, and reconstruction. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day36_dimensionality_reduction_pca.md`
- learner artifact: `python/ds-60day/notebooks/day36_dimensionality_reduction_pca.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-35`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
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
