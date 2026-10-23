-- sql-deep-04: Recursive Graph Reachability, Paths, Cycles, and Dependency Order
-- Guide: sql/professional/companion-guides/sql_deep_04.md
-- Use the complete file in the disposable advanced_sql_training database.

BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE deep4_vertices(vertex text PRIMARY KEY) ON COMMIT DROP;
INSERT INTO deep4_vertices VALUES ('a'),('b'),('c'),('d'),('e'),('f'),('g');
CREATE TEMP TABLE deep4_edges(source text NOT NULL,target text NOT NULL,cost integer NOT NULL CHECK(cost>=0),PRIMARY KEY(source,target)) ON COMMIT DROP;
INSERT INTO deep4_edges VALUES ('a','b',1),('a','c',4),('b','c',1),('c','d',1),('d','b',1),('b','e',5),('d','g',1);

-- Worked example 1
WITH RECURSIVE sequence(value) AS (
 VALUES(1)
 UNION ALL
 SELECT value+1 FROM sequence WHERE value<4
)
SELECT value,value*value AS square FROM sequence ORDER BY value;

-- Worked example 2
SELECT ARRAY['a','b','c']::text[] AS path,
       'b'=ANY(ARRAY['a','b','c']::text[]) AS revisits_b,
       ARRAY['a','b','c']::text[] || 'd'::text AS extended_path;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.

-- 1. Compute reachability with a finite identity state
-- Prompt: Starting at a, return vertex for every reachable vertex including a. Use recursive UNION over vertex identity only so the b-c-d cycle terminates. One output row represents one vertex, ordered by vertex.
-- Expected: Rows a, b, c, d, e, g appear once each; isolated f is absent. No arbitrary depth cap is required for this finite identity-state traversal.

-- 2. Enumerate simple routes to a target
-- Prompt: Return path, total_cost, hops for every simple path from a to d. Carry vertex, path, cost in the recursive state, append targets and prevent revisiting any vertex already in the path. One output row represents a complete path; order by path.
-- Expected: Paths[a, b, c, d] cost 3, hops 3 and [a, c, d] cost 5, hops 2 appear. The cheaper route has more hops, and no path repeats a vertex.

-- 3. Emit one cycle-closing step as evidence
-- Prompt: Return cycle_path, repeated_vertex, cycle_cost for traversals from a that first revisit a vertex. Allow a closing edge to be emitted, mark it as a cycle and stop expanding marked states. Order by cycle_path and do not claim that the whole path prefix is itself a cycle.
-- Expected: Paths[a, b, c, d, b] repeat b at cost 4 and [a, c, d, b, c] repeat c at cost 7. Both are emitted once and terminate.

-- 4. Report a truncated search honestly
-- Prompt: Explore simple paths from a for at most two edges. Return vertex, min_hops, search_truncated for vertices reached within that budget, ordered by vertex. Set the global truncation flag true if any depth-two state has an outgoing target not already in its path.
-- Expected: Vertices a, b, c, d, e have minimum hops 0,1,1,2,2 and search_truncated=true. Vertex g is absent because it requires more than two hops, so absence cannot be called unreachable.

-- 5. Return cheapest path evidence for every vertex
-- Prompt: Enumerate simple paths on this tiny nonnegative graph and choose the cheapest per vertex, breaking ties by fewer hops then lexicographic path. Left-join to all vertices and return vertex, total_cost, path ordered by vertex, preserving unreachable f with NULL cost/path.
-- Expected: Costs a 0, b1, c2, d3, e6, g4 have paths[a],[a, b],[a, b, c],[a, b, c, d],[a, b, e],[a, b, c, d, g]. Vertex f has NULL cost and path.

-- 6. Separate processed dependencies from cyclic or blocked vertices
-- Prompt: Repeatedly select the lexicographically smallest unprocessed vertex whose incoming prerequisites are all processed. Return vertex, processed, cyclic_or_blocked for every vertex ordered by vertex. Stop when no eligible vertex remains and label remaining vertices as cyclic or blocked, not all proven cycle members.
-- Expected: Only a and isolated f are processed. Vertices b, c, d, e, g are cyclic_or_blocked=true; e and g depend on the cycle but are not themselves on its directed loop.

ROLLBACK;
