# Day 21: Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST (Companion Guide)

## How to run this lesson

Open **sql-21** from the PostgreSQL side of `./classroom` and choose **Whole SQL
lesson (psql)** so the distribution queries run in file order against the local
`advanced_sql_training` database. Your editable copy is
`.learning/sql/sql-21/lesson/workspace/sql/postgres-60day/day21_distribution_functions.sql`.
The script only reads `customers`, `orders`, `order_items`, `employees` and
`products` from the standard course fixture inside one `BEGIN`/`ROLLBACK`
block, so a clean `psql` transcript is a series of result tables whose bucket
and rank columns you can check by hand. Launcher, saving and troubleshooting
steps are in [Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

To step through the distribution queries in JupyterLab, generate this notebook
([setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-21
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 20; first, last, and Nth values](day20_first_last_value.md)
- **Artifacts:** [learner SQL](../day21_distribution_functions.sql) ·
  [solution reasoning](../solutions/day21_solutions.md) ·
  [executable solution](../solutions/day21_solutions.sql)

## A beginner's mental model for this lesson

All three functions in this lesson answer "where does this row sit in an
ordered list?" without collapsing rows, so the row count after the window step
equals the row count before it. They differ in what they count:

- `NTILE(n)` deals rows into n buckets by position, like dealing cards. With
  438 ordering customers and `NTILE(4)`, the first two quartiles get 110
  customers and the last two get 109, because 438 = 4 x 109 + 2 and the two
  leftover rows go to the earliest buckets. Tied values can land in different
  buckets, so the ordering needs a tie-breaker such as `customer_id`.
- `PERCENT_RANK()` is `(rank - 1) / (rows in partition - 1)`. The lowest value
  always gets 0, the highest distinct value gets 1, and tied rows share a value
  because they share a rank.
- `CUME_DIST()` is `(rows with a value at or below this one) / (rows in
  partition)`. It never reaches 0, since every row counts itself, and the last
  peer group always gets 1.

For the values 10, 10 and 20 (Exercise 4), both 10s have rank 1, so
`PERCENT_RANK` gives 0, 0 and 1. Two of the three rows are at or below 10, so
`CUME_DIST` gives 0.667, 0.667 and 1. Before running any query here, write
down how many rows the partition has, because every denominator above comes
from that count.

## Two worked SQL examples

### Example 1

```sql
WITH cust_rev AS (
  SELECT
    c.customer_id,
    COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0) AS revenue
  FROM
    customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    c.customer_id
)
SELECT
  customer_id,
  revenue,
  -- NTILE must assign tied rows to physical buckets; customer_id makes
  -- that assignment reproducible without changing PERCENT_RANK tie rules.
  NTILE(4) OVER (ORDER BY revenue DESC, customer_id) AS revenue_quartile,
  ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM
  cust_rev
ORDER BY
  revenue DESC,
  customer_id
LIMIT 50;
```

**How to read it:** The `cust_rev` CTE starts from all 500 `customers` and
left-joins `orders` and `order_items`, so customers who never ordered survive
with `revenue` of 0 after `COALESCE`. Revenue is recomputed from line items
(`unit_price * quantity * (1 - discount)`) rather than read from
`orders.total_amount`. The two windows then read the same 500 rows in opposite
directions: `NTILE(4)` sorts revenue descending, so quartile 1 holds the
biggest spenders, while `PERCENT_RANK` sorts ascending, so a big spender gets a
value near 1.

**Expected result/shape:** 50 rows because of the `LIMIT`, all from
quartile 1 and highest revenue first. Across the full 500 rows each quartile
holds exactly 125 customers, and the 62 customers with zero revenue all sit in
quartile 4 with a `pct_rank` of 0. Remove the `LIMIT` and count by
`revenue_quartile` to see those numbers.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH cust_rev AS (
  SELECT
    c.customer_id,
    COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0) AS revenue
  FROM
    customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  c.customer_id
)
SELECT
  customer_id,
  revenue,
  -- NTILE must assign tied rows to physical buckets; customer_id makes
  -- that assignment reproducible without changing PERCENT_RANK tie rules.
  NTILE(4) OVER (ORDER BY revenue DESC, customer_id) AS revenue_quartile,
    ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM
  cust_rev
ORDER BY
  revenue DESC,
  customer_id
LIMIT 50;
```

**How to read it:** `EXPLAIN (COSTS OFF)` prints the plan for Example 1
without running it. Read the tree from the bottom: sequential scans of the
three tables feed two hash right joins and a `HashAggregate` grouped on
`c.customer_id`. Above that sit two `Sort` and `WindowAgg` pairs, one per
distinct window ordering (revenue descending with `customer_id` for `NTILE`,
revenue ascending for `PERCENT_RANK`), then a final `Sort` and `Limit` for the
presentation order.

**Expected result/shape:** About 20 plan lines and no business rows.
Count the `WindowAgg` nodes: two windows with different `ORDER BY` lists need
two sorts. Give both windows the same ordering and PostgreSQL can compute them
in one `WindowAgg` over a single sort.

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
- **Review loop:** for each result, count rows per bucket or partition, then
  compare the first and last value in one partition with the formulas in the
  mental model above.

## Exercises

Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.

Every exercise below windows either a 438-row customer-spend relation or a
base table directly. Before running, write the partition size you expect (438
ordering customers, 16 or 17 employees per department, 50 products per
category), since each distribution value is a fraction of that count.

1. **Query writing:** Assign customers to four stored-spend buckets.
   **Progressive hint:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.
   **Inputs/evidence:** For sql-21 Exercise 1, read `orders`, total `total_amount` per `customer_id` in the `customer_spend` CTE, then apply `NTILE(4)` over that customer-grain relation ordered by spend descending with `customer_id` as the tie-breaker; `order_id` does not survive the aggregation.
   **Expected result/shape:** For sql-21 Exercise 1, expected output: 438 rows, one per customer who has at least one order (the other 62 of the 500 customers have none), with quartiles of 110, 110, 109, and 109 customers. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
   **Verify:** For sql-21 Exercise 1, confirm the row count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that grouping the result by `spend_quartile` returns counts 110, 110, 109, 109 with quartile 1 running from 9502.21 down to 7133.41 and quartile 4 from 3522.32 down to 962.26; the seed has 18 pairs of customers with identical spend (for example 51 and 428 at 8970.66), and each pair lands in the same quartile with the lower `customer_id` first.
2. **Query writing:** Calculate salary percent rank within each department.
   **Progressive hint:** Partition by department and rank on salary alone so tied salaries share rank.
   **Inputs/evidence:** For sql-21 Exercise 2, read the 100 rows of `employees`, partition by `department_id`, and order each partition by `salary` alone so that equal salaries would share a rank; keep `employee_id` because the result stays at employee grain.
   **Expected result/shape:** For sql-21 Exercise 2, expected output: 100 rows, one per employee, with `salary_percent_rank` from 0 to 1 inside each of the six departments (four of 17 employees and two of 16). The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
   **Verify:** For sql-21 Exercise 2, in department 1 (17 employees, no tied salaries) check the formula (rank - 1) / (rows - 1): employee 1 at 40079.19 returns 0, employee 7 at 40554.33 returns 0.0625 (1/16), employee 49 returns 0.5, and employee 97 at 47681.43 returns 1; in 16-employee department 5 the second row returns 1/15 (0.0667). Then run the window on `VALUES (9, 50000), (8, 100), (8, 100), (8, 200)` and expect 0 for the one-row department and 0, 0, 1 for the tied salaries.
3. **Query writing:** Calculate cumulative distribution of product price within category.
   **Progressive hint:** Partition by category and order on price.
   **Inputs/evidence:** For sql-21 Exercise 3, read the 300 rows of `products`, partition by `category`, and order by `price`; keep `product_id` because each product stays one row.
   **Expected result/shape:** For sql-21 Exercise 3, expected output: 300 rows, one per product, 50 per category, with `price_cume_dist` in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-21 Exercise 3, in `Apparel` (50 products, no repeated prices) check rows at or below / partition rows: product 1 at 10.37 returns 0.02, product 7 at 12.59 returns 0.04, product 145 at 63.65 returns 0.5, and product 295 at 119.15 returns 1; confirm `MAX(price_cume_dist)` is exactly 1 in each of the six categories, and that a one-row partition such as `VALUES (9, 50000)` returns 1, not 0.
4. **Prediction:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
   **Progressive hint:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.
   **Inputs/evidence:** For sql-21 Exercise 4, read only the three-row inline `VALUES` fixture `(1, 10), (2, 10), (3, 20)` with columns `row_id` and `value`; compute both functions over the whole fixture ordered by `value`.
   **Expected result/shape:** For sql-21 Exercise 4, expected output: three rows, one per `row_id`, where the two rows tied at 10 share both results. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
   **Verify:** For sql-21 Exercise 4, expect rows 1 and 2 to return `percent_rank_value` 0 and `cume_dist_value` 0.6667 (two of three rows are at or below 10), and row 3 to return 1 and 1; then change row 2 to 15 and confirm the results become 0, 0.5, 1 for percent rank and 0.3333, 0.6667, 1 for cumulative distribution, because the tie is gone.
5. **Debugging:** Audit the row count in each customer spend decile rather than assuming exact equality.
   **Progressive hint:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.
   **Inputs/evidence:** For sql-21 Exercise 5, read `orders`, total spend per `customer_id`, assign `NTILE(10)` over the 438 customer totals ordered by spend descending and `customer_id`, then count customers per decile.
   **Expected result/shape:** For sql-21 Exercise 5, expected output: 10 rows, deciles 1 to 8 holding 44 customers and deciles 9 and 10 holding 43, because 438 = 10 x 43 + 8 and `NTILE` gives the remainder to the first buckets. The final columns are `decile`, and `customers`. The final order is `decile`.
   **Verify:** For sql-21 Exercise 5, confirm `SUM(customers)` equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that the counts differ by at most one; then run `NTILE(4)` over `generate_series(1, 3)` and confirm it returns only buckets 1, 2, and 3, showing that a bucket can be empty when there are fewer rows than buckets.
6. **Extension:** Return customers in the top stored-spend decile with their spend and population share.
   **Progressive hint:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
   **Inputs/evidence:** For sql-21 Exercise 6, read `orders`, total spend per `customer_id`, assign `NTILE(10)` and `COUNT(*) OVER ()` in the `bucketed` CTE, and only then filter to `decile = 1`, so the population is counted before the filter.
   **Expected result/shape:** For sql-21 Exercise 6, expected output: the 44 customers of decile 1, from customer 181 at 9502.21 down to 8190.44, each carrying `population` 438. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
   **Verify:** For sql-21 Exercise 6, confirm 44 rows, every `decile` equals 1, every `population` equals 438, and no customer appears twice; the first three rows are customers 181 (9502.21), 12 (9244.27), and 25 (9196.96). Customers 51 and 428 tie at 8970.66 and both appear, 51 first; the next spend below the cut, 8168.74, belongs to decile 2. Computing `COUNT(*) OVER ()` in the outer query after the filter instead returns 44, which is why `population` is taken inside `bucketed`.

## Common mistakes and how to recover

- **Reading `PERCENT_RANK` as a probability.** A value of 0.75 means 75% of
  the other rows in the partition rank below this one. It says nothing about
  likelihood or cause, and a single-row partition always returns 0.
- **Expecting equal value ranges from `NTILE`.** In Exercise 5 every decile
  holds 43 or 44 customers, but decile 1 spans spend from 8,190.44 to 9,502.21
  while decile 10 spans 962.26 to 2,521.63. Buckets are equal in row count,
  not in spend width.
- **Leaving ties to chance in `NTILE`.** Two customers both have stored spend
  of 5,303.39. Ordering only by spend lets PostgreSQL put either one first,
  which changes buckets when they sit on a boundary; adding `customer_id` makes
  the assignment repeatable.
- **Ranking before aggregating.** `NTILE(4)` applied directly to `orders`
  buckets 4,362 orders, not 438 customers. Sum to one row per customer in a CTE
  first, then window over that.
- **Filtering on a window alias in the same `SELECT`.** `WHERE decile = 1`
  cannot see `decile` at the level where it is computed, because `WHERE` runs
  before windows. Exercise 6 assigns the decile in a CTE and filters outside.
- General recovery steps (row counts, `NULL`s, `psql` stopping at the first
  error) are in [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Are the outputs described as row-position summaries rather than guaranteed
  business segments?
- Can you explain how ties affect each function?

## Next step

Continue to [Day 22; advanced windows](day22_advanced_windows.md).

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

Further reading
- Distribution: https://www.postgresql.org/docs/17/functions-window.html#FUNCTIONS-WINDOW

## Ask an AI tutor about this lesson

A tutor is most useful here for checking your hand-calculated `PERCENT_RANK`
and `CUME_DIST` fractions; the prompt below keeps it away from the solutions
([why it is optional](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-21: Distribution Functions: NTILE, PERCENT_RANK, and CUME_DIST.

I have completed the direct catalog prerequisite: `sql-20`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day21_distribution_functions.md
- Answer-free learner SQL: sql/postgres-60day/day21_distribution_functions.sql

Key terms to teach in context: Quantile bucket, Percent rank, Cumulative distribution. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Apply `NTILE(4)`, `PERCENT_RANK`, and `CUME_DIST` to a five-row `VALUES` set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
