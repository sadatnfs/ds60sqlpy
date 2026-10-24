-- SQL-START-01: Reading Tables and Result Grain
-- Guide: sql/professional/companion-guides/sql_start_01_tables_and_grain.md
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
CREATE TEMP TABLE start_readings (
  reading_id integer PRIMARY KEY,
  station text NOT NULL,
  reading_day date NOT NULL,
  temperature numeric
) ON COMMIT DROP;
INSERT INTO start_readings (reading_id, station, reading_day, temperature)
VALUES
  (1, 'North', DATE '2024-01-01', 18),
  (2, 'North', DATE '2024-01-02', 18),
  (3, 'South', DATE '2024-01-01', 0),
  (4, 'South', DATE '2024-01-02', NULL),
  (5, 'West', DATE '2024-01-01', -4),
  (6, 'North', DATE '2024-01-03', 20);
-- Example 1: A full observation retains its identity
-- Expected: Six rows with columns reading_id, station, reading_day, temperature; IDs 1 through 6 in order. ID 4 has NULL temperature.
SELECT
  reading_id,
  station,
  reading_day,
  temperature
FROM
  start_readings
ORDER BY
  reading_id;
-- Example 2: Two visually identical rows are still two observations
-- Expected: Two rows, each (North, 18), with columns station and temperature. No table row is removed or updated.
SELECT
  station,
  temperature
FROM
  start_readings
WHERE
  reading_id <= 2
ORDER BY
  reading_id;
-- Exercises
-- Keep predictions and attempts in your own working copy.
-- 1. Trace identities.
-- Inputs/evidence: For sql-start-01 Exercise 1, Return all observations with reading_id, station, and temperature. Write a sentence naming the table grain and output grain before running the query. Use the identity as the final display order.
-- Expected result/shape: For sql-start-01 Exercise 1, Six rows, one per reading_id, with columns reading_id, station, temperature; final ORDER BY reading_id. IDs are 1,2,3,4,5,6 and ID 4 keeps its NULL measurement.
-- Verify: For sql-start-01 Exercise 1, Compare the six returned reading_id values with the fixture IDs 1 through 6 and inspect the NULL temperature at ID 4; no identity is repeated or absent.
-- Hint: Start with FROM, then choose the three requested columns.
-- 2. Reveal repeated visible values.
-- Inputs/evidence: For sql-start-01 Exercise 2, Show reading_id, station, reading_day, temperature for IDs 1 and 2. Explain why projecting only station and temperature produces two identical-looking rows rather than one row.
-- Expected result/shape: For sql-start-01 Exercise 2, Two observation rows with columns reading_id, station, reading_day, temperature; final ORDER BY reading_id. Both temperatures are 18, with dates January 1 and January 2 respectively.
-- Verify: For sql-start-01 Exercise 2, Inspect two different reading_id and reading_day values while confirming both station/temperature pairs are North/18. Removing the visible identity must not collapse the two observations.
-- Hint: A column can repeat even when the primary key cannot.
-- 3. Filter observations without losing missing values.
-- Inputs/evidence: For sql-start-01 Exercise 3, Return the South observations with reading_id, station, temperature, ordered by reading_id. Do not add a measurement condition.
-- Expected result/shape: For sql-start-01 Exercise 3, Two rows keyed by reading_id, columns reading_id, station, temperature, final ORDER BY reading_id: (3, South, 0), (4, South, NULL).
-- Verify: For sql-start-01 Exercise 3, Inspect the two returned rows: reading_id 3 and 4, exactly one present zero temperature, and exactly one NULL measurement. Neither a missing field nor zero makes the South observation disappear.
-- Hint: The question restricts station, not temperature.
-- 4. Calculate without editing storage.
-- Inputs/evidence: For sql-start-01 Exercise 4, For IDs 1 and 3, return reading_id, temperature, and temperature + 2 named adjusted_temperature. Then rerun the original projection to show that the stored values did not change.
-- Expected result/shape: For sql-start-01 Exercise 4, Two rows keyed by reading_id, columns reading_id, temperature, adjusted_temperature, final ORDER BY reading_id: (1,18,20) and (3,0,2). Original temperatures remain 18 and 0.
-- Verify: For sql-start-01 Exercise 4, Inspect calculated values 20 and 2, then rerun the original reading_id/temperature projection and confirm the stored temperatures remain 18 and 0.
-- Hint: An expression in SELECT calculates a result; UPDATE would change storage.
-- 5. Distinguish no rows from a missing field.
-- Inputs/evidence: For sql-start-01 Exercise 5, Search for station East and project reading_id, station, temperature. Compare its output with the South result from Exercise 3.
-- Expected result/shape: For sql-start-01 Exercise 5, Zero observation rows with columns reading_id, station, temperature and final ORDER BY reading_id. South has two rows, including a row with a NULL field; East has no stored observation.
-- Verify: For sql-start-01 Exercise 5, Inspect the zero-row message and compare it with the South row at ID 4, which has an identity and a NULL field. Do not manufacture an East row.
-- Hint: A WHERE condition can produce an empty result without causing an error.
-- 6. Transfer grain to a new collection.
-- Inputs/evidence: For sql-start-01 Exercise 6, Use a VALUES input containing (11, 'North', 'battery') and (12, 'North', 'screen') with columns ticket_id, station, issue. Return ticket_id, station, issue ordered by ticket_id. Explain why station is not a ticket key.
-- Expected result/shape: For sql-start-01 Exercise 6, Two ticket rows, columns ticket_id, station, issue, final ORDER BY ticket_id: IDs 11 and 12 both belong to North. The output grain is one ticket, not one station or observation.
-- Verify: For sql-start-01 Exercise 6, Count two distinct ticket_id values and one distinct station; inspect battery at ID 11 and screen at ID 12 to retain their source associations.
-- Hint: Name the three VALUES columns in the table alias.
ROLLBACK;
