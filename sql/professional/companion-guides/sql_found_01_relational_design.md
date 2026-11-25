# SQL-FOUND-01: Relational Design, DDL, and Integrity Constraints

## How to run this lesson

Start **sql-found-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. The script needs no course tables. Inside
one transaction on `advanced_sql_training` it creates the `pro_relational_lab`
schema with four tables (`members`, `equipment_categories`, `equipment_items`
and `loans`), loads two categories, two members, two items (`AUD-001` and
`TOL-001`) and one loan of `AUD-001`, and ends with `ROLLBACK`. Three `DO`
blocks then try a duplicate email, a due date before checkout and a nonexistent
member. Each should print a NOTICE such as `Expected UNIQUE failure`; that
NOTICE is the passing outcome, while an uncaught ERROR or an "unexpectedly
succeeded" exception is a real failure. Save your DDL in
`.learning/sql/sql-found-01/lesson/workspace/sql/professional/lessons/sql_found_01_relational_design.sql`,
before the final `ROLLBACK`, so a rerun starts without the schema.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-found-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisite:** `sql-15`; [SQL Day 15; Phase 1 Project](../../postgres-60day/companion-guides/day15_phase1_project.md)
- **Prerequisites:** Complete SQL Days 1-15 so you can query, join, aggregate,
  modify, and verify the supplied training schema before designing one of your
  own. PostgreSQL setup and the disposable database are also required.
- **Artifacts:** [learner SQL](../lessons/sql_found_01_relational_design.sql) ·
  [solution reasoning](../solutions/sql_found_01_relational_design_solutions.md) ·
  [executable solution](../solutions/sql_found_01_relational_design_solutions.sql)

The file creates `pro_relational_lab` inside a transaction and rolls it back.
Expected constraint failures are caught as notices; any unexpected error still
stops the script.

## A beginner's mental model for this lesson

This lesson is about the tables themselves rather than about query results. The
vocabulary below (grain, cardinality, natural and surrogate keys, primary and
foreign keys) is what you use to decide where each fact lives in
`pro_relational_lab`, and the constraints are what make PostgreSQL refuse a row
that breaks one of those decisions.

