# dbt-011: explained reference

Define a model schema contract and verify both accepted and rejected changes.

The reference enforces a contract on a table model with declared integer and bigint columns, builds a compatible version and then a version that casts `amount` to varchar. The rejected run leaves 42 in place for this DuckDB table; other adapters and materializations may fail differently. See [how these answers are laid out](../STUDY-GUIDE.md#answers-and-references).


## 1. Remove a declared column

A consumer cannot safely assume the missing field exists. Treat removal as a compatibility change rather than silently updating the contract.

**Why it holds here:** contract.enforced compares the model's actual columns to the declared id and amount list before building. Dropping amount makes the actual list shorter than the declared one, so dbt refuses the run.

**Plausible wrong approach:** Deleting the amount entry from the YAML at the same time makes the build pass, but it silently removes a field that downstream readers of contracted still select.

**How to verify:** Change the SQL to select 1::integer as id and run dbt run --select contracted; expect a contract mismatch error naming amount, with the earlier table still holding (1, 42).

**Expected:** The enforced contract rejects the mismatch.

## 2. Add a new output field

Review the consumer interface and update/version the contract deliberately. Do not assume additional fields are harmless in every downstream system.

**Why it holds here:** An extra currency column is also a mismatch under an enforced contract, because the declared column list is the full interface, not a minimum.

**Plausible wrong approach:** Assuming extra columns are always safe ignores consumers that read by position or write the relation into a fixed schema, which then break or misalign.

**How to verify:** Add 'usd'::varchar as currency to the SQL without declaring it and run; expect a contract error naming currency, then declare it with data_type varchar and confirm the build passes.

**Expected:** The schema change is explicit.

## 3. Test a null identifier

Keep data tests as appropriate and inspect adapter constraint support. A declared constraint should not be advertised as enforced without actual evidence.

**Why it holds here:** example_one declares a not_null constraint on id. DuckDB supports not null in its table DDL, so returning null for id should fail when dbt creates the table with that constraint.

**Plausible wrong approach:** Assuming every adapter enforces the same constraints is wrong; some warehouses accept primary key or foreign key declarations as metadata only.

**How to verify:** Change the SQL to select null::integer as id, 42::bigint as amount and run dbt build; expect a constraint violation, and query contracted to confirm whether the prior row survived.

**Expected:** The database/contract path reports the violation when supported.

## 4. Distinguish failure stages

A schema preflight may reject replacement earlier, while a data test can fail after materialization. Design publication around the actual sequence.

**Why it holds here:** In example_two the varchar amount is rejected before the table is replaced, so the earlier row (1, 42) is still readable. A unique test failure, by contrast, runs after the model is built.

**Plausible wrong approach:** Treating both failures as equally safe misses that the data-test failure leaves new rows materialized for anyone who reads the table directly.

**How to verify:** After the failed run, query select amount from contracted and expect 42; repeat with a duplicate id plus a unique test and observe that the new rows exist despite the test failure.

**Expected:** The two cases leave different observed state.

## 5. Check consumer assumptions

Add semantic contracts and tests. Schema enforcement does not establish that amount uses the expected currency or period.

**Why it holds here:** The contract checks names and types only. amount as bigint says nothing about whether it is cents or dollars, gross or net, or whether a null means zero.

**Plausible wrong approach:** Treating a passing enforced contract as proof that amount is correct confuses type compatibility with meaning.

**How to verify:** Write the column description with grain, unit, period and null policy, then add an accepted_range or custom test that a deliberately negative amount fails.

**Expected:** They include grain, units, time and missingness.

## 6. Plan an incompatible change

Publish a new version with its definition, compare results, migrate consumers and retain rollback evidence. The next lesson makes version selection explicit.

**Why it holds here:** Changing what amount means while keeping its name and bigint type passes the contract unchanged, so the contract alone cannot protect consumers from a meaning change.

**Plausible wrong approach:** Editing the existing model in place to compute net amount ships a semantic break that every reader receives at once with no rollback point.

**How to verify:** Create a second version with net_amount, run both side by side, compare totals per id, migrate readers, and confirm the old version still builds until it is retired.

**Expected:** It uses an explicit version and consumer migration.

## Complete reference

```python
"""dbt-011: actual local dbt and DuckDB reference."""

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
        schema = {
            "models": [
                {
                    "name": "contracted",
                    "config": {"materialized": "table", "contract": {"enforced": True}},
                    "columns": [
                        {
                            "name": "id",
                            "data_type": "integer",
                            "constraints": [{"type": "not_null"}],
                        },
                        {"name": "amount", "data_type": "bigint"},
                    ],
                }
            ]
        }
        p = project(
            d, models={"contracted": "select 1::integer as id, 42::bigint as amount"}, schema=schema
        )
        invoke(p, "build")
        assert rows(p, "select id,amount from contracted") == [(1, 42)]
        return {"declared_columns": ["id:integer", "amount:bigint"], "row": [1, 42]}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "models": [
                {
                    "name": "contracted",
                    "config": {"materialized": "table", "contract": {"enforced": True}},
                    "columns": [
                        {"name": "id", "data_type": "integer"},
                        {"name": "amount", "data_type": "bigint"},
                    ],
                }
            ]
        }
        p = project(
            d, models={"contracted": "select 1::integer as id, 42::bigint as amount"}, schema=schema
        )
        invoke(p, "build")
        (p / "models/contracted.sql").write_text(
            "select 1::integer as id, 'bad'::varchar as amount"
        )
        invoke(p, "run", succeeds=False)
        assert rows(p, "select amount from contracted") == [(42,)]
        return {
            "incompatible_schema_rejected": True,
            "previous_relation_retained_for_this_failure": True,
        }


def main():
    print(example_one())
    print(example_two())
    print("dbt-011 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Keep the observed failure timing separate from broader transaction claims, and combine structural compatibility with semantic and publication checks.
