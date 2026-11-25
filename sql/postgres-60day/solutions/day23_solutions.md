# Day 23 solutions: Common Table Expressions (CTEs) Introduction


<!-- beginner-solution-enrichment -->
## How to study and run this solution

`day23_solutions.sql` sets `search_path` to `training` and wraps everything in
`BEGIN`/`ROLLBACK`. Exercise 6 also opens `SAVEPOINT exercise_6` and rolls back
to it straight after its update, so product prices are restored even before
the outer rollback. For the general comparison routine, see
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day23_solutions.sql
```

## How these answers fit together

Each answer names its stages with `WITH`, and most change grain on the way:
order lines to orders to customers in Exercise 1, payments to orders in the
third answer, and orders to customers to countries in the fifth. Exercise 2
reads one CTE twice, and Exercise 4 compares two copies of the same filter, so
both are about how PostgreSQL plans a CTE rather than about new grains. The
last answer moves the idea to writes. When an answer of yours disagrees, count
the rows of each stage and find the first one that differs. The learner file
is [day23_ctes_intro.sql](../day23_ctes_intro.sql).

## Reading contract

- **Focus:** Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability, not forced materialization, is the default goal.
- **Assumptions:** Each CTE declares its output grain. PostgreSQL inlines a side-effect-free CTE that is referenced once unless `MATERIALIZED` is requested; a CTE referenced more than once is materialized (computed once) by default.
- **Primary pitfall:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Build order-level net value in one CTE and summarize it by customer in the outer query.

**Reasoning:** Name the one-row-per-order grain before changing to customer grain.

```sql
WITH order_values AS (
  SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id
)
SELECT
  ov.customer_id,
  COUNT(*) AS order_count,
  ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM
  order_values AS ov
GROUP BY
  ov.customer_id
ORDER BY
  net_revenue DESC,
  ov.customer_id;
```

**Expected shape:** One row per ordering customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 1, read `orders` joined to `order_items`, build the `order_values` CTE at one row per `order_id` with net value `unit_price * quantity * (1 - discount)`, then group that CTE by `customer_id`; `order_id` disappears in the outer aggregate.
- **Expected result/shape:** For sql-23 Exercise 1, expected output: 438 rows, one per ordering customer, led by customer 181 with 16 orders and 9502.22 of item-level net revenue. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
- **Independent verification:** For sql-23 Exercise 1, confirm `SUM(order_count)` is 4362 and matches `SELECT COUNT(*) FROM orders`, and that the unrounded revenue total equals `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12); then count joined rows for customer 181 without the CTE, `SELECT COUNT(*) FROM orders o JOIN order_items oi USING (order_id) WHERE o.customer_id = 181`, and see 50 item rows instead of 16 orders, which is the fanout the order-grain CTE prevents.
- **Intermediate relation check:** `order_values` returns 4,362 rows with 4,362 distinct `order_id` values; every order has at least one of the 13,085 item rows, so the inner join loses nothing. The final query returns 438 customers.
- **Clause check:** The CTE groups by `order_id` and `customer_id`, so `COUNT(*)` in the outer query counts orders, not items. Customer 181 has 16 orders and 9,502.22 net revenue; the bottom of the list is customer 364 with 4 orders and 962.26.
- **Alternative/trade-off:** `COUNT(DISTINCT o.order_id)` and `SUM(...)` grouped by customer straight over the join give the same answer in one level. The CTE version is longer but lets you check the order grain before the customer grain is built.
- **Edge case:** Summing `orders.total_amount` instead of the item formula gives 9,502.21 for customer 181, a cent lower, because each stored total is rounded to two decimals per order. Decide which source defines revenue before comparing answers.

## Exercise 2: Query writing

**Prompt:** Use one category-revenue CTE twice to return the highest category and total revenue.

**Reasoning:** A named aggregate can support multiple scalar reads without repeating the business formula.

```sql
WITH category_revenue AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items AS oi
    JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY
    p.category
)
SELECT
  (
    SELECT
      cr.category
    FROM
      category_revenue AS cr
    ORDER BY
      cr.revenue DESC,
      cr.category
    LIMIT 1) AS top_category,
  ROUND((
    SELECT
      SUM(cr.revenue)
    FROM category_revenue AS cr), 2) AS all_revenue;
```

