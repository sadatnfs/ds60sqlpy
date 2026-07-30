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

## Practice assumptions and review method

- **Focus:** Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
- **Assumptions:** `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
- **Failure to watch for:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return customers who have at least one delivered order.
   **Progressive hint:** `EXISTS` expresses the yes/no question without multiplying customer rows.
   **Expected shape:** One row per qualifying customer.
2. **Query writing:** Return products that have never been sold.
   **Progressive hint:** `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
   **Expected shape:** One row per unsold product.
3. **Query writing:** Return each customer's orders that are above that customer's average order total.
   **Progressive hint:** Correlate the average to the current order's customer, not to the current order ID.
   **Expected shape:** Order rows above their own customer average.
4. **Prediction:** Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
   **Progressive hint:** Correlate on the customer key; a matching row alone determines exclusion.
   **Expected shape:** One row per customer with no order.
5. **Debugging:** Return only each customer's most recent order without an arbitrary `LIMIT 1`.
   **Progressive hint:** Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
   **Expected shape:** At most one deterministic order per customer.
6. **Extension:** Return customers for whom every order has at least one payment, excluding customers with no orders.
   **Progressive hint:** Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
   **Expected shape:** One row per customer satisfying the universal condition.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- EXISTS: https://www.postgresql.org/docs/current/functions-subquery.html
