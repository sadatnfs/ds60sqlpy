# Day 10 — DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 09 — correlated subqueries and EXISTS](day09_correlated_subqueries.md)
- **Artifacts:** [learner SQL](../day10_dml_with_subqueries.sql) ·
  [solution reasoning](../solutions/day10_solutions.md) ·
  [executable solution](../solutions/day10_solutions.sql)

## Learning objectives

- Modify a precisely selected row set and inspect affected rows with
  `RETURNING`.
- Make repeated loads safe with a declared conflict key and update policy.

## Vocabulary and concepts

- **DML:** data manipulation language—`INSERT`, `UPDATE`, and `DELETE`.
- **Upsert:** insert a row or resolve a uniqueness conflict through a declared
  alternative action.
- **Idempotent:** safe to repeat without accumulating unintended changes.

## Worked example / walkthrough

Run the candidate-selection `SELECT` before the matching `UPDATE`. Compare its
keys with `UPDATE ... RETURNING`, verify the affected count, and leave the
course transaction at `ROLLBACK`. This preview/modify/reconcile pattern is safer
than starting with an unbounded write.

## Exercises

Complete the prompts in the [learner SQL](../day10_dml_with_subqueries.sql).
Run an upsert twice inside the disposable transaction and prove the second run
does not create a duplicate.

## Self-check

- Is every write bounded by reviewed keys or a deliberate predicate?
- Can you name the unique constraint that makes each `ON CONFLICT` clause valid?

## Next step

Continue to [Day 11 — CASE expressions](day11_case_expressions.md).

## Deep dive and reference

Learning objectives
- INSERT ... SELECT to populate tables from queries
- UPDATE ... FROM and DELETE using subqueries
- Use ON CONFLICT for idempotent upserts

Core concepts and deep dive
- INSERT INTO table(cols) SELECT ... FROM ... WHERE ...; carry all required columns, handle default values.
- UPDATE t SET col=expr FROM other WHERE t.id=other.id; mind ambiguity with JOINs.
- DELETE FROM t USING other WHERE t.id=other.id; or use WHERE EXISTS (...) pattern.
- Upsert: INSERT ... ON CONFLICT (key) DO UPDATE SET ...; choose conflict target (PK/unique) and update columns carefully.

Walkthrough of the learner script
- `CREATE TEMP TABLE ... AS SELECT` materializes category revenue for the
  current session.
- `UPDATE employees` gives a demonstration raise to Sales and Engineering,
  with `RETURNING` exposing affected rows.
- `DELETE FROM orders` removes only old orders for which no payment exists.
- The enclosing `BEGIN`/`ROLLBACK` makes all demonstrations non-persistent.

Pitfalls
- Multi-row subqueries in scalar contexts; ensure uniqueness or add LIMIT 1.
- Upserts racing under concurrency; consider locking or version columns.

Exercises from the learner script
- There is no separate exercise block on Day 10. Run the three demonstrated DML
  patterns, inspect their returned rows, and verify after `ROLLBACK` that
  employee salaries and order counts are unchanged.

Optional extension: stage a price feed keyed by `product_id` and upsert all
required `products` columns. The current schema has no `updated_at` column, so
add one explicitly inside the same rollback-safe transaction if you want to
practice timestamped updates.

Further reading
- INSERT: https://www.postgresql.org/docs/current/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/current/sql-update.html
- UPSERT: https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT
