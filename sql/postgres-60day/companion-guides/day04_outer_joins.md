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

## Practice assumptions and review method

- **Focus:** Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
- **Assumptions:** Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
- **Failure to watch for:** A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every customer with order count, including customers with zero orders.
   **Progressive hint:** Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
   **Expected shape:** One row per customer; zero is visible.
2. **Query writing:** Find products that have never appeared in an order item.
   **Progressive hint:** Left join and retain rows where the right-side primary key is NULL.
   **Expected shape:** One row per unsold product.
3. **Query writing:** Compare monthly budgets and expenses by category with a full outer join.
   **Progressive hint:** Aggregate each side to the same category/month grain before joining; preserve keys from either side.
   **Expected shape:** One row per category/month present in either source.
4. **Prediction:** Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
   **Progressive hint:** Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
   **Expected shape:** One row per customer, including zero delivered orders.
5. **Debugging:** Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
   **Progressive hint:** Count a non-nullable right-side key that becomes NULL for an unmatched row.
   **Expected shape:** One row per customer with correct zero counts.
6. **Extension:** Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
   **Progressive hint:** Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
   **Expected shape:** One summary row with three mutually interpretable counts.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Outer joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM
