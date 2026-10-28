"""dbt-008: actual local dbt and DuckDB reference."""

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
            "{{ config(materialized='incremental') }} select * from {{ "
            "ref('events') }} {% if is_incremental() %} where "
            "updated_at > (select max(updated_at) from {{ this }}) {% "
            "endif %}"
        )
        p = project(d, models={"history": sql}, seeds={"events": "id,updated_at,amount\n1,10,5\n"})
        invoke(p, "build")
        (p / "seeds/events.csv").write_text("id,updated_at,amount\n1,10,5\n2,20,7\n")
        invoke(p, "build")
        invoke(p, "run")
        assert rows(p, "select id,amount from history order by id") == [(1, 5), (2, 7)]
        return {"monotone_append_rows": 2, "rerun_did_not_duplicate": True}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        sql = (
            "{{ config(materialized='incremental') }} select * from {{ "
            "ref('events') }} {% if is_incremental() %} where "
            "updated_at > (select max(updated_at) from {{ this }}) {% "
            "endif %}"
        )
        p = project(
            d, models={"history": sql}, seeds={"events": "id,updated_at,amount\n1,10,5\n2,20,7\n"}
        )
        invoke(p, "build")
        (p / "seeds/events.csv").write_text("id,updated_at,amount\n1,10,5\n2,20,7\n3,15,9\n")
        invoke(p, "build")
        assert rows(p, "select count(*) from history") == [(2,)]
        invoke(p, "run", "--full-refresh")
        assert rows(p, "select count(*) from history") == [(3,)]
        return {"late_event_missed_by_watermark": True, "full_refresh_rows": 3}


def main():
    print(example_one())
    print(example_two())
    print("dbt-008 reference checks passed")


if __name__ == "__main__":
    main()
