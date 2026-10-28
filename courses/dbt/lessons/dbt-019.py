"""dbt-019: worked starting point; complete the guide's six changes."""

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


def targets(p):
    config = yaml.safe_load((p / "profiles.yml").read_text())
    original = config["classroom"]["outputs"]["dev"]
    config["classroom"]["outputs"] = {
        name: {**original, "schema": name} for name in ("dev", "prod")
    }
    (p / "profiles.yml").write_text(yaml.safe_dump(config))


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d, models={"answer": "select '{{ target.name }}' as environment, 42::integer as answer"}
        )
        targets(p)
        invoke(p, "build", "--target", "dev")
        invoke(p, "build", "--target", "prod")
        assert rows(p, "select environment,answer from dev.answer") == [("dev", 42)]
        assert rows(p, "select environment,answer from prod.answer") == [("prod", 42)]
        return {"same_file_owned_test_database": True, "separate_schemas": ["dev", "prod"]}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Identify the exact file and schema selected for each target.
# TODO 2: Return the same numeric result in both targets.
# TODO 3: Select another default target but still pass --target explicitly.
# TODO 4: Remove an output and attempt to select it.
# TODO 5: Describe how real credentials should be supplied.
# TODO 6: Explain what two schemas in one file do not establish.
