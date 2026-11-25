# Day 16 solutions: Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each of the six answers places an aggregate inside `OVER (...)` and then decides what to partition by: customer in Exercises 1, 3 and 5, department in Exercise 2, and customer and country side by side in Exercise 6. Exercise 4 sets a window against `GROUP BY` so you can see the row counts differ. Try each prompt first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day16_solutions.sql
```

Expected row counts are 4,362, 100, 4,362, 2, 2,249 and 4,362. All statements only read, the file ends in `ROLLBACK`, and the excerpts below omit its `SET search_path` line. The numbering matches [the learner file](../day16_window_functions_fundamentals.sql); the study guide's [advice on studying a worked answer](../../STUDY-GUIDE.md#read-a-solution) suggests how to compare without copying.

## Reading contract

- **Focus:** Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
- **Assumptions:** Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
- **Primary pitfall:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
- **Safety:** read-only; the six statements are all `SELECT`s or `WITH ... SELECT`s inside a transaction that ends in `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Show each order with the customer's average order total.

**Reasoning:** Partition by customer ID and keep one output row per order.

**Clause-by-clause reading:**

- `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`: the average of all orders that share this row's `customer_id`, repeated on each of them.
- `ROUND(..., 2)`: rounds the displayed average to cents; the window itself averages exact values.
- `FROM orders AS o` with no `GROUP BY`: every order stays a separate row.
- `ORDER BY o.customer_id, o.order_date, o.order_id`: each customer's orders in date order, with the order ID as the final tie-breaker.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS customer_average
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 1, attach `ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2)` to each of the 4,362 `orders` rows; the 438 buyers have between 4 and 16 orders each.
- **Expected result/shape:** For sql-16 Exercise 1, return 4,362 rows, one per order, grouped by customer; customer 1's five orders (1 to 5) all show `customer_average` 504.33, and customer 500's ten orders show 613.75. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 1, confirm 4,362 distinct `order_id` values and that customer 1's value equals 2521.63 / 5 = 504.33 from `SELECT SUM(total_amount), COUNT(*) FROM orders WHERE customer_id = 1`. Inside a rolled-back transaction, add one order of 100.00 for customer 8, who has none; that new one-row partition must show `customer_average` 100.00 while customer 1's rows stay at 504.33.
- **What prints:** 4,362 rows. Customer 1 comes first with orders 1 to 5, all showing 504.33; customer 2's orders 6 to 11 all show 602.72.
- **Partition sizes:** the 438 customers with orders have between 4 and 16 each, so there is no one-row partition in this data. A one-order customer would simply see its own total as the average.
- **No `ORDER BY` inside `OVER`:** that is deliberate. Adding `ORDER BY o.order_date` there would make customer 1's values climb from 240.20 to 504.33 as a running average.
- **Same number, other routes:** `AVG(total_amount)` grouped by customer and joined back on `customer_id` gives identical averages, but needs a second pass over `orders` and a join.

## Exercise 2: Query writing

**Prompt:** Show each employee salary with department average, minimum, and maximum.

**Reasoning:** Partition all three window aggregates by department.

**Clause-by-clause reading:**

- `AVG(e.salary) OVER (PARTITION BY e.department_id)`: the department's mean salary on every employee row, rounded to cents.
- `MIN(e.salary) OVER (...)` and `MAX(e.salary) OVER (...)`: the lowest and highest salary in the same department.
- All three use the identical partition. Writing `WINDOW d AS (PARTITION BY e.department_id)` once and then `OVER d` would say the same thing more briefly.
- `ORDER BY e.department_id, e.employee_id`: department 1's employees first, by ID.

```sql
SELECT
  e.employee_id,
  e.department_id,
  e.salary,
  ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id), 2) AS department_average,
  MIN(e.salary) OVER (PARTITION BY e.department_id) AS department_minimum,
  MAX(e.salary) OVER (PARTITION BY e.department_id) AS department_maximum
FROM
  employees AS e
ORDER BY
  e.department_id,
  e.employee_id;
```

