# dbt-001: explained reference

Build and inspect a local dbt project through its real adapter.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Locate the project

The model states SQL logic, project configuration defines resource locations, and the profile chooses the database. Keeping these roles separate prevents accidental environment assumptions.

**Expected:** Each file has a distinct responsibility.

## 2. Change the expression

The source expression changes while the result remains equal. That is a concrete example of why source identity and result equality are different evidence.

**Expected:** The database still returns 42.

## 3. Introduce invalid SQL

Do not continue publication after a failed command. Preserve the diagnostic and distinguish parsing/template errors from SQL execution errors.

**Expected:** Execution reports failure with a database diagnostic.

## 4. Inspect the manifest

The manifest is a structured graph artifact, not merely a log. It can support lineage and selection, but does not prove data quality by itself.

**Expected:** They identify the project node and source.

## 5. Inspect run results

The result concerns this invocation and selected resources. A prior successful artifact should not be reused as evidence for changed source.

**Expected:** A successful model result is recorded.

## 6. State the runtime boundary

For a durable external project, prepare an owned work directory and explicit database/artifact storage. Do not assume a temporary classroom path is a deployment.

**Expected:** Source and bounded results remain; scratch project databases do not.

## Complete reference

```python
"""dbt-001: actual local dbt and DuckDB reference."""

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
        p = project(d)
        invoke(p, "parse")
        manifest = artifact(p, "manifest.json")
        assert "model.classroom.answer" in manifest["nodes"]
        invoke(p, "build")
        assert rows(p, "select answer from answer") == [(42,)]
        assert artifact(p, "run_results.json")["results"][0]["status"] == "success"
        return {"parsed_model": "answer", "actual_database_value": 42}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(d, models={"answer": "select 6 * 7 as answer"})
        invoke(p, "compile")
        compiled = (p / "target/compiled/classroom/models/answer.sql").read_text()
        assert "6 * 7" in compiled
        assert (
            not (p / "warehouse.duckdb").exists()
            or rows(p, "select count(*) from information_schema.tables where table_name='answer'")[
                0
            ][0]
            == 0
        )
        invoke(p, "run")
        assert rows(p, "select answer from answer") == [(42,)]
        return {"compiled_sql": compiled.strip(), "run_created_relation": True}


def main():
    print(example_one())
    print(example_two())
    print("dbt-001 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Build and inspect a local dbt project through its real adapter. Keep parsing, compilation, materialization and validation distinct. This gives you a reliable basis for the later incremental, contract and publication lessons without depending on a hosted warehouse.
