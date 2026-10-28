"""dbt-007: actual local dbt and DuckDB reference."""

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
        macro = (
            "{% macro safe_ratio(n, d) %} case when {{ d }} = 0 then "
            "null else cast({{ n }} as double) / {{ d }} end {% "
            "endmacro %}"
        )
        p = project(
            d,
            models={
                "rates": (
                    "select id, {{ safe_ratio('successes', 'trials') }} as "
                    "rate from {{ ref('counts') "
                    "}}"
                )
            },
            seeds={"counts": "id,successes,trials\n1,1,4\n2,0,0\n"},
            macros={"safe_ratio": macro},
        )
        invoke(p, "build")
        assert rows(p, "select rate from rates order by id") == [(0.25,), (None,)]
        compiled = (p / "target/compiled/classroom/models/rates.sql").read_text()
        assert "case when" in compiled and "safe_ratio" not in compiled
        return {"rates": [0.25, None], "macro_expanded": True}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(d, models={"bad": "select {{ missing_macro('amount') }} as value"})
        invoke(p, "compile", succeeds=False)
        assert not (p / "target/compiled/classroom/models/bad.sql").exists()
        return {"undefined_macro_rejected_before_model_execution": True}


def main():
    print(example_one())
    print(example_two())
    print("dbt-007 reference checks passed")


if __name__ == "__main__":
    main()
