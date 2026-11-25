# Day 34: Query Optimization Techniques

## How to run this lesson

Open `./classroom`, select **sql-34** and run **Whole SQL lesson (psql)**.
The learner file runs one grouped report, one `EXPLAIN ANALYZE` and one
plain `EXPLAIN`, then rolls back. Edit your copy at
`.learning/sql/sql-34/lesson/workspace/sql/postgres-60day/day34_query_optimization.sql`;
it runs against `advanced_sql_training`. Launch details are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Every rewrite in this lesson is judged in two steps: first prove the new
query returns the same rows as the old one, then compare plans. Keep the
original query's output open in a second tab so the comparison is quick.

### Optional contributor notebook route

A notebook makes the side-by-side comparison of an original and a rewritten
query easier to keep
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-34
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 33; composite, covering, and partial indexes](day33_index_optimization_strategies.md)
- **Artifacts:** [learner SQL](../day34_query_optimization.sql) ·
  [solution reasoning](../solutions/day34_solutions.md) ·
  [executable solution](../solutions/day34_solutions.sql)

## A beginner's mental model for this lesson

Optimizing a query means removing work while the answer stays identical.
Both halves need evidence. The plan shows the work: rows read, rows thrown
away, loops repeated. A result comparison shows the answer did not change.
A rewrite that is faster but returns different rows is a different query.

The course seed makes the trade-offs concrete. A correlated subquery that
counts orders for each of the 500 customers runs its inner scan 500 times,
reading all 4,362 orders each time and discarding 4,353 of them. Grouping
`orders` once by `customer_id` produces 438 counts in one pass, and a
`LEFT JOIN` back to `customers` restores the 62 customers with no orders as
zeros. Those 62 are every customer in Brazil, so a rewrite that used an
inner join would silently drop a whole country from the report.

The learner file's third statement shows the same idea at a larger scale.
It sums `order_items.quantity` by product category for paid, shipped and
delivered orders. The plan filters `orders` to an estimated 2,617 rows
before joining, so only items of those orders reach the six-row
`HashAggregate`. The filter was written in `WHERE`, but the planner decided
where it runs.

## Two worked SQL examples

### Example 1

```sql
WITH filtered_orders AS (
  SELECT
    order_id,
    customer_id
  FROM
    orders
  WHERE
    order_date >= now() - interval '30 days'
)
SELECT
  c.country,
  COUNT(*)
FROM
  filtered_orders fo
  JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY
  c.country
ORDER BY
  COUNT(*) DESC;
```

**How to read it:** The CTE keeps orders from the last 30 days,
and the outer query counts them by customer country. PostgreSQL inlines
this CTE: the plan shows a `Seq Scan on orders` with the date filter
directly under a `Hash Join`, with no separate CTE step.

**Expected result/shape:** Seven rows, one per country, from
CA with 39 orders down to FR with 24; the counts add up to 209 recent
orders. Brazil is absent because its customers have never ordered. GB and
DE tie at 28, and `ORDER BY COUNT(*) DESC` has no second key, so those two
rows may appear in either order.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT
  o.order_id,
  o.customer_id
FROM
  orders o
WHERE
  o.order_date >= now() - interval '7 days';
