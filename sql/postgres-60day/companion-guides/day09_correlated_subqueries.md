# Day 09: Correlated Subqueries and EXISTS (Companion Guide)

## How to run this lesson

Open `./classroom`, choose PostgreSQL and **sql-09**, then run **Whole SQL lesson (psql)**. The script sets `search_path` to `training` inside a `BEGIN`/`ROLLBACK` pair on `advanced_sql_training` and prints two lists: the 432 customers who have bought at least one Electronics item, then the products sold in the last 30 days (256 in our check; that count drifts with the date the fixture was loaded and the date you run it).

Your working copy lives at
`.learning/sql/sql-09/lesson/workspace/sql/postgres-60day/day09_correlated_subqueries.sql`.
A good first edit: change `'Electronics'` to `'Books'`; the list becomes 429 customers in our check and still holds one row per customer. A second: replace `EXISTS` with a plain three-table join and customer 12 prints eight times, once per Electronics line item.

Stuck on setup? The study guide explains [the classroom workflow](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) and an optional [notebook route for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 08; scalar and inline subqueries](day08_scalar_inline_subqueries.md)
- **Artifacts:** [learner SQL](../day09_correlated_subqueries.sql) ·
  [solution reasoning](../solutions/day09_solutions.md) ·
  [executable solution](../solutions/day09_solutions.sql)

## A beginner's mental model for this lesson

A correlated subquery is a query nested inside another that refers to the outer row. In Example 1 the inner query mentions `c.customer_id`, which belongs to the outer `customers` row, so PostgreSQL logically answers it once per customer: does this customer have any order line in Electronics? That outer reference is the **correlation**.

`EXISTS (subquery)` turns the inner query into true or false. It only checks whether at least one row comes back; the `SELECT 1` inside is a placeholder, and no inner column reaches the output. Keeping the outer rows that have a match is a **semi-join**: each customer prints at most once, however many matches exist, so customer 12 appears once despite eight Electronics line items. `NOT EXISTS` is the reverse, an **anti-join**: keep the outer row only when the inner query finds nothing, as in Exercise 4's 62 customers without orders.

A correlated subquery can also return a value instead of true or false. Exercise 3 compares each order with `AVG(peer.total_amount)` over that same customer's orders, so the bar moves from row to row: 504.33 for customer 1, 602.72 for customer 2. The column to watch is the one in the correlation. Tie the inner query to the wrong outer column and it still runs without complaint, but it answers a different question.

## Two worked SQL examples

### Example 1

```sql
SELECT
  c.*
FROM
  customers c
WHERE
  EXISTS (
    SELECT
      1
    FROM
      orders o
      JOIN order_items oi ON oi.order_id = o.order_id
      JOIN products p ON p.product_id = oi.product_id
    WHERE
      o.customer_id = c.customer_id
      AND p.category = 'Electronics')
ORDER BY
  c.customer_id;
```

**How to read it:** For each customer, the inner query walks from that customer's orders through `order_items` to `products` and looks for any line whose product is in Electronics. `WHERE o.customer_id = c.customer_id` is the correlation that ties it to the outer row. `EXISTS` needs only one such line, so the joins inside never multiply customers, and `SELECT c.*` prints all seven `customers` columns.

**Expected result/shape:** 432 rows, one per customer, in ID order. The 68 missing customers are the 62 Brazilian ones, who have no orders at all, and six more (13, 52, 299, 364, 390 and 429) whose four orders contain no Electronics item. Written as a plain join with the same filter, the query returns 2,187 rows, one per Electronics line item.

### Example 2

```sql
SELECT
  p.product_id,
  p.name
FROM
  products p
WHERE
  p.product_id IN ( SELECT DISTINCT
      oi.product_id
    FROM
      order_items oi
      JOIN orders o ON o.order_id = oi.order_id
    WHERE
      o.order_date >= now() - interval '30 days')
ORDER BY
  p.product_id;
```

**How to read it:** This is the `IN` form of a semi-join, and it is not correlated: the inner query lists every `product_id` on a line item from an order placed in the last 30 days without looking at the outer row. `IN` then keeps each product whose ID is somewhere in that list. The `DISTINCT` inside does no harm but changes nothing, because `IN` cannot return a product twice.

**Expected result/shape:** 256 products in our check, all with IDs between 1 and 275, printed by `product_id`. That 30-day window held 209 orders with 642 line items. Because the window is measured from `now()`, expect a slightly different count on your run. Products 276 to 300 can never appear: they have never been sold.

## Learning objectives

- Express existence and non-existence without multiplying outer rows.
- Recognize when a correlated subquery repeats work for each candidate row.

## Vocabulary and concepts

- **Correlation:** a nested query's reference to a column from its outer query.
- **Semi-join:** return an outer row when at least one match exists.
- **Anti-join:** return an outer row only when no match exists.

## Worked example / walkthrough

Read `WHERE EXISTS (...)` as a yes/no question for one outer customer. The
subquery may stop after its first qualifying order, and it never adds order
columns or duplicates the customer. Replace it temporarily with a join to see
why `DISTINCT` may become necessary in the join form.

## Practice assumptions and review method

- **Focus:** Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
- **Assumptions:** `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
- **Failure to watch for:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
- **Review loop:** count the result, then run the opposite test (`NOT EXISTS` for `EXISTS`, or the reverse); the two counts should add up to the whole outer table, 500 customers, 300 products or 4,362 orders.

## Exercises

Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.

Before writing each query, say in one sentence what the inner query asks about a single outer row, and name the column that ties it to that row.

1. **Query writing:** Return customers who have at least one delivered order.
   **Your call:** how many of the 500 customers will be left out, and which group must be among them?
   **Progressive hint:** `EXISTS` expresses the yes/no question without multiplying customer rows.
   **Inputs/evidence:** For sql-09 Exercise 1, keep each of the 500 `customers` rows for which a correlated `EXISTS` finds at least one `orders` row with `status = 'delivered'`; 872 orders are delivered.
   **Expected result/shape:** For sql-09 Exercise 1, return 431 rows, one per customer with a delivered order, from customer 1 to customer 500; the 62 customers without orders and 7 buyers with no delivered order (39, 169, 234, 299, 364, 429, 494) are missing. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 1, confirm 431 equals `SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'delivered'`; a plain `JOIN` on the same condition returns 872 rows because it repeats customers. Inside a rolled-back transaction, set customer 38's 4 delivered orders to `shipped`; the result must drop to 430 rows.
2. **Query writing:** Return products that have never been sold.
   **Your call:** Day 04 found unsold products with an outer join. Should this query return the same count?
   **Progressive hint:** `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
   **Inputs/evidence:** For sql-09 Exercise 2, keep each of the 300 `products` rows for which `NOT EXISTS` finds no `order_items` row with the same `product_id`.
   **Expected result/shape:** For sql-09 Exercise 2, return 25 rows, one per never-sold product, products 276 through 300, from Product 276 (Books) to Product 300 (Books). The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
   **Verify:** For sql-09 Exercise 2, confirm `NOT IN (SELECT product_id FROM order_items)` and a `LEFT JOIN ... WHERE oi.product_id IS NULL` both return the same 25 products, which is safe here because `order_items.product_id` is `NOT NULL`. Inside a rolled-back transaction, insert one `order_items` row for product 276; the result must drop to 24 rows.
3. **Query writing:** Return each customer's orders that are above that customer's average order total.
   **Your call:** customer 1's orders are 240.20, 417.94, 601.73, 1,155.92 and 105.84. Which of them beat that customer's own average?
   **Progressive hint:** Correlate the average to the current order's customer, not to the current order ID.
   **Inputs/evidence:** For sql-09 Exercise 3, compare each of the 4,362 `orders` rows with a correlated subquery that averages `total_amount` over the same customer's orders.
   **Expected result/shape:** For sql-09 Exercise 3, return 2,249 rows, one per order above its own customer's average, covering all 438 buyers; customer 1 contributes orders 4 (1155.92) and 3 (601.73). The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
   **Verify:** For sql-09 Exercise 3, confirm 2,249 distinct `order_id` values and that filtering on `total_amount > AVG(total_amount) OVER (PARTITION BY customer_id)` returns the same 2,249 orders. Comparing with the global average instead, as in sql-08, returns 2,269 rows, so a correlation mistake changes the count.
4. **Prediction:** Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
   **Your call:** if one `NULL` slipped into the list that `NOT IN` compares against, how many customers would come back?
   **Progressive hint:** Correlate on the customer key; a matching row alone determines exclusion.
   **Inputs/evidence:** For sql-09 Exercise 4, keep each of the 500 `customers` rows for which `NOT EXISTS` finds no matching `orders` row.
   **Expected result/shape:** For sql-09 Exercise 4, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 4, confirm the same 62 customers as the sql-06 `EXCEPT` result. Rewrite the filter as `customer_id NOT IN (SELECT customer_id FROM orders UNION ALL SELECT NULL)` and it must return 0 rows, which is why `NOT EXISTS` is used instead of `NOT IN` against a column that can contain `NULL`.
5. **Debugging:** Return only each customer's most recent order without an arbitrary `LIMIT 1`.
   **Your call:** 438 customers have orders. How many rows should print?
   **Progressive hint:** Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
   **Inputs/evidence:** For sql-09 Exercise 5, keep each `orders` row whose `order_id` equals a correlated subquery that picks the same customer's order by `order_date DESC, order_id DESC` with `LIMIT 1`.
   **Expected result/shape:** For sql-09 Exercise 5, return 438 rows, one latest order per buyer, starting with order 5 for customer 1 and ending with order 4362 for customer 500. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
   **Verify:** For sql-09 Exercise 5, confirm 438 distinct `customer_id` values and that `DISTINCT ON (customer_id)` with the same ordering returns the same 438 orders. Inside a rolled-back transaction, insert a new order for customer 1 with the default `order_date` of `now()`; customer 1's row must switch from order 5 to the new order.
6. **Extension:** Return customers for whom every order has at least one payment, excluding customers with no orders.
   **Your call:** none of the 873 placed orders has a payment. What order history would a customer need in order to qualify?
   **Progressive hint:** Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
   **Inputs/evidence:** For sql-09 Exercise 6, keep each `customers` row that has at least one order and no order lacking a `payments` row, using `EXISTS` plus a doubly nested `NOT EXISTS`; 873 of the 4,362 orders have no payment.
   **Expected result/shape:** For sql-09 Exercise 6, return 7 rows, one per customer whose every order is paid: customers 26, 91, 156, 221, 286, 351, and 481, each with 4 orders. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 6, confirm each of the 7 customers has 0 orders without a payment. Dropping the `EXISTS` guard must return 69 rows, because the 62 customers with no orders satisfy the universal condition vacuously. Inside a rolled-back transaction, delete the payments for order 223; customer 26 must leave the result, leaving 6 rows.

## Common mistakes and how to recover

- **Correlating on the wrong column:** in Exercise 3, writing `peer.order_id = o.order_id` makes each order's "average" its own amount. No order is greater than itself, so the query returns 0 rows and raises no error.
- **Trusting `NOT IN` with a list that can hold `NULL`:** `customer_id NOT IN (SELECT customer_id FROM orders)` gives 62 rows only because `orders.customer_id` is declared `NOT NULL`. Add one `NULL` to the list, for example with `UNION ALL SELECT NULL`, and it returns 0 rows, since a comparison with `NULL` is unknown rather than false. `NOT EXISTS` returns 62 either way.
- **Forgetting the empty case in an "every" question:** Exercise 6 without its first `EXISTS` returns 69 customers instead of 7. The extra 62 have no orders, so "none of their orders lacks a payment" is true for them by default.
- **Joining when you meant to test:** a join to `orders` repeats each customer once per matching order, 872 rows for delivered orders instead of 431 customers. Patching that with `DISTINCT` hides the cause; `EXISTS` asks the question directly.
- **A per-row subquery in the `SELECT` list:** harmless for a few hundred customers, but on a big table it means one inner lookup for every output row. Aggregating once and joining the result is usually clearer and faster.

When `psql` halts partway, the study guide's [recovery steps](../../STUDY-GUIDE.md#recover-from-common-failures) cover the usual fixes.

## Self-check

- Does the outer result retain one row per intended entity?
- Can you explain the `NULL` hazard of `NOT IN` and why `NOT EXISTS` avoids it?

## Next step

Continue to [Day 10; data modification with subqueries](day10_dml_with_subqueries.md).

## Deep dive and reference

Learning objectives
- Write correlated subqueries that reference outer query rows
- Use EXISTS/NOT EXISTS efficiently for semi/anti-joins
- Decide between EXISTS vs IN vs JOIN for correctness and performance

Core concepts and deep dive
- Correlated subquery runs per outer row; use with EXISTS to short-circuit on the first match.
- EXISTS returns true if subquery returns any row; NOT EXISTS is a robust anti-join that handles NULLs well.
- IN vs EXISTS: IN materializes a set; EXISTS stops early. Prefer EXISTS for large or non-indexed right sides.

Examples
- Customers with at least one order: WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id).
- Products never sold: WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id=p.product_id).

Pitfalls
- Correlated subqueries in SELECT list scale poorly; precompute and join.
- NOT IN with NULLs can drop all rows unexpectedly; prefer NOT EXISTS with correlated subquery.

Further reading
- EXISTS: https://www.postgresql.org/docs/17/functions-subquery.html

## Ask an AI tutor about this lesson

You can finish this lesson without a tutor. If you want one, ask it to describe a customer with three orders and have you say, before anything runs, whether `EXISTS`, a join and `NOT IN` would each return that customer once, several times or not at all. Setup and ground rules are in the study guide's [tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-09: Correlated Subqueries and EXISTS.

I have completed the direct catalog prerequisite: `sql-08`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day09_correlated_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day09_correlated_subqueries.sql

Key terms to teach in context: Correlation, Semi-join, Anti-join. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Read `WHERE EXISTS (...)` as a yes/no question for one outer customer. The subquery may stop after its first qualifying order, and it never adds order columns or duplicates the customer. Replace it temporarily with a join to see why `DISTINCT` may become necessary in the join form.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-09/ working copy. Never point setup, reset, DDL, or DML
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
