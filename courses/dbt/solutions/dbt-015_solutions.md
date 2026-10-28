# dbt-015: explained reference

Separate candidate computation from accepted publication.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the failure condition

Define the condition and verify a designed negative fixture. Do not treat every possible warning as equivalent to an accepted result.

**Expected:** The candidate can be blocked by a meaningful semantic failure.

## 2. Inspect candidate state

Use this observation to design consumer isolation. Hiding an error message does not remove invalid data from a relation.

**Expected:** Its materialized rows are still observable.

## 3. Retain an accepted version

A consumer should follow a declared accepted version or pointer, not whichever file was most recently written.

**Expected:** The accepted version remains identifiable.

## 4. Handle an uncertain write

Read the intended publication identifier or hash and determine whether it exists. Blind retries can duplicate side effects in less idempotent systems.

**Expected:** The response reconciles identity before retrying.

## 5. Record the evidence

Retain input and model versions, schema/grain, executed test outcomes and output identity. Keep provenance and semantic quality as distinct claims.

**Expected:** It identifies source, checks and data identity.

## 6. Test a stale artifact

Use invocation and source/data identities. A successful result from a different run cannot justify publication of changed data.

**Expected:** A reviewed gate rejects the mismatched evidence.

## Complete reference

```python
"""dbt-015: actual local dbt and DuckDB reference."""

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


def example_two():
    return publication_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-015 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Separate candidate computation from accepted publication. Demonstrate both paths and retain a source-bound decision record. Extend the mechanism to an atomic version pointer and a tested recovery plan in a durable owned environment.
