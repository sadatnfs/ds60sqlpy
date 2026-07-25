# Day 44 — Solutions: Model Deployment Basics with FastAPI

We train and save a model (joblib), build a minimal FastAPI endpoint to serve predictions, and test it with curl. We then add small improvements: input validation and class name mapping.

Contents
- Exercise 1: Train and save a model with joblib; verify load
- Exercise 2: Minimal FastAPI endpoint `/predict`
- Exercise 3: Validate inputs and return class names; test with curl

---

Exercise 1 — Train and save model
```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path

X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
clf = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print({'test_acc': clf.score(Xte, yte)})
artifact_dir = Path('artifacts/day44')
artifact_dir.mkdir(parents=True, exist_ok=True)
model_path = artifact_dir / 'model.joblib'
joblib.dump(clf, model_path)

# Reload & quick sanity
m = joblib.load(model_path)
assert m.predict(Xte[:1]).shape == (1,)
```
Line-by-line
- joblib.dump persists the fitted estimator; joblib.load restores it for serving

---

Exercise 2 — Minimal FastAPI endpoint
Create `artifacts/day44/app.py`:
```python
from typing import Annotated

import joblib
import numpy as np
from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel, Field

app = FastAPI()
artifact_dir = Path(__file__).resolve().parent
model = joblib.load(artifact_dir / 'model.joblib')
CLASS_NAMES = ['setosa', 'versicolor', 'virginica']

class IrisFeatures(BaseModel):
    # exactly 4 numeric features (sepal length/width, petal length/width)
    features: Annotated[list[float], Field(min_length=4, max_length=4)]

@app.post('/predict')
def predict(data: IrisFeatures):
    X = np.array([data.features], dtype=float)
    pred = int(model.predict(X).tolist()[0])
    return {'prediction': pred, 'class_name': CLASS_NAMES[pred]}
```
Run the server in a terminal:
```bash
python -m uvicorn app:app --app-dir artifacts/day44 --reload
```

---

Exercise 3 — Test with curl; handle bad inputs
```bash
# OK request
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

# Bad request (length != 4) triggers validation error
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features": [1,2,3]}'
```
Notes
- Pydantic validates the request shape and types automatically
- Prefer returning human-friendly class names along with numeric ids
- Load only trusted joblib artifacts; pickle-compatible formats can execute code while loading

Deployment pointers
- Freeze dependencies into a minimal requirements.txt (fastapi, uvicorn, scikit-learn, joblib, numpy)
- Set `workers` via gunicorn/uvicorn in production; pin model and library versions for reproducibility