```

**How to read it:** `EXPLAIN ANALYZE` runs the seven-day
query and reports the plan with actual counts. It selects only
`order_id` and `customer_id`, so each output row is narrow, but the table
still has to be read in full: there is no index on `order_date`.

**Expected result/shape:** A single `Seq Scan on orders`
node with an estimate of 23 rows and an actual count of 17, and `Rows
Removed by Filter: 4345`. Narrowing the projection did not reduce the
pages read; only an index or a smaller table could.

## Learning objectives

- Optimize one measured bottleneck while preserving result semantics.
- Reduce repeated work through early safe filtering, narrower projection, or
  pre-aggregation.

## Vocabulary and concepts

- **Baseline:** the controlled query, data, plan, and result used for comparison.
- **Predicate pushdown:** evaluating a safe filter closer to its source.
- **Semantic equivalence:** two queries returning the same defined result.

## Worked example / walkthrough

Capture a baseline and control totals, replace a repeated scalar aggregate with
one grouped relation, and join it back. Recheck keys and totals before comparing
plans; a faster query that silently drops zero-order customers is not an
optimization of the same requirement.

## Exercises

Complete these in the [learner SQL](../day34_query_optimization.sql):

1. Replace a scalar/correlated subquery with a join and compare plans.
   **Inputs/evidence:** For sql-34 Exercise 1, read `orders`, `order_items`, and `products` (50 `Electronics` products) and plan two forms of 'orders with an Electronics line' with `EXPLAIN (ANALYZE, BUFFERS)`: an `EXISTS` subquery and a `SELECT DISTINCT` join through `order_items` and `products`.
   **Expected result/shape:** For sql-34 Exercise 1, expected output: both forms return 2,187 orders, one per `order_id`; the `EXISTS` plan is a `Hash Semi Join`, and the join plan is a `Hash Join` under a `HashAggregate` for the `DISTINCT`. The final columns are `order_id`, and `order_date`.
   **Verify:** For sql-34 Exercise 1, confirm both forms return 2,187 rows without `EXPLAIN` and that the join without `DISTINCT` also returns 2,187, because no order has two Electronics lines; then, inside `BEGIN ... ROLLBACK`, insert a second Electronics line (product 116) into order 5 and confirm the plain join grows to 2,188 rows while the `EXISTS` and `DISTINCT` forms stay at 2,187.
2. Limit rows early without changing the result.
   **Inputs/evidence:** For sql-34 Exercise 2, read `orders` (4,362 rows) and `customers`, and plan two forms of the latest 100 orders with country: a join followed by `ORDER BY ... LIMIT 100`, and a `top_orders` CTE `AS MATERIALIZED` that limits `orders` to 100 rows before joining `customers`.
   **Expected result/shape:** For sql-34 Exercise 2, expected output: exactly 100 rows from each form on this load, newest first, starting with order 2258 and ending with order 2269; the plain plan joins all 4,362 orders before a `top-N heapsort`, while the CTE plan joins only the 100 kept orders. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
   **Verify:** For sql-34 Exercise 2, confirm the plain query `EXCEPT` the CTE query returns no rows, and that the 100 rows have 100 distinct `order_id` values; then, inside `BEGIN ... ROLLBACK`, move order 2258 to `order_date = '2000-01-01'` and confirm the CTE form now starts with order 745 and ends with order 910, the former 101st row.
3. Predict `MATERIALIZED` versus `NOT MATERIALIZED` planner freedom.
   **Inputs/evidence:** For sql-34 Exercise 3, run `EXPLAIN` on the same recent-orders count twice, once with `WITH recent AS MATERIALIZED (...)` and once with `AS NOT MATERIALIZED`, where `recent` keeps orders from the last 30 days and is joined to `customers`.
   **Expected result/shape:** For sql-34 Exercise 3, expected output: two plans. The `MATERIALIZED` plan computes `CTE recent` separately and reads it through a `CTE Scan on recent`; the `NOT MATERIALIZED` plan folds the date filter into a `Seq Scan on orders` under the join. Both queries return the same count.
   **Verify:** For sql-34 Exercise 3, run both queries without `EXPLAIN` and confirm that they return the same `count`; then confirm that only the `MATERIALIZED` plan contains a `CTE recent` node, and treat the estimated costs as plan evidence, not as a universal speed ranking.
4. Pre-aggregate items at order grain and verify totals.
   **Inputs/evidence:** For sql-34 Exercise 4, read `order_items` (13,085 lines, 39,257 units), sum `quantity` per order in the `item_totals` CTE (4,362 rows), then join `orders` and `customers` and group by `country`.
   **Expected result/shape:** For sql-34 Exercise 4, expected output: exactly 7 country rows, from IN with 5,479 units to FR with 5,711, with AU 5,529, CA 5,683, DE 5,687, GB 5,558, and US 5,610; BR is absent because its customers have no orders. The final columns are `country`, and `units`. The final order is `c.country`.
   **Verify:** For sql-34 Exercise 4, confirm the seven `units` add up to 39,257, the result of `SELECT SUM(quantity) FROM order_items`, and that summing `oi.quantity` straight through the three-way join gives the same seven rows; then, inside `BEGIN ... ROLLBACK`, insert a 3-unit line into order 1 (a US customer) and confirm only US changes, from 5,610 to 5,613.
5. Repair payment/item fanout.
   **Inputs/evidence:** For sql-34 Exercise 5, read `payments` (3,836 rows) into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep the first 20 orders.
   **Expected result/shape:** For sql-34 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have no payment and show `NULL` `paid_amount`, order 10 shows its two payments as 143.43, and order 17 shows 172.16 paid against 344.3105 of line revenue. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
   **Verify:** For sql-34 Exercise 5, confirm order 4 shows 1155.92 paid and 1155.9185 of revenue, while joining `payments` and `order_items` directly to `orders` inflates its `paid_amount` five times, to 5,779.60, because it has five item lines; then, inside `BEGIN ... ROLLBACK`, insert a second 240.20 payment for order 1 and confirm its `paid_amount` doubles to 480.40 while `line_revenue` stays 240.2000.
6. Replace nullable `NOT IN` logic with `NOT EXISTS`.
   **Inputs/evidence:** For sql-34 Exercise 6, read `customers` (500 rows) and test each `customer_id` against `orders` (438 distinct customers) with a correlated `NOT EXISTS`.
   **Expected result/shape:** For sql-34 Exercise 6, expected output: exactly 62 rows, customers 8, 16, 24, and every eighth id up to 496, all of them in `BR`. The final columns are `customer_id`. The final order is `c.customer_id`.
   **Verify:** For sql-34 Exercise 6, confirm 500 customers minus 438 distinct ordering customers equals the 62 returned rows; then append a `NULL` to the inner list with `UNION ALL SELECT NULL` and confirm `customer_id NOT IN (...)` now returns 0 rows while `NOT EXISTS` over the same list still returns 62.

Change one thing per experiment and reconcile results before timing.

## Self-check

- Are compared queries semantically identical at edge cases as well as typical
  rows?
- Does the evidence identify work removed rather than relying only on elapsed
  time?

## Next step

Continue to [Day 35; performance pitfalls](day35_avoiding_pitfalls.md).

## Deep dive and reference

## What you will learn

- Reduce rows and columns before expensive joins or aggregates.
- Replace repeated subquery work with set-based joins when semantics allow.
- Measure a rewrite rather than assuming it is faster.

## How the learner script uses the current schema

The script filters recent `orders` in a CTE before joining to `customers`,
projects only `order_id` and `customer_id` in a seven-day plan, and aggregates
`order_items.quantity` by `products.category` for successful order statuses.

PostgreSQL can inline many non-materialized CTEs, so writing a filter in a CTE
does not itself guarantee a faster plan. The value is a clear, correct query
shape that the optimizer can transform.

## Optimization loop

1. Capture `EXPLAIN (ANALYZE, BUFFERS)` for a safe baseline.
2. Identify excess rows, repeated loops, large sorts, or poor estimates.
3. Make one targeted change.
4. Reconcile keys, counts, and totals.
5. Compare plans under the same data and predicate.

## Two rewrites measured on the seed

The table compares the two forms of the first two answers. Both forms of
a pair return the same rows.

| Rewrite | Original plan | Rewritten plan |
|---|---|---|
| Orders with an Electronics line | `EXISTS` becomes a `Hash Semi Join`, 165 buffers, about 1.5 ms | `DISTINCT` join adds a `HashAggregate` over 2,187 rows, 165 buffers, about 1.8 ms |
| Latest 100 orders with country | join all 4,362 orders, then top-N sort, 80 buffers | sort orders alone, then 100 key lookups, 224 buffers |

Neither rewrite wins on this seed. PostgreSQL already turns `EXISTS` into
a semi-join, so the join form reads the same 165 buffers and only adds the
`HashAggregate` its `DISTINCT` needs. The second rewrite removes join work
but adds 53 index probes into `customers`, so it touches more buffers and
is not faster. That is still a useful result: it shows why each rewrite
has to be measured.

## Practice map

Each prompt above has a semantic check as well as a plan check. Run the
check first: if the rewrite returns different rows, its plan does not
matter yet.

## Pitfalls and validation

- The optimizer chooses physical join order; SQL text order is not a reliable
  tuning lever.
- Pushing a filter from `WHERE` into the nullable side of an outer join can
  change results.
- `DISTINCT` can hide join fanout. Fix grain instead of masking duplicates.
- A faster query that changes counts or totals is incorrect.

## Expanded practice lab

Prompts 3-6 make semantic equivalence the first optimization gate. Compare
`MATERIALIZED` and `NOT MATERIALIZED` as planner boundaries, then verify a
one-row-per-order pre-aggregation against the direct join with `EXCEPT` in both
directions.

When payments and line items are both many-to-one with orders, aggregate each
to order grain before combining them. Use `NOT EXISTS` for a NULL-safe anti-join;
`NOT IN` becomes unknown for every candidate if its subquery can return NULL.

## Ask an AI tutor about this lesson

A tutor can quiz you on whether two queries are equivalent. Paste an
original and a rewrite and ask it to find the input row that would make
them disagree
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-34: Query Optimization Techniques.

I have completed the direct catalog prerequisite: `sql-33`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
- Answer-free learner SQL: sql/postgres-60day/day34_query_optimization.sql

Key terms to teach in context: Baseline, Predicate pushdown, Semantic equivalence. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-34/ working copy. Never point setup, reset, DDL, or DML
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