Here the grain question comes before any query: write what one row of each
table means before you type a column. The four requirements below give one
member, one reusable category, one physical item and one checkout, and the
`loans` row is the only one that points at two parents. When you later join the
tables back together, as the learner script's loan description does, one output
row should still be one loan; the general reading order is in the [study
guide](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

The walkthrough turns four sentences of requirements into four tables, then
shows which rule each constraint protects. Example 1 and Example 2 are the
first two of those tables; read them with the requirement sentence beside each
column.

## Two worked SQL examples

Both excerpts below run inside the learner script after its setup, before its
final `ROLLBACK`.

### Example 1

```sql
CREATE TABLE pro_relational_lab.members (
  member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  display_name text NOT NULL CHECK (btrim(display_name) <> ''),
  email text NOT NULL UNIQUE,
  backup_contact text UNIQUE,
  joined_on date NOT NULL DEFAULT CURRENT_DATE
);
```

**How to read it:** `members` has a generated surrogate key, `member_id`, and
also makes `email` `UNIQUE` because two member rows must never share an email
address. `backup_contact` is `UNIQUE` but nullable, and
`btrim(display_name) <> ''` rejects a name made only of spaces. `joined_on`
uses `DEFAULT CURRENT_DATE` only when an insert leaves the column out.

**Expected result/shape:** psql prints `CREATE TABLE`. The two members loaded
later both have a NULL `backup_contact`, and the script's count query shows
that ordinary `UNIQUE` accepts both, while the duplicate `avery@example.test`
insert prints the expected UNIQUE notice.

### Example 2

```sql
CREATE TABLE pro_relational_lab.equipment_categories (
  category_code text PRIMARY KEY,
  display_name text NOT NULL UNIQUE,
  standard_loan_days integer NOT NULL CHECK (standard_loan_days BETWEEN 1 AND 90)
);
```

**How to read it:** `equipment_categories` uses the natural key `category_code`
(such as `AUDIO`) as its primary key, keeps `display_name` unique, and limits
`standard_loan_days` to 1 through 90. Items reference this code, so one
category row serves many items.

**Expected result/shape:** psql prints `CREATE TABLE`. The fixture loads two
categories, `AUDIO` with 7 loan days and `TOOL` with 14, and every item's
`category_code` must match one of them.

## Learning objectives

- State a table's grain, map one-to-one and one-to-many requirements to keys,
  and create a normalized schema.
- Choose database constraints for durable invariants and explain one deliberate
  denormalization.
- Predict and observe safe `NOT NULL`, `CHECK`, `UNIQUE`, primary-key, and
  foreign-key failures.

## Vocabulary and concepts

- **Grain:** exactly what one row represents. State it before naming columns.
- **Cardinality:** how many rows on one side may relate to rows on another side,
  such as one category to many physical items.
- **Natural key:** a meaningful value from the domain, such as an asset tag.
- **Surrogate key:** a generated identifier with no domain meaning.
- **Primary key:** the chosen unique, non-null identity for a row.
- **Foreign key:** a reference whose value must identify an allowed parent row.
- **Invariant:** a rule that must remain true for every valid database state.
- **Identity column:** a PostgreSQL-managed sequence value declared with
  `GENERATED ... AS IDENTITY`.
- **Generated column:** a stored value calculated from other columns in the same
  row; its expression must be immutable.
- **Normalization:** separating facts so each is stored at the appropriate
  grain and accidental update contradictions are reduced.
- **Deliberate denormalization:** intentionally copying or deriving a value for
  a stated historical, performance, or availability reason, with an explicit
  consistency rule.

## Worked example / walkthrough

The example begins with four requirements and turns each into a grain:

1. A member is one person who may borrow equipment.
2. A category is one reusable classification.
3. An equipment item is one physical asset and belongs to one category.
4. A loan is one checkout of one item to one member.

`members.member_id`, `equipment_items.item_id`, and `loans.loan_id` are identity
primary keys. Meaningful identifiers such as `email` and `asset_tag` also receive
`UNIQUE` constraints. The item and member identifiers in `loans` are foreign
keys, so an application bug cannot create an orphan checkout.

Constraints express the smallest durable rule:

- `NOT NULL` says absence is invalid.
- `CHECK` limits values or relationships within a row.
- `UNIQUE` prevents duplicate keys.
- `PRIMARY KEY` supplies row identity.
- `FOREIGN KEY` protects a relationship between tables.
- `DEFAULT` supplies a value only when the insert omits that column.

An ordinary PostgreSQL `UNIQUE` constraint allows multiple NULL values. NULL
means “unknown,” and unknown is not equal to unknown. PostgreSQL 15 and newer
also support `UNIQUE NULLS NOT DISTINCT` when the requirement says that at most
one unknown value is allowed.

The loan stores `daily_fee_at_checkout` even though the current item has
`daily_fee`. That is deliberate denormalization: the snapshot answers “what fee
was quoted then?” after the catalog fee changes. By contrast, copying the
category display name into every item would create a needless update anomaly.

The learner script catches expected exceptions inside small anonymous blocks.
The wrapper is only test scaffolding: the important event is PostgreSQL
rejecting the invalid statement while the outer transaction remains usable.

## Exercises

Complete all eight prompts at the bottom of the learner SQL. Begin by designing
`maintenance_visits` from prose, load a valid row, prove an invalid cost is
rejected, investigate NULL uniqueness, and justify whether the checkout fee
snapshot is deliberate denormalization; then continue through normalization,
outer joins, deletion policy, and catalog contracts. Keep your DDL inside the
existing transaction so a rerun begins cleanly.

Before typing, write the proposed grain and cardinality in comments. For every
constraint, complete the sentence: “This belongs in the database because
without it, ___ could become false regardless of which application wrote the
row.”

Work through these in order; each item names the evidence to leave in your
scratch SQL:

1. **Maintenance DDL:** translate every visit requirement into a column,
   constraint, key, default, or generated expression; annotate the table grain.
   **Inputs/evidence:** For sql-found-01 Exercise 1, create `pro_relational_lab.maintenance_visits` at one-row-per-visit grain inside the rollback-only lab, referencing `equipment_items`; inspect its columns, constraints, defaults, and generated expression through PostgreSQL catalogs.
   **Expected result/shape:** For sql-found-01 Exercise 1, expected output: a successful `CREATE TABLE` command tag followed by catalog evidence for one identity primary key, one item foreign key, nonblank and nonnegative checks, completion-order logic, nullable uniqueness, the `opened_on` default, and stored `service_days` that remains NULL until completion.
   **Verify:** For sql-found-01 Exercise 1, assert the catalog definitions rather than generated constraint names, execute one accepted visit and rejected cost/date/foreign-key cases with their SQLSTATE classes, and confirm the final rollback removes `pro_relational_lab`.
2. **Negative cost:** insert one valid visit, isolate the rejected insert in a
   nested block, and verify the expected SQLSTATE category.
   **Inputs/evidence:** For sql-found-01 Exercise 2, resolve the `AUD-001` item key, insert one valid maintenance visit with `RETURNING visit_id, item_id, cost`, and attempt one negative-cost insert inside a nested exception block.
   **Expected result/shape:** For sql-found-01 Exercise 2, expected output: exactly one returned valid visit with `cost = 28.50`; the invalid attempt emits the expected check-violation notice and contributes no visit row.
   **Verify:** For sql-found-01 Exercise 2, compare the returned `item_id` with the independently selected `AUD-001` key, count exactly one `VISIT-100` row, and prove the negative-cost target count remains zero after SQLSTATE `23514` is caught.
3. **NULL uniqueness:** insert two NULL references, explain the observed rule,
   and write, but do not blindly apply, the stricter PostgreSQL 15+ alternative.
   **Inputs/evidence:** For sql-found-01 Exercise 3, insert two visits with `external_reference IS NULL`, then inspect all visit rows plus the unique index property that controls NULL comparison.
   **Expected result/shape:** For sql-found-01 Exercise 3, expected output: exactly three visits in the supplied solution state, exactly two with NULL external references, and ordinary uniqueness with `indnullsnotdistinct = false`; PostgreSQL 15+ `UNIQUE NULLS NOT DISTINCT` is the stated alternative policy.
   **Verify:** For sql-found-01 Exercise 3, assert the two NULL rows both survive, retry a duplicate non-NULL `VISIT-100` and record SQLSTATE `23505`, and explain that changing to `NULLS NOT DISTINCT` would permit at most one NULL.
4. **Historical fee:** state the invariant, the historical question, and why the
   checkout snapshot is or is not deliberate denormalization.
   **Inputs/evidence:** For sql-found-01 Exercise 4, create a loan-level numeric `daily_fee_at_checkout`, copy the equipment item's current fee at checkout, change the current fee, and return both values plus a decision record.
   **Expected result/shape:** For sql-found-01 Exercise 4, expected output: one loan row showing current fee 15.00 and preserved checkout fee 12.00, followed by one classification row with `attribute_name`, `classification`, `invariant`, and `historical_question`.
   **Verify:** For sql-found-01 Exercise 4, change the equipment item's current fee and compare both values; assert the historical `daily_fee_at_checkout` remains unchanged while the catalog fee changes.
5. **Many-to-many work:** model providers, technicians, and assignments with
   one declared grain and key per relation; do not use delimited text.
   **Inputs/evidence:** For sql-found-01 Exercise 5, model providers and technicians as keyed entities, one provider assignment per visit, and a many-to-many `visit_technicians` bridge; then join the normalized relationships for `VISIT-100`.
   **Expected result/shape:** For sql-found-01 Exercise 5, expected output: a four-row grain map (`providers`, `technicians`, `visit_providers`, `visit_technicians`) followed by two assignment rows with `visit_id`, `provider_name`, `technician_id`, and `technician_name`.
   **Verify:** For sql-found-01 Exercise 5, inspect primary and foreign keys, assert one provider assignment and two distinct technician assignments for `VISIT-100`, and prove a duplicate `(visit_id, technician_id)` is rejected.
6. **Outer-join report:** retain never-borrowed equipment, make date ties
   deterministic, and test the result with an item that has no loan.
   **Inputs/evidence:** For sql-found-01 Exercise 6, start from `pro_relational_lab.equipment_items`, `LEFT JOIN` `loans`, count the nullable-side `loan_id`, and aggregate the latest `checked_out_on` at item grain.
   **Expected result/shape:** For sql-found-01 Exercise 6, expected output: one row per equipment item with columns `item_id`, `asset_tag`, `loan_count`, and `latest_checkout`, ordered by `asset_tag, item_id`; never-loaned items show zero and NULL.
   **Verify:** For sql-found-01 Exercise 6, assert output row count equals equipment-item count, `AUD-001` has one loan, and `TOL-001` has zero with NULL latest checkout; move a loan-side date predicate between `ON` and `WHERE` and record the preservation difference.
7. **Deletion policy:** choose and defend one referential action for each named
   relationship, including what happens to historical records.
   **Inputs/evidence:** For sql-found-01 Exercise 7, join an expected deletion-policy manifest for all eight implemented foreign keys to `pg_constraint`, translating `confdeltype` into readable referential actions.
   **Expected result/shape:** For sql-found-01 Exercise 7, expected output: eight rows with `relationship`, `expected_action`, `actual_action`, `drift_status`, and `rationale`; category, borrower, equipment, provider, and technician identities use `RESTRICT`, parentless visit-assignment bridges use `CASCADE`, and every row reports `matches`.
   **Verify:** For sql-found-01 Exercise 7, require all eight expected relationships exactly once, compare actions with `pg_get_constraintdef`, attempt one protected parent deletion to observe a foreign-key violation, and verify deleting a disposable visit removes only its dependent assignment rows.
8. **Contract introspection:** prove key, check, generated-value, and uniqueness
   properties from catalogs without depending on generated object names.
   **Inputs/evidence:** For sql-found-01 Exercise 8, inspect `pg_constraint`, `pg_attribute`/`pg_attrdef`, and `pg_index` for `maintenance_visits` without depending on generated object names.
   **Expected result/shape:** For sql-found-01 Exercise 8, expected output: separate deterministic result sets for named constraint identities/types/definitions ordered by `conname`, column/generated-expression metadata, and external-reference unique-index properties including `indnullsnotdistinct`.
   **Verify:** For sql-found-01 Exercise 8, assert one primary key, one item foreign key, the declared CHECK and UNIQUE semantics, `service_days` as a stored generated column with the expected expression, and ordinary NULL-distinct uniqueness; order each result by its own displayed key.

## Self-check

- Can you say what one row means for all five tables without using a vague word
  such as “data”?
- Does every foreign key point from the many side to a declared parent key?
- Can valid absence still use NULL without a fake empty string or zero?
- Do invalid dates, negative costs, duplicates, and orphan identifiers fail at
  the database boundary?
- Can you distinguish a current catalog value from a historical snapshot?
- Does the final `ROLLBACK` leave no `pro_relational_lab` schema behind?

## Common pitfalls

- Starting with columns before defining grain often creates mixed-grain tables.
- A surrogate primary key does not make a meaningful duplicate valid; add the
  natural `UNIQUE` rule when the domain requires it.
- `CHECK (value > 0)` permits NULL unless the column is also `NOT NULL`.
- `DEFAULT` does not replace an explicitly supplied NULL.
- Foreign keys do not automatically create an index on the referencing column.
- Money-like examples use fixed-scale `numeric`, not binary floating point.
- Generated columns are not a place for volatile values such as “today.”
- Normalization is a reasoning tool, not a command to split every table.

## Next step

Resume the numbered sequence at
[SQL-16; window-function fundamentals](../../postgres-60day/companion-guides/day16_window_functions_fundamentals.md).
Continue through SQL-39 before taking SQL-FOUND-02; that later foundation
module combines this lesson's schema design with the transaction and locking
skills needed for safe migrations.

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-found-01: Relational Design, DDL, and Integrity Constraints.

I have completed the direct catalog prerequisite: `sql-15`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_found_01_relational_design.md
- Answer-free learner SQL: sql/professional/lessons/sql_found_01_relational_design.sql

Key terms to teach in context: Grain, Cardinality, Natural key, Surrogate key, Primary key, Foreign key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The example begins with four requirements and turns each into a grain:

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-found-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
