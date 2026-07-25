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

## Learner exercises

1. Add `test_size` and `random_state` parameters to the training flow.
2. Split the training task into separate train and evaluate tasks with explicit
   outputs.
3. Explore the optional local Prefect UI and scheduling basics.

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
