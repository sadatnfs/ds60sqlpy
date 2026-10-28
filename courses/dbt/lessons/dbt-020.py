"""dbt-020: worked starting point; complete the guide's six changes."""

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
            d, models={"base": "select 1 as x", "child": "select x+10 as x from {{ ref('base') }}"}
        )
        targets(p)
        invoke(p, "build", "--target", "prod")
        state = p / "prod_state"
        state.mkdir()
        shutil.copyfile(p / "target/manifest.json", state / "manifest.json")
        invoke(p, "run", "--target", "dev", "--select", "child", "--defer", "--state", str(state))
        assert rows(p, "select x from dev.child") == [(11,)]
        assert rows(
            p,
            (
                "select count(*) from information_schema.tables where "
                "table_schema='dev' and table_name='base'"
            ),
        ) == [(0,)]
        compiled = (p / "target/compiled/classroom/models/child.sql").read_text()
        assert '"prod"."base"' in compiled
        return {"deferred_parent": "prod.base", "child": 11, "dev_parent_not_built": True}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Read the child's compiled relation name.
# TODO 2: Leave an old target relation before a deferred build.
# TODO 3: Describe what happens if the manifest points to a missing table.
# TODO 4: Include the parent in the current selection.
# TODO 5: Explain why a deferred CI job still needs reviewed access.
# TODO 6: Specify the metadata needed for a reproducible deferred run.
