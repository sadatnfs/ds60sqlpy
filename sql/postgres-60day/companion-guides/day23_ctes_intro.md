# Day 23: Common Table Expressions (CTEs) Introduction (Companion Guide)

## How to run this lesson

Choose **sql-23** in `./classroom` (PostgreSQL track) and press **Whole SQL
lesson (psql)**. The classroom copies the lesson to
`.learning/sql/sql-23/lesson/workspace/sql/postgres-60day/day23_ctes_intro.sql`
and runs it against `advanced_sql_training`. The learner file only reads:
both statements are the same two-stage revenue pipeline, first as rows and
then under `EXPLAIN (COSTS OFF)`, between `BEGIN` and `ROLLBACK`. The `psql`
transcript therefore holds one 20-row table followed by a plan tree. The
solution's Exercise 6 is the only place this lesson writes, and it undoes its
own update with a savepoint. Saving, resetting and launcher help live in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

A notebook lets you run each CTE body as its own cell before adding the next
stage ([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-23
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 22; advanced windows](day22_advanced_windows.md)
- **Artifacts:** [learner SQL](../day23_ctes_intro.sql) ·
  [solution reasoning](../solutions/day23_solutions.md) ·
  [executable solution](../solutions/day23_solutions.sql)

## A beginner's mental model for this lesson

A common table expression gives a subquery a name for the length of one
statement. `WITH order_lines AS (...)` does not create a table; it lets the
next stage say `FROM order_lines` instead of nesting the whole aggregate in
parentheses. The value of the name is that you can state its grain and check
it on its own.

The lesson's pipeline has three stages, and each one has a different grain:

- `order_lines` joins 4,362 orders to their 13,085 `order_items` rows and
  groups back to one row per order. Every order has at least one item, so the
  stage returns exactly 4,362 rows.
- `top_customers` sums those order totals per customer: 438 rows, because 62
  of the 500 customers (all of them in Brazil) never ordered.
- The final `SELECT` sorts by lifetime revenue with `customer_id` as the tie
  breaker and keeps 20 rows.

Two separate questions apply to every CTE. The logical one: what is one row,
and is its key unique? The physical one: does PostgreSQL compute the CTE
separately or fold it into the outer query? Since PostgreSQL 12, a
side-effect-free CTE referenced once is inlined, so Example 2's plan shows two
stacked `HashAggregate` nodes and no CTE step at all. A CTE referenced twice,
like `category_revenue` in Exercise 2, is computed once and read through
`CTE Scan` nodes. `MATERIALIZED` and `NOT MATERIALIZED` override that default,
and Exercise 4 shows both plans side by side.

A data-modifying CTE (`UPDATE ... RETURNING` inside `WITH`) adds a third rule:
the rest of the statement still reads the snapshot taken before the update,
so the changed values are visible only through the `RETURNING` relation.

## Two worked SQL examples

### Example 1

```sql
WITH order_lines AS (
  SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id
),
top_customers AS (
  SELECT
    customer_id,
    SUM(order_total) AS lifetime_revenue
  FROM
    order_lines
  GROUP BY
    customer_id
)
SELECT
  tc.customer_id,
  tc.lifetime_revenue
FROM
  top_customers tc
ORDER BY
  lifetime_revenue DESC,
  tc.customer_id
LIMIT 20;
```

**How to read it:** Read the two CTEs top to bottom, then the outer
query. `order_lines` groups by `order_id` and `customer_id` together; including
`customer_id` in the key is safe because each order has one customer, and it
carries the customer forward without a second join. `top_customers` regroups
by `customer_id` alone, which is the grain change the lesson is about. The
outer query sorts by `lifetime_revenue DESC` and uses `tc.customer_id` to make
ties deterministic before `LIMIT 20`.

**Expected result/shape:** 20 customer rows. Customer 181 leads with
9,502.22 from 16 orders, then customer 12 (9,244.26) and customer 25
(9,196.96); the twentieth row is customer 259 at 8,760.17. The revenue column
is unrounded `numeric`, so expect long decimals in the transcript. Running
`SELECT COUNT(*) FROM order_lines` with the same CTE header should print
4,362, and the same check on `top_customers` should print 438.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH order_lines AS (
  SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id),
  top_customers AS (
    SELECT
      customer_id,
      SUM(order_total) AS lifetime_revenue
    FROM
      order_lines
    GROUP BY
      customer_id
)
  SELECT
    tc.customer_id,
    tc.lifetime_revenue
  FROM
    top_customers tc
  ORDER BY
    lifetime_revenue DESC,
    tc.customer_id
  LIMIT 20;
```

**How to read it:** `EXPLAIN (COSTS OFF)` prints the plan for the
Example 1 query without running it or showing cost estimates. Read the tree
from the innermost node outward: two sequential scans feed a `Hash Join` on
`order_id`, a `HashAggregate` keyed on `o.order_id` builds the order grain, a
second `HashAggregate` keyed on `o.customer_id` builds the customer grain, and
`Sort` plus `Limit` produce the top 20.

**Expected result/shape:** A 12-line plan tree, not customer rows.
Neither CTE name appears in it: there is no `CTE order_lines` step and no
`CTE Scan`, which is how you can tell both single-use CTEs were inlined. Add
`AS MATERIALIZED` to `order_lines` and the plan gains a `CTE order_lines`
section read by `CTE Scan on order_lines`, while the rows returned stay the
same.

## Learning objectives

- Decompose a query into named stages with an explicit grain at each stage.
- Explain when PostgreSQL may inline or materialize a non-recursive CTE.

## Vocabulary and concepts

- **CTE:** a statement-local named query introduced by `WITH`.
- **Inlining:** planner substitution of a CTE into the surrounding query.
- **Materialization:** evaluating and storing an intermediate relation before
  later use.

## Worked example / walkthrough

Trace `order_lines` at one row per order, then `top_customers` at one row per
customer, then the final top-N presentation. Run each CTE body independently
while developing and verify its key uniqueness before adding the next stage.

## Practice assumptions and review method

- **Focus:** Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability, not forced materialization, is the default goal.
- **Assumptions:** Each CTE declares its output grain. PostgreSQL inlines a side-effect-free CTE that is referenced once unless `MATERIALIZED` is requested; a CTE referenced more than once is materialized (computed once) by default.
- **Failure to watch for:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Review loop:** write the grain of each CTE as a comment above it, run
  `SELECT COUNT(*), COUNT(DISTINCT key)` against that stage alone, and only
  then add the next stage. For this fixture the counts to expect are 4,362
  orders, 438 ordering customers and 6 categories.

## Exercises

Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability, not forced materialization, is the default goal.

Exercises 1, 3 and 5 each build at least two stages, so write down the
row count you expect from every stage before running anything. Exercise 2 must
end with a single row, Exercise 4 with two rows holding the same count, and
Exercise 6 should leave `products` exactly as it found it.

1. **Query writing:** Build order-level net value in one CTE and summarize it by customer in the outer query.
   **Progressive hint:** Name the one-row-per-order grain before changing to customer grain.
   **Inputs/evidence:** For sql-23 Exercise 1, read `orders` joined to `order_items`, build the `order_values` CTE at one row per `order_id` with net value `unit_price * quantity * (1 - discount)`, then group that CTE by `customer_id`; `order_id` disappears in the outer aggregate.
   **Expected result/shape:** For sql-23 Exercise 1, expected output: 438 rows, one per ordering customer, led by customer 181 with 16 orders and 9502.22 of item-level net revenue. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
   **Verify:** For sql-23 Exercise 1, confirm `SUM(order_count)` is 4362 and matches `SELECT COUNT(*) FROM orders`, and that the unrounded revenue total equals `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12); then count joined rows for customer 181 without the CTE, `SELECT COUNT(*) FROM orders o JOIN order_items oi USING (order_id) WHERE o.customer_id = 181`, and see 50 item rows instead of 16 orders, which is the fanout the order-grain CTE prevents.
