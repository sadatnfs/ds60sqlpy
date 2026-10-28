# dbt-010: explained reference

Explain what a snapshot actually observed and what it cannot reconstruct.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect a closed version

Retain both versions and their interval meaning. A current-only query is appropriate for a different question than a historical reconstruction.

**Expected:** The changed version has a non-null dbt_valid_to.

## 2. Change a tracked column

Review whether the attribute represents meaningful state or noisy metadata. Tracking every field can produce unnecessary history churn.

**Expected:** Its changes can create new versions under the revised policy.

## 3. Explain unobserved changes

Use a source change log or another stronger history mechanism when the intermediate state matters. Snapshots cannot reconstruct unobserved facts.

**Expected:** The intermediate state may never appear in the snapshot.

## 4. Compare deletion policies

Choose a policy that distinguishes genuine deletion from incomplete ingestion. A partial load should not automatically invalidate valid entities.

**Expected:** A formerly current record can remain open.

## 5. Review temporal meaning

For event-effective analyses, preserve source effective/known times and define a temporal model. Do not infer them from snapshot timing alone.

**Expected:** The explanation keeps the clocks separate.

## 6. Verify identity

Multiple source rows for one snapshot key need a deterministic, justified resolution or a failure. Otherwise the historical record becomes ambiguous.

**Expected:** Conflicting identity is detected before trusting history.

## Complete reference

```python
"""dbt-010: actual local dbt and DuckDB reference."""

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


def relation(root, unique_id):
    return artifact(root, "manifest.json")["nodes"][unique_id]["relation_name"]


def snapshot_case(delete):
    with tempfile.TemporaryDirectory() as d:
        snapshots = [
            {
                "name": "customer_history",
                "relation": "ref('customers')",
                "config": {
                    "schema": "history",
                    "unique_key": "customer_id",
                    "strategy": "check",
                    "check_cols": ["region"],
                    "hard_deletes": "invalidate",
                },
            }
        ]
        p = project(
            d,
            models={"dummy": "select 1 as value"},
            seeds={"customers": "customer_id,region\n1,north\n2,south\n"},
            snapshots=snapshots,
        )
        invoke(p, "seed")
        invoke(p, "snapshot")
        (p / "seeds/customers.csv").write_text(
            "customer_id,region\n1,west\n" if delete else "customer_id,region\n1,west\n2,south\n"
        )
        invoke(p, "seed")
        invoke(p, "snapshot")
        table = relation(p, "snapshot.classroom.customer_history")
        assert rows(p, f"select count(*) from {table}") == [(3,)]
        active = rows(
            p,
            f"select customer_id,region from {table} "
            "where dbt_valid_to is null order by customer_id",
        )
        assert active == ([(1, "west")] if delete else [(1, "west"), (2, "south")])
        return {"history_rows": 3, "active_rows": active, "delete_invalidation": delete}


def example_one():
    return snapshot_case(False)


def example_two():
    return snapshot_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-010 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Explain what a snapshot actually observed and what it cannot reconstruct. Verify current and closed versions, define deletion handling, and preserve identity and clock contracts before using the history for features or analysis.
