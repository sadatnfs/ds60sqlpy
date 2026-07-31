# Day 60 — Final Capstone, Part 3: End-to-End Sign-off

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 59 — stakeholder analytics](day59_final_capstone_part2.md)
  and completed evidence from the full SQL track
- **Artifacts:** [learner SQL](../day60_final_capstone_part3.sql) ·
  [solution reasoning](../solutions/day60_solutions.md) ·
  [executable solution](../solutions/day60_solutions.sql)

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

2. Open **SQL-60 — Final Capstone Part3** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-60/day60_final_capstone_part3.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day60_final_capstone_part3.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day60_final_capstone_part3.sql
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
on screen are not automatically stored. This lesson introduces or reinforces
Acceptance criterion, Evidence bundle, Handoff. Its worked SQL reads or creates `customers`, `orders`, `order_items`, `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day60_final_capstone_part3.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT * FROM v_dq_customers;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT * FROM v_dq_orders;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Apply explicit acceptance criteria to data quality, business metrics,
  performance evidence, and documentation.
- Produce a handoff that separates verified results, limitations, and future
  production work.

## Vocabulary and concepts

- **Acceptance criterion:** an observable condition required for sign-off.
- **Evidence bundle:** reproducible query, environment, output, reconciliation,
  and interpretation.
- **Handoff:** documentation that lets another person operate, verify, and
  extend the work safely.

## Worked example / walkthrough

Take customer LTV through the final evidence loop: state one-customer grain and
revenue scope, run the view query, reconcile summed LTV with
`SUM(orders.total_amount)`, capture the result and environment, and record any
exception with owner and next action. Apply the same loop to each deliverable.

## Exercises

Complete these in the [learner SQL](../day60_final_capstone_part3.sql):

1. Classify snapshot-independent versus clock-dependent outputs.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Build a named, severity-aware sign-off check result.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. Remove repeated `LAG` calls while preserving first-month NULL growth.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. Mark an incomplete current month separately.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Capture and document before/after JSON plan evidence.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Produce a release checklist covering operations and known limits.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. Map metric lineage from source tables through validation.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
8. Reconcile every dashboard subtotal to a simple control.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. Test empty, one-row, NULL-heavy, and duplicate-key fixtures.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
10. Return `PASS`/`FAIL`/`NOT_RUN` for every acceptance criterion.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Link every sign-off claim to executable evidence.

## Self-check

- Does every sign-off claim have reproducible evidence and a named limitation
  or owner where applicable?
- Are tutorial views and indexes still rollback-only unless a separate reviewed
  migration explicitly persists them?

## Next step

Review any weak SQL areas, then combine both languages in the
[Python and PostgreSQL engineering bridge](../../../bridge/README.md). The
bridge expects at least Python Day 15 and SQL Day 15.

## Deep dive and reference

Day 60 defines acceptance criteria rather than discrete exercises. The final
submission connects reusable DQ checks, business views, stakeholder outputs,
performance evidence, and a written handoff.

## Deliverable 1 — Data quality

- `v_dq_customers`: total rows plus invalid email, country, and name counts.
- `v_dq_orders`: total rows plus negative totals and missing customers.
- Document every nonzero result with remediation, owner, and severity.

## Deliverable 2 — Core business views

- Customer LTV at one row per customer, retaining zero-order customers.
- Monthly order revenue with previous month and safely divided month-over-month
  growth.
- Reconcile summed customer LTV to summed `orders.total_amount`; expected
  difference on the seed is zero.

## Deliverable 3 — Stakeholder outputs

- Finance: current-year budget versus actual by month/category.
- Marketing: active customers by signup cohort and lifecycle month 0–6. A true
  retention rate also needs the cohort-size denominator from Day 47.
- Operations: an actual plan for recent units by product category.

## Deliverable 4 — Performance sign-off

Capture before/after `EXPLAIN (ANALYZE, BUFFERS)` for critical queries and record
dataset size, PostgreSQL version, indexes, timing, buffers, correctness check,
and decision. The requested under-10-second goal applies to the measured learner
machine/dataset; the compact seed does not prove production-scale performance.

## Deliverable 5 — Written handoff

Document DQ exceptions, model grain, join rationale, KPI definitions,
reconciliation, freshness-versus-speed tradeoffs, known limitations, and next
steps. Evidence must support every sign-off claim.

## State and safety

The learner file ends with `ROLLBACK`; its views and indexes do not persist.
Replace it with `COMMIT` only as a deliberate reviewed migration. Days 59–60 are
capstone criteria/checkpoints, so measured evidence and documentation are part
of the deliverable, not optional stretch work.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-60 — Final Capstone Part3.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day60_final_capstone_part3.md
- Answer-free learner SQL: sql/postgres-60day/day60_final_capstone_part3.sql

The lesson concepts include Acceptance criterion, Evidence bundle, Handoff. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-60/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
