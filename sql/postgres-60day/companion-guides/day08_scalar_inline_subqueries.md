# Day 08 — Scalar and Inline Subqueries (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 07 — Week 1 project](day07_week1_project.md)
- **Artifacts:** [learner SQL](../day08_scalar_inline_subqueries.sql) ·
  [solution reasoning](../solutions/day08_solutions.md) ·
  [executable solution](../solutions/day08_solutions.sql)

## Learning objectives

- Use a scalar subquery only where zero or one value is guaranteed.
- Compare subquery forms with equivalent joins for correctness and work done.

## Vocabulary and concepts

- **Scalar subquery:** a nested query used where one value is expected.
- **Inline view:** a subquery in `FROM` that behaves like a temporary relation.
- **Uncorrelated subquery:** a nested query that does not reference the outer
  row.

## Worked example / walkthrough

For each customer, the learner needs one first-order date. `MIN(order_date)`
returns exactly one value, including `NULL` when no order exists. Contrast that
with selecting raw order dates, which can raise “more than one row returned by a
subquery used as an expression.”

## Exercises

Complete the prompts in the [learner SQL](../day08_scalar_inline_subqueries.sql).
Rewrite one scalar aggregate as a grouped derived table plus `LEFT JOIN` and
compare outputs.

## Self-check

- Can every scalar subquery prove its one-value contract without an arbitrary
  `LIMIT 1`?
- Are customers with no matching orders handled deliberately?

## Next step

Continue to [Day 09 — correlated subqueries and EXISTS](day09_correlated_subqueries.md).

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

Exercises from the learner script
1) For each country, return its largest single `orders.total_amount`.
2) For each customer, show the first order date via a scalar subquery.

Exercise 2 must return exactly one scalar value per customer. `MIN(order_date)`
is deterministic and returns `NULL` for a customer with no orders.

Further reading
- Subqueries: https://www.postgresql.org/docs/current/sql-select.html#SQL-SELECT-SUBQUERIES
