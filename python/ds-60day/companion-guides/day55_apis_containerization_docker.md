# Day 55 — Containerizing a FastAPI Service

**Lesson ID:** `python-55` · **Level:** advanced · **Dependencies:** `production` · **Network:** offline

A container image packages application files, runtime dependencies, and startup
configuration. It improves portability, but it is not a virtual machine,
security boundary, or substitute for tests and observability.

## Learning objectives

By the end of the lesson, you can:

- package the Day 44 FastAPI service and trusted model artifact;
- write a small Python 3.12 Dockerfile with a minimal runtime dependency set;
- build, run, test, inspect, and stop a local container;
- add an application health endpoint and image health check; and
- identify image, secret, dependency, and registry risks.

## Prerequisites

- Complete `python-54`; retain the Day 44 API files.
- Install Docker Desktop or another compatible Docker runtime during setup.
- During connected bootstrap, pre-pull the base image and build once so the
  image layers and Python dependencies are available for offline reruns.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Image | Immutable layered package used to create containers |
| Container | Running isolated process created from an image |
| Build context | Files made available to `docker build` |
| Layer | Cached filesystem change produced by an image instruction |
| Port mapping | Host port forwarded to a container port |
| Health check | Probe reporting whether the process can serve its contract |
| Registry | Remote service for image storage and distribution |
| `.dockerignore` | Excludes unnecessary or sensitive build-context files |

Install dependencies before copying frequently changing source so Docker can
reuse the dependency layer. Never copy `.env`, `.git`, local caches, or training
data into the build context.

## Worked example: minimal service image

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY requirements-api.txt ./
RUN python -m pip install --no-cache-dir -r requirements-api.txt

COPY app.py model.joblib ./
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Pin and review dependencies through project tooling for a durable image. The
unpinned learner snippet keeps the first Dockerfile readable; it is not a
release supply-chain policy.

## Build and run

These Docker commands are the same in PowerShell and POSIX shells:

```text
docker build -t ds60-api:local .
docker run --rm --name ds60-api -p 8000:8000 ds60-api:local
```

Test from another terminal.

macOS/Linux:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[5.1,3.5,1.4,0.2]}'
```

Windows PowerShell:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
$body = @{ features = @(5.1, 3.5, 1.4, 0.2) } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/predict' `
  -ContentType 'application/json' -Body $body
```

## Learner exercises and progressive hints

1. Create a slim dependency file containing only direct API runtime needs.
2. Add `GET /health` returning `{"status": "ok"}`.
3. Optionally push the image to a registry if you intentionally use a connected
   account.

### Progressive hints

1. Trace imports from `app.py` and the serialized pipeline. Rebuild in a clean
   image and run both endpoints.
2. Keep liveness cheap. A Docker `HEALTHCHECK` can use Python's standard
   `urllib.request` so a slim image does not need `curl`.
3. Use a non-secret image name/tag, authenticate through the registry's
   supported credential flow, scan the image, and never embed credentials in a
   layer. Registry upload is optional and networked.

### Additional mastery practice

Containerize a minimal, testable service without embedding secrets or privileged assumptions. Build, readiness, and runtime health have distinct contracts.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Layer and secret audit:** Create a `.dockerignore`, inspect image history, and prove that `.env`, Git metadata, notebooks, caches, and local artifacts are absent.
   **Progressive hint:** The build context is the first boundary. Deleting a secret in a later layer does not remove it from earlier layers.
5. **Least-privilege runtime:** Run the service as a non-root user with a read-only filesystem and an explicit writable temporary directory. Diagnose any write assumptions.
   **Progressive hint:** Create the user in the image, set ownership only where needed, and write transient files under an intentionally mounted/temp path.
6. **Health semantics:** Implement separate `/live` and `/ready` checks and a startup failure when the model manifest is incompatible. Test all three states.
   **Progressive hint:** Liveness answers whether the process can respond; readiness answers whether it can safely serve the declared model contract.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why must Uvicorn bind to `0.0.0.0` inside the container?
- What is the difference between `EXPOSE 8000` and `-p 8000:8000`?
- Which files should `.dockerignore` exclude?
- Why is a process-running check weaker than a prediction-contract smoke test?

Expected behavior: the container starts without a network after its image has
been built, `/health` returns status JSON, and `/predict` matches the local API.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Port is unreachable | App bound to localhost inside container or port not mapped | Bind `0.0.0.0`; inspect `docker ps` |
| `model.joblib` missing | File outside build context or omitted from `COPY` | Inspect context and image paths |
| Image rebuild downloads packages offline | Dependency layer/cache absent | Prebuild during connected bootstrap or use a wheelhouse |
| Health check always fails | Probe tool absent or endpoint wrong | Use a standard-library probe and test manually |
| Image contains secrets/large data | Broad `COPY . .` | Use explicit copies and `.dockerignore` |

Multi-stage and distroless images can reduce size and attack surface but add
debugging and compatibility tradeoffs. Measure the image and threat model before
adding complexity.

## Next step

- Work in the [Day 55 learner notebook](../notebooks/day55_apis_containerization_docker.ipynb).
- Then consult the
  [Day 55 solution](../solutions/day55_apis_containerization_docker/day55_solutions.md).
- Continue to [Day 56 — Prefect](day56_orchestration_prefect_intro.md).
