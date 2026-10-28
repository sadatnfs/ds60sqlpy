"""dbt-025: worked starting point; complete the guide's six changes."""

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


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "candidate": "{{ config(materialized='table') }} select 1 as version, 42 as value"
            },
        )
        invoke(p, "build")
        with duckdb.connect(str(p / "warehouse.duckdb")) as c:
            c.execute("create schema published")
            c.execute("create table published.release_one as select * from candidate")
            c.execute(
                "create view published.current_product as select * from published.release_one"
            )
            c.execute("begin")
            c.execute(
                "create or replace view published.current_product as "
                "select 2 as version, 99 as "
                "value"
            )
            assert c.execute("select value from published.current_product").fetchone() == (99,)
            c.execute("rollback")
            assert c.execute("select version,value from published.current_product").fetchone() == (
                1,
                42,
            )
        return {"transactional_pointer_rollback": True, "retained_release": [1, 42]}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Query candidate and accepted relations after failure.
# TODO 2: Repeat the pointer transaction under a valid policy and commit it.
# TODO 3: Describe a client timeout after a possible commit.
# TODO 4: List what a data/model rollback may need beyond one table.
# TODO 5: Define how old accepted versions are removed.
# TODO 6: Explain what the local rollback test cannot prove.
