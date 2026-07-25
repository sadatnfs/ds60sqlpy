# Day 25 — Multiple CTEs and Hierarchies in One Query (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 24 — recursive CTEs](day24_recursive_ctes.md)
- **Artifacts:** [learner SQL](../day25_multiple_ctes_hierarchies.sql) ·
  [solution reasoning](../solutions/day25_solutions.md) ·
  [executable solution](../solutions/day25_solutions.sql)

## Learning objectives

- Compose recursive and non-recursive stages without obscuring grain.
- Validate a complex query stage by stage.

## Vocabulary and concepts

- **CTE pipeline:** ordered named relations in which later stages consume
  earlier output.
- **Hierarchy enrichment:** joining traversal output to descriptive or
  aggregate data.
- **Stage invariant:** a property such as key uniqueness or row count checked
  before the next transformation.

## Worked example / walkthrough

Build the employee hierarchy separately and validate `(employee_id, depth)`.
Build department aggregates separately at one row per department. Join them
only after both grains are stable, so a department measure is not accidentally
re-aggregated across hierarchy paths.

## Exercises

Complete the prompts in the [learner SQL](../day25_multiple_ctes_hierarchies.sql).
Add a comment stating the grain and expected key of every stage.

## Self-check

- Does each CTE have one clear purpose and a testable output contract?
- Are repeated measures protected from hierarchy fanout?

## Next step

Continue to [Day 26 — CTEs with window functions](day26_ctes_with_windows.md).

## Deep dive and reference

Learning objectives
- Chain multiple CTEs to express stepwise logic clearly
- Mix recursive and non-recursive CTEs for hierarchical problems
- Reuse earlier CTE outputs to avoid recomputation

Why this matters
Complex reports often need staging, filtering, enrichment, and aggregation in stages. Multiple CTEs provide a declarative pipeline that remains readable and testable.

Core concepts and deep dive
- Ordering of CTEs: later CTEs can reference earlier ones. Think of each as a named subquery stage.
- Mixed recursion: WITH RECURSIVE tree AS (...), leaves AS (...) SELECT ... FROM tree JOIN leaves ...
- Performance: since Postgres 12, non-recursive CTEs may be inlined. Force MATERIALIZED for expensive reused CTEs.

Patterns
- Stage raw lines -> enrich with dims -> filter -> aggregate -> final select.
- Build an employee hierarchy and join it to department headcount, payroll, or
  average-salary aggregates.

Pitfalls
- Circular references between CTEs are invalid.
- Excessive staging for trivial logic harms readability; strike a balance.

Exercises from the learner script
1) Build a three-level hierarchical report and combine it with department
   aggregates.
2) Create a CTE chain with four explicit stages: filter, enrich, aggregate, and
   present.

“Three-level” is interpreted by the maintained answer as employee, direct
manager, and manager's manager. The second prompt leaves the business question
open; the maintained example reports last-180-day country-category orders,
revenue, and revenue per order.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
