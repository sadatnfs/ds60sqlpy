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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 55 learner notebook from this guide's **Next
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

## Concept deep dive — container build boundaries, minimal images, and health semantics

### The mental model

A container image is a versioned filesystem plus process configuration;
a container is one running process created from that image. Docker
builds layers from a **build context**, so `.dockerignore` controls what
can be sent to the builder. Multi-stage or ordered builds copy only the
runtime artifacts needed after dependency installation.

Liveness asks whether the process is functioning; readiness asks whether
it should receive traffic. Packaging does not add application security,
trusted artifacts, secret management, network policy, or safe defaults
automatically.

### Worked examples and syntax anatomy

- **`FROM` / pinned base:** establishes operating-system and Python dependencies; pin and scan rather than trusting `latest`.
- **`COPY` and `.dockerignore`:** define which local files enter the build context and image layers.
- **`CMD` / `HEALTHCHECK`:** define the main process and probe command without replacing service-level readiness policy.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — audit build-context inclusion before Docker runs

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
from fnmatch import fnmatch

files = [
    "app.py",
    "requirements.txt",
    ".env",
    ".venv/lib/package.py",
    "artifacts/model.joblib",
]
ignore_patterns = [".env", ".venv/*"]
included = [
    path for path in files
    if not any(fnmatch(path, pattern) for pattern in ignore_patterns)
]
print(included)
assert ".env" not in included and not any(p.startswith(".venv/") for p in included)
```

**Expected observation:** The environment file and local virtual environment are excluded while explicit runtime assets remain.

**Assumption to name:** This simplified matcher demonstrates review logic; Docker's complete ignore semantics and the real context still need inspection.

### Focused example B — distinguish process health from traffic readiness

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
def probe(*, process_running, model_loaded, dependency_ready, draining):
    return {
        "healthy": process_running,
        "ready": (
            process_running
            and model_loaded
            and dependency_ready
            and not draining
        ),
    }

during_dependency_outage = probe(
    process_running=True,
    model_loaded=True,
    dependency_ready=False,
    draining=False,
)
print(during_dependency_outage)
assert during_dependency_outage == {"healthy": True, "ready": False}
```

**Expected observation:** A running process can remain live while correctly refusing new traffic during a dependency outage.

**Assumption to name:** Restarting the healthy process would not repair the external dependency and could amplify the incident.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define container build boundaries, minimal images, and health semantics in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Copying the whole repository into an image, baking credentials into layers, or binding a development server publicly.

**Debug it deliberately:** Inspect build context, image history/SBOM, user, exposed ports, process signals, environment, artifact hash, and health/readiness responses.

**Stop condition:** Do not publish an image until secrets, base/dependency provenance, non-root runtime, probes, resource limits, and rollback are reviewed.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Create a slim dependency file containing only direct API runtime needs.

**Verify:** Practice 1 — container build boundaries, minimal images, and health semantics — build the image from a direct-runtime-only dependency file, print resolved package versions and image size, and run the health/predict smoke tests; prove test/notebook-only packages are absent.

2. Add `GET /health` returning `{"status": "ok"}`.

**Verify:** Practice 2 — container build boundaries, minimal images, and health semantics — with TestClient and the running container, assert GET /health returns status 200 and exactly {'status': 'ok'}; distinguish liveness from readiness by testing a missing/tampered model artifact.

3. Optionally push the image to a registry if you intentionally use a connected
   account.

**Verify:** Practice 3 — container build boundaries, minimal images, and health semantics — keep this optional and connected: either record a skipped result, or name the registry/repository/tag/digest, show authenticated push exit code 0, pull by digest, and rerun health/predict without exposing credentials.

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

**Verify:** Layer and secret audit — build/save the image, inspect history and archive file list, and assert sentinel .env, .git, notebook, cache, and artifacts paths/content are absent while required application files remain.

5. **Least-privilege runtime:** Run the service as a non-root user with a read-only filesystem and an explicit writable temporary directory. Diagnose any write assumptions.
   **Progressive hint:** Create the user in the image, set ownership only where needed, and write transient files under an intentionally mounted/temp path.

**Verify:** Least-privilege runtime — inside the container, print UID/GID and filesystem mount policy; assert UID is nonzero, writes outside the declared temp path fail, temp writes succeed, and health/predict still return expected statuses.

6. **Health semantics:** Implement separate `/live` and `/ready` checks and a startup failure when the model manifest is incompatible. Test all three states.
   **Progressive hint:** Liveness answers whether the process can respond; readiness answers whether it can safely serve the declared model contract.

**Verify:** Health semantics — assert /live is 200 while the process runs, /ready is 200 only after a compatible artifact loads, and tampered/missing manifests produce non-ready or startup failure with a sanitized message.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-55` — Day 55 — Containerizing a FastAPI Service.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize container build boundaries, minimal images, and health semantics. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day55_apis_containerization_docker.md`
- learner artifact: `python/ds-60day/notebooks/day55_apis_containerization_docker.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-54`. Do not assume knowledge beyond them or skip the
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
