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

## Exercises

Complete the prompts in the [learner SQL](../day11_case_expressions.sql). Add a
small `VALUES` table of boundary cases and display both input and assigned
label.

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

Exercises from the learner script
1) Segment customers into tiers by lifetime net line revenue using `CASE`.
2) Bucket each order's hour into morning, afternoon, evening, or night.

Define hour boundaries explicitly, for example morning 06:00–11:59, afternoon
12:00–17:59, evening 18:00–21:59, and night otherwise. Different boundaries are
valid if documented.

Further reading
- CASE: https://www.postgresql.org/docs/current/functions-conditional.html
