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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-21/day21_distribution_functions.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Quantile bucket, Percent rank, Cumulative distribution. Its worked SQL reads or creates `customers`, `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Apply NTILE(4), PERCENTRANK, and CUMEDIST to a five-row VALUES set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.
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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per ordering customer with bucket 1–4.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per ordering customer with bucket 1–4.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Calculate salary percent rank within each department.
   **Progressive hint:** Partition by department and rank on salary alone so tied salaries share rank.
   **Expected shape:** One row per employee with values from 0 to 1.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Calculate cumulative distribution of product price within category.
   **Progressive hint:** Partition by category and order on price.
   **Expected shape:** One row per product with cume_dist in (0, 1].
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
   **Progressive hint:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.
   **Expected shape:** Three rows making tie behavior visible.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Audit the row count in each customer spend decile rather than assuming exact equality.
   **Progressive hint:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.
   **Expected shape:** Up to 10 bucket rows with counts.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Return customers in the top stored-spend decile with their spend and population share.
   **Progressive hint:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
   **Expected shape:** Customers in decile 1.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day21_distribution_functions.md
- Answer-free learner SQL: sql/postgres-60day/day21_distribution_functions.sql

The lesson concepts include Quantile bucket, Percent rank, Cumulative distribution. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Apply NTILE(4), PERCENTRANK, and CUMEDIST to a five-row VALUES set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-21/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
