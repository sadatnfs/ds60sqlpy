# dbt-012: explained reference

Manage a semantic model change with explicit consumer versioning.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Pin a consumer

Pinning defines the chosen contract. It also creates a responsibility to review and migrate deliberately when the old version is retired.

**Expected:** It returns 100.

## 2. Change latest selection

The behavior is controlled by configuration, not a universal semantic ordering. Keep release and consumer expectations explicit.

**Expected:** The unversioned consumer follows that declaration.

## 3. Add a type-compatible defect

Add semantic reconciliation and consumer-level checks. A feature can remain Float64 while changing units or time windows.

**Expected:** Schema checks alone can still pass.

## 4. Design a model migration

Evaluate or retrain under the new feature contract, compare decisions and retain a rollback-compatible bundle. Do not change the upstream alias silently.

**Expected:** The answer includes feature version and validation.

## 5. Inspect lineage

Use lineage to identify affected consumers. It does not itself prove that the calculation answers their intended question.

**Expected:** It points to the declared base model.

## 6. Retain rollback information

Retain the implementation, dependency versions, schema/semantic definition and accepted evidence. A rollback should restore a coherent bundle.

**Expected:** They identify source, model version and validated data/interface.

## Complete reference

```python
"""dbt-012: actual local dbt and DuckDB reference."""

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
        schema = {
            "models": [
                {
                    "name": "customer_value",
                    "latest_version": 2,
                    "versions": [
                        {"v": 1, "defined_in": "customer_value_v1"},
                        {"v": 2, "defined_in": "customer_value_v2"},
                    ],
                }
            ]
        }
        p = project(
            d,
            models={
                "customer_value_v1": "select 100 as value",
                "customer_value_v2": "select 80 as value",
                "stable_consumer": "select value from {{ ref('customer_value', version=1) }}",
                "latest_consumer": "select value from {{ ref('customer_value') }}",
            },
            schema=schema,
        )
        invoke(p, "build")
        assert rows(p, "select value from stable_consumer") == [(100,)]
        assert rows(p, "select value from latest_consumer") == [(80,)]
        return {"explicit_v1": 100, "latest_v2": 80}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "base": "select 100 as gross, 20 as returns",
                "net": "select gross-returns as net from {{ ref('base') }}",
            },
        )
        invoke(p, "build")
        assert rows(p, "select net from net") == [(80,)]
        manifest = artifact(p, "manifest.json")
        assert manifest["nodes"]["model.classroom.net"]["depends_on"]["nodes"] == [
            "model.classroom.base"
        ]
        return {"semantic_change": "gross to net", "net": 80, "dependency_recorded": True}


def main():
    print(example_one())
    print(example_two())
    print("dbt-012 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Manage a semantic model change with explicit consumer versioning. Demonstrate the changed result, identify affected consumers and define validation and rollback requirements. Carry the same discipline into ML feature and model artifact versions.
