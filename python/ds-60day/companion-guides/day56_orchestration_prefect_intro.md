# Day 56 — Orchestration with Prefect 3

**Lesson ID:** `python-56` · **Level:** advanced · **Dependencies:** `production` · **Network:** first-run Seaborn cache

Orchestration coordinates when and how a workflow runs, records state, and helps
operators recover from failure. It does not make a non-idempotent, leaky, or
incorrect pipeline reliable automatically.

## Learning objectives

By the end of the lesson, you can:

- define local Prefect 3 tasks and a flow;
- pass explicit data and parameters between tasks;
- split training from evaluation with typed outputs;
- interpret local run logs and task states; and
- describe retries, caching, scheduling, and idempotency tradeoffs.

## Prerequisites

- Complete `python-55` (containerization).
- Recall the Day 45 training pipeline and Day 53 run metadata.
- Install the `production` dependency group.
- Cache Seaborn's Titanic dataset once while connected before offline study.

## Dataset and execution contract

The learner flow loads `seaborn.load_dataset("titanic")`; the first call may
download and cache the dataset. After that accepted bootstrap, direct local flow
runs are offline. The Prefect UI and local server are optional; Prefect Cloud is
not required.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Flow | Observable workflow function coordinating tasks |
| Task | Unit with independently recorded state and optional retry/cache policy |
| State | Run condition such as pending, running, completed, failed, or crashed |
| Parameter | Explicit input to a flow or task |
| Retry | Re-execution after failure under a declared policy |
| Idempotency | Repeating an operation has the same intended effect as doing it once |
| Deployment | Configuration connecting a flow to remote/scheduled execution |
| Scheduler | Creates planned runs according to timing rules |

Use tasks at meaningful failure and retry boundaries. Turning every trivial line
into a task adds serialization, logging, and coordination overhead.

## Worked example: small, typed, local flow

```python
from prefect import flow, task

@task
def load_numbers(limit: int) -> list[int]:
    return list(range(limit))

@task
def summarize(values: list[int]) -> dict[str, int]:
    return {"rows": len(values), "total": sum(values)}

@flow(log_prints=True)
def summary_flow(limit: int = 10) -> dict[str, int]:
    result = summarize(load_numbers(limit))
    print(result)
    return result

if __name__ == "__main__":
    summary_flow(limit=10)
```

This runs directly in one local process and needs no server. Add retries only to
operations that can safely repeat and whose failures are plausibly transient.

## Optional local Prefect 3 UI

Start the local server.

macOS/Linux:

```bash
.venv/bin/prefect server start
```

Windows PowerShell:

```powershell
.\.venv\Scripts\prefect.exe server start
```

Follow the CLI output for the local API URL and open the displayed local UI
(normally `http://127.0.0.1:4200`). Keep this local; no hosted account is needed.
For scheduling practice in Prefect 3, prefer a local `flow.serve(...)` example
after the direct flow is correct, and keep its serving process running.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 56 learner notebook from this guide's **Next
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

## Concept deep dive — observable task boundaries, retries, caching, and idempotent orchestration

### The mental model

An orchestrator records workflow state and coordinates retries,
dependencies, schedules, and concurrency. A flow describes the larger
run; tasks are observable units with their own state and policy. The
boundary should be large enough to be meaningful and small enough to
retry without repeating unrelated side effects.

Retries are safe only for transient failures and idempotent operations.
Caching requires a key representing all inputs and code/data meaning,
plus persisted results. Neither retry nor cache makes an unsafe side
effect idempotent automatically.

### Worked examples and syntax anatomy

- **`@flow`:** creates the orchestration boundary and run-level parameters/state.
- **`@task(retries=..., retry_delay_seconds=...)`:** declares task-level retry policy; exception classification still matters.
- **cache key + result persistence:** reuses a completed result only when identity and storage semantics are deliberate.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — derive an idempotent local output identity

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import hashlib
import json

inputs = {"data_snapshot": "sales-v3", "model": "ridge", "alpha": 1.0}
canonical = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
key = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
output_path = f"artifacts/day56/{key}/metrics.json"
print({"cache_key": key, "output_path": output_path})
assert key in output_path
```

**Expected observation:** Identical canonical inputs produce the same bounded output identity instead of a new timestamped duplicate.

**Assumption to name:** The key includes every input that changes result meaning, including data and code/version identity where needed.

### Focused example B — separate retryable from permanent failures

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
class TemporaryUnavailable(RuntimeError):
    pass

class InvalidInput(ValueError):
    pass

def should_retry(error):
    return isinstance(error, (TemporaryUnavailable, TimeoutError))

cases = [TemporaryUnavailable("later"), TimeoutError(), InvalidInput("bad row")]
decisions = [should_retry(error) for error in cases]
print(decisions)
assert decisions == [True, True, False]
```

**Expected observation:** Only failures that may succeed without changing the input are eligible for retry.

**Assumption to name:** The task's side effects are idempotent or protected by a durable idempotency key.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define observable task boundaries, retries, caching, and idempotent orchestration in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Adding retries to every exception or caching a task with undeclared external inputs and side effects.

