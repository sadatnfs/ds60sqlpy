# dbt-005: explained reference

Define and test a source freshness policy with an explicit clock and response.

The reference declares a `landing.events` source with `loaded_at_field` and a one-hour `error_after`, seeds a single timestamp and runs `dbt source freshness`. It proves the policy compares that column with the current clock, not that the upstream system actually delivered on time. See [how these answers are laid out](../STUDY-GUIDE.md#answers-and-references).


## 1. Change the threshold

The outcome changes because the policy changed. Document who accepts that age and what decisions use the data.

**Why it holds here:** The stale fixture writes loaded_at as now minus two days while error_after is one hour, so sources.json reports error. Raising error_after to three days moves the boundary past the fixture's 48 hour age without touching the data.

**Plausible wrong approach:** Editing the seed so loaded_at becomes recent also turns the status to pass, but it hides the real lag instead of recording a reviewed tolerance for the landing.events source.

**How to verify:** Rerun seed and source freshness with count 3 and period day, then read `results[0].status` from target/sources.json; it should be pass for the two-day stamp and still error for a four-day stamp.

**Expected:** A two-day-old source can pass that revised policy.

## 2. Use a future timestamp

Reject or investigate impossible future timestamps within a declared skew tolerance. A negative age is not evidence of a healthy ingestion process.

**Why it holds here:** dbt computes age as the invocation time minus max(loaded_at). A stamp one day ahead yields a negative age, which is always below a one hour error_after, so the check passes for a row that cannot be real.

**Plausible wrong approach:** Taking the absolute value of the age would convert a clock error into an apparently stale source and send the investigation toward ingestion delay instead of producer clock skew.

**How to verify:** Seed raw_events with now plus one day and run source freshness; expect pass because the age is negative. Then add a singular test such as select * from raw_events where loaded_at > now() + interval 5 minute and confirm it returns that row.

**Expected:** The answer calls for a separate future-time validation.

## 3. Separate event and load time

Check event-time coverage separately when the consumer needs a recent event window. Late arrivals can be valid under the ingestion contract.

**Why it holds here:** The freshness block only reads loaded_at, the ingestion stamp. A row whose business event happened last month but landed a minute ago is fresh under this contract while being useless to a consumer that needs yesterday's events.

**Plausible wrong approach:** Pointing loaded_at_field at the event timestamp instead would fail legitimate late arrivals and stop measuring whether the loader itself is running.

**How to verify:** Add an event_at column dated 30 days back with loaded_at set to now; source freshness reports pass, and a separate query on max(event_at) shows the 30 day gap that the consumer actually cares about.

**Expected:** Fresh ingestion does not imply recent event coverage.

## 4. Inspect the artifact

Record the invocation and exact threshold with the result. A status without its policy is difficult to interpret.

**Why it holds here:** sources.json holds one result per tested source table with unique_id source.classroom.landing.events, its status, max_loaded_at and the criteria that were applied. That pairing of status with threshold is what makes the record interpretable later.

**Plausible wrong approach:** Reading run_results.json instead finds nothing about freshness, because the reference never runs the model in that invocation, and a missing source entry is easy to misread as a pass.

**How to verify:** Load target/sources.json with json.loads and print `results[0]['unique_id']`, `['status']` and `['criteria']`; expect the landing.events identifier, error for the stale case and error_after of 1 hour.

**Expected:** The source identifier and status are retained.

## 5. Test partial ingestion

Use expected partitions, counts, batch manifests or other source-specific reconciliation. Combine independent dimensions of reliability.

**Why it holds here:** Freshness only asks whether the newest loaded_at is recent. If a loader writes one row of a thousand row batch and then crashes, max(loaded_at) is current and the check passes on an incomplete table.

**Plausible wrong approach:** Adding a row-count threshold to the freshness block does not exist as a dbt freshness option, and a generic minimum count would still accept a partial batch that happens to exceed it.

**How to verify:** Seed raw_events with one fresh row and compare its count to an expected manifest value of, say, 1000 using a singular test; freshness passes while the reconciliation test fails, showing the two checks are independent.

**Expected:** The answer names a coverage or batch-integrity check.

## 6. Define an action

For a critical feature, the consumer might refuse publication or use an explicitly valid older model/input. Record the degraded state rather than silently using stale values.

**Why it holds here:** The reference shows dbt source freshness returning a nonzero result for the stale case, so an orchestrator can branch on it. The policy must say which branch runs: stop the downstream build, serve the last accepted version, or page an owner.

**Plausible wrong approach:** Wrapping the freshness command so its failure is ignored keeps the pipeline green but lets the events model publish two-day-old data as if it were current.

**How to verify:** In the stale case the invoke call asserts result.success is False; an orchestration test should show the downstream build step is skipped or marked degraded when that happens.

**Expected:** The action distinguishes blocking, fallback and investigation.

## Complete reference

```python
"""dbt-005: actual local dbt and DuckDB reference."""

import json
import os
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml


def project(directory, models=None, seeds=None, schema=None, snapshots=None, macros=None):
    os.environ["DBT_SEND_ANONYMOUS_USAGE_STATS"] = "false"
    os.environ["DBT_USE_COLORS"] = "false"
    os.environ["DO_NOT_TRACK"] = "true"
    root = Path(directory) / "project"
    root.mkdir(parents=True)
    for folder in ("models", "seeds", "snapshots", "macros"):
        (root / folder).mkdir()
    config = {
        "name": "classroom",
        "version": "1.0",
        "config-version": 2,
        "profile": "classroom",
        "model-paths": ["models"],
        "seed-paths": ["seeds"],
        "snapshot-paths": ["snapshots"],
        "macro-paths": ["macros"],
    }
    (root / "dbt_project.yml").write_text(yaml.safe_dump(config))
    output = {
        "type": "duckdb",
        "path": str(root / "warehouse.duckdb"),
        "schema": "main",
        "threads": 1,
        "settings": {"threads": 2, "memory_limit": "256MB"},
    }
    (root / "profiles.yml").write_text(
        yaml.safe_dump({"classroom": {"target": "dev", "outputs": {"dev": output}}})
    )
    for name, sql in (models or {"answer": "select 42::integer as answer"}).items():
        (root / "models" / (name + ".sql")).write_text(sql)
    for name, csv in (seeds or {}).items():
        (root / "seeds" / (name + ".csv")).write_text(csv)
    if schema:
        (root / "models/schema.yml").write_text(yaml.safe_dump({"version": 2, **schema}))
    if snapshots:
        (root / "snapshots/snapshots.yml").write_text(
            yaml.safe_dump({"version": 2, "snapshots": snapshots})
        )
    for name, sql in (macros or {}).items():
        (root / "macros" / (name + ".sql")).write_text(sql)
    return root


def invoke(root, *arguments, succeeds=True):
    from dbt.cli.main import dbtRunner

    result = dbtRunner().invoke(
        [
            "--quiet",
            "--no-use-colors",
            "--no-send-anonymous-usage-stats",
            *arguments,
            "--project-dir",
            str(root),
            "--profiles-dir",
            str(root),
            "--no-partial-parse",
        ]
    )
    if succeeds:
        assert result.success, str(result.exception)
    else:
        assert not result.success, "The deliberately invalid fixture was accepted."
    return result


def artifact(root, name):
    return json.loads((root / "target" / name).read_text())


def freshness_case(stale):
    with tempfile.TemporaryDirectory() as d:
        stamp = datetime.now(UTC) - timedelta(days=2 if stale else 0)
        schema = {
            "sources": [
                {
                    "name": "landing",
                    "schema": "main",
                    "tables": [
                        {
                            "name": "events",
                            "identifier": "raw_events",
                            "config": {
                                "loaded_at_field": "loaded_at",
                                "freshness": {"error_after": {"count": 1, "period": "hour"}},
                            },
                        }
                    ],
                }
            ]
        }
        p = project(
            d,
            models={"events": "select * from {{ source('landing', 'events') }}"},
            seeds={"raw_events": f"id,loaded_at\n1,{stamp.isoformat()}\n"},
            schema=schema,
        )
        invoke(p, "seed")
        invoke(p, "source", "freshness", succeeds=not stale)
        status = artifact(p, "sources.json")["results"][0]["status"]
        assert status == ("error" if stale else "pass"), status
        return {"stale": stale, "status": status}


def example_one():
    return freshness_case(False)


def example_two():
    return freshness_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-005 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Pair it with batch completeness and time-coverage checks appropriate to the consumer. Keep the local fixture evidence separate from claims about an actual upstream service.
