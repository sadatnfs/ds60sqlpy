# Day 03: INNER JOINs: Relational Linking and Predicate Placement (Companion Guide)

## How to run this lesson

Launch `./classroom`, pick PostgreSQL, open **sql-03** and press **Whole SQL lesson (psql)**. Inside a `BEGIN`/`ROLLBACK` pair on `advanced_sql_training`, the file points `search_path` at `training` and prints two results: the 50 newest order lines with customer and product names attached, then the 20 orders holding the most units, with each buyer's country.

The copy you edit is
`.learning/sql/sql-03/lesson/workspace/sql/postgres-60day/day03_inner_joins.sql`.
Two edits worth trying. Delete `LIMIT 50` and wrap the first query in `SELECT COUNT(*) FROM (...) AS s`: you get 13,085, exactly the number of rows in `order_items`, because every line has an order and a product. Then add `JOIN payments pay ON pay.order_id = o.order_id` to the second query and watch the unit totals for some orders double.

Classroom refusing to start, or `advanced_sql_training` missing? Work through the study guide's [classroom checklist](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). Running lessons from Jupyter is a [contributor-only option](../../STUDY-GUIDE.md#optional-contributor-notebook-route) that learners can skip.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 02; aggregations and grouping](day02_aggregates_groupby_having.md)
- **Artifacts:** [learner SQL](../day03_inner_joins.sql) ·
  [solution reasoning](../solutions/day03_solutions.md) ·
  [executable solution](../solutions/day03_solutions.sql)

## A beginner's mental model for this lesson

An inner join glues a row from one table to a row from another whenever the `ON` condition is true for the pair. In this lesson every `ON` condition compares a **join key**: a foreign key such as `orders.customer_id` against the primary key it points to, `customers.customer_id`. A pair with no match is simply left out, which is what makes the join "inner". Here nothing is lost: all 4,362 orders have a customer and all 13,085 order lines have an order and a product. The 62 Brazilian customers do drop out, though, because they never ordered, so no order row exists to pair with them.

Before writing a join, say how many rows on each side can match. That is the **cardinality** of the relationship. Many orders point to one customer, so joining customers onto orders keeps the order count: 4,362 rows in, 4,362 rows out. One order has one to five line items, so joining `order_items` onto `orders` turns 4,362 rows into 13,085. That growth is called **fanout**. It is correct when you want one row per line, as in Example 1, and wrong when a per-order number like `total_amount` rides along and gets added up once per line.

The habit that prevents most join bugs: name the grain you want, start from the table whose rows have that grain, and only join tables that sit on the "one" side of it. To bring in two tables that are both on the "many" side, such as line items and payments, total each of them per order first and then join the totals. Exercise 4 shows why.

## Two worked SQL examples

### Example 1

```sql
SELECT
  o.order_id,
  o.order_date,
  c.full_name,
  p.name AS product,
  oi.quantity,
  oi.unit_price
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
ORDER BY
  o.order_date DESC,
  o.order_id DESC,
  p.product_id
LIMIT 50;
```

**How to read it:** Three joins hang off `orders`: `customers` adds the buyer's name, `order_items` adds the line rows and `products` turns each `product_id` into a product name. Each `ON` follows one foreign key, and every column carries an alias (`o.`, `c.`, `oi.`, `p.`) so a reader can see which table it comes from. The `ORDER BY` puts the newest orders first and lists each order's lines by product ID; `LIMIT 50` stops after 50 lines.

**Expected result/shape:** 50 rows, one per order line, so an order shows up once per line it holds. In our check the rows cover the 14 newest orders, starting with order 2258 (Customer 258, products 10, 192, 223 and 254) and ending exactly at the last line of order 3027. Without the limit the query returns 13,085 rows, the full size of `order_items`; an inner join here loses nothing, because no line points at a missing order or product.

### Example 2

```sql
SELECT
  o.order_id,
  c.country,
  SUM(oi.quantity) AS total_items
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  o.order_id,
  c.country
ORDER BY
  total_items DESC,
  o.order_id
LIMIT 20;
```

**How to read it:** The same chain, minus `products`, then collapsed with `GROUP BY o.order_id, c.country`. `SUM(oi.quantity)` adds up the units on each order's lines. Listing `c.country` in the `GROUP BY` costs nothing: each order has exactly one customer, so the country cannot split an order into two groups.

**Expected result/shape:** 20 rows, one per order, and every one of them shows 15 units: 872 orders tie at that maximum (five lines with quantities 1 to 5), so `o.order_id` decides which 20 print. They are orders 4, 9, 14 and so on up to 99, starting with order 4 from customer 1 in the US. Remove the limit and you get 4,362 rows, one for every order.

## Learning objectives

- Join related tables with explicit keys and qualified column names.
- Predict one-to-many fanout and validate the intended output grain.

## Vocabulary and concepts

- **Join key:** columns that define how rows from two relations correspond.
- **Cardinality:** whether a relationship is one-to-one, one-to-many, or
  many-to-many.
- **Fanout:** row multiplication caused by matching one row to several rows.

## Worked example / walkthrough

Take order 2258, the newest order in our check. It belongs to Customer 258 in Canada, has a stored `total_amount` of 742.14 and four line items (products 10, 192, 223 and 254). After the join to `order_items` it occupies four rows of Example 1, and each of those rows still carries 742.14. Add `total_amount` across them and you report 2,968.56 for one order. Exercise 6 avoids the trap by measuring revenue from each line's own `unit_price * quantity * (1 - discount)`, which is meant to be summed per line, and only then grouping by country.

## Practice assumptions and review method

- **Focus:** Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
- **Assumptions:** Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
- **Failure to watch for:** A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
- **Review loop:** after each new `JOIN`, run `COUNT(*)` next to `COUNT(DISTINCT ...)` of the key you expect one row per; if the two numbers part ways, a join has multiplied your rows.

## Exercises

Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.

For each exercise, first write the grain as a phrase ("one row per payment", "one row per country") and name the table whose rows already have that grain. That table goes first in `FROM`.

1. **Query writing:** List orders with customer names and countries.
   **Picture it:** 500 customers, 4,362 orders. How many rows come back, and which customers never appear?
   **Progressive hint:** Join the order foreign key to the customer primary key and qualify every selected column.
   **Inputs/evidence:** For sql-03 Exercise 1, join the 4,362 `orders` rows to `customers` on the `customer_id` foreign key, which references the `customers` primary key, so each order finds exactly one customer. Return `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`.
   **Expected result/shape:** For sql-03 Exercise 1, return 4,362 rows, one per order, newest first; order 2258 for customer 258 (`CA`) leads. The 62 customers with no orders, all of them in `BR`, do not appear. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-03 Exercise 1, confirm 4,362 rows and 4,362 distinct `order_id` values, matching `SELECT COUNT(*) FROM orders`, so the inner join neither lost nor repeated an order. Count `country = 'BR'` in the output: it must be 0, because all 62 `BR` customers have no orders.
2. **Query writing:** Calculate each order item's net line revenue with the product name and category.
   **Picture it:** order item 1 is three units at 27.76 with no discount. What should its `line_revenue` be?
   **Progressive hint:** Remain at one row per order item; do not aggregate until the desired grain changes.
   **Inputs/evidence:** For sql-03 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; the items use 275 of the 300 products and every item finds its product. Return `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`.
   **Expected result/shape:** For sql-03 Exercise 2, return 13,085 rows, one per order item, starting with item 1 (order 1, product 48, `Books`, quantity 3, `line_revenue` 83.28). The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
   **Verify:** For sql-03 Exercise 2, confirm 13,085 rows and 13,085 distinct `order_item_id` values, and that the `line_revenue` column sums to 2355648.13, 1.01 above the unrounded 2355647.12 because each line is rounded before the sum. Item 1 has `unit_price` 27.76, `quantity` 3, and `discount` 0.00, so 27.76 * 3 must equal its 83.28.
3. **Query writing:** List payments with order status and customer name.
   **Picture it:** placed orders have never been paid. Which `status` value will be absent from your result?
   **Progressive hint:** Follow payments → orders → customers using each declared foreign key.
   **Inputs/evidence:** For sql-03 Exercise 3, join the 3,836 `payments` rows to `orders` and then to `customers`; the payments cover 3,489 orders, 347 of which have two payments. Return `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`.
   **Expected result/shape:** For sql-03 Exercise 3, return 3,836 rows, one per payment, newest first; payment 654 (order 745, `paypal`, 54.04) leads. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
   **Verify:** For sql-03 Exercise 3, confirm 3,836 rows and 3,836 distinct `payment_id` values, matching `SELECT COUNT(*) FROM payments`, and that `COUNT(DISTINCT order_id)` in the output is 3,489. Order 10 must appear twice, once per payment, which is the expected grain here rather than fan-out.
4. **Prediction:** Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
   **Picture it:** order 10 has one line worth 143.43 and two payments, 71.72 and 71.71. What does a direct three-way join report as its item total?
   **Progressive hint:** Aggregate items and payments separately to one row per order before joining those aggregates.
   **Inputs/evidence:** For sql-03 Exercise 4, aggregate the 13,085 `order_items` rows and the 3,836 `payments` rows to one row per `order_id` each, then join both to `orders`; 873 orders have no payment and 347 have two.
   **Expected result/shape:** For sql-03 Exercise 4, return 4,362 rows, one per order, with `paid_total` 0.00 for the 873 unpaid orders and no doubled item totals for the 347 two-payment orders. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
   **Verify:** For sql-03 Exercise 4, confirm 4,362 distinct `order_id` values; 3,290 orders show equal totals, 199 differ, and 873 show `paid_total` 0.00. Order 10 has one item and two payments: its `item_total` must be 143.43, while joining raw `order_items` to raw `payments` before summing reports 286.86.
5. **Debugging:** Repair a customer/order join whose `ON` clause compares unrelated IDs.
   **Picture it:** the broken query matches `c.customer_id = o.order_id`. Will it raise an error, and how many rows can it return at most?
   **Progressive hint:** Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
   **Inputs/evidence:** For sql-03 Exercise 5, join the 4,362 `orders` rows to `customers` on `customer_id` and count the joined rows and the distinct orders; no row-level key is returned.
   **Expected result/shape:** For sql-03 Exercise 5, return exactly one row with `joined_rows` 4,362 and `distinct_orders` 4,362, which shows every order matched exactly one customer. The final columns are `joined_rows`, and `distinct_orders`.
   **Verify:** For sql-03 Exercise 5, confirm both values equal `SELECT COUNT(*) FROM orders`. Reverse the join into `customers LEFT JOIN orders` and the row count must become 4,424, because the 62 customers without orders each add one unmatched row.
6. **Extension:** Calculate net line revenue by customer country without double-counting order totals.
   **Picture it:** customers live in eight countries. How many rows will the report have?
   **Progressive hint:** Start from line items, join through orders and customers, then aggregate at country grain.
   **Inputs/evidence:** For sql-03 Exercise 6, join the 13,085 `order_items` rows to `orders` and then to `customers`, and total net revenue by `country`; `BR` customers have no orders.
   **Expected result/shape:** For sql-03 Exercise 6, return 7 rows, one per country with orders: `FR` first at 343290.13 and `IN` last at 329081.73, with no `BR` row. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
   **Verify:** For sql-03 Exercise 6, confirm the 7 totals sum to 2355647.12, the same as `SUM(unit_price * quantity * (1 - discount))` over all of `order_items`. Starting the join from `customers` with `LEFT JOIN` must add an eighth `BR` row whose `net_revenue` is `NULL`.

## Common mistakes and how to recover

- **Comparing the wrong keys:** `ON c.customer_id = o.order_id` runs without complaint and returns 500 rows, because order IDs 1 to 500 happen to match customer IDs. Order 2 belongs to customer 1, yet that join labels it Customer 2. A join between two integer columns always runs; only checking the row count against the 4,362 orders exposes it.
- **An `ON` that tests nothing:** `ON c.customer_id = c.customer_id` is always true, so every order pairs with every customer: 2,181,000 rows. A row count far beyond any table in the query means a key comparison is missing.
- **Summing a per-order value after a per-line join:** `SUM(o.total_amount)` over order lines reports 8,633,041.53 instead of 2,355,646.89, because each order total repeats once per line. Sum line values, or total the orders before joining.
- **Joining two "many" tables at once:** orders joined to both `order_items` and `payments` produce 10,816 rows, and payments add up to 6,707,306.05 against a real 1,831,900.81. Every payment repeats once per line and every line once per payment.
- **Patching duplicates with `DISTINCT`:** it can hide a bad join for a while, and it also removes legitimate rows that happen to look alike. Fix the join instead.

If a run stops at an `ERROR`, the study guide's [notes on recovering from failures](../../STUDY-GUIDE.md#recover-from-common-failures) explain how to get back to a clean state.

## Self-check

- Can you diagram every join as one-to-one or one-to-many before running it?
- Does each relationship predicate live in `ON`, with business filters placed
  deliberately?

## Next step

Continue to [Day 04; outer joins](day04_outer_joins.md).

## Deep dive and reference

Learning objectives
- Join multiple tables with explicit INNER JOIN ... ON syntax
- Place join predicates vs row filters correctly (ON vs WHERE)
- Avoid fanout and duplicate rows; validate cardinalities
- Use table aliases and qualified names for clarity

Why this matters
Most analytical questions span multiple entities. Correct join logic preserves row counts, avoids duplicate multiplication, and keeps queries maintainable.

Core concepts and deep dive
- INNER JOIN returns rows where the join condition matches in both tables. Rows without matches are dropped.
- Predicate placement:
  - ON defines how rows from left and right relate. Keep relationship conditions here (keys, equality).
  - WHERE filters the result after joins. Put row-level filters here (time windows, status).
- Cardinality awareness: 1:1, 1:N, N:M. Validate with COUNT(*) vs COUNT(DISTINCT key) to detect accidental fanout.
- Joining chains: Join dimension tables (customers, products) to fact tables (orders, order_items) along keys. Prefer explicit column lists to avoid ambiguous names.

Walkthrough mapping to your schema
- orders o JOIN customers c ON c.customer_id=o.customer_id; adds customer context to orders.
- `order_items oi JOIN products p ON p.product_id=oi.product_id` brings product
  name, category, catalog price, and cost to lines.
- Multi-join: orders→order_items→products to compute revenue: SUM(oi.quantity*oi.unit_price*(1-oi.discount)).

Validation patterns
- Compare: SELECT COUNT(*) FROM orders vs SELECT COUNT(DISTINCT order_id) after joining order_items; counts should match if grouping by order_id.
- Check join selectivity: how many rows drop when adding additional ON predicates.

Anti-patterns and pitfalls
- Old-style comma joins with predicates in WHERE; easy to miss a condition and create cross joins; use explicit JOIN ... ON.
- Using LIKE to join keys; always use exact key equality unless justified.
- Ambiguity in column names after join; qualify columns to avoid surprises.

Further reading
- Joins: https://www.postgresql.org/docs/17/queries-table-expressions.html#QUERIES-JOINS

## Ask an AI tutor about this lesson

A tutor is optional. If you use one, ask it to name a pair of tables from this schema and have you state the relationship (one-to-one, many-to-one or one-to-many) and the row count of their join before you run anything; then compare with `COUNT(*)`. The study guide's [section on AI tutors](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) covers setup and limits.

```text
Tutor me through sql-03: Inner Joins and Predicate Placement.

I have completed the direct catalog prerequisite: `sql-02`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day03_inner_joins.md
- Answer-free learner SQL: sql/postgres-60day/day03_inner_joins.sql

Key terms to teach in context: Join key, Cardinality, Fanout. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Follow one `orders` row through the `order_items` join. It becomes one row per line item, so summing `orders.total_amount` at that point repeats the order total. The learner query instead calculates value from each line and aggregates at the requested customer or category grain.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-03/ working copy. Never point setup, reset, DDL, or DML
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