**Expected shape:** One summary row.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 2, read `order_items` joined to `products`, aggregate net item revenue by `category` once in `category_revenue`, and read that CTE twice: once in a scalar subquery ordered by revenue then category with `LIMIT 1`, and once in a scalar `SUM`; there is no outer `FROM` or `GROUP BY`.
- **Expected result/shape:** For sql-23 Exercise 2, expected output: exactly one row, `top_category` `Sports` and `all_revenue` 2355647.12. The final columns are `top_category`, and `all_revenue`.
- **Independent verification:** For sql-23 Exercise 2, run the CTE body alone and confirm six category rows led by Sports at 397427.70 ahead of Electronics at 394424.39, and that they add to the same 2355647.12 as `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items`; then add `WHERE false` inside `category_revenue` and confirm the query still returns one row, now with both values NULL, because scalar subqueries over an empty CTE yield NULL rather than no row.
- **Intermediate relation check:** `category_revenue` has 6 rows, one per category, ranging from Books at 386,192.77 to Sports at 397,427.70. The final result is one row: `Sports` and 2,355,647.12.
- **Clause check:** The two scalar subqueries each read `category_revenue`; one sorts by revenue with `cr.category` as the tie breaker and keeps 1 row, the other sums all six. Because the CTE is referenced twice, `EXPLAIN` shows one `CTE category_revenue` step and two `CTE Scan` nodes, so the join and grouping run once.
- **Alternative/trade-off:** `SELECT category, SUM(revenue) OVER () ... ORDER BY revenue DESC LIMIT 1` over the CTE returns the same pair from one read. The scalar-subquery form keeps the two questions separate and is easier to extend with a third measure.
- **Edge case:** `all_revenue` is 2,355,647.12, while `SUM(orders.total_amount)` is 2,355,646.89. The 0.23 gap comes from per-order rounding in the stored totals, not from a lost row.

## Exercise 3: Query writing

**Prompt:** Create staged payment reconciliation CTEs at order grain.

**Reasoning:** Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.

```sql
WITH paid AS (
  SELECT
    p.order_id,
    SUM(p.amount) AS paid_amount
  FROM
    payments AS p
  GROUP BY
    p.order_id
),
reconciled AS (
  SELECT
    o.order_id,
    o.total_amount,
    COALESCE(paid.paid_amount, 0) AS paid_amount
  FROM
    orders AS o
    LEFT JOIN paid ON paid.order_id = o.order_id
)
SELECT
  order_id,
  ROUND(total_amount, 2) AS order_total,
  ROUND(paid_amount, 2) AS paid_amount,
  ROUND(total_amount - paid_amount, 2) AS unpaid_balance
FROM
  reconciled
ORDER BY
  ABS(total_amount - paid_amount) DESC,
  order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 3, read `payments` (3836 rows for 3489 orders) and pre-aggregate them to one `paid_amount` per `order_id` in `paid`, then `LEFT JOIN` that CTE to all 4362 `orders` in `reconciled` and turn a missing payment into 0 with `COALESCE`.
- **Expected result/shape:** For sql-23 Exercise 3, expected output: 4362 rows, one per order; 873 orders have no payment, 199 more are partly paid, none is overpaid, and the first rows are orders 2029, 3129, and 3679 each with 1432.49 unpaid. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
- **Independent verification:** For sql-23 Exercise 3, confirm the row count equals `SELECT COUNT(*) FROM orders` (4362), that `SUM(paid_amount)` equals `SELECT SUM(amount) FROM payments` (1831900.81), and that the 873 zero-paid rows are exactly the `placed` orders; then join `payments` to `orders` without the `paid` CTE and see 4709 rows, because 347 orders have more than one payment.
- **Intermediate relation check:** `payments` has 3,836 rows for 3,489 orders (347 orders have two payments), so `paid` has 3,489 rows. `reconciled` keeps all 4,362 orders: 3,290 paid in full, 199 underpaid, 873 with no payment and none overpaid.
- **Clause check:** `LEFT JOIN paid` keeps the 873 unpaid orders, and `COALESCE(paid.paid_amount, 0)` turns their missing payment into 0 so the subtraction is not `NULL`. Sorting by `ABS(total_amount - paid_amount)` puts the largest gaps first: orders 2029, 3129 and 3679 each owe 1,432.49 and appear in `order_id` order.
- **Alternative/trade-off:** A correlated subquery, `COALESCE((SELECT SUM(amount) FROM payments p WHERE p.order_id = o.order_id), 0)`, gives the same 4,362 rows without a separate CTE. The staged version shows the payment grain explicitly, which is the point of the exercise.
- **Edge case:** Every unpaid order has status `placed`, and the balances total 523,746.08. Joining `payments` before summing would count each two-payment order's total twice and push the order total for those orders up by the same amount.

## Exercise 4: Prediction

**Prompt:** Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.

**Reasoning:** Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.

```sql
WITH materialized_orders AS MATERIALIZED (
  SELECT
    o.order_id
  FROM
    orders AS o
  WHERE
    o.status = 'delivered'
),
inline_orders AS NOT MATERIALIZED (
  SELECT
    o.order_id
  FROM
    orders AS o
  WHERE
    o.status = 'delivered'
)
SELECT
  'materialized' AS variant,
  COUNT(*) AS row_count
FROM
  materialized_orders
UNION ALL
SELECT
  'not_materialized' AS variant,
  COUNT(*) AS row_count
FROM
  inline_orders
ORDER BY
  variant;
```

**Expected shape:** Two count rows with equal values.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 4, read from `orders` through two side-effect-free CTEs that both keep `delivered` orders, one declared `AS MATERIALIZED` and one `AS NOT MATERIALIZED`, and count the rows each returns.
- **Expected result/shape:** For sql-23 Exercise 4, expected output: two rows, `materialized` and `not_materialized`, each with `row_count` 872. The final columns are `variant`, and `row_count`. The final order is `variant`.
- **Independent verification:** For sql-23 Exercise 4, confirm both `row_count` values are 872, equal to `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`; then run `EXPLAIN` on the query: the `MATERIALIZED` CTE appears as a separate `CTE materialized_orders` step read through a `CTE Scan`, while the `NOT MATERIALIZED` CTE is folded into a `Seq Scan on orders` with the status filter.
- **Intermediate relation check:** Both CTEs select the 872 `delivered` orders, so the result is two rows, `materialized` and `not_materialized`, each with `row_count` 872. The five statuses hold 872 or 873 orders each.
- **Clause check:** `UNION ALL` stacks the two counts and the final `ORDER BY variant` sorts them alphabetically. Under `EXPLAIN (COSTS OFF)` the first branch reads `CTE Scan on materialized_orders` fed by a separate `CTE materialized_orders` step, while the second branch is just `Seq Scan on orders` with `Filter: (status = 'delivered'::text)`.
- **Alternative/trade-off:** Leaving out both keywords gives the inlined plan for each CTE, because each is referenced once. The keywords are worth writing only when a measured plan shows a benefit, for example to stop a heavy CTE from being recomputed when `NOT MATERIALIZED` was forced elsewhere.
- **Edge case:** On a 4,362-row table the two variants are indistinguishable in timing. That is why the exercise asks for equal counts and a plan comparison, not for a claim about speed.

## Exercise 5: Debugging

**Prompt:** Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.

**Reasoning:** Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.

```sql
WITH order_values AS (
  SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id
),
customer_revenue AS (
  SELECT
    ov.customer_id,
    SUM(ov.order_value) AS customer_revenue
  FROM
    order_values AS ov
  GROUP BY
    ov.customer_id
)
SELECT
  c.country,
  ROUND(SUM(cr.customer_revenue), 2) AS country_revenue
FROM
  customer_revenue AS cr
  JOIN customers AS c ON c.customer_id = cr.customer_id
GROUP BY
  c.country
ORDER BY
  country_revenue DESC,
  c.country;
```

**Expected shape:** One row per country.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 5, read `orders` and `order_items` into the order-grain CTE `order_values`, roll it up to one `customer_revenue` per customer, and only then join `customers` and group by `country`, giving each stage its own alias instead of a reused `total`.
- **Expected result/shape:** For sql-23 Exercise 5, expected output: 7 rows, one per country with orders, from FR at 343290.13 down to IN at 329081.73; BR's 62 customers place no orders, so BR is absent. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
- **Independent verification:** For sql-23 Exercise 5, confirm the seven values add to the item-level total `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12) within one cent of rounding, and that `SELECT country, COUNT(*) FROM customers GROUP BY country` lists eight countries; change the final join to `customers LEFT JOIN customer_revenue` and BR appears with a NULL revenue, which shows why the inner join drops it.
- **Intermediate relation check:** `order_values` has 4,362 rows and `customer_revenue` has 438. The join to `customers` keeps all 438, and grouping by country returns 7 rows, not 8.
- **Clause check:** The broken version this exercise repairs carries one name, `total`, through every stage; as soon as two stages that both expose `total` meet in one `FROM`, PostgreSQL raises `column reference "total" is ambiguous`. Here each stage names its measure for its grain, so the final `SUM(cr.customer_revenue)` cannot be confused with an order-level value. FR leads with 343,290.13 from 62 customers, DE follows at 341,622.95 from 63, and IN is last at 329,081.73.
- **Alternative/trade-off:** Joining `customers` inside `order_values` and grouping by country there skips the customer stage. It returns the same 7 totals, but you lose the 438-row checkpoint that confirms no customer was double-counted.
- **Edge case:** Brazil is missing because none of its 62 customers has an order. To show it with 0 revenue, start from `customers` and `LEFT JOIN customer_revenue`, then wrap the sum in `COALESCE`.

## Exercise 6: Extension

**Prompt:** Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.

**Reasoning:** The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.

```sql
SAVEPOINT exercise_6;

WITH candidates AS (
  SELECT
    p.product_id
  FROM
    products AS p
  ORDER BY
    p.product_id
  LIMIT 3
),
updated AS (
  UPDATE
    products AS p
  SET
    price = ROUND(p.price * 1.01, 2)
  WHERE
    p.product_id IN (
      SELECT
        c.product_id
      FROM
        candidates AS c)
    RETURNING
      p.product_id,
      p.price
)
SELECT
  COUNT(*) AS updated_rows,
  MIN(product_id) AS first_updated_product,
  MAX(product_id) AS last_updated_product
FROM
  updated;

ROLLBACK TO SAVEPOINT exercise_6;
```

**Expected shape:** One summary row for a bounded three-product update.

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 6, read `products` in the `candidates` CTE to pick the three lowest `product_id` values (1, 2, 3, priced 10.37, 10.74, and 11.11), update only those rows in the data-modifying CTE `updated`, and read its `RETURNING` rows; `SAVEPOINT exercise_6` and `ROLLBACK TO SAVEPOINT` undo the change.
- **Expected result/shape:** For sql-23 Exercise 6, expected output: one summary row with `updated_rows` 3, `first_updated_product` 1, and `last_updated_product` 3. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
- **Independent verification:** For sql-23 Exercise 6, add `string_agg(price::text, ',' ORDER BY product_id)` to the outer query and confirm the returned new prices are 10.47, 10.85, and 11.22; after `ROLLBACK TO SAVEPOINT exercise_6`, `SELECT product_id, price FROM products WHERE product_id <= 3` must show 10.37, 10.74, and 11.11 again. With `LIMIT 0` in `candidates` the summary row still appears, with 0 updated rows and NULL first and last products.
- **Intermediate relation check:** `candidates` returns product ids 1, 2 and 3, priced 10.37, 10.74 and 11.11. `updated` returns the same three ids with the new prices 10.47, 10.85 and 11.22.
- **Clause check:** The outer `SELECT` aggregates the `RETURNING` relation, so it reports `updated_rows` 3, `first_updated_product` 1 and `last_updated_product` 3. `ROLLBACK TO SAVEPOINT exercise_6` then restores the three prices while keeping the outer transaction open.
- **Alternative/trade-off:** A plain `UPDATE ... RETURNING` prints the three changed rows instead of a summary. Wrapping it in a CTE lets you count or join the changed rows in the same statement.
- **Edge case:** A subquery on `products` in that same statement still sees 10.37 for product 1, because every part of the statement shares the pre-update snapshot. If `candidates` returned no rows, the update would touch nothing and the summary would show `updated_rows` 0 with `NULL` first and last ids.

## Final self-check

- What is the grain and row count of every CTE you wrote, and which stage
  changed the grain?
- Which of your CTEs were inlined and which were computed separately, and
  what in `EXPLAIN` told you?
- Why must payments be summed per order before they meet `orders`?
- What does the rest of a statement see after a data-modifying CTE updates a
  row?
