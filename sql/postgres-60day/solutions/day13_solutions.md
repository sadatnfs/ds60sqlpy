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

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List orders from the last 30 days with their UTC calendar date” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_order_date`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: List orders from the last 30 days with their UTC calendar date. Why: Filter the timestamp directly and convert for display only. Expected: Recent order rows in deterministic order. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Summarize orders and stored revenue by UTC month” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_month`, `order_count`, `stored_revenue`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Summarize orders and stored revenue by UTC month. Why: Convert to UTC before truncating when the reporting calendar is UTC. Expected: One row per observed UTC month. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Calculate each customer's age in whole days as of the current date” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `of`, `evidence`, `customer_age_days`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 3: Query writing Prompt: Calculate each customer's age in whole days as of the current date. Why: Compare calendar dates after declaring the UTC reporting date. Expected: One row per customer with nonnegative age days. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 4 needs the plan evidence for “Prediction: Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `month_start`, `next_month_start`, `o`, `b`, `utc`.
- **Independent verification:** For Exercise 4, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers. The executable solution's check is: Exercise 4: Prediction Prompt: Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded. Why: Include the month start and exclude the next month start. Expected: Orders in exactly one UTC month. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 5 requires a written prediction and the observed result for “Debugging: Compare UTC and America/LosAngeles display times without stripping the stored instant”. Show both compared result shapes at one row at TIME ZONE on timestamptz produces a local wall-clock display value grain, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `utc_wall_time`, `los_angeles_wall_time`, `e`, `utc`.
- **Independent verification:** For Exercise 5, run the two forms over the identical rows in `events`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 5: Debugging Prompt: Compare UTC and America/LosAngeles display times without stripping the stored instant. Why: AT TIME ZONE on timestamptz produces a local wall-clock display value. Expected: One row per sampled event with two displays of the same instant. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 6 must make “Extension: Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero” observable through the exact DDL/DML command tag plus one row per requested calendar/cohort bucket and grouping key; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero. Why: Generate the date spine first, aggregate orders by the same UTC date, then COALESCE absent counts. Expected: Exactly seven chronological rows. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - COALESCE: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
