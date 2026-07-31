# Day 44 — Model Deployment with FastAPI

**Lesson ID:** `python-44` · **Level:** intermediate · **Dependencies:** `production` · **Network:** offline

This lesson turns a fitted scikit-learn model into a local HTTP service. It
teaches a development baseline—schema validation, serialization, and a request
contract—not a complete production platform.

## Learning objectives

By the end of the lesson, you can:

- save and reload a trusted scikit-learn artifact with `joblib`;
- define typed request data with Pydantic;
- implement a FastAPI `POST /predict` endpoint;
- test valid and invalid requests from PowerShell or a POSIX shell; and
- identify versioning, security, concurrency, and observability gaps.

## Prerequisites

- Complete `python-43` (model interpretation).
- Recall pipelines from `python-34` and input validation from `python-29`.
- Install the `production` dependency group during bootstrap.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| API | Explicit software contract for requests and responses |
| Endpoint | HTTP method and path handled by an application |
| Request schema | Validated structure and types accepted by an endpoint |
| Serialization | Converting an object into a stored or transmitted representation |
| Inference | Applying a fitted model to new inputs |
| HTTP 422 | FastAPI response for request data that fails schema validation |
| Model contract | Expected feature names, order, types, units, and model version |

An API boundary should reject malformed input before model code runs. A
four-number list is adequate for this exercise, but named fields and units are
safer in a real service.

## Worked example: validate the feature count

```python
from typing import Annotated

import joblib
import numpy as np
from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel, Field

app = FastAPI()
artifact_dir = Path(__file__).resolve().parent
model = joblib.load(artifact_dir / "model.joblib")  # load only an artifact you trust
class_names = ["setosa", "versicolor", "virginica"]

class IrisFeatures(BaseModel):
    features: Annotated[list[float], Field(min_length=4, max_length=4)]

@app.post("/predict")
def predict(payload: IrisFeatures) -> dict[str, int | str]:
    row = np.asarray([payload.features], dtype=float)
    prediction = int(model.predict(row)[0])
    return {
        "prediction": prediction,
        "class_name": class_names[prediction],
    }
```

Keep `app.py` beside the trusted model under `artifacts/day44/`, then run
`python -m uvicorn app:app --app-dir artifacts/day44 --reload` from the
repository root. Use
development reload only while editing.

## Test the request on your operating system

macOS/Linux:

```bash
.venv/bin/python -m uvicorn app:app --reload
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[5.1,3.5,1.4,0.2]}'
```

Windows PowerShell (server in one terminal, request in another):

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
$body = @{ features = @(5.1, 3.5, 1.4, 0.2) } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/predict' `
  -ContentType 'application/json' -Body $body
```

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 44 learner notebook from this guide's **Next
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

## Concept deep dive — validated request contracts, trusted artifacts, and testable inference endpoints

### The mental model

Deployment turns a model into a boundary other software can call. The
request schema validates untrusted JSON before it reaches model code;
the feature builder establishes exact name, order, type, missing-value,
and range rules; the response schema makes outputs stable for clients.

FastAPI handles HTTP routing and delegates data validation to Pydantic.
A successful model load is not proof of compatibility or trust.
Artifact format, source, digest, library versions, and feature schema
must be verified before the service becomes ready.

### Worked examples and syntax anatomy

- **`class Request(BaseModel)`:** declares typed input fields and validation constraints that become JSON Schema.
- **`@app.post('/predict', response_model=...)`:** binds an HTTP method/path to a validated function contract.
- **`TestClient(app).post(..., json=payload)`:** exercises serialization, routing, validation, and response behavior without starting a network server.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — make request validation fail before inference

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
from pydantic import BaseModel, Field, ValidationError

class PredictionRequest(BaseModel):
    measurements: list[float] = Field(min_length=4, max_length=4)

valid = PredictionRequest.model_validate(
    {"measurements": [5.1, 3.5, 1.4, 0.2]}
)
print(valid.model_dump())
try:
    PredictionRequest.model_validate({"measurements": [5.1, 3.5]})
except ValidationError as exc:
    print(exc.errors()[0]["type"])
```

**Expected observation:** The valid payload becomes a typed object; the short list raises a structured validation error before any model call.

**Assumption to name:** Exactly four ordered measurements is the public contract; coercion and range policy are documented.

### Focused example B — check artifact feature compatibility explicitly

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0, 0, 1, 1])
model = LogisticRegression().fit(X, y)

request_features = np.array([[0.2, 0.8]])
if request_features.shape[1] != model.n_features_in_:
    raise ValueError("feature-count mismatch")
