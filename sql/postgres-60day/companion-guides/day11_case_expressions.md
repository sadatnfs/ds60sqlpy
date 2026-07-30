# Day 11 — CASE Expressions and Conditional Logic (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 10 — data modification with subqueries](day10_dml_with_subqueries.md)
- **Artifacts:** [learner SQL](../day11_case_expressions.sql) ·
  [solution reasoning](../solutions/day11_solutions.md) ·
  [executable solution](../solutions/day11_solutions.sql)

## Learning objectives

- Classify rows with ordered, mutually understandable `CASE` branches.
- Use conditional aggregation without losing unmatched categories.

## Vocabulary and concepts

- **Searched CASE:** evaluates Boolean conditions in order.
- **Simple CASE:** compares one expression with several values.
- **Short-circuit ordering:** the first matching branch supplies the result.

## Worked example / walkthrough

Take a three-tier amount classification and test values just below, exactly at,
and just above each boundary. Because `CASE` stops at the first match, place the
most specific or highest-threshold conditions before broader ones.

## Practice assumptions and review method

- **Focus:** Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
- **Assumptions:** Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
- **Failure to watch for:** Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Classify orders as small, medium, or large by total amount.
   **Progressive hint:** Validate boundaries and place the highest threshold first.
   **Expected shape:** One row per order with exactly one size label.
2. **Query writing:** Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
   **Progressive hint:** Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
   **Expected shape:** One summary row.
3. **Query writing:** Label missing customer segments separately from known segment values.
   **Progressive hint:** Test `IS NULL` before comparing text values.
   **Expected shape:** One row per customer with an explicit segment label.
4. **Prediction:** Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
   **Progressive hint:** First-match wins, so specific/high thresholds must precede broader/lower ones.
   **Expected shape:** A value of 500 is labeled high.
5. **Debugging:** Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
   **Progressive hint:** All result branches must resolve to a compatible PostgreSQL type.
   **Expected shape:** Three rows with text labels.
6. **Extension:** Create payment-method display labels and preserve unknown future methods with an explicit fallback.
   **Progressive hint:** A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
   **Expected shape:** One row per payment method and display label.

## Self-check

- Are branch boundaries exhaustive and non-overlapping?
- Do all branches, including `ELSE`, resolve to compatible data types?

## Next step

Continue to [Day 12 — string functions](day12_string_functions.md).

## Deep dive and reference

Learning objectives
- Write simple and searched CASE expressions in SELECT and ORDER BY
- Use CASE within aggregates for conditional sums/counts
- Understand evaluation order and NULL handling in CASE

Core concepts and deep dive
- Simple CASE: CASE expr WHEN val1 THEN ... WHEN val2 THEN ... ELSE ... END
- Searched CASE: CASE WHEN cond1 THEN ... WHEN cond2 THEN ... ELSE ... END — more flexible; prefer for predicates.
- CASE is an expression; can be nested and used anywhere expressions are allowed.
- Use CASE to implement bucketing, flags, and conditional aggregation without extra joins.

Examples
- Segment labels: CASE WHEN ltv>=1000 THEN 'gold' WHEN ltv>=300 THEN 'silver' ELSE 'bronze' END.
- Conditional aggregate: `SUM(CASE WHEN status='returned' THEN total_amount
  ELSE 0 END)` over `orders`.

Pitfalls
- Overlapping conditions in searched CASE; first match wins. Order matters.
- Returning mixed types; ensure consistent result types across branches.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- CASE: https://www.postgresql.org/docs/current/functions-conditional.html
