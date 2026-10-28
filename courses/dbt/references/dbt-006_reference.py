"""dbt-006: actual local dbt and DuckDB reference."""

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


def unit_case(wrong):
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "unit_tests": [
                {
                    "name": "two_orders_same_customer",
                    "model": "totals",
                    "given": [
                        {
                            "input": "ref('raw_orders')",
                            "rows": [{"customer": 1, "amount": 2}, {"customer": 1, "amount": 3}],
                        }
                    ],
                    "expect": {"rows": [{"customer": 1, "total": 99 if wrong else 5}]},
                }
            ]
        }
        p = project(
            d,
            models={
                "totals": (
                    "select customer, sum(amount)::bigint as total from {{ "
                    "ref('raw_orders') }} group by "
                    "customer"
                )
            },
            seeds={"raw_orders": "customer,amount\n2,100\n"},
            schema=schema,
        )
        invoke(p, "seed")
        invoke(p, "test", "--select", "test_type:unit", succeeds=not wrong)
        result = artifact(p, "run_results.json")["results"]
        assert len(result) == 1 and result[0]["status"] == ("fail" if wrong else "pass")
        assert rows(p, "select amount from raw_orders") == [(100,)]
        return {
            "unit_fixture_total": 5,
            "status": result[0]["status"],
            "production_seed_unchanged": 100,
            "wrong_expectation": wrong,
        }


def example_one():
    return unit_case(False)


def example_two():
    return unit_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-006 reference checks passed")


if __name__ == "__main__":
    main()
