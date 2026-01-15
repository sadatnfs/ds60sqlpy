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
def predict(p: Payload):
    # placeholder: sum as a toy 'model'
    return {'pred': p.x + p.y}
```

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```text
# requirements.txt
fastapi
uvicorn[standard]
```
Build and run
```bash
docker build -t ds-fastapi:latest .
docker run -p 8000:8000 ds-fastapi:latest
```

---

Exercise 2 — Health endpoint and HEALTHCHECK
```python
# app.py addition
@app.get('/health')
def health():
    return {'status':'ok'}
```

```dockerfile
# Dockerfile addition
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```
Explanation
- HEALTHCHECK lets orchestrators replace unhealthy containers
- Keep timeouts short; endpoint should be fast and dependency‑light

---

Exercise 3 — Multi‑stage build
```dockerfile
# Stage 1: builder with build deps
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-warn-script-location --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM gcr.io/distroless/python3-debian12 AS runtime
COPY --from=builder /install /usr/local
WORKDIR /app
COPY app.py .
EXPOSE 8000
CMD ["/usr/local/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```
Notes
- Distroless reduces attack surface; ensure compatibility
- Alternatively, use python:slim and remove build tools after install
