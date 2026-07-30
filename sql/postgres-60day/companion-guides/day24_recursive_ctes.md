# Day 24 — Recursive CTEs: Hierarchies, Trees, and Graph Walks (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 23 — common table expressions](day23_ctes_intro.md)
- **Artifacts:** [learner SQL](../day24_recursive_ctes.sql) ·
  [solution reasoning](../solutions/day24_solutions.md) ·
  [executable solution](../solutions/day24_solutions.sql)

## Learning objectives

- Build a recursive CTE from compatible anchor and recursive members.
- Track depth and path while preventing cycles.

## Vocabulary and concepts

- **Anchor member:** the non-recursive seed rows.
- **Recursive member:** the query that derives the next rows from prior output.
- **Cycle guard:** a path or visited-key check that prevents revisiting nodes.

## Worked example / walkthrough

Seed each direct manager/report edge with a path array containing both keys.
Each recursive step joins the current report to its direct reports, increments
depth, and rejects a key already present in the path. Inspect the maximum depth
and path before trusting the hierarchy.

## Practice assumptions and review method

- **Focus:** Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
- **Assumptions:** Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
- **Failure to watch for:** `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every manager's direct and indirect reports with depth and path.
   **Progressive hint:** Seed every direct edge, carry the original manager, and reject IDs already in the path.
   **Expected shape:** One row per ancestor-descendant pair.
2. **Query writing:** Generate integers 1 through 100 recursively and return their sum.
   **Progressive hint:** Anchor at 1 and stop producing rows after 100.
   **Expected shape:** Exactly one row with 5050.
3. **Query writing:** Generate the first day of the current and prior 11 months recursively.
   **Progressive hint:** Carry a counter as an explicit termination condition.
   **Expected shape:** Exactly 12 chronological month rows.
4. **Prediction:** Traverse a local graph containing a cycle and prove a path-array guard terminates.
   **Progressive hint:** Reject a destination already present in the path before adding it.
   **Expected shape:** Finite paths starting from node 1; no repeated node inside a path.
5. **Debugging:** Walk upward from every employee to ancestors while preventing cycles.
   **Progressive hint:** The recursive step follows current manager ID to the manager row and appends it to path.
   **Expected shape:** One row per employee-ancestor relation.
6. **Extension:** Summarize employee count by hierarchy depth from all roots.
   **Progressive hint:** Build the guarded root traversal first, then aggregate only after depth is assigned.
   **Expected shape:** One row per observed depth.

## Self-check

- Do anchor and recursive branches return the same column types?
- Can you prove recursion terminates for malformed cyclic data?

## Next step

Continue to [Day 25 — multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md).

## Deep dive and reference

Learning objectives
- Use WITH RECURSIVE to traverse hierarchical/graph data (up/down)
- Understand anchor vs recursive member, UNION ALL, and termination
- Compute depth, paths, cycle detection, and ordering

Why this matters
Many data structures are hierarchical: org charts, category trees, dependency graphs. Recursive CTEs let you explore them without procedural code.

Core concepts and deep dive
- Anatomy
  - WITH RECURSIVE t AS ( anchor_query UNION ALL recursive_query ) SELECT ... FROM t;
  - Anchor emits starting rows (roots). Recursive member references t and produces next-level rows.
  - Termination occurs when recursive member returns no new rows.
- Columns
  - Ensure both SELECTs output the same column list/types (id, parent_id, depth, path, ...).
- Depth and path
  - depth := anchor depth 0 (or 1) plus 1 each recursion.
  - path := path || id to accumulate ancestry for cycle checks and sorting.
- Cycle detection
  - WHERE id <> ALL(path) prevents revisiting nodes (for graphs with cycles).
- Ordering
  - Use ORDER BY path for pre-order traversal; or track sort_keys.

Patterns
- Downward traversal: employees (`employee_id`, `manager_id`) from a manager to
  all reports.
- Level summaries: GROUP BY depth to count nodes per level.

Pitfalls
- Infinite recursion on cycles; always implement a cycle guard or LIMIT depth.
- UNION vs UNION ALL: use UNION ALL to avoid global de-dup unless necessary; dedup can be expensive.
- Large trees can be costly; index parent_id and id.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH RECURSIVE: https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-RECURSIVE
- Tree traversal recipes: https://wiki.postgresql.org/wiki/Hierarchical_queries
