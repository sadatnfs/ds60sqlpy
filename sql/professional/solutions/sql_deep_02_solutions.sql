-- sql-deep-02: complete reference queries and exact result assertions

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

CREATE TEMP TABLE deep2_usage (customer_id integer PRIMARY KEY,revenue numeric NOT NULL,visits integer NOT NULL CHECK(visits>=0)) ON COMMIT DROP;
INSERT INTO deep2_usage VALUES (1,10,1),(2,90,3),(3,0,0);
CREATE TEMP TABLE deep2_stock (snapshot_id integer PRIMARY KEY,product_id integer NOT NULL,snapshot_day date NOT NULL,units integer NOT NULL) ON COMMIT DROP;
INSERT INTO deep2_stock VALUES (1,1,'2026-01-01',10),(2,1,'2026-01-02',12),(3,2,'2026-01-01',20),(4,2,'2026-01-02',17),(5,1,'2026-01-03',99);
CREATE TEMP TABLE deep2_orders (order_id integer PRIMARY KEY,amount numeric NOT NULL) ON COMMIT DROP;
INSERT INTO deep2_orders VALUES (1,100),(2,60),(3,40);
CREATE TEMP TABLE deep2_bridge (order_id integer NOT NULL,channel text NOT NULL,weight numeric NOT NULL CHECK(weight>=0 AND weight<=1),PRIMARY KEY(order_id,channel)) ON COMMIT DROP;
INSERT INTO deep2_bridge VALUES (1,'email',0.6),(1,'search',0.4),(2,'email',1.0),(3,'search',0.7),(3,'direct',0.2);
CREATE TEMP TABLE deep2_history (version_id integer PRIMARY KEY,customer_id integer NOT NULL,valid_from timestamptz NOT NULL,valid_to timestamptz NOT NULL,segment text NOT NULL,CHECK(valid_from<valid_to)) ON COMMIT DROP;
INSERT INTO deep2_history VALUES
 (11,1,'2026-01-01T00:00Z','2026-01-02T00:00Z','basic'),
 (12,1,'2026-01-02T00:00Z','2026-01-03T00:00Z','premium'),
 (21,2,'2026-01-01T00:00Z','2026-01-03T00:00Z','alpha'),
 (22,2,'2026-01-02T00:00Z','2026-01-04T00:00Z','beta');
CREATE TEMP TABLE deep2_events (event_id integer PRIMARY KEY,customer_id integer NOT NULL,occurred_at timestamptz NOT NULL) ON COMMIT DROP;
INSERT INTO deep2_events VALUES (1,1,'2026-01-01T12:00Z'),(2,1,'2026-01-02T00:00Z'),(3,2,'2026-01-02T12:00Z'),(4,3,'2026-01-02T12:00Z');

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises

-- 1. Preserve undefined customer ratios
SAVEPOINT exercise_1;
CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
SELECT customer_id,revenue,visits,revenue/NULLIF(visits,0) AS revenue_per_visit,
 visits>0 AS ratio_defined FROM deep2_usage ORDER BY customer_id;
SELECT customer_id,revenue,visits,revenue_per_visit,ratio_defined FROM answer_1 ORDER BY customer_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_1) ORDER BY customer_id),'[]'::jsonb) FROM answer_1) = '[{"customer_id": 1, "revenue": 10, "visits": 1, "revenue_per_visit": 10, "ratio_defined": true}, {"customer_id": 2, "revenue": 90, "visits": 3, "revenue_per_visit": 30, "ratio_defined": true}, {"customer_id": 3, "revenue": 0, "visits": 0, "revenue_per_visit": null, "ratio_defined": false}]'::jsonb,'sql-deep-02 exercise 1');
ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Compare ratio weighting and population counts
SAVEPOINT exercise_2;
CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
SELECT 'all_customers' AS metric_id,count(*) AS customer_count,
 count(revenue/NULLIF(visits,0)) AS defined_ratio_count,
 sum(revenue)/NULLIF(sum(visits),0) AS ratio_of_totals,
 avg(revenue/NULLIF(visits,0)) AS mean_customer_ratio
