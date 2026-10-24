-- SQL-QUALITY-01: Bag Reconciliation and Join Fanout
-- Guide: sql/professional/companion-guides/sql_quality_01_bags_and_fanout.md
-- Use Create/open guided SQL notebook and the ignored learner copy.
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
CREATE TEMP TABLE quality_source (
  invoice_id integer PRIMARY KEY,
  amount numeric
) ON COMMIT DROP;
CREATE TEMP TABLE quality_target (
  invoice_id integer PRIMARY KEY,
  amount numeric
) ON COMMIT DROP;
INSERT INTO quality_source
VALUES
  (1, 100),
  (2, 50),
  (3, 0),
  (4, 80);
INSERT INTO quality_target
VALUES
  (1, 100),
  (2, 40),
  (3, 0),
  (5, 90);
CREATE TEMP TABLE quality_sent (
  invoice_id integer,
  amount numeric
) ON COMMIT DROP;
CREATE TEMP TABLE quality_received (
  invoice_id integer,
  amount numeric
) ON COMMIT DROP;
INSERT INTO quality_sent
VALUES
  (1, 100),
  (1, 100),
  (2, 50);
INSERT INTO quality_received
VALUES
  (1, 100),
  (2, 50),
  (2, 50);
CREATE TEMP TABLE quality_orders (
  order_id integer PRIMARY KEY
) ON COMMIT DROP;
CREATE TEMP TABLE quality_lines (
  line_id integer PRIMARY KEY,
  order_id integer,
  amount numeric
) ON COMMIT DROP;
CREATE TEMP TABLE quality_attempts (
  attempt_id integer PRIMARY KEY,
  order_id integer,
  amount numeric
) ON COMMIT DROP;
INSERT INTO quality_orders
VALUES
  (1),
  (2),
  (3);
INSERT INTO quality_lines
VALUES
  (11, 1, 60),
  (12, 1, 40),
  (21, 2, 50);
INSERT INTO quality_attempts
VALUES
  (101, 1, 100),
  (102, 1, 100),
  (201, 2, 50);
-- Example 1: Equal summaries conceal changed identities
-- Expected: Two summary rows keyed by origin, columns origin, row_count, amount_total. Both totals equal 230 and both counts equal 4.
SELECT
  'source' AS origin,
  count(*) AS row_count,
  sum(amount) AS amount_total
FROM
  quality_source
UNION ALL
SELECT
  'target',
  count(*),
  sum(amount)
FROM
  quality_target
ORDER BY
  origin;
-- Example 2: Aggregate separate children before joining
-- Expected: Three order rows; columns order_id, line_total, attempted_total: (1,100,200),(2,50,50),(3,0,0).
WITH lines AS (
  SELECT
    order_id,
    sum(amount) AS line_total
  FROM
    quality_lines
  GROUP BY
    order_id
),
attempts AS (
  SELECT
    order_id,
    sum(amount) AS attempted_total
  FROM
    quality_attempts
  GROUP BY
    order_id
)
SELECT
  o.order_id,
  COALESCE(l.line_total, 0) AS line_total,
  COALESCE(a.attempted_total, 0) AS attempted_total
FROM
  quality_orders AS o
  LEFT JOIN lines AS l ON l.order_id = o.order_id
  LEFT JOIN attempts AS a ON a.order_id = o.order_id
ORDER BY
  o.order_id;
