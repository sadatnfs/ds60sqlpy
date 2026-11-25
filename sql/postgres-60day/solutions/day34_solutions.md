# Day 34: Solutions: Query Optimization Techniques


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The executable file runs inside one transaction that ends in `ROLLBACK`.
Compare your rows with the counts below before you compare plans; plan
costs and timings vary by machine. General advice is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day34_solutions.sql
```

## How these answers fit together

Every answer is a pair, or a check, that keeps the result fixed while the
plan changes. The first answer swaps a subquery for joins, the second
moves a `LIMIT` ahead of a join, and the third toggles a CTE between
inlined and materialized. The fourth and fifth aggregate to order grain
before joining, so line items and payments cannot multiply each other.
The sixth replaces `NOT IN` with `NOT EXISTS` so a `NULL` cannot erase the
answer.

The first pair asks for orders with an Electronics line, and the second
for the 100 newest orders with their customer's country. The learner file
is
[day34_query_optimization.sql](../day34_query_optimization.sql).

## Exercise 1: Replace a subquery with a join

The first query uses `EXISTS`; the second uses joins. `DISTINCT` is necessary in
the join form because one order can contain multiple Electronics lines.

```sql
SET search_path TO training, public;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  o.order_id,
  o.order_date
FROM
  orders o
WHERE
  EXISTS (
    SELECT
      1
    FROM
      order_items oi
      JOIN products p ON p.product_id = oi.product_id
    WHERE
      oi.order_id = o.order_id
      AND p.category = 'Electronics');

EXPLAIN (
  ANALYZE,
  BUFFERS
) SELECT DISTINCT
  o.order_id,
  o.order_date
FROM
  orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
WHERE
  p.category = 'Electronics';
```

PostgreSQL may already transform `EXISTS` into a semi-join, so the explicit join
is not automatically faster. Compare final row counts as well as cost and time.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 1, read `orders`, `order_items`, and `products` (50 `Electronics` products) and plan two forms of 'orders with an Electronics line' with `EXPLAIN (ANALYZE, BUFFERS)`: an `EXISTS` subquery and a `SELECT DISTINCT` join through `order_items` and `products`.
- **Expected result/shape:** For sql-34 Exercise 1, expected output: both forms return 2,187 orders, one per `order_id`; the `EXISTS` plan is a `Hash Semi Join`, and the join plan is a `Hash Join` under a `HashAggregate` for the `DISTINCT`. The final columns are `order_id`, and `order_date`.
- **Independent verification:** For sql-34 Exercise 1, confirm both forms return 2,187 rows without `EXPLAIN` and that the join without `DISTINCT` also returns 2,187, because no order has two Electronics lines; then, inside `BEGIN ... ROLLBACK`, insert a second Electronics line (product 116) into order 5 and confirm the plain join grows to 2,188 rows while the `EXISTS` and `DISTINCT` forms stay at 2,187.

- **Intermediate relation check:** 2,187 order lines are Electronics, and both forms return 2,187 orders. No order in the seed has two Electronics lines, so `DISTINCT` removes nothing here. Insert a second Electronics line into one order inside a transaction to see the join form grow by one row without it.
- **Clause check:** PostgreSQL turns the `EXISTS` form into a `Hash Semi Join`, which stops at the first match per order. The join form becomes a `Hash Join` followed by a `HashAggregate` that performs the `DISTINCT`. Both read all 13,085 items and keep 50 of the 300 products.
- **Alternative/trade-off:** A third form, `WHERE o.order_id IN (SELECT oi.order_id FROM order_items oi JOIN products p ... WHERE p.category = 'Electronics')`, is planned as the same `Hash Semi Join` and returns the same 2,187 orders. Both measured forms read 165 buffers, so on this seed the `EXISTS` form saves only the `HashAggregate`, about 1.5 ms against 1.8 ms.
- **Edge case:** The category test is case-sensitive: with `p.category = 'electronics'` both forms return 0 orders and no error, so check the stored spelling before trusting an empty result.

## Exercise 2: Limit rows before enrichment

Both forms request the latest 100 orders with customer country. The second form
makes the bounded order set explicit before the dimension join.

```sql
SET search_path TO training, public;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  o.order_id,
  o.order_date,
  c.country
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
ORDER BY
  o.order_date DESC,
  o.order_id DESC
LIMIT 100;

EXPLAIN (
  ANALYZE,
  BUFFERS
) WITH top_orders AS MATERIALIZED (
  SELECT
    order_id,
    customer_id,
    order_date
  FROM
    orders
  ORDER BY
    order_date DESC,
    order_id DESC
  LIMIT 100
)
SELECT
  t.order_id,
  t.order_date,
  c.country
FROM
  top_orders t
  JOIN customers c ON c.customer_id = t.customer_id
ORDER BY
  t.order_date DESC,
  t.order_id DESC;
```

Expected shape for either actual query: 100 rows when at least 100 orders exist.
`MATERIALIZED` is used here to make the learning contrast visible; in ordinary
code, allow PostgreSQL to inline a CTE unless an optimization fence is needed.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 2, read `orders` (4,362 rows) and `customers`, and plan two forms of the latest 100 orders with country: a join followed by `ORDER BY ... LIMIT 100`, and a `top_orders` CTE `AS MATERIALIZED` that limits `orders` to 100 rows before joining `customers`.
- **Expected result/shape:** For sql-34 Exercise 2, expected output: exactly 100 rows from each form on this load, newest first, starting with order 2258 and ending with order 2269; the plain plan joins all 4,362 orders before a `top-N heapsort`, while the CTE plan joins only the 100 kept orders. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
- **Independent verification:** For sql-34 Exercise 2, confirm the plain query `EXCEPT` the CTE query returns no rows, and that the 100 rows have 100 distinct `order_id` values; then, inside `BEGIN ... ROLLBACK`, move order 2258 to `order_date = '2000-01-01'` and confirm the CTE form now starts with order 745 and ends with order 910, the former 101st row.

- **Intermediate relation check:** Both forms return the same 100 orders, newest first. The second sort key, `order_id DESC`, fixes the order of any orders placed at the same moment, so the two lists can be compared row by row.
- **Clause check:** The plain query joins all 4,362 orders to `customers` and then keeps 100 through a `top-N heapsort`, touching 80 buffers. The materialized CTE sorts `orders` alone, then looks up 100 customers through `customers_pkey` with a `Memoize` node (47 cache hits, 53 misses), touching 224 buffers.
- **Alternative/trade-off:** Limiting first is safe here only because `orders.customer_id` is `NOT NULL` with a foreign key to `customers`, so every order survives the inner join. If some orders could fail the join, the early `LIMIT` could return fewer than 100 rows while the plain query would reach further down the list.
- **Edge case:** The `ORDER BY` inside the CTE is what makes the early `LIMIT` safe. Without it, `LIMIT 100` keeps the first 100 rows in physical order, orders 1 to 100 on this load, and the outer `ORDER BY` then sorts the wrong set.

## Pitfalls

- A join can multiply rows. Never remove `EXISTS` without checking the
  relationship cardinality.
- “Filter early” is not a rule to duplicate everywhere; PostgreSQL can push
  many predicates itself.
- An early `LIMIT` is valid only when it selects the same ordered set the final
  query requires.
- Faster on one tiny seeded database is not sufficient evidence for a
  production rewrite.

## Exercise 3: Compare CTE planner boundaries

`MATERIALIZED` computes/stores the CTE as a boundary. `NOT MATERIALIZED` permits
folding into the parent query. Compare plans; neither spelling is universally
faster.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 3, run `EXPLAIN` on the same recent-orders count twice, once with `WITH recent AS MATERIALIZED (...)` and once with `AS NOT MATERIALIZED`, where `recent` keeps orders from the last 30 days and is joined to `customers`.
- **Expected result/shape:** For sql-34 Exercise 3, expected output: two plans. The `MATERIALIZED` plan computes `CTE recent` separately and reads it through a `CTE Scan on recent`; the `NOT MATERIALIZED` plan folds the date filter into a `Seq Scan on orders` under the join. Both queries return the same count.
- **Independent verification:** For sql-34 Exercise 3, run both queries without `EXPLAIN` and confirm that they return the same `count`; then confirm that only the `MATERIALIZED` plan contains a `CTE recent` node, and treat the estimated costs as plan evidence, not as a universal speed ranking.

- **Intermediate relation check:** The CTE keeps 209 orders from the last 30 days, and both versions return a count of 209.
- **Clause check:** The `MATERIALIZED` plan has a `CTE recent` subplan, a `CTE Scan on recent` and a nested loop that probes `customers_pkey` with an `Index Only Scan`. The `NOT MATERIALIZED` plan drops the CTE node and uses a `Hash Join` with the date filter on the `Seq Scan on orders`.
- **Alternative/trade-off:** The estimated totals are 163.02 for the fenced version and 162.66 for the inlined one, so the fence costs almost nothing here. It matters when the outer query has a selective filter the planner could push into the CTE, and the fence stops it.
- **Edge case:** A plain `WITH recent AS (...)` referenced once is inlined by default, so it plans like `NOT MATERIALIZED`. Reference it twice and PostgreSQL materializes it unless you say otherwise.

## Exercise 4: Pre-aggregate to order grain

`item_totals` emits one row per order before customer/country joins. This
reduces fanout while preserving the unit total.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 4, read `order_items` (13,085 lines, 39,257 units), sum `quantity` per order in the `item_totals` CTE (4,362 rows), then join `orders` and `customers` and group by `country`.
- **Expected result/shape:** For sql-34 Exercise 4, expected output: exactly 7 country rows, from IN with 5,479 units to FR with 5,711, with AU 5,529, CA 5,683, DE 5,687, GB 5,558, and US 5,610; BR is absent because its customers have no orders. The final columns are `country`, and `units`. The final order is `c.country`.
- **Independent verification:** For sql-34 Exercise 4, confirm the seven `units` add up to 39,257, the result of `SELECT SUM(quantity) FROM order_items`, and that summing `oi.quantity` straight through the three-way join gives the same seven rows; then, inside `BEGIN ... ROLLBACK`, insert a 3-unit line into order 1 (a US customer) and confirm only US changes, from 5,610 to 5,613.

- **Intermediate relation check:** `item_totals` has 4,362 rows, one per order; no order lacks items. The final result has seven countries, from IN with 5,479 units to FR with 5,711, and the seven totals add up to all 39,257 units in `order_items`.
- **Clause check:** The CTE groups 13,085 item rows to order grain before any join, so the joins to `orders` and `customers` handle 4,362 rows. The outer `GROUP BY c.country` then sums the per-order totals.
- **Alternative/trade-off:** Summing `oi.quantity` straight through the three-way join gives the same seven totals; an `EXCEPT` between the two queries returns no rows. Pre-aggregating pays off when a later join would multiply line items, as in the next answer.
- **Edge case:** Brazil does not appear because its customers have no orders. If the report must list it with 0 units, start from `customers` with `LEFT JOIN`s and `COALESCE`.

## Exercise 5: Repair two-many-side fanout

Payments and items are independently many-to-one with orders. Each is grouped
by `order_id` before their results are joined, so amounts are never multiplied.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 5, read `payments` (3,836 rows) into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep the first 20 orders.
- **Expected result/shape:** For sql-34 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have no payment and show `NULL` `paid_amount`, order 10 shows its two payments as 143.43, and order 17 shows 172.16 paid against 344.3105 of line revenue. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
- **Independent verification:** For sql-34 Exercise 5, confirm order 4 shows 1155.92 paid and 1155.9185 of revenue, while joining `payments` and `order_items` directly to `orders` inflates its `paid_amount` five times, to 5,779.60, because it has five item lines; then, inside `BEGIN ... ROLLBACK`, insert a second 240.20 payment for order 1 and confirm its `paid_amount` doubles to 480.40 while `line_revenue` stays 240.2000.

- **Intermediate relation check:** 3,489 orders have payments: 3,142 have one and 347 have two. 873 orders, all with status `placed`, have none, so 4 of the first 20 orders (5, 9, 14 and 20) show an empty `paid_amount`.
- **Clause check:** `paid` and `sold` each return one row per `order_id`, so the `LEFT JOIN`s to `orders` cannot multiply anything. Order 10 shows both payments summed, 71.72 plus 71.71, as 143.43.
- **Alternative/trade-off:** Joining `payments` and `order_items` directly to `orders` inflates both sums. Order 4 has five items and one payment, so its naive `paid_amount` is 5,779.60, five times the real 1,155.92. Order 10 has one item and two payments, so its naive revenue doubles to 286.86.
- **Edge case:** Correct sums can still disagree. Order 17 has 344.31 of line revenue but one payment of 172.16; across the seed, 199 paid orders differ from their line revenue by a cent or more.

## Exercise 6: Write a NULL-safe anti-join

`NOT EXISTS` asks whether a matching order exists for the current customer.
Unlike nullable `NOT IN`, one NULL produced by the inner relation cannot turn
every comparison into UNKNOWN.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 6, read `customers` (500 rows) and test each `customer_id` against `orders` (438 distinct customers) with a correlated `NOT EXISTS`.
- **Expected result/shape:** For sql-34 Exercise 6, expected output: exactly 62 rows, customers 8, 16, 24, and every eighth id up to 496, all of them in `BR`. The final columns are `customer_id`. The final order is `c.customer_id`.
- **Independent verification:** For sql-34 Exercise 6, confirm 500 customers minus 438 distinct ordering customers equals the 62 returned rows; then append a `NULL` to the inner list with `UNION ALL SELECT NULL` and confirm `customer_id NOT IN (...)` now returns 0 rows while `NOT EXISTS` over the same list still returns 62.

- **Intermediate relation check:** 62 customers have no orders, ids 8, 16, 24 and every eighth id up to 496: the Brazilian customers.
- **Clause check:** The plan is a `Hash Anti Join` of `customers` against `orders`, estimated at 62 rows. The `NOT IN` version gives the same 62 today, but through a hashed `SubPlan` filter with a rough estimate of 250.
- **Alternative/trade-off:** `NOT IN` is correct only while the subquery cannot return `NULL`. Appending one `NULL` to the list of order customer ids makes `NOT IN` return 0 customers, while `NOT EXISTS` still returns 62.
- **Edge case:** `orders.customer_id` is declared `NOT NULL`, so the seed is safe. A nullable column in the subquery, or a future schema change, would break `NOT IN` without any error.

## Final self-check

1. Why does the join form of the first answer need `DISTINCT` even though
   removing it changes nothing on this seed?
2. What constraint makes it safe to apply `LIMIT 100` before joining
   orders to customers?
3. How do the plans for `AS MATERIALIZED` and `AS NOT MATERIALIZED` differ
   for the 30-day count?
4. Why does order 4's `paid_amount` come out five times too large when
   payments and items are joined directly?
