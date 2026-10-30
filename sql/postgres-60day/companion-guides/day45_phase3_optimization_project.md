# Day 45: Phase 3 Optimization Project

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-45**. The
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
   `.learning/sql/sql-45/lesson/workspace/sql/postgres-60day/day45_phase3_optimization_project.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-45
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 44; monitoring and diagnostics](day44_monitoring_diagnostics.md)
  and the complete performance sequence from Days 31–44
- **Artifacts:** [learner SQL](../day45_phase3_optimization_project.sql) ·
  [solution reasoning](../solutions/day45_solutions.md) ·
  [executable solution](../solutions/day45_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Experimental control, Buffer evidence, Regression check. Its worked SQL reads or creates `customers`, `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.
The first runnable example has a concrete contract: Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `country` key set and row count over `customers`, `orders`, and `order_items`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan. Its final projection is `country`. Run the underlying query without `EXPLAIN` first; preserve its keys and row count, then compare estimates with actual rows × loops and read buffer/timing evidence without requiring one fixed node type. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day45_phase3_optimization_project.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
EXPLAIN ANALYZE
SELECT
  c.country,
  SUM(oi.quantity)
FROM
  customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')
GROUP BY
  c.country
ORDER BY
  2 DESC;
```

**How to read it:** Example 1 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `country` key set and row count over `customers`, `orders`, and `order_items`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

### Example 2

```sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date_only ON orders (order_date);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `idx_orders_order_date_only`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Run a controlled optimization experiment with comparable plans and outputs.
- Report measured improvement honestly, including a result below the target.

## Vocabulary and concepts

- **Experimental control:** fixed query semantics, data, parameters, and
  environment for a comparison.
- **Buffer evidence:** shared/local block hits, reads, dirties, and writes
  reported by `BUFFERS`.
- **Regression check:** proof that a rewrite preserves the defined output.

## Worked example / walkthrough

Capture the function-wrapped date baseline, rewrite it as a raw half-open range,
and add one candidate index inside the rollback transaction. Run both forms
several times, reconcile country/unit results, and calculate percentage change
from comparable observations without promising 70%.

## Exercises

Complete these in the
[learner SQL](../day45_phase3_optimization_project.sql):

1. Predict the effect of replacing the non-sargable timestamp expression.
   **Inputs/evidence:** For sql-45 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-45 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-45 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Capture/compare JSON plans for baseline and rewrite.
   **Inputs/evidence:** For sql-45 Exercise 2, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-45 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
   **Verify:** For sql-45 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Prove direct and pre-aggregated results equivalent with two-way `EXCEPT`.
   **Inputs/evidence:** For sql-45 Exercise 3, read from `orders`, `customers`, and `order_items`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-45 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
   **Verify:** For sql-45 Exercise 3, project `order_id` plus the raw source columns from `orders`, `customers`, and `order_items` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
4. Test an empty-window boundary.
   **Inputs/evidence:** For sql-45 Exercise 4, read from `orders`. Build the answer toward `impossible_window_rows`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-45 Exercise 4, expected output: one row per `order_id`. The final columns are `impossible_window_rows`.
   **Verify:** For sql-45 Exercise 4, run an anti-check that counts rows where NOT ((order_date >= timestamptz '1900-01-01 00:00:00+00' AND order_date < timestamptz '1900-01-02 00:00:00+00')); require unique `order_id` where the expected grain is one row per key and confirm the projected `impossible_window_rows` against `orders`. Insert rows immediately before, exactly at, and immediately after `order_date >= timestamptz '1900-01-01 00:00:00+00'`, and `order_date < timestamptz '1900-01-02 00:00:00+00'`; identify which rows pass each inclusive or exclusive comparison.
5. Design and justify one workload-specific index.
   **Inputs/evidence:** For sql-45 Exercise 5, read from `pg_indexes`. Build the answer toward `indexname`, and `indexdef`; keep `indexname` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-45 Exercise 5, expected output: one row per `indexname`. The final columns are `indexname`, and `indexdef`. The final order is `indexname`.
   **Verify:** For sql-45 Exercise 5, run an anti-check that counts rows where NOT ((schemaname = 'training' AND indexname LIKE '%solution')); require unique `indexname` where the expected grain is one row per key and confirm the projected `indexname`, and `indexdef` against `pg_indexes`. Add one row for which `(schemaname = 'training' AND indexname LIKE '%solution')` is true and one for which it is false; verify only the matching `indexname` value is returned.
6. Write an optimization report separating semantics, plans, and timing.
   **Inputs/evidence:** For sql-45 Exercise 6, complete the write an optimization report separating semantics plans and  written analysis and support its claims with read-only evidence from `customers`, `orders`, and `order_items`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-45 Exercise 6, expected output: a completed the write an optimization report separating semantics plans and  written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-45 Exercise 6, check the write an optimization report separating semantics plans and  written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

Produce a decision record covering plan, buffers, correctness, index cost, and
whether the candidate should proceed.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Are result keys and totals identical before performance is discussed?
- Does the recommendation distinguish the compact seed from representative
  production-scale evidence?

## Next step

Continue to [Day 46; e-commerce LTV and cohorts](day46_project1_ecommerce_part1.md).

## Deep dive and reference

## Project goal

Measure a recent country-units query, make its predicate and aggregation more
efficient, and attempt to reduce runtime by more than 70% without changing the
result.

## What the learner script compares

1. A baseline whose date filter wraps `orders.order_date` in `date_trunc`.
2. A sargable raw-column date range after adding an `orders(order_date)` index.
3. A rewrite that pre-aggregates `order_items.quantity` by `order_id` before the
   country rollup.

All DDL and plans are inside a transaction and roll back.

## Evidence to collect

- exact SQL and seed/setup version;
- row counts and country-to-units totals for correctness;
- `EXPLAIN (ANALYZE, BUFFERS)` before and after;
- execution time, shared buffer hits/reads, rows, loops, and scan/join types;
- candidate index size and expected write cost; and
- percentage improvement calculated from comparable timings.

## Optimization reasoning

- A raw `order_date >= boundary` predicate can use a normal B-tree range.
- Set-based pre-aggregation avoids repeated line-level work.
- A covering order-item index may help but remains a measured candidate.
- Small tables can legitimately use sequential scans.

## The 70% target is not guaranteed

The target is an experiment goal, not a promised result on the compact
deterministic seed. Planning overhead, cache state, and small table size can
dominate. Report the observed percentage honestly, reconcile outputs, and use a
representative-scale dataset before recommending production changes.

Production index creation requires a separate reviewed migration and may need
`CREATE INDEX CONCURRENTLY`; the tutorial transaction intentionally persists
nothing.

## Expanded practice lab

The six explicit prompts make this a measured project instead of a single
rewrite. Begin with a prediction, capture JSON plans, and prove equivalence with
two-way `EXCEPT` before comparing performance. JSON makes the root execution
time and buffer fields machine-readable, but repeated trials and environment
notes are still required.

Test the empty-window boundary and document any proposed index as a workload
tradeoff, not free speed. The final report must keep three claims separate:
same result semantics, observed planner evidence, and timing that may change on
different hardware, cache state, cardinality, or PostgreSQL versions.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-45 — Phase3 Optimization Project.

I have completed the direct catalog prerequisite: `sql-44`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day45_phase3_optimization_project.md
- Answer-free learner SQL: sql/postgres-60day/day45_phase3_optimization_project.sql

Key terms to teach in context: Experimental control, Buffer evidence, Regression check. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-45/ working copy. Never point setup, reset, DDL, or DML
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
