# Day 13 solutions — Date/Time Functions and Time Zones


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day13_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day13_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Half-open interval, Time zone, Calendar bucket. Its worked-model focus is:
Express one day as timestamp >= daystart AND timestamp < nextdaystart. Test a row exactly at each boundary. This half-open form prevents double counting when adjacent daily queries are combined and is friendlier to a normal timestamp index than wrapping the column in a function.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, and `utc_order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 1, expected output: Recent order rows in deterministic order. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-13 Exercise 1, run an anti-check that counts rows where NOT ((o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days')); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `order_date`, and `utc_order_date` against `orders`. Tie two rows on `o.order_date DESC` and give them different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` chooses a stable first/last row.
- **Intermediate relation check:** For sql-13 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.order_date DESC, o.order_id DESC` before applying the row cap.
- **Clause check:** For sql-13 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, and `utc_order_date` ordered by `o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-13 Exercise 1, the chosen form is justified by this lesson-specific rationale: Filter the timestamp directly and convert for display only. Evaluate another form against the concrete expected result (Recent order rows in deterministic order) and the verification above.
- **Edge case:** Tie two rows on `o.order_date DESC` and give them different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` chooses a stable first/last row.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 2, read from `orders`. Build the answer toward `utc_month`, `order_count`, and `stored_revenue`; keep `utc_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 2, expected output: One row per observed UTC month. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
- **Independent verification:** For sql-13 Exercise 2, independently aggregate `orders` by `utc_month`; require one output row for every distinct `utc_month` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `utc_month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-13 Exercise 2, confirm the groups are `utc_month`; then check `utc_month` before applying the row cap.
- **Clause check:** For sql-13 Exercise 2, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `utc_month`, and finish with `utc_month`, `order_count`, and `stored_revenue` ordered by `utc_month`.
- **Alternative/trade-off:** For sql-13 Exercise 2, the chosen form is justified by this lesson-specific rationale: Convert to UTC before truncating when the reporting calendar is UTC. Evaluate another form against the concrete expected result (One row per observed UTC month) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `utc_month` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 3, read from `customers`. Build the answer toward `customer_id`, `created_at`, and `customer_age_days`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 3, expected output: One row per customer with nonnegative age days. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
- **Independent verification:** For sql-13 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `created_at`, and `customer_age_days` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-13 Exercise 3, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-13 Exercise 3, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `created_at`, and `customer_age_days` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-13 Exercise 3, the chosen form is justified by this lesson-specific rationale: Compare calendar dates after declaring the UTC reporting date. Evaluate another form against the concrete expected result (One row per customer with nonnegative age days) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 4, expected output: Orders in exactly one UTC month. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
- **Independent verification:** For sql-13 Exercise 4, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-13 Exercise 4, run `bounds` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-13 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, and `order_date` ordered by `o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-13 Exercise 4, the chosen form is justified by this lesson-specific rationale: Include the month start and exclude the next month start. Evaluate another form against the concrete expected result (Orders in exactly one UTC month) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 5, read from `events`. Build the answer toward `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`; keep `event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 5, expected output: One row per sampled event with two displays of the same instant. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
- **Independent verification:** For sql-13 Exercise 5, assert no more than 20 rows, no duplicate `event_id`, and no adjacent pair that violates `e.event_time, e.event_id`. Rejoin the returned keys to `events` to confirm `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `e.event_time, e.event_id`.
- **Intermediate relation check:** For sql-13 Exercise 5, check `e.event_time, e.event_id` before applying the row cap.
- **Clause check:** For sql-13 Exercise 5, the solution actually uses `FROM`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `events`, preserve one row per `event_id`, and finish with `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time` ordered by `e.event_time, e.event_id`.
- **Alternative/trade-off:** For sql-13 Exercise 5, the chosen form is justified by this lesson-specific rationale: `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value. Evaluate another form against the concrete expected result (One row per sampled event with two displays of the same instant) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `e.event_time, e.event_id`.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 6, read from `orders`. Build the answer toward `utc_date`, and `order_count`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-13 Exercise 6, expected output: Exactly seven chronological rows. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
- **Independent verification:** For sql-13 Exercise 6, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `utc_date`, and `order_count` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-13 Exercise 6, run `calendar`, and `daily_orders` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-13 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `utc_date`, and `order_count` ordered by `c.utc_date`.
- **Alternative/trade-off:** For sql-13 Exercise 6, the chosen form is justified by this lesson-specific rationale: Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts. Evaluate another form against the concrete expected result (Exactly seven chronological rows) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
