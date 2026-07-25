# Day 45 — Solutions: End-to-End Modeling Project

We deliver a reproducible baseline solution: clean data pipeline with validation and features, model training with CV/tuning, holdout evaluation with thresholding, saved artifacts, and a minimal FastAPI service.

Contents
- Exercise 1: Define target/metric and acceptance criteria; build a Pipeline
- Exercise 2: Cross-validate and tune; evaluate on a holdout and pick threshold
- Exercise 3: Save model + artifacts; serve via FastAPI; write README instructions

---

Exercise 1 — Problem framing and Pipeline
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

Exercise 2 — CV/tuning and holdout evaluation
```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, precision_recall_curve, average_precision_score
import numpy as np

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
param_grid = {'lr__C': [0.1, 1.0, 10.0]}
search = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1, refit=True)
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

Exercise 3 — Save artifacts and serve via FastAPI
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
