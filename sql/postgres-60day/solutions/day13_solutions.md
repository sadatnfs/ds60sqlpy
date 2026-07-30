# Day 13 solutions — Date/Time Functions and Time Zones

These answers align one-for-one with [day13_date_time_functions.sql](../day13_date_time_functions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.
- **Assumptions:** Stored event/order timestamps are `timestamptz`. Relative examples use the database clock; reports label UTC explicitly where conversion matters.
- **Primary pitfall:** `BETWEEN` is inclusive at both ends and is often wrong for adjacent time windows; use half-open `[start, end)` predicates.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List orders from the last 30 days with their UTC calendar date.

**Reasoning:** Filter the timestamp directly and convert for display only.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.order_date,
       (o.order_date AT TIME ZONE 'UTC')::date AS utc_order_date
FROM orders AS o
WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY o.order_date DESC, o.order_id DESC;
```

**Expected shape:** Recent order rows in deterministic order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Summarize orders and stored revenue by UTC month.

**Reasoning:** Convert to UTC before truncating when the reporting calendar is UTC.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS utc_month,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM orders AS o
GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
ORDER BY utc_month;
```

**Expected shape:** One row per observed UTC month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Calculate each customer's age in whole days as of the current date.

**Reasoning:** Compare calendar dates after declaring the UTC reporting date.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.created_at,
       (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
         - (c.created_at AT TIME ZONE 'UTC')::date AS customer_age_days
FROM customers AS c
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer with nonnegative age days.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.

**Reasoning:** Include the month start and exclude the next month start.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH bounds AS (
  SELECT date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AS month_start,
         date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 month' AS next_month_start
)
SELECT o.order_id,
       o.order_date
FROM orders AS o
CROSS JOIN bounds AS b
WHERE o.order_date >= b.month_start AT TIME ZONE 'UTC'
  AND o.order_date < b.next_month_start AT TIME ZONE 'UTC'
ORDER BY o.order_date, o.order_id;
```

**Expected shape:** Orders in exactly one UTC month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.

**Reasoning:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT e.event_id,
       e.event_time,
       e.event_time AT TIME ZONE 'UTC' AS utc_wall_time,
       e.event_time AT TIME ZONE 'America/Los_Angeles' AS los_angeles_wall_time
FROM events AS e
ORDER BY e.event_time, e.event_id
LIMIT 20;
```

**Expected shape:** One row per sampled event with two displays of the same instant.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.

**Reasoning:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH calendar AS (
  SELECT generate_series(
           (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6,
           (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date,
           INTERVAL '1 day'
         )::date AS utc_date
), daily_orders AS (
  SELECT (o.order_date AT TIME ZONE 'UTC')::date AS utc_date,
         COUNT(*) AS order_count
  FROM orders AS o
  WHERE o.order_date >= ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6) AT TIME ZONE 'UTC'
  GROUP BY (o.order_date AT TIME ZONE 'UTC')::date
)
SELECT c.utc_date,
       COALESCE(d.order_count, 0) AS order_count
FROM calendar AS c
LEFT JOIN daily_orders AS d
  ON d.utc_date = c.utc_date
ORDER BY c.utc_date;
```

**Expected shape:** Exactly seven chronological rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
