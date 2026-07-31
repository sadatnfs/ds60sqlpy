# Day 45 — Solutions: End-to-End Modeling Project

We deliver a reproducible baseline solution: clean data pipeline with validation and features, model training with CV/tuning, holdout evaluation with thresholding, saved artifacts, and a minimal FastAPI service.

Contents
- Exercise 1: Define target/metric and acceptance criteria; build a Pipeline
- Exercise 2: Cross-validate and tune; evaluate on a holdout and pick threshold
- Exercise 3: Save model + artifacts; serve via FastAPI; write README instructions

---

Worked reference for Exercise 1 — Problem framing and Pipeline
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Target/metric: binary classification; metric = ROC AUC, plus thresholded F1
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xho, ytr, yho = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

pipe = Pipeline([
    ('sc', StandardScaler()),
    ('lr', LogisticRegression(max_iter=2000, solver='lbfgs'))
])
```
Notes
- Preprocessing belongs inside the Pipeline to avoid leakage
- Reproducibility: pin random_state and library versions

---

Worked reference for Exercise 2 — CV/tuning and holdout evaluation
```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, precision_recall_curve, average_precision_score
import numpy as np

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
param_grid = {'lr__C': [0.1, 1.0, 10.0]}
search = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=1, refit=True)
search.fit(Xtr, ytr)

# Holdout metrics
proba = search.predict_proba(Xho)[:, 1]
roc = roc_auc_score(yho, proba)
ap = average_precision_score(yho, proba)

# Threshold via PR for F1 (example)
prec, rec, th = precision_recall_curve(yho, proba)
th = np.r_[0.0, th]
f1s = 2 * prec * rec / (prec + rec + 1e-12)
best_i = np.nanargmax(f1s)
th_star, f1_star = float(th[best_i]), float(f1s[best_i])
{'cv_best_params': search.best_params_, 'holdout_roc_auc': float(roc), 'holdout_ap': float(ap), 'best_threshold': th_star, 'best_f1': f1_star}
```
Interpretation
- Report CV best params and holdout AUC/AP
- Pick an operating threshold based on PR/F1 or business constraints (precision/recall tradeoff)

---

Worked reference for Exercise 3 — Save artifacts and serve via FastAPI
```python
import json
from pathlib import Path

import joblib

# Save fitted search (contains the best estimator)
artifact_dir = Path('artifacts/day45')
artifact_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(search, artifact_dir / 'model_search.joblib')
# Bundle threshold and metadata
meta = {'threshold': th_star, 'params': search.best_params_, 'metric': {'roc_auc': float(roc), 'ap': float(ap)}}
with (artifact_dir / 'model_meta.json').open('w', encoding='utf-8') as stream:
    json.dump(meta, stream)