2. **Query writing:** Use one category-revenue CTE twice to return the highest category and total revenue.
   **Progressive hint:** A named aggregate can support multiple scalar reads without repeating the business formula.
   **Inputs/evidence:** For sql-23 Exercise 2, read `order_items` joined to `products`, aggregate net item revenue by `category` once in `category_revenue`, and read that CTE twice: once in a scalar subquery ordered by revenue then category with `LIMIT 1`, and once in a scalar `SUM`; there is no outer `FROM` or `GROUP BY`.
   **Expected result/shape:** For sql-23 Exercise 2, expected output: exactly one row, `top_category` `Sports` and `all_revenue` 2355647.12. The final columns are `top_category`, and `all_revenue`.
   **Verify:** For sql-23 Exercise 2, run the CTE body alone and confirm six category rows led by Sports at 397427.70 ahead of Electronics at 394424.39, and that they add to the same 2355647.12 as `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items`; then add `WHERE false` inside `category_revenue` and confirm the query still returns one row, now with both values NULL, because scalar subqueries over an empty CTE yield NULL rather than no row.
3. **Query writing:** Create staged payment reconciliation CTEs at order grain.
   **Progressive hint:** Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
   **Inputs/evidence:** For sql-23 Exercise 3, read `payments` (3836 rows for 3489 orders) and pre-aggregate them to one `paid_amount` per `order_id` in `paid`, then `LEFT JOIN` that CTE to all 4362 `orders` in `reconciled` and turn a missing payment into 0 with `COALESCE`.
   **Expected result/shape:** For sql-23 Exercise 3, expected output: 4362 rows, one per order; 873 orders have no payment, 199 more are partly paid, none is overpaid, and the first rows are orders 2029, 3129, and 3679 each with 1432.49 unpaid. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
   **Verify:** For sql-23 Exercise 3, confirm the row count equals `SELECT COUNT(*) FROM orders` (4362), that `SUM(paid_amount)` equals `SELECT SUM(amount) FROM payments` (1831900.81), and that the 873 zero-paid rows are exactly the `placed` orders; then join `payments` to `orders` without the `paid` CTE and see 4709 rows, because 347 orders have more than one payment.
