"""dbt-003: actual local dbt and DuckDB reference."""

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
        p = project(
            d,
            models={
                "staging": (
                    "{{ config(materialized='view') }} select id, amount from "
                    "{{ ref('raw_orders') }}"
                ),
                "customer_total": (
                    "{{ config(materialized='table') }} select "
                    "sum(amount)::bigint as total from {{ ref('staging') "
                    "}}"
                ),
            },
            seeds={"raw_orders": "id,amount\n1,5\n2,7\n"},
        )
        invoke(p, "build")
        manifest = artifact(p, "manifest.json")
        assert manifest["nodes"]["model.classroom.customer_total"]["depends_on"]["nodes"] == [
            "model.classroom.staging"
        ]
        assert rows(p, "select total from customer_total") == [(12,)]
        kinds = dict(
            rows(
                p,
                (
                    "select table_name, table_type from "
                    "information_schema.tables where "
                    "table_schema='main'"
                ),
            )
        )
        assert kinds["staging"] == "VIEW" and kinds["customer_total"] == "BASE TABLE"
        return {"dependency": "raw_orders -> staging -> customer_total", "total": 12}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "base": "{{ config(materialized='ephemeral') }} select 3 as x",
                "answer": "select x * 14 as answer from {{ ref('base') }}",
            },
        )
        invoke(p, "build")
        assert rows(p, "select answer from answer") == [(42,)]
        assert rows(
            p, "select count(*) from information_schema.tables where table_name='base'"
        ) == [(0,)]
        compiled = (p / "target/compiled/classroom/models/answer.sql").read_text()
        assert "__dbt__cte__base" in compiled
        return {"inlined_dependency": True, "answer": 42}


def main():
    print(example_one())
    print(example_two())
    print("dbt-003 reference checks passed")


if __name__ == "__main__":
    main()
