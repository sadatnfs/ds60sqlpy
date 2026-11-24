# dbt-024: explained reference

Use groups and model access to define supported project interfaces, while keeping database authorization claims separate.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Identify the owner

Use ownership to route review and incidents. A declared owner does not prove someone has acknowledged or fulfilled the responsibility.

**Why it holds here:** Groups commerce and analysis each declare an owner, and each model names its group in config.

**Plausible wrong approach:** Taking the owner field as proof that someone is on call ignores that it is only a declaration.

**How to verify:** Read the manifest's groups section and the model's group config and expect Classroom team for commerce.

**Expected:** Responsibility is explicitly declared.

## 2. Change access deliberately

Review schema, semantics, support and migration obligations before broadening access. Public within dbt is not synonymous with public on the internet.

**Why it holds here:** internal is private to commerce, so the cross-group consumer fails. Making internal public allows the reference.

**Plausible wrong approach:** Making a model public without reviewing its schema and support exposes an unstable interface to other teams.

**How to verify:** Change internal's access to public, run build for the cross-group case, and expect consumer to return 42.

**Expected:** The reference policy changes explicitly.

## 3. Test database visibility

Use actual grants and identity controls in a deployed environment. Do not advertise model access metadata as row/column authorization.

**Why it holds here:** Model access only governs ref() in dbt. DuckDB still lets anyone with the file query internal directly.

**Plausible wrong approach:** Advertising private access as a security control misleads users into thinking the data is protected.

**How to verify:** Run select value from internal in DuckDB directly and expect 41.

**Expected:** It remains readable here.

## 4. Define a sensitive field boundary

Use an appropriate governed model, grants or service boundary and test it with the intended identity. This lesson does not configure external permissions.

**Why it holds here:** A restricted column needs database grants, masking, or a separate service, tested with the intended user.

**Plausible wrong approach:** Marking the model private in dbt does not hide the column from database queries.

**How to verify:** Describe the grant or masking rule and how you would test it with a restricted identity.

**Expected:** The answer includes a real authorization mechanism.

## 5. Plan a dependency change

Publish a documented stable model, validate consumers and retire internal references under a clear policy. Avoid silently changing their meaning.

**Why it holds here:** Consumers move from internal to a documented public model, validated before internal references are removed.

**Plausible wrong approach:** Changing internal's meaning in place breaks readers without warning.

**How to verify:** Create the public model, run consumers against it, and confirm their outputs match before retiring the old reference.

**Expected:** The plan identifies versions and acceptance checks.

## 6. Audit the claim

Record accepted/rejected dependencies and observed direct SQL access. Name the external controls that require their own configuration and tests.

**Why it holds here:** These two cases show that dbt accepts a same-group reference and rejects a cross-group reference to a private model.

**Plausible wrong approach:** Claiming the cases prove data is protected overstates them, since direct SQL still works.

**How to verify:** Write the claim and check it against the build results: example_one passes, example_two fails, and direct SQL reads internal.

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
                "consumer": "select value + 1 as value from {{ ref('internal') }}",
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

Test both allowed and rejected dependencies and record who owns semantic compatibility and external access controls.