**Expected shape:** One row per employee.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 2, attach the department's `AVG`, `MIN`, and `MAX` salary to each of the 100 `employees` rows with three `OVER (PARTITION BY e.department_id)` windows.
- **Expected result/shape:** For sql-16 Exercise 2, return 100 rows, one per employee; department 1's 17 rows all carry average 43880.31, minimum 40079.19, and maximum 47681.43, and departments 5 and 6 have 16 rows each. The final columns are `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`. The final order is `e.department_id, e.employee_id`.
- **Independent verification:** For sql-16 Exercise 2, confirm 100 rows and that each department's three values match `SELECT department_id, ROUND(AVG(salary), 2), MIN(salary), MAX(salary) FROM employees GROUP BY department_id`. Inside a rolled-back transaction, set employee 1's salary to 50000; department 1 must change to 44463.89, 40554.33, and 50000.00 on all 17 rows, while department 2 stays at 43959.50, 40158.38, and 47760.62.
- **What prints:** 100 rows in six departments. Departments 1 to 4 have 17 employees each and departments 5 and 6 have 16.
- **First row:** employee 1 earns 40,079.19, which is also the department 1 minimum; the average is 43,880.31 and the maximum 47,681.43, earned by employee 97.
- **A regular fixture:** employee *n* sits in department ((*n* - 1) mod 6) + 1 and earns 40,000 + 79.19 * *n*. That is why departments 2 and 5 share an average of 43,959.50, and 3 and 6 share 44,038.69: their employee IDs have the same mean.
- **No gaps:** no employee has a `NULL` salary or department, so every row belongs to one of six partitions. A `NULL` department would form its own partition rather than disappearing.

## Exercise 3: Query writing

**Prompt:** Calculate every order's share of its customer's stored revenue.

**Reasoning:** Use a partition total denominator and guard it with `NULLIF`.

**Clause-by-clause reading:**

- `SUM(o.total_amount) OVER (PARTITION BY o.customer_id)`: the customer's lifetime revenue, placed on each of that customer's orders.
- `o.total_amount / NULLIF(..., 0)`: the order's share of that revenue; a customer whose orders all totalled 0 would get `NULL` instead of an error.
- `ROUND(..., 4)`: four decimal places, so 0.4584 reads as 45.84%.
- `ORDER BY o.customer_id, o.order_date, o.order_id`: the same order as Exercise 1.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  ROUND(o.total_amount / NULLIF (SUM(o.total_amount) OVER (PARTITION BY o.customer_id), 0), 4) AS customer_revenue_share
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order with shares summing near one per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 3, divide each order's `total_amount` by `SUM(o.total_amount) OVER (PARTITION BY o.customer_id)`, guarded with `NULLIF(..., 0)`, and round the share to 4 places.
- **Expected result/shape:** For sql-16 Exercise 3, return 4,362 rows, one per order; customer 1's five shares are 0.0953, 0.1657, 0.2386, 0.4584, and 0.0420, which add to exactly 1.0000. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 3, sum the shares per customer: all 438 totals must be within 0.0003 of 1, and 231 of them miss 1 exactly only because of rounding to 4 places. Inside a rolled-back transaction, add one order for customer 8, who has none; that one-row partition must show a share of 1.0000.
- **What prints:** 4,362 rows. Customer 1's shares are 0.0953, 0.1657, 0.2386, 0.4584 and 0.0420.
- **Summing near one:** customer 1's five shares add to exactly 1.0000, as do those of 207 customers. The other 231 land between 0.9997 and 1.0002, because each share was rounded on its own.
- **Largest share:** order 3074 makes up 0.5320 of customer 351's revenue, the highest in the table.
- **Why a window here:** the denominator is a per-customer total but the numerator is per order. With `GROUP BY` you would need a second query and a join to bring them together.

## Exercise 4: Prediction

**Prompt:** Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.

