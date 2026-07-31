# Day 21 — Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 20 — first, last, and Nth values](day20_first_last_value.md)
- **Artifacts:** [learner SQL](../day21_distribution_functions.sql) ·
  [solution reasoning](../solutions/day21_solutions.md) ·
  [executable solution](../solutions/day21_solutions.sql)

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

2. Open **SQL-21 — Distribution Functions** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-21/lesson/workspace/sql/postgres-60day/day21_distribution_functions.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day21_distribution_functions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day21_distribution_functions.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Quantile bucket, Percent rank, Cumulative distribution. Its worked SQL reads or creates `customers`, `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Apply NTILE(4), PERCENTRANK, and CUMEDIST to a five-row VALUES set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.
The expected contract is that One row per ordering customer with bucket 1–4. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day21_distribution_functions.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH cust_rev AS (
  SELECT c.customer_id,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id
)
SELECT customer_id,
       revenue,
       -- NTILE must assign tied rows to physical buckets; customer_id makes
       -- that assignment reproducible without changing PERCENT_RANK tie rules.
       NTILE(4) OVER (
         ORDER BY revenue DESC, customer_id
       ) AS revenue_quartile,
       ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM cust_rev
ORDER BY revenue DESC, customer_id
LIMIT 50;
```

**How to read it:** Example 1: Start with `customers`, `orders`, and `order_items` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `revenue`, `revenue_quartile`, and `pct_rank`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, capped at 50 rows with columns `customer_id`, `revenue`, `revenue_quartile`, and `pct_rank` from `customers`, `orders`, and `order_items`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH cust_rev AS (
  SELECT c.customer_id,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id
)
SELECT customer_id,
       revenue,
       -- NTILE must assign tied rows to physical buckets; customer_id makes
       -- that assignment reproducible without changing PERCENT_RANK tie rules.
       NTILE(4) OVER (
         ORDER BY revenue DESC, customer_id
       ) AS revenue_quartile,
       ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM cust_rev
ORDER BY revenue DESC, customer_id
LIMIT 50;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `customer_id` key set and row count over `customers`, `orders`, and `order_items`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Place ordered observations into buckets and relative distribution positions.
- Explain tie handling and small-partition limitations.

## Vocabulary and concepts

- **Quantile bucket:** one of N approximately equal row-count groups from
  `NTILE(N)`.
- **Percent rank:** relative rank from 0 through 1 based on rank position.
- **Cumulative distribution:** the fraction of rows less than or equal to the
  current peer group.

## Worked example / walkthrough

Apply `NTILE(4)`, `PERCENT_RANK`, and `CUME_DIST` to a five-row `VALUES` set
containing a tie. Observe that buckets need not have equal value ranges and that
peer-aware distribution functions treat equal ordering values together.

## Practice assumptions and review method

- **Focus:** Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
- **Assumptions:** `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
- **Failure to watch for:** A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Assign customers to four stored-spend buckets.
   **Progressive hint:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.
   **Inputs/evidence:** For sql-21 Exercise 1, read from `orders`. Build the answer toward `customer_id`, `stored_spend`, and `spend_quartile`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 1, expected output: One row per ordering customer with bucket 1–4. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
   **Verify:** For sql-21 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `customer_id`, `stored_spend`, and `spend_quartile`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
2. **Query writing:** Calculate salary percent rank within each department.
   **Progressive hint:** Partition by department and rank on salary alone so tied salaries share rank.
   **Inputs/evidence:** For sql-21 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `salary_percent_rank`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 2, expected output: One row per employee with values from 0 to 1. The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
   **Verify:** For sql-21 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `salary_percent_rank`, then verify output keys remain `employee_id`. Give two rows the same `e.department_id` value and different `e.employee_id` values; verify `e.department_id, e.salary, e.employee_id` produces the intended rank and display order.
3. **Query writing:** Calculate cumulative distribution of product price within category.
   **Progressive hint:** Partition by category and order on price.
   **Inputs/evidence:** For sql-21 Exercise 3, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `price_cume_dist`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 3, expected output: One row per product with cume_dist in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-21 Exercise 3, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `price_cume_dist`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. **Prediction:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
   **Progressive hint:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.
   **Inputs/evidence:** For sql-21 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`; keep `row_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 4, expected output: Three rows making tie behavior visible. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
   **Verify:** For sql-21 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `percent_rank_value`, and `cume_dist_value`, then verify output keys remain `row_id`. Give two rows the same `row_id` value and different ``row_id`` values; verify `row_id` produces the intended rank and display order.
5. **Debugging:** Audit the row count in each customer spend decile rather than assuming exact equality.
   **Progressive hint:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.
   **Inputs/evidence:** For sql-21 Exercise 5, read from `orders`. Build the answer toward `decile`, and `customers`; keep `decile` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 5, expected output: Up to 10 bucket rows with counts. The final columns are `decile`, and `customers`. The final order is `decile`.
   **Verify:** For sql-21 Exercise 5, independently aggregate `orders` by `decile`; require one output row for every distinct `decile` tuple and compare `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers` for the existing `decile` tuple and verify the new tuple appears exactly once.
6. **Extension:** Return customers in the top stored-spend decile with their spend and population share.
   **Progressive hint:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
   **Inputs/evidence:** For sql-21 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `total_spend`, `decile`, and `population`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-21 Exercise 6, expected output: Customers in decile 1. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
   **Verify:** For sql-21 Exercise 6, run an anti-check that counts rows where NOT ((decile = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `total_spend`, `decile`, and `population` against `orders`. Give two rows the same `total_spend DESC` value and different `customer_id` values; verify `total_spend DESC, customer_id` produces the intended rank and display order.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A percentile rank is not a probability or causal score, and NTILE(10) does not guarantee equal value ranges.
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

- Are the outputs described as row-position summaries rather than guaranteed
  business segments?
- Can you explain how ties affect each function?

## Next step

Continue to [Day 22 — advanced windows](day22_advanced_windows.md).

## Deep dive and reference

Learning objectives
- Bin ordered data into quantiles/tiles with NTILE
- Compute relative position within a partition via PERCENT_RANK and CUME_DIST
- Use distribution metrics for scoring, segmentation, and anomaly thresholds

Why this matters
Quantiles and ranks model relative standing robustly in skewed data and support thresholding without assuming normality.

Core concepts and deep dive
- NTILE(n) OVER (PARTITION BY k ORDER BY x): assigns tile indices 1..n with sizes as equal as possible.
- PERCENT_RANK() = (rank-1) / (count-1); 0 to 1 inclusive; undefined for single-row partitions (returns 0).
- CUME_DIST() = (number of rows with value <= current) / count; non-decreasing; useful for percentile-style thresholds.

Patterns
- Score bands: NTILE(10) deciles for customers by LTV.
- Top x% filters: WHERE CUME_DIST() OVER (...) >= 0.95 to flag extremes.
- Percentile thresholds: compute p95 within groups and join back.

Pitfalls
- Non-unique ORDER BY yields arbitrary rankings among ties; define tie policy.
- NTILE with small partitions creates imbalanced tiles; consider minimum partition size.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Distribution: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-21 — Distribution Functions.

I have completed the direct catalog prerequisite: `sql-20`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day21_distribution_functions.md
- Answer-free learner SQL: sql/postgres-60day/day21_distribution_functions.sql

Key terms to teach in context: Quantile bucket, Percent rank, Cumulative distribution. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Apply NTILE(4), PERCENTRANK, and CUMEDIST to a five-row VALUES set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-21/ working copy. Never point setup, reset, DDL, or DML
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
