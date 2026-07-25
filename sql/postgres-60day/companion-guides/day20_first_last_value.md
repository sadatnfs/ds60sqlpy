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

## Exercises

Complete the prompts in the [learner SQL](../day20_first_last_value.sql). Add
same-timestamp rows and choose a deterministic secondary order key.

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

Exercises from the learner script
1) For each product, compare current-month revenue with its first observed
   month revenue.
2) For each employee, compare salary with the first salary recorded.

The schema has no salary-history table. The maintained answer explicitly
simulates exercise 2 by treating the earliest-hired employee's salary within a
department as the baseline. That is not an employee's historical starting
salary and must not be described as one.

Further reading
- FIRST/LAST/NTH: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE
