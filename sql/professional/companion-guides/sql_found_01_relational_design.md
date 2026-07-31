# SQL-FOUND-01 — Relational Design, DDL, and Integrity Constraints

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisite:** `sql-15`
- **Prerequisites:** Complete SQL Days 1–15 so you can query, join, aggregate,
  modify, and verify the supplied training schema before designing one of your
  own. PostgreSQL setup and the disposable database are also required.
- **Artifacts:** [learner SQL](../lessons/sql_found_01_relational_design.sql) ·
  [solution reasoning](../solutions/sql_found_01_relational_design_solutions.md) ·
  [executable solution](../solutions/sql_found_01_relational_design_solutions.sql)

Run this portable command from the repository root in Windows PowerShell,
macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_01_relational_design.sql
```

The file creates `pro_relational_lab` inside a transaction and rolls it back.
Expected constraint failures are caught as notices; any unexpected error still
stops the script.

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-FOUND-01 — Relational Design, DDL, and Integrity Constraints** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-found-01/lesson/workspace/sql/professional/lessons/sql_found_01_relational_design.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_found_01_relational_design.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_found_01_relational_design.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

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

These are answer-free worked excerpts from `sql/professional/lessons/sql_found_01_relational_design.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

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
   **Inputs/evidence:** For sql-found-01 Exercise 1, change only `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` rows.
   **Expected result/shape:** For sql-found-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `external_reference`, `service_days`, `completed_on`, `opened_on`, and `coalesce`.
   **Verify:** For sql-found-01 Exercise 1, inspect `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` for `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
2. **Negative cost:** insert one valid visit, isolate the rejected insert in a
   nested block, and verify the expected SQLSTATE category.
   **Inputs/evidence:** For sql-found-01 Exercise 2, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-found-01 Exercise 2, expected output: the command tag and an independently counted set of affected `item_id` values. The final columns are `item_id`.
   **Verify:** For sql-found-01 Exercise 2, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
3. **NULL uniqueness:** insert two NULL references, explain the observed rule,
   and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative.
   **Inputs/evidence:** For sql-found-01 Exercise 3, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-found-01 Exercise 3, expected output: at most one row may have no external reference,” PostgreSQL 15+ supports: That is uncommon for external identifiers. The final columns are `item_id`, `opened_on`, `service_note`, and `NULL`. The final order is `mv.visit_id`.
   **Verify:** For sql-found-01 Exercise 3, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
4. **Historical fee:** state the invariant, the historical question, and why the
   checkout snapshot is or is not deliberate denormalization.
   **Inputs/evidence:** For sql-found-01 Exercise 4, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `daily_fee_at_checkout`; keep `item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-found-01 Exercise 4, expected output: one row per `item_id`. The final columns are `daily_fee_at_checkout`.
   **Verify:** For sql-found-01 Exercise 4, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `daily_fee_at_checkout` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
5. **Many-to-many work:** model providers, technicians, and assignments with
   one declared grain and key per relation; do not use delimited text.
   **Inputs/evidence:** For sql-found-01 Exercise 5, read from `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`. Compute `visit_id`, and `technician_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-found-01 Exercise 5, expected output: one row per provider, one row per technician, and one row per visit/technician assignment. The final columns are `visit_id`, and `technician_id`.
   **Verify:** For sql-found-01 Exercise 5, evaluate each of `technician_id` in a separate control `SELECT` over `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians` using `(mv.external_reference = 'VISIT-100')`; require one final row and compare every value. Add one row for which `(mv.external_reference = 'VISIT-100')` is true and one for which it is false; verify only the matching `visit_id` value is returned.
6. **Outer-join report:** retain never-borrowed equipment, make date ties
   deterministic, and test the result with an item that has no loan.
   **Inputs/evidence:** For sql-found-01 Exercise 6, read from `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`. Build the answer toward `item_id`; keep `item_id`, and `asset_tag` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-found-01 Exercise 6, expected output: one row per `item_id`, and `asset_tag`. The final columns are `item_id`. The final order is `i.asset_tag`.
   **Verify:** For sql-found-01 Exercise 6, independently aggregate `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans` by `item_id`, and `asset_tag`; require one output row for every distinct `item_id`, and `asset_tag` tuple satisfying `(i.asset_tag = 'AUD-001')` and compare `row_count` tuple by tuple. Give two rows the same `i.asset_tag` value and different ``item_id`, and `asset_tag`` values; verify `i.asset_tag` produces the intended rank and display order.
7. **Deletion policy:** choose and defend one referential action for each named
   relationship, including what happens to historical records.
   **Inputs/evidence:** For sql-found-01 Exercise 7, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `maintenance_visits`; keep `item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-found-01 Exercise 7, expected output: one row per `item_id`. The final columns are `maintenance_visits`.
   **Verify:** For sql-found-01 Exercise 7, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `maintenance_visits` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
8. **Contract introspection:** prove key, check, generated-value, and uniqueness
   properties from catalogs without depending on generated object names.
   **Inputs/evidence:** For sql-found-01 Exercise 8, read from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`. Build the answer toward `contype`, and `constraint_definition`; keep `contype` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-found-01 Exercise 8, expected output: one row per `contype`. The final columns are `contype`, and `constraint_definition`. The final order is `a.attnum`.
   **Verify:** For sql-found-01 Exercise 8, project `contype` plus the raw source columns from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef` at each join stage; record row count and distinct `contype`, then assert the final `contype`, and `constraint_definition` values match those staged rows without unintended fanout or loss. Give two rows the same `a.attnum` value and different ``contype`` values; verify `a.attnum` produces the intended rank and display order.

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
[SQL-16 — window-function fundamentals](../../postgres-60day/companion-guides/day16_window_functions_fundamentals.md).
Continue through SQL-39 before taking SQL-FOUND-02; that later foundation
module combines this lesson's schema design with the transaction and locking
skills needed for safe migrations.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

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
lesson reader's Create/open guided SQL notebook action and its ignored
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
