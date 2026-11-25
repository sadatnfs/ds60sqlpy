# Day 03 solutions: INNER JOINs: Relational Linking and Predicate Placement

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each answer below begins with the table whose rows already have the grain the exercise asks for, then joins only tables that add one matching row each, apart from Exercise 4, which totals two detail tables before joining them. Make your own attempt first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day03_solutions.sql
```

The six results print in order: 4,362 orders, 13,085 order lines, 3,836 payments, 4,362 reconciled orders, one row of counts (4,362 and 4,362) and 7 countries. Everything runs inside `BEGIN`/`ROLLBACK`, and the snippets omit the opening `SET search_path` line. Exercise numbers match [the learner file](../day03_inner_joins.sql); for a way to compare your attempt against these answers, see the study guide's [solution-reading advice](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
- **Assumptions:** Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
- **Primary pitfall:** A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
- **Safety:** read-only from start to finish; the six statements are all `SELECT` queries, wrapped in `BEGIN`/`ROLLBACK` like every lesson file.

## Exercise 1: Query writing

**Prompt:** List orders with customer names and countries.

**Reasoning:** Join the order foreign key to the customer primary key and qualify every selected column.

**Clause-by-clause reading:**

- `FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id`: each order finds its one customer through the foreign key, so the row count stays at the order count.
- `SELECT o.order_id, o.order_date, o.total_amount, c.customer_id, c.full_name, c.country`: three columns from each side, each one prefixed with its table alias.
- `ORDER BY o.order_date DESC, o.order_id DESC`: newest first; the ID settles any timestamp tie.

```sql
SELECT
  o.order_id,
  o.order_date,
  o.total_amount,
  c.customer_id,
  c.full_name,
  c.country
FROM
  orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id
ORDER BY
  o.order_date DESC,
  o.order_id DESC;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 1, join the 4,362 `orders` rows to `customers` on the `customer_id` foreign key, which references the `customers` primary key, so each order finds exactly one customer. Return `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`.
- **Expected result/shape:** For sql-03 Exercise 1, return 4,362 rows, one per order, newest first; order 2258 for customer 258 (`CA`) leads. The 62 customers with no orders, all of them in `BR`, do not appear. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-03 Exercise 1, confirm 4,362 rows and 4,362 distinct `order_id` values, matching `SELECT COUNT(*) FROM orders`, so the inner join neither lost nor repeated an order. Count `country = 'BR'` in the output: it must be 0, because all 62 `BR` customers have no orders.
- **What prints:** 4,362 rows, one per order. In our check the first is order 2258 (742.14, Customer 258, CA) and the second is order 745 (54.04, Customer 86, IN).
- **Nothing lost, one group absent:** `orders.customer_id` is `NOT NULL` and every value points at a real customer, so all 4,362 orders survive the inner join. The 62 Brazilian customers never appear, because none of them placed an order.
- **Count to compare:** `SELECT COUNT(*) FROM orders` also returns 4,362; a larger number would mean a customer matched twice, a smaller one that some orders lost their customer.
- **Why every column has a prefix:** `orders` and `customers` both own a `customer_id` column. Write a bare `customer_id` in the `SELECT` list and PostgreSQL stops with `column reference "customer_id" is ambiguous`.

## Exercise 2: Query writing

**Prompt:** Calculate each order item's net line revenue with the product name and category.

**Reasoning:** Remain at one row per order item; do not aggregate until the desired grain changes.

**Clause-by-clause reading:**

- `FROM order_items AS oi JOIN products AS p ON p.product_id = oi.product_id`: each line picks up its one product, so the line count does not change.
- `ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2) AS line_revenue`: what the customer paid for this line after its discount, rounded to cents.
- `ORDER BY oi.order_id, oi.order_item_id`: lines grouped by order, in the order they were entered.

```sql
SELECT
  oi.order_item_id,
  oi.order_id,
  p.product_id,
  p.name,
  p.category,
  oi.quantity,
  ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2) AS line_revenue
FROM
  order_items AS oi
  JOIN products AS p ON p.product_id = oi.product_id
ORDER BY
  oi.order_id,
  oi.order_item_id;
```

