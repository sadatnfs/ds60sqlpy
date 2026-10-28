# dbt-021: explained reference

Implement a reproducible reduced CI workflow with explicit selection, baseline and ownership.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect selected resources

Keep that inventory with the result. An empty or incomplete selection cannot justify acceptance merely because the command exits successfully.

**Expected:** The changed child and required tests are visible.

## 2. Introduce a semantic failure

Add a known reconciliation or domain condition. A reduced suite is useful only if its assertions cover the relevant behavior.

**Expected:** An independent semantic test is needed to detect it.

## 3. Verify isolation

Use a dedicated CI schema/database and approved access. Do not redirect a failing exercise to a shared valuable environment.

**Expected:** Its content remains unchanged.

## 4. Review a shared macro change

Inspect graph expansion and run broader checks when needed. Explain the reason rather than treating slim selection as an unconditional policy.

**Expected:** The decision includes downstream effects.

## 5. Retain invocation evidence

Keep the selected resources, command, target, baseline manifest and actual outcomes. Avoid attaching old successful artifacts to changed source.

**Expected:** The result can be traced to exact inputs.

## 6. Define failure handling

Retain diagnostics and cleanup only owned CI resources. Repair the defect and generate new evidence before promotion.

**Expected:** It cannot replace the accepted product.

## Complete reference

```python
"""dbt-021: complete local dbt project investigation."""

import json
import os
import shutil
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


def targets(p):
    config = yaml.safe_load((p / "profiles.yml").read_text())
    original = config["classroom"]["outputs"]["dev"]
    config["classroom"]["outputs"] = {
        name: {**original, "schema": name} for name in ("dev", "prod")
    }
    (p / "profiles.yml").write_text(yaml.safe_dump(config))


def ci_case(bad):
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {"name": "child", "columns": [{"name": "id", "data_tests": ["unique", "not_null"]}]}
            ]
        }
        p = project(
            d,
            models={"base": "select 1 as id", "child": "select id from {{ ref('base') }}"},
            schema=schema,
        )
        targets(p)
        invoke(p, "build", "--target", "prod")
        state = p / "state"
        state.mkdir()
        shutil.copyfile(p / "target/manifest.json", state / "manifest.json")
        sql = "select id from {{ ref('base') }}" + (
            " union all select id from {{ ref('base') }}" if bad else " where id > 0"
        )
        (p / "models/child.sql").write_text(sql)
        invoke(
            p,
            "build",
            "--target",
            "dev",
            "--select",
            "state:modified+",
            "--defer",
            "--state",
            str(state),
            succeeds=not bad,
        )
        assert rows(p, "select count(*) from prod.child") == [(1,)]
        statuses = [r["status"] for r in artifact(p, "run_results.json")["results"]]
        assert ("fail" in statuses) is bad
        return {"bad_change": bad, "protected_baseline_rows": 1, "statuses": statuses}


def example_one():
    return ci_case(False)


def example_two():
    return ci_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-021 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Implement a reproducible reduced CI workflow with explicit selection, baseline and ownership. Demonstrate that a meaningful defect fails and that accepted data remains intact. Explain when the change requires a broader validation scope.
