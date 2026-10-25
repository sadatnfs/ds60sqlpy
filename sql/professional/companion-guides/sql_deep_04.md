# Recursive Graph Reachability, Paths, Cycles, and Dependency Order

**Stable ID:** `sql-deep-04`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-deep-04**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-deep-04/lesson/workspace/sql/professional/lessons/sql_deep_04.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-deep-04
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-24`](../../postgres-60day/companion-guides/day24_recursive_ctes.md), [`sql-25`](../../postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_04.sql), [explained reference](../solutions/sql_deep_04_solutions.md), and [executable reference](../solutions/sql_deep_04_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Recursive state:** The columns carried from one recursive CTE iteration to the next; they determine both meaning and duplicate elimination.

- **Simple path:** A route that visits no vertex more than once, represented here by a text-array path.

- **Cycle-closing edge:** An edge whose target already appears in the current path, proving a repeated vertex in that traversal.

- **Blocked dependency:** A vertex that cannot yet be processed because an unprocessed prerequisite remains; it may depend on a cycle without lying in the cycle itself.

A recursive CTE consists of an anchor query and a recursive step. The anchor defines initial state. The step joins that state to relationships and emits new state. Termination depends on the meaning of those columns, not merely on using the keyword RECURSIVE. A graph with cycles needs explicit duplicate elimination, a visited condition or another finite-state argument.

UNION can safely deduplicate reachability states containing only vertex identity. Once a vertex has been reached, another route to the same vertex adds no new information for that question. If the state also contains a growing path or depth, those rows differ and UNION no longer prevents cycling. The appropriate state depends on whether the target is reachability, every route, minimum hops or weighted cost.

Path arrays make the traversal inspectable. Append the next vertex and refuse expansion when it already appears in the path to enumerate simple paths. To diagnose cycles, permit one closing step, mark it and stop expanding that marked row. The resulting route may include a noncyclic prefix before the repeated vertex; do not describe the entire prefix as a cycle.

A depth limit guarantees a bounded exploration but does not prove completeness. If a boundary state still has an unexplored outgoing edge, a missing vertex may simply lie beyond the budget. Report a truncation flag rather than labeling every absent vertex unreachable. Reachability with a finite identity state can terminate without an arbitrary depth cutoff on this fixture.

Enumerating all simple paths can identify the cheapest path on a tiny nonnegative graph, but the number of paths can grow exponentially. It is an explanatory reference, not a scalable replacement for Dijkstra or a specialized graph engine. Return an actual chosen path along with its cost so the value can be independently checked.

Dependency ordering uses different logic. A vertex is eligible only when all of its incoming prerequisites have already been processed. Repeatedly choose an eligible vertex, append it to processed state and stop when none remain. If some vertices remain, they may form a cycle or depend on one. Distinguish that blocked set from proof that every remaining vertex lies in a cycle.

## Worked example / walkthrough

### Example 1

```sql
WITH RECURSIVE sequence(value) AS (
 VALUES(1)
 UNION ALL
 SELECT value+1 FROM sequence WHERE value<4
)
SELECT value,value*value AS square FROM sequence ORDER BY value;
```

The anchor starts at one and the step adds one only while the current value is below four. The output grain is one integer value with its square, yielding(1,1),(2,4),(3,9),(4,16). The strict step condition supplies a finite termination argument; ORDER BY supplies presentation, not recursion execution order.

### Example 2

```sql
SELECT ARRAY['a','b','c']::text[] AS path,
       'b'=ANY(ARRAY['a','b','c']::text[]) AS revisits_b,
       ARRAY['a','b','c']::text[] || 'd'::text AS extended_path;
```

The one-row output has path, revisits_b, extended_path. Membership is true for b, and appending d yields [a, b, c, d]. The path array records vertex identities, making a cycle guard independent of depth or a total-cost value that might repeat for unrelated routes.

## Exercises

1. **Compute reachability with a finite identity state.** Starting at a, return vertex for every reachable vertex including a. Use recursive UNION over vertex identity only so the b-c-d cycle terminates. One output row represents one vertex, ordered by vertex.

**Inputs/evidence:** For sql-deep-04 Exercise 1, Starting at a, return vertex for every reachable vertex including a. Use recursive UNION over vertex identity only so the b-c-d cycle terminates. One output row represents one vertex, ordered by vertex.

**Expected result/shape:** For sql-deep-04 Exercise 1, Rows a, b, c, d, e, g appear once each; isolated f is absent. No arbitrary depth cap is required for this finite identity-state traversal.

**Verify:** For sql-deep-04 Exercise 1, compare the distinct returned vertices with a hand traversal from the start; confirm the cycle does not produce an unbounded growing recursion state.

2. **Enumerate simple routes to a target.** Return path, total_cost, hops for every simple path from a to d. Carry vertex, path, cost in the recursive state, append targets and prevent revisiting any vertex already in the path. One output row represents a complete path; order by path.

**Inputs/evidence:** For sql-deep-04 Exercise 2, Return path, total_cost, hops for every simple path from a to d. Carry vertex, path, cost in the recursive state, append targets and prevent revisiting any vertex already in the path. One output row represents a complete path; order by path.

**Expected result/shape:** For sql-deep-04 Exercise 2, Paths[a, b, c, d] cost 3, hops 3 and [a, c, d] cost 5, hops 2 appear. The cheaper route has more hops, and no path repeats a vertex.

**Verify:** For sql-deep-04 Exercise 2, inspect every route array for repeated vertices and check each consecutive pair is an edge; sum edge weights independently and retain distinct valid routes.

3. **Emit one cycle-closing step as evidence.** Return cycle_path, repeated_vertex, cycle_cost for traversals from a that first revisit a vertex. Allow a closing edge to be emitted, mark it as a cycle and stop expanding marked states. Order by cycle_path and do not claim that the whole path prefix is itself a cycle.

**Inputs/evidence:** For sql-deep-04 Exercise 3, Return cycle_path, repeated_vertex, cycle_cost for traversals from a that first revisit a vertex. Allow a closing edge to be emitted, mark it as a cycle and stop expanding marked states. Order by cycle_path and do not claim that the whole path prefix is itself a cycle.

**Expected result/shape:** For sql-deep-04 Exercise 3, Paths[a, b, c, d, b] repeat b at cost 4 and [a, c, d, b, c] repeat c at cost 7. Both are emitted once and terminate.

**Verify:** For sql-deep-04 Exercise 3, confirm the final step repeats a vertex already in the route, and that this closing row is emitted once without being expanded further.

4. **Report a truncated search honestly.** Explore simple paths from a for at most two edges. Return vertex, min_hops, search_truncated for vertices reached within that budget, ordered by vertex. Set the global truncation flag true if any depth-two state has an outgoing target not already in its path.

**Inputs/evidence:** For sql-deep-04 Exercise 4, Explore simple paths from a for at most two edges. Return vertex, min_hops, search_truncated for vertices reached within that budget, ordered by vertex. Set the global truncation flag true if any depth-two state has an outgoing target not already in its path.

**Expected result/shape:** For sql-deep-04 Exercise 4, Vertices a, b, c, d, e have minimum hops 0,1,1,2,2 and search_truncated=true. Vertex g is absent because it requires more than two hops, so absence cannot be called unreachable.

**Verify:** For sql-deep-04 Exercise 4, find at least one admissible outgoing edge beyond a boundary-depth route; a nonempty frontier proves the result is truncated rather than complete.

5. **Return cheapest path evidence for every vertex.** Enumerate simple paths on this tiny nonnegative graph and choose the cheapest per vertex, breaking ties by fewer hops then lexicographic path. Left-join to all vertices and return vertex, total_cost, path ordered by vertex, preserving unreachable f with NULL cost/path.

**Inputs/evidence:** For sql-deep-04 Exercise 5, Enumerate simple paths on this tiny nonnegative graph and choose the cheapest per vertex, breaking ties by fewer hops then lexicographic path. Left-join to all vertices and return vertex, total_cost, path ordered by vertex, preserving unreachable f with NULL cost/path.

**Expected result/shape:** For sql-deep-04 Exercise 5, Costs a0, b1, c2, d3, e6, g4 have paths[a],[a, b],[a, b, c],[a, b, c, d],[a, b, e],[a, b, c, d, g]. Vertex f has NULL cost and path.

**Verify:** For sql-deep-04 Exercise 5, compare candidate simple routes for each reachable vertex and independently sum the selected route weights; preserve the unreachable vertex as explicitly unreachable.

6. **Separate processed dependencies from cyclic or blocked vertices.** Repeatedly select the lexicographically smallest unprocessed vertex whose incoming prerequisites are all processed. Return vertex, processed, cyclic_or_blocked for every vertex ordered by vertex. Stop when no eligible vertex remains and label remaining vertices as cyclic or blocked, not all proven cycle members.

**Inputs/evidence:** For sql-deep-04 Exercise 6, Repeatedly select the lexicographically smallest unprocessed vertex whose incoming prerequisites are all processed. Return vertex, processed, cyclic_or_blocked for every vertex ordered by vertex. Stop when no eligible vertex remains and label remaining vertices as cyclic or blocked, not all proven cycle members.

**Expected result/shape:** For sql-deep-04 Exercise 6, Only a and isolated f are processed. Vertices b, c, d, e, g are cyclic_or_blocked=true; e and g depend on the cycle but are not themselves on its directed loop.

**Verify:** For sql-deep-04 Exercise 6, repeatedly remove zero-indegree vertices by hand and compare the processed-vertex output; distinguish vertices on the cycle from a downstream vertex blocked by it, rather than calling the entire remainder a cycle.

## Common mistakes and diagnosis

If recursion does not terminate on a cycle, inspect every state column used by UNION duplicate elimination. A growing path makes every row new. If a bounded search omits a vertex, inspect the frontier before declaring it unreachable. If cheapest and fewest-hop paths differ, preserve the edge-weight objective. If a dependency check marks every remaining node as a cycle member, distinguish actual cycle witnesses from downstream blockage. Use actual path arrays and exact costs as evidence, and keep exponential path enumeration confined to the tiny teaching fixture.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the next deepening lesson](sql_deep_05.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL17 recursive CTEs, search order and cycle handling](https://www.postgresql.org/docs/17/queries-with.html).

- [PostgreSQL17 array functions](https://www.postgresql.org/docs/17/functions-array.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-04: Recursive Graph Reachability, Paths, Cycles, and Dependency Order.
Read sql/professional/companion-guides/sql_deep_04.md and sql/professional/lessons/sql_deep_04.sql. Direct prerequisites: sql-24, sql-25.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
