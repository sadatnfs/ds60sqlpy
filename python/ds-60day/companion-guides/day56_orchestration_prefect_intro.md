# Day 56 — Orchestration with Prefect (Companion Guide)

## Learning objectives
- Build Prefect flows/tasks with retries, caching, and parameters
- Run locally and deploy to Prefect Cloud/Server
- Use blocks for secrets/storage; schedule runs

## Why this matters
Orchestration turns notebooks and scripts into robust, observable pipelines.

## Core concepts and examples
```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=10)
def extract(): ...
@task
def transform(df): ...
@task
def load(df): ...

@flow
def etl_flow():
    raw = extract()
    clean = transform(raw)
    load(clean)

if __name__ == '__main__':
    etl_flow()
```

- Parameters, mapping, concurrency limits
- Blocks: S3/GCS storage, Secrets; UI to monitor states

## Common pitfalls
- Packing heavy objects into task returns; prefer storage references
- No idempotency; re-runs cause duplicates
- Mixing local paths with remote storage

## Practice exercises
1) Convert an ETL notebook into a Prefect flow
2) Add retries and alerting on failure
3) Parameterize date range and schedule daily

## Further reading
- Prefect: https://docs.prefect.io
