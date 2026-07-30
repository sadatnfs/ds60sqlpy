-- Day 22 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
-- Assumptions: Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
-- Pitfall: Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Use a named window to show each order with customer count, average, first date, and last date.
-- Why: Name a full-partition customer window once and reuse it.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       COUNT(*) OVER customer_window AS customer_order_count,
       ROUND(AVG(o.total_amount) OVER customer_window, 2) AS customer_average,
       FIRST_VALUE(o.order_date) OVER customer_window AS first_order_date,
       LAST_VALUE(o.order_date) OVER customer_window AS last_order_date
FROM orders AS o
WINDOW customer_window AS (
  PARTITION BY o.customer_id
  ORDER BY o.order_date, o.order_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Compare each employee salary with the average of other employees in the department.
-- Why: Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
-- Expected: One row per employee with nullable peer average.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.employee_id,
       e.department_id,
       e.salary,
       ROUND(
         AVG(e.salary) OVER (
           PARTITION BY e.department_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
           EXCLUDE CURRENT ROW
         ),
         2
       ) AS other_employee_average
FROM employees AS e
ORDER BY e.department_id, e.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Show each order's distance from its customer's average and standard deviation.
-- Why: Compute independent partition windows and guard interpretation when variation is zero.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER customer_orders, 2) AS customer_average,
       ROUND(STDDEV_POP(o.total_amount) OVER customer_orders, 2) AS customer_stddev,
       ROUND(
         (o.total_amount - AVG(o.total_amount) OVER customer_orders)
           / NULLIF(STDDEV_POP(o.total_amount) OVER customer_orders, 0),
         4
       ) AS customer_z_score
FROM orders AS o
WINDOW customer_orders AS (PARTITION BY o.customer_id)
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Sessionize events using a 30-minute gap and predict why the first event starts a session.
-- Why: Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
-- Expected: One row per event with session number starting at one.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH sequenced AS (
  SELECT e.*,
         LAG(e.event_time) OVER (
           PARTITION BY e.customer_id
           ORDER BY e.event_time, e.event_id
         ) AS previous_event_time
  FROM events AS e
), flagged AS (
  SELECT sequenced.*,
         CASE
           WHEN previous_event_time IS NULL
             OR event_time - previous_event_time > INTERVAL '30 minutes'
           THEN 1
           ELSE 0
         END AS starts_session
  FROM sequenced
)
SELECT event_id,
       customer_id,
       event_time,
       SUM(starts_session) OVER (
         PARTITION BY customer_id
         ORDER BY event_time, event_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS session_number
FROM flagged
ORDER BY customer_id, event_time, event_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Find consecutive calendar-day islands in customer order dates without nesting windows.
-- Why: Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
-- Expected: One row per customer/date island.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH order_days AS (
  SELECT DISTINCT o.customer_id,
         (o.order_date AT TIME ZONE 'UTC')::date AS order_day
  FROM orders AS o
), numbered AS (
  SELECT customer_id,
         order_day,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id ORDER BY order_day
         ) AS day_number
  FROM order_days
), grouped AS (
  SELECT customer_id,
         order_day,
         order_day - day_number::integer AS island_key
  FROM numbered
)
SELECT customer_id,
       MIN(order_day) AS island_start,
       MAX(order_day) AS island_end,
       COUNT(*) AS days_in_island
FROM grouped
GROUP BY customer_id, island_key
ORDER BY customer_id, island_start;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Summarize sessions from the sessionized event stream with start, end, event count, and duration.
-- Why: Aggregate only after session IDs exist at event grain.
-- Expected: One row per customer session.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH sequenced AS (
  SELECT e.*,
         LAG(e.event_time) OVER (
           PARTITION BY e.customer_id
           ORDER BY e.event_time, e.event_id
         ) AS previous_event_time
  FROM events AS e
), flagged AS (
  SELECT sequenced.*,
         (
           previous_event_time IS NULL
           OR event_time - previous_event_time > INTERVAL '30 minutes'
         )::integer AS starts_session
  FROM sequenced
), assigned AS (
  SELECT flagged.*,
         SUM(starts_session) OVER (
           PARTITION BY customer_id
           ORDER BY event_time, event_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS session_number
  FROM flagged
)
SELECT customer_id,
       session_number,
       MIN(event_time) AS session_start,
       MAX(event_time) AS session_end,
       COUNT(*) AS event_count,
       MAX(event_time) - MIN(event_time) AS session_duration
FROM assigned
GROUP BY customer_id, session_number
ORDER BY customer_id, session_number;

-- No course answer persists changes or temporary objects.
ROLLBACK;
