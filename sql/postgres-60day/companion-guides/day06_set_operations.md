# Day 06 — Set Operations: UNION, INTERSECT, EXCEPT (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 05 — cross and self joins](day05_cross_self_joins.md)
- **Artifacts:** [learner SQL](../day06_set_operations.sql) ·
  [solution reasoning](../solutions/day06_solutions.md) ·
  [executable solution](../solutions/day06_solutions.sql)

## Learning objectives

- Combine compatible result sets and choose deliberately between duplicate
  preservation and removal.
- Express set overlap and difference at the correct projected grain.

## Vocabulary and concepts

- **Set operation:** an operator that combines or compares complete result rows.
- **Union compatibility:** equal column counts with compatible data types.
- **Duplicate semantics:** `UNION ALL` preserves duplicates; `UNION`,
  `INTERSECT`, and `EXCEPT` use set-style duplicate handling.

## Worked example / walkthrough

Project only `order_id` from orders and payments before applying `EXCEPT`.
Because set operations compare every projected column, adding an unrelated
amount or timestamp would change the meaning from “missing order IDs” to
“missing complete tuples.”

## Practice assumptions and review method

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Failure to watch for:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return customer IDs that have either an order or a support event.
   **Progressive hint:** `UNION` expresses set membership and removes duplicates across both sources.
   **Expected shape:** One distinct customer ID per qualifying customer.
2. **Query writing:** Return customer IDs that have both an order and a support event.
   **Progressive hint:** `INTERSECT` keeps keys present in both compatible sets.
   **Expected shape:** One distinct customer ID in both sets.
3. **Query writing:** Return customers who have no orders.
   **Progressive hint:** `EXCEPT` subtracts the order-customer set from all customers.
   **Expected shape:** One row per customer absent from orders.
4. **Prediction:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
   **Progressive hint:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.
   **Expected shape:** Two labeled summary rows showing all-count >= distinct-count.
5. **Debugging:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
   **Progressive hint:** Each branch below returns one text label and one numeric amount at the same report grain.
   **Expected shape:** Rows identify revenue and expense measures with compatible types.
6. **Extension:** Return the symmetric difference between customers with orders and customers with support events.
   **Progressive hint:** Subtract each set from the other, then union the two differences.
   **Expected shape:** Customers present in exactly one of the two source sets.

## Self-check

- Do both branches return columns in the same semantic order, not merely
  compatible types?
- Can you state whether duplicates should survive for the business question?

## Next step

Continue to [Day 07 — Week 1 project](day07_week1_project.md).

## Deep dive and reference

Learning objectives
- Combine result sets with UNION/UNION ALL
- Compute set intersection and differences with INTERSECT/EXCEPT
- Understand duplicate handling and column alignment rules

Why this matters
Merging and comparing result sets is common in data reconciliation, feature flags, and A/B test cohorts.

Core concepts and deep dive
- UNION ALL concatenates rows and keeps duplicates; UNION removes duplicates (implies sort/unique).
- INTERSECT returns rows present in both queries; EXCEPT returns rows in left not in right.
- Column rules: Both queries must have same number of columns and compatible types; column names come from the first query.
- Performance: DISTINCT/UNION can be expensive; prefer UNION ALL followed by targeted dedup when appropriate.

Examples in your schema
- Customers from the `gold` and `platinum` segments can be combined by
  selecting `customer_id` from each set.
- Orders with no payment can be found with `SELECT order_id FROM orders EXCEPT
  SELECT order_id FROM payments`.
- Common high-value customers across two periods can be found by intersecting
  compatible `customer_id` result sets.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Set operations: https://www.postgresql.org/docs/current/queries-union.html