4. **Prediction:** Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
   **Progressive hint:** Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
   **Inputs/evidence:** For sql-23 Exercise 4, read from `orders` through two side-effect-free CTEs that both keep `delivered` orders, one declared `AS MATERIALIZED` and one `AS NOT MATERIALIZED`, and count the rows each returns.
   **Expected result/shape:** For sql-23 Exercise 4, expected output: two rows, `materialized` and `not_materialized`, each with `row_count` 872. The final columns are `variant`, and `row_count`. The final order is `variant`.
   **Verify:** For sql-23 Exercise 4, confirm both `row_count` values are 872, equal to `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`; then run `EXPLAIN` on the query: the `MATERIALIZED` CTE appears as a separate `CTE materialized_orders` step read through a `CTE Scan`, while the `NOT MATERIALIZED` CTE is folded into a `Seq Scan on orders` with the status filter.
5. **Debugging:** Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
   **Progressive hint:** Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
   **Inputs/evidence:** For sql-23 Exercise 5, read `orders` and `order_items` into the order-grain CTE `order_values`, roll it up to one `customer_revenue` per customer, and only then join `customers` and group by `country`, giving each stage its own alias instead of a reused `total`.
   **Expected result/shape:** For sql-23 Exercise 5, expected output: 7 rows, one per country with orders, from FR at 343290.13 down to IN at 329081.73; BR's 62 customers place no orders, so BR is absent. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
   **Verify:** For sql-23 Exercise 5, confirm the seven values add to the item-level total `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12) within one cent of rounding, and that `SELECT country, COUNT(*) FROM customers GROUP BY country` lists eight countries; change the final join to `customers LEFT JOIN customer_revenue` and BR appears with a NULL revenue, which shows why the inner join drops it.
6. **Extension:** Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
   **Progressive hint:** The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
   **Inputs/evidence:** For sql-23 Exercise 6, read `products` in the `candidates` CTE to pick the three lowest `product_id` values (1, 2, 3, priced 10.37, 10.74, and 11.11), update only those rows in the data-modifying CTE `updated`, and read its `RETURNING` rows; `SAVEPOINT exercise_6` and `ROLLBACK TO SAVEPOINT` undo the change.
   **Expected result/shape:** For sql-23 Exercise 6, expected output: one summary row with `updated_rows` 3, `first_updated_product` 1, and `last_updated_product` 3. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
   **Verify:** For sql-23 Exercise 6, add `string_agg(price::text, ',' ORDER BY product_id)` to the outer query and confirm the returned new prices are 10.47, 10.85, and 11.22; after `ROLLBACK TO SAVEPOINT exercise_6`, `SELECT product_id, price FROM products WHERE product_id <= 3` must show 10.37, 10.74, and 11.11 again. With `LIMIT 0` in `candidates` the summary row still appears, with 0 updated rows and NULL first and last products.

## Common mistakes and how to recover

- **Expecting a CTE to make a query faster.** A single-use CTE is inlined, so
  Example 1 runs the same plan as the nested-subquery version. Splitting a
  query into stages is a readability decision; only `EXPLAIN` evidence shows
  whether forcing `MATERIALIZED` helps.
- **Joining detail rows before aggregating them.** Joining `orders` directly
  to `payments` gives 4,709 rows, because 347 orders have two payments, and
  `SUM(total_amount)` over that join reports 2,396,554.68 instead of
  2,355,646.89. Exercise 3 sums payments per order in its own CTE first.
- **Turning a left join into an inner join.** The 873 orders with no payment
  (every one has status `placed`) disappear if `paid` is joined with `JOIN`,
  and the largest unpaid balances go with them.
- **Reusing a generic column name in every stage.** If two CTEs both expose
  `total` and the final query joins them, PostgreSQL stops with
  `column reference "total" is ambiguous`. Exercise 5 names each measure for
  its grain: `order_value`, `customer_revenue`, `country_revenue`.
- **Reading an updated row back in the same statement.** Inside Exercise 6,
  a plain `SELECT price FROM products WHERE product_id = 1` placed in the same
  statement still returns 10.37, the pre-update value. Use the `RETURNING`
  rows instead.
- For the general recovery steps (count each stage, rerun the whole file after
  the first `psql` error), see
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Can later stages reference only columns deliberately exposed by earlier ones?
- Is `MATERIALIZED` or `NOT MATERIALIZED` used only for a measured reason?

## Next step

Continue to [Day 24; recursive CTEs](day24_recursive_ctes.md).

## Deep dive and reference

Learning objectives
- Rewrite subqueries as CTEs (WITH ...) to improve readability and reuse
- Understand evaluation order and CTE inlining/materialization in Postgres
- Structure multi-step analytical pipelines with clean, named stages

Why this matters
CTEs make complex queries understandable. By naming intermediate results, you reduce cognitive load and avoid repeating logic. Since PostgreSQL 12 the planner folds a side-effect-free, non-recursive CTE that is referenced once into the outer query, so you often get both clarity and performance.

Core concepts and deep dive
- Syntax: WITH name AS (subquery) SELECT ... FROM name ...; Multiple CTEs are comma-separated.
- Visibility: CTEs are visible only to the main query and to subsequent CTEs defined after them.
- Evaluation (Postgres specifics):
  - Before PostgreSQL 12, non-recursive CTEs were optimization fences (always materialized). Since 12, a side-effect-free CTE referenced once is inlined and planned like a subquery; one referenced more than once is still materialized by default.
  - `MATERIALIZED` and `NOT MATERIALIZED` (PostgreSQL 12 and later) override that default when a measured plan justifies it.
- Reuse: a side-effect-free CTE referenced once is normally inlined; one referenced more than once is materialized (computed once) by default. NOT MATERIALIZED forces inlining and can repeat the work; MATERIALIZED forces a separate computation even for one reference.

Walkthrough of the day’s script
- order_lines CTE aggregates order-level revenue by joining orders and order_items, producing one row per order_id and customer_id.
- top_customers CTE rolls order_lines up to lifetime_revenue per customer.
- The final SELECT orders customers by lifetime revenue and returns the top 20. This expresses a clear two-stage pipeline: lines → customers.

Design patterns
- “Stage and refine”: build granular CTEs (lines), then roll-ups (customers), then selections (top-N).
- “Filter early”: push selective WHERE predicates into earlier CTEs to reduce data volume in later stages.
- Parameterization with psql variables: WHERE order_date >= :'since'.

Pitfalls
- Overusing CTEs for tiny subqueries can hurt readability and prevent predicate pushdown if forced materialization.
- Forcing NOT MATERIALIZED on a heavy, multiply referenced CTE can repeat its work, and forcing MATERIALIZED on a single-use CTE can block predicate pushdown. Measure before overriding the default.

Further reading
- WITH queries: https://www.postgresql.org/docs/17/queries-with.html
- MATERIALIZED/NOT MATERIALIZED: https://www.postgresql.org/docs/17/queries-with.html#QUERIES-WITH-MATERIALIZED

## Ask an AI tutor about this lesson

A tutor can help you predict the row count of each CTE stage before you
run it; the prompt below points it at the guide and the answer-free learner
file only ([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-23: Common Table Expressions (CTEs).

I have completed the direct catalog prerequisite: `sql-22`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day23_ctes_intro.md
- Answer-free learner SQL: sql/postgres-60day/day23_ctes_intro.sql

Key terms to teach in context: CTE, Inlining, Materialization. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Trace `order_lines` at one row per order, then `top_customers` at one row per customer, then the final top-N presentation. Run each CTE body independently while developing and verify its key uniqueness before adding the next stage.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-23/ working copy. Never point setup, reset, DDL, or DML
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
