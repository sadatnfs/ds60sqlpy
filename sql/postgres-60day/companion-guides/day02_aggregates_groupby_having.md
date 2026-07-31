# Day 02 — Aggregations, GROUP BY, HAVING, Grouping Sets (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 01 — SELECT, filtering, and ordering](day01_select_where_orderby.md)
- **Artifacts:** [learner SQL](../day02_aggregates_groupby_having.sql) ·
  [solution reasoning](../solutions/day02_solutions.md) ·
  [executable solution](../solutions/day02_solutions.sql)

## How to run this lesson

The rendered page explains the ideas; PostgreSQL runs the real learner file.
For a first attempt, use the private course portal so the target database,
ignored working copy, and complete `psql` transcript stay visible.

1. From the repository root, start the portal:

   ```powershell
   # Windows PowerShell (or double-click START_DS60.cmd)
   .\START_DS60.cmd
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-02**, choose **Create/open guided SQL notebook**, and run the
   readiness cells in order. The notebook accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned `training` schema, set `CONFIRM_COURSE_RESET = True` and run
   that cell. Preparation loads and verifies deterministic seed data.
4. Edit the ignored working copy at
   `.learning/sql/sql-02/lesson/workspace/sql/postgres-60day/day02_aggregates_groupby_having.sql`, save it, then run the
   notebook's full-script cell. It uses
   `psql -X -v ON_ERROR_STOP=1 -f`, so the learner file's transaction and
   `psql` commands behave exactly as written.
5. Read each table-shaped result below the cell. Success means no `ERROR`, an
   exit code of 0, the final `ROLLBACK`, and a passing database-verification
   cell. `ROLLBACK` restores the starting data after the experiments.

Direct terminal alternative:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\\postgres-60day\\day02_aggregates_groupby_having.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day02_aggregates_groupby_having.sql
```

The terminal becomes the output surface. If `psql` is not recognized on
Windows, relaunch with `START_DS60.cmd`; it can discover PostgreSQL for the
current process. If the database or a `training` relation is missing, return
to the preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor rather than placing a password in
SQL, a notebook, or Git. With `ON_ERROR_STOP`, fix the first error and rerun
the whole script; do not trust output produced after a partial manual run.

## A beginner's mental model for this lesson

A **table** is stored data with named columns. A **row** is one occurrence of
the table's subject. A query produces a temporary **result set**; seeing rows
on screen does not mean the stored tables changed. The **grain** is what one
result row represents. Here the inputs are training.orders, and the intended
grain is one row per grouping key, such as one row per order status.

Read the main query as a pipeline: FROM supplies orders; WHERE removes rows before grouping; GROUP BY forms buckets; aggregate functions reduce each bucket; HAVING filters completed buckets; ORDER BY arranges the summaries. For ordinary analytical
queries, the useful logical reading order is `FROM/JOIN` → `WHERE` →
`GROUP BY`/aggregates → `HAVING` → window calculations → `SELECT` →
`ORDER BY` → `LIMIT`. This is a reasoning model, not a promise about the
physical plan PostgreSQL chooses.

Before running, write the expected column names and row grain in a comment.
After running, expect the grouping columns plus named measures such as order_count or revenue; compare SUM of group counts with a direct COUNT over the same filtered population. COUNT(column) ignores NULL while COUNT(*) counts rows; SUM over no input rows is NULL; order grouped output explicitly. A blank cell, SQL `NULL`, zero,
and an absent row have different meanings; never substitute one for another
without a stated rule.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day02_aggregates_groupby_having.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT c.country, COUNT(*) AS customers
FROM customers c
GROUP BY c.country
ORDER BY customers DESC, c.country;
```

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `country`, and `customers`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `country` with columns `country`, and `customers` from `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT p.category, ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY revenue DESC, p.category;
```

**How to read it:** Example 2: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `category`, and `revenue`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `category` with columns `category`, and `revenue` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Aggregate rows at a declared grain with `GROUP BY`.
- Choose `WHERE` for row filters and `HAVING` for post-aggregation group filters.
- Produce subtotals without confusing subtotal `NULL`s with data `NULL`s.

## Vocabulary and concepts

- **Aggregate:** a function such as `SUM` or `COUNT` that summarizes rows.
- **Group grain:** the real-world meaning of one output row after grouping.
- **Grouping set:** one of several grouping-key combinations evaluated in one
  aggregate query.

## Worked example / walkthrough

In the category-revenue query, first identify one joined row as an order line.
Next group those rows by product category, calculate the revenue aggregate, and
only then apply `HAVING`. Compare that flow with a date predicate in `WHERE`,
which removes rows before the category totals are computed.

## Practice assumptions and review method

- **Focus:** Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
- **Assumptions:** Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
- **Failure to watch for:** Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Count customers by country and order countries by count then country.
   **Progressive hint:** The output grain is one row per country; include a deterministic secondary sort.
   **Inputs/evidence:** For sql-02 Exercise 1, read from `customers`. Build the answer toward `country`, and `customer_count`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 1, expected output: One row per country. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
   **Verify:** For sql-02 Exercise 1, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `country` tuple and verify the new tuple appears exactly once.
2. **Query writing:** Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
   **Progressive hint:** Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
   **Inputs/evidence:** For sql-02 Exercise 2, read from `order_items`, and `products`. Build the answer toward `category`, `net_revenue`, and `average_unit_price`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 2, expected output: One row per qualifying category. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
   **Verify:** For sql-02 Exercise 2, independently aggregate `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `net_revenue`, and `average_unit_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue`, and `average_unit_price` for the existing `category` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Summarize order count and average total by status, retaining statuses with at least 100 orders.
   **Progressive hint:** Filter groups after aggregation with `HAVING COUNT(*)`.
   **Inputs/evidence:** For sql-02 Exercise 3, read from `orders`. Build the answer toward `status`, `order_count`, and `average_order_total`; keep `status` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 3, expected output: One row per qualifying order status. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
   **Verify:** For sql-02 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `average_order_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `average_order_total` for the existing `status` tuple and verify the new tuple appears exactly once.
4. **Prediction:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
   **Progressive hint:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
   **Inputs/evidence:** For sql-02 Exercise 4, read from `customers`. Build the answer toward `all_rows`, `nonnull_email_rows`, and `missing_email_rows`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
   **Verify:** For sql-02 Exercise 4, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `all_rows`, `nonnull_email_rows`, and `missing_email_rows` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
5. **Debugging:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
   **Progressive hint:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
   **Inputs/evidence:** For sql-02 Exercise 5, read from `expenses`. Build the answer toward `category`, and `total_expense`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 5, expected output: One row per expense category over the threshold. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
   **Verify:** For sql-02 Exercise 5, independently aggregate `expenses` by `category`; require one output row for every distinct `category` tuple and compare `total_expense` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `total_expense` for the existing `category` tuple and verify the new tuple appears exactly once.
6. **Extension:** Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
   **Progressive hint:** Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
   **Inputs/evidence:** For sql-02 Exercise 6, read from `orders`. Build the answer toward `order_month`, `order_count`, `order_revenue`, and `returned_orders`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-02 Exercise 6, expected output: Up to 12 month rows in chronological order. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
   **Verify:** For sql-02 Exercise 6, independently aggregate `orders` by `order_id`; require one output row for every distinct `order_id` tuple satisfying `(o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months')` and compare `order_month`, `order_count`, `order_revenue`, and `returned_orders` tuple by tuple. Tie two rows on `order_month` and give them different `order_month` values; verify `order_month` chooses a stable first/last row.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Selecting a non-grouped, non-aggregated column or using WHERE for an aggregate condition changes or invalidates the question.
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

- Can you state the grain of every result and explain why each selected
  non-aggregate belongs in `GROUP BY`?
- Do subtotal rows use `GROUPING(...)` rather than assuming every `NULL` is a
  subtotal marker?

## Next step

Continue to [Day 03 — inner joins](day03_inner_joins.md).

## Deep dive and reference

Learning objectives
- Master aggregate functions: COUNT/COUNT(DISTINCT), SUM, AVG, MIN/MAX, BOOL_AND/BOOL_OR
- Use GROUP BY on columns and expressions; understand functional dependencies
- Filter groups with HAVING; distinguish WHERE vs HAVING
- Apply advanced grouping: GROUPING SETS, ROLLUP, CUBE; handle NULLs in groups

Why this matters
Aggregations turn rows into insights. Correct use of GROUP BY, HAVING, and grouping sets is the backbone of reporting, dashboards, and dimensional analysis.

Core concepts and deep dive
- Aggregate functions
  - COUNT(*) counts rows; COUNT(col) counts non-null col values. COUNT(DISTINCT col) deduplicates within group.
  - AVG(col) = SUM(col)/COUNT(col) over non-null rows; watch type (integer division vs numeric).
  - BOOL_AND/BOOL_OR aggregate booleans; use for rule checks per group.
- Grouping scope
  - GROUP BY partitions the FROM result into groups; aggregates compute per group. SELECT may include only group keys and aggregates.
  - You may group by expressions: GROUP BY date_trunc('month', order_date).
  - Functional dependency (Postgres extension): In some modes, non-key columns can be selected if functionally dependent on the GROUP BY keys (e.g., primary key), but rely on explicit grouping for portability.
- WHERE vs HAVING
  - WHERE filters rows before grouping. HAVING filters groups after aggregation.
  - Example: WHERE order_date >= current_date - interval '90 days'; HAVING SUM(revenue) > 1000.
- NULL handling in groups
  - GROUP BY treats NULLs as equal, forming a single NULL group. Use COALESCE to bucket NULLs into labels.
- Grouping sets
  - GROUPING SETS((a,b), (a), ()) lets you compute multi-level totals in one pass. ROLLUP(a,b) is shorthand for ((a,b), (a), ()). CUBE(a,b) creates all combinations.
  - Use GROUPING(a) to detect subtotal rows (returns 1 when a is aggregated away).

Walkthrough of the day’s script (mapping to your data)
- Customer counts by `customers.country` introduce grouping and count aliases.
- Net line revenue by `products.category` uses `HAVING` to retain categories
  whose undiscounted line value exceeds 10,000.
- Monthly order counts and average `orders.total_amount` demonstrate grouping
  by `date_trunc('month', order_date)`.

Advanced patterns
- Conditional aggregation
  - `SUM(amount) FILTER (WHERE method = 'card') AS card_payments`
  - `COUNT(*) FILTER (WHERE status = 'returned') AS returned_orders`
- Distinct inside aggregates
  - SUM(DISTINCT amount) is allowed but costly. Prefer dedup in a subquery when needed.
- Multi-level totals
  - Use GROUPING SETS/ROLLUP/CUBE with GROUPING() indicator columns to format reports with subtotal rows.

Anti-patterns and pitfalls
- Selecting non-grouped, non-aggregated columns; results are undefined in standard SQL.
- Confusing WHERE and HAVING; using HAVING for row-level filters degrades performance.
- Relying on integer AVG without casting (integer division truncates). Cast to numeric: AVG(col::numeric).

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Check your understanding
- When do you use HAVING instead of WHERE? Give an example that would be wrong with WHERE.
- How does GROUPING SETS differ from running multiple queries with UNION ALL?

Further reading
- Postgres aggregation: https://www.postgresql.org/docs/current/functions-aggregate.html
- GROUPING SETS/ROLLUP/CUBE: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-02 — Aggregates Groupby Having.

I have completed the direct catalog prerequisite: `sql-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day02_aggregates_groupby_having.md
- Answer-free learner SQL: sql/postgres-60day/day02_aggregates_groupby_having.sql

Key terms to teach in context: Aggregate, Group grain, Grouping set. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: In the category-revenue query, first identify one joined row as an order line. Next group those rows by product category, calculate the revenue aggregate, and only then apply HAVING. Compare that flow with a date predicate in WHERE, which removes rows before the category totals are computed.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-02/ working copy. Never point setup, reset, DDL, or DML
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
