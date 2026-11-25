# apache-032: Operations and recovery

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-028`, `apache-030`, `apache-031`.

## Key terms

- **Metadata database:** Airflow's store for Dag Runs, task instances, scheduling state and configuration. A successful connection to it does not prove that output data still exists.
- **Scheduler heartbeat:** The scheduler's periodically updated liveness timestamp. A stale heartbeat reveals a stopped scheduler even when the API server returns HTTP 200.
- **Task instance state:** The recorded status of one task in one Dag Run, such as queued, running, success, failed or up_for_retry.
- **Named volume:** The Docker volume that holds the workshop's metadata, logs, attempt markers and outputs so they survive replacing the container image or process.

## Operational state has several independent owners

Airflow retains Dag Runs, task instances, scheduling state and configuration in
its metadata system. Task logs and data outputs have their own storage paths.
The container image supplies application code and dependencies. Replacing the
image or process should not silently erase the other state categories, and a
successful metadata connection is not proof that output data still exists.

The workshop keeps SQLite metadata, local logs, attempt markers and synthetic
outputs in its owned named volume. Its source project remains read-only inside
the service. The standalone installation includes scheduler, DAG processor, API
server and triggerer processes, with explicit CPU, memory and process limits.
This is a local development topology and has no replicated availability guarantee.

Health checks must inspect component status, not merely HTTP200. Airflow's monitor
endpoint can return a successful HTTP response containing an unhealthy scheduler
status. A scheduler heartbeat check and an API-server liveness check answer
different questions. The project evaluates the relevant component fields and
reports missing or stale components clearly.

## Worked case A: restart without losing completed history

After the finite workflows complete, capture readback, stop the owned container,
resume it and read back again. Resume starts the exact retained container without
building or pulling. Completed Dag Run identities, output source hashes and
partition values should remain present. Readback itself does not trigger work or
recreate previous outputs.

A separate down/start sequence replaces the service container while preserving
the named volume. The project validates ownership labels before each mutation
and refuses incomplete or mismatched retained data. This demonstrates the local
storage boundary across process and container lifetime, not survival after volume
loss, disk corruption or a second-host failover.

An automatically generated new database would conceal a failed persistence path.
The initializer therefore distinguishes a fresh owned state from an existing
installation and does not delete metadata to make startup succeed. Inspect the
actual database path, mount and permissions before diagnosing a missing-history
report as a scheduler defect.

## Worked case B: diagnose waiting and failed work

The health and readback actions show actual component state, task-instance state,
try count and pool configuration. The worked diagnosis distinguishes a task
waiting for a pool slot from one queued for execution, one running, and one that
failed after starting. Those states suggest different next checks: capacity,
executor availability, logs, dependencies or data/configuration errors.

The intentional fail_once task supplies a known failed-then-retried history.
Its first exception is expected only for that fixture path; unrelated failures
must not be dismissed as part of the lesson. Compare run identity, task name,
attempt number and diagnostic before taking corrective action.

A hung external call needs an execution timeout and a policy for ambiguous effects.
Restarting the scheduler does not necessarily stop every external job it submitted.
A production runbook must reconcile the external system's request identity before
resubmitting. The workshop uses bounded local tasks and does not claim to recover
unseen cloud or database operations.

## Mistakes, diagnosis and interview discussion

Preserve logs and state before repair, and keep a supported backup/restore plan
for valuable installations. Do not run global Docker prune, remove unrelated
volumes or clear all tasks to hide one issue. The confirmed destroy command
checks every owned resource and deletes only this workshop's disposable state.
Ordinary stop, resume and down preserve it.

**Interview discussion: what should an Airflow recovery report contain?** State
which components restarted, whether existing run identities survived, which data
and logs were read back, what work remained failed or ambiguous, and whether the
service was unavailable during interruption. These cases separate actual local
persistence and task diagnosis from a broad unsupported claim of production
resilience.

The [complete Airflow workshop](../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

## Worked examples

### Read component health instead of an HTTP status

```python external
import json
import urllib.request

url = "http://127.0.0.1:8080/api/v2/monitor/health"
with urllib.request.urlopen(url, timeout=5) as response:
    data = json.loads(response.read(16_385))
components = ("metadatabase", "scheduler", "dag_processor", "triggerer")
print({name: data[name]["status"] for name in components})
```

This mirrors the project health.py, which runs inside the Airflow container. A healthy deployment prints four entries, each with the status healthy. The endpoint can answer with HTTP 200 while the scheduler entry says unhealthy, because the API server is a separate process from the scheduler; a probe that stops at the status code would report a stalled platform as fine. If only dag_processor is unhealthy, new or edited DAG files will not appear even though existing runs continue.

### Stop, resume and compare saved history

```bash
cd work/airflow
bash run.sh readback
bash run.sh stop
bash run.sh resume
bash run.sh health
bash run.sh readback
```

In an owned workshop, the two readback documents should list the same outputs and saved_observations, because stop and resume keep the container and its PostgreSQL metadata volume. Readback only inspects files and metadata, so running it twice must not create new runs. If the second readback shows fewer summaries, something deleted state between the calls; check whether down or destroy was run instead of stop, and read bash run.sh logs before starting anything new.

### Separate waiting work from failed work

```bash
cd work/airflow
bash run.sh status
bash run.sh logs
bash run.sh health
```

Status shows whether the airflow container is running and healthy, the bounded logs show the last 100 lines, and health names which component is unhealthy. A task stuck in queued with a healthy scheduler usually points to pool or concurrency limits, while a task that never leaves scheduled with an unhealthy scheduler points to the scheduler process itself. A failed task has a log with an exception and a retry count; treat that as an application problem and fix its inputs, not the platform.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Health, saved history and exact resume

```bash
bash run.sh health
bash run.sh readback
bash run.sh stop
bash run.sh resume
bash run.sh health
bash run.sh readback
```

Readback is inspection only. For retained-volume replacement:

```bash
bash run.sh down
bash run.sh start
bash run.sh readback
```

Inspect bounded logs before changing state:

```bash
bash run.sh logs
```

The README documents the separate `destroy --confirm-owned-data-loss` action.
It is never implied by stop, resume, down or a health failure.

## Primary references

- [Airflow health checks](https://airflow.apache.org/docs/apache-airflow/3.3.2/administration-and-deployment/logging-monitoring/check-health.html)
- [Airflow standalone boundary](https://airflow.apache.org/docs/apache-airflow/3.3.2/start.html)
