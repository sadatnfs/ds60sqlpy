# Day 44 — Model Deployment with FastAPI (Companion Guide)

## Learning objectives
- Serve a trained sklearn pipeline behind a FastAPI endpoint
- Validate inputs with Pydantic models and handle errors
- Package artifacts and ensure reproducible environments

## Why this matters
A model is only valuable when it’s accessible reliably. FastAPI provides a lightweight, production-friendly API layer.

## Core concepts and examples
### App skeleton
```python
# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib

app = FastAPI()
model = joblib.load('model.joblib')

class Input(BaseModel):
    age: float
    income: float
    city: str

@app.post('/predict')
def predict(inp: Input):
    try:
        X = [[inp.age, inp.income, inp.city]]
        yhat = model.predict_proba(X)[0,1]
        return {'score': float(yhat)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```
Run: `uvicorn app:app --reload`.

### Packaging
- Pin versions in requirements.txt; store model with joblib
- Add a startup health route and logging

## Common pitfalls
- Mismatch between training and serving preprocessing; always serve the full Pipeline
- Missing input validation; Pydantic models help
- No timeouts/retries on client side; define SLAs

## Practice exercises
1) Wrap a trained pipeline and expose /predict
2) Add schema validation and informative error messages
3) Write a small client script to call the API

## Further reading
- FastAPI: https://fastapi.tiangolo.com/
