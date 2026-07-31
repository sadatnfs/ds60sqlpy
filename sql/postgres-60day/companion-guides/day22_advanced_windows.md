# Day 22 — Advanced Windows: Multiple Partitions, Named Windows, Exclusion (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 21 — distribution functions](day21_distribution_functions.md)
- **Artifacts:** [learner SQL](../day22_advanced_windows.sql) ·
  [solution reasoning](../solutions/day22_solutions.md) ·
  [executable solution](../solutions/day22_solutions.sql)

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

2. Open **SQL-22 — Advanced Windows** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-22/lesson/workspace/sql/postgres-60day/day22_advanced_windows.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day22_advanced_windows.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day22_advanced_windows.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Named window, Peer exclusion, Mixed grain. Its worked SQL reads or creates `order_items`, `products`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate revenue to (country, category) first. Rank categories within each country from that relation, then calculate a separate category-total relation for the overall rank. Joining those stable grains avoids incorrectly ranking every country/category pair as though it were one global category.
The expected contract is that One row per order. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day22_advanced_windows.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH prod_rev AS (
  SELECT p.product_id,
         p.name,
         p.category,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT *,
  RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
  RANK() OVER (ORDER BY revenue DESC) AS rank_overall
FROM prod_rev
ORDER BY category, rank_in_category, revenue DESC, product_id
LIMIT 100;
```

**How to read it:** Example 1: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `*`, `rank_in_category`, and `rank_overall`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `*`, capped at 100 rows with columns `*`, `rank_in_category`, and `rank_overall` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT o.customer_id,
       o.order_id,
       o.total_amount,
       AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS avg_per_customer,
       SUM(o.total_amount) OVER () AS total_revenue_all,
       RANK() OVER (PARTITION BY o.customer_id ORDER BY o.total_amount DESC) AS order_value_rank
FROM orders o
ORDER BY o.customer_id,
         order_value_rank,
         o.total_amount DESC,
         o.order_id
LIMIT 100;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `order_id`, `total_amount`, `avg_per_customer`, `total_revenue_all`, and `order_value_rank`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns exactly one summary row, capped at 100 rows with columns `customer_id`, `order_id`, `total_amount`, `avg_per_customer`, `total_revenue_all`, and `order_value_rank` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Combine local and global windows at a stable grain.
- Reuse named window specifications and exclude current rows or peers when
  required.

## Vocabulary and concepts

- **Named window:** a reusable `WINDOW name AS (...)` specification.
- **Peer exclusion:** removal of the current row, its peers, or ties from a
  frame.
- **Mixed grain:** an unsafe calculation that combines measures defined at
  different row meanings.

## Worked example / walkthrough

Aggregate revenue to `(country, category)` first. Rank categories within each
country from that relation, then calculate a separate category-total relation
for the overall rank. Joining those stable grains avoids incorrectly ranking
every country/category pair as though it were one global category.

## Practice assumptions and review method

- **Focus:** Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
- **Assumptions:** Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
- **Failure to watch for:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Use a named window to show each order with customer count, average, first date, and last date.
   **Progressive hint:** Name a full-partition customer window once and reuse it.
   **Inputs/evidence:** For sql-22 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-22 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
2. **Query writing:** Compare each employee salary with the average of other employees in the department.
   **Progressive hint:** Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
   **Inputs/evidence:** For sql-22 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `other_employee_average`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 2, expected output: One row per employee with nullable peer average. The final columns are `employee_id`, `department_id`, `salary`, and `other_employee_average`. The final order is `e.department_id, e.employee_id`.
   **Verify:** For sql-22 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `other_employee_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
3. **Query writing:** Show each order's distance from its customer's average and standard deviation.
   **Progressive hint:** Compute independent partition windows and guard interpretation when variation is zero.
   **Inputs/evidence:** For sql-22 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 3, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-22 Exercise 3, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
4. **Prediction:** Sessionize events using a 30-minute gap and predict why the first event starts a session.
   **Progressive hint:** Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
   **Inputs/evidence:** For sql-22 Exercise 4, read from `events`. Build the answer toward `event_id`, `customer_id`, `event_time`, and `session_number`; keep `event_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 4, expected output: One row per event with session number starting at one. The final columns are `event_id`, `customer_id`, `event_time`, and `session_number`. The final order is `customer_id, event_time, event_id`.
   **Verify:** For sql-22 Exercise 4, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `event_time`, then verify output keys remain `event_id`. Use a one-row partition and a partition tied on `customer_id`; verify `event_id` and `customer_id, event_time, event_id` preserve the intended first/last row.
5. **Debugging:** Find consecutive calendar-day islands in customer order dates without nesting windows.
   **Progressive hint:** Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
   **Inputs/evidence:** For sql-22 Exercise 5, read from `orders`. Build the answer toward `customer_id`, `island_start`, `island_end`, and `days_in_island`; keep `customer_id`, and `island_key` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 5, expected output: One row per customer/date island. The final columns are `customer_id`, `island_start`, `island_end`, and `days_in_island`. The final order is `customer_id, island_start`.
   **Verify:** For sql-22 Exercise 5, independently aggregate `orders` by `customer_id`, and `island_key`; require one output row for every distinct `customer_id`, and `island_key` tuple and compare `island_start`, `island_end`, and `days_in_island` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `days_in_island` for the existing `customer_id`, and `island_key` tuple and verify the new tuple appears exactly once.
6. **Extension:** Summarize sessions from the sessionized event stream with start, end, event count, and duration.
   **Progressive hint:** Aggregate only after session IDs exist at event grain.
   **Inputs/evidence:** For sql-22 Exercise 6, read from `events`. Build the answer toward `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`; keep `customer_id`, and `session_number` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-22 Exercise 6, expected output: One row per customer session. The final columns are `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`. The final order is `customer_id, session_number`.
   **Verify:** For sql-22 Exercise 6, independently aggregate `events` by `customer_id`, and `session_number`; require one output row for every distinct `customer_id`, and `session_number` tuple and compare `event_count`, and `session_duration` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `event_count`, and `session_duration` for the existing `customer_id`, and `session_number` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
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

- Can you state the grain before every window layer?
- Does an excluded-row calculation handle one-row partitions without dividing
  by zero?

## Next step

Continue to [Day 23 — common table expressions](day23_ctes_intro.md).

## Deep dive and reference

Learning objectives
- Reuse window specs with WINDOW clause and combine multiple windows efficiently
- Use EXCLUDE to omit current row/peers from aggregates
- Optimize window queries with pre-aggregation and indexing

Why this matters
Complex analytics often require many windowed metrics at different grains. Clean specs and performance awareness keep queries readable and fast.

Core concepts and deep dive
- WINDOW w AS (PARTITION BY k ORDER BY t): define once, reuse across functions.
- EXCLUDE CURRENT ROW/EXCLUDE TIES to remove the current row or equal-ordered peers from an aggregate (e.g., average of others).
- Mixed grains: daily pre-aggregate then window across days, not raw events.
- Indexing: multi-column btree on (k, t) supports partitioned sorts; work_mem affects window performance.

Patterns
- Leave-one-out mean: (SUM(x) OVER w - x) / NULLIF(COUNT(*) OVER w - 1, 0) with EXCLUDE CURRENT ROW.
- Cross-window features: per-customer cumulative plus global cumulative in one SELECT using named windows w1 (partitioned) and w2 (global).

Pitfalls
- Window after GROUP BY changes row cardinality; ensure you window the intended grain.
- Excessive repeated specs without WINDOW harms readability.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WINDOW clause: https://www.postgresql.org/docs/current/sql-select.html#SQL-WINDOW
- Exclusion: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-22 — Advanced Windows.

I have completed the direct catalog prerequisite: `sql-21`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day22_advanced_windows.md
- Answer-free learner SQL: sql/postgres-60day/day22_advanced_windows.sql

Key terms to teach in context: Named window, Peer exclusion, Mixed grain. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate revenue to (country, category) first. Rank categories within each country from that relation, then calculate a separate category-total relation for the overall rank. Joining those stable grains avoids incorrectly ranking every country/category pair as though it were one global category.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-22/ working copy. Never point setup, reset, DDL, or DML
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
