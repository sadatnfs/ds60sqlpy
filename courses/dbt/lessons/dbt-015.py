"""dbt-015: worked starting point; complete the guide's six changes."""

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


def publication_case(bad):
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {"name": "ready", "columns": [{"name": "id", "data_tests": ["unique", "not_null"]}]}
            ]
        }
        p = project(
            d,
            models={"ready": "select * from {{ ref('events') }}"},
            seeds={"events": "id,value\n1,5\n" + ("1,7\n" if bad else "2,7\n")},
            schema=schema,
        )
        result = invoke(p, "build", succeeds=not bad)
        output = p / "published.json"
        statuses = [row["status"] for row in artifact(p, "run_results.json")["results"]]
        if result.success and all(value in {"pass", "success"} for value in statuses):
            output.write_text(json.dumps(rows(p, "select id,value from ready order by id")))
        assert output.exists() is (not bad)
        assert rows(p, "select count(*) from ready") == [(2,)]
        return {
            "materialized_rows": 2,
            "published": output.exists(),
            "failed_tests_block_publication": bad,
        }


def example_one():
    return publication_case(False)


if __name__ == "__main__":
    print(example_one())

# TODO 1: Add a domain test that rejects negative amounts.
# TODO 2: Query the bad relation after failure.
# TODO 3: Keep a prior valid artifact while a new candidate fails.
# TODO 4: Describe a publication timeout after the write may have occurred.
# TODO 5: Add a compact receipt beside the accepted data.
# TODO 6: Change source data but reuse an old successful run_results file.