# Minimal FastAPI app (artifacts/day45/app.py)
app_source = '''\
from pathlib import Path
import json
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ARTIFACT_DIR = Path(__file__).resolve().parent
app = FastAPI()
search = joblib.load(ARTIFACT_DIR / "model_search.joblib")
with (ARTIFACT_DIR / "model_meta.json").open(encoding="utf-8") as stream:
    meta = json.load(stream)

class Features(BaseModel):
    x: list[float]

@app.post("/predict")
def predict(req: Features):
    try:
        X = np.array([req.x], dtype=float)
        proba = float(search.predict_proba(X)[:, 1][0])
        label = int(proba >= meta["threshold"])
        return {"proba": proba, "label": label, "threshold": meta["threshold"]}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
'''
(artifact_dir / 'app.py').write_text(app_source, encoding='utf-8')
```
Test locally
```bash
python -m uvicorn app:app --app-dir artifacts/day45 --reload
curl -s -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{"x": [X_FEATURES_HERE]}'
```
Checklist for README.md
- Environment setup and dependencies (versions)
- Training command(s) and hyperparameters
- CV/holdout metrics and chosen threshold rationale
- How to serve the model (FastAPI) and sample requests
- Future work: monitoring, CI, Dockerfile, infra

---

**Portable worker default:** These reference runs use `n_jobs=1` so they behave predictably on Windows, CI runners, and constrained notebook environments. After correctness is established, benchmark a larger worker count on your own workload rather than assuming `n_jobs=1` is faster.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`DummyClassifier(strategy=...)`:** creates a minimal predictive reference under the exact same split and metric.
2. **`ColumnTransformer` inside `Pipeline`:** binds column-specific preprocessing and prediction into one fitted artifact.
3. **manifest + acceptance gates:** connect data hash, schema, code/environment, metrics, limitations, and artifact identity.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Separating contracts and gates makes each project stage testable and connects model performance to a reproducible decision claim.

**Useful alternative:** A simpler rule-based or statistical model may meet the decision need with lower maintenance and explanation cost.

**Trade-off:** A richer model can improve metrics while increasing data, compute, monitoring, privacy, and operational obligations.

**Edge case to test:** Missing categories, changed schema, data drift, tiny slices, artifact incompatibility, and unavailable first-run Seaborn cache need explicit behavior.

**Evidence of correctness:** Reproduce from a fresh environment, validate data and split hashes, beat a same-split baseline, reload the complete pipeline, test slices, and connect every claim to an artifact.

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

**Prompt:** Load the dataset and create train/validation/test boundaries.

**How to reason about it:** Write the row unit, target, prediction time, and train/validation/test boundary before loading features. A stratified random split is valid only when entities and time do not require stronger separation.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — an end-to-end evidence chain from decision to reproducible artifact — record dataset identity/hash, target, row count, and frozen train/validation/test indices; assert the three index sets are pairwise disjoint and their counts sum to the validated rows.

### Exercise 2 — Original lesson practice

**Prompt:** Preprocess with `ColumnTransformer`.

**How to reason about it:** Use ColumnTransformer to keep all learned preprocessing inside the pipeline. Test missing, unseen-category, dtype, and column-order behavior with tiny synthetic rows.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — an end-to-end evidence chain from decision to reproducible artifact — fit one ColumnTransformer inside the training pipeline, print output feature names/order and transformed shapes, and predict a validation row containing the declared missing/unknown-category boundary.

### Exercise 3 — Original lesson practice

**Prompt:** Train a baseline model.

**How to reason about it:** A baseline establishes the minimum useful comparison and catches broken evaluation. Include a dummy predictor and one simple model before tuning.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — an end-to-end evidence chain from decision to reproducible artifact — fit a declared naive/simple baseline on training rows, print validation metric and denominator/support, and save its parameters and seed before trying a more complex candidate.

### Exercise 4 — Original lesson practice

**Prompt:** Evaluate with appropriate metrics and cross-validation.

**How to reason about it:** Cross-validation belongs only to development data. Report fold spread, choose metrics before results, and reserve the holdout for one frozen candidate and threshold.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 4 — an end-to-end evidence chain from decision to reproducible artifact — print every cross-validation score plus mean/std on training data and one frozen validation comparison; reserve the test set for one final evaluation and report the metric formula and support.

### Exercise 5 — Original lesson practice

**Prompt:** Save the model and preprocessing together with `joblib`.

**How to reason about it:** Serialize preprocessing and model together, under an ignored artifacts path. Record dependency/model/schema versions and validate reload parity in a fresh process.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 5 — an end-to-end evidence chain from decision to reproducible artifact — save one joblib pipeline containing preprocessing and model, compute its SHA-256, reload it in a fresh process, and assert predictions and feature metadata match the pre-save values.

### Exercise 6 — Original lesson practice

**Prompt:** Write a short README-style section in the notebook covering rationale, metrics, limitations, and next steps.

**How to reason about it:** The README-style handoff must state exact commands, data origin, metric definitions, limitations, and output locations. A narrative without reproduction evidence is incomplete.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 6 — an end-to-end evidence chain from decision to reproducible artifact — include runnable setup/train/test commands, data provenance/hash, baseline/candidate metrics, limitations, and next step; have a clean-shell replay finish with exit code 0.

### Exercise 7 — Original lesson practice

**Prompt:** Optionally adapt the Day 44 FastAPI service.

**How to reason about it:** Serving is optional and should reuse the saved pipeline and schema rather than rebuilding preprocessing. Test the API boundary before adding network or container complexity.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 7 — an end-to-end evidence chain from decision to reproducible artifact — if the API extension is attempted, run Day 44 health/valid/invalid TestClient cases against the reloaded artifact; otherwise record an explicit skipped result and keep the capstone complete.

### Exercise 8 — Data-contract gate

**Prompt:** Write executable checks for row identity, required columns, target domain, missingness limits, duplicate policy, and data snapshot fingerprint.

**Reasoning before implementation:** Validate raw data before splitting. Separate hard failures from reported warnings and hash stable source bytes or a canonical snapshot manifest.

The checks should fail with actionable field names and counts. Preserve the raw
input, then create a validated copy for modeling. A row fingerprint must be
stable across operating systems; canonicalize column order and serialization
or hash the original immutable file.

Record what was excluded and why. Quietly dropping invalid rows changes the
training population and can make later metrics impossible to reproduce.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Data-contract gate — run the contract against one valid fixture and separate duplicate-ID, missing-column, invalid-target, excessive-missingness, and changed-snapshot fixtures; assert each failure names its rule and print the accepted snapshot hash.

### Exercise 9 — Leakage audit

**Prompt:** Create a feature-by-feature table with availability time, source, transformation fit scope, and leakage decision. Investigate at least one suspicious post-outcome field.

**Reasoning before implementation:** Ask whether the value exists at prediction time and whether it was computed using future rows or target information.

Remove or quarantine post-outcome fields before model comparison, then show
how metrics change. A dramatic decrease is evidence the earlier result was not
deployable, not evidence that the corrected pipeline became worse.

Version the audit beside the model. Feature names alone are insufficient:
rolling aggregates and target encoders can leak through their time window or
fit scope even when the raw field is available.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Leakage audit — save a feature lineage table with feature, source, availability timestamp, fit scope, target dependence, and decision; remove/quarantine the post-outcome fixture and show the corrected split/metric.

### Exercise 10 — Baseline ladder

**Prompt:** Evaluate a dummy strategy, a simple linear/tree model, and one selected candidate on identical folds. Define a minimum practical improvement before seeing results.

**Reasoning before implementation:** Use paired fold scores and include runtime/complexity. A statistically detectable gain may still be operationally irrelevant.

Keep preprocessing comparable and report mean, spread, and per-fold deltas.
The dummy baseline validates class prevalence and metric direction. The simple
baseline tests whether added complexity earns its maintenance cost.

If the selected candidate misses the predeclared improvement, document that
finding rather than optimizing the acceptance criterion after the fact.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Baseline ladder — print fold-level and mean/std metrics for DummyClassifier, the declared simple model, and one candidate on identical folds; record a predeclared practical-improvement threshold and whether it is met.

### Exercise 11 — Operating-policy selection

**Prompt:** Build a threshold table with false-positive cost, false-negative cost, precision, recall, and queue volume. Select a threshold on validation data, then freeze it.

**Reasoning before implementation:** Translate confusion-matrix counts into the same business unit and include capacity constraints such as maximum daily reviews.

The best threshold is conditional on prevalence, costs, and capacity. Save it
as model metadata rather than hard-coding `0.5` in serving code. On the final
holdout, report performance at the frozen threshold without reopening the
selection.

Include sensitivity scenarios because costs and prevalence are estimates.
Ranking metrics alone cannot define the operating point.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Operating-policy selection — print one row per threshold with TP/FP/FN/TN, precision, recall, queue volume, and total expected cost; select on validation only, serialize the frozen threshold, and apply it once to test scores.

### Exercise 12 — Error-slice analysis

**Prompt:** Define at least three pre-motivated slices, report support and error metrics, and inspect representative false positives and false negatives without exposing sensitive raw values.

**Reasoning before implementation:** Choose slices from domain risk, not by mining the test set for the worst-looking subgroup. Small support requires uncertainty and caution.

Use stable row IDs and redacted fields for case review. Report denominators,
confidence intervals or bootstrap ranges, and missing-label coverage. A slice
with two examples cannot sustain a broad fairness claim.

New features or threshold changes prompted by test errors return the project to
development and require a new untouched evaluation set.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Error-slice analysis — for at least three predeclared slices, print support, metric, and uncertainty plus sanitized false-positive/false-negative examples; flag slices below minimum support rather than ranking them.

### Exercise 13 — Artifact manifest

**Prompt:** Save the fitted pipeline with a JSON manifest containing model ID, training-data fingerprint, schema, metric definitions/results, threshold, dependency versions, and file hashes.

**Reasoning before implementation:** JSON holds metadata; joblib holds the trusted fitted object. Write both to a versioned artifacts directory and verify them on load.

Use atomic writes where practical and fail if an existing version would be
overwritten. Compute the artifact hash after serialization, then validate it
before loading. Keep secrets and absolute developer paths out of metadata.

The manifest makes the artifact reviewable but does not make pickle safe from
untrusted sources. Provenance and access control remain required.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Artifact manifest — validate the JSON manifest schema and every listed SHA-256/size, then tamper one artifact and assert loading/promotion stops before prediction.

### Exercise 14 — Fresh-process acceptance

**Prompt:** Create a smoke test that starts from a clean process, loads the saved artifact, scores a fixed fixture, and compares the result with the pre-save prediction within a numeric tolerance.

**Reasoning before implementation:** Do not rely on notebook variables. The test needs only documented files, installed dependencies, and repository-relative paths.

Run the smoke test from the repository root on both the documented Windows and
POSIX commands. Assert response shape, finite probabilities, class mapping,
threshold behavior, and model/schema version.

Reload parity catches missing custom classes, accidental preprocessing outside
the pipeline, path assumptions, and serialization drift. Delete and rebuild
the ignored test artifact to prove the workflow—not a stale file—creates it.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Fresh-process acceptance — run a subprocess from a clean working directory that loads the artifact and scores the fixed fixture; require exit code 0 and prediction parity within the declared numeric tolerance.
