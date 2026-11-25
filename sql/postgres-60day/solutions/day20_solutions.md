# Day 20 solutions: FIRST_VALUE, LAST_VALUE, and Window Frames

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Five answers use `FIRST_VALUE` and `LAST_VALUE` over a full frame: per customer's orders (Exercises 1 and 5), per category's prices (Exercise 2) and per order's payments (Exercise 3). Exercise 4 shows the default frame failing on three numbers, and Exercise 6 swaps windows for PostgreSQL's `DISTINCT ON`. Attempt each yourself, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day20_solutions.sql
```

Expect 4,362, 300, 3,836, 3, 438 and 438 rows. The script only reads and finishes with `ROLLBACK`; the excerpts below skip its `SET search_path` line. They correspond to [the learner file](../day20_first_last_value.sql), and the study guide has advice on [comparing a worked answer with yours](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Primary pitfall:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Safety:** read-only; every statement is a `SELECT` inside a transaction that ends in `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Show every order with the customer's first and last order timestamps.

**Reasoning:** Use one full-partition frame from unbounded preceding through unbounded following.

**Clause-by-clause reading:**

- `WINDOW customer_orders AS (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)`: one named window, used by both functions.
- `FIRST_VALUE(o.order_date) OVER customer_orders AS first_order_date`: the earliest order's date for the row's customer.
- `LAST_VALUE(o.order_date) OVER customer_orders AS last_order_date`: the latest, which needs the full frame.
- `ORDER BY o.customer_id, o.order_date, o.order_id`: the customer's orders in sequence.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  FIRST_VALUE(o.order_date) OVER customer_orders AS first_order_date,
  LAST_VALUE(o.order_date) OVER customer_orders AS last_order_date
FROM
  orders AS o
