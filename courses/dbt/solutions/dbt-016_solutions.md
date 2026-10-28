# dbt-016: explained reference

Publish a metric with a complete numerator/denominator contract and an independent check.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Write the population

State eligibility, time, treatment of missingness and duplicate policy before writing the SQL. Keep those rules with the metric owner.

**Expected:** The inclusion and time rules are explicit.

## 2. Pool across cohorts

A mean of cohort rates would give equal cohort weight and a different target. Choose the weighting unit from the question.

**Expected:** The rate is 11/102.

## 3. Test empty evidence

Return null or a separate no-evidence status and retain the denominator. Do not silently manufacture observed failures.

**Expected:** Its rate follows an explicit undefined-value policy.

## 4. Preserve counts

Counts support intervals and comparison of evidence. Preserve the original metric grain while joining other descriptive fields.

**Expected:** The estimate can be independently reconstructed.

## 5. Prevent join inflation

Validate the relationship and compare numerator/denominator totals before and after joins. Distinct on a final display is not a general repair.

**Expected:** The gate detects changed totals or cardinality.

## 6. Review semantic-layer claims

Use known fixtures and compare service results with an independent oracle, including nulls, joins, time boundaries and filters. Keep platform setup explicit.

**Expected:** It includes actual generated queries and equivalent outputs.

## Complete reference

```python
"""dbt-016: actual local dbt and DuckDB reference."""

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
        p = project(
            d,
            models={
                "metrics": (
                    "select cohort, sum(successes)::double/nullif(sum(trials),0"
                    ") as rate, sum(trials) as denominator from {{ "
                    "ref('counts') }} group by cohort"
                )
            },
            seeds={"counts": "cohort,successes,trials\nA,1,1\nA,9,99\nB,1,2\n"},
        )
        invoke(p, "build")
        assert rows(p, "select cohort,rate,denominator from metrics order by cohort") == [
            ("A", 0.1, 100),
            ("B", 0.5, 2),
        ]
        return {"rates": {"A": 0.1, "B": 0.5}, "denominators": {"A": 100, "B": 2}}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "wrong": "select avg(successes::double/trials) as rate from {{ ref('counts') }}"
            },
            seeds={"counts": "successes,trials\n1,1\n9,99\n"},
        )
        invoke(p, "build")
        value = rows(p, "select rate from wrong")[0][0]
        assert abs(value - 0.1) > 0.4
        return {"equal_row_rate": value, "correct_trial_weighted_rate": 0.1}


def main():
    print(example_one())
    print(example_two())
    print("dbt-016 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Publish a metric with a complete numerator/denominator contract and an independent check. Carry it across SQL, Polars and downstream model dashboards without changing its meaning. Treat semantic-layer adoption as an additional implementation to qualify against that contract.
