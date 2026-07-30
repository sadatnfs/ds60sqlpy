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

## Practice assumptions and review method

- **Focus:** Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
- **Assumptions:** The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
- **Failure to watch for:** Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build a root-based organization CTE and report headcount and payroll by depth.
   **Progressive hint:** Assign depth during recursion, then aggregate employee rows once.
   **Expected shape:** One row per hierarchy depth.
2. **Query writing:** Report each manager's direct-report count and payroll.
   **Progressive hint:** Direct-team grain needs one self join, not full recursive descendants.
   **Expected shape:** One row per manager with at least one direct report.
3. **Query writing:** Identify hierarchy roots and leaves in one report.
   **Progressive hint:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.
   **Expected shape:** One labeled row per root or leaf employee.
4. **Prediction:** Count employees reachable from roots and compare with total employees.
   **Progressive hint:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
   **Expected shape:** One row with zero unreachable employees.
5. **Debugging:** Calculate full-subtree report counts per manager without counting the manager as their own report.
   **Progressive hint:** Seed direct edges and recurse descendants while carrying the original manager.
   **Expected shape:** One row per manager with descendant count.
6. **Extension:** Report department headcount split between managers and nonmanagers.
   **Progressive hint:** First derive the manager ID set, then conditionally aggregate employees once.
   **Expected shape:** One row per department.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
