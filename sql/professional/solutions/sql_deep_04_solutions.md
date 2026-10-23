# sql-deep-04: Explained reference solutions

Read [Recursive Graph Reachability, Paths, Cycles, and Dependency Order](../companion-guides/sql_deep_04.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_04_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

### Exercise 1: Compute reachability with a finite identity state

Starting at a, return vertex for every reachable vertex including a. Use recursive UNION over vertex identity only so the b-c-d cycle terminates. One output row represents one vertex, ordered by vertex.

**Expected:** Rows a, b, c, d, e, g appear once each; isolated f is absent. No arbitrary depth cap is required for this finite identity-state traversal.

```sql
WITH RECURSIVE reachable(vertex) AS (
 VALUES('a'::text)
 UNION
 SELECT e.target FROM reachable AS r JOIN deep4_edges AS e ON e.source=r.vertex
)
SELECT vertex FROM reachable ORDER BY vertex;
```

The recursive state contains only the identity needed for reachability. UNION removes repeated vertices across iterations, so traversing the cycle cannot create endlessly new states. Adding path or depth columns would change this duplicate identity and invalidate that termination argument. The isolated vertex is absent because no edge sequence from a reaches it, not because an exploration budget was exhausted.

### Exercise 2: Enumerate simple routes to a target

Return path, total_cost, hops for every simple path from a to d. Carry vertex, path, cost in the recursive state, append targets and prevent revisiting any vertex already in the path. One output row represents a complete path; order by path.

**Expected:** Paths[a, b, c, d] cost 3, hops 3 and [a, c, d] cost 5, hops 2 appear. The cheaper route has more hops, and no path repeats a vertex.

```sql
WITH RECURSIVE paths(vertex,path,total_cost) AS (
 VALUES('a'::text,ARRAY['a']::text[],0)
 UNION ALL
 SELECT e.target,p.path||e.target,p.total_cost+e.cost
 FROM paths AS p JOIN deep4_edges AS e ON e.source=p.vertex
 WHERE NOT(e.target=ANY(p.path))
)
SELECT path,total_cost,cardinality(path)-1 AS hops FROM paths WHERE vertex='d' ORDER BY path;
```

UNION ALL retains genuinely different paths to the same vertex, while the visited-array condition prevents infinite expansion around the cycle. Cost adds edge weights and hops counts transitions, demonstrating that minimum hops differs from minimum cost. The path itself is the output identity because the same target can have several legitimate routes. This exhaustive construction is intentionally limited to a tiny graph.

### Exercise 3: Emit one cycle-closing step as evidence

Return cycle_path, repeated_vertex, cycle_cost for traversals from a that first revisit a vertex. Allow a closing edge to be emitted, mark it as a cycle and stop expanding marked states. Order by cycle_path and do not claim that the whole path prefix is itself a cycle.

**Expected:** Paths[a, b, c, d, b] repeat b at cost 4 and [a, c, d, b, c] repeat c at cost 7. Both are emitted once and terminate.

```sql
WITH RECURSIVE walks(vertex,path,total_cost,is_cycle) AS (
 VALUES('a'::text,ARRAY['a']::text[],0,false)
 UNION ALL
 SELECT e.target,w.path||e.target,w.total_cost+e.cost,e.target=ANY(w.path)
 FROM walks AS w JOIN deep4_edges AS e ON e.source=w.vertex
 WHERE NOT w.is_cycle
)
SELECT path AS cycle_path,vertex AS repeated_vertex,total_cost AS cycle_cost
FROM walks WHERE is_cycle ORDER BY cycle_path;
```

The guard checks the previous state rather than excluding the closing edge outright. That preserves a concrete witness of repetition and then prevents further expansion. The route beginning at a includes a prefix leading into the cycle, so the repeated vertex identifies where the cyclic portion closes. A depth-only diagnostic would show long paths without proving why they recur.

### Exercise 4: Report a truncated search honestly

Explore simple paths from a for at most two edges. Return vertex, min_hops, search_truncated for vertices reached within that budget, ordered by vertex. Set the global truncation flag true if any depth-two state has an outgoing target not already in its path.

**Expected:** Vertices a, b, c, d, e have minimum hops 0,1,1,2,2 and search_truncated=true. Vertex g is absent because it requires more than two hops, so absence cannot be called unreachable.

```sql
WITH RECURSIVE paths(vertex,path,hops) AS (
 VALUES('a'::text,ARRAY['a']::text[],0)
 UNION ALL
 SELECT e.target,p.path||e.target,p.hops+1
 FROM paths AS p JOIN deep4_edges AS e ON e.source=p.vertex
 WHERE p.hops<2 AND NOT(e.target=ANY(p.path))
), budget AS (
 SELECT EXISTS(SELECT 1 FROM paths AS p JOIN deep4_edges AS e ON e.source=p.vertex
               WHERE p.hops=2 AND NOT(e.target=ANY(p.path))) AS truncated
)
SELECT p.vertex,min(p.hops) AS min_hops,b.truncated AS search_truncated
FROM paths AS p CROSS JOIN budget AS b GROUP BY p.vertex,b.truncated ORDER BY p.vertex;
```

The depth condition bounds computation, while the separate boundary inspection asks whether unexplored continuations remain. The minimum observed hop count is valid for reached vertices in this breadth-depth enumeration, but the search is not complete for all reachability. The flag prevents a bounded operational budget from being mistaken for proof of nonexistence. Comparing with the complete reachability result reveals g as the concrete omitted reachable vertex.

### Exercise 5: Return cheapest path evidence for every vertex

Enumerate simple paths on this tiny nonnegative graph and choose the cheapest per vertex, breaking ties by fewer hops then lexicographic path. Left-join to all vertices and return vertex, total_cost, path ordered by vertex, preserving unreachable f with NULL cost/path.

**Expected:** Costs a 0, b1, c2, d3, e6, g4 have paths[a],[a, b],[a, b, c],[a, b, c, d],[a, b, e],[a, b, c, d, g]. Vertex f has NULL cost and path.

```sql
WITH RECURSIVE paths(vertex,path,total_cost) AS (
 VALUES('a'::text,ARRAY['a']::text[],0)
 UNION ALL
 SELECT e.target,p.path||e.target,p.total_cost+e.cost
 FROM paths AS p JOIN deep4_edges AS e ON e.source=p.vertex
 WHERE NOT(e.target=ANY(p.path))
), best AS (
 SELECT DISTINCT ON(vertex) vertex,total_cost,path FROM paths
 ORDER BY vertex,total_cost,cardinality(path),path
)
SELECT v.vertex,b.total_cost,b.path FROM deep4_vertices AS v
LEFT JOIN best AS b ON b.vertex=v.vertex ORDER BY v.vertex;
```

DISTINCT ON selects one route only after the ordering states the optimization and tie policy. The outer vertex table preserves unreachable nodes, making absence explicit instead of silently omitting them from a report. Nonnegative weights mean cycles cannot improve a minimum-cost route, so a simple-path optimum exists for reachable vertices. Enumeration can still grow exponentially and should not be advertised as a scalable shortest-path engine.

### Exercise 6: Separate processed dependencies from cyclic or blocked vertices

Repeatedly select the lexicographically smallest unprocessed vertex whose incoming prerequisites are all processed. Return vertex, processed, cyclic_or_blocked for every vertex ordered by vertex. Stop when no eligible vertex remains and label remaining vertices as cyclic or blocked, not all proven cycle members.

**Expected:** Only a and isolated f are processed. Vertices b, c, d, e, g are cyclic_or_blocked=true; e and g depend on the cycle but are not themselves on its directed loop.

```sql
WITH RECURSIVE steps(done) AS (
 VALUES(ARRAY[]::text[])
 UNION ALL
 SELECT s.done||candidate.vertex
 FROM steps AS s CROSS JOIN LATERAL (
  SELECT v.vertex FROM deep4_vertices AS v
  WHERE NOT(v.vertex=ANY(s.done))
    AND NOT EXISTS(SELECT 1 FROM deep4_edges AS e
                   WHERE e.target=v.vertex AND NOT(e.source=ANY(s.done)))
  ORDER BY v.vertex LIMIT 1
 ) AS candidate
), final AS (
 SELECT done FROM steps ORDER BY cardinality(done) DESC LIMIT 1
)
SELECT v.vertex,v.vertex=ANY(f.done) AS processed,
 NOT(v.vertex=ANY(f.done)) AS cyclic_or_blocked
FROM deep4_vertices AS v CROSS JOIN final AS f ORDER BY v.vertex;
```

Every step appends one previously unprocessed eligible vertex, so at most the number of vertices can be processed. The b-c-d cycle prevents any of its members from losing all unprocessed prerequisites, which also blocks downstream e and g. The remaining-set label deliberately avoids overclaiming exact cycle membership. The isolated vertex is eligible independently of reachability from a, showing that dependency ordering and single-source reachability answer different questions.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
