"""dbt-007: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Return a separate invalid-denominator flag alongside the rate.
# TODO 2: Use 1 success and 4 trials and inspect the result type.
# TODO 3: Explain why arbitrary user text should not become a SQL expression.
# TODO 4: Locate the CASE expression under target/compiled.
# TODO 5: Define a policy for negative trial counts.
# TODO 6: Describe what should be reviewed when the macro changes.
