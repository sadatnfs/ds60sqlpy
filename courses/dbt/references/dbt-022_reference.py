"""dbt-022: complete local dbt project investigation."""

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
            models={"bad": "select missing_column from {{ ref('orders') }}"},
            seeds={"orders": "id,amount\n1,5\n"},
        )
        invoke(p, "seed")
        invoke(p, "compile")
        assert (p / "target/compiled/classroom/models/bad.sql").exists()
        invoke(p, "run", succeeds=False)
        assert artifact(p, "run_results.json")["results"][0]["status"] == "error"
        return {"template_compiled": True, "database_binding_rejected": True}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={"total": "select sum(amount)*2 as amount from {{ ref('orders') }}"},
            seeds={"orders": "id,amount\n1,5\n2,7\n"},
        )
        (p / "tests").mkdir()
        (p / "tests/reconcile.sql").write_text(
            "select * from {{ ref('total') }} where amount != 12"
        )
        invoke(p, "build", succeeds=False)
        assert rows(p, "select amount from total") == [(24,)]
        assert "fail" in [r["status"] for r in artifact(p, "run_results.json")["results"]]
        return {"sql_executed": True, "wrong_quantity": 24, "independent_expected_quantity": 12}


def main():
    print(example_one())
    print(example_two())
    print("dbt-022 reference checks passed")


if __name__ == "__main__":
    main()