-- Exercises
-- Keep predictions and attempts in your own working copy.
-- 1. Disprove summary equality.
-- Inputs/evidence: For sql-quality-01 Exercise 1, Compare quality_source and quality_target using one row per origin with origin, row_count, amount_total. Explain one concrete mismatch the summary cannot reveal.
-- Expected result/shape: For sql-quality-01 Exercise 1, Two summary rows keyed by origin, columns origin, row_count, amount_total; final ORDER BY origin. Both counts are 4 and totals are 230 despite differing invoice contents.
-- Verify: For sql-quality-01 Exercise 1, Inspect changed invoice 2 and the replacement of identity 4 by 5 while confirming both summaries still report four rows and amount_total 230.
-- Hint: Keep the aggregate as a control, then inspect invoice 2 and identities 4 and 5.
-- 2. Report keyed mismatches in both directions.
-- Inputs/evidence: For sql-quality-01 Exercise 2, Use FULL OUTER JOIN on invoice_id and NULL-safe amount comparison. Return invoice_id, source_amount, target_amount, difference_kind with missing_target, missing_source, or changed.
-- Expected result/shape: For sql-quality-01 Exercise 2, Three invoice rows keyed by invoice_id, columns invoice_id, source_amount, target_amount, difference_kind; final ORDER BY invoice_id: 2 changed (50,40), 4 missing_target (80,NULL), 5 missing_source (NULL,90).
-- Verify: For sql-quality-01 Exercise 2, Compare exact diagnostics for invoices 2,4,5 with kinds changed,missing_target,missing_source and amounts (50,40),(80,NULL),(NULL,90). Matching keys 1 and 3 are absent.
-- Hint: Use key presence to classify an absent row before comparing its amount.
-- 3. Preserve duplicate multiplicity.
-- Inputs/evidence: For sql-quality-01 Exercise 3, Compare quality_sent and quality_received as bags on invoice_id, amount using two EXCEPT ALL branches labeled sent_only and received_only. Explain why ordinary EXCEPT would miss this difference.
-- Expected result/shape: For sql-quality-01 Exercise 3, Two unmatched occurrence rows, columns direction, invoice_id, amount; final ORDER BY direction, invoice_id, amount: received_only (2,50), sent_only (1,100). An occurrence has no independent ID; (direction,invoice_id,amount) is a value tuple and may repeat in larger bags.
-- Verify: For sql-quality-01 Exercise 3, Count one sent-only occurrence (1,100) and one received-only occurrence (2,50). Repeat with ordinary EXCEPT and explain why its empty difference hides the changed multiplicities.
-- Hint: Run both directions before adding UNION ALL; do not insert DISTINCT.
-- 4. Repair independent-child fanout.
-- Inputs/evidence: For sql-quality-01 Exercise 4, Return order_id, line_total, attempted_total for all quality_orders. Aggregate quality_lines and quality_attempts separately before joining. Diagnose the raw two-child join on order 1.
-- Expected result/shape: For sql-quality-01 Exercise 4, Three order rows, columns order_id, line_total, attempted_total; final ORDER BY order_id: (1,100,200),(2,50,50),(3,0,0). The raw order-1 join has four pairs and incorrectly sums lines to 200.
-- Verify: For sql-quality-01 Exercise 4, Check all three order_id values survive, reconcile each metric with a separate child-only sum, and expose the raw order-1 join with four pairs and incorrect line sum 200.
-- Hint: A parent with two rows in each independent child has 2 x 2 matched pairs.
-- 5. Detect a missingness transition.
-- Inputs/evidence: For sql-quality-01 Exercise 5, Compare a source invoice (6,NULL::numeric) with target invoice (6,0::numeric). Return invoice_id, source_amount, target_amount only when the amounts differ under a missingness-sensitive contract.
-- Expected result/shape: For sql-quality-01 Exercise 5, One invoice row keyed by invoice_id, columns invoice_id, source_amount, target_amount; final ORDER BY invoice_id: (6,NULL,0). The keyed row exists on both sides.
-- Verify: For sql-quality-01 Exercise 5, Inspect the one row with NULL source and known zero target. Coalescing both sides to zero hides the mismatch, while ordinary inequality fails to qualify it.
-- Hint: Replacing both values with zero before comparison destroys this diagnostic.
-- 6. Gate a keyed comparison on valid identity.
-- Inputs/evidence: For sql-quality-01 Exercise 6, For quality_sent, return invoice_id, occurrences only for duplicate keys. Explain why a keyed reconciliation must stop before joining this fixture to another nonunique extract.
-- Expected result/shape: For sql-quality-01 Exercise 6, One diagnostic row keyed by invoice_id, columns invoice_id, occurrences; final ORDER BY invoice_id: (1,2). No amount is used as an identity.
-- Verify: For sql-quality-01 Exercise 6, Require exactly duplicate-key diagnostic (invoice_id=1,occurrences=2). This nonempty result prevents interpreting a later keyed join as one diagnostic per invoice.
-- Hint: Validate the key at the incoming extract grain before validating its attributes.
ROLLBACK;
