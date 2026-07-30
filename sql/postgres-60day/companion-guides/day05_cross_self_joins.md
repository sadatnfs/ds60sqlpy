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

## Practice assumptions and review method

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Failure to watch for:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every employee with their direct manager when present.
   **Progressive hint:** Self join employees and use a left join so top-level employees remain visible.
   **Expected shape:** One row per employee.
2. **Query writing:** Find employees who manage nobody.
   **Progressive hint:** Left join candidate managers to reports and retain managers with no right-side match.
   **Expected shape:** One row per leaf employee.
3. **Query writing:** Build a complete grid of six recent months and all expense categories.
   **Progressive hint:** Cross join two small declared dimensions; do not cross join raw fact tables.
   **Expected shape:** Six rows per distinct expense category.
4. **Prediction:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
   **Progressive hint:** Cross-join cardinality is the product of input row counts.
   **Expected shape:** One row containing 72.
5. **Debugging:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.
   **Progressive hint:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
   **Expected shape:** One row per unordered same-department pair.
6. **Extension:** Show each employee, their manager, and their manager's manager.
   **Progressive hint:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
   **Expected shape:** One row per employee with up to two ancestor columns.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Self-joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS
