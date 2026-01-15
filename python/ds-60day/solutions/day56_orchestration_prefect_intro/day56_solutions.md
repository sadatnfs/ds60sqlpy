# Day 56 — Solutions: Orchestration with Prefect

We convert an ETL notebook into a Prefect flow, add retries and alerting, and parameterize the date with a schedule.

Contents
- Exercise 1: Convert ETL to Prefect flow
- Exercise 2: Add retries and alerting
- Exercise 3: Parameterize date and schedule daily

---

Exercise 1 — Flow and tasks
```python
from prefect import flow, task, get_run_logger

@task(retries=3, retry_delay_seconds=10)
def extract(date: str):
    logger = get_run_logger(); logger.info(f'Extract for {date}')
    # ... fetch from API/storage
    return {'rows': 100}

@task
def transform(data):
    # ... cleaning, joins
    data['rows'] *= 0.95
    return data

@task
def load(data):
    # ... write to warehouse
    return {'loaded': data['rows']}

@flow(name='etl-daily')
def etl_flow(date: str):
    raw = extract(date)
    clean = transform(raw)
    result = load(clean)
    return result

if __name__ == '__main__':
    etl_flow(date='2024-01-01')
```

Exercise 2 — Alerting on failure
```python
from prefect.blocks.notifications import SlackWebhook

# Configure once in UI or via code, then load by name
slack = SlackWebhook.load('alerts')

@flow
def etl_flow_with_alerts(date: str):
    try:
        return etl_flow(date)
    except Exception as e:
        slack.notify(f':rotating_light: ETL failed for {date}: {e}')
        raise
```
Notes
- Prefer flow‑level failure hooks (State Handlers) for broader coverage

---

Exercise 3 — Parameters and schedule
```python
# Using Prefect deployments (CLI)
# 1) prefect deployment build etl.py:etl_flow -n etl-daily -p date
# 2) prefect deployment apply etl_flow-deployment.yaml
# 3) prefect schedule create -n daily --cron "0 2 * * *" --timezone "UTC" --deployment etl-daily
```
Guidance
- Use Blocks for secrets (DB creds, API keys) and storage (S3/GCS)
- Keep tasks idempotent; re‑runs should not double‑load
