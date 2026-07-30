# Day 55 — Solutions: APIs and Containerization with Docker

We containerize a FastAPI service, add a health endpoint and Docker HEALTHCHECK, and optimize image size via multi‑stage builds.

Contents
- Exercise 1: Containerize the Day 44 FastAPI service
- Exercise 2: Add health endpoint and HEALTHCHECK
- Exercise 3: Optimize image with multi‑stage builds

---

Exercise 1 — Minimal FastAPI app and Dockerfile
```python
# app.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Payload(BaseModel):
    x: float
    y: float

@app.post('/predict')
def predict(payload: Payload) -> dict[str, float]:
    # placeholder: sum as a toy 'model'
    return {"pred": payload.x + payload.y}
```

```dockerfile
# Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```text
# requirements.txt
fastapi>=0.115,<1
uvicorn>=0.30,<1
```
Build and run (the same one-line commands work in Bash, zsh, PowerShell, and Command Prompt):
```bash
docker build -t ds-fastapi:latest .
docker run -p 8000:8000 ds-fastapi:latest
```

---

Exercise 2 — Health endpoint and HEALTHCHECK
```python
# app.py addition
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

```dockerfile
# Add this before CMD. Python is already present in python:3.12-slim, so the
# check needs no curl package and uses no shell-specific operators.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"]
```
Explanation
- During the start period, failed probes do not count toward the retry threshold
- A successful probe marks the container healthy; consecutive failures mark it unhealthy
- Docker records health status but does not restart an unhealthy container by itself
- An orchestrator can act on that status only when its policy is configured to do so
- Keep the endpoint fast and dependency-light; use a separate readiness check when needed

---

Exercise 3 — Multi‑stage build
```dockerfile
# Stage 1: build dependencies in an isolated virtual environment.
FROM python:3.12-slim AS builder
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /build
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Stage 2: use the matching Python base so the copied environment is compatible.
FROM python:3.12-slim AS runtime
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser app.py .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```
Notes
- The final image contains neither `requirements.txt` nor build-stage caches
- Builder and runtime use the same Python minor version, avoiding ABI and script-shebang mismatches
- The runtime uses a non-root user and the same shell-independent health probe as Exercise 2
- For compiled packages, install compilers only in the builder stage

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Create a slim dependency file containing only direct API runtime needs.

**How to reason about it:** Trace direct imports from the service and serialized pipeline, install only runtime needs, and rebuild from a clean context. Keep development notebooks, tests, datasets, and credentials out of the image.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Add `GET /health` returning `{"status": "ok"}`.

**How to reason about it:** A liveness endpoint is cheap and local; a readiness endpoint verifies the artifact/schema is loaded. Test both and use a standard-library probe when a slim image does not contain curl.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Optionally push the image to a registry if you intentionally use a connected account.

**How to reason about it:** Registry upload is optional and networked. Use the registry's credential flow, a non-secret versioned tag/digest, image scanning, and never place tokens in Dockerfile instructions or build arguments.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Layer and secret audit

**Prompt:** Create a `.dockerignore`, inspect image history, and prove that `.env`, Git metadata, notebooks, caches, and local artifacts are absent.

**Reasoning before implementation:** The build context is the first boundary. Deleting a secret in a later layer does not remove it from earlier layers.

Allow only the service source, locked dependency metadata, and approved model
artifact into the context. Use runtime secret injection for connected
extensions; the portable lesson should require no credential.

Inspect final files as a non-root user and scan both source and image. If a
secret ever entered a built/pushed layer, rotate it—removing the file from the
latest layer is not sufficient.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Least-privilege runtime

**Prompt:** Run the service as a non-root user with a read-only filesystem and an explicit writable temporary directory. Diagnose any write assumptions.

**Reasoning before implementation:** Create the user in the image, set ownership only where needed, and write transient files under an intentionally mounted/temp path.

The model artifact and application code should be read-only at runtime.
Logging should go to stdout/stderr rather than a mutable file beside source.
If a framework requires a cache, configure a bounded writable temp directory
and document its lifecycle.

Bind to an unprivileged port such as 8000. Dropping root reduces impact but
does not replace dependency updates, network policy, or input validation.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Health semantics

**Prompt:** Implement separate `/live` and `/ready` checks and a startup failure when the model manifest is incompatible. Test all three states.

**Reasoning before implementation:** Liveness answers whether the process can respond; readiness answers whether it can safely serve the declared model contract.

`/live` should avoid dependency fan-out that could cause restart loops.
`/ready` can require successful artifact load, schema validation, and critical
local resources. A malformed artifact should fail startup or keep readiness
false, not return an “ok” response with later prediction failures.

Tests should simulate absent and mismatched artifacts without requiring Docker
or a network, then add one container smoke test for the packaged path.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
