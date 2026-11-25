# Day 08 solutions: Scalar and Inline Subqueries

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Five of these answers put a subquery where a single value belongs and rely on an aggregate (`AVG`, `COUNT` or `MAX`) to guarantee one row; Exercise 4 shows what happens when the subquery finds nothing. Exercise 6 moves the repeated value into a `WITH` clause. Write your versions first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day08_solutions.sql
```

Expect 2,269 orders, 8 countries, 500 customers, a single `t`, 6 categories and 8 countries again. The file runs inside `BEGIN`/`ROLLBACK`, and the snippets below skip its `SET search_path` line. Numbering follows [the learner file](../day08_scalar_inline_subqueries.sql), and the study guide's page on [reading a solution](../../STUDY-GUIDE.md#read-a-solution) suggests what to compare first.

## Reading contract

- **Focus:** Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
- **Assumptions:** A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
- **Primary pitfall:** Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
- **Safety:** nothing here writes; six `SELECT` statements run between `BEGIN` and `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Return orders whose total exceeds the overall average order total.

**Reasoning:** The aggregate subquery is guaranteed to return exactly one value.

**Clause-by-clause reading:**

- `(SELECT AVG(all_orders.total_amount) FROM orders AS all_orders)`: an uncorrelated scalar subquery. It ignores the outer row and returns one number, 540.04 (to two places).
- `WHERE o.total_amount > (...)`: keeps orders strictly above that number.
- `ORDER BY o.total_amount DESC, o.order_id`: biggest orders first, ID breaking ties.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount
FROM
  orders AS o
WHERE
  o.total_amount > (
    SELECT
      AVG(all_orders.total_amount)
    FROM
      orders AS all_orders)
ORDER BY
  o.total_amount DESC,
  o.order_id;
```

**Expected shape:** Order rows above the global average.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 1, compare each of the 4,362 `orders` rows with one scalar subquery, `SELECT AVG(total_amount) FROM orders`, which evaluates to about 540.0383.
- **Expected result/shape:** For sql-08 Exercise 1, return 2,269 rows, one per order above the average, from 16 orders tied at 1432.49 (order 104 first) down to 540.27. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
- **Independent verification:** For sql-08 Exercise 1, confirm 2,269 distinct `order_id` values and that the complementary filter `total_amount <= (SELECT AVG(total_amount) FROM orders)` returns the other 2,093 orders, topping out at 538.05. Replace `AVG(all_orders.total_amount)` with the bare column and the query must fail with `more than one row returned by a subquery used as an expression`.
- **What prints:** 2,269 of the 4,362 orders, from 1,432.49 down to 540.27 (order 29, customer 5). Sixteen orders tie at the top value, so the ID ordering matters: 104, 379 and 654 come first.
- **Why more than half:** the median order is 561.21, above the mean of 540.04, so a little over half the orders (52%) clear the average.
- **The alias inside:** writing `AVG(o.total_amount)` inside the subquery points the aggregate at the outer `orders`, and PostgreSQL rejects the query with `aggregate functions are not allowed in WHERE`. Plain `AVG(total_amount)` works because an unqualified name is looked up in the nearest `FROM` first; the `all_orders` alias makes that choice visible.

## Exercise 2: Query writing

**Prompt:** Add the total customer count as a scalar column beside each country-level customer count.

**Reasoning:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.

**Clause-by-clause reading:**

- `FROM customers AS c GROUP BY c.country`: one group per country.
- `COUNT(*) AS country_customers`: how many customers each group holds.
- `(SELECT COUNT(*) FROM customers) AS all_customers`: an uncorrelated scalar subquery, the same 500 on every row. It is allowed beside `GROUP BY` because it does not depend on any ungrouped column.
- `ORDER BY country_customers DESC, c.country`: larger countries first, alphabetical within ties.

```sql
SELECT
  c.country,
  COUNT(*) AS country_customers,
  (
    SELECT
      COUNT(*)
    FROM
      customers) AS all_customers
FROM
  customers AS c
GROUP BY
  c.country
ORDER BY
  country_customers DESC,
  c.country;
