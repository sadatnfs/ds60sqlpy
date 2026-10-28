# dbt-014: explained reference

Build documentation that joins observed structure with authored meaning and ownership.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Write a complete definition

State which records contribute, the grouping key, time boundary and unit. Keep the definition aligned with the model and tests.

**Expected:** A reader can interpret the quantity without guessing.

## 2. Add a downstream consumer

The exposure is a maintained declaration. Validate actual consumer behavior separately and update ownership when responsibility changes.

**Expected:** The new edge appears in the manifest.

## 3. Inspect physical type

Generate docs against the intended materialized state and retain its invocation/source context. A stale catalog can describe an older deployment.

**Expected:** It matches the built database representation.

## 4. Find an undocumented field

Add a semantic review gate appropriate to the project. Avoid automatically filling descriptions with generic repeated text.

**Expected:** The documentation gap remains visible.

## 5. Separate lineage from execution

Combine lineage with actual deployment and service evidence when making operational claims. Keep those evidence sources separately identifiable.

**Expected:** It cannot prove the external dashboard ran successfully.

## 6. Export a compact review record

Keep a bounded summary with links or hashes identifying the underlying artifacts. The full files remain the detailed evidence in a durable project.

**Expected:** The record contains meaning, ownership and dependency identifiers.

## Complete reference

```python
"""dbt-014: actual local dbt and DuckDB reference."""

import json
import os
import tempfile
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


def example_one():
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {
                    "name": "mart",
                    "description": "One total for this synthetic fixture.",
                    "columns": [{"name": "total", "description": "Sum of declared amount values."}],
                }
            ],
            "exposures": [
                {
                    "name": "decision_report",
                    "type": "dashboard",
                    "depends_on": ["ref('mart')"],
                    "owner": {"name": "Classroom team"},
                }
            ],
        }
        p = project(
            d,
            models={"mart": "select sum(amount)::bigint as total from {{ ref('orders') }}"},
            seeds={"orders": "id,amount\n1,5\n2,7\n"},
            schema=schema,
        )
        invoke(p, "build")
        invoke(p, "docs", "generate")
        catalog = artifact(p, "catalog.json")
        manifest = artifact(p, "manifest.json")
        assert "model.classroom.mart" in catalog["nodes"]
        assert "total" in catalog["nodes"]["model.classroom.mart"]["columns"]
        exposure = manifest["exposures"]["exposure.classroom.decision_report"]
        assert exposure["depends_on"]["nodes"] == ["model.classroom.mart"]
        return {"catalog_column": "total", "exposure_dependency": "mart"}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(d, models={"answer": "select 42::integer as answer"})
        invoke(p, "build")
        invoke(p, "docs", "generate")
        manifest = artifact(p, "manifest.json")
        catalog = artifact(p, "catalog.json")
        assert manifest["nodes"]["model.classroom.answer"]["description"] == ""
        assert (
            catalog["nodes"]["model.classroom.answer"]["columns"]["answer"]["type"].upper()
            == "INTEGER"
        )
        return {"physical_type_known": True, "business_description_missing": True}


def main():
    print(example_one())
    print(example_two())
    print("dbt-014 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Build documentation that joins observed structure with authored meaning and ownership. Review a consumer's dependency and record which claims are declarations versus runtime evidence. This creates a useful handoff for analysts, data scientists and operators.
