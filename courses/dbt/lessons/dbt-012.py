"""dbt-012: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Change the latest consumer to request version 1 explicitly.
# TODO 2: Declare version 1 as latest in the fixture.
# TODO 3: Change the value while keeping the same type and name.
# TODO 4: Explain what a trained model needs when its input changes from gross to net.
# TODO 5: Find the dependency for the net model in the manifest.
# TODO 6: List the artifacts needed to restore a previous consumer contract.
