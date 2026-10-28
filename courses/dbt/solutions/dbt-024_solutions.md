# dbt-024: explained reference

Use groups and model access to define supported project interfaces, while keeping database authorization claims separate.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Identify the owner

Use ownership to route review and incidents. A declared owner does not prove someone has acknowledged or fulfilled the responsibility.

**Expected:** Responsibility is explicitly declared.

## 2. Change access deliberately

Review schema, semantics, support and migration obligations before broadening access. Public within dbt is not synonymous with public on the internet.

**Expected:** The reference policy changes explicitly.

## 3. Test database visibility

Use actual grants and identity controls in a deployed environment. Do not advertise model access metadata as row/column authorization.

**Expected:** It remains readable here.

## 4. Define a sensitive field boundary

Use an appropriate governed model, grants or service boundary and test it with the intended identity. This lesson does not configure external permissions.

**Expected:** The answer includes a real authorization mechanism.

## 5. Plan a dependency change

Publish a documented stable model, validate consumers and retire internal references under a clear policy. Avoid silently changing their meaning.

**Expected:** The plan identifies versions and acceptance checks.

## 6. Audit the claim

Record accepted/rejected dependencies and observed direct SQL access. Name the external controls that require their own configuration and tests.

**Expected:** They establish local dbt reference-policy behavior.

## Complete reference

```python
"""dbt-024: complete local dbt project investigation."""

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


def governance_case(cross_group):
    with tempfile.TemporaryDirectory() as d:
        groups = [
            {"name": "commerce", "owner": {"name": "Classroom team"}},
            {"name": "analysis", "owner": {"name": "Learning review"}},
        ]
        schema = {
            "groups": groups,
            "models": [
                {"name": "internal", "config": {"group": "commerce", "access": "private"}},
                {
                    "name": "consumer",
                    "config": {
                        "group": "analysis" if cross_group else "commerce",
                        "access": "public",
                    },
                },
            ],
        }
        p = project(
            d,
            models={
                "internal": "{{ config(materialized='table') }} select 41 as value",
                "consumer": "select value+1 as value from {{ ref('internal') }}",
            },
            schema=schema,
        )
        invoke(p, "build", succeeds=not cross_group)
        if not cross_group:
            assert rows(p, "select value from consumer") == [(42,)]
            assert rows(p, "select value from internal") == [(41,)]
        return {
            "cross_group_reference": cross_group,
            "dbt_build_accepted": not cross_group,
            "not_a_database_permission_system": True,
        }


def example_one():
    return governance_case(False)


def example_two():
    return governance_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-024 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Use groups and model access to define supported project interfaces, while keeping database authorization claims separate. Test both allowed and rejected dependencies and record who owns semantic compatibility and external access controls.
