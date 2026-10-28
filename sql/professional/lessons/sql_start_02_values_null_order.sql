-- SQL-START-02: Values NULL and Deterministic Order
-- Guide: sql/professional/companion-guides/sql_start_02_values_null_order.md
-- Use ./classroom -> PostgreSQL -> sql-start-02 and its saved learner copy.
-- Select "Whole SQL lesson (psql)"; Docker supplies the client.
-- Run the complete file with psql -X -v ON_ERROR_STOP=1.
-- Only the local disposable advanced_sql_training database is permitted.
-- Setup is supplied. Write attempts before the final ROLLBACK.
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

CREATE TEMP TABLE start_shipments (
  shipment_id integer PRIMARY KEY,
  weight numeric,
  label text
) ON COMMIT DROP;

INSERT INTO start_shipments (shipment_id, weight, label)
VALUES
  (1, 0, ''),
  (2, NULL, NULL),
  (3, 5, 'ready'),
  (4, 5, ''),
  (5, NULL, 'hold');

-- Example 1: Inspect truth before filtering
-- Expected: Five shipment rows; columns shipment_id, weight, is_positive, is_missing. True positive IDs are 3 and 4; missing IDs are 2 and 5.
SELECT
  shipment_id,
  weight,
  weight > 0 AS is_positive,
  weight IS NULL AS is_missing
FROM
  start_shipments
ORDER BY
  shipment_id;

-- Example 2: Rank known values while preserving unknowns
-- Expected: IDs 3,4,1,2,5, with columns shipment_id, weight, label. The NULL weights remain NULL.
SELECT
  shipment_id,
  weight,
  label
FROM
  start_shipments
ORDER BY
  weight DESC NULLS LAST,
  shipment_id;

-- Exercises
-- Keep predictions and attempts in your own working copy.
-- 1. Inspect missingness.
-- Inputs/evidence: For sql-start-02 Exercise 1, Return shipment_id, weight, and weight IS NULL named is_missing for every shipment. Predict the Boolean column before executing.
-- Expected result/shape: For sql-start-02 Exercise 1, Five shipment rows with columns shipment_id, weight, is_missing; final ORDER BY shipment_id. is_missing is true only for IDs 2 and 5.
-- Verify: For sql-start-02 Exercise 1, Inspect true only at shipment_id 2 and 5; ID 1 has zero weight and a false is_missing flag. The missingness test itself never produces unknown.
-- Hint: Show the missingness test in SELECT before trying a WHERE condition.
-- 2. Compare a complement with missingness.
-- Inputs/evidence: For sql-start-02 Exercise 2, Return shipment_id, weight for NOT (weight > 0). Explain why the result is not the complement of the positive-weight result over all five shipments.
-- Expected result/shape: For sql-start-02 Exercise 2, One row keyed by shipment_id with columns shipment_id, weight, final ORDER BY shipment_id: (1,0). Unknown IDs 2 and 5 are absent from both positive and negated filters.
-- Verify: For sql-start-02 Exercise 2, Inspect the projected predicate values for all five input rows: ID 1 is false, IDs 3 and 4 true, IDs 2 and 5 unknown. Only ID 1 qualifies after ordinary negation.
-- Hint: NOT unknown is still unknown.
-- 3. Keep unknown and zero as separate categories.
-- Inputs/evidence: For sql-start-02 Exercise 3, Return shipment_id, weight for weights that are known zero or missing. Use explicit predicates rather than replacing unknown weights with zero.
-- Expected result/shape: For sql-start-02 Exercise 3, Three shipment rows with columns shipment_id, weight, final ORDER BY shipment_id: IDs 1,2,5. ID 1 is zero; IDs 2 and 5 remain NULL.
-- Verify: For sql-start-02 Exercise 3, Require identities 1,2,5 and exactly two NULL weights. Inspect the original measurements to prove selection did not replace unknown values with zero.
-- Hint: Combine the zero comparison and missingness test with OR.
-- 4. Specify every ordering decision.
-- Inputs/evidence: For sql-start-02 Exercise 4, Return the top two known weights with shipment_id, weight. Use descending weight, NULLS LAST, and ascending shipment_id before LIMIT 2.
-- Expected result/shape: For sql-start-02 Exercise 4, Two rows keyed by shipment_id, columns shipment_id, weight, final ORDER BY weight DESC NULLS LAST, shipment_id: IDs 3 and 4, each weight 5.
-- Verify: For sql-start-02 Exercise 4, Inspect ordered IDs 3 then 4 and both weights 5; repeat on unchanged input and justify the unique identity tie-breaker rather than relying on one observed storage order.
-- Hint: Tied measurements require an identity even with a small LIMIT.
-- 5. Debug an empty text display policy.
-- Inputs/evidence: For sql-start-02 Exercise 5, Return shipment_id, label, and a display_label that uses (unlabeled) for both NULL and empty text. Explain why COALESCE(label, '(unlabeled)') alone misses IDs 1 and 4.
-- Expected result/shape: For sql-start-02 Exercise 5, Five shipment rows with columns shipment_id, label, display_label; final ORDER BY shipment_id. Display labels in ID order are (unlabeled),(unlabeled),ready,(unlabeled),hold; original empty labels remain empty.
-- Verify: For sql-start-02 Exercise 5, Compare all five display_label values and inspect original labels beside them: IDs 1 and 4 remain empty strings, while ID 2 remains NULL.
-- Hint: Convert exactly empty text to NULL before selecting a fallback.
-- 6. Transfer to a NULL-safe change detector.
-- Inputs/evidence: For sql-start-02 Exercise 6, Compare old and new weights (10,NULL,NULL), (11,0,NULL), (12,5,5), (13,NULL,0), named shipment_id, old_weight, new_weight. Return shipment_id, old_weight, new_weight only for changed values, including missingness transitions.
-- Expected result/shape: For sql-start-02 Exercise 6, Two changed shipment rows, columns shipment_id, old_weight, new_weight, final ORDER BY shipment_id: IDs 11 and 13. Two unknowns at ID 10 do not count as a change.
-- Verify: For sql-start-02 Exercise 6, Require changed IDs 11 and 13. Check that both negative controls are absent: ID 10 has two unknown values, and ID 12 has the same known value twice.
-- Hint: IS DISTINCT FROM gives a definite result when either operand is NULL.
ROLLBACK;
