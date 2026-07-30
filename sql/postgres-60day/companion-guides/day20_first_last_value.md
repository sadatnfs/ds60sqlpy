# Day 20 — FIRST_VALUE, LAST_VALUE, NTH_VALUE (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 19 — running aggregates](day19_running_aggregates.md)
- **Artifacts:** [learner SQL](../day20_first_last_value.sql) ·
  [solution reasoning](../solutions/day20_solutions.md) ·
  [executable solution](../solutions/day20_solutions.sql)

## Learning objectives

- Retrieve boundary values from a deliberately framed ordered partition.
- Diagnose the common `LAST_VALUE` default-frame surprise.

## Vocabulary and concepts

- **Boundary value:** the first, last, or Nth value under a declared ordering.
- **Current-row frame:** a frame whose upper boundary stops at the current row.
- **Full-partition frame:** a frame extending through
  `UNBOUNDED FOLLOWING`.

## Worked example / walkthrough

Order a customer's orders by date and compare default
`LAST_VALUE(total_amount)` with the same function over
`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`. The default often
returns the current row's value; the full frame exposes the true final value.

## Practice assumptions and review method

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Failure to watch for:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show every order with the customer's first and last order timestamps.
   **Progressive hint:** Use one full-partition frame from unbounded preceding through unbounded following.
   **Expected shape:** One row per order with constant first/last values per customer.
2. **Query writing:** Show each product with the cheapest and most expensive price in its category.
   **Progressive hint:** Order by price and use a full frame; values tie without needing row identity.
   **Expected shape:** One row per product.
3. **Query writing:** Compare every payment with the first and last payment amount for its order.
   **Progressive hint:** Partition by order, order by timestamp/payment ID, and keep the full frame.
   **Expected shape:** One row per payment.
4. **Prediction:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
   **Progressive hint:** The default ends at the current row; explicit following reaches the true last row.
   **Expected shape:** Three rows showing default current value and full-frame 30.
5. **Debugging:** Return one first and one last order per customer without using window output as an accidental duplicate report.
   **Progressive hint:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.
   **Expected shape:** One row per customer with orders.
6. **Extension:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
   **Progressive hint:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.
   **Expected shape:** At most one latest order per customer.

## Self-check

- Does “last” mean last so far or last in the complete partition?
- What should `NTH_VALUE` return when fewer than N rows exist?

## Next step

Continue to [Day 21 — distribution functions](day21_distribution_functions.md).

## Deep dive and reference

Learning objectives
- Extract first/last values within ordered partitions
- Use frame clauses to avoid surprising LAST_VALUE behavior
- Compute baselines and end-of-period values side-by-side

Why this matters
Anchoring a row against a starting or ending value supports normalization (e.g., index to 100), growth from baseline, and end-of-period reporting.

Core concepts and deep dive
- FIRST_VALUE(expr) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) reliably gives the partition’s first value.
- LAST_VALUE requires an appropriate frame; default frame returns current row’s value. Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING to get the true last value.
- NTH_VALUE(expr, n) generalizes to the nth ordered value.

Patterns
- Normalize to first: x / NULLIF(FIRST_VALUE(x) OVER (...),0).
- Compare current to last: current - LAST_VALUE(x) OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING).

Pitfalls
- Forgetting to extend the frame for LAST_VALUE yields row’s current, not partition last.
- Non-deterministic ordering for duplicates; add tiebreakers.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- FIRST/LAST/NTH: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE
