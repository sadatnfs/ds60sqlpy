# Day 45 — End-to-End Modeling Mini-Project

**Lesson ID:** `python-45` · **Level:** intermediate · **Dependencies:** `data` · **Network:** first-run Seaborn cache

This checkpoint integrates data loading, leak-safe preprocessing, validation,
evaluation, and a saved pipeline. The objective is reproducible evidence—not the
highest possible score.

## Learning objectives

By the end of the project, you can:

- frame a binary-classification problem and declare an evaluation metric;
- preserve train/test boundaries through a `ColumnTransformer` and `Pipeline`;
- compare a simple baseline with cross-validation and a held-out result;
- save the complete preprocessing-plus-model artifact; and
- document limitations, reproduction steps, and a next experiment.

## Prerequisites

- Complete `python-44` and therefore `python-31` through `python-44`.
- Have a working `data` environment and a writable ignored `artifacts/` folder.
- Cache the Seaborn Titanic dataset while connected before an offline session.

## Dataset and offline contract

The learner notebook calls `seaborn.load_dataset("titanic")`. That first call
may download the small dataset and place it in Seaborn's local cache. This
one-time connected bootstrap is accepted. Once cached, the project can run
offline on that machine.

The separate reference solution uses scikit-learn's package-bundled
breast-cancer dataset to demonstrate the same engineering gates without a
network dependency. It is intentionally a transferable reference, not a
line-for-line Titanic answer.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Baseline | Simple reference that an added-complexity model must justify beating |
| Holdout | Data kept outside fitting and model selection for a final estimate |
| `ColumnTransformer` | Applies different preprocessing to named column groups |
| Reproducibility | Ability to rebuild results from declared code, data, versions, and seeds |
| Artifact | Saved output such as a fitted pipeline, metrics JSON, or plot |
| Acceptance gate | Explicit evidence required before calling a deliverable complete |

## Project gates and evidence

| Gate | Required evidence |
|---|---|
| Problem | Target, prediction unit, intended user, and cost of major error types |
| Data | Columns, missingness, row exclusions, cache requirement, and leakage review |
| Split | Stratified train/holdout split with a fixed seed; holdout untouched during selection |
| Baseline | Named baseline and metric |
| Pipeline | Categories encoded with unknown handling; numeric features processed inside the pipeline |
| Evaluation | Cross-validation scores plus one held-out result and confusion/error analysis |
| Reproducibility | Dependency setup, random states, exact run order, and artifact paths |
| Security/privacy | No secrets or direct identifiers committed; trusted model artifact only |

## Worked pattern: one deployable unit

```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocess = ColumnTransformer(
    [
        ("categorical", OneHotEncoder(handle_unknown="ignore"), ["sex", "class"]),
        ("numeric", StandardScaler(), ["fare", "age"]),
    ]
)
pipeline = make_pipeline(
    preprocess,
    LogisticRegression(max_iter=1_000),
)
```

Fit and serialize this complete pipeline, not separately transformed arrays. A
future input must pass through the exact fitted preprocessing.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 45 learner notebook from this guide's **Next
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

## Concept deep dive — an end-to-end evidence chain from decision to reproducible artifact

### The mental model

An end-to-end project is a sequence of contracts, not one long notebook:
problem framing defines the decision and prediction time; data
validation defines row grain and allowed values; splitting protects the
evaluation boundary; a pipeline binds preprocessing to the model;
metrics and error analysis support a scoped claim; artifact packaging
preserves the exact fitted workflow.

A baseline is a decision checkpoint. Added complexity is justified only
if it improves a declared metric or operational property under the same
data and evaluation design. Reproducibility also requires data identity,
environment, seed, commands, and limitations.

### Worked examples and syntax anatomy

