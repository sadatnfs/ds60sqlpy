# dbt-017: explained reference

Produce a historical feature relation with explicit entity, time and version semantics.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add an unmatched request

Left-join selected results back to the request population and report missing-feature reasons. Do not drop difficult requests before evaluating a model.

**Expected:** The request is explicitly retained or counted as unmatched.

## 2. Change the availability clock

The result changes because the source history changed. Preserve that history/version when reporting a retrospective analysis.

**Expected:** It is eligible for cutoff 5.

## 3. Test equal cutoffs

The example uses <=. Some systems require a transaction or ingestion watermark that changes what equality means operationally.

**Expected:** Its treatment matches the documented inclusive rule.

## 4. Add version ties

Do not rely on accidental database ordering. Define an additional version identifier or fail ambiguous input.

**Expected:** A further deterministic authority rule or rejection is required.

## 5. Compare with a snapshot

Choose a source history mechanism that supports the desired retrospective question. Do not reinterpret snapshot observation time as business-effective time.

**Expected:** The answer distinguishes observed state from complete source history.

## 6. Validate with an oracle

Keep this independent fixture in regression tests. SQL execution success alone cannot identify a temporal leakage error.

**Expected:** The oracle returns 10 and 30.

## Complete reference

```python
"""dbt-017: actual local dbt and DuckDB reference."""

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


def temporal_case(available):
    with tempfile.TemporaryDirectory() as d:
        clause = "and f.known_at <= r.cutoff" if available else ""
        sql = (
            (
                "select request_id, value from (select "
                "r.request_id,f.value,row_number() over(partition by "
                "r.request_id order by f.event_at desc,f.known_at desc) as "
                "rank from {{ ref('requests') }} r join {{ ref('features') "
                "}} f on r.customer=f.customer and f.event_at<=r.cutoff "
            )
            + clause
            + ") where rank=1"
        )
        p = project(
            d,
            models={"training_features": sql},
            seeds={
                "requests": "request_id,customer,cutoff\n1,10,5\n2,10,9\n",
                "features": "customer,event_at,known_at,value\n10,2,3,10\n10,4,7,999\n10,8,8,30\n",
            },
        )
        invoke(p, "build")
        result = rows(p, "select request_id,value from training_features order by request_id")
        assert result == ([(1, 10), (2, 30)] if available else [(1, 999), (2, 30)])
        return {"availability_checked": available, "features": result}


def example_one():
    return temporal_case(True)


def example_two():
    return temporal_case(False)


def main():
    print(example_one())
    print(example_two())
    print("dbt-017 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Produce a historical feature relation with explicit entity, time and version semantics. Demonstrate a late-known counterexample and retain request coverage. This prepares the feature-store and ML engineering route to test actual retrieval against a meaningful temporal oracle.
