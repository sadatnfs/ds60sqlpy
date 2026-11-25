# Day 07 solutions: Week 1 Project: From Questions to Queries

<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers are reads that, between them, describe the whole Week 1 fixture: Exercise 1 by status, 2 by product, 3 by customer, 4 by order, 5 by month and 6 as one audit row. Make your own attempt first, then run the companion:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day07_solutions.sql
```

It switches `search_path` to `training, public` and keeps everything inside `BEGIN`/`ROLLBACK`. Totals that ignore dates (5 statuses, 500 customers, 4,362 orders, 2,355,646.89) should match yours exactly; month labels in Exercise 5 follow the date the fixture was loaded. The answers follow [day07_week1_project.sql](../day07_week1_project.sql) prompt by prompt, and the [solution reading steps](../../STUDY-GUIDE.md#read-a-solution) apply.

## Reading contract

- **Focus:** Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
- **Assumptions:** Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
- **Primary pitfall:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
- **Safety:** nothing here writes. The companion still runs inside `BEGIN`/`ROLLBACK`, so trial inserts made while testing the edge cases disappear at the end.

## Exercise 1: Query writing

**Prompt:** Build an order KPI table by status with order count, revenue, average order value, and distinct customers.

**Reasoning:** Aggregate orders at status grain and round only displayed monetary values.

**Clause-by-clause reading:**

- `FROM orders AS o`: one row per order, 4,362 in all.
- `GROUP BY o.status`: five buckets, one per status value.
- `COUNT(*)` and `COUNT(DISTINCT o.customer_id)`: orders in the bucket, and the number of different people who placed them.
- `ROUND(SUM(...), 2)` and `ROUND(AVG(...), 2)`: stored revenue and average order value, rounded only for display.
- `ORDER BY revenue DESC, o.status`: largest status first; the status name breaks a tie.

```sql
SELECT
  o.status,
  COUNT(*) AS order_count,
  COUNT(DISTINCT o.customer_id) AS customer_count,
  ROUND(SUM(o.total_amount), 2) AS revenue,
  ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM
  orders AS o
GROUP BY
  o.status
ORDER BY
  revenue DESC,
  o.status;
```

**Expected shape:** One row per order status.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 1, group the 4,362 `orders` rows by `status`; there are five statuses, `placed` and `shipped` with 873 orders each and `delivered`, `paid`, and `returned` with 872 each.
- **Expected result/shape:** For sql-07 Exercise 1, return 5 rows, one per status, led by `paid` with 872 orders, 432 customers, and 478068.36 revenue, and ending with `returned` at 468083.26. The final columns are `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`. The final order is `revenue DESC, o.status`.
- **Independent verification:** For sql-07 Exercise 1, confirm the five `order_count` values sum to 4362 and the five `revenue` values sum to 2355646.89, the same as `SELECT ROUND(SUM(total_amount), 2) FROM orders`. Inside a rolled-back transaction, set order 21's status to `cancelled`; the result must grow to 6 rows, with `cancelled` showing 1 order and `paid` dropping to 871.
- **What prints:** five rows. `paid` leads with 872 orders from 432 customers, 478,068.36 revenue and a 548.24 average; then `delivered` (470,008.41), `placed` (469,843.10), `shipped` (469,643.76) and `returned` (468,083.26). The four other statuses each have 431 customers.
- **Reconciling it:** order counts add to 4,362 and revenue to 2,355,646.89. `customer_count` adds to 2,156, far above the 438 customers who ordered, because one customer can hold orders in several statuses. Distinct counts never add across groups.
- **Testing the add-a-row rule:** insert an order with status `paid` and `paid` grows by one order; insert one with a new status such as `cancelled` and a sixth row appears.
- **Equivalent query:** `GROUP BY 1` would work, but naming `o.status` survives someone adding a column at the front of the select list.

## Exercise 2: Query writing

**Prompt:** Return the 20 products with the highest net line revenue.

**Reasoning:** Aggregate order items by product before ranking; use product ID as tie-breaker.

**Clause-by-clause reading:**

- `FROM products AS p JOIN order_items AS oi`: one row per sold line. Never-sold products (276 to 300) drop out, which is fine for a top-20 list.
- `SUM(oi.unit_price * oi.quantity * (1 - oi.discount))`: net revenue computed per line, then added up per product.
- `GROUP BY p.product_id, p.name, p.category`: one row per product; name and category ride along with the ID.
- `ORDER BY net_revenue DESC, p.product_id LIMIT 20`: ranks first, then cuts at 20.

```sql
SELECT
  p.product_id,
  p.name,
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM
  products AS p
  JOIN order_items AS oi ON oi.product_id = p.product_id
GROUP BY
  p.product_id,
  p.name,
  p.category
ORDER BY
  net_revenue DESC,
  p.product_id
LIMIT 20;
```

**Expected shape:** At most 20 product rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 2, join the 13,085 `order_items` rows to `products`, sum `unit_price * quantity * (1 - discount)` per product across the 275 products that have sold, and keep the top 20.
- **Expected result/shape:** For sql-07 Exercise 2, return 20 rows, one per product, from product 271 (Apparel, 17643.20) down to product 260 (Electronics, 15292.80). The final columns are `product_id`, `name`, `category`, and `net_revenue`. The final order is `net_revenue DESC, p.product_id`.
- **Independent verification:** For sql-07 Exercise 2, confirm 20 distinct `product_id` values with `net_revenue` never rising from one row to the next. Rerun with `LIMIT 21`; the only added row must be product 231 at 15275.20, which is below product 260, so the cutoff falls between two different values rather than inside a tie.
- **What prints:** 20 rows from product 271 (Apparel, 17,643.20) down to 260 (Electronics, 15,292.80). Every one has an ID between 236 and 275, because prices rise with the product number in this catalog.
- **Just outside the cut:** product 231 (Home, 15,275.20) would be 21st. Change the limit to 21 to watch it appear, which is the quickest check that the cutoff sits where you expect.
- **A common slip:** computing `SUM(unit_price) * SUM(quantity)` multiplies two unrelated totals and inflates every product. The discount differs line by line, so the multiplication has to happen before the sum.
- **Equivalent query:** aggregate `order_items` by `product_id` in a CTE, rank it, then join `products` for the names. It touches `products` only 20 times.

## Exercise 3: Query writing

**Prompt:** Create a customer summary that retains customers with no orders.

**Reasoning:** Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.

**Clause-by-clause reading:**

- `FROM customers AS c LEFT JOIN orders AS o`: keeps every customer; the 62 without orders appear once with NULL order columns.
- `COUNT(o.order_id)`: counts only real orders, so those 62 get 0 rather than 1.
- `COALESCE(ROUND(SUM(o.total_amount), 2), 0)`: an empty sum is NULL, and here "spent nothing" is the honest reading, so 0 is shown.
- `GROUP BY c.customer_id, c.full_name, c.country`: back to one row per customer.
- `ORDER BY stored_order_total DESC, c.customer_id`: biggest spenders first, IDs ordering the zeros.

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  COUNT(o.order_id) AS order_count,
  COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_order_total
FROM
  customers AS c
  LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.full_name,
  c.country
ORDER BY
  stored_order_total DESC,
  c.customer_id;
```

**Expected shape:** One row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 3, `LEFT JOIN` the 500 `customers` rows to `orders`, count `o.order_id` and sum `total_amount` per customer, and turn a missing sum into 0 with `COALESCE`.
- **Expected result/shape:** For sql-07 Exercise 3, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21); the 62 customers without orders sort last with 0 orders and a 0 total. The final columns are `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`. The final order is `stored_order_total DESC, c.customer_id`.
- **Independent verification:** For sql-07 Exercise 3, confirm the `order_count` column sums to 4362, `stored_order_total` sums to 2355646.89, and exactly 62 rows show 0 orders. An inner join must return only 438 rows, and counting `*` instead of `o.order_id` must wrongly give those 62 customers an `order_count` of 1.
- **What prints:** 500 rows. Customer 181 (FR) tops the list with 16 orders and 9,502.21, ahead of customer 12 (DE, 9,244.27) and 25 (US, 9,196.96). The last 62 rows are the Brazilian customers, each with 0 orders and 0 spent.
- **Where it goes wrong:** an inner join returns 438 rows and loses Brazil completely. A left join with `COUNT(*)` keeps them but credits each with one order that never happened.
- **Applying the add-a-row rule:** a new customer without orders adds row 501 at the bottom; a new order for customer 181 changes only that customer's two numbers.
- **Equivalent query:** sum `orders` per customer in a CTE, then left join it to `customers`. That shape keeps working when a second detail table joins later.
- **A quick count to run:** `SELECT COUNT(*) FILTER (WHERE order_count = 0)` over your result should return 62, and `SUM(order_count)` should return 4,362. If the first is 0 your join dropped Brazil; if the second is higher, something fanned out.

## Exercise 4: Debugging

**Prompt:** Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.

**Reasoning:** Aggregate each detail table to order grain first, then join the one-row-per-order relations.

**Clause-by-clause reading:**

- `item_totals`: net line revenue per order, 4,362 rows because every order has lines.
- `payment_totals`: payments per order. The 3,836 payment rows shrink to 3,489 orders here, so the 347 split payments are folded in before any join.
- `JOIN item_totals`: safe as an inner join since no order is missing lines.
- `LEFT JOIN payment_totals` with `COALESCE(pt.paid_total, 0)`: the 873 placed orders have no payments, and for them "paid 0" is literally true.
- `ORDER BY ABS(o.total_amount - it.line_total) DESC, o.order_id`: largest unrounded disagreement first.

```sql
WITH item_totals AS (
  SELECT
    oi.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM
    order_items AS oi
  GROUP BY
    oi.order_id
),
payment_totals AS (
  SELECT
    p.order_id,
    SUM(p.amount) AS paid_total
  FROM
    payments AS p
  GROUP BY
    p.order_id
)
SELECT
  o.order_id,
  o.status,
  ROUND(o.total_amount, 2) AS stored_total,
  ROUND(it.line_total, 2) AS line_total,
  ROUND(o.total_amount - it.line_total, 2) AS storage_difference,
  ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
  ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM
  orders AS o
  JOIN item_totals AS it ON it.order_id = o.order_id
  LEFT JOIN payment_totals AS pt ON pt.order_id = o.order_id
ORDER BY
  ABS(o.total_amount - it.line_total) DESC,
  o.order_id;
```

**Expected shape:** One row per order with signed differences.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 4, pre-aggregate `order_items` to one `line_total` per order and `payments` to one `paid_total` per order, then join both to the 4,362 `orders` rows, with `LEFT JOIN` for payments because 873 orders have none.
- **Expected result/shape:** For sql-07 Exercise 4, return 4,362 rows, one per order; every `storage_difference` rounds to 0.00 (the largest raw gap is 0.0045), while 1,072 rows have a nonzero `unpaid_balance` of up to 1432.49. The final columns are `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`. The final order is `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
- **Independent verification:** For sql-07 Exercise 4, confirm 4,362 distinct `order_id` values and that the 1,072 nonzero balances split into 873 orders with `paid_total` 0.00 and 199 paid orders whose payments differ from `total_amount`. Joining raw `order_items` and `payments` to `orders` without pre-aggregation returns 13,432 rows and inflates the summed `total_amount` to 8673949.32.
- **What prints:** 4,362 rows. `storage_difference` is 0.00 on every row: each stored total was rounded from its own lines, and the largest raw gap is 0.0045. The top rows (orders 21, 28 and 43) differ by exactly that half cent, with the order ID breaking the tie.
- **The informative column:** `unpaid_balance`. 3,290 orders are settled at 0.00, none is overpaid, the 873 placed orders owe their whole total, and 199 other orders owe part of theirs. All balances add to 523,746.08.
- **The tempting shortcut:** joining `order_items` and `payments` to `orders` in one `FROM` gives 10,816 rows and double-counts every line of a split-payment order.
- **Applying the add-a-row rule:** a new order with lines but no payment adds one row whose `unpaid_balance` equals its stored total.

## Exercise 5: Prediction

**Prompt:** Build a monthly order trend and explain which months are absent rather than zero.

**Reasoning:** Grouping observed orders alone cannot create empty calendar months.

**Clause-by-clause reading:**

- `date_trunc('month', o.order_date)::date`: the first day of each order's month in the session time zone, shown as a date.
- `GROUP BY date_trunc('month', o.order_date)`: the same expression without the cast, so each month forms one bucket.
- `COUNT(*)` and `ROUND(SUM(o.total_amount), 2)`: orders and stored revenue per month.
- `ORDER BY order_month`: oldest first.

```sql
SELECT
  date_trunc('month', o.order_date)::date AS order_month,
  COUNT(*) AS order_count,
  ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM
  orders AS o
GROUP BY
  date_trunc('month', o.order_date)
ORDER BY
  order_month;
```

**Expected shape:** One row per observed order month.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 5, read from `orders`, group by `date_trunc('month', order_date)`, and return each month's `order_count` and `stored_revenue` (`SUM(total_amount)` rounded to 2 places).
- **Expected result/shape:** For sql-07 Exercise 5, return 46 rows, one per calendar month with orders, from 2023-02-01 with 2 orders to the current month, which has 151 orders on a freshly loaded fixture. The final columns are `order_month`, `order_count`, and `stored_revenue`. The final order is `order_month`.
- **Independent verification:** For sql-07 Exercise 5, confirm that `order_month` is unique, that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders` (4362), and that the monthly `stored_revenue` values add up to `SELECT ROUND(SUM(total_amount), 2) FROM orders` (2355646.89).
- **What prints:** 46 rows on the load used here, February 2023 through November 2026. The opening months are thin (2, 3 and 6 orders) as the fixture ramps up, and the newest month is partial: 151 orders against 313 the month before, because the data stops at load time.
- **Absent versus zero:** a month with no orders produces no row at all. To prove there are no gaps, count `generate_series` from the first month to the last in steps of one month; it returns 46 as well, so every month is present. A month outside that span is absent, not zero.
- **Reconciling it:** `order_count` adds to 4,362 and `stored_revenue` to 2,355,646.89.
- **Time zone note:** the classroom session runs in UTC. Under another `TimeZone` an order placed near midnight on a month's last day can move into the next month; `order_date AT TIME ZONE 'UTC'` would pin the buckets.

## Exercise 6: Extension

**Prompt:** Create a compact one-row audit of customer, order, item, and payment coverage.

**Reasoning:** Use scalar subqueries for independent counts; this avoids accidental cross multiplication.

**Clause-by-clause reading:**

- Four scalar subqueries, each `SELECT COUNT(*)` over one table, so no table is ever joined to another.
- `NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id)`: counts customers with no matching order.
- No outer `FROM`: a `SELECT` of scalar subqueries returns exactly one row.

```sql
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      customers) AS customer_rows,
  (
    SELECT
      COUNT(*)
    FROM
      orders) AS order_rows,
  (
    SELECT
      COUNT(*)
    FROM
      order_items) AS order_item_rows,
  (
    SELECT
      COUNT(*)
    FROM
      payments) AS payment_rows,
  (
    SELECT
      COUNT(*)
    FROM
      customers AS c
    WHERE
      NOT EXISTS (
        SELECT
          1
        FROM
          orders AS o
        WHERE
          o.customer_id = c.customer_id)) AS customers_without_orders;
```

**Expected shape:** Exactly one audit row.

### Reasoning and verification

- **Inputs/evidence:** For sql-07 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Compute `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-07 Exercise 6, return one row: 500 customer rows, 4,362 order rows, 13,085 order item rows, 3,836 payment rows, and 62 customers without orders. The final columns are `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
- **Independent verification:** For sql-07 Exercise 6, confirm each value equals its own standalone `COUNT(*)`, and that 62 matches Exercise 3's count of zero-order customers. Inside a rolled-back transaction, insert one customer with no orders; the result must stay one row, with `customer_rows` at 501 and `customers_without_orders` at 63.
- **What prints:** one row, 500 | 4,362 | 13,085 | 3,836 | 62. Each value matches an earlier answer: Exercise 3's row count, Exercise 1's order total, the line count behind Exercise 2 and the 62 zero rows at the bottom of Exercise 3.
- **Why not one join:** `customers JOIN orders JOIN order_items JOIN payments` would yield 10,816 rows, and every `COUNT(*)` would report that same number.
- **Applying the add-a-row rule:** a new customer raises `customer_rows` to 501 and `customers_without_orders` to 63, while the output stays one row.
- **Equivalent query:** a CTE per count, cross joined. It reads the same and makes room for sums such as stored revenue next to each count.

## Final self-check

- Which number in Exercise 6 would change if you deleted one payment from a split-payment order, and which would not?
- Why does Exercise 1's `customer_count` add to more than 438?
- In Exercise 4, what fact makes `COALESCE(pt.paid_total, 0)` honest rather than a cover-up?
- How would you prove that Exercise 5 has no missing months on your own load?
- What allocation rule would you state before reporting revenue by payment method?
