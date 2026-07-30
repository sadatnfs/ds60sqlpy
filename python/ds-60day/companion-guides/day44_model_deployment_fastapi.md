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

## Learner exercises and progressive hints

1. Add input validation and friendly error behavior.
2. Return the class name as well as the numeric class identifier.
3. Create a minimal runtime dependency file for this API.

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
5. **Batch contract:** Design a `/predict-batch` request and response with stable row IDs, a maximum batch size, ordered results, and per-request model metadata.
   **Progressive hint:** Validate the entire batch before scoring or define explicit partial failure semantics. Never rely only on list position to identify rows.
6. **Artifact-compatibility check:** At startup, validate model version, expected feature schema, and class metadata before accepting traffic. Explain why loading a pickle from an untrusted source is unsafe.
   **Progressive hint:** Persist a small manifest beside the artifact and compare required fields. Python pickle/joblib loading can execute code.

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