**Debug it deliberately:** Inspect task state history, attempt count, exception type, cache key inputs, persisted result, output identity, and cleanup after injected failure.

**Stop condition:** Do not schedule/deploy a flow until local runs are deterministic, reruns are safe, and ownership/alerts are defined.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Add `test_size` and `random_state` parameters to the training flow.

**Verify:** Practice 1 — observable task boundaries, retries, caching, and idempotent orchestration — run the flow twice with two explicit test_size/random_state pairs, print parameter values, split row counts/hashes, and metrics, and assert a repeated identical pair reproduces the same split.

2. Split the training task into separate train and evaluate tasks with explicit
   outputs.

**Verify:** Practice 2 — observable task boundaries, retries, caching, and idempotent orchestration — make train return a model/artifact identity and evaluate accept that explicit value; print task states and metric, and inject a train failure to prove evaluate does not run on missing output.

3. Explore the optional local Prefect UI and scheduling basics.

**Verify:** Practice 3 — observable task boundaries, retries, caching, and idempotent orchestration — either print an explicit offline-skip result or start the local UI, record the local URL and one completed flow-run ID/state, then stop it cleanly; scheduling remains optional and must not require a cloud account.

### Progressive hints

1. Pass parameters from the flow to the task; log them with the resulting metric
   so a run can be reproduced.
2. Return the fitted pipeline plus held-out arrays or a small typed result.
   Consider whether passing a large dataset between task processes would scale.
3. First prove `training_flow()` succeeds directly. Then run a local server and
   use Prefect 3's current `serve`/deployment workflow—not commands copied from
   older major versions.

The separate solution reinforces retry, notification, and scheduling concepts.
Use the Prefect 3 execution path in this guide and the current learner
environment when translating those concepts.

### Additional mastery practice

Orchestrate explicit, typed tasks whose retries are safe, artifacts are versioned, and failures are observable. A flow wrapper does not repair an unsafe task.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Retry and idempotence:** Add retries to a task that writes an artifact. Make the write idempotent so a failure after writing cannot create duplicate or partially valid outputs.
   **Progressive hint:** Write to a temporary path, validate, then atomically replace a versioned destination. A retry should produce the same logical result.

**Verify:** Retry and idempotence — inject a failure after the first artifact write, then retry; assert exactly one final path/manifest exists, its hash matches a clean run, no partial file remains, and attempt count/state are recorded.

5. **Cache-key design:** Design a task cache key that changes when data fingerprint, code/config, or relevant parameters change, but not when an unrelated log message changes.
   **Progressive hint:** Hash canonical semantic inputs and include a task/schema version. Do not cache a task whose hidden external state is untracked.

**Verify:** Cache-key design — print cache keys for identical inputs, changed data hash, changed code/config, changed relevant parameter, and log-only change; assert equality only for identical/log-only cases and inequality for semantic changes.

6. **Failure observability:** Instrument a three-task flow so logs and a final summary identify run ID, task, safe input version, attempt, elapsed time, artifact ID, and failure category without logging sensitive rows.
   **Progressive hint:** Use structured fields and task/run context. Emit counts and opaque IDs rather than raw feature values.

**Verify:** Failure observability — capture a three-task failure run and assert every event contains run ID, task, safe input version, attempt, elapsed time, artifact ID, and failure category; raw row and secret sentinels must be absent and final state must identify the failed task.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Which tasks are safe to retry, and which could duplicate an external write?
- What metadata is required to reproduce a scheduled training run?
- Why might returning a large DataFrame between distributed tasks be expensive?
- What must remain true if a failed run restarts halfway through?

Expected behavior: direct flow execution prints a deterministic local result and
records task/flow state. A local UI is optional and must not change model logic.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Retrying non-idempotent load | Duplicate external records | Use transactions/upserts and idempotency keys |
| Hiding parameters in globals | Runs cannot be reproduced | Declare flow/task parameters |
| Orchestrator-specific business logic | Hard to test without runtime | Keep core functions plain and wrap them in tasks |
| Old Prefect CLI examples | Commands fail under Prefect 3 | Use installed-version help and current `serve`/deploy flow |
| Secrets in code or logs | Credential exposure | Use environment/secret facilities and redact output |
| Every operation becomes a task | High orchestration overhead | Choose meaningful state/retry boundaries |

Scheduling creates new operational obligations: ownership, concurrency limits,
late-run handling, alerts, backfills, retention, and recovery tests.

## Next step

- Work in the [Day 56 learner notebook](../notebooks/day56_orchestration_prefect_intro.ipynb).
- Then consult the
  [Day 56 solution](../solutions/day56_orchestration_prefect_intro/day56_solutions.md).
- Continue to [Day 57 — Security, Privacy, and Ethics](day57_security_privacy_ethics.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-56` — Day 56 — Orchestration with Prefect 3.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize observable task boundaries, retries, caching, and idempotent orchestration. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day56_orchestration_prefect_intro.md`
- learner artifact: `python/ds-60day/notebooks/day56_orchestration_prefect_intro.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-55`. Do not assume knowledge beyond them or skip the
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
