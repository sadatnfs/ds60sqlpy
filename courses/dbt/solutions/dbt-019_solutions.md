# dbt-019: explained reference

Run a project against an explicitly identified owned target and verify its actual destination.

The reference rewrites profiles.yml so the `dev` and `prod` outputs differ only in schema, builds into each, and reads the target name stored by the model. The unknown target leaves no run results. All schemas sit in one local DuckDB file, so this proves routing, not isolation between real environments. See [how these answers are laid out](../STUDY-GUIDE.md#answers-and-references).


## 1. Inspect the destination

Record adapter type, database identity and schema. Names such as prod should not be assumed to point to real production or to be safe without inspection.

**Why it holds here:** Both targets use the same warehouse.duckdb file and differ only in schema, dev or prod.

**Plausible wrong approach:** Assuming a target named prod is real production is wrong here; it is a schema in a local file.

**How to verify:** Read profiles.yml outputs and run dbt debug --target prod; expect the local path and schema prod.

**Expected:** Both are owned local fixtures.

## 2. Preserve calculation semantics

Use environment branches only where their behavior is deliberate and tested. Hidden semantic differences can invalidate promotion evidence.

**Why it holds here:** The model adds target.name only as a label. answer is 42 in both schemas.

**Plausible wrong approach:** Branching numeric logic on target.name would make dev results differ from what prod publishes.

**How to verify:** Query select answer from dev.answer and from prod.answer and expect 42 in both.

**Expected:** The result remains 42.

## 3. Change the default

A repeatable job should record the chosen target. Relying on a mutable local default weakens reproducibility.

**Why it holds here:** Changing the profile default to prod does not matter when --target dev is passed; the flag wins.

**Plausible wrong approach:** Relying on the default means a teammate with a different profile writes somewhere else.

**How to verify:** Set target: prod in profiles.yml, run build --target dev, and confirm only dev.answer changes.

**Expected:** The explicit selection wins for the invocation.

## 4. Reject missing configuration

Preserve the failure and repair the environment declaration. Do not redirect checks to a shared database to make them run.

**Why it holds here:** example_two runs with --target missing and dbt fails before writing run_results.json.

**Plausible wrong approach:** Pointing the missing name at another shared database just to make it run hides the misconfiguration.

**How to verify:** Confirm the command fails and target/run_results.json does not exist.

**Expected:** The command fails clearly.

## 5. Separate secrets

Use an approved secret mechanism in a separately owned environment. Do not place real passwords or tokens into the versioned lesson project.

**Why it holds here:** Real credentials belong in an approved secret store or environment variables read through env_var, never in the committed profiles.yml.

**Plausible wrong approach:** Hardcoding a password in the lesson project leaks it to anyone who can read the repo or logs.

**How to verify:** Search the project and logs for the secret value and expect no match; profiles.yml should only reference env_var.

**Expected:** They are outside maintained public fixtures and logs.

## 6. Compare isolation claims

Evaluate actual permissions, concurrency, backups, network boundaries and recovery for a deployed environment. The local case demonstrates routing only.

**Why it holds here:** Two schemas in one DuckDB file show routing only. They share the same file, process and permissions.

**Plausible wrong approach:** Claiming dev and prod are isolated because they have different schema names ignores that a single file corruption affects both.

**How to verify:** List what a deployed setup needs: separate credentials, grants, backups and network rules, and confirm none exist here.

**Expected:** They do not provide independent failure domains or access control.

## Complete reference

```python
"""dbt-019: complete local dbt project investigation."""

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


def targets(p):
    config = yaml.safe_load((p / "profiles.yml").read_text())
    original = config["classroom"]["outputs"]["dev"]
    config["classroom"]["outputs"] = {
        name: {**original, "schema": name} for name in ("dev", "prod")
    }
    (p / "profiles.yml").write_text(yaml.safe_dump(config))


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d, models={"answer": "select '{{ target.name }}' as environment, 42::integer as answer"}
        )
        targets(p)
        invoke(p, "build", "--target", "dev")
        invoke(p, "build", "--target", "prod")
        assert rows(p, "select environment,answer from dev.answer") == [("dev", 42)]
        assert rows(p, "select environment,answer from prod.answer") == [("prod", 42)]
        return {"same_file_owned_test_database": True, "separate_schemas": ["dev", "prod"]}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(d)
        targets(p)
        invoke(p, "run", "--target", "missing", succeeds=False)
        assert not (p / "target/run_results.json").exists()
        return {"unknown_target_rejected": True, "no_ambient_warehouse_selected": True}


def main():
    print(example_one())
    print(example_two())
    print("dbt-019 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Preserve calculation semantics across routing changes, reject unknown environments and document the additional isolation requirements of real deployments.