- **`DummyClassifier(strategy=...)`:** creates a minimal predictive reference under the exact same split and metric.
- **`ColumnTransformer` inside `Pipeline`:** binds column-specific preprocessing and prediction into one fitted artifact.
- **manifest + acceptance gates:** connect data hash, schema, code/environment, metrics, limitations, and artifact identity.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — require the candidate to beat a same-split baseline

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=4501
)
baseline = DummyClassifier(strategy="prior").fit(X_train, y_train)
candidate = make_pipeline(
    StandardScaler(), LogisticRegression(max_iter=2_000)
).fit(X_train, y_train)
scores = {
    "baseline": roc_auc_score(y_test, baseline.predict_proba(X_test)[:, 1]),
    "candidate": roc_auc_score(y_test, candidate.predict_proba(X_test)[:, 1]),
}
print(scores)
assert scores["candidate"] > scores["baseline"]
```

**Expected observation:** The model must improve the declared held-out metric over the simple prior baseline on identical rows.

**Assumption to name:** ROC AUC and this split reflect the decision; the test result was not repeatedly consulted during development.

### Focused example B — turn completion into explicit acceptance gates

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
evidence = {
    "data_contract_passed": True,
    "tests_passed": True,
    "baseline_auc": 0.50,
    "candidate_auc": 0.97,
    "minimum_improvement": 0.05,
    "artifact_reloaded": True,
    "limitations_documented": True,
}
gates = {
    "quality": evidence["data_contract_passed"] and evidence["tests_passed"],
    "performance": (
        evidence["candidate_auc"] - evidence["baseline_auc"]
        >= evidence["minimum_improvement"]
    ),
    "delivery": evidence["artifact_reloaded"] and evidence["limitations_documented"],
}
print(gates)
assert all(gates.values())
```

**Expected observation:** A project is ready only when every named quality, performance, and delivery gate passes.

**Assumption to name:** Thresholds and evidence requirements were set before viewing the final candidate result.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define an end-to-end evidence chain from decision to reproducible artifact in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Treating a high notebook score as the project outcome while omitting baseline, leakage audit, artifact reload, and limitations.

**Debug it deliberately:** Trace every claim backward to metric rows, split, feature pipeline, data version, environment, and command; rerun in a fresh kernel/process.

**Stop condition:** Do not promote a project when a gate is unknown, final evaluation influenced iteration, or the intended decision and harm boundaries are vague.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

The notebook's project checklist is the exercise:

1. Load the dataset and create train/validation/test boundaries.

**Verify:** Practice 1 — an end-to-end evidence chain from decision to reproducible artifact — record dataset identity/hash, target, row count, and frozen train/validation/test indices; assert the three index sets are pairwise disjoint and their counts sum to the validated rows.

2. Preprocess with `ColumnTransformer`.

**Verify:** Practice 2 — an end-to-end evidence chain from decision to reproducible artifact — fit one ColumnTransformer inside the training pipeline, print output feature names/order and transformed shapes, and predict a validation row containing the declared missing/unknown-category boundary.

3. Train a baseline model.

**Verify:** Practice 3 — an end-to-end evidence chain from decision to reproducible artifact — fit a declared naive/simple baseline on training rows, print validation metric and denominator/support, and save its parameters and seed before trying a more complex candidate.

4. Evaluate with appropriate metrics and cross-validation.

**Verify:** Practice 4 — an end-to-end evidence chain from decision to reproducible artifact — print every cross-validation score plus mean/std on training data and one frozen validation comparison; reserve the test set for one final evaluation and report the metric formula and support.

5. Save the model and preprocessing together with `joblib`.

**Verify:** Practice 5 — an end-to-end evidence chain from decision to reproducible artifact — save one joblib pipeline containing preprocessing and model, compute its SHA-256, reload it in a fresh process, and assert predictions and feature metadata match the pre-save values.

6. Write a short README-style section in the notebook covering rationale,
   metrics, limitations, and next steps.

**Verify:** Practice 6 — an end-to-end evidence chain from decision to reproducible artifact — include runnable setup/train/test commands, data provenance/hash, baseline/candidate metrics, limitations, and next step; have a clean-shell replay finish with exit code 0.

7. Optionally adapt the Day 44 FastAPI service.

**Verify:** Practice 7 — an end-to-end evidence chain from decision to reproducible artifact — if the API extension is attempted, run Day 44 health/valid/invalid TestClient cases against the reloaded artifact; otherwise record an explicit skipped result and keep the capstone complete.

### Progressive hints

1. Start by writing the target, row unit, and split before feature engineering.
2. Use `handle_unknown="ignore"` for categorical inference and keep every fitted
   transformation inside the pipeline.
3. Report the distribution of fold scores; do not tune against the holdout.
4. Reload the saved artifact in a fresh cell and predict a small valid batch.

### Additional mastery practice

Finish one reproducible modeling system rather than a notebook demo. Every data boundary, fitted transform, metric, artifact, and handoff claim needs evidence.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

8. **Data-contract gate:** Write executable checks for row identity, required columns, target domain, missingness limits, duplicate policy, and data snapshot fingerprint.
   **Progressive hint:** Validate raw data before splitting. Separate hard failures from reported warnings and hash stable source bytes or a canonical snapshot manifest.

**Verify:** Data-contract gate — run the contract against one valid fixture and separate duplicate-ID, missing-column, invalid-target, excessive-missingness, and changed-snapshot fixtures; assert each failure names its rule and print the accepted snapshot hash.

