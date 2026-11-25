# Day 08: Scalar and Inline Subqueries (Companion Guide)

## How to run this lesson

From the repository root, start `./classroom`, select PostgreSQL, open **sql-08** and run **Whole SQL lesson (psql)**. The script switches `search_path` to `training` inside `BEGIN`/`ROLLBACK` on `advanced_sql_training`, then prints two results: the 20 customers with the highest lifetime revenue, worked out by a subquery in the `SELECT` list, and the average order value per product category, worked out by a subquery in `FROM`.

Your editable copy sits at
`.learning/sql/sql-08/lesson/workspace/sql/postgres-60day/day08_scalar_inline_subqueries.sql`.
Try removing the `COALESCE(..., 0)` from the first query. The 62 customers with no orders now get `NULL` instead of 0.00, and because `DESC` sorts `NULL` first, they fill the whole top 20 with blank revenue.

When the classroom does not come up, the study guide walks through [starting a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). A [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) exists for contributors only.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 07; Week 1 project](day07_week1_project.md)
- **Artifacts:** [learner SQL](../day08_scalar_inline_subqueries.sql) ·
  [solution reasoning](../solutions/day08_solutions.md) ·
  [executable solution](../solutions/day08_solutions.sql)

## A beginner's mental model for this lesson

A subquery is a complete `SELECT` placed inside another query. Where you put it decides what it must return. In the `SELECT` list or in a comparison such as `total_amount > (...)`, it stands in for a single value, so it is a **scalar subquery**: it must produce one column and at most one row. Zero rows is allowed and becomes `NULL`. Two or more rows stop the query with `more than one row returned by a subquery used as an expression`.

The safest way to promise one row is an aggregate without `GROUP BY`. `SELECT AVG(total_amount) FROM orders` always returns exactly one row, 540.04 here, even on an empty table. In Example 1 the subquery also refers to `c.customer_id` from the outer query, so it is worked out again for each customer. Exercise 1's average does not mention the outer row at all; an **uncorrelated subquery** like that gives the same value on every row.

A subquery in `FROM` plays a different role. It may return any number of rows, and the outer query treats them like a table under the alias you give it. Example 2 builds one such **inline view** `x` holding one row per category and order, then averages it per category. When an inline view gets long or is needed twice, a `WITH` clause (Exercise 6) does the same job with a name at the top of the query.

## Two worked SQL examples

### Example 1

```sql
SELECT
  c.customer_id,
  c.full_name,
  (
    SELECT
      ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0), 2)
    FROM
      orders o
      JOIN order_items oi ON oi.order_id = o.order_id
    WHERE
      o.customer_id = c.customer_id) AS lifetime_revenue
FROM
  customers c
ORDER BY
  lifetime_revenue DESC,
  c.customer_id
LIMIT 20;
```

**How to read it:** The outer query walks through all 500 customers. For each one, the subquery in the `SELECT` list joins that customer's orders to their line items and adds up the net line value. `WHERE o.customer_id = c.customer_id` ties the inner query to the current customer, and `SUM` folds all their lines into one number. `COALESCE(..., 0)` turns "no lines at all" into 0, and the result is sorted on the alias `lifetime_revenue`.

**Expected result/shape:** 20 rows, one per customer. Customer 181 leads with 9,502.22 across 16 orders, followed by customers 12 (9,244.26) and 25 (9,196.96); the twentieth row is customer 259 at 8,760.17. All 500 customers are evaluated before the limit is applied, and the 62 Brazilian customers sit at the bottom with 0.00.

### Example 2

```sql
SELECT
  x.category,
  ROUND(AVG(x.order_total), 2) AS avg_order_total
FROM (
  SELECT
    p.category,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category,
    o.order_id) x
GROUP BY
  x.category
ORDER BY
  avg_order_total DESC,
  x.category;
```

**How to read it:** Read the inner query first. It joins orders, lines and products and groups by `p.category, o.order_id`, so each row is "what this order spent in this category". The outer query treats that result as a table named `x` and averages `order_total` per category. A subquery in `FROM` must have an alias; leave out `x` and PostgreSQL refuses to run it.

**Expected result/shape:** 6 rows, one per category, from Sports at 181.81 down to Apparel at 178.10. The inner query produces 13,085 rows, exactly the number of order lines, which tells you no order buys two products from the same category. So in this data each category average is also the plain average line value; with real baskets the two would differ.

## Learning objectives

- Use a scalar subquery only where zero or one value is guaranteed.
- Compare subquery forms with equivalent joins for correctness and work done.

## Vocabulary and concepts

- **Scalar subquery:** a nested query used where one value is expected.
- **Inline view:** a subquery in `FROM` that behaves like a temporary relation.
- **Uncorrelated subquery:** a nested query that does not reference the outer
  row.

## Worked example / walkthrough

Ask for each customer's order date with a subquery that has no aggregate: `(SELECT o.order_date FROM orders o WHERE o.customer_id = c.customer_id)`. For customer 8, who has no orders, it works and returns `NULL`. For customer 1, with five orders, it returns five dates, and the whole query fails with the "more than one row" error. Wrapping the column in `MAX(...)` turns five dates into one, which is exactly what Exercise 3 does. Adding `LIMIT 1` would also silence the error, but without an `ORDER BY` it returns whichever date PostgreSQL reads first.

## Practice assumptions and review method

- **Focus:** Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
- **Assumptions:** A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
- **Failure to watch for:** Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
- **Review loop:** for every subquery, write "returns at most one row because..." next to it and finish the sentence with an aggregate, a primary key or an ordered `LIMIT 1`; then run it alone with one outer value filled in.

## Exercises

Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.

Before each query, decide which kind of subquery the exercise needs: one value (scalar) or a whole table (in `FROM` or `WITH`). For a scalar one, say what guarantees a single row.

1. **Query writing:** Return orders whose total exceeds the overall average order total.
   **Bet:** the average order is 540.04 but the median is 561.21. Will more or fewer than half of the 4,362 orders beat the average?
   **Progressive hint:** The aggregate subquery is guaranteed to return exactly one value.
   **Inputs/evidence:** For sql-08 Exercise 1, compare each of the 4,362 `orders` rows with one scalar subquery, `SELECT AVG(total_amount) FROM orders`, which evaluates to about 540.0383.
   **Expected result/shape:** For sql-08 Exercise 1, return 2,269 rows, one per order above the average, from 16 orders tied at 1432.49 (order 104 first) down to 540.27. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
   **Verify:** For sql-08 Exercise 1, confirm 2,269 distinct `order_id` values and that the complementary filter `total_amount <= (SELECT AVG(total_amount) FROM orders)` returns the other 2,093 orders, topping out at 538.05. Replace `AVG(all_orders.total_amount)` with the bare column and the query must fail with `more than one row returned by a subquery used as an expression`.
2. **Query writing:** Add the total customer count as a scalar column beside each country-level customer count.
   **Bet:** how many rows print, and what value fills `all_customers` on each of them?
   **Progressive hint:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
   **Inputs/evidence:** For sql-08 Exercise 2, group the 500 `customers` rows by `country` and add an uncorrelated scalar subquery, `SELECT COUNT(*) FROM customers`, as a constant column.
   **Expected result/shape:** For sql-08 Exercise 2, return 8 rows, one per country: CA, DE, GB, and US with 63 customers, then AU, BR, FR, and IN with 62, each showing `all_customers` = 500. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
   **Verify:** For sql-08 Exercise 2, confirm the `country_customers` values sum to 500, the value repeated in every `all_customers` cell. Inside a rolled-back transaction, insert one customer from `MX`; the result must grow to 9 rows, with `MX` at 1 and every `all_customers` value at 501.
3. **Query writing:** Show each customer with their latest order timestamp using a scalar correlated subquery.
   **Bet:** how many of the 500 rows will have no date, and where will `NULLS LAST` put them?
   **Progressive hint:** Use `MAX` to guarantee one result and let customers without orders receive NULL.
   **Inputs/evidence:** For sql-08 Exercise 3, list all 500 `customers` and fill `latest_order_date` with a correlated subquery that takes `MAX(order_date)` over that customer's `orders`.
   **Expected result/shape:** For sql-08 Exercise 3, return 500 rows, one per customer: 438 dated rows, newest first and led by customer 258 on a freshly loaded fixture, then the 62 customers without orders with a `NULL` date. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
   **Verify:** For sql-08 Exercise 3, confirm 438 non-`NULL` dates, all distinct, so the `c.customer_id` tiebreaker only orders the 62 `NULL` rows. A `LEFT JOIN` to `orders` grouped by customer must return the same 500 `(customer_id, latest_order_date)` pairs; removing `NULLS LAST` must move customers 8 through 496 to the top.
4. **Prediction:** Demonstrate that a scalar subquery with no matching rows returns NULL.
   **Bet:** no product has ID -1. Does the query error, print zero rows, or print one row?
   **Progressive hint:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.
   **Inputs/evidence:** For sql-08 Exercise 4, wrap a scalar subquery that selects `price` for `product_id = -1`, an ID no `products` row has, and test the result with `IS NULL`.
   **Expected result/shape:** For sql-08 Exercise 4, return one row with `no_row_becomes_null` = `true`. The final columns are `no_row_becomes_null`.
   **Verify:** For sql-08 Exercise 4, confirm `SELECT COUNT(*) FROM products WHERE product_id = -1` returns 0, so the scalar subquery has no row and yields `NULL`. Point the subquery at product 300 instead and the column must become `false`, because that row exists with a price of 121.00.
5. **Debugging:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
   **Bet:** the broken version selects `price` from all 300 products. Which message do you get, and on which row?
   **Progressive hint:** Choose the business reduction explicitly; this answer uses maximum price.
   **Inputs/evidence:** For sql-08 Exercise 5, group the 300 `products` rows (50 per category) by `category` for `MAX(price)`, and add the uncorrelated subquery `SELECT MAX(price) FROM products` as a constant column.
   **Expected result/shape:** For sql-08 Exercise 5, return 6 rows, one per category from Apparel (119.15) to Sports (120.63); every row shows `global_max_price` = 121.00, which only Books reaches, through product 300. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
   **Verify:** For sql-08 Exercise 5, confirm `global_max_price` equals the largest `category_max_price` (121.00 for Books). Inside a rolled-back transaction, set product 1's price to 130.00; Apparel's maximum and every `global_max_price` value must become 130.00, while the other five category maximums stay the same.
6. **Extension:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
   **Bet:** what is 63 divided by 500 in integer arithmetic, and why does the CTE cast the count to `numeric`?
   **Progressive hint:** Compute the global total once, then cross join the guaranteed one-row relation.
   **Inputs/evidence:** For sql-08 Exercise 6, read from `customers`; compute the overall customer count once in a one-row CTE named `global`, then return each `country` with `country_customers` and `customer_share`, its fraction of all customers rounded to 4 places.
   **Expected result/shape:** For sql-08 Exercise 6, return 8 rows, one per country, with the four 63-customer countries (CA, DE, GB, US) first at 0.1260 and the four 62-customer countries (AU, BR, FR, IN) after them at 0.1240. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
   **Verify:** For sql-08 Exercise 6, confirm 8 rows whose `country_customers` add up to `SELECT COUNT(*) FROM customers` (500) and whose `customer_share` values add up to 1.0000; on the seed, CA, DE, GB, and US have 63 customers (0.1260) and AU, BR, FR, and IN have 62 (0.1240).

## Common mistakes and how to recover

- **A scalar subquery that can return several rows:** `(SELECT order_date FROM orders o WHERE o.customer_id = c.customer_id)` runs fine for a customer with no orders and fails with `more than one row returned by a subquery used as an expression` as soon as it meets customer 1. Fix it with an aggregate such as `MAX`, not by hoping the data stays small.
- **`LIMIT 1` as a silencer:** it stops the error but picks an arbitrary row unless an `ORDER BY` inside the subquery says which one, and even then it hides the question of whether several rows were expected.
- **Sorting `NULL` by accident:** without `COALESCE`, Example 1's customers with no orders get `NULL`, and `ORDER BY ... DESC` puts `NULL` first. Exercise 3 writes `NULLS LAST` for the same reason.
- **Testing the empty result with `=`:** `(SELECT price FROM products WHERE product_id = -1) = NULL` prints a blank rather than true. Only `IS NULL` answers "is this missing?".
- **Integer division in shares:** `63 / 500` is 0 in PostgreSQL because both sides are integers; Exercise 6 casts the total to `numeric` to get 0.1260.
- **Forgetting the alias on a `FROM` subquery:** PostgreSQL requires a name such as `x` for the derived table.

For an `ERROR` that halts `psql` midway, the study guide's [failure recovery section](../../STUDY-GUIDE.md#recover-from-common-failures) shows how to reset and rerun.

## Self-check

- Can every scalar subquery prove its one-value contract without an arbitrary
  `LIMIT 1`?
- Are customers with no matching orders handled deliberately?

## Next step

Continue to [Day 09; correlated subqueries and EXISTS](day09_correlated_subqueries.md).

## Deep dive and reference

Learning objectives
- Use scalar subqueries in SELECT/WHERE for per-row lookups
- Use IN/ANY/ALL with subqueries and understand semantics
- Replace subqueries with joins where appropriate for performance

Core concepts and deep dive
- Scalar subquery returns a single value; errors on >1 row. Use LIMIT 1 with ORDER BY to guarantee determinism.
- IN subquery builds a set; ANY/ALL compare a value against a subquery-produced set with an operator.
- Correlated vs uncorrelated inline subqueries: prefer uncorrelated when possible.

Examples
- SELECT customer_id, (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.customer_id) AS order_cnt FROM customers c.
- `WHERE product_id IN (SELECT product_id FROM promotions WHERE CURRENT_DATE
  BETWEEN start_date AND end_date)`.

Pitfalls
- Scalar subqueries in SELECT executed per row; may be slow. Consider pre-aggregating and joining.
- IN with large sets can be slow; join instead or use EXISTS.

Further reading
- Subqueries: https://www.postgresql.org/docs/17/sql-select.html#SQL-SELECT-SUBQUERIES

## Ask an AI tutor about this lesson

No tutor is needed. If you want one, have it show you subqueries from this lesson with the aggregate removed or the filter changed, and before running each one say whether it returns no row, one row or many, and what PostgreSQL does in each case. The study guide's [tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) explain how to keep it from revealing the solutions.

```text
Tutor me through sql-08: Scalar and Inline Subqueries.

I have completed the direct catalog prerequisite: `sql-07`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day08_scalar_inline_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day08_scalar_inline_subqueries.sql

Key terms to teach in context: Scalar subquery, Inline view, Uncorrelated subquery. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For each customer, the learner needs one first-order date. `MIN(order_date)` returns exactly one value, including `NULL` when no order exists. Contrast that with selecting raw order dates, which can raise “more than one row returned by a subquery used as an expression.”

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-08/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
