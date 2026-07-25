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
