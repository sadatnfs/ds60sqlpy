# Day 04: OUTER JOINs: Preserving Unmatched Rows (Companion Guide)

## How to run this lesson

Open `./classroom`, pick PostgreSQL and **sql-04**, and press **Whole SQL lesson (psql)**. `psql` connects to `advanced_sql_training` and runs three read-only outer joins between `BEGIN` and `ROLLBACK`: customers with their order counts (fewest first), products with units sold (fewest first), and every order or payment that has no partner on the other side.

Your editable copy of the file is
`.learning/sql/sql-04/lesson/workspace/sql/postgres-60day/day04_outer_joins.sql`.
Try changing `LEFT JOIN` to `JOIN` in the first query and rerunning: the first 25 rows change completely, because the customers with no orders vanish and the list starts at customers with four orders instead.

If the classroom will not start or `advanced_sql_training` is missing, see [running a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). Contributors who prefer Jupyter can follow the [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route); learners do not need it.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 03; inner joins](day03_inner_joins.md)
- **Artifacts:** [learner SQL](../day04_outer_joins.sql) ·
  [solution reasoning](../solutions/day04_solutions.md) ·
  [executable solution](../solutions/day04_solutions.sql)

## A beginner's mental model for this lesson

An inner join only keeps pairs that match, so a customer who never ordered simply disappears from `customers JOIN orders`. An outer join names a **preserved side** that keeps every row whether or not a match exists. In `customers c LEFT JOIN orders o`, `customers` is preserved: all 500 customers come through, and the 62 Brazilian customers who have no orders arrive as **NULL-extended rows**, with every `o.` column set to `NULL`.

That `NULL` is the evidence of absence, and the lesson is mostly about not destroying it by accident. Three habits protect it. Count a right-side key, `COUNT(o.order_id)`, so a NULL-extended row counts as 0 rather than 1. Put conditions about the right-side table in `ON`, because a `WHERE o.status = 'delivered'` throws away every row where `o.status` is `NULL`. And decide what `NULL` means before replacing it: `COALESCE(SUM(oi.quantity), 0)` is right for units sold, because a product with no line items really sold zero.

Keeping only the NULL-extended rows gives an **anti-join**: `products LEFT JOIN order_items ... WHERE oi.order_item_id IS NULL` lists the 25 products nobody has bought. A `FULL JOIN` preserves both sides at once, which turns it into a reconciliation tool: anything with `NULL` on one side exists only on the other.

## Two worked SQL examples

### Example 1

```sql
SELECT
  c.customer_id,
  c.full_name,
  COUNT(o.order_id) AS orders
FROM
  customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.full_name
ORDER BY
  orders ASC,
  c.customer_id
LIMIT 25;
```

**How to read it:** `customers` is the preserved side, so every customer survives the join even with no matching order. `COUNT(o.order_id)` skips the `NULL` key on NULL-extended rows, giving 0 for customers without orders. Sorting by `orders ASC` puts those customers first, and `LIMIT 25` shows only the first 25.

**Expected result/shape:** 25 rows, all with `orders` = 0: customers 8, 16, 24 and so on up to 200, every one of them in Brazil. The fixture has 62 such customers (8 to 496 in steps of 8), so the limit hides 37 of them. The lowest count among customers who did order is 4, which is where the list would continue.

### Example 2

```sql
SELECT
  p.product_id,
  p.name,
  COALESCE(SUM(oi.quantity), 0) AS sold_qty
FROM
  order_items oi
  RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.product_id,
  p.name
ORDER BY
  sold_qty ASC,
  p.product_id
LIMIT 25;
```

**How to read it:** This is the same idea written as a `RIGHT JOIN`: `products` is on the right and preserved. Unsold products have no `order_items` rows, so `SUM(oi.quantity)` is `NULL` for them and `COALESCE` turns it into 0. The sort puts the zeros first and breaks ties by `product_id`.

**Expected result/shape:** 25 rows, products 276 to 300, all with `sold_qty` 0. They are exactly the 25 products that appear in no order item, spread over all six categories. Without `COALESCE` the `NULL` sums would sort last under `ASC`, and the top of the list would show product 14 (105 units), 99 and 184 (106 each) instead.

## Learning objectives

- Preserve unmatched dimension rows with an outer join.
- Place nullable-side predicates without accidentally converting a `LEFT JOIN`
  into an inner join.

## Vocabulary and concepts

- **Preserved side:** the side whose rows survive when no match exists.
- **NULL-extended row:** an unmatched outer-join row filled with `NULL` values
  for the other side.
- **Anti-join:** a query that returns rows for which no related row exists.

## Worked example / walkthrough

Start from `products` and left-join `order_items`. A product with no line item
still appears, with `oi.product_id IS NULL`. Moving a right-side filter from
`ON` into `WHERE` removes that row; run both shapes and explain the change.

## Practice assumptions and review method

- **Focus:** Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
- **Assumptions:** Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
- **Failure to watch for:** A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
- **Review loop:** before running, decide which side is preserved and how many rows that side has; afterwards, count the rows whose right-side key is `NULL` and check that number against a separate `NOT EXISTS` query.

## Exercises

Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.

Before each query, write down which table is preserved, how many rows it has, and how many of them you expect to be NULL-extended.

1. **Query writing:** List every customer with order count, including customers with zero orders.
   **Expect:** how many of the 500 rows should show 0, and which country will those customers come from?
   **Progressive hint:** Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
   **Inputs/evidence:** For sql-04 Exercise 1, start from all 500 `customers` and `LEFT JOIN` the 4,362 `orders`; 62 customers have no orders. Return `customer_id`, `full_name`, and `order_count`.
   **Expected result/shape:** For sql-04 Exercise 1, return 500 rows, one per customer: 33 customers tie at the maximum of 16 orders, starting with customer 12, and the 62 customers without orders show 0 at the bottom. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
   **Verify:** For sql-04 Exercise 1, confirm 500 distinct `customer_id` values and that `order_count` sums to 4,362, the size of `orders`. Count rows with `order_count = 0` and expect 62; changing `COUNT(o.order_id)` to `COUNT(*)` would turn each of those zeros into 1.
2. **Query writing:** Find products that have never appeared in an order item.
   **Expect:** Example 2 already showed which products sold nothing. How many rows will this anti-join return?
   **Progressive hint:** Left join and retain rows where the right-side primary key is NULL.
   **Inputs/evidence:** For sql-04 Exercise 2, `LEFT JOIN` all 300 `products` to the 13,085 `order_items` and keep only rows where `oi.order_item_id IS NULL`; the items use 275 distinct products.
   **Expected result/shape:** For sql-04 Exercise 2, return 25 rows, one per product that has never been sold: products 276 through 300. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
   **Verify:** For sql-04 Exercise 2, confirm 300 products minus 275 sold products leaves the 25 returned rows, and that `SELECT COUNT(*) FROM products p WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)` also returns 25. Inside a rolled-back transaction, add one `order_items` row for product 300; the result must drop to 24 rows, ending at product 299.
3. **Query writing:** Compare monthly budgets and expenses by category with a full outer join.
   **Expect:** both tables cover five categories. If they cover the same months too, how many rows will have a `NULL` on either side?
   **Progressive hint:** Aggregate each side to the same category/month grain before joining; preserve keys from either side.
   **Inputs/evidence:** For sql-04 Exercise 3, aggregate `budgets` (125 rows) and `expenses` (10,000 rows) separately to one row per category and month, then `FULL JOIN` the two; each side has 125 category-month keys over 25 months and 5 categories.
   **Expected result/shape:** For sql-04 Exercise 3, return 125 rows, one per category and month, from the oldest budget month to the current month; on the fixture every key exists on both sides, so no amount is `NULL`. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
   **Verify:** For sql-04 Exercise 3, confirm 125 distinct `(category, period)` pairs and zero `NULL` values in either amount column. Inside a rolled-back transaction, delete the `COGS` expenses for the oldest month; the result must still have 125 rows, now with one `NULL` `actual_amount`, while an inner join would drop to 124.
4. **Prediction:** Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
   **Expect:** will more customers show 0 delivered orders than the 62 who never ordered at all?
   **Progressive hint:** Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
   **Inputs/evidence:** For sql-04 Exercise 4, start from all 500 `customers` and `LEFT JOIN` `orders` with `o.status = 'delivered'` inside the `ON` clause; 872 orders are delivered.
   **Expected result/shape:** For sql-04 Exercise 4, return 500 rows, one per customer: 7 customers lead with 4 delivered orders, starting with customer 38, and 69 customers show 0. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
   **Verify:** For sql-04 Exercise 4, confirm 500 rows and that `delivered_orders` sums to 872, matching `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`. Move the status test from `ON` to `WHERE` and the result must shrink to 431 customers, because the 69 zero rows are filtered out.
5. **Debugging:** Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
   **Expect:** with `COUNT(*)`, what does customer 8 show, and why can no real customer in this data show that value?
   **Progressive hint:** Count a non-nullable right-side key that becomes NULL for an unmatched row.
   **Inputs/evidence:** For sql-04 Exercise 5, start from all 500 `customers` and `LEFT JOIN` `orders`, counting `o.order_id` rather than `*`; 62 customers have no orders.
   **Expected result/shape:** For sql-04 Exercise 5, return 500 rows in `customer_id` order; customer 1 has 5 orders, customer 8 has 0, and customer 500 has 10. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
   **Verify:** For sql-04 Exercise 5, confirm `order_count` sums to 4,362 across 438 nonzero rows and 62 zero rows. The buggy `COUNT(*)` version sums to 4,424 instead, because each of the 62 unmatched customers contributes one all-`NULL` joined row.
6. **Extension:** Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
   **Expect:** the three counts should add up to the number of products plus any orphans. What total do you expect?
   **Progressive hint:** Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
   **Inputs/evidence:** For sql-04 Exercise 6, `FULL JOIN` all 300 `products` to the 13,085 `order_items` on `product_id`, which produces 13,110 joined rows, and count distinct product keys by match state.
   **Expected result/shape:** For sql-04 Exercise 6, return exactly one row: `matched_products` 275, `unsold_products` 25, and `orphan_item_product_ids` 0. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
   **Verify:** For sql-04 Exercise 6, confirm 275 + 25 equals `SELECT COUNT(*) FROM products` and that 13,110 joined rows equal 13,085 items plus the 25 unsold products. The orphan count must be 0, because `order_items.product_id` is a foreign key to `products` and cannot point at a missing product.

## Common mistakes and how to recover

- **Filtering the preserved rows away:** `LEFT JOIN orders o ON ... WHERE o.status = 'delivered'` returns 431 customers, not 500, because the `WHERE` drops every NULL-extended row. Move the condition into `ON`.
- **Counting rows instead of matches:** `COUNT(*)` gives each customer without orders a count of 1, since the NULL-extended row is still a row. Count `o.order_id`.
- **Leaving `NULL` sums in a sort:** without `COALESCE`, unsold products have a `NULL` total, which PostgreSQL sorts after every number in ascending order. They drop out of a "fewest first" list.
- **Joining detail to detail in a reconciliation:** joining raw `expenses` rows to `budgets` multiplies each budget by the number of expenses in that month. Sum each side to category and month first, as Exercise 3 does.
- **Assuming a full join found nothing wrong:** zero one-sided rows can mean the data agrees, or that the join key is wrong on both sides. Check the row count against each input.

A typo in one of the three outer joins (the `LEFT`, `RIGHT` or `FULL` query) stops `psql` at that statement, so the queries after it never print; fix the line and rerun the whole file, or follow the study guide's [advice on resetting a failed lesson run](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Do entities with zero matching facts remain visible when the question
  requires complete coverage?
- Can you explain why `COUNT(*)` and `COUNT(right_table.id)` differ after a
  left join?

## Next step

Continue to [Day 05; cross and self joins](day05_cross_self_joins.md).

## Deep dive and reference

Learning objectives
- Use LEFT/RIGHT/FULL OUTER JOIN to retain non-matching rows
- Write NULL-aware filters; COALESCE and IS NULL checks
- Identify when to prefer LEFT JOIN vs INNER JOIN

Why this matters
Real data is messy. Outer joins let you keep entities that currently lack related rows (e.g., products with no sales), which is essential for completeness and auditing.

Core concepts and deep dive
- LEFT OUTER JOIN: keeps all rows from the left table, with NULLs for missing right-side columns.
- RIGHT OUTER JOIN: mirror of LEFT; prefer LEFT by flipping table order for readability.
- FULL OUTER JOIN: keeps rows from both sides even when no match exists; useful for reconciliation.
- NULL-aware filtering: Put right-table predicates in `ON` to avoid turning the
  `LEFT JOIN` into an inner join by accident.
  - Example: `LEFT JOIN payments p ON p.order_id=o.order_id AND p.method='card'`
  - `WHERE p.method='card'` would filter out NULL-extended rows and collapse the
    result to matched card payments.

Walkthrough mapping to your schema
- Products with zero sales: products p LEFT JOIN order_items oi ON oi.product_id=p.product_id; filter WHERE oi.product_id IS NULL to find non-sellers.
- Customer coverage: customers c LEFT JOIN orders o ON o.customer_id=c.customer_id to count actives vs inactives by segment.
- Reconciliation: FULL JOIN of two extracts to find missing keys on either side.

Pitfalls
- Filtering on right-side columns in WHERE after LEFT JOIN removes the NULL-extended rows.
- Aggregations with NULLs: COUNT(oi.*) counts only non-null matches; use COUNT(*) with CASE WHEN to count zeroes explicitly.

Further reading
- Outer joins: https://www.postgresql.org/docs/17/queries-table-expressions.html#QUERIES-FROM

## Ask an AI tutor about this lesson

An AI tutor is optional. A good use for this lesson: ask it to give you a three-customer, four-order table on paper and have you write the output of the same query with `JOIN`, `LEFT JOIN`, and `LEFT JOIN` plus a `WHERE` on an order column, before it reveals the answers. See the study guide's [tutor setup](../../STUDY-GUIDE.md#use-an-ai-tutor-optional); the prompt below keeps solutions hidden.

```text
Tutor me through sql-04: Outer Joins and Unmatched Rows.

I have completed the direct catalog prerequisite: `sql-03`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day04_outer_joins.md
- Answer-free learner SQL: sql/postgres-60day/day04_outer_joins.sql

Key terms to teach in context: Preserved side, NULL-extended row, Anti-join. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Start from `products` and left-join `order_items`. A product with no line item still appears, with `oi.product_id IS NULL`. Moving a right-side filter from `ON` into `WHERE` removes that row; run both shapes and explain the change.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-04/ working copy. Never point setup, reset, DDL, or DML
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
