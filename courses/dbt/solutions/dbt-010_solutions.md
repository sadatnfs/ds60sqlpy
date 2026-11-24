# dbt-010: explained reference

Explain what a snapshot actually observed and what it cannot reconstruct.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect a closed version

Retain both versions and their interval meaning. A current-only query is appropriate for a different question than a historical reconstruction.

**Why it holds here:** The check strategy compared region for customer 1, saw north change to west and closed the north row by setting dbt_valid_to. That is why the snapshot holds 3 rows for 2 customers after the second run.

**Plausible wrong approach:** Querying only where dbt_valid_to is null returns west for customer 1 and loses the north interval, which answers what is current rather than what was observed before.

**How to verify:** Select customer_id, region, dbt_valid_from, dbt_valid_to from the relation named in the manifest where customer_id = 1; expect north with a non-null dbt_valid_to and west with null.

**Expected:** The changed version has a non-null dbt_valid_to.

## 2. Change a tracked column

Review whether the attribute represents meaningful state or noisy metadata. Tracking every field can produce unnecessary history churn.

**Why it holds here:** check_cols lists the columns whose change opens a new version. Adding segment means a later seed that edits only segment closes the current row, which is right if segment is business state and wasteful if it is load metadata.

**Plausible wrong approach:** Switching check_cols to all would also version on columns like a load batch id that change every run, producing a new history row per customer per snapshot without any real change.

**How to verify:** Add segment to the seed and check_cols, snapshot, change only segment for customer 2 and snapshot again; the history count should grow by one row for customer 2.

**Expected:** Its changes can create new versions under the revised policy.

## 3. Explain unobserved changes

Use a source change log or another stronger history mechanism when the intermediate state matters. Snapshots cannot reconstruct unobserved facts.

**Why it holds here:** A snapshot only compares the source at each invocation. If region goes north to east to west between two runs, the stored history shows north then west, and east never existed as far as the table can tell.

**Plausible wrong approach:** Shortening dbt_valid_from intervals or interpolating an east row from the gap would invent state that no run observed.

**How to verify:** Write east to the seed without running snapshot, then write west and snapshot; querying customer 1 returns exactly two rows, north and west, with no east.

**Expected:** The intermediate state may never appear in the snapshot.

## 4. Compare deletion policies

Choose a policy that distinguishes genuine deletion from incomplete ingestion. A partial load should not automatically invalidate valid entities.

**Why it holds here:** In example_two customer 2 disappears and hard_deletes invalidate closes its row, leaving only customer 1 active. With ignore, the south row for customer 2 would remain open as if still current.

**Plausible wrong approach:** Choosing invalidate on a feed that sometimes lands partially would close valid customers whenever a load is truncated, so a partial file looks like mass churn.

**How to verify:** Rerun example_two with hard_deletes set to ignore; the active query should return both (1, west) and (2, south), whereas invalidate returns only (1, west).

**Expected:** A formerly current record can remain open.

## 5. Review temporal meaning

For event-effective analyses, preserve source effective/known times and define a temporal model. Do not infer them from snapshot timing alone.

**Why it holds here:** dbt_valid_from is the time the snapshot run saw the change, not when the customer moved. A move on Monday captured by a Thursday run is recorded as Thursday.

**Plausible wrong approach:** Joining orders to region by dbt_valid_from as if it were the effective date assigns Monday through Wednesday orders to the old region.

**How to verify:** Add an effective_date column to the seed with a date earlier than the run, snapshot, and compare it to dbt_valid_from; the two differ, which shows they come from different clocks.

**Expected:** The explanation keeps the clocks separate.

## 6. Verify identity

Multiple source rows for one snapshot key need a deterministic, justified resolution or a failure. Otherwise the historical record becomes ambiguous.

**Why it holds here:** unique_key customer_id assumes one source row per customer. If the seed holds two rows for customer 1 with different regions, the snapshot cannot tell which one is the observed state.

**Plausible wrong approach:** Deduplicating with select distinct still leaves two rows when the regions differ, so the ambiguity passes through to history.

**How to verify:** Add a unique data test on customers.customer_id, seed a duplicate id, and run dbt test; the test should fail before any snapshot run is trusted.

**Expected:** Conflicting identity is detected before trusting history.

## Complete reference

```python
"""dbt-010: actual local dbt and DuckDB reference."""

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


def relation(root, unique_id):
    return artifact(root, "manifest.json")["nodes"][unique_id]["relation_name"]


def snapshot_case(delete):
    with tempfile.TemporaryDirectory() as d:
        snapshots = [
            {
                "name": "customer_history",
                "relation": "ref('customers')",
                "config": {
                    "schema": "history",
                    "unique_key": "customer_id",
                    "strategy": "check",
                    "check_cols": ["region"],
                    "hard_deletes": "invalidate",
                },
            }
        ]
        p = project(
            d,
            models={"dummy": "select 1 as value"},
            seeds={"customers": "customer_id,region\n1,north\n2,south\n"},
            snapshots=snapshots,
        )
        invoke(p, "seed")
        invoke(p, "snapshot")
        (p / "seeds/customers.csv").write_text(
            "customer_id,region\n1,west\n" if delete else "customer_id,region\n1,west\n2,south\n"
        )
        invoke(p, "seed")
        invoke(p, "snapshot")
        table = relation(p, "snapshot.classroom.customer_history")
        assert rows(p, f"select count(*) from {table}") == [(3,)]
        active = rows(
            p,
            f"select customer_id,region from {table} "
            "where dbt_valid_to is null order by customer_id",
        )
        assert active == ([(1, "west")] if delete else [(1, "west"), (2, "south")])
        return {"history_rows": 3, "active_rows": active, "delete_invalidation": delete}


def example_one():
    return snapshot_case(False)


def example_two():
    return snapshot_case(True)


def main():
    print(example_one())
    print(example_two())
    print("dbt-010 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Verify current and closed versions, define deletion handling, and preserve identity and clock contracts before using the history for features or analysis.