**Expected shape:** One row per order item.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; the items use 275 of the 300 products and every item finds its product. Return `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`.
- **Expected result/shape:** For sql-03 Exercise 2, return 13,085 rows, one per order item, starting with item 1 (order 1, product 48, `Books`, quantity 3, `line_revenue` 83.28). The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
- **Independent verification:** For sql-03 Exercise 2, confirm 13,085 rows and 13,085 distinct `order_item_id` values, and that the `line_revenue` column sums to 2355648.13, 1.01 above the unrounded 2355647.12 because each line is rounded before the sum. Item 1 has `unit_price` 27.76, `quantity` 3, and `discount` 0.00, so 27.76 * 3 must equal its 83.28.
- **What prints:** 13,085 rows. The first is item 1 of order 1: Product 48 (Books), 3 units at 27.76 with no discount, so `line_revenue` is 83.28. Item 2 is Product 79 (Apparel), 4 at 39.23, giving 156.92.
- **Discounts:** 3,568 lines carry a discount between 0.01 and 0.15; the rest have 0.00, where `line_revenue` is just price times quantity.
- **Rounding check:** summing the unrounded line values gives 2,355,647.12, while summing the rounded `line_revenue` column gives 2,355,648.13. Round once at the level you report, not line by line before adding.
- **Why `products` is safe to join:** `product_id` is the products table's primary key, so each line matches exactly one product. Unsold products 276 to 300 have no lines and do not appear.
- **Lines per category:** Apparel 2,192, Beauty 2,189, Electronics 2,187, Home 2,186, Sports 2,186 and Books 2,145. Counting `category` in your result should give those numbers.

## Exercise 3: Query writing

**Prompt:** List payments with order status and customer name.

**Reasoning:** Follow payments → orders → customers using each declared foreign key.

**Clause-by-clause reading:**

- `FROM payments AS p`: start from payments, because the grain is one row per payment.
- `JOIN orders AS o ON o.order_id = p.order_id`: each payment belongs to one order, which supplies `status`.
- `JOIN customers AS c ON c.customer_id = o.customer_id`: the order leads on to its customer's name; payments hold no customer column.
- `ORDER BY p.payment_date DESC, p.payment_id DESC`: newest payment first.

```sql
SELECT
  p.payment_id,
  p.payment_date,
  p.amount,
  p.method,
  o.order_id,
  o.status,
  c.full_name
FROM
  payments AS p
  JOIN orders AS o ON o.order_id = p.order_id
  JOIN customers AS c ON c.customer_id = o.customer_id
ORDER BY
  p.payment_date DESC,
  p.payment_id DESC;
```

**Expected shape:** One row per payment.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 3, join the 3,836 `payments` rows to `orders` and then to `customers`; the payments cover 3,489 orders, 347 of which have two payments. Return `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`.
- **Expected result/shape:** For sql-03 Exercise 3, return 3,836 rows, one per payment, newest first; payment 654 (order 745, `paypal`, 54.04) leads. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
- **Independent verification:** For sql-03 Exercise 3, confirm 3,836 rows and 3,836 distinct `payment_id` values, matching `SELECT COUNT(*) FROM payments`, and that `COUNT(DISTINCT order_id)` in the output is 3,489. Order 10 must appear twice, once per payment, which is the expected grain here rather than fan-out.
- **What prints:** 3,836 rows, one per payment. In our check the newest is payment 654, 54.04 by PayPal for order 745 (shipped, Customer 86).
- **Status mix:** shipped 961, paid 960, returned 958 and delivered 957. No row says `placed`, because none of the 873 placed orders has a payment yet.
- **Two payments, one order:** 347 orders were paid in two parts, so they appear twice. Order 10 is one of them: payments 8 and 9 for 71.72 and 71.71. That duplication is correct at payment grain.
- **Methods:** credit 1,050, PayPal 1,040, bank 886 and card 860, which add up to 3,836.
- **Why start from `payments`:** `FROM orders LEFT JOIN payments` would add the 873 unpaid placed orders as rows with empty payment columns, 4,709 in all. Those rows are orders, not payments, so they do not belong in this list.

## Exercise 4: Prediction

**Prompt:** Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.

**Reasoning:** Aggregate items and payments separately to one row per order before joining those aggregates.

**Clause-by-clause reading:**

- `item_totals`: one row per order with `SUM(oi.unit_price * oi.quantity * (1 - oi.discount))`, built from `order_items` alone.
- `payment_totals`: one row per paid order with `SUM(p.amount)`, built from `payments` alone.
- `FROM orders AS o JOIN item_totals AS it ON it.order_id = o.order_id`: every order has at least one line, so the inner join keeps all 4,362.
- `LEFT JOIN payment_totals AS pt ON pt.order_id = o.order_id`: keeps orders with no payment, which get a `NULL` total.
- `ROUND(COALESCE(pt.paid_total, 0), 2)`: for an order with no payments, "paid nothing" really is 0, so the `NULL` becomes 0.00.
- `ORDER BY o.order_id`: one line per order in ID order.

```sql
WITH item_totals AS (
  SELECT
    oi.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS item_total
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
  ROUND(it.item_total, 2) AS item_total,
  ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total
FROM
  orders AS o
  JOIN item_totals AS it ON it.order_id = o.order_id
  LEFT JOIN payment_totals AS pt ON pt.order_id = o.order_id
ORDER BY
  o.order_id;
```

**Expected shape:** One row per order; no six-row multiplication.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 4, aggregate the 13,085 `order_items` rows and the 3,836 `payments` rows to one row per `order_id` each, then join both to `orders`; 873 orders have no payment and 347 have two.
- **Expected result/shape:** For sql-03 Exercise 4, return 4,362 rows, one per order, with `paid_total` 0.00 for the 873 unpaid orders and no doubled item totals for the 347 two-payment orders. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
- **Independent verification:** For sql-03 Exercise 4, confirm 4,362 distinct `order_id` values; 3,290 orders show equal totals, 199 differ, and 873 show `paid_total` 0.00. Order 10 has one item and two payments: its `item_total` must be 143.43, while joining raw `order_items` to raw `payments` before summing reports 286.86.
- **The prediction:** three lines times two payments gives 3 x 2 = 6 joined rows, so the item total would be counted twice and the paid total three times. No order in this fixture has that exact shape: all 347 two-payment orders hold a single line.
- **The real case, order 10:** one line worth 143.43 and two payments of 71.72 and 71.71. Joined directly it yields 2 rows and an item total of 286.86; the per-order totals show 143.43 against 143.43.
- **Across the whole table:** a direct join of orders, items and payments gives 10,816 rows and sums payments to 6,707,306.05, while the real payment total is 1,831,900.81.
- **What prints instead:** 4,362 rows. 3,290 orders balance exactly, 873 placed orders show 0.00 paid (order 5: 105.84 against 0.00), and 199 are paid for less than their lines, such as order 17 at 344.31 with one payment of 172.16. No order is overpaid.

## Exercise 5: Debugging

**Prompt:** Repair a customer/order join whose `ON` clause compares unrelated IDs.

**Reasoning:** Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.

**Clause-by-clause reading:**

- `FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id`: the repaired predicate; the foreign key in `orders` meets the primary key it refers to.
- `COUNT(*) AS joined_rows`: how many rows the join produced.
- `COUNT(DISTINCT o.order_id) AS distinct_orders`: how many different orders those rows represent.

```sql
SELECT
  COUNT(*) AS joined_rows,
  COUNT(DISTINCT o.order_id) AS distinct_orders
FROM
  orders AS o
  JOIN customers AS c ON c.customer_id = o.customer_id;
```

