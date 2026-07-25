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

## Exercises

Complete the prompts in the [learner SQL](../day14_numeric_and_casting.sql).
Test a zero denominator and a text value that cannot be cast, then choose an
explicit validation policy.

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

Exercises from the learner script
1) Apply `CEIL` and `FLOOR` to product prices to create price buckets.
2) Extract `customers.attributes->>'channel'`, cast it to text, and group by
   that channel.

The `->>` operator already returns text, so the explicit cast in exercise 2 is
pedagogical rather than necessary. Preserve `NULL` as its own group or label it
with `COALESCE`, but state the choice.

Further reading
- Numeric types: https://www.postgresql.org/docs/current/datatype-numeric.html
