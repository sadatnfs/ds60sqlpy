# Day 21 solutions: Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Compare these answers with your own transcript after an attempt. The
executable companion sets `search_path` to `training` and wraps the answers in
`BEGIN`/`ROLLBACK`, so it leaves `advanced_sql_training` unchanged;
[Read a solution](../../STUDY-GUIDE.md#read-a-solution) explains the general
method.

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day21_solutions.sql
```

## How these answers fit together

Exercises 1, 5 and 6 share one shape: a CTE sums `orders.total_amount` per
customer (438 rows), and a window ranks that CTE. Exercises 2 and 3 window a
base table directly with `PARTITION BY`. Exercise 4 uses a three-row `VALUES`
list so you can check both formulas by hand. When your query differs, compare
partition sizes and the first and last value in each partition before
comparing syntax. The learner file is
[day21_distribution_functions.sql](../day21_distribution_functions.sql).

## Reading contract

- **Focus:** Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
- **Assumptions:** `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
- **Primary pitfall:** A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Assign customers to four stored-spend buckets.

**Reasoning:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.

```sql
WITH customer_spend AS (
  SELECT
    o.customer_id,
    SUM(o.total_amount) AS stored_spend
  FROM
    orders AS o
  GROUP BY
    o.customer_id
)
SELECT
  customer_id,
  ROUND(stored_spend, 2) AS stored_spend,
  NTILE(4) OVER (ORDER BY stored_spend DESC, customer_id) AS spend_quartile
FROM
  customer_spend
ORDER BY
  spend_quartile,
  stored_spend DESC,
  customer_id;
```

**Expected shape:** One row per ordering customer with bucket 1-4.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 1, read `orders`, total `total_amount` per `customer_id` in the `customer_spend` CTE, then apply `NTILE(4)` over that customer-grain relation ordered by spend descending with `customer_id` as the tie-breaker; `order_id` does not survive the aggregation.
- **Expected result/shape:** For sql-21 Exercise 1, expected output: 438 rows, one per customer who has at least one order (the other 62 of the 500 customers have none), with quartiles of 110, 110, 109, and 109 customers. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
- **Independent verification:** For sql-21 Exercise 1, confirm the row count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that grouping the result by `spend_quartile` returns counts 110, 110, 109, 109 with quartile 1 running from 9502.21 down to 7133.41 and quartile 4 from 3522.32 down to 962.26; the seed has 18 pairs of customers with identical spend (for example 51 and 428 at 8970.66), and each pair lands in the same quartile with the lower `customer_id` first.
- **Intermediate relation check:** Run the `customer_spend` CTE alone: 438 rows, one per customer with at least one order, and no `NULL` spend because no `total_amount` is `NULL`. Customers without orders are absent, which is why the prompt says "ordering customer".
- **Clause check:** `GROUP BY o.customer_id` collapses 4,362 orders to 438 customer rows. `NTILE(4) OVER (ORDER BY stored_spend DESC, customer_id)` then deals those rows into buckets of 110, 110, 109 and 109. The outer `ORDER BY` repeats bucket and spend so the printed order matches the assignment.
- **Alternative/trade-off:** A subquery in `FROM` behaves exactly like the CTE. Writing `NTILE(4) OVER (ORDER BY SUM(o.total_amount) DESC, o.customer_id)` in the grouped query is also valid, because windows run after grouping, but the CTE lets you inspect the 438-row input first.
- **Edge case:** Two customers both total 5,303.39. Without `customer_id` in the window ordering, a rerun could swap them, which would move a customer between buckets if the pair ever straddled a boundary.

## Exercise 2: Query writing

**Prompt:** Calculate salary percent rank within each department.

**Reasoning:** Partition by department and rank on salary alone so tied salaries share rank.

```sql
SELECT
  e.employee_id,
  e.department_id,
  e.salary,
  PERCENT_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary) AS salary_percent_rank
FROM
  employees AS e
ORDER BY
  e.department_id,
  e.salary,
  e.employee_id;
```

**Expected shape:** One row per employee with values from 0 to 1.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 2, read the 100 rows of `employees`, partition by `department_id`, and order each partition by `salary` alone so that equal salaries would share a rank; keep `employee_id` because the result stays at employee grain.
- **Expected result/shape:** For sql-21 Exercise 2, expected output: 100 rows, one per employee, with `salary_percent_rank` from 0 to 1 inside each of the six departments (four of 17 employees and two of 16). The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
- **Independent verification:** For sql-21 Exercise 2, in department 1 (17 employees, no tied salaries) check the formula (rank - 1) / (rows - 1): employee 1 at 40079.19 returns 0, employee 7 at 40554.33 returns 0.0625 (1/16), employee 49 returns 0.5, and employee 97 at 47681.43 returns 1; in 16-employee department 5 the second row returns 1/15 (0.0667). Then run the window on `VALUES (9, 50000), (8, 100), (8, 100), (8, 200)` and expect 0 for the one-row department and 0, 0, 1 for the tied salaries.
- **Intermediate relation check:** Count employees per department first: departments 1 to 4 have 17 rows and departments 5 and 6 have 16. Those counts set the denominators, so values step by 1/16 = 0.0625 in the larger departments and by 1/15 (about 0.0667) in the smaller ones.
- **Clause check:** `PARTITION BY e.department_id` restarts the calculation for each department, and `ORDER BY e.salary` ranks within it, so each department's lowest salary prints 0 and its highest prints 1. `e.employee_id` appears only in the outer `ORDER BY`; it is kept out of the window so equal salaries would share a rank.
- **Alternative/trade-off:** `(RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary) - 1)::numeric / NULLIF(COUNT(*) OVER (PARTITION BY e.department_id) - 1, 0)` reproduces every value and makes a good hand check, but it returns `NULL` for a one-person department where `PERCENT_RANK` returns 0.
- **Edge case:** The fixture has no tied salaries inside a department. Insert a test employee with a colleague's salary inside `BEGIN`/`ROLLBACK` and confirm both rows get the same value.

## Exercise 3: Query writing

**Prompt:** Calculate cumulative distribution of product price within category.

**Reasoning:** Partition by category and order on price.

```sql
SELECT
  p.product_id,
  p.category,
  p.price,
  CUME_DIST() OVER (PARTITION BY p.category ORDER BY p.price) AS price_cume_dist
FROM
  products AS p
ORDER BY
  p.category,
  p.price,
  p.product_id;
```

**Expected shape:** One row per product with cume_dist in (0, 1].

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 3, read the 300 rows of `products`, partition by `category`, and order by `price`; keep `product_id` because each product stays one row.
- **Expected result/shape:** For sql-21 Exercise 3, expected output: 300 rows, one per product, 50 per category, with `price_cume_dist` in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-21 Exercise 3, in `Apparel` (50 products, no repeated prices) check rows at or below / partition rows: product 1 at 10.37 returns 0.02, product 7 at 12.59 returns 0.04, product 145 at 63.65 returns 0.5, and product 295 at 119.15 returns 1; confirm `MAX(price_cume_dist)` is exactly 1 in each of the six categories, and that a one-row partition such as `VALUES (9, 50000)` returns 1, not 0.
- **Intermediate relation check:** Each of the six categories holds 50 products with 50 distinct prices, so every value is a multiple of 1/50 = 0.02. The cheapest Apparel product (10.37) prints 0.02 and the most expensive prints 1. Confirm the 50 and 50 with `SELECT category, COUNT(*), COUNT(DISTINCT price) FROM products GROUP BY category` before trusting any fraction.
- **Clause check:** `PARTITION BY p.category` creates six independent windows, and `ORDER BY p.price` defines the "at or below" comparison. Because `CUME_DIST` counts the current row, the minimum here is 0.02 and never 0, which is why the contract writes the range as (0, 1].
- **Alternative/trade-off:** A correlated subquery that counts products in the same category with `q.price <= p.price`, divided by a second subquery that counts the category, gives the same numbers. It rescans the category for every row, so it is a verification tool rather than the answer.
- **Edge case:** If two Books products shared a price, both would get the higher cumulative fraction, because peers are counted together. A product with a `NULL` price would sort last under the default ascending order and get 1.

## Exercise 4: Prediction

**Prompt:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.

**Reasoning:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.

```sql
SELECT
  row_id,
  value,
  PERCENT_RANK() OVER (ORDER BY value) AS percent_rank_value,
  CUME_DIST() OVER (ORDER BY value) AS cume_dist_value
FROM (
  VALUES (1, 10),
    (2, 10),
    (3, 20)) AS sample (row_id, value)
ORDER BY
  row_id;
```

**Expected shape:** Three rows making tie behavior visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 4, read only the three-row inline `VALUES` fixture `(1, 10), (2, 10), (3, 20)` with columns `row_id` and `value`; compute both functions over the whole fixture ordered by `value`.
- **Expected result/shape:** For sql-21 Exercise 4, expected output: three rows, one per `row_id`, where the two rows tied at 10 share both results. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
- **Independent verification:** For sql-21 Exercise 4, expect rows 1 and 2 to return `percent_rank_value` 0 and `cume_dist_value` 0.6667 (two of three rows are at or below 10), and row 3 to return 1 and 1; then change row 2 to 15 and confirm the results become 0, 0.5, 1 for percent rank and 0.3333, 0.6667, 1 for cumulative distribution, because the tie is gone.
- **Intermediate relation check:** The `VALUES` list is the whole input: three rows, one partition, two distinct values. Write each row's rank before running: 1, 1 and 3.
- **Clause check:** Both windows use `ORDER BY value` with no partition. `PERCENT_RANK` = (rank - 1) / (3 - 1) gives 0, 0 and 1. `CUME_DIST` = (rows at or below the value) / 3 gives 2/3, 2/3 and 1, printed as 0.6666666666666666. The final `ORDER BY row_id` fixes display order only; it changes neither calculation.
- **Alternative/trade-off:** Adding `row_id` to the window ordering (`ORDER BY value, row_id`) breaks the tie and produces 0, 0.5 and 1 for `PERCENT_RANK` and 1/3, 2/3 and 1 for `CUME_DIST`. That answers a different question, so the tie has to stay.
- **Edge case:** Delete row 3 and both tied rows remain: `PERCENT_RANK` returns 0 for each and `CUME_DIST` returns 1 for each, because the whole partition is one peer group.

## Exercise 5: Debugging

**Prompt:** Audit the row count in each customer spend decile rather than assuming exact equality.

**Reasoning:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.

```sql
WITH spend AS (
  SELECT
    o.customer_id,
    SUM(o.total_amount) AS total_spend
  FROM
    orders AS o
  GROUP BY
    o.customer_id
),
bucketed AS (
  SELECT
    customer_id,
    NTILE(10) OVER (ORDER BY total_spend DESC,
      customer_id) AS decile
  FROM
    spend
)
SELECT
  decile,
  COUNT(*) AS customers
FROM
  bucketed
GROUP BY
  decile
ORDER BY
  decile;
```

**Expected shape:** Up to 10 bucket rows with counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 5, read `orders`, total spend per `customer_id`, assign `NTILE(10)` over the 438 customer totals ordered by spend descending and `customer_id`, then count customers per decile.
- **Expected result/shape:** For sql-21 Exercise 5, expected output: 10 rows, deciles 1 to 8 holding 44 customers and deciles 9 and 10 holding 43, because 438 = 10 x 43 + 8 and `NTILE` gives the remainder to the first buckets. The final columns are `decile`, and `customers`. The final order is `decile`.
- **Independent verification:** For sql-21 Exercise 5, confirm `SUM(customers)` equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that the counts differ by at most one; then run `NTILE(4)` over `generate_series(1, 3)` and confirm it returns only buckets 1, 2, and 3, showing that a bucket can be empty when there are fewer rows than buckets.
- **Intermediate relation check:** Run `spend` (438 rows) and then `bucketed` (still 438 rows, now with a `decile` column). The window adds a column; only the final `GROUP BY decile` changes the row count, down to 10.
- **Clause check:** 438 = 10 x 43 + 8, so `NTILE(10)` gives the first eight deciles 44 customers and the last two 43. `COUNT(*)` per decile shows exactly that, which is the point of the audit: buckets are equal only when the row count divides evenly.
- **Alternative/trade-off:** Deciles from `CEIL(10 * CUME_DIST() OVER (ORDER BY total_spend DESC))` keep tied customers together; on this data they produce buckets of 43 to 45 customers. Choose `NTILE` when equal counts matter and a `CUME_DIST` cutoff when ties must never be split.
- **Edge case:** With fewer customers than buckets, for example 7 rows and `NTILE(10)`, deciles 8 to 10 do not appear at all, which is why the contract promises "up to 10" rows.

## Exercise 6: Extension

**Prompt:** Return customers in the top stored-spend decile with their spend and population share.

**Reasoning:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.

```sql
WITH spend AS (
  SELECT
    o.customer_id,
    SUM(o.total_amount) AS total_spend
  FROM
    orders AS o
  GROUP BY
    o.customer_id
),
bucketed AS (
  SELECT
    customer_id,
    total_spend,
    NTILE(10) OVER (ORDER BY total_spend DESC,
      customer_id) AS decile,
    COUNT(*) OVER () AS population
  FROM
    spend
)
SELECT
  customer_id,
  ROUND(total_spend, 2) AS total_spend,
  decile,
  population
FROM
  bucketed
WHERE
  decile = 1
ORDER BY
  total_spend DESC,
  customer_id;
```

**Expected shape:** Customers in decile 1.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 6, read `orders`, total spend per `customer_id`, assign `NTILE(10)` and `COUNT(*) OVER ()` in the `bucketed` CTE, and only then filter to `decile = 1`, so the population is counted before the filter.
- **Expected result/shape:** For sql-21 Exercise 6, expected output: the 44 customers of decile 1, from customer 181 at 9502.21 down to 8190.44, each carrying `population` 438. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
- **Independent verification:** For sql-21 Exercise 6, confirm 44 rows, every `decile` equals 1, every `population` equals 438, and no customer appears twice; the first three rows are customers 181 (9502.21), 12 (9244.27), and 25 (9196.96). Customers 51 and 428 tie at 8970.66 and both appear, 51 first; the next spend below the cut, 8168.74, belongs to decile 2. Computing `COUNT(*) OVER ()` in the outer query after the filter instead returns 44, which is why `population` is taken inside `bucketed`.
- **Intermediate relation check:** In `bucketed`, every row carries `population` = 438 from `COUNT(*) OVER ()`, a window with no partition and no ordering that covers all rows. Check that value once before filtering.
- **Clause check:** The window step assigns deciles to all 438 customers; only then does the outer `WHERE decile = 1` keep the 44 customers with spend from 8,190.44 to 9,502.21. Descending order inside `NTILE` is what makes decile 1 the top spenders.
- **Alternative/trade-off:** Moving `COUNT(*) OVER ()` into the outer query, after the filter, would report 44 instead of 438, because that window would see only the surviving rows. Computing it in `bucketed` captures the population before filtering, which is what a population share (44 / 438, about 10%) needs.
- **Edge case:** If the `NTILE` ordering were ascending, decile 1 would hold the lowest spenders and the same `WHERE decile = 1` would silently return the wrong 44 customers.

## Final self-check

- Can you predict the bucket sizes `NTILE(n)` produces for any row count, such
  as 438 rows into 4 or 10 buckets?
- Can you compute `PERCENT_RANK` and `CUME_DIST` for a three-row partition by
  hand, including a tie?
- Which of your windows needed a tie-breaker, and which had to keep ties as
  peers?
- Did you compute population counts before the filter and apply the filter
  after the window step?
