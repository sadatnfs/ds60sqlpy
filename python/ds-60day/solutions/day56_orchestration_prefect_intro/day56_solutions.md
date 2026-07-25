# Day 56 — Solutions: Orchestration with Prefect 3

We convert a small offline ETL job into a Prefect 3 flow, add retries and a local
failure hook, and serve it from a self-hosted local scheduler.

Contents
- Exercise 1: Convert ETL to Prefect flow
- Exercise 2: Add retries and a local failure hook
- Exercise 3: Parameterize date and schedule daily

---

Exercise 1 — Flow and tasks
```python
from datetime import date
from typing import TypedDict

from prefect import flow, get_run_logger, task


class ExtractedData(TypedDict):
    run_date: str
    values: list[int]


@task(retries=2, retry_delay_seconds=1)
def extract(run_date: str) -> ExtractedData:
    logger = get_run_logger()
    logger.info("Extracting the local sample for %s", run_date)
    return {"run_date": run_date, "values": [3, 1, 4, 1, 5]}


@task
def transform(data: ExtractedData) -> ExtractedData:
    return {**data, "values": sorted(set(data["values"]))}


@task
def load(data: ExtractedData) -> dict[str, int | str]:
    # A real loader would perform an idempotent upsert. This offline example
    # returns a summary and writes no files or remote data.
    return {
        "run_date": data["run_date"],
        "loaded_rows": len(data["values"]),
    }


@flow(name="etl-daily")
def etl_flow(run_date: str | None = None) -> dict[str, int | str]:
    effective_date = run_date or date.today().isoformat()
    raw = extract(effective_date)
    clean = transform(raw)
    return load(clean)


if __name__ == "__main__":
    print(etl_flow(run_date="2026-01-15"))
```
This one-off run is local and deterministic. It needs no Prefect Cloud account,
API key, external API, or network download after the dependency is installed.

Exercise 2 — Retries and a local failure hook
```python
from prefect.logging.loggers import flow_run_logger


def log_failure(flow, flow_run, state) -> None:
    logger = flow_run_logger(flow_run, flow)
    logger.error(
        "Flow %s entered %s: %s",
        flow_run.name,
        state.name,
        state.message,
    )


@flow(name="monitored-etl", on_failure=[log_failure])
def monitored_etl(run_date: str | None = None) -> dict[str, int | str]:
    return etl_flow(run_date=run_date)
```
Notes
- The `extract` task retries before a final task or flow failure is recorded
- Hooks run in the flow process and are best-effort; use a Prefect Automation
  when delivery must survive a worker crash
- `get_run_logger()` has no active run context inside a hook, so use
  `flow_run_logger()` there
- Slack is deliberately not imported: it requires the separately installed
  `prefect-slack` integration, a stored webhook secret, and network access

---

Exercise 3 — Parameters and a local daily schedule
```python
def serve_daily() -> None:
    # serve() creates a deployment and then blocks while listening for work.
    etl_flow.serve(
        name="etl-daily-local",
        cron="0 2 * * *",
        pause_on_shutdown=True,
    )


# Put the function above in etl_schedule.py, then uncomment for scheduled use:
# if __name__ == "__main__":
#     serve_daily()
```
Run the scheduler entirely on the local machine:
```text
# Terminal 1: start the open-source Prefect API/UI.
prefect server start

# Run once so every Prefect process uses that local API profile.
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"

# Terminal 2: keep the serving process running.
python etl_schedule.py
```
These commands are the same in the VS Code terminal on Windows, macOS, and
Linux. The local server uses SQLite by default. No Prefect Cloud login is
required. Stop the serving process with Ctrl+C; with
`pause_on_shutdown=True`, Prefect pauses its schedule.

Guidance
- `flow.serve(..., cron=...)` is the Prefect 3 static-process deployment pattern;
  the old Prefect 2 `deployment build/apply` commands do not apply
- The serving process must remain running to execute scheduled work
- Resolve `run_date` when each run starts, so a daily deployment does not reuse
  a date captured when it was registered
- Keep tasks idempotent; retries and re-runs must not double-load data
