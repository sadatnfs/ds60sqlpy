# Day 40 — Solutions: Hyperparameter Tuning with SearchCV

We build a Pipeline, perform parameter search with GridSearchCV/RandomizedSearchCV, and discuss nested CV for unbiased estimates.

Contents
- Exercise 1: GridSearchCV with an SVC pipeline
- Exercise 2: RandomizedSearchCV over a wider parameter space
- Exercise 3: Nested CV (concept + code sketch)

---

Worked reference for Exercise 1 — GridSearchCV + Pipeline (SVC)
```python
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.datasets import load_breast_cancer

X, y = load_breast_cancer(return_X_y=True)

pipe = Pipeline([
    ('sc', StandardScaler()),
    ('svc', SVC(probability=False))
])

param_grid = {
    'svc__C': [0.1, 1, 10],
    'svc__kernel': ['linear', 'rbf'],
    'svc__gamma': ['scale', 'auto']
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
search = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=1, refit=True)
search.fit(X, y)
search.best_params_, search.best_score_
```
Line-by-line
- Keep preprocessing (scaler) in the Pipeline to avoid leakage
- Use StratifiedKFold for classification
- scoring='roc_auc' is often better than accuracy for imbalanced data

---

Worked reference for Exercise 2 — RandomizedSearchCV
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform

param_dist = {
    'svc__C': loguniform(1e-3, 1e3),
    'svc__gamma': ['scale', 'auto'],
    'svc__kernel': ['linear', 'rbf']
}

rand = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=20,
                          cv=cv, scoring='roc_auc', n_jobs=1, random_state=0, refit=True)
rand.fit(X, y)
rand.best_params_, rand.best_score_
```
Notes
- RandomizedSearch explores broader spaces efficiently
- Prefer bounded priors (e.g., loguniform for C) for sensible sampling

---

Worked reference for Exercise 3 — Nested CV (sketch)
```python
from sklearn.model_selection import cross_val_score

# inner search for model selection; outer CV for unbiased performance estimate
inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

inner_search = GridSearchCV(pipe, param_grid, cv=inner, scoring='roc_auc', n_jobs=1)
outer_scores = cross_val_score(inner_search, X, y, cv=outer, scoring='roc_auc', n_jobs=1)
{'outer_auc_mean': outer_scores.mean(), 'outer_auc_std': outer_scores.std()}
```
Takeaways
- Tune inside the cross-validation loop to avoid optimistic bias (nested CV)
- Keep all preprocessing inside Pipelines
- Pick metrics aligned with the problem and validate on held-out data

---

**Portable worker default:** These reference runs use `n_jobs=1` so they behave predictably on Windows, CI runners, and constrained notebook environments. After correctness is established, benchmark a larger worker count on your own workload rather than assuming `n_jobs=1` is faster.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`step__parameter`:** addresses nested pipeline parameters; inspect `get_params()` instead of guessing names.
2. **`ParameterGrid(space)`:** enumerates the exact Cartesian search and makes the fit budget calculable.
3. **`GridSearchCV(..., scoring=..., refit=...)`:** scores candidates in inner folds and refits the selected configuration on all supplied rows.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Explicit candidate enumeration controls compute, while a declared refit metric and outer evaluation control selection bias.

**Useful alternative:** Randomized or successive-halving search can spend a bounded budget across broader spaces; domain-guided manual comparison may be clearer for few candidates.

**Trade-off:** A larger search may find a better inner-fold score while increasing compute, multiplicity, and overfitting to the validation procedure.

**Edge case to test:** Invalid parameter combinations, stochastic candidates without seeds, NaN scores, and resource oversubscription can silently distort rankings.

**Evidence of correctness:** Count candidates and expected fits, inspect every failed/NaN result, declare the refit metric, and evaluate the full search procedure on untouched data or outer folds.

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

**Prompt:** Use `RandomizedSearchCV` with a wider parameter space.

**How to reason about it:** Randomized search samples a bounded number of candidates, so state the distributions and seed. Log-scaled parameters should be sampled over orders of magnitude rather than uniformly on the raw scale.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — hyperparameter search spaces, fit budgets, and nested evaluation — declare parameter distributions, n_iter, scorer, CV splitter, and seed; print candidate count, expected fit count, best parameters, best CV score, failed-fit count, and one untouched-test metric.

### Exercise 2 — Original lesson practice

**Prompt:** Implement nested cross-validation and compare its result with the non-nested search score.

**How to reason about it:** Nested CV evaluates the complete search procedure. Use distinct inner and outer splitters, and pass the unfitted search object into the outer evaluation so selection repeats independently.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — hyperparameter search spaces, fit budgets, and nested evaluation — print every outer-fold score from a search fitted only inside that fold, its mean/std, and the optimistic non-nested best-CV score; assert outer validation indices never enter their inner search.

### Exercise 3 — Search-budget calculation

**Prompt:** For a grid with 5 values of C, 4 penalties, 3 class weights, and 5-fold CV, calculate candidate and fit counts. Then identify invalid solver/penalty combinations before running.

**Reasoning before implementation:** Cartesian-product candidates multiply; each candidate is fit once per fold, plus a possible final refit.

The naive grid has `5*4*3 = 60` candidates and `60*5 = 300` validation fits,
plus one refit of the selected configuration. Invalid combinations waste time
and can fill results with errors.

Represent compatible spaces as a list of dictionaries—one dictionary per
solver family—or use a constrained sampler. Estimate runtime from a small
pilot before launching the full budget, especially on Windows laptops.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Search-budget calculation — show 5×4×3=60 raw combinations and 60×5=300 fits before filtering; list invalid solver/penalty pairs, print the valid candidate/fit count, and reconcile it with cv_results_ rows.

### Exercise 4 — Multi-metric selection

**Prompt:** Configure GridSearchCV to report ROC AUC, average precision, and balanced accuracy while refitting one declared metric. Explain why the refit choice belongs in the experiment plan.

**Reasoning before implementation:** Pass a scoring dictionary and set `refit` to a metric name. Selection changes when metrics rank candidates differently.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

scoring = {
    "roc_auc": "roc_auc",
    "average_precision": "average_precision",
    "balanced_accuracy": "balanced_accuracy",
}
pipeline = Pipeline(
    [("model", LogisticRegression(max_iter=1_000, random_state=40))]
)
param_grid = {"model__C": [0.1, 1.0, 10.0]}
inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=40)
search = GridSearchCV(
    pipeline,
    param_grid,
    scoring=scoring,
    refit="average_precision",
    cv=inner_cv,
    return_train_score=True,
)
```

