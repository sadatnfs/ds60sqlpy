"""dbt-024: worked starting point; complete the guide's six changes."""

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


def governance_case(cross_group):
    with tempfile.TemporaryDirectory() as d:
        groups = [
            {"name": "commerce", "owner": {"name": "Classroom team"}},
            {"name": "analysis", "owner": {"name": "Learning review"}},
        ]
        schema = {
            "groups": groups,
            "models": [
                {"name": "internal", "config": {"group": "commerce", "access": "private"}},
                {
                    "name": "consumer",
                    "config": {
                        "group": "analysis" if cross_group else "commerce",
                        "access": "public",
                    },
                },
            ],
        }
        p = project(
            d,
            models={
                "internal": "{{ config(materialized='table') }} select 41 as value",
                "consumer": "select value+1 as value from {{ ref('internal') }}",
            },
            schema=schema,
        )
        invoke(p, "build", succeeds=not cross_group)
        if not cross_group:
            assert rows(p, "select value from consumer") == [(42,)]
            assert rows(p, "select value from internal") == [(41,)]
        return {
            "cross_group_reference": cross_group,
            "dbt_build_accepted": not cross_group,
            "not_a_database_permission_system": True,
        }


def example_one():
    return governance_case(False)


if __name__ == "__main__":
    print(example_one())

# TODO 1: Locate the group and owner metadata for a model.
# TODO 2: Make the producer public and review the cross-group dependency.
# TODO 3: Query the internal relation directly in the owned fixture.
# TODO 4: Explain how a restricted column should be controlled outside this fixture.
# TODO 5: Describe how consumers should migrate from an internal model to a supported interface.
# TODO 6: Write exactly what these two cases establish.
