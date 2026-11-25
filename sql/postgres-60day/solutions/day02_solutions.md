# Day 02 solutions: Aggregations, GROUP BY, HAVING, Grouping Sets

<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers group rows and then report one row per group. Exercises 1 and 3 count rows per country or status, Exercises 2 and 5 add money per category and filter the totals with `HAVING`, Exercise 4 compares three kinds of count over the whole table, and Exercise 6 groups orders by calendar month. Write your own versions first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day02_solutions.sql
```

Row counts to expect: 8, 6, 5, 1, 5, and 12 in our check (Exercise 6 depends on today's date). Nothing is written; the file ends with `ROLLBACK`, and the excerpts below leave out its `SET search_path` line. The exercises follow [the learner file](../day02_aggregates_groupby_having.sql), and the study guide gives [suggestions for checking your answer against this one](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
- **Assumptions:** Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
- **Primary pitfall:** Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
- **Safety:** read-only; the six statements are plain `SELECT`s, wrapped in a transaction that ends in `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Count customers by country and order countries by count then country.

**Reasoning:** The output grain is one row per country; include a deterministic secondary sort.

**Clause-by-clause reading:**

- `FROM customers AS c`: all 500 customers, one row each.
- `GROUP BY c.country`: one bucket per country; `c.country` may appear in the `SELECT` list because it is the grouping key.
- `COUNT(*) AS customer_count`: the number of rows in each bucket.
- `ORDER BY customer_count DESC, c.country`: largest count first, alphabetical within a tie. `ORDER BY` may use the alias because it runs after the `SELECT` list.

```sql
SELECT
  c.country,
  COUNT(*) AS customer_count
FROM
  customers AS c
GROUP BY
  c.country
ORDER BY
  customer_count DESC,
  c.country;
```

**Expected shape:** One row per country.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 1, read all 500 `customers` rows; `country` is `NOT NULL` and takes 8 values. Return `country` and `customer_count`.
- **Expected result/shape:** For sql-02 Exercise 1, return 8 rows, one per country: `CA`, `DE`, `GB`, and `US` with 63 customers each, then `AU`, `BR`, `FR`, and `IN` with 62 each. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
- **Independent verification:** For sql-02 Exercise 1, confirm the 8 counts sum to 500, matching `SELECT COUNT(*) FROM customers`, and that the four-way tie at 63 is listed alphabetically. Inside a rolled-back transaction, move customer 1 from `US` to `NZ`; the result must grow to 9 rows, with `US` falling to 62 and `NZ` appearing last with 1.
- **What prints:** eight rows. CA, DE, GB and US each have 63 customers; AU, BR, FR and IN each have 62.
- **Ties decide the layout:** every row ties with three others, so without `c.country` the order within each count would be arbitrary.
- **Checking the total:** the eight counts add to 500, which equals `SELECT COUNT(*) FROM customers`. A country with no customers cannot appear, because groups come only from existing rows.
- **Customers, not buyers:** BR's 62 customers count here even though none of them has an order. Counting buyers per country would mean joining to `orders` and using `COUNT(DISTINCT o.customer_id)`.

## Exercise 2: Query writing

**Prompt:** Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.

**Reasoning:** Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.

**Clause-by-clause reading:**

- `JOIN products AS p ON p.product_id = oi.product_id`: attaches a category to each of the 13,085 order lines without changing the row count, since every line has exactly one product.
- `ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue`: line value after discount, added up per category and rounded once.
- `ROUND(AVG(oi.unit_price), 2) AS average_unit_price`: the mean list price over the category's lines.
- `HAVING SUM(...) > 100000`: the same net expression, unrounded, tested after grouping.
- `ORDER BY net_revenue DESC, p.category`: highest revenue first.

```sql
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
  ROUND(AVG(oi.unit_price), 2) AS average_unit_price
FROM
  order_items AS oi
  JOIN products AS p ON p.product_id = oi.product_id
GROUP BY
  p.category
HAVING
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) > 100000
ORDER BY
  net_revenue DESC,
  p.category;
```

**Expected shape:** One row per qualifying category.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; every item finds its product, and the 6 categories hold between 2,145 and 2,192 items each. Return `category`, `net_revenue`, and `average_unit_price`.
- **Expected result/shape:** For sql-02 Exercise 2, return 6 rows, because every category clears the 100,000 `HAVING` threshold; `Sports` leads at 397427.70 and `Books` is last at 386192.77. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
- **Independent verification:** For sql-02 Exercise 2, confirm the 6 `net_revenue` values sum to 2355647.12, the same total that `SUM(unit_price * quantity * (1 - discount))` gives over all of `order_items`. Raise the threshold to 395000 and only `Sports` must remain, which proves `HAVING` filters groups after they are summed.
- **What prints:** six rows, from Sports at 397,427.70 down to Books at 386,192.77. Average unit prices sit between 60.40 (Apparel) and 61.78 (Sports).
- **The threshold keeps everything:** the smallest category still clears 100,000 almost four times over. Raise it to 390,000 and Books disappears; raise it to 395,000 and only Sports is left.
- **Average per line, not per unit:** `AVG(oi.unit_price)` counts a line of one unit and a line of five units equally and ignores discounts. Net revenue divided by `SUM(oi.quantity)` would give the price actually paid per unit, 60.66 for Sports.
- **`HAVING` before rounding:** the filter compares the exact sum, so a category at 100,000.004 would pass even though its displayed value rounds to 100,000.00.
- **Line counts behind each total:** Books has the fewest lines, 2,145, against 2,186 to 2,192 elsewhere, which explains most of its gap to Sports. `COUNT(*)` beside the revenue makes that visible.

## Exercise 3: Query writing

**Prompt:** Summarize order count and average total by status, retaining statuses with at least 100 orders.

**Reasoning:** Filter groups after aggregation with `HAVING COUNT(*)`.

**Clause-by-clause reading:**

- `GROUP BY o.status`: one bucket for each of the five statuses.
- `COUNT(*) AS order_count` and `ROUND(AVG(o.total_amount), 2) AS average_order_total`: the size and mean order value of each bucket.
- `HAVING COUNT(*) >= 100`: drops any status with fewer than 100 orders, after counting.
- `ORDER BY order_count DESC, o.status`: busiest status first, alphabetical within a tie.

```sql
SELECT
  o.status,
  COUNT(*) AS order_count,
  ROUND(AVG(o.total_amount), 2) AS average_order_total
FROM
  orders AS o
GROUP BY
  o.status
HAVING
  COUNT(*) >= 100
ORDER BY
  order_count DESC,
  o.status;
```

**Expected shape:** One row per qualifying order status.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 3, read all 4,362 `orders` rows across 5 `status` values. Return `status`, `order_count`, and `average_order_total`.
- **Expected result/shape:** For sql-02 Exercise 3, return 5 rows, since every status has far more than 100 orders: `placed` and `shipped` with 873 each, then `delivered`, `paid`, and `returned` with 872 each. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
- **Independent verification:** For sql-02 Exercise 3, confirm the 5 counts sum to 4,362 and that `paid` has the highest average at 548.24. Change the filter to `HAVING COUNT(*) >= 873`; only `placed` and `shipped` must remain, so the tie at 873 is broken by `status` name.
- **What prints:** five rows: placed and shipped with 873 orders, then delivered, paid and returned with 872. The average order total ranges from 536.79 (returned) to 548.24 (paid).
- **No status is dropped:** each status holds about a fifth of the 4,362 orders, so the `HAVING` bar of 100 is far below every group.
- **Total check:** 873 + 873 + 872 + 872 + 872 = 4,362, every order exactly once.
- **Reading the averages:** paid orders average 548.24, about eight above the overall 540.04, while returned orders sit lowest at 536.79. With roughly 870 orders per status, gaps this small are not worth a business conclusion.
- **Why not `WHERE`:** `WHERE COUNT(*) >= 100` is rejected, and `WHERE status <> 'returned'` would answer a different question by removing orders before they are counted.

## Exercise 4: Prediction

**Prompt:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.

**Reasoning:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.

**Clause-by-clause reading:**

- `COUNT(*) AS all_rows`: every customer row, whatever its columns contain.
- `COUNT(c.email) AS nonnull_email_rows`: only rows whose `email` is not `NULL`.
- `COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_rows`: counts only the rows that pass the `FILTER` condition.
- No `GROUP BY`: the whole table is one group, so exactly one row comes back.

```sql
SELECT
  COUNT(*) AS all_rows,
  COUNT(c.email) AS nonnull_email_rows,
  COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_rows
FROM
  customers AS c;
```

**Expected shape:** One row; present plus missing equals total.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 4, read from `customers` and count, in one aggregate query, all rows as `all_rows`, rows with a non-null `email` as `nonnull_email_rows`, and rows whose `email` is NULL as `missing_email_rows`.
- **Expected result/shape:** For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
- **Independent verification:** For sql-02 Exercise 4, confirm `nonnull_email_rows + missing_email_rows = all_rows`; the seed returns 500, 500, and 0 because every seeded customer has an email. In a transaction you roll back, set one customer's `email` to NULL and rerun: expect 500, 499, and 1.
- **What prints:** one row: 500, 500 and 0. Every seeded customer has an email, and all 500 addresses are distinct.
- **The relationship:** `nonnull_email_rows + missing_email_rows = all_rows` holds for any data, because each row is counted in exactly one of the last two columns.
- **Empty string versus `NULL`:** an email of `''` is not `NULL`, so `COUNT(c.email)` counts it. To treat blanks as missing, test `NULLIF(btrim(c.email), '') IS NULL`.
- **`FILTER` versus `CASE`:** `SUM(CASE WHEN c.email IS NULL THEN 1 ELSE 0 END)` gives the same number; `FILTER` states the intent more directly.

