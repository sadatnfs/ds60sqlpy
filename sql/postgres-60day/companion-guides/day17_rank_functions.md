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

## Practice assumptions and review method

- **Focus:** Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
- **Assumptions:** All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
- **Failure to watch for:** `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Number each customer's orders from newest to oldest.
   **Progressive hint:** Partition by customer and use order date plus order ID as a unique descending order.
   **Expected shape:** One row per order with sequence starting at one per customer.
2. **Query writing:** Rank products by price within category using both `RANK` and `DENSE_RANK`.
   **Progressive hint:** Rank only on price so equal prices tie; order the final display by product ID.
   **Expected shape:** One row per product with two rank semantics.
3. **Query writing:** Return the three highest-priced products per category, including price ties.
   **Progressive hint:** Compute `DENSE_RANK` in a CTE and filter outside.
   **Expected shape:** At least three price levels per category where available.
4. **Prediction:** Compare row number, rank, and dense rank on values 100, 100, and 90.
   **Progressive hint:** Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
   **Expected shape:** Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2.
5. **Debugging:** Return exactly one latest order per customer even when timestamps tie.
   **Progressive hint:** Use row number with the unique order ID as final tie-breaker.
   **Expected shape:** At most one row per customer.
6. **Extension:** Rank employee salaries within department and show only the top two distinct salary levels.
   **Progressive hint:** Dense rank includes all employees tied at either of the top two salary values.
   **Expected shape:** Top two salary levels per department.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Ranking: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE
