"""dbt-014: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Describe total with its grain, units and inclusion rule.
# TODO 2: Declare a second exposure with its owner and dependency.
# TODO 3: Read the catalog's type for a column.
# TODO 4: Create a model column without a description.
# TODO 5: Explain what an exposure cannot establish.
# TODO 6: Select useful metadata from the generated artifacts.