9. **Leakage audit:** Create a feature-by-feature table with availability time, source, transformation fit scope, and leakage decision. Investigate at least one suspicious post-outcome field.
   **Progressive hint:** Ask whether the value exists at prediction time and whether it was computed using future rows or target information.

**Verify:** Leakage audit — save a feature lineage table with feature, source, availability timestamp, fit scope, target dependence, and decision; remove/quarantine the post-outcome fixture and show the corrected split/metric.

10. **Baseline ladder:** Evaluate a dummy strategy, a simple linear/tree model, and one selected candidate on identical folds. Define a minimum practical improvement before seeing results.
   **Progressive hint:** Use paired fold scores and include runtime/complexity. A statistically detectable gain may still be operationally irrelevant.

**Verify:** Baseline ladder — print fold-level and mean/std metrics for DummyClassifier, the declared simple model, and one candidate on identical folds; record a predeclared practical-improvement threshold and whether it is met.

11. **Operating-policy selection:** Build a threshold table with false-positive cost, false-negative cost, precision, recall, and queue volume. Select a threshold on validation data, then freeze it.
   **Progressive hint:** Translate confusion-matrix counts into the same business unit and include capacity constraints such as maximum daily reviews.

**Verify:** Operating-policy selection — print one row per threshold with TP/FP/FN/TN, precision, recall, queue volume, and total expected cost; select on validation only, serialize the frozen threshold, and apply it once to test scores.

12. **Error-slice analysis:** Define at least three pre-motivated slices, report support and error metrics, and inspect representative false positives and false negatives without exposing sensitive raw values.
   **Progressive hint:** Choose slices from domain risk, not by mining the test set for the worst-looking subgroup. Small support requires uncertainty and caution.

**Verify:** Error-slice analysis — for at least three predeclared slices, print support, metric, and uncertainty plus sanitized false-positive/false-negative examples; flag slices below minimum support rather than ranking them.

13. **Artifact manifest:** Save the fitted pipeline with a JSON manifest containing model ID, training-data fingerprint, schema, metric definitions/results, threshold, dependency versions, and file hashes.
   **Progressive hint:** JSON holds metadata; joblib holds the trusted fitted object. Write both to a versioned artifacts directory and verify them on load.

**Verify:** Artifact manifest — validate the JSON manifest schema and every listed SHA-256/size, then tamper one artifact and assert loading/promotion stops before prediction.

14. **Fresh-process acceptance:** Create a smoke test that starts from a clean process, loads the saved artifact, scores a fixed fixture, and compares the result with the pre-save prediction within a numeric tolerance.
   **Progressive hint:** Do not rely on notebook variables. The test needs only documented files, installed dependencies, and repository-relative paths.

**Verify:** Fresh-process acceptance — run a subprocess from a clean working directory that loads the artifact and scores the fixed fixture; require exit code 0 and prediction parity within the declared numeric tolerance.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Can a new category pass through the fitted pipeline?
- Can another learner reproduce the split and metric from the notebook alone?
- Did any preprocessing or threshold choice inspect holdout labels?
- Does the saved artifact include both preprocessing and prediction?
- What failure mode would prevent you from recommending deployment?

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Evidence of the problem | Response |
|---|---|---|
| Dropping missing rows without discussion | Cohort changes silently | Quantify removals and possible bias |
| Calling accuracy “the metric” | Error costs remain unstated | Add ROC AUC and thresholded metrics with rationale |
| Comparing many models on the holdout | Score steadily improves through reuse | Return selection to CV; reserve a fresh final set if possible |
| Saving to an arbitrary working directory | Artifact cannot be found/reproduced | Use a documented ignored `artifacts/` path |
| Loading an untrusted model file | Code-execution risk | Load only artifacts produced by this trusted workflow |

This project demonstrates a responsible baseline. It does not establish
production readiness, causal validity, fairness, or stability under future data.

## Next step

- Build in the [Day 45 learner notebook](../notebooks/day45_end_to_end_modeling_project.ipynb).
- Use the differently-dataseted
  [Day 45 reference solution](../solutions/day45_end_to_end_modeling_project/day45_solutions.md)
  only after producing your own evidence.
- Continue to [Day 46 — Deep Learning Overview](day46_deep_learning_overview.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-45` — Day 45 — End-to-End Modeling Mini-Project.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize an end-to-end evidence chain from decision to reproducible artifact. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day45_end_to_end_modeling_project.md`
- learner artifact: `python/ds-60day/notebooks/day45_end_to_end_modeling_project.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-44`. Do not assume knowledge beyond them or skip the
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