print(model.predict_proba(request_features).tolist())
```

**Expected observation:** Inference proceeds only after the request matrix matches the fitted feature-count contract.

**Assumption to name:** Feature count alone is insufficient in production; names, order, types, and preprocessing version must also match.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define validated request contracts, trusted artifacts, and testable inference endpoints in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Loading an arbitrary pickle/joblib file or accepting a raw list with undocumented feature order.

**Debug it deliberately:** Test valid, missing, extra, wrong-type, non-finite, out-of-range, and batch-size payloads; log only bounded non-sensitive metadata.

**Stop condition:** Do not bind a development server publicly or treat a local endpoint as production-ready security.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Add input validation and friendly error behavior.

**Verify:** Practice 1 — validated request contracts, trusted artifacts, and testable inference endpoints — with TestClient, assert a valid payload returns 200 and the declared response schema; assert missing, wrong-type, extra, and out-of-range fields return 422 with field-level errors and no traceback or request body in logs.

2. Return the class name as well as the numeric class identifier.

**Verify:** Practice 2 — validated request contracts, trusted artifacts, and testable inference endpoints — for a fixed request, assert the response contains both numeric class_id and the matching class_name from persisted metadata; test an unknown/out-of-range model class as an explicit startup or 5xx failure.

3. Create a minimal runtime dependency file for this API.

**Verify:** Practice 3 — validated request contracts, trusted artifacts, and testable inference endpoints — build a fresh environment from the runtime file, run the health and predict smoke tests with exit code 0, and record installed versions; exclude notebooks, test-only tools, and undeclared transitive guesses.

### Progressive hints

1. Let Pydantic reject the wrong length or nonnumeric values. Do not catch every
   exception and turn programming defects into vague client errors.
2. Keep the mapping beside the model metadata and test all valid numeric class
   identifiers.
3. Include only direct runtime imports. Pin or lock versions through the
   repository tooling rather than copying the entire development environment.

### Additional mastery practice

Make an API boundary explicit: validate shape and meaning, map model outputs to a versioned schema, and test behavior without relying on a manually running server.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Boundary-case testing:** Write API tests for a missing feature, an extra feature, a string, NaN/infinity, wrong feature count, and one valid request. State the expected status-code family for each.
   **Progressive hint:** Use FastAPI TestClient so validation can be tested in-process. Malformed client input is 4xx; unexpected service failure is 5xx.

**Verify:** Boundary-case testing — parameterize TestClient cases for missing, extra, string, NaN, infinity, wrong-length, and valid payloads; assert exact 2xx/4xx families, response keys, and that no invalid request reaches model.predict.

5. **Batch contract:** Design a `/predict-batch` request and response with stable row IDs, a maximum batch size, ordered results, and per-request model metadata.
   **Progressive hint:** Validate the entire batch before scoring or define explicit partial failure semantics. Never rely only on list position to identify rows.

**Verify:** Batch contract — define request/response examples with stable row_id, max batch size, ordered one-result-per-input output, model_id/version, and per-row error policy; test empty, oversize, duplicate-ID, mixed-validity, and valid batches.

6. **Artifact-compatibility check:** At startup, validate model version, expected feature schema, and class metadata before accepting traffic. Explain why loading a pickle from an untrusted source is unsafe.
   **Progressive hint:** Persist a small manifest beside the artifact and compare required fields. Python pickle/joblib loading can execute code.

**Verify:** Artifact-compatibility check — tamper model version, feature order, and class metadata one at a time; assert readiness/startup fails before traffic for each, while a matching manifest yields ready status and one fixed prediction.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why is an untrusted `joblib`/pickle-compatible artifact unsafe to load?
- Which data contract is lost when a bare numeric list is reordered?
- What should a client receive for three features instead of four?
- Why should training and serving library versions be recorded together?

Expected behavior: a valid request returns JSON with an integer and class name;
an invalid-length request is rejected before `model.predict`.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Diagnostic or response |
|---|---|---|
| `Error loading ASGI app` | Wrong directory or module path | Confirm `app.py` and run `python -m uvicorn app:app` there |
| `FileNotFoundError: model.joblib` | Relative working directory differs | Resolve an application-relative `Path` |
| HTTP 422 | Request violates Pydantic schema | Read the response detail; fix the client payload |
| Prediction shape error | Contract and model features differ | Version and test feature schema |
| Works locally but not under concurrency | Shared state or resource assumptions | Load immutable artifacts at startup and test load |

FastAPI generates local OpenAPI docs at `/docs`. Authentication, rate limits,
TLS, secrets, audit logs, drift monitoring, and rollback are outside this single
lesson and must be designed before Internet-facing deployment.

## Next step

- Work in the [Day 44 learner notebook](../notebooks/day44_model_deployment_fastapi.ipynb).
- Then review the
  [Day 44 solution](../solutions/day44_model_deployment_fastapi/day44_solutions.md).
- Continue to [Day 45 — End-to-End Project](day45_end_to_end_modeling_project.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-44` — Day 44 — Model Deployment with FastAPI.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize validated request contracts, trusted artifacts, and testable inference endpoints. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day44_model_deployment_fastapi.md`
- learner artifact: `python/ds-60day/notebooks/day44_model_deployment_fastapi.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-43`. Do not assume knowledge beyond them or skip the
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
