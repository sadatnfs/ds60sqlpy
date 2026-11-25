# Day 07: Week 1 Project: From Questions to Queries (Companion Guide)

## How to run this lesson

Launch `./classroom`, pick PostgreSQL, open **sql-07** and press **Whole SQL lesson (psql)**. `psql` sends the file to `advanced_sql_training`, where it opens a transaction, sets `search_path` to `training`, prints a single starter report (net revenue, buyers and revenue per buyer for each country and product category over the last 90 days) and closes with `ROLLBACK`. The six project prompts sit underneath as comments, ready for your queries.

Type your answers into
`.learning/sql/sql-07/lesson/workspace/sql/postgres-60day/day07_week1_project.sql`,
each under its prompt and above the final `ROLLBACK`. The starter report filters on `now() - interval '90 days'`, so its numbers shift as the loaded data ages; the exercises read the whole history and stay fixed. A typo in Exercise 3 stops the run there and hides Exercises 4 to 6, so fix the earliest error first.

Classroom loading and resets: [study guide steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). Notebook users: [contributor route](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 06; set operations](day06_set_operations.md) and the
  joins and aggregates from Days 01-05
- **Artifacts:** [learner SQL](../day07_week1_project.sql) ·
  [solution reasoning](../solutions/day07_solutions.md) ·
  [executable solution](../solutions/day07_solutions.sql)

## A beginner's mental model for this lesson

This week's project asks one question in six shapes: what does a single output row stand for, and can you prove its numbers? That first half is the **report grain**. The starter report's grain is one country and one category, so 7 countries times 6 categories gives 42 rows; Brazil is missing because its 62 customers never ordered, and `LIMIT 50` therefore trims nothing.

The proof is **reconciliation**: an independent number your result must add back to. Every exercise has one. The five status rows of Exercise 1 must sum to 4,362 orders and 2,355,646.89 in stored revenue; Exercise 3 must return all 500 customers; Exercise 5's months must add to the same two totals; Exercise 6 prints the raw counts (500, 4,362, 13,085, 3,836) that the others lean on.

An **allocation rule** matters as soon as a shared amount meets a finer dimension. In this fixture 347 orders were paid in two parts, each part with a different method. Report revenue by payment method and those orders land in two method rows; without a stated rule (split by payment amount, or credit the first method) the same revenue is counted twice. Exercise 4 sidesteps the question by reducing payments to one row per order before joining.

## Two worked SQL examples

### Example 1

```sql
WITH recent_orders AS (
  SELECT
    *
  FROM
    orders
  WHERE
    order_date >= now() - interval '90 days'
),
line AS (
  SELECT
    ro.order_id,
    ro.customer_id,
    c.country,
    p.category,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
FROM
  recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT
  country,
  category,
  ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT customer_id) AS buyers,
  ROUND(SUM(line_revenue) / NULLIF (COUNT(DISTINCT customer_id), 0), 2) AS rev_per_buyer
FROM
  line
GROUP BY
  country,
  category
ORDER BY
  revenue DESC,
  country,
  category
LIMIT 50;
```

**How to read it:** `recent_orders` keeps orders from the last 90 days, measured from the moment you run it. `line` joins those orders to their customers, order lines and products, so it holds one row per order line carrying the buyer's country and the product's category. The outer query groups the lines by country and category, sums net line revenue and counts each buyer once with `COUNT(DISTINCT customer_id)`. `NULLIF` turns a zero buyer count into NULL so the division could never fail, although every group that exists has at least one buyer.

