# apache-032: Operations and recovery

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-028`, `apache-030`, `apache-031`.

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
