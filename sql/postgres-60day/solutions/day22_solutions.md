# Day 22 solutions — Advanced Windows: Multiple Partitions, Named Windows, Exclusion


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day22_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day22_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Named window, Peer exclusion, Mixed grain. Its worked-model focus is:
Aggregate revenue to (country, category) first. Rank categories within each country from that relation, then calculate a separate category-total relation for the overall rank. Joining those stable grains avoids incorrectly ranking every country/category pair as though it were one global category.

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

These answers align one-for-one with [day22_advanced_windows.sql](../day22_advanced_windows.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
- **Assumptions:** Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
- **Primary pitfall:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Use a named window to show each order with customer count, average, first date, and last date.

**Reasoning:** Name a full-partition customer window once and reuse it.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-22 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-22 Exercise 1, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-22 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-22 Exercise 1, the chosen form is justified by this lesson-specific rationale: Name a full-partition customer window once and reuse it. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.

## Exercise 2 — Query writing

**Prompt:** Compare each employee salary with the average of other employees in the department.

**Reasoning:** Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per employee with nullable peer average.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `other_employee_average`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 2, expected output: One row per employee with nullable peer average. The final columns are `employee_id`, `department_id`, `salary`, and `other_employee_average`. The final order is `e.department_id, e.employee_id`.
- **Independent verification:** For sql-22 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `other_employee_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-22 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.employee_id` before applying the row cap.
- **Clause check:** For sql-22 Exercise 2, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `department_id`, `salary`, and `other_employee_average` ordered by `e.department_id, e.employee_id`.
- **Alternative/trade-off:** For sql-22 Exercise 2, the chosen form is justified by this lesson-specific rationale: Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL. Evaluate another form against the concrete expected result (One row per employee with nullable peer average) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 3 — Query writing

**Prompt:** Show each order's distance from its customer's average and standard deviation.

**Reasoning:** Compute independent partition windows and guard interpretation when variation is zero.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 3, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-22 Exercise 3, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-22 Exercise 3, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-22 Exercise 3, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-22 Exercise 3, the chosen form is justified by this lesson-specific rationale: Compute independent partition windows and guard interpretation when variation is zero. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 4 — Prediction

**Prompt:** Sessionize events using a 30-minute gap and predict why the first event starts a session.

**Reasoning:** Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per event with session number starting at one.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 4, read from `events`. Build the answer toward `event_id`, `customer_id`, `event_time`, and `session_number`; keep `event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 4, expected output: One row per event with session number starting at one. The final columns are `event_id`, `customer_id`, `event_time`, and `session_number`. The final order is `customer_id, event_time, event_id`.
- **Independent verification:** For sql-22 Exercise 4, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `event_time`, then verify output keys remain `event_id`. Use a one-row partition and a partition tied on `customer_id`; verify `event_id` and `customer_id, event_time, event_id` preserve the intended first/last row.
- **Intermediate relation check:** For sql-22 Exercise 4, run `sequenced`, and `flagged` one at a time. Record each CTE's row count and `event_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-22 Exercise 4, the solution actually uses `WITH`, `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `event_id`, and finish with `event_id`, `customer_id`, `event_time`, and `session_number` ordered by `customer_id, event_time, event_id`.
- **Alternative/trade-off:** For sql-22 Exercise 4, the chosen form is justified by this lesson-specific rationale: Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer. Evaluate another form against the concrete expected result (One row per event with session number starting at one) and the verification above.
- **Edge case:** Use a one-row partition and a partition tied on `customer_id`; verify `event_id` and `customer_id, event_time, event_id` preserve the intended first/last row.

## Exercise 5 — Debugging

**Prompt:** Find consecutive calendar-day islands in customer order dates without nesting windows.

**Reasoning:** Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per customer/date island.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 5, read from `orders`. Build the answer toward `customer_id`, `island_start`, `island_end`, and `days_in_island`; keep `customer_id`, and `island_key` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 5, expected output: One row per customer/date island. The final columns are `customer_id`, `island_start`, `island_end`, and `days_in_island`. The final order is `customer_id, island_start`.
- **Independent verification:** For sql-22 Exercise 5, independently aggregate `orders` by `customer_id`, and `island_key`; require one output row for every distinct `customer_id`, and `island_key` tuple and compare `island_start`, `island_end`, and `days_in_island` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `days_in_island` for the existing `customer_id`, and `island_key` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-22 Exercise 5, run `order_days`, `numbered`, and `grouped` one at a time. Record each CTE's row count and `customer_id`, and `island_key` uniqueness before the next stage uses it.
- **Clause check:** For sql-22 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `customer_id`, and `island_key`, and finish with `customer_id`, `island_start`, `island_end`, and `days_in_island` ordered by `customer_id, island_start`.
- **Alternative/trade-off:** For sql-22 Exercise 5, the chosen form is justified by this lesson-specific rationale: Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands. Evaluate another form against the concrete expected result (One row per customer/date island) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `days_in_island` for the existing `customer_id`, and `island_key` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Extension

**Prompt:** Summarize sessions from the sessionized event stream with start, end, event count, and duration.

**Reasoning:** Aggregate only after session IDs exist at event grain.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per customer session.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 6, read from `events`. Build the answer toward `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`; keep `customer_id`, and `session_number` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-22 Exercise 6, expected output: One row per customer session. The final columns are `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`. The final order is `customer_id, session_number`.
- **Independent verification:** For sql-22 Exercise 6, independently aggregate `events` by `customer_id`, and `session_number`; require one output row for every distinct `customer_id`, and `session_number` tuple and compare `event_count`, and `session_duration` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `event_count`, and `session_duration` for the existing `customer_id`, and `session_number` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-22 Exercise 6, run `sequenced`, `flagged`, and `assigned` one at a time. Record each CTE's row count and `customer_id`, and `session_number` uniqueness before the next stage uses it.
- **Clause check:** For sql-22 Exercise 6, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `customer_id`, and `session_number`, and finish with `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration` ordered by `customer_id, session_number`.
- **Alternative/trade-off:** For sql-22 Exercise 6, the chosen form is justified by this lesson-specific rationale: Aggregate only after session IDs exist at event grain. Evaluate another form against the concrete expected result (One row per customer session) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `event_count`, and `session_duration` for the existing `customer_id`, and `session_number` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
