# Bridge Day 5 — Solution notes

Attempt the [learner file](../lessons/day05_db_testing_fixtures_doubles.py)
before comparing [day05_solution.py](day05_solution.py).

## Test seams

`customer_order_total()` depends on `OrderRepository`, a one-method Protocol
expressed in domain terms. The fake stores configured `Decimal` sequences and
records customer IDs. Tests can prove the rule and the collaboration without
knowing about SQL or cursors.

`CursorOrderRepository` is the adapter. Its separate tests should prove a
positive ID check, `%s` binding, and row conversion. An optional PostgreSQL test
then proves the statement against the real course schema.

## Rollback-only ownership

`rollback_only()` puts rollback in `finally`, so a passing assertion and a
failing assertion both clean up. It does not catch the body exception and
therefore cannot accidentally turn a failure into success.

`live_database_url()` requires the explicit opt-in flag and the URL. Merely
having a connection string in a shell does not authorize a normal test run to
contact it.

## Tradeoffs

- The fake is intentionally less capable than PostgreSQL. Adding joins,
  transactions, or constraints would duplicate the implementation and create
  false confidence.
- An in-memory fake can return impossible states. Adapter and integration tests
  cover the small set of database contracts where that matters.
- Transaction rollback removes row changes but not every side effect:
  sequences advance, locks were visible, and some DDL or external calls may
  behave differently. Use a disposable isolated database.
- A session-scoped live fixture is faster, while a function-scoped transaction
  isolates failures better. Choose based on test cost and contamination risk.

The balanced suite has many pure tests, a few recording-adapter tests, and the
smallest useful number of opt-in PostgreSQL tests.

