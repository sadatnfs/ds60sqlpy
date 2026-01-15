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
