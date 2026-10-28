# dbt-022: explained reference

Diagnose failures using the layer that actually rejected the work.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Classify the first failure

Inspect the actual relation schema and generated column name. Changing package configuration would not address this specific defect.

**Expected:** It is database binding/execution.

## 2. Create a template error

The failure concerns definition resolution before the final SQL can be evaluated. Keep the layers separate in the diagnostic record.

**Expected:** Compilation fails earlier.

## 3. Preserve the wrong result

Retain a bounded source/result record in an owned environment. It helps prove what changed and prevents a vague claim that the previous code merely failed.

**Expected:** The materialized 24 remains evidence of the defect.

## 4. Repair one cause

Keep the same fixture and oracle while applying the correction. A new unrelated dataset would make the before/after comparison less informative.

**Expected:** The independent total becomes 12 and the test passes.

## 5. Avoid a circular oracle

Use hand calculation, a different implementation or a separately established contract. Record which assumptions the oracle itself depends on.

**Expected:** The expected value is independently justified.

## 6. Write an incident note

Include the invocation and resource identities without exposing credentials. Distinguish confirmed causes from hypotheses that still need testing.

**Expected:** The note is specific and reproducible.

## Complete reference

```python
"""dbt-022: complete local dbt project investigation."""

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
            models={"bad": "select missing_column from {{ ref('orders') }}"},
            seeds={"orders": "id,amount\n1,5\n"},
        )
        invoke(p, "seed")
        invoke(p, "compile")
        assert (p / "target/compiled/classroom/models/bad.sql").exists()
        invoke(p, "run", succeeds=False)
        assert artifact(p, "run_results.json")["results"][0]["status"] == "error"
        return {"template_compiled": True, "database_binding_rejected": True}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={"total": "select sum(amount)*2 as amount from {{ ref('orders') }}"},
            seeds={"orders": "id,amount\n1,5\n2,7\n"},
        )
        (p / "tests").mkdir()
        (p / "tests/reconcile.sql").write_text(
            "select * from {{ ref('total') }} where amount != 12"
        )
        invoke(p, "build", succeeds=False)
        assert rows(p, "select amount from total") == [(24,)]
        assert "fail" in [r["status"] for r in artifact(p, "run_results.json")["results"]]
        return {"sql_executed": True, "wrong_quantity": 24, "independent_expected_quantity": 12}


def main():
    print(example_one())
    print(example_two())
    print("dbt-022 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Diagnose failures using the layer that actually rejected the work. Preserve bounded before/after evidence and verify a focused correction with an independent oracle. Apply the same method to feature and model pipelines where an apparently healthy process can still produce an invalid product.
