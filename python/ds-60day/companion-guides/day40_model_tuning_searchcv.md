# Day 40 — Hyperparameter Tuning with SearchCV

**Lesson ID:** `python-40` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Hyperparameter search automates a controlled set of model comparisons. It does
not eliminate the need to define a defensible search space, metric, resampling
strategy, or final evaluation boundary.

## Learning objectives

By the end of the lesson, you can:

- address nested pipeline parameters with `step__parameter` names;
- run `GridSearchCV` and `RandomizedSearchCV`;
- use distributions that match parameter scale;
- interpret `best_score_` as an inner validation result; and
- use nested cross-validation for a less biased estimate of a tuning procedure.

## Prerequisites

- Complete `python-39` (gradient boosting).
- Be comfortable with pipelines and stratified CV from `python-34`–`python-35`.
- Understand the distinction between hyperparameters and fitted parameters.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Search space | Declared candidate values or distributions |
| Grid search | Exhaustive Cartesian product of listed candidates |
| Randomized search | Fixed number of samples from parameter distributions |
| Refit | Training the selected configuration on all data supplied to the search |
| Inner CV | Resampling used to select hyperparameters |
| Outer CV | Resampling used to estimate the entire selection procedure |
| Nested CV | Inner search repeated independently inside each outer training fold |

If you evaluate thousands of choices and report the same CV's maximum, selection
noise makes the result optimistic. Nested CV separates selection from estimation.

## Worked example: parameter names follow pipeline structure

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipeline = make_pipeline(StandardScaler(), SVC())
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(
    pipeline,
    param_grid={
        "svc__C": [0.1, 1.0, 10.0],
        "svc__kernel": ["linear", "rbf"],
    },
    cv=folds,
    scoring="roc_auc",
    n_jobs=2,
    refit=True,
)
search.fit(X, y)
print(search.best_params_, search.best_score_)
```

`best_score_` estimates performance inside the search. It is not a score from an
untouched final test set.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 40 learner notebook from this guide's **Next
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

## Concept deep dive — hyperparameter search spaces, fit budgets, and nested evaluation

### The mental model

Hyperparameters configure how an estimator learns; a search procedure
chooses among candidate configurations using validation data. A grid is
a Cartesian product of listed values. Randomized search samples a fixed
number of configurations from distributions, which is often more
efficient when only a few dimensions matter.

Search results are themselves fitted to data. `best_score_` estimates
the best candidate on the inner validation folds and is optimistically
selected from many alternatives. A separate holdout or outer
cross-validation loop evaluates the entire selection procedure.

### Worked examples and syntax anatomy

- **`step__parameter`:** addresses nested pipeline parameters; inspect `get_params()` instead of guessing names.
- **`ParameterGrid(space)`:** enumerates the exact Cartesian search and makes the fit budget calculable.
- **`GridSearchCV(..., scoring=..., refit=...)`:** scores candidates in inner folds and refits the selected configuration on all supplied rows.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — calculate the search budget before fitting

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
from sklearn.model_selection import ParameterGrid

space = {
    "model__C": [0.01, 0.1, 1.0, 10.0],
    "model__class_weight": [None, "balanced"],
    "model__solver": ["liblinear", "lbfgs"],
}
candidates = list(ParameterGrid(space))
folds = 5
expected_fits = len(candidates) * folds + 1  # final refit
print({"candidates": len(candidates), "expected_fits": expected_fits})
assert len(candidates) == 16
```

**Expected observation:** Three modest lists already create 16 candidates and 81 model fits with five folds and refit.

**Assumption to name:** Every listed combination is valid for the estimator and receives the same fold assignments.

