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

X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
clf = LogisticRegression(max_iter=1000, multi_class='auto').fit(Xtr, ytr)
print({'test_acc': clf.score(Xte, yte)})
joblib.dump(clf, 'model.joblib')

# Reload & quick sanity
m = joblib.load('model.joblib')
assert m.predict(Xte[:1]).shape == (1,)
```
Line-by-line
- joblib.dump persists the fitted estimator; joblib.load restores it for serving

---

Exercise 2 — Minimal FastAPI endpoint
Create `app.py` in this folder:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conlist
import joblib, numpy as np

app = FastAPI()
model = joblib.load('model.joblib')
CLASS_NAMES = ['setosa', 'versicolor', 'virginica']

class IrisFeatures(BaseModel):
    # exactly 4 numeric features (sepal length/width, petal length/width)
    features: conlist(float, min_items=4, max_items=4)

@app.post('/predict')
def predict(data: IrisFeatures):
    try:
        X = np.array([data.features], dtype=float)
        pred = int(model.predict(X).tolist()[0])
        return {'prediction': pred, 'class_name': CLASS_NAMES[pred]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Bad request: {e}')
```
Run the server in a terminal:
```bash
uvicorn app:app --reload
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

Deployment pointers
- Freeze dependencies into a minimal requirements.txt (fastapi, uvicorn, scikit-learn, joblib, numpy)
- Set `workers` via gunicorn/uvicorn in production; pin model and library versions for reproducibility
