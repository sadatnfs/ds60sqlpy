# dbt-005: explained reference

Define and test a source freshness policy with an explicit clock and response.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the threshold

The outcome changes because the policy changed. Document who accepts that age and what decisions use the data.

**Expected:** A two-day-old source can pass that revised policy.

## 2. Use a future timestamp

Reject or investigate impossible future timestamps within a declared skew tolerance. A negative age is not evidence of a healthy ingestion process.

**Expected:** The answer calls for a separate future-time validation.

## 3. Separate event and load time

Check event-time coverage separately when the consumer needs a recent event window. Late arrivals can be valid under the ingestion contract.

**Expected:** Fresh ingestion does not imply recent event coverage.

## 4. Inspect the artifact

Record the invocation and exact threshold with the result. A status without its policy is difficult to interpret.

**Expected:** The source identifier and status are retained.

## 5. Test partial ingestion

Use expected partitions, counts, batch manifests or other source-specific reconciliation. Combine independent dimensions of reliability.

**Expected:** The answer names a coverage or batch-integrity check.

## 6. Define an action

For a critical feature, the consumer might refuse publication or use an explicitly valid older model/input. Record the degraded state rather than silently using stale values.

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

Define and test a source freshness policy with an explicit clock and response. Pair it with batch completeness and time-coverage checks appropriate to the consumer. Keep the local fixture evidence separate from claims about an actual upstream service.