### Focused example B — make the refit metric explicit in multi-metric search

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(max_iter=2_000)),
])
search = GridSearchCV(
    pipe,
    {"model__C": [0.1, 1.0, 10.0]},
    scoring={"accuracy": "accuracy", "f1_macro": "f1_macro"},
    refit="f1_macro",
    cv=StratifiedKFold(3, shuffle=True, random_state=4002),
).fit(X, y)
print(search.best_params_, search.best_score_)
assert search.refit == "f1_macro"
```

**Expected observation:** The selected estimator and `best_score_` are tied to `f1_macro`, not an implicit first metric.

**Assumption to name:** Macro F1 matches the decision and class-weighting priorities for this task.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define hyperparameter search spaces, fit budgets, and nested evaluation in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Reporting `best_score_` as unbiased test performance after trying many candidates.

**Debug it deliberately:** Inspect `cv_results_`, candidate count, rank stability, train/validation gaps, failed fits, and whether search preprocessing lives inside the pipeline.

**Stop condition:** Do not expand a search space without a fit budget, parameter rationale, and untouched evaluation plan.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Use `RandomizedSearchCV` with a wider parameter space.

**Verify:** Practice 1 — hyperparameter search spaces, fit budgets, and nested evaluation — declare parameter distributions, n_iter, scorer, CV splitter, and seed; print candidate count, expected fit count, best parameters, best CV score, failed-fit count, and one untouched-test metric.

2. Implement nested cross-validation and compare its result with the non-nested
   search score.

**Verify:** Practice 2 — hyperparameter search spaces, fit budgets, and nested evaluation — print every outer-fold score from a search fitted only inside that fold, its mean/std, and the optimistic non-nested best-CV score; assert outer validation indices never enter their inner search.

### Progressive hints

1. Sample `C` over orders of magnitude (for example with SciPy's `loguniform`)
   and set `random_state`. Start with about 20 iterations on a laptop.
2. Build separate inner and outer `StratifiedKFold` objects. Pass the entire
   search object—not its already-selected best estimator—to
   `cross_val_score` with the outer splitter.

### Additional mastery practice

Treat tuning as a finite experimental budget with a declared search space, selection metric, resampling design, and reproducible result table.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Search-budget calculation:** For a grid with 5 values of C, 4 penalties, 3 class weights, and 5-fold CV, calculate candidate and fit counts. Then identify invalid solver/penalty combinations before running.
   **Progressive hint:** Cartesian-product candidates multiply; each candidate is fit once per fold, plus a possible final refit.

**Verify:** Search-budget calculation — show 5×4×3=60 raw combinations and 60×5=300 fits before filtering; list invalid solver/penalty pairs, print the valid candidate/fit count, and reconcile it with cv_results_ rows.

4. **Multi-metric selection:** Configure GridSearchCV to report ROC AUC, average precision, and balanced accuracy while refitting one declared metric. Explain why the refit choice belongs in the experiment plan.
   **Progressive hint:** Pass a scoring dictionary and set `refit` to a metric name. Selection changes when metrics rank candidates differently.

**Verify:** Multi-metric selection — configure all three scorers, print their mean/std/rank columns and the declared refit metric, and assert best_estimator_ corresponds to rank 1 for that metric rather than another scorer.

5. **Results-table diagnosis:** Turn `cv_results_` into a tidy table containing parameters, mean and standard deviation of train/validation scores, rank, and fit time. Flag overfit and unstable candidates.
   **Progressive hint:** Large train-validation gaps suggest overfit; large fold standard deviation suggests sensitivity. Sort by the declared rank, not by eye.

**Verify:** Results-table diagnosis — emit a tidy table with one row per candidate and explicit parameter, train mean/std, validation mean/std, rank, fit-time mean/std, and failure columns; flag candidates using declared train-validation-gap and variability rules.

6. **Reproducibility debugging:** A randomized search produces different winners on repeated runs. List every random source and parallelism setting to inspect, then design a deterministic comparison.
   **Progressive hint:** Seed the sampler, splitters, and estimator. Threaded numeric libraries and GPU algorithms can still introduce small nondeterminism.

**Verify:** Reproducibility debugging — run the search twice and match candidate order, scores, ranks, and winner after fixing data split, estimator, distribution sampler, CV, and library-thread seeds; record n_jobs and versions.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why does a logarithmic distribution make sense for `C`?
- What exactly is retrained when `refit=True`?
- Why should the outer test fold never influence the inner winner?
- When is randomized search more efficient than a full grid?

Expected behavior: nested CV performs many fits and may be slower. Its mean score
can be lower than `best_score_`; that is an expected consequence of a stricter
evaluation boundary, not a failure.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Preprocessing outside the searched pipeline | Fold leakage | Search a complete pipeline |
| Huge grid on a laptop | Combinatorial runtime | Start bounded; use randomized search |
| Default CV ignores groups or time | Invalid independence assumptions | Select a domain-appropriate splitter |
| Repeatedly expanding space after test results | Test-set overfitting | Freeze the search before final evaluation |
| Reporting only winner | Hides instability and cost | Inspect `cv_results_`, spread, and runtime |

Nested CV is computationally expensive: outer folds multiply every inner search
fit. Use it when the risk of tuning optimism warrants that cost, and use a final
held-out set when the project requires a locked evaluation.

## Next step

- Work in the [Day 40 learner notebook](../notebooks/day40_model_tuning_searchcv.ipynb).
- Then consult the
  [Day 40 solution](../solutions/day40_model_tuning_searchcv/day40_solutions.md).
- Continue to [Day 41 — Class Imbalance](day41_imbalance_handling.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-40` — Day 40 — Hyperparameter Tuning with SearchCV.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize hyperparameter search spaces, fit budgets, and nested evaluation. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day40_model_tuning_searchcv.md`
- learner artifact: `python/ds-60day/notebooks/day40_model_tuning_searchcv.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-39`. Do not assume knowledge beyond them or skip the
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
