# dbt-006: explained reference

Use controlled fixtures to test transformation logic and real-data checks to test integration.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a second customer

This catches a model that returns one global total. Verify row identities as well as amounts.

**Why it holds here:** The given rows for ref('raw_orders') currently hold only customer 1, so a model that drops group by customer and returns sum(amount) over everything still produces a single row with total 5. A second customer makes the grouping observable.

**Plausible wrong approach:** Adding the second customer only to the production seed raw_orders.csv changes nothing in the unit test, because the fixture replaces that relation during test_type:unit.

**How to verify:** Add customer 2 with amount 10 to the given rows and expect rows [customer 1 total 5, customer 2 total 10]; dbt test --select test_type:unit should report pass, and the run_results entry should show status pass.

**Expected:** The expected result has one row per customer.

## 2. Add a zero amount

A separate count output or row-accounting test can reveal a dropped zero-valued row when that distinction matters.

**Why it holds here:** sum(amount) ignores whether a zero row is present, so adding customer 1 amount 0 leaves total at 5. The exercise shows that this model's output cannot detect a dropped zero row on its own.

**Plausible wrong approach:** Expecting total 5 and concluding the zero row was processed is wrong; a filter such as where amount > 0 would give the same 5 and pass the same test.

**How to verify:** Add count(*) as order_count to a scratch copy of the model and expect order_count 3 for customer 1; the filtered version then fails with order_count 2, proving the extra column adds coverage.

**Expected:** The total is unchanged but row coverage increases.

## 3. Change a key

The fixture should catch grouping by a nonunique display field. Use the actual intended key in both SQL and expectation.

**Why it holds here:** When rows carry customer ids 1 and 2 but share a label like Acme, grouping by the label merges them into one total while grouping by customer keeps them apart. The fixture is chosen to make that difference visible.

**Plausible wrong approach:** Writing the expectation by grouping on the label as well would let the test pass on the merged total, since model and oracle would share the same mistake.

**How to verify:** Expect two rows, customer 1 total 5 and customer 2 total 10, and temporarily group by label in the model; the unit test should fail with one row of 15 versus the two expected rows.

**Expected:** They remain separate groups.

## 4. Remove a grouping clause

A failure proves that this fixture detects that defect. It does not prove the suite detects all possible changes.

**Why it holds here:** Deleting group by customer makes the select list invalid in DuckDB, because customer is neither aggregated nor grouped, so dbt test reports an error for the unit test node rather than a passing comparison.

**Plausible wrong approach:** Concluding from one caught defect that the suite is complete is wrong: replacing sum(amount) with sum(distinct amount) still returns 5 for the amounts 2 and 3, so that defect passes this fixture unnoticed.

**How to verify:** Run dbt test --select test_type:unit after the edit and read run_results.json; the totals unit test status should be error or fail, and restoring the clause should return it to pass.

**Expected:** The unit test rejects wrong output or SQL.

## 5. Compare test types

Use integration tests, source contracts and operational observations for the actual data. Keep the evidence categories separate.

**Why it holds here:** The unit test swaps ref('raw_orders') for two inline rows, so it says nothing about the seeded table holding customer 2 amount 100. The reference even asserts that seed value is unchanged after the test.

**Plausible wrong approach:** Reading a passing unit test as evidence that raw_orders has unique, complete rows mixes logic evidence with data evidence; production duplicates would never reach the fixture.

**How to verify:** Add not_null and relationships or unique data tests on the real raw_orders relation and run dbt test --select test_type:data; those results, not the unit result, describe the source.

**Expected:** It cannot prove actual source completeness or uniqueness.

## 6. Build an independent oracle

Independent expected values reduce the risk that the model and test share the same error. Document the assumptions behind the oracle.

**Why it holds here:** The oracle is computed by hand from the fixture rows: 2 plus 3 gives 5 for customer 1. Because it comes from the inputs rather than the SQL, a shared bug cannot make both sides agree.

**Plausible wrong approach:** Generating the expected rows by running the totals model on the fixture and pasting its output would freeze whatever the current SQL returns, including errors, as the expectation.

**How to verify:** Compute the expectation in Python from the given rows, for example sum of amounts per customer, compare it with the YAML expect block, and confirm the deliberately wrong 99 case reports fail.

**Expected:** The oracle does not copy the SQL expression verbatim.

## Complete reference

```python
"""dbt-006: actual local dbt and DuckDB reference."""

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


def unit_case(wrong):
    with tempfile.TemporaryDirectory() as d:
        schema = {
            "unit_tests": [
                {
                    "name": "two_orders_same_customer",
                    "model": "totals",
                    "given": [
                        {
                            "input": "ref('raw_orders')",
                            "rows": [{"customer": 1, "amount": 2}, {"customer": 1, "amount": 3}],
                        }
                    ],
                    "expect": {"rows": [{"customer": 1, "total": 99 if wrong else 5}]},
                }
            ]
        }
        p = project(
            d,
            models={
                "totals": (
                    "select customer, sum(amount)::bigint as total from {{ "
                    "ref('raw_orders') }} group by "
                    "customer"
                )
            },
            seeds={"raw_orders": "customer,amount\n2,100\n"},
            schema=schema,
        )
        invoke(p, "seed")
        invoke(p, "test", "--select", "test_type:unit", succeeds=not wrong)
        result = artifact(p, "run_results.json")["results"]
        assert len(result) == 1 and result[0]["status"] == ("fail" if wrong else "pass")
        assert rows(p, "select amount from raw_orders") == [(100,)]
        return {
            "unit_fixture_total": 5,
            "status": result[0]["status"],
            "production_seed_unchanged": 100,
            "wrong_expectation": wrong,
        }


def example_one():
    return unit_case(False)


def example_two():
    return unit_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-006 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Include at least one counterexample that would detect a plausible defect, and retain the source and expected rows needed to explain the result.
