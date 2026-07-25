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

## Exercises

Complete the prompts in the [learner SQL](../day22_advanced_windows.sql). Define
one named window and compare a full average with a leave-one-out average.

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

Exercises from the learner script
1) For each country, rank categories by net line revenue and also compute the
   category's overall rank.
2) For each employee, compute salary rank within department and across the
   whole company.

“Overall category rank” means rank categories by their revenue summed across
all countries, then attach that category-level rank to each country-category
row. Ranking every country-category pair globally would answer a different
question.

Further reading
- WINDOW clause: https://www.postgresql.org/docs/current/sql-select.html#SQL-WINDOW
- Exclusion: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
