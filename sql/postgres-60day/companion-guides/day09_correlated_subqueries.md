# Day 09 — Correlated Subqueries and EXISTS (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 08 — scalar and inline subqueries](day08_scalar_inline_subqueries.md)
- **Artifacts:** [learner SQL](../day09_correlated_subqueries.sql) ·
  [solution reasoning](../solutions/day09_solutions.md) ·
  [executable solution](../solutions/day09_solutions.sql)

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

## Exercises

Complete the prompts in the [learner SQL](../day09_correlated_subqueries.sql).
Implement one exclusion with `NOT EXISTS` and test it against a nullable-key
counterexample before considering `NOT IN`.

## Self-check

- Does the outer result retain one row per intended entity?
- Can you explain the `NULL` hazard of `NOT IN` and why `NOT EXISTS` avoids it?

## Next step

Continue to [Day 10 — data modification with subqueries](day10_dml_with_subqueries.md).

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

Exercises from the learner script
1) Find customers with any order over 1,000 using a correlated `EXISTS`.
2) Find products never purchased using correlated `NOT EXISTS`.

Use `orders.total_amount > 1000` for the first prompt. For the second, correlate
`order_items.product_id` to the outer `products.product_id`; do not use
`NOT IN`, whose NULL behavior is less robust.

Further reading
- EXISTS: https://www.postgresql.org/docs/current/functions-subquery.html