**Expected result/shape:** On the load used here the window holds 807 orders from 290 buyers and 2,448 order lines worth 437,431.95. They form 42 country and category groups, all of which fit under `LIMIT 50`. US Home leads with 13,627.14 from 29 buyers (469.90 each), followed by CA Apparel at 13,524.80; CA Beauty is last at 7,627.64. Because the window slides with the clock, rerunning on a later day returns smaller figures; the 42-row shape holds as long as every country keeps buying in every category.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH recent_orders AS (
  SELECT
    *
  FROM
    orders
  WHERE
    order_date >= now() - interval '90 days'), line AS (
    SELECT
      ro.order_id,
      ro.customer_id,
      c.country,
      p.category,
      (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
    FROM
      recent_orders ro
      JOIN customers c ON c.customer_id = ro.customer_id
      JOIN order_items oi ON oi.order_id = ro.order_id
      JOIN products p ON p.product_id = oi.product_id
)
  SELECT
    country,
    category,
    ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT customer_id) AS buyers,
  ROUND(SUM(line_revenue) / NULLIF (COUNT(DISTINCT customer_id), 0), 2) AS rev_per_buyer
FROM
  line
GROUP BY
  country,
  category
ORDER BY
  revenue DESC,
  country,
  category
LIMIT 50;
```

**How to read it:** This variant is only in the guide; the learner file runs the report itself. Paste it as an **SQL snippet** to see how PostgreSQL executes the query without fetching any rows. Both CTEs disappear into the plan: `recent_orders` becomes a `Filter` on the scan of `orders`, and `line` becomes three hash joins.

**Expected result/shape:** About 21 plan lines. From the bottom: `Seq Scan on orders` with the 90-day filter, hashed and joined to `order_items`, then to `customers`, then to `products`. A `Sort` on country, category and customer feeds a `GroupAggregate`, because `COUNT(DISTINCT customer_id)` needs each group's buyers in order. A second `Sort` puts revenue first, and `Limit` sits on top. Exact node choices can change with table sizes and PostgreSQL version.

## Learning objectives

- Translate a report request into grain, joins, filters, aggregates, and
  validation queries.
- Prevent payment-to-line fanout and document an allocation policy.

## Vocabulary and concepts

- **Report grain:** the dimensions represented by one output row.
- **Reconciliation:** comparing a complex result with an independent trusted
  total or count.
- **Allocation rule:** a declared policy for assigning a shared amount across
  multiple categories or methods.

## Worked example / walkthrough

Build the report in checkpoints. First reduce order lines to net revenue per order and category, then reduce payments to one row per order and method, join those two stable inputs, and only then roll up to country, category and method. Check the revenue total at each checkpoint before adding a cohort month, because a new dimension can hide a fanout that already happened.

## Practice assumptions and review method

- **Focus:** Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
- **Assumptions:** Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
- **Failure to watch for:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
- **Review loop:** write the control total you expect beside each query (4,362 orders, 500 customers or 2,355,646.89), run it, and compare before moving to the next prompt.

## Exercises

Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.

Do the prompts in order: Exercises 1 to 3 each read one or two tables, Exercise 4 is the fanout trap, and Exercise 6 prints the raw row counts the other answers should agree with.

1. **Query writing:** Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
   **Progressive hint:** Aggregate orders at status grain and round only displayed monetary values.
   **Guess first:** five statuses hold roughly equal order counts; will `customer_count` across the five rows add to 438 buyers or to far more?
   **Inputs/evidence:** For sql-07 Exercise 1, group the 4,362 `orders` rows by `status`; there are five statuses, `placed` and `shipped` with 873 orders each and `delivered`, `paid`, and `returned` with 872 each.
   **Expected result/shape:** For sql-07 Exercise 1, return 5 rows, one per status, led by `paid` with 872 orders, 432 customers, and 478068.36 revenue, and ending with `returned` at 468083.26. The final columns are `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`. The final order is `revenue DESC, o.status`.
   **Verify:** For sql-07 Exercise 1, confirm the five `order_count` values sum to 4362 and the five `revenue` values sum to 2355646.89, the same as `SELECT ROUND(SUM(total_amount), 2) FROM orders`. Inside a rolled-back transaction, set order 21's status to `cancelled`; the result must grow to 6 rows, with `cancelled` showing 1 order and `paid` dropping to 871.
2. **Query writing:** Return the 20 products with the highest net line revenue.
   **Progressive hint:** Aggregate order items by product before ranking; use product ID as tie-breaker.
   **Guess first:** does any product outside the catalog's top 40 IDs make the list, given that higher-numbered products carry higher prices?
   **Inputs/evidence:** For sql-07 Exercise 2, join the 13,085 `order_items` rows to `products`, sum `unit_price * quantity * (1 - discount)` per product across the 275 products that have sold, and keep the top 20.
   **Expected result/shape:** For sql-07 Exercise 2, return 20 rows, one per product, from product 271 (Apparel, 17643.20) down to product 260 (Electronics, 15292.80). The final columns are `product_id`, `name`, `category`, and `net_revenue`. The final order is `net_revenue DESC, p.product_id`.
   **Verify:** For sql-07 Exercise 2, confirm 20 distinct `product_id` values with `net_revenue` never rising from one row to the next. Rerun with `LIMIT 21`; the only added row must be product 231 at 15275.20, which is below product 260, so the cutoff falls between two different values rather than inside a tie.
3. **Query writing:** Create a customer summary that retains customers with no orders.
   **Progressive hint:** Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
   **Guess first:** which country fills the bottom of this list, and what does `order_count` show for those rows?
   **Inputs/evidence:** For sql-07 Exercise 3, `LEFT JOIN` the 500 `customers` rows to `orders`, count `o.order_id` and sum `total_amount` per customer, and turn a missing sum into 0 with `COALESCE`.
   **Expected result/shape:** For sql-07 Exercise 3, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21); the 62 customers without orders sort last with 0 orders and a 0 total. The final columns are `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`. The final order is `stored_order_total DESC, c.customer_id`.
   **Verify:** For sql-07 Exercise 3, confirm the `order_count` column sums to 4362, `stored_order_total` sums to 2355646.89, and exactly 62 rows show 0 orders. An inner join must return only 438 rows, and counting `*` instead of `o.order_id` must wrongly give those 62 customers an `order_count` of 1.
4. **Debugging:** Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
   **Progressive hint:** Aggregate each detail table to order grain first, then join the one-row-per-order relations.
   **Guess first:** after rounding, how large can `storage_difference` get when every stored total was computed from the same lines?
   **Inputs/evidence:** For sql-07 Exercise 4, pre-aggregate `order_items` to one `line_total` per order and `payments` to one `paid_total` per order, then join both to the 4,362 `orders` rows, with `LEFT JOIN` for payments because 873 orders have none.
   **Expected result/shape:** For sql-07 Exercise 4, return 4,362 rows, one per order; every `storage_difference` rounds to 0.00 (the largest raw gap is 0.0045), while 1,072 rows have a nonzero `unpaid_balance` of up to 1432.49. The final columns are `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`. The final order is `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
   **Verify:** For sql-07 Exercise 4, confirm 4,362 distinct `order_id` values and that the 1,072 nonzero balances split into 873 orders with `paid_total` 0.00 and 199 paid orders whose payments differ from `total_amount`. Joining raw `order_items` and `payments` to `orders` without pre-aggregation returns 13,432 rows and inflates the summed `total_amount` to 8673949.32.
