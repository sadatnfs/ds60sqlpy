# dbt-002: explained reference

Create a staging boundary with complete record accounting.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a valid row

The source and staged counts should both increase by one. Keep the identifier unique and verify the new row separately.

**Expected:** Accepted total becomes 24.

## 2. Add missing text

Keep a raw-is-null or blank indicator and a rejection reason. Treating all failed conversions alike can hide different operational problems.

**Expected:** The policy distinguishes missing from malformed.

## 3. Keep the source identity

Row identity supports diagnosis and later deduplication. A total without identifiers is insufficient to explain rejection.

**Expected:** Each accepted result can be traced to a raw record.

## 4. Check source coverage

The reconciliation fails if a row is counted twice or disappears. State classification order when duplicate and invalid conditions overlap.

**Expected:** Their sum equals the raw count under the fixture policy.

## 5. Choose a seed use case

Use seeds for small controlled fixtures or mappings. Production ingestion needs a separate reproducible source contract and operational process.

**Expected:** The answer distinguishes small reference data from ingestion.

## 6. Fail mandatory parsing

Use strict failure when invalid input must block the product. Keep the failed evidence and do not mistake a stopped run for data that never arrived.

**Expected:** The malformed fixture fails.

## Complete reference

```python
"""dbt-002: actual local dbt and DuckDB reference."""

import json
import os
import tempfile
from pathlib import Path

import duckdb
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


def rows(root, sql):
    with duckdb.connect(str(root / "warehouse.duckdb"), read_only=False) as connection:
        return connection.execute(sql).fetchall()


def artifact(root, name):
    return json.loads((root / "target" / name).read_text())


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "orders": (
                    "select id::integer as id, amount::integer as amount from "
                    "{{ ref('raw_orders') }}"
                )
            },
            seeds={"raw_orders": "id,amount\n1,5\n2,7\n3,9\n"},
        )
        invoke(p, "build")
        assert rows(p, "select count(*), sum(amount) from orders") == [(3, 21)]
        seed = artifact(p, "manifest.json")["nodes"]["seed.classroom.raw_orders"]
        assert seed["resource_type"] == "seed"
        return {"seed_rows": 3, "amount_total": 21}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "clean": (
                    "select id::integer as id, try_cast(amount as integer) as "
                    "amount from {{ ref('raw_orders') }} where try_cast(amount "
                    "as integer) is not null"
                )
            },
            seeds={"raw_orders": "id,amount\n1,5\n2,bad\n3,9\n"},
        )
        invoke(p, "build")
        assert rows(p, "select id, amount from clean order by id") == [(1, 5), (3, 9)]
        assert rows(p, "select count(*) from raw_orders") == [(3,)]
        assert rows(
            p, "select count(*) from raw_orders where try_cast(amount as integer) is null"
        ) == [(1,)]
        return {"accepted_rows": 2, "rejected_rows": 1, "raw_rows": 3}


def main():
    print(example_one())
    print(example_two())
    print("dbt-002 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Create a staging boundary with complete record accounting. State which invalid inputs block publication and which are quarantined, then test both paths using identified records. The same contract will later protect model features from silent data changes.
