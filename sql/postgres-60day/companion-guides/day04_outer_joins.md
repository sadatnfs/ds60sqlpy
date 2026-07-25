# Day 04 — OUTER JOINs: Preserving Unmatched Rows (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 03 — inner joins](day03_inner_joins.md)
- **Artifacts:** [learner SQL](../day04_outer_joins.sql) ·
  [solution reasoning](../solutions/day04_solutions.md) ·
  [executable solution](../solutions/day04_solutions.sql)

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

## Exercises

Complete the prompts in the [learner SQL](../day04_outer_joins.sql). For one
result, report both the preserved-entity count and the matched-fact count.

## Self-check

- Do entities with zero matching facts remain visible when the question
  requires complete coverage?
- Can you explain why `COUNT(*)` and `COUNT(right_table.id)` differ after a
  left join?

## Next step

Continue to [Day 05 — cross and self joins](day05_cross_self_joins.md).

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

Exercises from the learner script
1) Identify orders with no payments and payments without orders.
2) Find products that were never purchased.
3) Find customers with no orders in the last 90 days.

The setup foreign key means an ordinary `payments` row without an order cannot
exist. Keep that side of exercise 1 as a reconciliation check that should return
zero unless constraints were bypassed in imported data.

Further reading
- Outer joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM
