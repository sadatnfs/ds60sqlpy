-- sql-deep-02: Metric Algebra Across Grains, Snapshots, and Weighted Bridges
-- Guide: sql/professional/companion-guides/sql_deep_02.md
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

CREATE TEMP TABLE deep2_usage (
  customer_id integer PRIMARY KEY,
  revenue numeric NOT NULL,
  visits integer NOT NULL CHECK (visits >= 0)
) ON COMMIT DROP;

INSERT INTO deep2_usage
VALUES
  (1, 10, 1),
  (2, 90, 3),
  (3, 0, 0);

CREATE TEMP TABLE deep2_stock (
  snapshot_id integer PRIMARY KEY,
  product_id integer NOT NULL,
  snapshot_day date NOT NULL,
  units integer NOT NULL
) ON COMMIT DROP;

INSERT INTO deep2_stock
VALUES
  (1, 1, '2026-01-01', 10),
  (2, 1, '2026-01-02', 12),
  (3, 2, '2026-01-01', 20),
  (4, 2, '2026-01-02', 17),
  (5, 1, '2026-01-03', 99);

CREATE TEMP TABLE deep2_orders (
  order_id integer PRIMARY KEY,
  amount numeric NOT NULL
) ON COMMIT DROP;

INSERT INTO deep2_orders
VALUES
  (1, 100),
  (2, 60),
  (3, 40);

CREATE TEMP TABLE deep2_bridge (
  order_id integer NOT NULL,
  channel text NOT NULL,
  weight numeric NOT NULL CHECK (weight >= 0 AND weight <= 1),
  PRIMARY KEY (order_id, channel)
) ON COMMIT DROP;

INSERT INTO deep2_bridge
VALUES
  (1, 'email', 0.6),
  (1, 'search', 0.4),
  (2, 'email', 1.0),
  (3, 'search', 0.7),
  (3, 'direct', 0.2);

CREATE TEMP TABLE deep2_history (
  version_id integer PRIMARY KEY,
  customer_id integer NOT NULL,
  valid_from timestamptz NOT NULL,
  valid_to timestamptz NOT NULL,
  segment text NOT NULL,
  CHECK (valid_from < valid_to)
) ON COMMIT DROP;

INSERT INTO deep2_history
VALUES
  (11, 1, '2026-01-01T00:00Z', '2026-01-02T00:00Z', 'basic'),
  (12, 1, '2026-01-02T00:00Z', '2026-01-03T00:00Z', 'premium'),
  (21, 2, '2026-01-01T00:00Z', '2026-01-03T00:00Z', 'alpha'),
  (22, 2, '2026-01-02T00:00Z', '2026-01-04T00:00Z', 'beta');

CREATE TEMP TABLE deep2_events (
  event_id integer PRIMARY KEY,
  customer_id integer NOT NULL,
  occurred_at timestamptz NOT NULL
) ON COMMIT DROP;

INSERT INTO deep2_events
VALUES
  (1, 1, '2026-01-01T12:00Z'),
  (2, 1, '2026-01-02T00:00Z'),
  (3, 2, '2026-01-02T12:00Z'),
  (4, 3, '2026-01-02T12:00Z');

-- Worked example 1
WITH groups (
  group_id,
  successes,
  trials
) AS (
  VALUES ('small', 1::numeric, 2),
    ('large', 9::numeric, 10))
SELECT
  'population' AS metric_id,
  round(sum(successes) / sum(trials), 3) AS trial_weighted_rate,
  round(avg(successes / trials), 3) AS equal_group_rate
FROM
  groups;

-- Worked example 2
WITH states (
  day,
  product_id,
  units
) AS (
  VALUES (DATE '2026-01-01', 1, 10),
    (DATE '2026-01-01', 2, 20),
    (DATE '2026-01-02', 1, 12),
    (DATE '2026-01-02', 2, 17))
SELECT
  day,
  sum(units) AS units_at_day
FROM
  states
GROUP BY
  day
ORDER BY
  day;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.
