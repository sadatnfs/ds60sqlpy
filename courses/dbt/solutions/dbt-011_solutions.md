# dbt-011: explained reference

Define a model schema contract and verify both accepted and rejected changes.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Remove a declared column

A consumer cannot safely assume the missing field exists. Treat removal as a compatibility change rather than silently updating the contract.

**Expected:** The enforced contract rejects the mismatch.

## 2. Add a new output field

Review the consumer interface and update/version the contract deliberately. Do not assume additional fields are harmless in every downstream system.

**Expected:** The schema change is explicit.

## 3. Test a null identifier

Keep data tests as appropriate and inspect adapter constraint support. A declared constraint should not be advertised as enforced without actual evidence.

**Expected:** The database/contract path reports the violation when supported.

## 4. Distinguish failure stages

A schema preflight may reject replacement earlier, while a data test can fail after materialization. Design publication around the actual sequence.

**Expected:** The two cases leave different observed state.

## 5. Check consumer assumptions

Add semantic contracts and tests. Schema enforcement does not establish that amount uses the expected currency or period.

**Expected:** They include grain, units, time and missingness.

## 6. Plan an incompatible change

Publish a new version with its definition, compare results, migrate consumers and retain rollback evidence. The next lesson makes version selection explicit.

**Expected:** It uses an explicit version and consumer migration.

## Complete reference

```python
"""dbt-011: actual local dbt and DuckDB reference."""

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
        schema = {
            "models": [
                {
                    "name": "contracted",
                    "config": {"materialized": "table", "contract": {"enforced": True}},
                    "columns": [
                        {
                            "name": "id",
                            "data_type": "integer",
                            "constraints": [{"type": "not_null"}],
                        },
                        {"name": "amount", "data_type": "bigint"},
                    ],
                }
            ]
        }
        p = project(
            d, models={"contracted": "select 1::integer as id, 42::bigint as amount"}, schema=schema
        )
        invoke(p, "build")
        assert rows(p, "select id,amount from contracted") == [(1, 42)]
        return {"declared_columns": ["id:integer", "amount:bigint"], "row": [1, 42]}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {
                    "name": "contracted",
                    "config": {"materialized": "table", "contract": {"enforced": True}},
                    "columns": [
                        {"name": "id", "data_type": "integer"},
                        {"name": "amount", "data_type": "bigint"},
                    ],
                }
            ]
        }
        p = project(
            d, models={"contracted": "select 1::integer as id, 42::bigint as amount"}, schema=schema
        )
        invoke(p, "build")
        (p / "models/contracted.sql").write_text(
            "select 1::integer as id, 'bad'::varchar as amount"
        )
        invoke(p, "run", succeeds=False)
        assert rows(p, "select amount from contracted") == [(42,)]
        return {
            "incompatible_schema_rejected": True,
            "previous_relation_retained_for_this_failure": True,
        }


def main():
    print(example_one())
    print(example_two())
    print("dbt-011 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Define a model schema contract and verify both accepted and rejected changes. Keep the observed failure timing separate from broader transaction claims, and combine structural compatibility with semantic and publication checks.
