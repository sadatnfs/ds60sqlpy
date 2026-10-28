# dbt-025: explained reference

Recover a data product through explicit accepted versions and a tested pointer mechanism.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect both states

Record what changed and what remained accepted. This supports a targeted recovery instead of a broad destructive reset.

**Expected:** Their different values are explicit.

## 2. Commit an accepted change

Verify the candidate first, then switch an identified pointer. Keep the previous version for a declared rollback period.

**Expected:** The new accepted view is visible afterward.

## 3. Handle an uncertain response

Read the accepted pointer and transaction evidence. Blindly repeating a non-idempotent action can create additional side effects.

**Expected:** The response reconciles the intended version before retry.

## 4. Restore compatible components

Restore a coherent accepted bundle and verify its consumer behavior. A stale model may not accept a newly changed feature schema.

**Expected:** It includes schema, features, model and interface versions.

## 5. Bound retention

Preserve required rollback and audit evidence, then remove only owned expired artifacts under the approved policy. Do not use a global prune as incident diagnosis.

**Expected:** Ownership and retention rules are explicit.

## 6. Separate transaction scopes

Use an appropriate publication/reconciliation protocol across boundaries and test partial failures. Keep this local result as one component of the design.

**Expected:** It does not establish a distributed transaction.

## Complete reference

```python
"""dbt-025: complete local dbt project investigation."""

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


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "candidate": "{{ config(materialized='table') }} select 1 as version, 42 as value"
            },
        )
        invoke(p, "build")
        with duckdb.connect(str(p / "warehouse.duckdb")) as c:
            c.execute("create schema published")
            c.execute("create table published.release_one as select * from candidate")
            c.execute(
                "create view published.current_product as select * from published.release_one"
            )
            c.execute("begin")
            c.execute(
                "create or replace view published.current_product as "
                "select 2 as version, 99 as "
                "value"
            )
            assert c.execute("select value from published.current_product").fetchone() == (99,)
            c.execute("rollback")
            assert c.execute("select version,value from published.current_product").fetchone() == (
                1,
                42,
            )
        return {"transactional_pointer_rollback": True, "retained_release": [1, 42]}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={"candidate": "{{ config(materialized='table') }} select 1 as id, 42 as value"},
        )
        invoke(p, "build")
        with duckdb.connect(str(p / "warehouse.duckdb")) as c:
            c.execute("create table accepted_release as select * from candidate")
        (p / "models/candidate.sql").write_text(
            "{{ config(materialized='table') }} select 1 as id, 99 as value"
        )
        (p / "tests").mkdir()
        (p / "tests/value_policy.sql").write_text(
            "select * from {{ ref('candidate') }} where value > 50"
        )
        invoke(p, "build", succeeds=False)
        assert rows(p, "select value from candidate") == [(99,)]
        assert rows(p, "select value from accepted_release") == [(42,)]
        return {"candidate_rejected": 99, "accepted_release_unchanged": 42}


def main():
    print(example_one())
    print(example_two())
    print("dbt-025 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Recover a data product through explicit accepted versions and a tested pointer mechanism. Demonstrate a failed candidate and a reversible local promotion, then describe which distributed or operational guarantees still need separate implementation and qualification.
