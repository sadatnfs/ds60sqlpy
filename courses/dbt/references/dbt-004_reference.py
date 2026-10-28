"""dbt-004: actual local dbt and DuckDB reference."""

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
        schema = {
            "models": [
                {
                    "name": "orders",
                    "columns": [{"name": "id", "data_tests": ["not_null", "unique"]}],
                }
            ]
        }
        p = project(
            d,
            models={"orders": "select * from {{ ref('raw_orders') }}"},
            seeds={"raw_orders": "id,amount\n1,5\n2,7\n"},
            schema=schema,
        )
        invoke(p, "build")
        statuses = [r["status"] for r in artifact(p, "run_results.json")["results"]]
        assert statuses.count("pass") == 2
        assert rows(p, "select count(*) from orders") == [(2,)]
        return {"tests_passed": 2, "rows": 2}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {
                    "name": "orders",
                    "columns": [{"name": "id", "data_tests": ["not_null", "unique"]}],
                }
            ]
        }
        p = project(
            d,
            models={"orders": "select * from {{ ref('raw_orders') }}"},
            seeds={"raw_orders": "id,amount\n1,5\n1,7\n"},
            schema=schema,
        )
        invoke(p, "build", succeeds=False)
        statuses = [r["status"] for r in artifact(p, "run_results.json")["results"]]
        assert "fail" in statuses
        assert rows(p, "select count(*) from orders") == [(2,)]
        (p / "seeds/raw_orders.csv").write_text("id,amount\n1,5\n2,7\n")
        invoke(p, "build", "--full-refresh")
        assert all(
            r["status"] in {"success", "pass"} for r in artifact(p, "run_results.json")["results"]
        )
        return {
            "duplicate_test_failed": True,
            "table_existed_before_repair": True,
            "repaired": True,
        }


def main():
    print(example_one())
    print(example_two())
    print("dbt-004 reference checks passed")


if __name__ == "__main__":
    main()
