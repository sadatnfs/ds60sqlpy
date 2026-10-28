-- sql-deep-04: complete reference queries and exact result assertions
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

CREATE TEMP TABLE deep4_vertices (
  vertex text PRIMARY KEY
) ON COMMIT DROP;

INSERT INTO deep4_vertices
VALUES
  ('a'),
  ('b'),
  ('c'),
  ('d'),
  ('e'),
  ('f'),
  ('g');

CREATE TEMP TABLE deep4_edges (
  source text NOT NULL,
  target text NOT NULL,
  cost integer NOT NULL CHECK (cost >= 0),
  PRIMARY KEY (source, target)
) ON COMMIT DROP;

INSERT INTO deep4_edges
VALUES
  ('a', 'b', 1),
  ('a', 'c', 4),
  ('b', 'c', 1),
  ('c', 'd', 1),
  ('d', 'b', 1),
  ('b', 'e', 5),
  ('d', 'g', 1);

CREATE FUNCTION pg_temp.assert_true (ok boolean, message text)
  RETURNS void
  LANGUAGE plpgsql
  AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$
;
-- Exercises
-- 1. Compute reachability with a finite identity state
SAVEPOINT exercise_1;

CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
WITH RECURSIVE reachable (
  vertex
) AS (
  VALUES ('a'::text)
  UNION
  SELECT
    e.target
  FROM
    reachable AS r
    JOIN deep4_edges AS e ON e.source = r.vertex
)
SELECT
  vertex
FROM
  reachable
ORDER BY
  vertex;

SELECT
  vertex
FROM
  answer_1
ORDER BY
  vertex;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_1)
      ORDER BY vertex), '[]'::jsonb)
    FROM answer_1) = '[{"vertex": "a"}, {"vertex": "b"}, {"vertex": "c"}, {"vertex": "d"}, {"vertex": "e"}, {"vertex": "g"}]'::jsonb, 'sql-deep-04 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. Enumerate simple routes to a target
SAVEPOINT exercise_2;

CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
WITH RECURSIVE paths (
  vertex,
  path,
  total_cost
) AS (
  VALUES ('a'::text, ARRAY['a']::text[], 0)
  UNION ALL
  SELECT
    e.target,
    p.path || e.target,
    p.total_cost + e.cost
  FROM
    paths AS p
    JOIN deep4_edges AS e ON e.source = p.vertex
  WHERE
    NOT (e.target = ANY (p.path)))
SELECT
  path, total_cost, cardinality(path) - 1 AS hops
FROM
  paths
WHERE
  vertex = 'd'
ORDER BY
  path;

SELECT
  path,
  total_cost,
  hops
FROM
  answer_2
ORDER BY
  path;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_2)
      ORDER BY path), '[]'::jsonb)
    FROM answer_2) = '[{"path": ["a", "b", "c", "d"], "total_cost": 3, "hops": 3}, {"path": ["a", "c", "d"], "total_cost": 5, "hops": 2}]'::jsonb, 'sql-deep-04 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. Emit one cycle-closing step as evidence
SAVEPOINT exercise_3;

CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
WITH RECURSIVE walks (
  vertex,
  path,
  total_cost,
  is_cycle
) AS (
  VALUES ('a'::text, ARRAY['a']::text[], 0, false)
  UNION ALL
  SELECT
    e.target,
    w.path || e.target,
    w.total_cost + e.cost,
    e.target = ANY (w.path)
  FROM
    walks AS w
    JOIN deep4_edges AS e ON e.source = w.vertex
  WHERE
    NOT w.is_cycle
)
SELECT
  path AS cycle_path, vertex AS repeated_vertex, total_cost AS cycle_cost
FROM
  walks
WHERE
  is_cycle
ORDER BY
  cycle_path;

SELECT
  cycle_path,
  repeated_vertex,
  cycle_cost
FROM
  answer_3
ORDER BY
  cycle_path;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_3)
      ORDER BY cycle_path), '[]'::jsonb)
    FROM answer_3) = '[{"cycle_path": ["a", "b", "c", "d", "b"], "repeated_vertex": "b", "cycle_cost": 4}, {"cycle_path": ["a", "c", "d", "b", "c"], "repeated_vertex": "c", "cycle_cost": 7}]'::jsonb, 'sql-deep-04 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. Report a truncated search honestly
SAVEPOINT exercise_4;

CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
WITH RECURSIVE paths (
  vertex,
  path,
  hops
) AS (
  VALUES ('a'::text, ARRAY['a']::text[], 0)
  UNION ALL
  SELECT
    e.target,
    p.path || e.target,
    p.hops + 1
  FROM
    paths AS p
    JOIN deep4_edges AS e ON e.source = p.vertex
  WHERE
    p.hops < 2
    AND NOT (e.target = ANY (p.path))
),
budget AS (
  SELECT
    EXISTS (
      SELECT
        1
      FROM
        paths AS p
        JOIN deep4_edges AS e ON e.source = p.vertex
      WHERE
        p.hops = 2
        AND NOT (e.target = ANY (p.path))) AS truncated
)
SELECT
  p.vertex, min(p.hops) AS min_hops, b.truncated AS search_truncated
FROM
  paths AS p
  CROSS JOIN budget AS b
GROUP BY
  p.vertex, b.truncated
ORDER BY
  p.vertex;

SELECT
  vertex,
  min_hops,
  search_truncated
FROM
  answer_4
ORDER BY
  vertex;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_4)
      ORDER BY vertex), '[]'::jsonb)
    FROM answer_4) = '[{"vertex": "a", "min_hops": 0, "search_truncated": true}, {"vertex": "b", "min_hops": 1, "search_truncated": true}, {"vertex": "c", "min_hops": 1, "search_truncated": true}, {"vertex": "d", "min_hops": 2, "search_truncated": true}, {"vertex": "e", "min_hops": 2, "search_truncated": true}]'::jsonb, 'sql-deep-04 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. Return cheapest path evidence for every vertex
SAVEPOINT exercise_5;

CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
WITH RECURSIVE paths (
  vertex,
  path,
  total_cost
) AS (
  VALUES ('a'::text, ARRAY['a']::text[], 0)
  UNION ALL
  SELECT
    e.target,
    p.path || e.target,
    p.total_cost + e.cost
  FROM
    paths AS p
    JOIN deep4_edges AS e ON e.source = p.vertex
  WHERE
    NOT (e.target = ANY (p.path))
),
best AS (
  SELECT DISTINCT ON (vertex)
    vertex,
    total_cost,
    path
  FROM
    paths
  ORDER BY
    vertex,
    total_cost,
    cardinality(path),
    path
)
SELECT
  v.vertex, b.total_cost, b.path
FROM
  deep4_vertices AS v
  LEFT JOIN best AS b ON b.vertex = v.vertex
ORDER BY
  v.vertex;

SELECT
  vertex,
  total_cost,
  path
FROM
  answer_5
ORDER BY
  vertex;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_5)
      ORDER BY vertex), '[]'::jsonb)
    FROM answer_5) = '[{"vertex": "a", "total_cost": 0, "path": ["a"]}, {"vertex": "b", "total_cost": 1, "path": ["a", "b"]}, {"vertex": "c", "total_cost": 2, "path": ["a", "b", "c"]}, {"vertex": "d", "total_cost": 3, "path": ["a", "b", "c", "d"]}, {"vertex": "e", "total_cost": 6, "path": ["a", "b", "e"]}, {"vertex": "f", "total_cost": null, "path": null}, {"vertex": "g", "total_cost": 4, "path": ["a", "b", "c", "d", "g"]}]'::jsonb, 'sql-deep-04 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. Separate processed dependencies from cyclic or blocked vertices
SAVEPOINT exercise_6;

CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
WITH RECURSIVE steps (
  done
) AS (
  VALUES (ARRAY[]::text[])
  UNION ALL
  SELECT
    s.done || candidate.vertex
  FROM
    steps AS s
    CROSS JOIN LATERAL (
      SELECT
        v.vertex
      FROM
        deep4_vertices AS v
      WHERE
        NOT (v.vertex = ANY (s.done))
        AND NOT EXISTS (
          SELECT
            1
          FROM
            deep4_edges AS e
          WHERE
            e.target = v.vertex
            AND NOT (e.source = ANY (s.done)))
        ORDER BY
          v.vertex
        LIMIT 1) AS candidate
),
final AS (
  SELECT
    done
  FROM
    steps
  ORDER BY
    cardinality(done) DESC
  LIMIT 1
)
SELECT
  v.vertex, v.vertex = ANY (f.done) AS processed, NOT (v.vertex = ANY (f.done)) AS cyclic_or_blocked
FROM
  deep4_vertices AS v
  CROSS JOIN final AS f
ORDER BY
  v.vertex;

SELECT
  vertex,
  processed,
  cyclic_or_blocked
FROM
  answer_6
ORDER BY
  vertex;

SELECT
  pg_temp.assert_true ((
    SELECT
      COALESCE(jsonb_agg(to_jsonb (answer_6)
      ORDER BY vertex), '[]'::jsonb)
    FROM answer_6) = '[{"vertex": "a", "processed": true, "cyclic_or_blocked": false}, {"vertex": "b", "processed": false, "cyclic_or_blocked": true}, {"vertex": "c", "processed": false, "cyclic_or_blocked": true}, {"vertex": "d", "processed": false, "cyclic_or_blocked": true}, {"vertex": "e", "processed": false, "cyclic_or_blocked": true}, {"vertex": "f", "processed": true, "cyclic_or_blocked": false}, {"vertex": "g", "processed": false, "cyclic_or_blocked": true}]'::jsonb, 'sql-deep-04 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