```

**Expected shape:** One row per country with a common global total.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 2, group the 500 `customers` rows by `country` and add an uncorrelated scalar subquery, `SELECT COUNT(*) FROM customers`, as a constant column.
- **Expected result/shape:** For sql-08 Exercise 2, return 8 rows, one per country: CA, DE, GB, and US with 63 customers, then AU, BR, FR, and IN with 62, each showing `all_customers` = 500. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
- **Independent verification:** For sql-08 Exercise 2, confirm the `country_customers` values sum to 500, the value repeated in every `all_customers` cell. Inside a rolled-back transaction, insert one customer from `MX`; the result must grow to 9 rows, with `MX` at 1 and every `all_customers` value at 501.
- **What prints:** 8 rows. CA, DE, GB and US have 63 customers each; AU, BR, FR and IN have 62. Every row shows 500 in `all_customers`.
- **Reconciliation:** 4 x 63 + 4 x 62 = 500, which matches the scalar column. Brazil appears here, unlike in reports built from orders, because this one counts customers.
- **Why not `COUNT(*)` twice:** a second `COUNT(*)` in the same `SELECT` would count the current group, not the table; only the subquery steps outside the grouping.

## Exercise 3: Query writing

**Prompt:** Show each customer with their latest order timestamp using a scalar correlated subquery.

**Reasoning:** Use `MAX` to guarantee one result and let customers without orders receive NULL.

**Clause-by-clause reading:**

- `FROM customers AS c`: all 500 customers, including those with no orders.
- `(SELECT MAX(o.order_date) FROM orders AS o WHERE o.customer_id = c.customer_id)`: a correlated scalar subquery. `MAX` reduces each customer's orders to one timestamp, or to `NULL` when there are none.
- `ORDER BY latest_order_date DESC NULLS LAST, c.customer_id`: most recent buyers first, customers with no orders at the bottom.

```sql
SELECT
  c.customer_id,
  c.full_name,
  (
    SELECT
      MAX(o.order_date)
    FROM
      orders AS o
    WHERE
      o.customer_id = c.customer_id) AS latest_order_date
FROM
  customers AS c
ORDER BY
  latest_order_date DESC NULLS LAST,
  c.customer_id;
```

**Expected shape:** One row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 3, list all 500 `customers` and fill `latest_order_date` with a correlated subquery that takes `MAX(order_date)` over that customer's `orders`.
- **Expected result/shape:** For sql-08 Exercise 3, return 500 rows, one per customer: 438 dated rows, newest first and led by customer 258 on a freshly loaded fixture, then the 62 customers without orders with a `NULL` date. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
- **Independent verification:** For sql-08 Exercise 3, confirm 438 non-`NULL` dates, all distinct, so the `c.customer_id` tiebreaker only orders the 62 `NULL` rows. A `LEFT JOIN` to `orders` grouped by customer must return the same 500 `(customer_id, latest_order_date)` pairs; removing `NULLS LAST` must move customers 8 through 496 to the top.
- **What prints:** 500 rows. In our check the first is customer 258 (latest order 2026-11-23), then 86 and 259; the last dated row is customer 429, whose most recent order goes back to February 2026.
- **The 62 blanks:** rows 439 to 500 are the Brazilian customers with `NULL` dates, sorted by ID from 8 to 496.
- **Without `NULLS LAST`:** PostgreSQL puts `NULL` first in a descending sort, so the list would open with 62 empty rows.
- **Without `MAX`:** the raw `o.order_date` version fails as soon as it reaches a customer with two or more orders.

## Exercise 4: Prediction

**Prompt:** Demonstrate that a scalar subquery with no matching rows returns NULL.

**Reasoning:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.

**Clause-by-clause reading:**

- `(SELECT p.price FROM products AS p WHERE p.product_id = -1)`: looks up a product ID that cannot exist, so the subquery finds no row.
- `... IS NULL AS no_row_becomes_null`: tests the result of that empty lookup.
- No `FROM` on the outer query: it returns exactly one row with one boolean.

```sql
SELECT
  (
    SELECT
      p.price
    FROM
      products AS p
    WHERE
      p.product_id = -1) IS NULL AS no_row_becomes_null;
```

**Expected shape:** One row whose boolean result is true.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 4, wrap a scalar subquery that selects `price` for `product_id = -1`, an ID no `products` row has, and test the result with `IS NULL`.
- **Expected result/shape:** For sql-08 Exercise 4, return one row with `no_row_becomes_null` = `true`. The final columns are `no_row_becomes_null`.
- **Independent verification:** For sql-08 Exercise 4, confirm `SELECT COUNT(*) FROM products WHERE product_id = -1` returns 0, so the scalar subquery has no row and yields `NULL`. Point the subquery at product 300 instead and the column must become `false`, because that row exists with a price of 121.00.
- **What prints:** one row, `t`. An empty scalar subquery is not an error and not zero rows; it becomes `NULL`, and `IS NULL` reports true.
- **The tempting wrong test:** `(...) = NULL` prints an empty cell instead of true, because any comparison with `NULL` is unknown.
- **Same lookup, other forms:** `SELECT COUNT(*) FROM products WHERE product_id = -1` returns 0, and the bare `SELECT p.price ... WHERE p.product_id = -1` returns zero rows. Only the scalar form turns "nothing" into `NULL`.

## Exercise 5: Debugging

**Prompt:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.

**Reasoning:** Choose the business reduction explicitly; this answer uses maximum price.

**Clause-by-clause reading:**

- `FROM products AS p GROUP BY p.category`: six groups of 50 products.
- `MAX(p.price) AS category_max_price`: the most expensive product per category.
- `(SELECT MAX(all_products.price) FROM products AS all_products) AS global_max_price`: the repaired subquery. `MAX` reduces 300 prices to one.
- `ORDER BY p.category`: categories alphabetically.

```sql
SELECT
  p.category,
  MAX(p.price) AS category_max_price,
  (
    SELECT
      MAX(all_products.price)
    FROM
      products AS all_products) AS global_max_price
FROM
  products AS p
GROUP BY
  p.category
ORDER BY
  p.category;
```

**Expected shape:** One row per category with a scalar global maximum for comparison.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 5, group the 300 `products` rows (50 per category) by `category` for `MAX(price)`, and add the uncorrelated subquery `SELECT MAX(price) FROM products` as a constant column.
- **Expected result/shape:** For sql-08 Exercise 5, return 6 rows, one per category from Apparel (119.15) to Sports (120.63); every row shows `global_max_price` = 121.00, which only Books reaches, through product 300. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
- **Independent verification:** For sql-08 Exercise 5, confirm `global_max_price` equals the largest `category_max_price` (121.00 for Books). Inside a rolled-back transaction, set product 1's price to 130.00; Apparel's maximum and every `global_max_price` value must become 130.00, while the other five category maximums stay the same.
- **What prints:** 6 rows, Apparel to Sports, each showing a global maximum of 121.00. Category maximums run from 119.15 (Apparel) to 121.00 (Books).
- **What the bug printed:** `(SELECT price FROM products)` returns 300 rows, and PostgreSQL stops with `more than one row returned by a subquery used as an expression`. The query never prints any rows.
- **Where 121.00 comes from:** product 300, a Book, which has never been sold. A price report built from order lines would never show it.
- **Gap to the top:** Books holds the global maximum, so its gap is 0.00. Sports trails by 0.37 and Apparel by 1.85, the widest gap of the six.
- **Choosing the reduction:** `MAX` answers "highest price"; `AVG` or `MIN` would be equally valid fixes for other questions, which is why the hint asks you to choose on purpose.

## Exercise 6: Extension

**Prompt:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.

**Reasoning:** Compute the global total once, then cross join the guaranteed one-row relation.

**Clause-by-clause reading:**

- `WITH global AS (SELECT COUNT(*)::numeric AS customer_count FROM customers)`: a one-row, one-column relation computed once; the cast makes later division exact.
- `FROM customers AS c CROSS JOIN global`: pairs every customer with that single row, so the customer count stays at 500.
- `GROUP BY c.country, global.customer_count`: the total must appear in `GROUP BY` because it is a column now, not a subquery; it has one value, so it does not split any group.
- `ROUND(COUNT(*) / NULLIF(global.customer_count, 0), 4) AS customer_share`: each country's share of all customers, guarded against an empty table.
- `ORDER BY customer_share DESC, c.country`: largest share first.

```sql
WITH global AS (
  SELECT
    COUNT(*)::numeric AS customer_count
  FROM
    customers
)
SELECT
  c.country,
  COUNT(*) AS country_customers,
  ROUND(COUNT(*) / NULLIF (global.customer_count, 0), 4) AS customer_share
FROM
  customers AS c
  CROSS JOIN global
GROUP BY
  c.country,
  global.customer_count
ORDER BY
  customer_share DESC,
  c.country;
```

**Expected shape:** One row per country with country share.

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 6, read from `customers`; compute the overall customer count once in a one-row CTE named `global`, then return each `country` with `country_customers` and `customer_share`, its fraction of all customers rounded to 4 places.
- **Expected result/shape:** For sql-08 Exercise 6, return 8 rows, one per country, with the four 63-customer countries (CA, DE, GB, US) first at 0.1260 and the four 62-customer countries (AU, BR, FR, IN) after them at 0.1240. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
- **Independent verification:** For sql-08 Exercise 6, confirm 8 rows whose `country_customers` add up to `SELECT COUNT(*) FROM customers` (500) and whose `customer_share` values add up to 1.0000; on the seed, CA, DE, GB, and US have 63 customers (0.1260) and AU, BR, FR, and IN have 62 (0.1240).
- **What prints:** 8 rows. CA, DE, GB and US show 63 customers and a share of 0.1260; AU, BR, FR and IN show 62 and 0.1240. The shares add up to 1.0000.
- **Why the cast:** without `::numeric`, `63 / 500` is integer division and every share would print 0.
- **Why `CROSS JOIN` is safe here:** a cross join multiplies rows, but by exactly one, because `global` is an aggregate without `GROUP BY`.
- **Same answer, older form:** Exercise 2's scalar subquery could compute the share too; the CTE names the total once and makes it easy to reuse in several columns.

## Final self-check

- What makes `(SELECT AVG(total_amount) FROM orders)` safe as a scalar subquery?
- What does a scalar subquery return when it finds no row, and how do you test for it?
- Why would Example 1 show 62 blank rows at the top without `COALESCE`?
- Which product supplies the 121.00 in Exercise 5, and why would a sales report miss it?
- Why does Exercise 6 add `global.customer_count` to `GROUP BY`?