**Reasoning:** Grouping collapses to one row per customer; a window preserves every order row.

**Clause-by-clause reading:**

- `grouped`: `AVG(o.total_amount)` with `GROUP BY o.customer_id`, one row per customer who ordered.
- `windowed`: `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`, one row per order.
- `SELECT 'grouped' ..., COUNT(*) ... UNION ALL SELECT 'windowed' ...`: one labelled count from each CTE, stacked into a two-row result.
- `ORDER BY method`: alphabetical, so `grouped` comes first.

```sql
WITH grouped AS (
  SELECT
    o.customer_id,
    AVG(o.total_amount) AS average_total
  FROM
    orders AS o
  GROUP BY
    o.customer_id
),
windowed AS (
  SELECT
    o.order_id,
    AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS average_total
  FROM
    orders AS o
)
SELECT
  'grouped' AS method,
  COUNT(*) AS row_count
FROM
  grouped
UNION ALL
SELECT
  'windowed' AS method,
  COUNT(*) AS row_count
FROM
  windowed
ORDER BY
  method;
```

**Expected shape:** Two labeled count rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 4, compare a `grouped` CTE (`AVG(o.total_amount) ... GROUP BY o.customer_id`) with a `windowed` CTE (`AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`) over `orders`, then count the rows of each.
- **Expected result/shape:** For sql-16 Exercise 4, expected output: two rows ordered by `method`, with columns `method` and `row_count`: `('grouped', 438)` and `('windowed', 4362)` on the course seed.
- **Independent verification:** For sql-16 Exercise 4, confirm that the `grouped` count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` and the `windowed` count equals `SELECT COUNT(*) FROM orders`; grouping keeps one row per ordering customer, while the window keeps every order row.
- **What prints:** `grouped` 438 and `windowed` 4,362.
- **Same averages, different grain:** both CTEs compute the identical 438 averages. The window version just repeats each one on every order, about ten times per customer on average.
- **Missing customers:** the 62 BR customers have no orders, so neither CTE mentions them. The table holds 500 customers, but both counts are driven by `orders`.
- **`UNION ALL`:** the two branches can never produce duplicate rows because their labels differ, so `UNION` would give the same output at the cost of a needless duplicate check.

## Exercise 5: Debugging

**Prompt:** Return orders above their customer average without placing a window function in `WHERE`.

**Reasoning:** Compute the window value in a CTE, then filter the named column outside.

**Clause-by-clause reading:**

- `scored` CTE: `SELECT o.*, AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_average`, so every order gains a named column holding its customer's average.
- Outer `WHERE total_amount > customer_average`: legal here, because by now `customer_average` is an ordinary column of `scored`.
- `ROUND(customer_average, 2)` in the outer `SELECT`: rounding only for display, after the comparison used the exact average.
- `ORDER BY customer_id, total_amount DESC, order_id`: each customer's largest qualifying order first.

```sql
WITH scored AS (
  SELECT
    o.*,
    AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_average
  FROM
    orders AS o
)
SELECT
  order_id,
  customer_id,
  total_amount,
  ROUND(customer_average, 2) AS customer_average
FROM
  scored
WHERE
  total_amount > customer_average
ORDER BY
  customer_id,
  total_amount DESC,
  order_id;