**Expected shape:** Exactly one customer match per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 5, join the 4,362 `orders` rows to `customers` on `customer_id` and count the joined rows and the distinct orders; no row-level key is returned.
- **Expected result/shape:** For sql-03 Exercise 5, return exactly one row with `joined_rows` 4,362 and `distinct_orders` 4,362, which shows every order matched exactly one customer. The final columns are `joined_rows`, and `distinct_orders`.
- **Independent verification:** For sql-03 Exercise 5, confirm both values equal `SELECT COUNT(*) FROM orders`. Reverse the join into `customers LEFT JOIN orders` and the row count must become 4,424, because the 62 customers without orders each add one unmatched row.
- **What prints:** one row, 4,362 and 4,362. Equal numbers mean no order matched twice; matching `SELECT COUNT(*) FROM orders` means no order was lost.
- **What the bug printed:** with `c.customer_id = o.order_id` the same counts come out as 500 and 500. The query works, but only orders 1 to 500 find a "customer", and most of them find the wrong one: order 2 belongs to customer 1 but is paired with Customer 2.
- **A worse slip:** `ON c.customer_id = c.customer_id` compares a column with itself, so every order meets every customer: 2,181,000 joined rows over 4,362 distinct orders.

## Exercise 6: Extension

**Prompt:** Calculate net line revenue by customer country without double-counting order totals.

**Reasoning:** Start from line items, join through orders and customers, then aggregate at country grain.

**Clause-by-clause reading:**

- `FROM order_items AS oi`: start at line level, where revenue is measured.
- `JOIN orders AS o ON o.order_id = oi.order_id JOIN customers AS c ON c.customer_id = o.customer_id`: each line climbs to its one order and that order's one customer, so no line is repeated.
- `SUM(oi.unit_price * oi.quantity * (1 - oi.discount))` with `GROUP BY c.country`: adds line revenue per country, rounded to cents at the end.
- `ORDER BY net_revenue DESC, c.country`: biggest market first.

```sql
SELECT
  c.country,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM
  order_items AS oi
  JOIN orders AS o ON o.order_id = oi.order_id
  JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY
  c.country
ORDER BY
  net_revenue DESC,
  c.country;
```

**Expected shape:** One row per country represented by an order.

### Reasoning and verification

- **Inputs/evidence:** For sql-03 Exercise 6, join the 13,085 `order_items` rows to `orders` and then to `customers`, and total net revenue by `country`; `BR` customers have no orders.
- **Expected result/shape:** For sql-03 Exercise 6, return 7 rows, one per country with orders: `FR` first at 343290.13 and `IN` last at 329081.73, with no `BR` row. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
- **Independent verification:** For sql-03 Exercise 6, confirm the 7 totals sum to 2355647.12, the same as `SUM(unit_price * quantity * (1 - discount))` over all of `order_items`. Starting the join from `customers` with `LEFT JOIN` must add an eighth `BR` row whose `net_revenue` is `NULL`.
- **What prints:** 7 rows. France leads with 343,290.13, then Germany 341,622.95, Canada 338,014.28, the US 337,931.77, Great Britain 334,758.57, Australia 330,947.70 and India 329,081.73. Brazil has no orders and so no row.
- **Reconciliation:** the seven figures add up to within a cent of 2,355,647.12, the sum of all line revenue.
- **The double count, measured:** `SUM(o.total_amount)` on the same joined rows reports 1,289,140.52 for France and 8,633,041.53 overall, about 3.7 times too much, because each order total repeats once per line.
- **Order count is not revenue:** Great Britain has the most orders, 634 from 63 customers, yet ranks fifth. France reaches the top with 619 orders from 62 customers.
- **Join order does not matter here:** `FROM customers JOIN orders JOIN order_items` returns the same 13,085 joined rows and the same seven totals, since inner joins can be listed in any order. Starting at the lines simply makes the grain easy to read.

## Final self-check

- Why does Exercise 1 return exactly as many rows as `orders`, yet no Brazilian customer?
- How many rows does order 10 contribute when orders, items and payments are joined directly?
- Why did the broken Exercise 5 join stop at 500 rows instead of failing?
- Which table should a country revenue report start from, and why not `orders` with `total_amount`?
