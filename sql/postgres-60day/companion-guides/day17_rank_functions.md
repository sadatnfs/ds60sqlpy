# Day 17 — Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 16 — window-function fundamentals](day16_window_functions_fundamentals.md)
- **Artifacts:** [learner SQL](../day17_rank_functions.sql) ·
  [solution reasoning](../solutions/day17_solutions.md) ·
  [executable solution](../solutions/day17_solutions.sql)

## Learning objectives

- Choose a ranking function whose tie behavior matches the requirement.
- Produce deterministic top-N-per-group results.

## Vocabulary and concepts

- **Peer rows:** rows equal on the window's `ORDER BY` expressions.
- **Gap rank:** `RANK` gives peers the same rank and leaves gaps afterward.
- **Dense rank:** `DENSE_RANK` gives peers the same rank without gaps.

## Worked example / walkthrough

Rank two products with equal revenue using `ROW_NUMBER`, `RANK`, and
`DENSE_RANK`. Add `product_id` as the last `ORDER BY` key when the requirement
is exactly five deterministic rows; omit that tie-breaker when equal metrics
must share a business rank.

## Exercises

Complete the prompts in the [learner SQL](../day17_rank_functions.sql). Add a
small `VALUES` example with a tie and record all three rank outputs.

## Self-check

- Is the requirement “exactly N rows” or “all rows tied in the top N ranks”?
- Does the ordering include a stable key where deterministic selection matters?

## Next step

Continue to [Day 18 — LAG and LEAD](day18_lag_lead.md).

## Deep dive and reference

Learning objectives
- Assign row ordinals and ranks within partitions using ORDER BY
- Choose the correct rank function for ties and pagination
- Build top-k per group, leaderboards, and tie-aware analytics

Why this matters
Ranking underpins “top N per X”, de-duplicating, and cohort benchmarking. Picking the right function controls tie behavior, which changes results and business meaning.

Core concepts and deep dive
- ROW_NUMBER() OVER (PARTITION BY k ORDER BY t): assigns 1,2,3… with no ties (deterministic if ORDER BY unique). Use for de-duplication (keep first per key).
- RANK(): equal sort values receive the same rank; leaves gaps after ties (1,1,3…).
- DENSE_RANK(): equal values share rank without gaps (1,1,2…).
- ORDER BY determinism: When values tie, add a tiebreaker column to produce stable ordering (e.g., ORDER BY amt DESC, order_id ASC).

Patterns
- Top-k per group: WHERE rn <= k after wrapping ROW_NUMBER in a subquery/CTE.
- Category leaders: DENSE_RANK by revenue within category; pick rank <= 3 for top-3 allowing ties.
- Latest records per entity: ROW_NUMBER ordered by timestamp DESC; keep rn=1.

Pitfalls
- Using RANK when you need exactly k rows per group; ties may exceed k (use ROW_NUMBER) or allow overflow intentionally.
- Non-deterministic ordering when ORDER BY is not unique; results can fluctuate.

Exercises from the learner script
1) Rank products by net line revenue within category and compare `RANK` with
   `DENSE_RANK`.
2) Return the top three customers per country by lifetime revenue.

The prompt does not specify tie overflow for the top three. The maintained
answer uses `DENSE_RANK`, so every customer tied in the first three distinct
revenue levels is retained; use `ROW_NUMBER` only when exactly three rows per
country are required.

Further reading
- Ranking: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE
