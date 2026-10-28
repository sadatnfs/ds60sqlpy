"""dbt-009: worked starting point; complete the guide's six changes."""

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
        sql = (
            "{{ config(materialized='incremental', unique_key='id', "
            "incremental_strategy='delete+insert') }} select * from {{ "
            "ref('events') }} {% if is_incremental() %} where "
            "updated_at >= (select max(updated_at)-10 from {{ this }}) "
            "{% endif %}"
        )
        p = project(
            d,
            models={"current_events": sql},
            seeds={"events": "id,updated_at,amount\n1,10,5\n2,20,7\n"},
        )
        invoke(p, "build")
        (p / "seeds/events.csv").write_text("id,updated_at,amount\n1,11,6\n2,20,7\n3,15,9\n")
        invoke(p, "build")
        invoke(p, "run")
        assert rows(p, "select id,amount from current_events order by id") == [
            (1, 6),
            (2, 7),
            (3, 9),
        ]
        return {"keyed_update_and_late_insert": True, "rows_after_rerun": 3}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Add a record at max(updated_at)-10.
# TODO 2: Apply the same corrected source twice.
# TODO 3: Add two selected records with one id.
# TODO 4: Include a previously missed old record by changing the window.
# TODO 5: Rebuild the small fixture and compare keyed rows.
# TODO 6: List what should be recorded for a backfill.
