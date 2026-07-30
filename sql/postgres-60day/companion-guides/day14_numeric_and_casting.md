# Day 14 — Numeric Types, Casting, and Precision (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 13 — date, time, and time zones](day13_date_time_functions.md)
- **Artifacts:** [learner SQL](../day14_numeric_and_casting.sql) ·
  [solution reasoning](../solutions/day14_solutions.md) ·
  [executable solution](../solutions/day14_solutions.sql)

## Learning objectives

- Choose numeric types that preserve required precision.
- Cast deliberately and guard division, rounding, overflow, and malformed text.

## Vocabulary and concepts

- **Exact numeric:** `numeric`/`decimal`, which stores decimal values without
  binary floating-point approximation.
- **Scale:** digits to the right of the decimal point.
- **Type coercion:** PostgreSQL's conversion of values to a compatible type.

## Worked example / walkthrough

Evaluate `1 / 3`, `1::numeric / 3`, and
`ROUND(1::numeric / NULLIF(3, 0), 2)`. Explain the result type at each step and
why guarding the denominator belongs before rounding.

## Practice assumptions and review method

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Failure to watch for:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
   **Progressive hint:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
   **Expected shape:** One row per product.
2. **Query writing:** Safely cast a set of text values to numeric only when they match a numeric grammar.
   **Progressive hint:** Validate with a regex before casting; otherwise return NULL.
   **Expected shape:** One row per sample text.
3. **Query writing:** Show order-item net revenue rounded only after summing.
   **Progressive hint:** Aggregate exact line expressions first; round the final display value.
   **Expected shape:** One row per order.
4. **Prediction:** Compare integer division with numeric division for 1 divided by 4.
   **Progressive hint:** At least one operand must be numeric to preserve the fraction.
   **Expected shape:** One row showing 0 and 0.25.
5. **Debugging:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
   **Progressive hint:** Aggregate payment amount and count distinct order IDs at one common scope.
   **Expected shape:** Exactly one summary row.
6. **Extension:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
   **Progressive hint:** This diagnostic makes the consequence of early rounding visible.
   **Expected shape:** One row with two totals and their signed difference.

## Self-check

- Can you justify the type used for money-like values and ratios?
- Are division-by-zero and `NULL` behavior visible rather than silently
  misleading?

## Next step

Continue to [Day 15 — Phase 1 project](day15_phase1_project.md).

## Deep dive and reference

Learning objectives
- Use integer, numeric/decimal, and floating types appropriately
- Control rounding and formatting; avoid integer division pitfalls
- Cast safely between types; handle NULLs and invalid text

Core concepts and deep dive
- Types: integer (fast, bounded), numeric(p,s) (exact decimal), double precision (approximate). Use numeric for money.
- Division: integer/int division truncates; cast to numeric for fractional results.
- Rounding: ROUND(x,2), CEIL/FLOOR; formatting with to_char for presentation.
- Casting: CAST(text AS numeric) or ::numeric; use to_number(text, format) for messy text.

Examples
- Compute gross_margin_pct = (price-cost)/NULLIF(price,0) casting to numeric with scale.
- Parse '1,234.50' with to_number and compare to numeric cast behavior.

Pitfalls
- Silent rounding when casting to narrower numeric precision.
- Dividing by zero — use NULLIF(den,0) to avoid errors.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Numeric types: https://www.postgresql.org/docs/current/datatype-numeric.html
