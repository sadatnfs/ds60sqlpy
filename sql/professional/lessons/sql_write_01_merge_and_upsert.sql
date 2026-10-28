-- SQL-WRITE-01: PostgreSQL 17 change application with MERGE and ON CONFLICT
-- Guide: sql/professional/companion-guides/sql_write_01_merge_and_upsert.md
-- Run ./classroom -> PostgreSQL -> sql-write-01 -> Whole SQL lesson (psql).
-- Docker supplies the client and disposable advanced_sql_training database.
-- Fixture, worked changes and practice slots are temporary and roll back.
\set ON_ERROR_STOP on
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
  IF current_setting('server_version_num')::integer < 170000 THEN
    RAISE EXCEPTION 'This lesson requires the prepared PostgreSQL 17 or newer runtime';
  END IF;
END
$course_target$;

SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE w17_stock (
  sku text PRIMARY KEY,
  quantity integer NOT NULL CHECK (quantity >= 0),
  source_version integer NOT NULL CHECK (source_version > 0)
) ON COMMIT DROP;

INSERT INTO w17_stock
VALUES
  ('A', 10, 1),
  ('B', 3, 1),
  ('Z', 5, 1);

CREATE TEMP TABLE w17_feed (
  sku text NOT NULL,
  quantity integer NOT NULL,
  source_version integer NOT NULL
) ON COMMIT DROP;

INSERT INTO w17_feed
VALUES
  ('A', 12, 2),
  ('B', 3, 1),
  ('C', 1, 1);

-- Worked case 1: this feed is explicitly a complete authoritative snapshot.
-- Match by business identity. Version eligibility belongs in WHEN, not ON.
-- Changed-row output has no promised display order: A UPDATE, C INSERT, Z DELETE.
MERGE INTO w17_stock AS t
  USING w17_feed AS s ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED BY SOURCE THEN
    DELETE
  WHEN NOT MATCHED BY TARGET THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version) RETURNING
  merge_action () AS action, t.sku, t.quantity, t.source_version;

SELECT
  sku,
  quantity,
  source_version
FROM
  w17_stock
ORDER BY
  sku;

-- Worked case 2: partial events leave absent keys alone and reject stale updates.
-- A advances, B's stale 999 is ignored, D is inserted and C remains present.
INSERT INTO w17_stock AS t (sku, quantity, source_version)
VALUES
  ('A', 14, 3),
  ('B', 999, 1),
  ('D', 4, 1)
ON CONFLICT (sku)
  DO UPDATE SET
    quantity = excluded.quantity,
    source_version = excluded.source_version
  WHERE
    excluded.source_version > t.source_version
  RETURNING
    sku, quantity, source_version;

SELECT
  sku,
  quantity,
  source_version
FROM
  w17_stock
ORDER BY
  sku;

-- A source that modifies one target twice has no implicit latest-version rule.
DO $duplicate_source$
BEGIN
  MERGE INTO w17_stock AS t
  USING (VALUES ('A',16,4),('A',17,5)) AS s(sku,quantity,source_version)
  ON t.sku = s.sku
  WHEN MATCHED THEN
    UPDATE SET quantity = s.quantity,source_version = s.source_version;
  RAISE EXCEPTION 'The duplicate source unexpectedly succeeded';
EXCEPTION WHEN cardinality_violation THEN
  RAISE NOTICE 'Expected cardinality violation; the subtransaction changed no target rows';
END
$duplicate_source$;

SELECT
  sku,
  quantity,
  source_version
FROM
  w17_stock
ORDER BY
  sku;

-- Each practice slot starts from this separate original fixture.
CREATE TEMP TABLE w17_practice_stock (
  LIKE w17_stock INCLUDING ALL
) ON COMMIT DROP;

INSERT INTO w17_practice_stock
VALUES
  ('A', 10, 1),
  ('B', 3, 1),
  ('Z', 5, 1);

CREATE TEMP TABLE w17_practice_feed (
  LIKE w17_feed INCLUDING ALL
) ON COMMIT DROP;

INSERT INTO w17_practice_feed
VALUES
  ('A', 12, 2),
  ('B', 3, 1),
  ('C', 1, 1);

-- Exercises
-- 1. [Prediction] Classify the full snapshot's INSERT, UPDATE, DELETE and no-action keys.
-- Inputs: For sql-write-01 Exercise 1, use the original w17_practice_stock target and complete w17_practice_feed, each with one row per sku.
-- Expected result/shape: For sql-write-01 Exercise 1, return action, sku, quantity, source_version for the three changed keys A/C/Z, without promising RETURNING order; display final sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1). The target identity is sku.
-- Verify: For sql-write-01 Exercise 1, compare the three action/key pairs with the independently ordered target rows. B has no returned action but remains present; deletion returns Z's old values.
-- Hint ladder, rung 1: Distinguish matching by sku from eligibility to update a matched row.
SAVEPOINT exercise_1;

-- Write your prediction and inspection queries here.
ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. [Query writing] Apply only A12v2 and C1v1 as partial events with MERGE.
-- Inputs: For sql-write-01 Exercise 2, use the original target and only partial source events (A,12,2) and (C,1,1), with one row per sku.
-- Expected result/shape: For sql-write-01 Exercise 2, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
-- Verify: For sql-write-01 Exercise 2, require Z to remain at quantity five and version one. Absence from a partial feed is not a deletion event; inspect the key set as well as quantities.
-- Hint ladder, rung 1: Use matched update eligibility and target-missing insert; do not delete absent source keys.
SAVEPOINT exercise_2;

-- Write your query here.
ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. [Debugging] Resolve a duplicate A feed using the greatest source_version before MERGE.
-- Inputs: For sql-write-01 Exercise 3, use the original target and source rows (A,12,2), (A,14,3), (C,1,1). Versions are unique within each sku, so the greatest version is an unambiguous winner.
-- Expected result/shape: For sql-write-01 Exercise 3, display sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
-- Verify: For sql-write-01 Exercise 3, show the deduplicated source with exactly one row per sku before mutation. Compare all four final key/value/version tuples; physical source order is not a conflict policy.
-- Hint ladder, rung 1: Rank within sku by source_version DESC, then select rank one.
SAVEPOINT exercise_3;

-- Write your inspection and repair here.
ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. [Query writing] Apply A14v3,B999v1,D4v1 with INSERT ... ON CONFLICT.
-- Inputs: For sql-write-01 Exercise 4, use the original target with its sku primary key and partial events (A,14,3), (B,999,1), (D,4,1).
-- Expected result/shape: For sql-write-01 Exercise 4, rETURNING contains only changed keys A/D. Display final sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (D,4,1), (Z,5,1), one row per sku.
-- Verify: For sql-write-01 Exercise 4, require B to retain quantity three and version one despite the stale proposed 999. Check Z remains five and distinguish a skipped update from a missing target.
-- Hint ladder, rung 1: Use excluded for proposed values and a version condition on DO UPDATE.
SAVEPOINT exercise_4;

-- Write your query here.
ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. [Verification] Apply the full snapshot twice and demonstrate converged target state.
-- Inputs: For sql-write-01 Exercise 5, use the original target and complete three-row w17_practice_feed. Run the same conditional full-snapshot MERGE twice within one exercise slot.
-- Expected result/shape: For sql-write-01 Exercise 5, the first run changes A/C/Z and the second changes zero rows. After each run, sku, quantity, source_version ordered by sku is (A,12,2), (B,3,1), (C,1,1), one row per sku.
-- Verify: For sql-write-01 Exercise 5, inspect the actual second statement's ROW_COUNT and compare all ordered target tuples after both runs. An equal grand total cannot prove correct identities or convergence.
-- Hint ladder, rung 1: The second run must not update equal versions or reinsert existing keys.
SAVEPOINT exercise_5;

-- Write your two runs and state checks here.
ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. [Extension] Guard full-snapshot deletion using a declared expected row count.
-- Inputs: For sql-write-01 Exercise 6, compare a declared expected snapshot count of three with an incomplete A/C source, then with the supplied complete A/B/C source. Row count is only one declared completeness condition.
-- Expected result/shape: For sql-write-01 Exercise 6, reject the incomplete source before MERGE and retain original (A,10,1), (B,3,1), (Z,5,1). After the complete source passes, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), one row per sku.
-- Verify: For sql-write-01 Exercise 6, require the explicit incomplete-snapshot rejection before any target mutation. Compare the unchanged original rows, then demonstrate the passing gate and complete final key set; equal counts alone do not establish source authenticity.
-- Hint ladder, rung 1: Completeness validation is a prerequisite for deletion, not a WHEN condition per row.
SAVEPOINT exercise_6;

-- Write your completeness guard and checks here.
ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
