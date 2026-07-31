# Day 17 — Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 16 — window-function fundamentals](day16_window_functions_fundamentals.md)
- **Artifacts:** [learner SQL](../day17_rank_functions.sql) ·
  [solution reasoning](../solutions/day17_solutions.md) ·
  [executable solution](../solutions/day17_solutions.sql)

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

2. Open **SQL-17 — Rank Functions** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-17/lesson/workspace/sql/postgres-60day/day17_rank_functions.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day17_rank_functions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day17_rank_functions.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Peer rows, Gap rank, Dense rank. Its worked SQL reads or creates `customers`, `orders`, `order_items`, `employees`, `departments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Rank two products with equal revenue using ROWNUMBER, RANK, and DENSERANK. Add productid as the last ORDER BY key when the requirement is exactly five deterministic rows; omit that tie-breaker when equal metrics must share a business rank.
The expected contract is that One row per order with sequence starting at one per customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day17_rank_functions.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH cust_rev AS (
  SELECT c.customer_id,
         c.full_name,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id,
       full_name,
       revenue,
       ROW_NUMBER() OVER (
         ORDER BY revenue DESC, customer_id
       ) AS row_num,
       RANK()       OVER (ORDER BY revenue DESC) AS rank_pos,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_pos
FROM cust_rev
ORDER BY revenue DESC, customer_id
LIMIT 30;
```

**How to read it:** Example 1: Start with `customers`, `orders`, and `order_items` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `full_name`, `revenue`, `row_num`, `rank_pos`, and `dense_rank_pos`. `ORDER BY` determines presentation order and the final `LIMIT 30` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, capped at 30 rows with columns `customer_id`, `full_name`, `revenue`, `row_num`, `rank_pos`, and `dense_rank_pos` from `customers`, `orders`, and `order_items`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT e.department_id,
       d.name AS department,
       e.employee_id,
       e.full_name,
       e.salary,
       RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_rank
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY department NULLS LAST,
         dept_rank,
         e.salary DESC,
         e.employee_id
LIMIT 50;
```

**How to read it:** Example 2: Start with `employees`, and `departments` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `department_id`, `department`, `employee_id`, `full_name`, `salary`, and `dept_rank`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `department_id`, and `employee_id`, capped at 50 rows with columns `department_id`, `department`, `employee_id`, `full_name`, `salary`, and `dept_rank` from `employees`, and `departments`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Choose a ranking function whose tie behavior matches the requirement.
- Produce deterministic top-N-per-group results.

## Vocabulary and concepts

- **Peer rows:** rows equal on the window's `ORDER BY` expressions.
- **Gap rank:** `RANK` gives peers the same rank and leaves gaps afterward.
- **Dense rank:** `DENSE_RANK` gives peers the same rank without gaps.

## Worked example / walkthrough

Rank two products with equal revenue using `ROW_NUMBER`, `RANK`, and
`DENSE_RANK`. Add `product_id` as the last `ORDER BY` key when the requirement
is exactly five deterministic rows; omit that tie-breaker when equal metrics
must share a business rank.

## Practice assumptions and review method

- **Focus:** Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
- **Assumptions:** All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
- **Failure to watch for:** `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Number each customer's orders from newest to oldest.
   **Progressive hint:** Partition by customer and use order date plus order ID as a unique descending order.
   **Inputs/evidence:** For sql-17 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `recency_number`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 1, expected output: One row per order with sequence starting at one per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
   **Verify:** For sql-17 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, then verify output keys remain `order_id`. Give two rows the same `o.customer_id` value and different `recency_number` values; verify `o.customer_id, recency_number` produces the intended rank and display order.