## Exercise 5: Debugging

**Prompt:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.

**Reasoning:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.

**Clause-by-clause reading:**

- `FROM expenses AS e`: 10,000 expense rows, from 100.51 to 9,998.28 each.
- `GROUP BY e.category`: five buckets of 2,000 rows.
- `ROUND(SUM(e.amount), 2) AS total_expense`: each category's spend.
- `HAVING SUM(e.amount) > 1000000`: the repaired filter, applied to finished category totals instead of single rows.
- `ORDER BY total_expense DESC, e.category`: biggest spender first.

```sql
SELECT
  e.category,
  ROUND(SUM(e.amount), 2) AS total_expense
FROM
  expenses AS e
GROUP BY
  e.category
HAVING
  SUM(e.amount) > 1000000
ORDER BY
  total_expense DESC,
  e.category;
```

**Expected shape:** One row per expense category over the threshold.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 5, read the 10,000 `expenses` rows, 2,000 in each of 5 categories, with amounts from 100.51 to 9998.28. Return `category` and `total_expense`.
- **Expected result/shape:** For sql-02 Exercise 5, return 5 rows, because every category total is above 1,000,000: `Marketing` first at 10108910.00 and `Infrastructure` last at 10080670.00. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
- **Independent verification:** For sql-02 Exercise 5, rerun the grouping without `HAVING` and confirm the same 5 totals, each over 2,000 rows. Raise the threshold to 10100000; only `Marketing` and `COGS` (10103230.00) must remain.
- **What prints:** five rows: Marketing 10,108,910.00, COGS 10,103,230.00, G&A 10,096,250.00, Payroll 10,094,790.00 and Infrastructure 10,080,670.00.
- **The original error:** with `SUM(amount)` in `WHERE`, PostgreSQL stops at `aggregate functions are not allowed in WHERE`, because no category total exists while rows are still being filtered.
- **Threshold scale:** every category passes the 1,000,000 bar about ten times over, and the five totals add to 50,483,850.00, the sum of the whole table.
- **Mixing both filters:** a row test such as `WHERE e.amount >= 500` can stay in `WHERE` alongside the `HAVING`; it shrinks each category total before the group test runs.

## Exercise 6: Extension

**Prompt:** Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.

**Reasoning:** Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.

**Clause-by-clause reading:**

- `WHERE o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`: keeps orders from the first day of the month eleven months back. It compares the bare column, so an index on `order_date` can be used.
- `GROUP BY date_trunc('month', o.order_date)`: one bucket per calendar month, computed in the session time zone (UTC here).
- `COUNT(*)`, `ROUND(SUM(o.total_amount), 2)`: orders and revenue per month.
- `COUNT(*) FILTER (WHERE o.status = 'returned')`: returned orders per month, in the same pass.
- `::date` in the `SELECT` list and `ORDER BY order_month`: shows the month as a plain date, oldest first.

```sql
SELECT
  date_trunc('month', o.order_date)::date AS order_month,
  COUNT(*) AS order_count,
  ROUND(SUM(o.total_amount), 2) AS order_revenue,
  COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders
FROM
  orders AS o
WHERE
  o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'
GROUP BY
  date_trunc('month', o.order_date)
ORDER BY
  order_month;
```

**Expected shape:** Up to 12 month rows in chronological order.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 6, read from `orders` placed on or after `date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`, group them by `date_trunc('month', order_date)`, and return each month's order count, summed `total_amount`, and count of `returned` orders.
- **Expected result/shape:** For sql-02 Exercise 6, return 12 month rows in chronological order, since every month of the window has orders; the first `order_month` is the first day of the month eleven months before the current one, and the last is the current month. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
- **Independent verification:** For sql-02 Exercise 6, confirm that `order_month` values are unique and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`; for one month, recount its `returned` orders directly and compare the result with `returned_orders`.
- **What prints, in our check:** 12 rows from 2025-12-01 to 2026-11-01. Monthly orders climb from 142 to 313 in October, and November, the month still in progress, has 151 so far.
- **Totals for the window:** in our check the 12 months hold 2,535 of the 4,362 orders and 1,365,406.78 in revenue; recent months are busier because the fixture's order dates cluster toward the present.
- **Returned orders:** they range from 26 to 61 a month in our check. Because `FILTER` counts inside the same group, a month with no returns would show 0, not disappear.
- **"Up to" 12 rows:** a month with no orders at all would have no row. To force twelve rows, start from `generate_series` over the months and left join the orders.

## Final self-check

- Why can Example 1's `ORDER BY` use the alias `customers` while `HAVING customer_count > 62` fails?
- In Example 2, which number does `HAVING` test, and which does the query print?
- What three values does Exercise 4 return, and which identity links them on any data?
- Which error does the broken Exercise 5 raise, and why does `HAVING` fix it?
- Why might Exercise 6 return fewer than 12 rows on another dataset?
