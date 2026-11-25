# Day 56 Solutions: CUBE and Percentiles


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day56_solutions.sql
```

The file only reads; every query runs against the course tables and returns
quickly. Expect one count row, 276 percentile rows, one fan-out row, 5 method
rows and two 6-row category summaries. The
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
The recurring move in this file is to shrink a table to order grain before it
meets another table: payments to one method per order, lines to one value per
order or per order and category. Only then are cubes and percentiles taken.

The exercises add payment method to a multidimensional cube and calculate
category-attributable order-value percentiles by month. See
[`day56_solutions.sql`](day56_solutions.sql).

## Exercise 1: Add payment method and measure cube growth

An order can have more than one payment. The answer defines its primary method
as the method with the greatest total paid amount, breaking ties by method name.
Reducing to one method prevents order lines from being duplicated; unpaid
orders remain visible.

```sql
SET search_path TO training, public;

WITH payment_by_method AS (
  SELECT
    order_id,
    method,
    SUM(amount) AS paid_amount
  FROM
    payments
  GROUP BY
    order_id,
    method
),
ranked_payment AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY paid_amount DESC,
      method) AS payment_rank
  FROM
    payment_by_method
),
primary_payment AS (
  SELECT
    order_id,
    method
  FROM
    ranked_payment
  WHERE
    payment_rank = 1
),
line AS (
  SELECT
    c.country,
    p.category,
    COALESCE(pp.method, 'unpaid') AS payment_method,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM
    orders o
    JOIN customers c USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
    LEFT JOIN primary_payment pp USING (order_id)
),
cube_two AS (
  SELECT
    country,
    category,
    SUM(revenue) AS revenue
  FROM
    line
  GROUP BY
    CUBE (country,
      category)
),
cube_three AS (
  SELECT
    country,
    category,
    payment_method,
    SUM(revenue) AS revenue
  FROM
    line
  GROUP BY
    CUBE (country,
      category,
      payment_method))
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      cube_two) AS two_dimension_rows,
  (
    SELECT
      COUNT(*)
    FROM
      cube_three) AS three_dimension_rows;
```

Expected shape: one row; `three_dimension_rows` should be larger.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 1, build `line` with one row per order item (13,085 rows) carrying `country`, `category`, and `payment_method`, where `payment_method` is the method with the largest paid amount for the order (ties broken by method name, `unpaid` when the order has no payment), then count the rows of `CUBE (country, category)` and of `CUBE (country, category, payment_method)`.
- **Expected result/shape:** For sql-56 Exercise 1, expected output: one row with `two_dimension_rows` 56 and `three_dimension_rows` 336. The 7 ordering countries plus a subtotal times the 6 categories plus a subtotal gives 56, and the 5 payment values (`bank`, `card`, `credit`, `paypal`, `unpaid`) plus a subtotal multiply that by 6. The final columns are `two_dimension_rows` and `three_dimension_rows`.
- **Independent verification:** For sql-56 Exercise 1, confirm that `line` has 13085 rows and 210 distinct `(country, category, payment_method)` tuples (7 x 6 x 5, so every combination occurs and the cube is complete), and that `primary_payment` has one row per paid order (3489). In a rolled-back transaction, run `UPDATE payments SET method = 'bank' WHERE method = 'card'`: `two_dimension_rows` stays 56 while `three_dimension_rows` falls to 280 (56 x 5).
- **Intermediate relation check:** `payment_by_method` turns 3,836 payments into one row per order and method, `primary_payment` keeps 3,489 rows (one per paid order) and `line` keeps all 13,085 lines, labeling 2,616 of them `unpaid`. `cube_two` then has 56 rows and `cube_three` 336.
- **Clause check:** `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY paid_amount DESC, method)` makes the policy deterministic: 327 of the 347 split orders pay equal amounts by both methods, so the `method` tie-breaker decides most of them. The two scalar subqueries count the cube CTEs into one row.
- **Alternative/trade-off:** `DISTINCT ON (order_id) ... ORDER BY order_id, paid_amount DESC, method` picks the same primary method in one step. It is shorter, but PostgreSQL-specific, and it hides the ranking that the `ROW_NUMBER` form lets you inspect.
- **Edge case:** Adding one payment does not add an output row, since this exercise always returns one row. Give a placed order its first payment and its lines move from `unpaid` to a method; the 336 count stays put unless a new method value appears.

## Exercise 2: Category-month p50 and p90

The metric is each category's contribution to an order, not the entire order
total repeated for every category.

```sql
SET search_path TO training, public;

WITH category_orders AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    p.category,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
  GROUP BY
    date_trunc('month', o.order_date), p.category, o.order_id
)
SELECT
  month,
  category,
  ROUND(percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value)::numeric, 2) AS p50_order_value,
  ROUND(percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value)::numeric, 2) AS p90_order_value
FROM
  category_orders
GROUP BY
  month,
  category
ORDER BY
  month DESC,
  category;
```

Expected grain: one row per represented `(month, category)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 2, sum line revenue per `(month, category, order_id)` in `category_orders`, so an order contributes one value to each category it bought from, then take `percentile_cont` at 0.50 and 0.90 of those values per `(month, category)`, rounded to 2 decimals.
- **Expected result/shape:** For sql-56 Exercise 2, expected output: 276 rows, one per `(month, category)` for 46 months (2023-02 to 2026-11) and 6 categories, starting with 2026-11 Apparel at `p50_order_value` 122.86 and `p90_order_value` 361.16. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
- **Independent verification:** For sql-56 Exercise 2, confirm 276 rows with no repeated `(month, category)` and that all six February 2023 rows show the same value for both percentiles, because each holds a single order. In a rolled-back transaction, add a January 2023 order with one 10.00 Books line: the result grows to 277 rows and the new 2023-01 Books row shows 10.00 for both percentiles.
- **Intermediate relation check:** `category_orders` groups 13,085 lines by month, category and order. No order has two lines in one category, so it also has 13,085 rows, and the outer query collapses them into 276 month and category groups.
- **Clause check:** `percentile_cont(0.50)` and `(0.90)` each return `double precision`, so the query casts to `numeric` before `ROUND(..., 2)`. The `GROUP BY` in the CTE repeats `date_trunc('month', o.order_date)` because the alias `month` is defined in the same `SELECT`.
- **Alternative/trade-off:** Computing both percentiles in one call, `percentile_cont(ARRAY[0.5, 0.9])`, sorts each group once and returns an array. It is efficient, but the two values then need unpacking into the named columns the exercise asks for.
- **Edge case:** A month and category with one order, as in all six categories of February 2023 (9 such groups in total), returns that order for both p50 and p90. Report `COUNT(*)` beside the percentiles so a reader can see when a p90 rests on one or two orders.

## Reasoning, safety, and pitfalls

- Joining all payment rows to lines would multiply revenue for split-payment
  orders. Define a payment attribution policy before adding that dimension.
- Aggregate by `(order_id, method)` before ranking so split payments using the
  same method are compared by their total paid amount.
- The method-name tie-break makes the primary-method policy deterministic.
- `percentile_cont` interpolates and returns a floating type; cast to numeric
  before two-argument `ROUND`.
- Percentiles need enough observations. Always accompany production percentiles
  with sample counts.

## Exercise 3: Measure raw fanout

The raw payment/item join reports joined rows and distinct source keys. Orders
with several rows on both sides demonstrate the multiplication risk.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 3, join `orders` to `order_items` and to `payments` on `order_id` without pre-aggregation and count the joined rows, the distinct `order_item_id` values, and the distinct `payment_id` values.
- **Expected result/shape:** For sql-56 Exercise 3, expected output: one row with `raw_join_rows` 10816, `distinct_items` 10469, and `distinct_payments` 3836; an order with two payments repeats each of its items, so the joined rows exceed the distinct items. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
- **Independent verification:** For sql-56 Exercise 3, confirm that `raw_join_rows` equals `SELECT SUM(i.n * p.n) FROM (SELECT order_id, COUNT(*) n FROM order_items GROUP BY order_id) i JOIN (SELECT order_id, COUNT(*) n FROM payments GROUP BY order_id) p USING (order_id)` (10816); summing item revenue over this join would count every line once per payment of its order.
- **Intermediate relation check:** Per order, `order_items` contributes its line count and `payments` its payment count, and the inner join multiplies them. 3,142 orders pay once, giving one row per line; the 347 split orders have one line and two payments each.
- **Clause check:** `COUNT(*)` counts joined rows, while `COUNT(DISTINCT oi.order_item_id)` and `COUNT(DISTINCT p.payment_id)` count source keys. Their difference, 347, is exactly the duplicated revenue rows that a `SUM` over this join would add.
- **Alternative/trade-off:** Counting in two subqueries, lines per order and payments per order, and summing their products, as the Verify step does, predicts the fan-out before any wide join runs. It scales better on large tables.
- **Edge case:** Orders without payments disappear from this inner join, so `distinct_items` (10,469) is 2,616 below the 13,085 lines. A fan-out check therefore has to watch for lost rows as well as duplicated ones.

## Exercise 4: Attribute at order grain

Payment policy reduces methods to one order-level label; line revenue also
reduces to one order row. The windowed grand total reconciles attribution.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 4, reduce `payments` to one `reporting_method` per order with `MIN(method)`, an alphabetical rule that differs from the largest-amount rule of Exercise 1, reduce `order_items` to one revenue total per order, left-join them at order grain with `unpaid` for orders without payments, and sum revenue per reporting method.
- **Expected result/shape:** For sql-56 Exercise 4, expected output: 5 rows, one per `reporting_method` (`bank`, `card`, `credit`, `paypal`, and `unpaid`), whose `revenue` values add up to `reconciled_total` (2355647.1235), the exact line revenue repeated on every row. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
- **Independent verification:** For sql-56 Exercise 4, confirm that the five `revenue` values add up to `SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items` (2355647.1235) and that `method` has one row per paid order (3489), so no order's revenue is counted twice.
- **Intermediate relation check:** `method` has 3,489 rows and `lines` has 4,362, each one row per order. The left join keeps all 4,362 orders, 873 of them without a method, and `attributed` folds them into 5 method rows.
- **Clause check:** `COALESCE(m.reporting_method, 'unpaid')` appears in both the `SELECT` and the `GROUP BY`, so unpaid orders form a group instead of a `NULL` row. `SUM(revenue) OVER ()` puts 2,355,647.1235 on every row, which lets a reader check the split without another query.
- **Alternative/trade-off:** Splitting each order's revenue by the share each method paid avoids choosing a label at all. It is fairer to mixed orders, but it needs payment amounts that add up to the order value and makes every method's revenue fractional.
- **Edge case:** `MIN(method)` picks one method for an order paid two ways, which is a reporting rule, not a fact. On this fixture it agrees with Exercise 1's largest-amount rule for all 347 split orders (327 tie on amount and 20 already paid more with the alphabetically first method), so both give the same totals. To see the rules diverge, raise order 30's `credit` payment to 108.43 in a rolled-back transaction: `MIN(method)` still files its 216.84 under `bank`, while the largest-amount rule moves it to `credit` (bank 479,604.5050, credit 471,722.8715).

## Exercise 5: Match percentile grain

`category_order` emits one observation per category/order before calculating
P50. A line-item percentile would answer a different question.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 5, sum line revenue per `(category, order_id)` in `category_order` first, then take `percentile_cont(0.5)` of those order values per category with `COUNT(*)` as `observations`; the faulty version takes the percentile over raw `order_items` rows instead.
- **Expected result/shape:** For sql-56 Exercise 5, expected output: 6 rows whose `observations` add up to 13085 (Apparel 2192, Beauty 2189, Books 2145, Electronics 2187, Home 2186, Sports 2186), with `p50` between 146.54 (Home) and 150.24 (Electronics). The final columns are `category`, `observations`, and `p50`. The final order is `category`.
- **Independent verification:** For sql-56 Exercise 5, confirm that the line-grain query over `order_items` joined to `products` returns the same counts and medians here, because no order has two lines in one category. In a rolled-back transaction, add a second Apparel line (product 1, quantity 1, `unit_price` 10.00) to order 1: the line-grain count for Apparel rises to 2193, while `observations` stays 2192 because order 1 still contributes one Apparel value, now 166.92.
- **Intermediate relation check:** `category_order` has 13,085 rows, one per order and category, which on this data is also one per line. The outer query reduces them to 6 categories with 2,145 to 2,192 observations each.
- **Clause check:** Grouping the CTE by `p.category, o.order_id` before the percentile defines the population as category spend per order. `COUNT(*) AS observations` reports how many such values each median rests on.
- **Alternative/trade-off:** Taking `percentile_cont` straight over `order_items` would measure line values. It gives the same numbers here only because no order repeats a category; add a second Apparel line to an order and the two answers part ways.
- **Edge case:** Grouping by `o.order_id` alone and joining that total back to each category would copy a multi-category order's whole value into every category it touched, pushing all six medians toward the overall order median.

## Exercise 6: Compare percentile definitions

Continuous P50 can interpolate; discrete P50 is an observed order value. The
observation count is retained so even-sized groups can be interpreted.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 6, reuse `category_order` (one value per category and order) and compute `percentile_cont(0.5)` and `percentile_disc(0.5)` side by side per category with `COUNT(*)` as `observations`; Apparel (2192), Home (2186), and Sports (2186) are the even-sized groups.
- **Expected result/shape:** For sql-56 Exercise 6, expected output: 6 rows in which `continuous_p50` equals `discrete_p50` in every category (Apparel 149.5, Beauty 147.66, Books 149.88, Electronics 150.24, Home 146.54, Sports 148.05), because the two middle values of each even group are tied. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
- **Independent verification:** For sql-56 Exercise 6, add `date_trunc('month', o.order_date)` to `category_order` and to the grouping, then compare the two columns: on the checked load 122 of the 133 even-sized category-months show different medians. For 2026-11 Electronics (82 orders) the two middle orders are 134.64 and 141.36, so `continuous_p50` returns their midpoint 138 while `discrete_p50` returns the observed 134.64.
- **Intermediate relation check:** The same 13,085-row `category_order` feeds both percentile functions, so the two medians come from identical populations and only the definition differs.
- **Clause check:** `percentile_cont(0.5)` averages the two middle values of an even group, while `percentile_disc(0.5)` returns the first value at or past the halfway point. Beauty, Books and Electronics have odd counts, so both functions return their single middle value.
- **Alternative/trade-off:** Ordering the values with `ROW_NUMBER` and picking positions `n/2` and `n/2 + 1` by hand shows exactly which two values an even group averages; the built-in functions are shorter but hide that step.
- **Edge case:** Values repeat heavily here, so the two middle values are equal in all three even groups (Apparel, Home and Sports) and the columns agree. Give Apparel one extra high order and the median position moves; then `discrete_p50` stays an observed value while `continuous_p50` may fall between two.