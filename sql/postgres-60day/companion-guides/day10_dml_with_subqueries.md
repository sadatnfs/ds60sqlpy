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

## Practice assumptions and review method

- **Focus:** Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
- **Assumptions:** Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
- **Failure to watch for:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Materialize category net revenue into a temporary table with `INSERT ... SELECT`.
   **Progressive hint:** Declare the temporary schema and aggregate source rows before inserting.
   **Expected shape:** One temporary row per product category.
2. **Query writing:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
   **Progressive hint:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.
   **Expected shape:** Affected employee rows only; no change persists.
3. **Query writing:** Delete orders older than one year only when no payment exists, returning candidate keys.
   **Progressive hint:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
   **Expected shape:** Deleted-candidate order rows, then fully restored state.
4. **Prediction:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
   **Progressive hint:** A primary key supplies the conflict target; the second statement updates rather than inserts.
   **Expected shape:** One row for `source_a` with the second value.
5. **Debugging:** Preview and update a bounded product set while reconciling selected and returned key counts.
   **Progressive hint:** Store candidate keys in a temporary table and update only through that reviewed set.
   **Expected shape:** One summary row with equal candidate and updated counts.
6. **Extension:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
   **Progressive hint:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
   **Expected shape:** Returned rows only for valid changed products.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- INSERT: https://www.postgresql.org/docs/current/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/current/sql-update.html
- UPSERT: https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT
