# Day 20: FIRST_VALUE, LAST_VALUE, and Window Frames (Companion Guide)

## How to run this lesson

Run `./classroom` at the repository root, choose PostgreSQL and **sql-20**, then **Whole SQL lesson (psql)**. Inside one transaction on `advanced_sql_training` (with `search_path` set to `training`, rolled back at the end), the file prints the first 100 orders by customer twice: once with each customer's first and last order amount beside every order, and once with each order's difference from that customer's first amount.

The copy you edit lives at
`.learning/sql/sql-20/lesson/workspace/sql/postgres-60day/day20_first_last_value.sql`.
Try deleting the `ROWS BETWEEN ... UNBOUNDED FOLLOWING` line from the `LAST_VALUE` call in Example 1 and rerunning: `last_order_amount` then copies `total_amount` on every row.

The study guide covers [launching a lesson from the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) if anything goes wrong, and keeps a separate [notebook workflow for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route) that learners do not need.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 19; running aggregates](day19_running_aggregates.md)
- **Artifacts:** [learner SQL](../day20_first_last_value.sql) ·
  [solution reasoning](../solutions/day20_solutions.md) ·
  [executable solution](../solutions/day20_solutions.sql)

## A beginner's mental model for this lesson

`FIRST_VALUE(x)` and `LAST_VALUE(x)` are window functions: every order keeps its own row, and each row gains a copy of some **boundary value** from its partition, such as the amount of the customer's earliest or latest order. "First" and "last" refer to positions under the window's `ORDER BY`, not to the smallest or largest value. Customer 1's first order by date is 240.20 and the last is 105.84, even though the largest is 1,155.92.

Which rows count depends on the window frame. When a window has `ORDER BY` and no frame clause, PostgreSQL uses a **current-row frame**: from the start of the partition up to the current row and any rows tied with it. `FIRST_VALUE` is unaffected, because the first row is always inside that frame. `LAST_VALUE` is not: it sees only rows up to the current one, so on unique dates it simply returns the current row's own value.

A **full-partition frame**, `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, gives every row the whole partition, so `LAST_VALUE` really returns the partition's final row. Window functions run before `ORDER BY` and `LIMIT`, so a customer whose orders are cut off by `LIMIT 100` still shows the true last value from orders that are not printed.

## Two worked SQL examples

### Example 1

```sql
SELECT
  o.customer_id,
  o.order_id,
  o.order_date,
  o.total_amount,
  FIRST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_order_amount,
  LAST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_amount
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 100;
```

**How to read it:** Both window calls use the same partition (`o.customer_id`), the same order (`o.order_date, o.order_id`) and the full frame, so every order of a customer carries the same `first_order_amount` and `last_order_amount`. The outer `ORDER BY` and `LIMIT 100` decide which orders are printed, after the windows have already seen every order.

**Expected result/shape:** 100 rows covering customers 1 to 12, without customer 8, who has no orders. Customer 1's five rows all show 240.20 and 105.84. The list stops after customer 12's first two orders, yet those rows already show 851.69 as the last amount, from order 114, which is not printed. That is the window running before `LIMIT`.

### Example 2

```sql
WITH per_cust AS (
  SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    o.total_amount,
    FIRST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date,
      o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_amt
  FROM
    orders o
)
SELECT
  *,
  ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM
  per_cust
ORDER BY
  customer_id,
  order_date,
  order_id
LIMIT 100;
```

**How to read it:** The CTE `per_cust` adds `first_amt`, each customer's first order amount, to every order. The outer query subtracts it from the row's own amount. `SELECT *` passes through the CTE's five columns, so the output has six: `customer_id`, `order_id`, `order_date`, `total_amount`, `first_amt` and `delta_from_first`.

**Expected result/shape:** The same 100 orders. Each customer's first row shows a delta of 0.00. Customer 1's deltas are 0.00, 177.74, 361.53, 915.72 and -134.36, so the last order was smaller than the first. Customer 2 starts at 460.35, so its sixth order of 680.50 has a delta of 220.15.

## Learning objectives

- Retrieve boundary values from a deliberately framed ordered partition.
- Diagnose the common `LAST_VALUE` default-frame surprise.

## Vocabulary and concepts

- **Boundary value:** the first, last, or Nth value under a declared ordering.
- **Current-row frame:** a frame whose upper boundary stops at the current row.
- **Full-partition frame:** a frame extending through
  `UNBOUNDED FOLLOWING`.

## Worked example / walkthrough

Take customer 1's five orders, dated in order with amounts 240.20, 417.94, 601.73, 1,155.92 and 105.84. With only `ORDER BY o.order_date, o.order_id`, `LAST_VALUE(total_amount)` on the second row sees rows one and two and returns 417.94, its own amount. With the full frame, all five rows return 105.84, the amount of the last order. `FIRST_VALUE` gives 240.20 on every row under either frame.

## Practice assumptions and review method

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Failure to watch for:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Review loop:** for one partition, write the expected first and last values by hand before running, then check that every row in that partition repeats the same pair. Expect the pair to match `MIN` and `MAX` only when the window is ordered by the reported value itself, as in Exercise 2.

## Exercises

Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.

Before each query, name the partition, the ordering and the frame the window needs, and write the first and last values you expect for one small partition, such as customer 1's orders or one order's payments. After running, check that partition first.

1. **Query writing:** Show every order with the customer's first and last order timestamps.
   **Anticipate:** for customer 1, which `order_date` should every row show as last?
   **Progressive hint:** Use one full-partition frame from unbounded preceding through unbounded following.
   **Inputs/evidence:** For sql-20 Exercise 1, read from `orders` and return, for every order, its customer's first and last `order_date` with `FIRST_VALUE` and `LAST_VALUE` over a named window partitioned by `customer_id`, ordered by `order_date, order_id`, with the frame `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
   **Expected result/shape:** For sql-20 Exercise 1, return 4,362 rows, one per order, where both dates stay constant within each of the 438 customers; customer 1's five rows all show order 1's date as `first_order_date` and order 5's date as `last_order_date`. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-20 Exercise 1, confirm 4362 rows and compare them with `SELECT customer_id, MIN(order_date), MAX(order_date) FROM orders GROUP BY customer_id` (438 customers): no row may differ. With the default frame instead, `LAST_VALUE` returns each row's own `order_date` on all 4362 rows.
2. **Query writing:** Show each product with the cheapest and most expensive price in its category.
   **Anticipate:** ordered by price, will the first value equal `MIN(price)`?
   **Progressive hint:** Order by price and use a full frame; values tie without needing row identity.
   **Inputs/evidence:** For sql-20 Exercise 2, read from `products` and show each product with the lowest and highest `price` in its `category`, using `FIRST_VALUE` and `LAST_VALUE` over a window ordered by `price, product_id` with a full frame.
   **Expected result/shape:** For sql-20 Exercise 2, return 300 rows, one per product, with two values per category; `Apparel` rows all show 10.37 and 119.15, `Books` rows show 12.22 and 121.00, and `Sports` rows show 11.85 and 120.63. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-20 Exercise 2, confirm 300 rows and compare the two window columns with `SELECT category, MIN(price), MAX(price) FROM products GROUP BY category`; for example, every `Apparel` row must show 10.37 and 119.15.
3. **Query writing:** Compare every payment with the first and last payment amount for its order.
   **Anticipate:** most orders have a single payment; what do the first and last columns show for those?
   **Progressive hint:** Partition by order, order by timestamp/payment ID, and keep the full frame.
   **Inputs/evidence:** For sql-20 Exercise 3, read from `payments` and compare every payment with the first and last payment `amount` of its order, using a window partitioned by `order_id`, ordered by `payment_date, payment_id`, with a full frame.
   **Expected result/shape:** For sql-20 Exercise 3, return 3,836 rows, one per payment; on the 3,142 single-payment orders both window columns repeat the payment's own `amount`, while order 10's two payments show a first amount of 71.72 and a last of 71.71. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
   **Verify:** For sql-20 Exercise 3, confirm 3836 rows, one per `payment_id`; 3489 orders have payments, 347 of them have two payments, and only 20 orders have a first amount that differs from the last, so check one of those 20 orders by hand.
