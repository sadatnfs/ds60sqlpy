"""dbt-023: worked starting point; complete the guide's six changes."""

import os
import tempfile
from pathlib import Path
from statistics import median
from time import perf_counter

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
        p = project(
            d,
            models={
                "events": (
                    "{{ config(materialized='table') }} select range as id, "
                    "range % 5 as segment, range % 7 as amount from "
                    "range(10000)"
                )
            },
        )
        invoke(p, "build")
        query = (
            "select segment,sum(amount) from events where id < 1000 "
            "group by segment order by segment"
        )
        expected = [(g, sum(i % 7 for i in range(1000) if i % 5 == g)) for g in range(5)]
        timings = []
        for _ in range(3):
            start = perf_counter()
            actual = rows(p, query)
            timings.append(perf_counter() - start)
            assert actual == expected
        plan = rows(p, "explain " + query)
        assert plan and len(str(plan)) > 50 and all(t >= 0 for t in timings)
        return {
            "result": actual,
            "median_query_seconds": median(timings),
            "plan_available": True,
            "dbt_build_time_not_measured_here": True,
        }


if __name__ == "__main__":
    print(example_one())

# TODO 1: Include the dbt build in a separate timing.
# TODO 2: Repeat the query at another bounded size.
# TODO 3: Change a predicate and review the new plan.
# TODO 4: Restore the repeated contribution in the second case.
# TODO 5: Specify whether consumers need sorted rows.
# TODO 6: Summarize what the fixture actually measured.
