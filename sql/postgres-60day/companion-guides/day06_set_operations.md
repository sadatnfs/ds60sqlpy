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

## Exercises

Complete the prompts in the [learner SQL](../day06_set_operations.sql). Run the
same pair of inputs with `UNION` and `UNION ALL`, then explain the row-count
difference.

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

Exercises from the learner script
1) Find products that appear in both order items and promotions.
2) Find countries that have customers but no orders.
3) Combine two filtered order sets with `UNION` and `UNION ALL`, then compare
   row counts to observe duplicate removal.

For exercise 2, project only `country` on both sides before using `EXCEPT`; set
operations compare complete rows, not business concepts.

Further reading
- Set operations: https://www.postgresql.org/docs/current/queries-union.html