4. **Prediction:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
   **Anticipate:** write both output columns for all three rows before running.
   **Progressive hint:** The default ends at the current row; explicit following reaches the true last row.
   **Inputs/evidence:** For sql-20 Exercise 4, apply `LAST_VALUE(value)` to the three-row `VALUES` fixture `(10), (20), (30)` twice: once over `ORDER BY value` with the default frame, and once with `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
   **Expected result/shape:** For sql-20 Exercise 4, return three rows: values 10, 20, and 30 with `default_last_value` 10, 20, and 30 and `partition_last_value` 30 on every row. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
   **Verify:** For sql-20 Exercise 4, check by hand that the default frame stops at the current row, so `default_last_value` repeats `value`, while the full frame reaches 30. Add `(NULL::int)` to the fixture; ascending order puts `NULL` last, so all four rows must then show `NULL` as `partition_last_value`, while the first three keep `default_last_value` 10, 20, and 30.
5. **Debugging:** Return one first and one last order per customer without using window output as an accidental duplicate report.
   **Anticipate:** how many rows does the query return without `DISTINCT`?
   **Progressive hint:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.
   **Inputs/evidence:** For sql-20 Exercise 5, read from `orders`, compute each customer's first and last `order_id` with full-frame `FIRST_VALUE` and `LAST_VALUE` windows ordered by `order_date, order_id` in the CTE `annotated`, then return one row per customer with `SELECT DISTINCT`.
   **Expected result/shape:** For sql-20 Exercise 5, return 438 rows, one per customer with orders; customer 1 shows orders 1 and 5, customer 2 shows 6 and 11, and customer 500 shows 4353 and 4362. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
   **Verify:** For sql-20 Exercise 5, confirm 438 rows, one per customer with orders, equal to `SELECT COUNT(DISTINCT customer_id) FROM orders`; without `DISTINCT`, the same query returns 4362 rows, one per order, with each customer's values repeated.
6. **Extension:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
   **Anticipate:** which order ID comes back for customer 1?
   **Progressive hint:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.
   **Inputs/evidence:** For sql-20 Exercise 6, keep one row per customer from the 4,362 `orders` rows with `SELECT DISTINCT ON (o.customer_id)`, where `ORDER BY o.order_date DESC, o.order_id DESC` decides which row survives.
   **Expected result/shape:** For sql-20 Exercise 6, return 438 rows, one latest order per customer with orders; customer 1 returns order 5 for 105.84, customer 2 returns order 11 for 680.50, and customer 500 returns order 4362 for 951.76. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-20 Exercise 6, confirm 438 distinct `customer_id` values, that every `order_id` equals the `last_order_id` from Exercise 5, and that the kept `total_amount` values add up to 252375.44. Inside a rolled-back transaction, set order 5's `order_date` to order 4's; customer 1 must still return order 5 because `o.order_id DESC` breaks the tie, and changing that key to `o.order_id ASC` must return order 4 for 1155.92.

## Common mistakes and how to recover

- **Leaving out the frame on `LAST_VALUE`:** with only `ORDER BY` in the window, Example 1's `last_order_amount` repeats each row's own `total_amount`. Add `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, or declare it once in a named `WINDOW` as the solutions do.
- **Reading "first" as "smallest":** `FIRST_VALUE(total_amount)` ordered by date is the earliest order's amount. Customer 1's is 240.20, while the smallest is 105.84.
- **Ties in the ordering:** with the default `RANGE` frame, tied rows are peers and all see the last of them. Ordering `(20, 'b')` and `(20, 'c')` by the number alone, `LAST_VALUE(tag)` shows `c` on both rows. Add a unique tie-breaker such as `order_id` so first and last always point at one row.
- **Collapsing to one row per customer with `DISTINCT` on the wrong columns:** `DISTINCT` removes duplicates only when every selected column repeats. Keep a per-order column such as `order_date` in the list and you are back to 4,362 rows.
- **`DISTINCT ON` with a mismatched sort:** `ORDER BY o.order_date DESC` alone fails with `SELECT DISTINCT ON expressions must match initial ORDER BY expressions`; the `DISTINCT ON` key must lead the `ORDER BY`.

When `ON_ERROR_STOP` ends the run, correct the first error and rerun the file from the top; the study guide has notes on [what to do after a failed run](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does “last” mean last so far or last in the complete partition?
- Why does `LAST_VALUE` with only `ORDER BY` in its window return the last peer of the current row instead of the partition's last row?

## Next step

Continue to [Day 21; distribution functions](day21_distribution_functions.md).

## Deep dive and reference

Learning objectives
- Extract first/last values within ordered partitions
- Use frame clauses to avoid surprising LAST_VALUE behavior
- Compute baselines and end-of-period values side-by-side

Why this matters
Anchoring a row against a starting or ending value supports normalization (e.g., index to 100), growth from baseline, and end-of-period reporting.

Core concepts and deep dive
- FIRST_VALUE(expr) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) reliably gives the partition’s first value.
- LAST_VALUE requires an appropriate frame. The default frame stops at the current row's last tied peer, so with unique ordering keys it returns the current row's own value. Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING to get the true last value.
- NTH_VALUE(expr, n) generalizes to the nth ordered value.

Patterns
- Normalize to first: x / NULLIF(FIRST_VALUE(x) OVER (...),0).
- Compare current to last: current - LAST_VALUE(x) OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING).

Pitfalls
- Forgetting to extend the frame for LAST_VALUE yields row’s current, not partition last.
- Non-deterministic ordering for duplicates; add tiebreakers.

Further reading
- FIRST/LAST/NTH: https://www.postgresql.org/docs/17/functions-window.html#FUNCTIONS-WINDOW-TABLE

## Ask an AI tutor about this lesson

This lesson does not require a tutor. If you use one, ask it what Example 1 prints for customer 1 without the frame clause, and check the answer in `psql` before moving on. The study guide explains [how to work with an AI tutor](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) so that it asks questions instead of writing the query for you.

```text
Tutor me through sql-20: FIRST_VALUE, LAST_VALUE, and Window Frames.

I have completed the direct catalog prerequisite: `sql-19`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
- Answer-free learner SQL: sql/postgres-60day/day20_first_last_value.sql

Key terms to teach in context: Boundary value, Current-row frame, Full-partition frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Order a customer's orders by date and compare default `LAST_VALUE(total_amount)` with the same function over `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`. The default often returns the current row's value; the full frame exposes the true final value.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-20/ working copy. Never point setup, reset, DDL, or DML
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