2. **Query writing:** Rank products by price within category using both `RANK` and `DENSE_RANK`.
   **Progressive hint:** Rank only on price so equal prices tie; order the final display by product ID.
   **Inputs/evidence:** For sql-17 Exercise 2, read from `products`. Build the answer toward `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 2, expected output: One row per product with two rank semantics. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
   **Verify:** For sql-17 Exercise 2, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `price_rank`, and `dense_price_rank`, then verify output keys remain `product_id`. Give two rows the same `p.category` value and different `p.product_id` values; verify `p.category, p.price DESC, p.product_id` produces the intended rank and display order.
3. **Query writing:** Return the three highest-priced products per category, including price ties.
   **Progressive hint:** Compute `DENSE_RANK` in a CTE and filter outside.
   **Inputs/evidence:** For sql-17 Exercise 3, read from `products`. Build the answer toward `product_id`, `name`, `category`, `price`, and `price_rank`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 3, expected output: At least three price levels per category where available. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
   **Verify:** For sql-17 Exercise 3, run an anti-check that counts rows where NOT ((price_rank <= 3)); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, `category`, `price`, and `price_rank` against `products`. Give two rows the same `category` value and different `product_id` values; verify `category, price_rank, product_id` produces the intended rank and display order.
4. **Prediction:** Compare row number, rank, and dense rank on values 100, 100, and 90.
   **Progressive hint:** Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
   **Inputs/evidence:** For sql-17 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`; keep `sample_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
   **Verify:** For sql-17 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `score`, `row_number_value`, `rank_value`, and `dense_rank_value`, then verify output keys remain `sample_id`. Give two rows the same `sample_id` value and different ``sample_id`` values; verify `sample_id` produces the intended rank and display order.
5. **Debugging:** Return exactly one latest order per customer even when timestamps tie.
   **Progressive hint:** Use row number with the unique order ID as final tie-breaker.
   **Inputs/evidence:** For sql-17 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 5, expected output: At most one row per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
   **Verify:** For sql-17 Exercise 5, run an anti-check that counts rows where NOT ((recency_number = 1)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, and `total_amount` against `orders`. Give two rows the same `customer_id` value and different ``order_id`` values; verify `customer_id` produces the intended rank and display order.
6. **Extension:** Rank employee salaries within department and show only the top two distinct salary levels.
   **Progressive hint:** Dense rank includes all employees tied at either of the top two salary values.
   **Inputs/evidence:** For sql-17 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-17 Exercise 6, expected output: Top two salary levels per department. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
   **Verify:** For sql-17 Exercise 6, run an anti-check that counts rows where NOT ((salary_rank <= 2)); require unique `employee_id` where the expected grain is one row per key and confirm the projected `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank` against `employees`. Give two rows the same `department_id` value and different `employee_id` values; verify `department_id, salary_rank, employee_id` produces the intended rank and display order.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** ROWNUMBER breaks ties, RANK leaves gaps, and DENSERANK does not; using the wrong function changes top-N membership.
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

- Is the requirement “exactly N rows” or “all rows tied in the top N ranks”?
- Does the ordering include a stable key where deterministic selection matters?

## Next step

Continue to [Day 18 — LAG and LEAD](day18_lag_lead.md).

## Deep dive and reference

Learning objectives
- Assign row ordinals and ranks within partitions using ORDER BY
- Choose the correct rank function for ties and pagination
- Build top-k per group, leaderboards, and tie-aware analytics

Why this matters
Ranking underpins “top N per X”, de-duplicating, and cohort benchmarking. Picking the right function controls tie behavior, which changes results and business meaning.

Core concepts and deep dive
- ROW_NUMBER() OVER (PARTITION BY k ORDER BY t): assigns 1,2,3… with no ties (deterministic if ORDER BY unique). Use for de-duplication (keep first per key).
- RANK(): equal sort values receive the same rank; leaves gaps after ties (1,1,3…).
- DENSE_RANK(): equal values share rank without gaps (1,1,2…).
- ORDER BY determinism: When values tie, add a tiebreaker column to produce stable ordering (e.g., ORDER BY amt DESC, order_id ASC).

Patterns
- Top-k per group: WHERE rn <= k after wrapping ROW_NUMBER in a subquery/CTE.
- Category leaders: DENSE_RANK by revenue within category; pick rank <= 3 for top-3 allowing ties.
- Latest records per entity: ROW_NUMBER ordered by timestamp DESC; keep rn=1.

Pitfalls
- Using RANK when you need exactly k rows per group; ties may exceed k (use ROW_NUMBER) or allow overflow intentionally.
- Non-deterministic ordering when ORDER BY is not unique; results can fluctuate.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Ranking: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-17 — Rank Functions.

I have completed the direct catalog prerequisite: `sql-16`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day17_rank_functions.md
- Answer-free learner SQL: sql/postgres-60day/day17_rank_functions.sql

Key terms to teach in context: Peer rows, Gap rank, Dense rank. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Rank two products with equal revenue using ROWNUMBER, RANK, and DENSERANK. Add productid as the last ORDER BY key when the requirement is exactly five deterministic rows; omit that tie-breaker when equal metrics must share a business rank.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-17/ working copy. Never point setup, reset, DDL, or DML
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
