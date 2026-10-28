# SQL-FOUND-01: Relational Design, DDL, and Integrity Constraints

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-found-01**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-found-01/lesson/workspace/sql/professional/lessons/sql_found_01_relational_design.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-found-01
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisite:** `sql-15`; [SQL Day 15; Phase 1 Project](../../postgres-60day/companion-guides/day15_phase1_project.md)
- **Prerequisites:** Complete SQL Days 1–15 so you can query, join, aggregate,
  modify, and verify the supplied training schema before designing one of your
  own. PostgreSQL setup and the disposable database are also required.
- **Artifacts:** [learner SQL](../lessons/sql_found_01_relational_design.sql) ·
  [solution reasoning](../solutions/sql_found_01_relational_design_solutions.md) ·
  [executable solution](../solutions/sql_found_01_relational_design_solutions.sql)

Use the Docker classroom workflow below for this cataloged script. The optional
contributor route requires its own prepared interpreter, psql client and
explicit disposable-database connection.

The file creates `pro_relational_lab` inside a transaction and rolls it back.
Expected constraint failures are caught as notices; any unexpected error still
stops the script.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Grain, Cardinality, Natural key, Surrogate key, Primary key, Foreign key. Its worked SQL reads or creates `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The example begins with four requirements and turns each into a grain:
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_relational_lab.members`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These worked excerpts come from `sql/professional/lessons/sql_found_01_relational_design.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
CREATE TABLE pro_relational_lab.members (
    member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name text NOT NULL
        CHECK (btrim(display_name) <> ''),
    email text NOT NULL UNIQUE,
    backup_contact text UNIQUE,
    joined_on date NOT NULL DEFAULT CURRENT_DATE
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_relational_lab.members`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE pro_relational_lab.equipment_categories (
    category_code text PRIMARY KEY,
    display_name text NOT NULL UNIQUE,
    standard_loan_days integer NOT NULL
        CHECK (standard_loan_days BETWEEN 1 AND 90)
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `pro_relational_lab.equipment_categories`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

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

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-found-01 — Relational Design, DDL, and Integrity Constraints.

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