```

**Expected shape:** Order rows above their customer mean.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 5, compute `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)` as `customer_average` in a `scored` CTE over `orders`, then filter `total_amount > customer_average` in the outer query.
- **Expected result/shape:** For sql-16 Exercise 5, expected output: one row per `order_id` whose `total_amount` is strictly above its customer's mean (2,249 rows on the course seed), with columns `order_id`, `customer_id`, `total_amount`, and `customer_average` (rounded to 2 places), ordered by `customer_id, total_amount DESC, order_id`.
- **Independent verification:** For sql-16 Exercise 5, compare the row count with `SELECT COUNT(*) FROM orders o WHERE o.total_amount > (SELECT AVG(i.total_amount) FROM orders i WHERE i.customer_id = o.customer_id)` (2,249), require unique `order_id`, and confirm that moving the window expression into `WHERE` fails with `window functions are not allowed in WHERE`.
- **What prints:** 2,249 rows. First come customer 1's orders 4 (1,155.92) and 3 (601.73), both above 504.33, then customer 2's order 8 at 917.69.
- **Every customer qualifies:** all 438 customers have at least one order above their own average, and no order equals its customer's average exactly, so the strict `>` drops nothing by accident here.
- **The error being fixed:** putting the window in `WHERE` raises `window functions are not allowed in WHERE`, because PostgreSQL filters rows before it computes windows.
- **Compare before rounding:** filtering on the rounded value could misjudge an order within half a cent of the average. This query compares first and rounds afterwards.

## Exercise 6: Extension

**Prompt:** Show order count and revenue context at both customer and country levels in the same row.

**Reasoning:** Use different partitions for independent analytical contexts.

**Clause-by-clause reading:**

- `JOIN customers AS c ON c.customer_id = o.customer_id`: brings in `country`. Each order matches exactly one customer, so the join keeps 4,362 rows.
- `COUNT(*)` and `SUM(o.total_amount)` `OVER (PARTITION BY o.customer_id)`: the customer's order count and revenue.
- `SUM(o.total_amount) OVER (PARTITION BY c.country)`: a different partition in the same `SELECT`, giving the revenue of the customer's whole country.
- `ORDER BY c.country, o.customer_id, o.order_date, o.order_id`: grouped by country, then customer, then date.

```sql
SELECT
  o.order_id,
  o.customer_id,
  c.country,
  COUNT(*) OVER (PARTITION BY o.customer_id) AS customer_order_count,
  SUM(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_revenue,
  SUM(o.total_amount) OVER (PARTITION BY c.country) AS country_revenue
FROM
  orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id
ORDER BY
  c.country,
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order with customer and country totals.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 6, join `orders` to `customers` and attach three windows to each order: `COUNT(*)` and `SUM(total_amount)` partitioned by `o.customer_id`, and `SUM(total_amount)` partitioned by `c.country`.
- **Expected result/shape:** For sql-16 Exercise 6, return 4,362 rows, one per order, across 7 countries (`BR` has no orders); the first rows are customer 7's 11 orders in `AU`, each with `customer_revenue` 5274.48 and `country_revenue` 330947.62. The final columns are `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`. The final order is `c.country, o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 6, confirm that the 7 distinct `country_revenue` values match `SELECT c.country, SUM(o.total_amount) FROM orders o JOIN customers c USING (customer_id) GROUP BY c.country` (from 329081.73 for `IN` to 343290.09 for `FR`) and add up to 2355646.89. Inside a rolled-back transaction, add one 100.00 order for customer 8; a `BR` row must appear with a count of 1 and both revenues at 100.00.
- **What prints:** 4,362 rows. The first is order 46 for customer 7 in AU: 11 orders, 5,274.48 in customer revenue and 330,947.62 for AU.
- **Seven countries, not eight:** BR customers placed no orders, so `country_revenue` takes only seven values, from 329,081.73 (IN) to 343,290.09 (FR). They add up to 2,355,646.89, the sum of all order totals.
- **Partitions are independent:** each window is computed separately, so the country window does not need the customer window and the two can use different keys in one pass.
- **Country share:** `customer_revenue / country_revenue` would show how much of AU's revenue customer 7 accounts for, with no extra join.

## Final self-check

- Why do all five of customer 1's rows show 504.33 in Exercise 1, and what would change if `ORDER BY order_date` went inside the `OVER`?
- Which two departments share an average salary in Exercise 2, and why?
- How can a customer's rounded shares in Exercise 3 add up to 0.9997?
- Where do the 438 and 4,362 in Exercise 4 come from, and why do neither of them include the 62 BR customers?
- Why does Exercise 5 need a CTE, and what error appears without one?
