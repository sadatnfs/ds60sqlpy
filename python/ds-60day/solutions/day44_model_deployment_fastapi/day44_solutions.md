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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`class Request(BaseModel)`:** declares typed input fields and validation constraints that become JSON Schema.
2. **`@app.post('/predict', response_model=...)`:** binds an HTTP method/path to a validated function contract.
3. **`TestClient(app).post(..., json=payload)`:** exercises serialization, routing, validation, and response behavior without starting a network server.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Validation narrows untrusted input first, artifact/schema checks establish compatibility second, and a thin endpoint delegates deterministic prediction.

**Useful alternative:** ONNX or a safe JSON-based custom format can improve portability; application code may call a plain function when HTTP adds no value.

**Trade-off:** Strict schemas protect clients and models but require explicit versioning when the feature contract evolves.

**Edge case to test:** NaN/Infinity, huge batches, missing artifacts, version drift, concurrent load, and model exceptions require bounded error behavior.

**Evidence of correctness:** Use TestClient for valid/invalid payloads, assert response schema/status, verify artifact identity and feature metadata before readiness, and test no credential or input body enters logs.

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

### Reasoning notes for original Exercise 1

**Prompt:** Add input validation and friendly error behavior.

**How to reason about it:** Let Pydantic reject malformed requests with field-level messages, but validate domain rules such as finite values and exact feature count. Do not catch programming defects and relabel them as client mistakes.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Add input validation and friendly error behavior`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 2

**Prompt:** Return the class name as well as the numeric class identifier.

**How to reason about it:** Map numeric classes through metadata saved with the model and test every valid identifier. A class-name list copied independently into the service can drift from the fitted encoder.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Return the class name as well as the numeric class identifier`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 3

**Prompt:** Create a minimal runtime dependency file for this API.

**How to reason about it:** A runtime dependency list contains direct imports needed to load the artifact and serve requests—not the entire notebook environment. Build and smoke-test it in a clean environment.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Create a minimal runtime dependency file for this API`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.








### Exercise 4 — Boundary-case testing

**Prompt:** Write API tests for a missing feature, an extra feature, a string, NaN/infinity, wrong feature count, and one valid request. State the expected status-code family for each.

**Reasoning before implementation:** Use FastAPI TestClient so validation can be tested in-process. Malformed client input is 4xx; unexpected service failure is 5xx.

Prefer named request fields when the feature set is stable; they make missing
and extra values visible. If a numeric vector is required, constrain its length
and reject non-finite values before NumPy/model calls.

Tests should assert a stable error shape without pinning every word of
framework-generated prose. A valid request should assert response schema,
probability range, class mapping, and model version.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Write API tests for a missing feature, an extra feature, a string, NaN/infinity, wrong featur...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 5 — Batch contract

**Prompt:** Design a `/predict-batch` request and response with stable row IDs, a maximum batch size, ordered results, and per-request model metadata.

**Reasoning before implementation:** Validate the entire batch before scoring or define explicit partial failure semantics. Never rely only on list position to identify rows.

Include `request_id` per input and return it with each prediction. Enforce a
bounded batch size to protect memory and latency. Score one matrix rather than
looping through individual model calls, then preserve request order explicitly.

Choose atomic failure for a teaching service: if any row is invalid, return a
4xx response with indexed details and score none. Partial success is possible
but requires a more complex, versioned response contract.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Design a /predict-batch request and response with stable row IDs, a maximum batch size, order...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 6 — Artifact-compatibility check

**Prompt:** At startup, validate model version, expected feature schema, and class metadata before accepting traffic. Explain why loading a pickle from an untrusted source is unsafe.

**Reasoning before implementation:** Persist a small manifest beside the artifact and compare required fields. Python pickle/joblib loading can execute code.

Fail fast if artifact files are absent, hashes or schema versions disagree, or
the model lacks required prediction methods. Health/readiness should remain
false until these checks pass.

Only load artifacts produced through the trusted course pipeline. Hashes detect
accidental change but do not make an untrusted pickle safe; artifact provenance
and controlled storage are security boundaries.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `At startup, validate model version, expected feature schema, and class metadata before accept...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.
