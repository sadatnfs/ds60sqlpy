# Day 53 — Solutions: MLOps with MLflow Experiment Tracking

We track a scikit‑learn grid search with MLflow, log the best model as an artifact, and load it for reuse.

Contents
- Exercise 1: Track a grid search and compare runs
- Exercise 2: Log best model and load it elsewhere
- Exercise 3: Explore Model Registry concepts (notes)

---

Setup
```python
import mlflow, mlflow.sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

mlflow.set_experiment('rf-breast-cancer')
```

Exercise 1 — Grid search with autologging
```python
mlflow.sklearn.autolog()

param_grid = {'n_estimators':[100,300], 'max_depth':[None,5,10]}
rf = RandomForestClassifier(random_state=0)
cv = GridSearchCV(rf, param_grid=param_grid, scoring='roc_auc', cv=3, n_jobs=-1, return_train_score=True)

with mlflow.start_run(run_name='rf_grid'):
    cv.fit(Xtr, ytr)
    best_auc = cv.best_score_
    mlflow.log_metric('cv_auc_mean', best_auc)
    print('Best CV AUC:', best_auc)

print('Best params:', cv.best_params_)
```
Explanation
- autolog captures params, metrics, and model artifacts automatically
- Start a run context so logs are grouped

---

Exercise 2 — Log and load best model
```python
with mlflow.start_run(run_name='rf_best_model') as run:
    best = RandomForestClassifier(random_state=0, **cv.best_params_).fit(Xtr, ytr)
    proba = best.predict_proba(Xte)[:,1]
    test_auc = roc_auc_score(yte, proba)
    mlflow.log_metric('test_auc', test_auc)
    mlflow.sklearn.log_model(best, 'model')
    run_id = run.info.run_id

print('Logged under run:', run_id)

# Load model later
loaded = mlflow.sklearn.load_model(f'runs:/{run_id}/model')
print('Loaded AUC:', roc_auc_score(yte, loaded.predict_proba(Xte)[:,1]))
```
Notes
- Track the run_id to retrieve artifacts
- Use mlflow ui to compare runs: `mlflow ui --port 5000`

---

Exercise 3 — Model Registry (concepts)
- Register models for stages: Staging → Production
- Transition approvals and CI checks gate promotions
- Versioned artifacts allow rollbacks and auditability

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Log additional parameters such as Logistic Regression `C` and compare runs.

**How to reason about it:** Log one controlled configuration per run, including split seed, model type, metric definition, and direct hyperparameters. Use tags for context rather than encoding all meaning in a run name.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Save a confusion-matrix PNG and log it as an artifact.

**How to reason about it:** Create the confusion matrix under ignored `artifacts/`, label axes, close the figure, and log it. The artifact must correspond to the same evaluation rows and threshold as the run's numeric metrics.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Try a different classifier, such as Random Forest, and compare ROC AUC.

**How to reason about it:** Compare classifiers on one frozen split and include runtime/complexity beside ROC AUC. A model-family change is a new run, not an overwritten metric in the prior run.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Failure-state handling

**Prompt:** Run an experiment that intentionally raises after logging parameters. Verify MLflow records a failed status and useful exception context without exposing raw data or secrets.

**Reasoning before implementation:** Use the run context manager so exception exit marks the run failed. Log safe stage/status information before re-raising.

Do not catch every exception and end the run as successful. If cleanup is
needed, catch narrowly, log a redacted diagnostic or tag, and re-raise so the
tracking status remains honest.

Never put credentials, full environment variables, or sensitive records in
tags/artifacts. Link to an approved local diagnostic ID when deeper incident
evidence is restricted.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Provenance manifest

**Prompt:** Log a JSON provenance artifact containing data fingerprint, code revision, dependency lock hash, feature schema, split policy, and metric definitions.

**Reasoning before implementation:** Use portable identifiers and hashes, not developer-specific absolute paths. Validate required fields before ending the run.

The manifest should make two similar-looking runs distinguishable. Include
target/positive-label semantics and units/denominators for metrics. Record a
dirty-worktree flag when applicable rather than falsely claiming the Git
revision alone captures code state.

A hash proves identity relative to the hashed bytes, not trust or data quality.
Keep the source snapshot governed and reproducible.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Reload and signature check

**Prompt:** Log a fitted pipeline with an input example/signature, reload it by run URI, and assert prediction parity on a fixed fixture.

**Reasoning before implementation:** The fixture must use the documented schema and never come from hidden notebook state. Compare probabilities within a tolerance.

Test missing/extra columns and dtypes as well as a valid prediction. The
signature catches many integration errors but does not replace domain
validation such as allowed ranges or category policy.

Use the local file-backed tracking URI for the offline lesson. A production
registry adds authentication and promotion policy, which should be documented
as an extension rather than required for the portable course.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