The refitted estimator is selected by average precision here. Other metrics
remain diagnostics, not additional opportunities to choose whichever winner
looks best after the run.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Multi-metric selection — configure all three scorers, print their mean/std/rank columns and the declared refit metric, and assert best_estimator_ corresponds to rank 1 for that metric rather than another scorer.

### Exercise 5 — Results-table diagnosis

**Prompt:** Turn `cv_results_` into a tidy table containing parameters, mean and standard deviation of train/validation scores, rank, and fit time. Flag overfit and unstable candidates.

**Reasoning before implementation:** Large train-validation gaps suggest overfit; large fold standard deviation suggests sensitivity. Sort by the declared rank, not by eye.

Use a DataFrame and select only columns relevant to the decision. Compute a
generalization gap as `mean_train_score - mean_test_score`, but interpret it
relative to metric scale and fold spread.

A candidate with a trivial score improvement, double the fit time, and much
higher variability may be a poor operational choice. Preserve the full table
as evidence instead of retaining only `best_params_`.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Results-table diagnosis — emit a tidy table with one row per candidate and explicit parameter, train mean/std, validation mean/std, rank, fit-time mean/std, and failure columns; flag candidates using declared train-validation-gap and variability rules.

### Exercise 6 — Reproducibility debugging

**Prompt:** A randomized search produces different winners on repeated runs. List every random source and parallelism setting to inspect, then design a deterministic comparison.

**Reasoning before implementation:** Seed the sampler, splitters, and estimator. Threaded numeric libraries and GPU algorithms can still introduce small nondeterminism.

Record random states for `RandomizedSearchCV`, shuffled CV, data generation,
and every stochastic estimator. Pin the data snapshot and dependency versions.
For strict debugging, reduce parallelism and compare full score tables with a
tolerance rather than requiring bitwise-identical floats.

Determinism improves diagnosis, but robustness is stronger evidence: repeat a
small set of seeds and prefer conclusions that do not depend on one lucky
partition.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Reproducibility debugging — run the search twice and match candidate order, scores, ranks, and winner after fixing data split, estimator, distribution sampler, CV, and library-thread seeds; record n_jobs and versions.