FROM deep2_usage;
SELECT metric_id,customer_count,defined_ratio_count,ratio_of_totals,mean_customer_ratio FROM answer_2 ORDER BY metric_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_2) ORDER BY metric_id),'[]'::jsonb) FROM answer_2) = '[{"metric_id": "all_customers", "customer_count": 3, "defined_ratio_count": 2, "ratio_of_totals": 25, "mean_customer_ratio": 20}]'::jsonb,'sql-deep-02 exercise 2');
ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Choose one state per product at a cutoff
SAVEPOINT exercise_3;
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
SELECT product_id,snapshot_day,units FROM (
 SELECT DISTINCT ON(product_id) product_id,snapshot_day,units,snapshot_id
 FROM deep2_stock WHERE snapshot_day<=DATE '2026-01-02'
 ORDER BY product_id,snapshot_day DESC,snapshot_id DESC
) AS latest ORDER BY product_id;
SELECT product_id,snapshot_day,units FROM answer_3 ORDER BY product_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_3) ORDER BY product_id),'[]'::jsonb) FROM answer_3) = '[{"product_id": 1, "snapshot_day": "2026-01-02", "units": 12}, {"product_id": 2, "snapshot_day": "2026-01-02", "units": 17}]'::jsonb,'sql-deep-02 exercise 3');
ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Audit allocation conservation before aggregation
SAVEPOINT exercise_4;
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
SELECT o.order_id,COALESCE(sum(b.weight),0) AS weight_sum
FROM deep2_orders AS o LEFT JOIN deep2_bridge AS b ON b.order_id=o.order_id
GROUP BY o.order_id HAVING COALESCE(sum(b.weight),0)<>1
ORDER BY o.order_id;
SELECT order_id,weight_sum FROM answer_4 ORDER BY order_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_4) ORDER BY order_id),'[]'::jsonb) FROM answer_4) = '[{"order_id": 3, "weight_sum": 0.9}]'::jsonb,'sql-deep-02 exercise 4');
ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Repair and reconcile a weighted allocation
SAVEPOINT exercise_5;
UPDATE deep2_bridge SET weight=0.3 WHERE order_id=3 AND channel='direct';
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
WITH weights AS (
 SELECT o.order_id,COALESCE(sum(b.weight),0) AS weight_sum
 FROM deep2_orders AS o LEFT JOIN deep2_bridge AS b ON b.order_id=o.order_id
 GROUP BY o.order_id
)
SELECT b.channel,sum(o.amount*b.weight) AS allocated_amount
FROM deep2_orders AS o JOIN deep2_bridge AS b ON b.order_id=o.order_id
WHERE NOT EXISTS(SELECT 1 FROM weights WHERE weight_sum<>1)
GROUP BY b.channel ORDER BY b.channel;
SELECT channel,allocated_amount FROM answer_5 ORDER BY channel;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_5) ORDER BY channel),'[]'::jsonb) FROM answer_5) = '[{"channel": "direct", "allocated_amount": 12}, {"channel": "email", "allocated_amount": 120}, {"channel": "search", "allocated_amount": 68}]'::jsonb,'sql-deep-02 exercise 5');
ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Expose temporal dimension ambiguity without multiplying events
SAVEPOINT exercise_6;
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
SELECT e.event_id,count(h.version_id) AS match_count,
 CASE WHEN count(h.version_id)=1 THEN min(h.segment) END AS segment,
 CASE WHEN count(h.version_id)=0 THEN 'missing'
      WHEN count(h.version_id)=1 THEN 'matched' ELSE 'ambiguous' END AS match_status
FROM deep2_events AS e LEFT JOIN deep2_history AS h
 ON h.customer_id=e.customer_id AND h.valid_from<=e.occurred_at AND e.occurred_at<h.valid_to
GROUP BY e.event_id ORDER BY e.event_id;
SELECT event_id,match_count,segment,match_status FROM answer_6 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_6) ORDER BY event_id),'[]'::jsonb) FROM answer_6) = '[{"event_id": 1, "match_count": 1, "segment": "basic", "match_status": "matched"}, {"event_id": 2, "match_count": 1, "segment": "premium", "match_status": "matched"}, {"event_id": 3, "match_count": 2, "segment": null, "match_status": "ambiguous"}, {"event_id": 4, "match_count": 0, "segment": null, "match_status": "missing"}]'::jsonb,'sql-deep-02 exercise 6');
ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
