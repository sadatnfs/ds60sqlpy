# Day 05 — CROSS and SELF JOINs: Combinatorics and Relationships to Self (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 04 — outer joins](day04_outer_joins.md)
- **Artifacts:** [learner SQL](../day05_cross_self_joins.sql) ·
  [solution reasoning](../solutions/day05_solutions.md) ·
  [executable solution](../solutions/day05_solutions.sql)

## Learning objectives

- Generate intentional combinations with `CROSS JOIN`.
- Traverse same-table relationships with distinct aliases and generate each
  unordered pair exactly once.

## Vocabulary and concepts

- **Cartesian product:** every possible left/right row combination.
- **Self-join:** joining a relation to another alias of itself.
- **Canonical pair:** one stable representation, such as `a.id < b.id`, for an
  unordered pair.

## Worked example / walkthrough

For product pairs, compare `p1.product_id <> p2.product_id` with
`p1.product_id < p2.product_id`. The first produces both `(A,B)` and `(B,A)`;
the second removes reversed duplicates and self-pairs in one predicate.

## Exercises

Complete the prompts in the [learner SQL](../day05_cross_self_joins.sql). Before
running a cross join, calculate the expected maximum rows as
`left_count * right_count`.

## Self-check

- Does every table instance have a clear alias and role?
- Can you prove the pair query contains neither self-pairs nor reversed
  duplicates?

## Next step

Continue to [Day 06 — set operations](day06_set_operations.md).

## Deep dive and reference

Learning objectives
- Use CROSS JOIN to form Cartesian products intentionally
- Write self-joins to compare rows within the same table
- Generate pairs and ensure de-duplication (i<j pattern)

Why this matters
Some analyses require pairing rows (A/B comparisons, before/after, customer-customer similarity). Self-joins and controlled Cartesian products enable these.

Core concepts and deep dive
- CROSS JOIN: every row on left with every row on right; use only with small sets or with subsequent filters.
- SELF JOIN: join a table to itself (aliasing required) to compare peers (e.g., orders on consecutive days per customer).
- Pair generation patterns:
  - Symmetric pairs once: JOIN with key ordering (a.id < b.id) to avoid duplicates and self-pairs.
  - Time adjacency: join on the same key and use
    `date_a BETWEEN date_b - interval '1 day' AND date_b + interval '1 day'`.

Walkthrough mapping
- Product substitution pairs within a category (p1.category=p2.category AND p1.product_id<p2.product_id) for bundling analysis.
- Employee hierarchy: `employees e LEFT JOIN employees m ON
  e.manager_id=m.employee_id` gets manager names with a self-join.

Performance notes
- CROSS JOIN blows up quickly; reduce with filters immediately after.
- Consider generating sequences with generate_series for small domains rather than CROSS of large tables.

Exercises from the learner script
1) Create a cross join between the top five categories and top five countries
   by net line revenue.
2) Show the three-level employee → manager → manager's manager hierarchy.

“Top” requires a metric. Use the same net line revenue expression as the
course—`unit_price * quantity * (1 - discount)`—and add stable tie-breakers.

Further reading
- Self-joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS
