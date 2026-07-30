# Day 22 — Advanced Windows: Multiple Partitions, Named Windows, Exclusion (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 21 — distribution functions](day21_distribution_functions.md)
- **Artifacts:** [learner SQL](../day22_advanced_windows.sql) ·
  [solution reasoning](../solutions/day22_solutions.md) ·
  [executable solution](../solutions/day22_solutions.sql)

## Learning objectives

- Combine local and global windows at a stable grain.
- Reuse named window specifications and exclude current rows or peers when
  required.

## Vocabulary and concepts

- **Named window:** a reusable `WINDOW name AS (...)` specification.
- **Peer exclusion:** removal of the current row, its peers, or ties from a
  frame.
- **Mixed grain:** an unsafe calculation that combines measures defined at
  different row meanings.

## Worked example / walkthrough

Aggregate revenue to `(country, category)` first. Rank categories within each
country from that relation, then calculate a separate category-total relation
for the overall rank. Joining those stable grains avoids incorrectly ranking
every country/category pair as though it were one global category.

## Practice assumptions and review method

- **Focus:** Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
- **Assumptions:** Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
- **Failure to watch for:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Use a named window to show each order with customer count, average, first date, and last date.
   **Progressive hint:** Name a full-partition customer window once and reuse it.
   **Expected shape:** One row per order.
2. **Query writing:** Compare each employee salary with the average of other employees in the department.
   **Progressive hint:** Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
   **Expected shape:** One row per employee with nullable peer average.
3. **Query writing:** Show each order's distance from its customer's average and standard deviation.
   **Progressive hint:** Compute independent partition windows and guard interpretation when variation is zero.
   **Expected shape:** One row per order.
4. **Prediction:** Sessionize events using a 30-minute gap and predict why the first event starts a session.
   **Progressive hint:** Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
   **Expected shape:** One row per event with session number starting at one.
5. **Debugging:** Find consecutive calendar-day islands in customer order dates without nesting windows.
   **Progressive hint:** Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
   **Expected shape:** One row per customer/date island.
6. **Extension:** Summarize sessions from the sessionized event stream with start, end, event count, and duration.
   **Progressive hint:** Aggregate only after session IDs exist at event grain.
   **Expected shape:** One row per customer session.

## Self-check

- Can you state the grain before every window layer?
- Does an excluded-row calculation handle one-row partitions without dividing
  by zero?

## Next step

Continue to [Day 23 — common table expressions](day23_ctes_intro.md).

## Deep dive and reference

Learning objectives
- Reuse window specs with WINDOW clause and combine multiple windows efficiently
- Use EXCLUDE to omit current row/peers from aggregates
- Optimize window queries with pre-aggregation and indexing

Why this matters
Complex analytics often require many windowed metrics at different grains. Clean specs and performance awareness keep queries readable and fast.

Core concepts and deep dive
- WINDOW w AS (PARTITION BY k ORDER BY t): define once, reuse across functions.
- EXCLUDE CURRENT ROW/EXCLUDE TIES to remove the current row or equal-ordered peers from an aggregate (e.g., average of others).
- Mixed grains: daily pre-aggregate then window across days, not raw events.
- Indexing: multi-column btree on (k, t) supports partitioned sorts; work_mem affects window performance.

Patterns
- Leave-one-out mean: (SUM(x) OVER w - x) / NULLIF(COUNT(*) OVER w - 1, 0) with EXCLUDE CURRENT ROW.
- Cross-window features: per-customer cumulative plus global cumulative in one SELECT using named windows w1 (partitioned) and w2 (global).

Pitfalls
- Window after GROUP BY changes row cardinality; ensure you window the intended grain.
- Excessive repeated specs without WINDOW harms readability.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WINDOW clause: https://www.postgresql.org/docs/current/sql-select.html#SQL-WINDOW
- Exclusion: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