WINDOW customer_orders AS (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order with constant first/last values per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 1, read from `orders` and return, for every order, its customer's first and last `order_date` with `FIRST_VALUE` and `LAST_VALUE` over a named window partitioned by `customer_id`, ordered by `order_date, order_id`, with the frame `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
- **Expected result/shape:** For sql-20 Exercise 1, return 4,362 rows, one per order, where both dates stay constant within each of the 438 customers; customer 1's five rows all show order 1's date as `first_order_date` and order 5's date as `last_order_date`. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-20 Exercise 1, confirm 4362 rows and compare them with `SELECT customer_id, MIN(order_date), MAX(order_date) FROM orders GROUP BY customer_id` (438 customers): no row may differ. With the default frame instead, `LAST_VALUE` returns each row's own `order_date` on all 4362 rows.
- **What prints:** 4,362 rows, one per order, for the 438 customers who have orders. Customer 1's five rows all show order 1's date as first and order 5's as last.
- **A grouped cross-check:** `MIN(order_date)` and `MAX(order_date)` per customer must equal the two window columns, because here the ordering column and the reported value are the same.
- **Without the frame:** `LAST_VALUE` returns each row's own `order_date` on all 4,362 rows, since no customer has two orders with the same timestamp.
- **Why a named window:** writing the partition, order and frame once guarantees both functions read the same rows; a typo in one of two copies would be easy to miss.

## Exercise 2: Query writing

**Prompt:** Show each product with the cheapest and most expensive price in its category.

**Reasoning:** Order by price and use a full frame; values tie without needing row identity.

**Clause-by-clause reading:**

- `WINDOW category_prices AS (PARTITION BY p.category ORDER BY p.price, p.product_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)`: products within a category from cheapest to dearest.
- `FIRST_VALUE(p.price)`: the first price under that order, the category's cheapest.
- `LAST_VALUE(p.price)`: the last price, the dearest, thanks to the full frame.
- `ORDER BY p.category, p.price, p.product_id`: categories alphabetically, cheapest product first.

```sql
SELECT
  p.product_id,
  p.category,
  p.price,
  FIRST_VALUE(p.price) OVER category_prices AS category_min_price,
  LAST_VALUE(p.price) OVER category_prices AS category_max_price
FROM
  products AS p
WINDOW category_prices AS (PARTITION BY p.category ORDER BY p.price, p.product_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY
  p.category,
  p.price,
  p.product_id;
```

**Expected shape:** One row per product.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 2, read from `products` and show each product with the lowest and highest `price` in its `category`, using `FIRST_VALUE` and `LAST_VALUE` over a window ordered by `price, product_id` with a full frame.
- **Expected result/shape:** For sql-20 Exercise 2, return 300 rows, one per product, with two values per category; `Apparel` rows all show 10.37 and 119.15, `Books` rows show 12.22 and 121.00, and `Sports` rows show 11.85 and 120.63. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-20 Exercise 2, confirm 300 rows and compare the two window columns with `SELECT category, MIN(price), MAX(price) FROM products GROUP BY category`; for example, every `Apparel` row must show 10.37 and 119.15.
- **What prints:** 300 rows, 50 per category. Every Apparel row shows 10.37 and 119.15; the other categories run from about 11 to 121.
- **First equals minimum here:** because the window is ordered by `p.price` itself, the first and last values are the minimum and maximum. `MIN(p.price) OVER (PARTITION BY p.category)` would give the same column without any frame.
- **Ties:** each category's 50 prices are all different in this fixture, so `p.product_id` never decides anything; if two products shared the lowest price, it would only choose which row is first, not the value.
- **When the window version is worth it:** use `FIRST_VALUE` when you need another column of the boundary row, such as `FIRST_VALUE(p.product_id)` for the cheapest product's ID, which `MIN` cannot return.

## Exercise 3: Query writing

**Prompt:** Compare every payment with the first and last payment amount for its order.

**Reasoning:** Partition by order, order by timestamp/payment ID, and keep the full frame.

**Clause-by-clause reading:**

- `WINDOW payment_sequence AS (PARTITION BY p.order_id ORDER BY p.payment_date, p.payment_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)`: each order's payments in time order.
- `FIRST_VALUE(p.amount)` and `LAST_VALUE(p.amount)`: the amounts of the earliest and latest payment.
- `ORDER BY p.order_id, p.payment_date, p.payment_id`: payments grouped by order.

```sql
SELECT
  p.payment_id,
  p.order_id,
  p.payment_date,
  p.amount,
  FIRST_VALUE(p.amount) OVER payment_sequence AS first_payment_amount,
  LAST_VALUE(p.amount) OVER payment_sequence AS last_payment_amount
FROM
  payments AS p
WINDOW payment_sequence AS (PARTITION BY p.order_id ORDER BY p.payment_date, p.payment_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY
  p.order_id,
  p.payment_date,
  p.payment_id;
```

**Expected shape:** One row per payment.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 3, read from `payments` and compare every payment with the first and last payment `amount` of its order, using a window partitioned by `order_id`, ordered by `payment_date, payment_id`, with a full frame.
- **Expected result/shape:** For sql-20 Exercise 3, return 3,836 rows, one per payment; on the 3,142 single-payment orders both window columns repeat the payment's own `amount`, while order 10's two payments show a first amount of 71.72 and a last of 71.71. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
- **Independent verification:** For sql-20 Exercise 3, confirm 3836 rows, one per `payment_id`; 3489 orders have payments, 347 of them have two payments, and only 20 orders have a first amount that differs from the last, so check one of those 20 orders by hand.
- **What prints:** 3,836 rows, one per payment, covering 3,489 orders. 3,142 orders have one payment and 347 have two; no order has more.
- **Single-payment orders:** the frame holds one row, so both columns equal that payment's own amount.
- **Split payments:** only 20 orders have a first amount different from the last. Order 10 is one: its 143.43 total was paid as 71.72 by bank and then 71.71 by credit six hours later, so both rows show 71.72 and 71.71.
- **Unpaid orders are absent:** the query starts from `payments`, so the 873 orders with no payment produce no rows at all.

## Exercise 4: Prediction

**Prompt:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.

**Reasoning:** The default ends at the current row; explicit following reaches the true last row.

**Clause-by-clause reading:**

- `FROM (VALUES (10), (20), (30)) AS sample (value)`: three distinct numbers, no table needed.
- `LAST_VALUE(value) OVER (ORDER BY value) AS default_last_value`: no frame clause, so the frame ends at the current row.
- `LAST_VALUE(value) OVER (ORDER BY value ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last_value`: the full frame.
- No `PARTITION BY`: all three rows form one partition.

```sql
SELECT
  value,
  LAST_VALUE(value) OVER (ORDER BY value) AS default_last_value,
  LAST_VALUE(value) OVER (ORDER BY value ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last_value
FROM (
  VALUES (10),
    (20),
    (30)) AS sample (value)
ORDER BY
  value;
```

**Expected shape:** Three rows showing default current value and full-frame 30.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 4, apply `LAST_VALUE(value)` to the three-row `VALUES` fixture `(10), (20), (30)` twice: once over `ORDER BY value` with the default frame, and once with `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
- **Expected result/shape:** For sql-20 Exercise 4, return three rows: values 10, 20, and 30 with `default_last_value` 10, 20, and 30 and `partition_last_value` 30 on every row. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
- **Independent verification:** For sql-20 Exercise 4, check by hand that the default frame stops at the current row, so `default_last_value` repeats `value`, while the full frame reaches 30. Add `(NULL::int)` to the fixture; ascending order puts `NULL` last, so all four rows must then show `NULL` as `partition_last_value`, while the first three keep `default_last_value` 10, 20, and 30.
- **What prints:** 10 / 10 / 30, 20 / 20 / 30 and 30 / 30 / 30. The default column copies `value`; the full-frame column is 30 on every row.
- **Only the last row agrees:** at 30 the default frame already reaches the end of the partition, so both columns match there and nowhere else.
- **With a tie:** add a second 20 and both 20 rows still show 20 in the default column, because tied rows are peers that share one frame end.
- **Seeing the peer effect:** with a label column, `(20, 'b')` and `(20, 'c')`, `LAST_VALUE(tag) OVER (ORDER BY value)` shows `c` on both 20 rows, the last peer, not the row's own `b`.

## Exercise 5: Debugging

**Prompt:** Return one first and one last order per customer without using window output as an accidental duplicate report.

**Reasoning:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.

**Clause-by-clause reading:**

- `WITH annotated AS (...)`: one row per order, carrying the customer's `first_order_id` and `last_order_id` from full-frame windows.
- `SELECT DISTINCT customer_id, first_order_id, last_order_id`: all three columns repeat within a customer, so each customer collapses to one row.
- `ORDER BY customer_id`: one line per customer.

```sql
WITH annotated AS (
  SELECT
    o.customer_id,
    FIRST_VALUE(o.order_id) OVER customer_orders AS first_order_id,
      LAST_VALUE(o.order_id) OVER customer_orders AS last_order_id
      FROM
        orders AS o
WINDOW customer_orders AS (PARTITION BY o.customer_id ORDER BY o.order_date,
  o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING))
SELECT DISTINCT
  customer_id,
  first_order_id,
  last_order_id
FROM
  annotated
ORDER BY
  customer_id;
```

**Expected shape:** One row per customer with orders.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 5, read from `orders`, compute each customer's first and last `order_id` with full-frame `FIRST_VALUE` and `LAST_VALUE` windows ordered by `order_date, order_id` in the CTE `annotated`, then return one row per customer with `SELECT DISTINCT`.
- **Expected result/shape:** For sql-20 Exercise 5, return 438 rows, one per customer with orders; customer 1 shows orders 1 and 5, customer 2 shows 6 and 11, and customer 500 shows 4353 and 4362. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
- **Independent verification:** For sql-20 Exercise 5, confirm 438 rows, one per customer with orders, equal to `SELECT COUNT(DISTINCT customer_id) FROM orders`; without `DISTINCT`, the same query returns 4362 rows, one per order, with each customer's values repeated.
- **What prints:** 438 rows, matching `SELECT COUNT(DISTINCT customer_id) FROM orders`. Customer 1 shows orders 1 and 5, customer 2 orders 6 and 11, customer 12 orders 99 and 114.
- **Without `DISTINCT`:** 4,362 rows, one per order, with each customer's pair repeated.
- **Why it works:** `DISTINCT` can merge rows only because the CTE selects no per-order column. Add `o.order_id` to `annotated`'s output and pass it through, and the duplicates come back.
- **A grouped alternative:** `GROUP BY customer_id` with `MIN(order_id)` and `MAX(order_id)` gives the same pairs here only because order IDs rise with dates in this fixture; the window version follows `order_date` no matter how IDs were assigned.

## Exercise 6: Extension

**Prompt:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.

**Reasoning:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.

**Clause-by-clause reading:**

- `SELECT DISTINCT ON (o.customer_id)`: keep one row per customer, the first one under the query's `ORDER BY`.
- `ORDER BY o.customer_id, o.order_date DESC, o.order_id DESC`: must start with the `DISTINCT ON` key; the later keys put each customer's newest order first.
- The selected columns come straight from that winning row.

```sql
SELECT DISTINCT ON (o.customer_id)
  o.customer_id,
  o.order_id,
  o.order_date,
  o.total_amount
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date DESC,
  o.order_id DESC;
```

**Expected shape:** At most one latest order per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 6, keep one row per customer from the 4,362 `orders` rows with `SELECT DISTINCT ON (o.customer_id)`, where `ORDER BY o.order_date DESC, o.order_id DESC` decides which row survives.
- **Expected result/shape:** For sql-20 Exercise 6, return 438 rows, one latest order per customer with orders; customer 1 returns order 5 for 105.84, customer 2 returns order 11 for 680.50, and customer 500 returns order 4362 for 951.76. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-20 Exercise 6, confirm 438 distinct `customer_id` values, that every `order_id` equals the `last_order_id` from Exercise 5, and that the kept `total_amount` values add up to 252375.44. Inside a rolled-back transaction, set order 5's `order_date` to order 4's; customer 1 must still return order 5 because `o.order_id DESC` breaks the tie, and changing that key to `o.order_id ASC` must return order 4 for 1155.92.
- **What prints:** 438 rows. Customer 1's latest order is order 5 at 105.84, and customer 2's is order 11 at 680.50.
- **Same answer as Exercise 5's last ID:** each `order_id` here matches `last_order_id` there, a quick consistency check.
- **Compared with `ROW_NUMBER()`:** a CTE with `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC)` and an outer `WHERE rn = 1` gives the same rows. That version works in any SQL database; `DISTINCT ON` is PostgreSQL-only but shorter.
- **The tie-breaker:** no customer has two orders at the same timestamp, but `o.order_id DESC` keeps the choice fixed if that ever changes.
- **Customers without orders:** the 62 BR customers do not appear, because the query reads only `orders`.

## Final self-check

- Why does Example 1 show customer 12's last amount even though `LIMIT 100` cuts off order 114?
- In Exercise 2, why does `FIRST_VALUE(p.price)` equal the minimum, and when would it not?
- What do the two payment columns show for an order with one payment, and for order 10?
- In Exercise 4, why does the default column match the full-frame column only at 30?
- Which error appears if Exercise 6's `ORDER BY` does not start with `o.customer_id`?