5. **Prediction:** Build a monthly order trend and explain which months are absent rather than zero.
   **Progressive hint:** Grouping observed orders alone cannot create empty calendar months.
   **Guess first:** is the newest month as busy as the one before it, and why might it not be?
   **Inputs/evidence:** For sql-07 Exercise 5, read from `orders`, group by `date_trunc('month', order_date)`, and return each month's `order_count` and `stored_revenue` (`SUM(total_amount)` rounded to 2 places).
   **Expected result/shape:** For sql-07 Exercise 5, return 46 rows, one per calendar month with orders, from 2023-02-01 with 2 orders to the current month, which has 151 orders on a freshly loaded fixture. The final columns are `order_month`, `order_count`, and `stored_revenue`. The final order is `order_month`.
   **Verify:** For sql-07 Exercise 5, confirm that `order_month` is unique, that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders` (4362), and that the monthly `stored_revenue` values add up to `SELECT ROUND(SUM(total_amount), 2) FROM orders` (2355646.89).
6. **Extension:** Create a compact one-row audit of customer, order, item, and payment coverage.
   **Progressive hint:** Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
   **Guess first:** you already know four of the five numbers from earlier prompts; which one is new?
   **Inputs/evidence:** For sql-07 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Compute `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-07 Exercise 6, return one row: 500 customer rows, 4,362 order rows, 13,085 order item rows, 3,836 payment rows, and 62 customers without orders. The final columns are `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
   **Verify:** For sql-07 Exercise 6, confirm each value equals its own standalone `COUNT(*)`, and that 62 matches Exercise 3's count of zero-order customers. Inside a rolled-back transaction, insert one customer with no orders; the result must stay one row, with `customer_rows` at 501 and `customers_without_orders` at 63.

## Common mistakes and how to recover

- **Joining payments to order lines directly:** `order_items JOIN payments` yields 10,816 rows instead of 13,085 lines. The 873 placed orders vanish (no payments) while the lines of the 347 split-payment orders appear twice, and revenue lands at 1,926,711.90. Aggregate each side to one row per order first, as Exercise 4 does.
- **Counting buyers with `COUNT(*)`:** in the starter report that counts order lines, 2,448 of them, not the 290 people who bought. Buyers need `COUNT(DISTINCT customer_id)`.
- **Turning every NULL into zero:** in Exercise 3 a customer with no orders genuinely spent 0, so `COALESCE` is right. Wrapping `latest_order_date` or an average in the same fallback would invent a date or an average for 62 people who have none.
- **Reading Exercise 5 as a calendar:** grouping orders returns only months that have orders. On this load all 46 months from February 2023 to November 2026 have some, but a quiet month would simply be missing rather than show 0.
- **Cutting a ranking on ties:** `ORDER BY net_revenue DESC LIMIT 20` with no `product_id` could pick a different 20th product on another run if two products ever tie.

When a run stops on an error or a table is missing, the study guide's [recovery steps](../../STUDY-GUIDE.md#recover-from-common-failures) apply.

## Self-check

- Can one order contribute to several payment-method rows, and if so, is its
  revenue allocation explicit?
- Are the 90-day boundary, unpaid-order policy, and report grain documented?

## Next step

Continue to [Day 08; scalar and inline subqueries](day08_scalar_inline_subqueries.md).

## Deep dive and reference

Goal
- Extend the starter report of last-90-day revenue and buyers by country and
  category using the joins, aggregates, and set reasoning from Days 01-06.

Deliverable checklist
- Use the six prompts above as the project acceptance checklist. They cover
  KPI grain, product and customer coverage, fanout-safe reconciliation,
  missing months, and a compact population audit.

Further extension: payment ambiguity
- `payments` can contain multiple rows per order. Joining raw payments to raw
  order lines can repeat revenue. Decide whether the report is payment revenue
  (`payments.amount`) or order-line revenue allocated to a method, and
  pre-aggregate to one row per order/method before joining.
- An order with split methods can legitimately appear in more than one method
  row. State the allocation rule rather than silently duplicating order revenue.

Checklist
1) Preserve the starter report's 90-day scope.
2) Validate each join and aggregation with order counts and revenue
   reconciliation.
3) Confirm how unpaid orders and split payments are represented.
4) Document cohort and payment-method assumptions beside the query.

Rubric
- Correct grain, no accidental payment fanout, reproducible date logic, clear
  assumptions, and readable SQL.

## Ask an AI tutor about this lesson

You can finish this project without a tutor. If you want one, paste the prompt below and ask it to test your allocation rule: how should an order paid half by card and half by PayPal appear in a revenue-by-method report? Keep `solutions/` closed until you have an answer; see [tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-07: Week 1 Project: From Questions to Queries.

I have completed the direct catalog prerequisite: `sql-06`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day07_week1_project.md
- Answer-free learner SQL: sql/postgres-60day/day07_week1_project.sql

Key terms to teach in context: Report grain, Reconciliation, Allocation rule. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build the report in checkpoints: aggregate net line revenue to order/category, reduce payments to the declared order/method grain, join those stable inputs, and only then roll up country, category, and method. Reconcile revenue before adding cohort month so a new dimension cannot hide fanout.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-07/ working copy. Never point setup, reset, DDL, or DML
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
