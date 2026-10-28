# dbt-026: explained reference

Deliver a complete local analytics product with a reviewable acceptance decision.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change a valid order

Verify the affected customer and overall total. Retain raw, accepted and rejected counts so the new result is explainable.

**Expected:** Counts and totals reconcile independently.

## 2. Add a conflicting dimension

Define a valid historical or authority rule before enrichment. If the intended dimension is current-only, its key must be unique.

**Expected:** The contract rejects the ambiguity.

## 3. Inspect lineage

Use them to trace the product, while keeping the distinction between declared lineage and independently verified quantity preservation.

**Expected:** They name staging_orders and customers.

## 4. Verify the receipt

A hash detects byte/content changes under its serialization convention. It does not prove that the input population or business definition was appropriate.

**Expected:** The received content matches the declared hash and grain.

## 5. Add temporal semantics

Do not label a current-state mart as historically available without testing that property. A model-training consumer needs the correct temporal version.

**Expected:** The resulting product obeys a declared cutoff.

## 6. Write the release decision

State the grain, parsing policy, key checks, quantities, lineage and output identity. Name the external operational requirements that the local exercise does not qualify.

**Expected:** The decision cites concrete checks and remaining boundaries.

## Complete reference

```python
"""dbt-026: actual local dbt and DuckDB reference."""

import hashlib
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


def capstone(bad_dimension):
    from ds60sqlpy.plot_artifacts import publish_report

    with tempfile.TemporaryDirectory() as d:
        models = {
            "staging_orders": (
                "select id::integer as order_id,customer::integer as "
                "customer_id,try_cast(amount as integer) as amount from {{ "
                "ref('raw_orders') }} where try_cast(amount as integer) is "
                "not null"
            ),
            "customer_mart": (
                "select o.customer_id,c.region,sum(o.amount)::bigint as "
                "total,count(*)::bigint as orders from {{ "
                "ref('staging_orders') }} o join {{ ref('customers') }} c "
                "on o.customer_id=c.customer_id group by "
                "o.customer_id,c.region"
            ),
        }
        schema = {
            "seeds": [
                {
                    "name": "customers",
                    "columns": [{"name": "customer_id", "data_tests": ["unique", "not_null"]}],
                }
            ],
            "models": [
                {
                    "name": "staging_orders",
                    "columns": [{"name": "order_id", "data_tests": ["unique", "not_null"]}],
                },
                {
                    "name": "customer_mart",
                    "description": "One accepted order total per customer and region.",
                },
            ],
        }
        customers = "customer_id,region\n10,north\n20,south\n" + (
            "10,north\n" if bad_dimension else ""
        )
        p = project(
            d,
            models=models,
            seeds={
                "raw_orders": "id,customer,amount\n1,10,5\n2,10,7\n3,20,9\n4,20,bad\n",
                "customers": customers,
            },
            schema=schema,
        )
        result = invoke(p, "build", succeeds=not bad_dimension)
        if bad_dimension:
            assert not result.success
            assert not (p / "published.json").exists()
            decision = {"published": False, "duplicate_dimension_blocked": True}
            publish_report(decision, description="dbt publication blocked by a failed key contract")
            return decision
        data = rows(
            p, "select customer_id,region,total,orders from customer_mart order by customer_id"
        )
        assert data == [(10, "north", 12, 2), (20, "south", 9, 1)]
        assert rows(p, "select count(*) from raw_orders") == [(4,)]
        assert rows(p, "select count(*) from staging_orders") == [(3,)]
        invoke(p, "docs", "generate")
        serialized = json.dumps(data, separators=(",", ":"))
        receipt = {
            "grain": "customer_id,region",
            "rows": len(data),
            "data_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
            "model_dependencies": artifact(p, "manifest.json")["nodes"][
                "model.classroom.customer_mart"
            ]["depends_on"]["nodes"],
        }
        (p / "published.json").write_text(json.dumps({"data": data, "receipt": receipt}))
        assert json.loads((p / "published.json").read_text())["receipt"] == receipt
        published = {
            "published": True,
            "total": 21,
            "quarantined": 1,
            "receipt": receipt,
            "data": [list(row) for row in data],
        }
        publish_report(published, description="Accepted dbt product and publication receipt")
        return published


def example_one():
    return capstone(False)


def example_two():
    return capstone(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-026 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Deliver a complete local analytics product with a reviewable acceptance decision. Extend it with a controlled schema or timing change, run its negative cases and explain how a consumer can select a valid version. Use the ML engineering path to connect that product to features, model training and serving contracts.
