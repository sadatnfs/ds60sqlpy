# pyweb-065: Database performance, indexes and contention

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-064`.

## Starting point and result

Database performance and correctness interact through query plans, indexes and transaction ownership. This chapter inspects a real SQLite plan before and after adding a composite index, then creates a controlled write conflict and verifies recovery. It avoids presenting small-fixture timing as a production benchmark.

## Mechanism: an index supports a particular access pattern

The query filters by owner, advances past an identifier and orders by identifier with a small limit. A composite index on owner and id matches that access pattern. Column order matters because the index organizes keys in that sequence; an unrelated index is not automatically useful merely because it contains one requested column.

EXPLAIN QUERY PLAN reports SQLite's chosen strategy. The program records the descriptive plan before and after index creation and checks that the new plan uses the named index. It also compares query results to ensure the optimization preserved semantics.

Indexes cost storage and write work. Adding every possible index can slow mutations and complicate maintenance. Choose indexes from actual query predicates, joins, ordering and selectivity, then inspect plans and representative workloads. The SQL curriculum supplies deeper plan analysis for PostgreSQL.

## Worked case: preserve a keyset page while changing the plan

The fixture inserts forty notes across five owners. It runs the bounded owner/id query, stores the expected rows, creates the composite index and repeats the query. The result rows remain identical, while the plan names the new index.

The limit bounds returned data, but it does not necessarily bound all work in an unindexed plan. A database may scan many candidates before finding the requested rows. Plan inspection helps distinguish result size from execution cost.

The test asserts the named index rather than copying an entire version-sensitive plan string. The complete plan is still reported for learning. Different database versions can choose different valid details, so tests should target the behavior they intend to qualify without becoming meaningless or excessively brittle.

## Worked case: conflict on a write, then recover

Two connections open the same temporary database. The first starts an immediate write transaction. The second, configured with zero wait, attempts a conflicting write and receives a locked error. After rollback releases the first transaction, the second writes successfully and the new value is visible.

This is actual SQLite locking behavior. PostgreSQL uses different concurrency machinery and error conditions, so the lesson does not label the result as PostgreSQL lock qualification. The owned service workshop tests its real database separately.

A production service should define whether to wait, retry or fail when contention occurs. Retrying without a bounded budget can amplify load. Retrying a non-idempotent operation without reconciling prior effects can also change business results.

## Failure diagnosis and discussion

**Why did LIMIT not make a query cheap?** The database may still scan or sort many rows to identify the limited result. Inspect the plan and the access path.

**Why does a failed write keep blocking later work?** A transaction or connection may remain open. Rollback and release resources according to the unit-of-work boundary rather than relying on eventual garbage collection.

If an index is unused, inspect predicate shape, column order, data distribution and planner estimates. If contention rises, inspect transaction duration and work performed while holding locks. Continue with caches and rate limits, which introduce another kind of shared-state consistency problem.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite cross-framework engineering investigation with explicit scope."""

import json
import sqlite3
import tempfile
from pathlib import Path


def run_cases():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "db.sqlite3"
        first = sqlite3.connect(path, timeout=0)
        first.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, owner INTEGER, title TEXT)")
        first.executemany(
            "INSERT INTO notes(owner,title) VALUES(?,?)", [(i % 5, str(i)) for i in range(40)]
        )
        first.commit()
        query = "SELECT id,title FROM notes WHERE owner=? AND id>? ORDER BY id LIMIT 4"
        before = [row[3] for row in first.execute("EXPLAIN QUERY PLAN " + query, (2, 0))]
        expected = first.execute(query, (2, 0)).fetchall()
        first.execute("CREATE INDEX notes_owner_id ON notes(owner,id)")
        after = [row[3] for row in first.execute("EXPLAIN QUERY PLAN " + query, (2, 0))]
        assert first.execute(query, (2, 0)).fetchall() == expected
        assert any("notes_owner_id" in detail for detail in after)
        second = sqlite3.connect(path, timeout=0)
        first.execute("BEGIN IMMEDIATE")
        try:
            second.execute("UPDATE notes SET title=? WHERE id=1", ("conflict",))
        except sqlite3.OperationalError as error:
            assert "locked" in str(error).lower()
        else:
            raise AssertionError("Competing write unexpectedly succeeded")
        first.rollback()
        second.rollback()
        second.execute("UPDATE notes SET title=? WHERE id=1", ("recovered",))
        second.commit()
        assert first.execute("SELECT title FROM notes WHERE id=1").fetchone()[0] == "recovered"
        first.close()
        second.close()
    return {
        "plan_before": before,
        "plan_after": after,
        "rows_preserved": expected,
        "write_conflict_then_recovery": True,
        "database": "SQLite, not PostgreSQL lock qualification",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
