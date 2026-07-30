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

## Practice assumptions and review method

- **Focus:** Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
- **Assumptions:** A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
- **Failure to watch for:** Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return orders whose total exceeds the overall average order total.
   **Progressive hint:** The aggregate subquery is guaranteed to return exactly one value.
   **Expected shape:** Order rows above the global average.
2. **Query writing:** Add the total customer count as a scalar column beside each country-level customer count.
   **Progressive hint:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
   **Expected shape:** One row per country with a common global total.
3. **Query writing:** Show each customer with their latest order timestamp using a scalar correlated subquery.
   **Progressive hint:** Use `MAX` to guarantee one result and let customers without orders receive NULL.
   **Expected shape:** One row per customer.
4. **Prediction:** Demonstrate that a scalar subquery with no matching rows returns NULL.
   **Progressive hint:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.
   **Expected shape:** One row whose boolean result is true.
5. **Debugging:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
   **Progressive hint:** Choose the business reduction explicitly; this answer uses maximum price.
   **Expected shape:** One row per category with a scalar global maximum for comparison.
6. **Extension:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
   **Progressive hint:** Compute the global total once, then cross join the guaranteed one-row relation.
   **Expected shape:** One row per country with country share.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Subqueries: https://www.postgresql.org/docs/current/sql-select.html#SQL-SELECT-SUBQUERIES
