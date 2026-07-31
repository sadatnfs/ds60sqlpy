# SQL-FOUND-01 — Relational Design, DDL, and Integrity Constraints

## Level and prerequisites

- **Level:** Foundation
- **Catalog prerequisites:** none
- **Prerequisites:** PostgreSQL setup and comfort running a `.sql` file with
  `psql`; no earlier SQL lesson is required.
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
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** Exercise 1 must make “Maintenance DDL: translate every visit requirement into a column, constraint, key, default, or generated expression; annotate the table grain” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`.
   **Verify:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
2. **Negative cost:** insert one valid visit, isolate the rejected insert in a
   nested block, and verify the expected SQLSTATE category.
   **Expected result/shape:** Exercise 2 needs a labeled transaction/session transcript that demonstrates “Negative cost: insert one valid visit, isolate the rejected insert in a nested block, and verify the expected SQLSTATE category”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `service`, `i`, `sqlstate`.
   **Verify:** For Exercise 2, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
3. **NULL uniqueness:** insert two NULL references, explain the observed rule,
   and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative.
   **Expected result/shape:** Exercise 3 requires a written prediction and the observed result for “NULL uniqueness: insert two NULL references, explain the observed rule, and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `i`, `dates`, `mv`.
   **Verify:** For Exercise 3, run the two forms over the identical rows in `pro_relational_lab.maintenance_visits`, `pro_relational_lab.equipment_items`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
4. **Historical fee:** state the invariant, the historical question, and why the
   checkout snapshot is or is not deliberate denormalization.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Historical fee: state the invariant, the historical question, and why the checkout snapshot is or is not deliberate denormalization”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Many-to-many work:** model providers, technicians, and assignments with
   one declared grain and key per relation; do not use delimited text.
   **Expected result/shape:** Exercise 5 must make “Many-to-many work: model providers, technicians, and assignments with one declared grain and key per relation; do not use delimited text” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`.
   **Verify:** For Exercise 5, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
6. **Outer-join report:** retain never-borrowed equipment, make date ties
   deterministic, and test the result with an item that has no loan.
   **Expected result/shape:** Exercise 6 must make “Outer-join report: retain never-borrowed equipment, make date ties deterministic, and test the result with an item that has no loan” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
7. **Deletion policy:** choose and defend one referential action for each named
   relationship, including what happens to historical records.
   **Expected result/shape:** Exercise 7 must make “Deletion policy: choose and defend one referential action for each named relationship, including what happens to historical records” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `historical`.
   **Verify:** For Exercise 7, inspect the relevant `pg_catalog` or `information_schema` rows for `historical`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
8. **Contract introspection:** prove key, check, generated-value, and uniqueness
   properties from catalogs without depending on generated object names.
   **Expected result/shape:** Exercise 8 returns a table-shaped answer to “Contract introspection: prove key, check, generated-value, and uniqueness properties from catalogs without depending on generated object names” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `constraint_definition`, `con`, `rel`, `n`, `column_name`, `generated_expression`, `def`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, `pg_catalog.pg_attrdef`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.

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

Continue to [SQL-FOUND-02 — versioned schema migrations](sql_found_02_versioned_migrations.md)
to evolve a schema without rewriting deployment history. Then begin the
[numbered SQL track](../../postgres-60day/README.md) and query a larger supplied
model.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-found-01 — Relational Design, DDL, and Integrity Constraints.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
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
