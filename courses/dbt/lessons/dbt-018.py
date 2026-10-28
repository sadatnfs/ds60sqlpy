"""dbt-018: worked starting point; complete the guide's six changes."""

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


def package_project(directory):
    p = project(
        directory, models={"answer": "select {{ classroom_utils.add_one('41') }} as answer"}
    )
    local = p / "local_packages/classroom_utils"
    (local / "macros").mkdir(parents=True)
    (local / "dbt_project.yml").write_text(
        "name: classroom_utils\nversion: '1.0'\nconfig-version: 2\nmacro-paths: [macros]\n"
    )
    (local / "macros/add_one.sql").write_text(
        "{% macro add_one(value) %} (({{ value }}) + 1) {% endmacro %}"
    )
    (p / "packages.yml").write_text("packages:\n  - local: local_packages/classroom_utils\n")
    return p


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = package_project(d)
        invoke(p, "deps")
        invoke(p, "build")
        assert rows(p, "select answer from answer") == [(42,)]
        assert (p / "package-lock.yml").exists()
        assert "macro.classroom_utils.add_one" in artifact(p, "manifest.json")["macros"]
        return {"local_package_used": True, "answer": 42, "lock_written": True}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Find the package name and macro namespace.
# TODO 2: Change the local macro to add 2 and rebuild.
# TODO 3: Inspect package-lock.yml after deps.
# TODO 4: Identify the authored local package and installed package directory.
# TODO 5: List evidence needed before adding a registry dependency.
# TODO 6: Use an incorrect package namespace and observe compilation.