-- 1. Preserve undefined customer ratios
-- Inputs/evidence: For sql-deep-02 Exercise 1, Return customer_id, revenue, visits, revenue_per_visit, ratio_defined from `deep2_usage`, one row per customer ordered by customer_id. Use NULLIF for a zero denominator and retain the zero-visit customer.
-- Expected result/shape: For sql-deep-02 Exercise 1, Customer 1 ratio 10, true; customer 2 ratio 30, true; customer 3 ratioNULL, false. Revenue/visits remain 10/1,90/3,0/0.
-- Verify: For sql-deep-02 Exercise 1, recompute each numerator and denominator from its customer rows; retain a NULL ratio when the denominator is zero rather than substituting an observed zero.
-- 2. Compare ratio weighting and population counts
-- Inputs/evidence: For sql-deep-02 Exercise 2, Return one row keyed by metric_id=all_customers with columns metric_id, customer_count, defined_ratio_count, ratio_of_totals, mean_customer_ratio. Compute both ratio targets from the same source, retaining the denominator policy from Exercise 1.
-- Expected result/shape: For sql-deep-02 Exercise 2, The row is all_customers,3,2,25,20. Ratio of totals uses 100 revenue/4 visits, while the mean customer ratio averages 10 and 30.
-- Verify: For sql-deep-02 Exercise 2, calculate the pooled numerator divided by the pooled denominator independently of the average of defined customer ratios; report how many customer ratios each calculation includes.
-- 3. Choose one state per product at a cutoff
-- Inputs/evidence: For sql-deep-02 Exercise 3, As of 2026-01-02, return product_id, snapshot_day, units from the latest eligible stock snapshot per product. Break same-day ties by greatest snapshot_id. One row represents one product and final order is product_id. Exclude the future January 3 snapshot.
-- Expected result/shape: For sql-deep-02 Exercise 3, Product 1 uses January 2 units 12 and product 2 uses January 2 units 17. Their as-of total is 29; product 1 future units 99 must not enter.
-- Verify: For sql-deep-02 Exercise 3, check the chosen timestamp is at or before the cutoff and no later eligible snapshot exists for the same product; sum only those chosen states.
-- 4. Audit allocation conservation before aggregation
-- Inputs/evidence: For sql-deep-02 Exercise 4, Return order_id, weight_sum only for orders whose total bridge weight is not exactly 1, including orders with no bridge rows. Preserve one diagnostic row per invalid order and order by order_id. Use exact numeric weights from the fixture.
-- Expected result/shape: For sql-deep-02 Exercise 4, Only order 3 appears with weight_sum0.9. Orders 1 and 2 sum to 1. The diagnostic must exist before any channel totals are treated as complete allocations.
-- Verify: For sql-deep-02 Exercise 4, sum the bridge weights separately for each source identity before multiplying amounts; inspect the per-source weight-sum output to identify the source whose weights fail conservation.
-- 5. Repair and reconcile a weighted allocation
-- Inputs/evidence: For sql-deep-02 Exercise 5, Within this exercise savepoint, change order 3 direct weight to 0.3. Return channel, allocated_amount ordered by channel, requiring every order weight total to equal 1 before producing any allocations. Verify that channel amounts sum to original order total 200.
-- Expected result/shape: For sql-deep-02 Exercise 5, Rows are direct 12, email 120, search 68. A failed global weight gate would return no allocation rows rather than silently exclude the invalid order. Roll back the repair after the case.
-- Verify: For sql-deep-02 Exercise 5, compare the repaired source-level weight sums with one and reconcile the allocated total to the original source total; inspect the named destination allocation as well.
-- 6. Expose temporal dimension ambiguity without multiplying events
-- Inputs/evidence: For sql-deep-02 Exercise 6, For every event return event_id, match_count, segment, match_status. Match customer history over valid_from<=occurred_at<valid_to. Only exactly one version supplies segment; zero matches is missing and multiple matches is ambiguous. One row per event, ordered by event_id.
-- Expected result/shape: For sql-deep-02 Exercise 6, Event 1 is 1, basic, matched; event 2 is 1, premium, matched; event 3 is 2, NULL, ambiguous; event 4 is 0, NULL, missing. The exact January 2 boundary belongs only to premium.
-- Verify: For sql-deep-02 Exercise 6, count effective interval matches per event before choosing a dimension value; preserve an event with zero matches and expose an event with multiple matches instead of arbitrary deduplication.
ROLLBACK;
