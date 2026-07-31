# Day 30 solutions — Phase 2 Project: Cohort Retention and CLV


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day30_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day30_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cohort, Retention denominator, Calendar spine. Its worked-model focus is:
Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.

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

These answers align one-for-one with [day30_phase2_project.sql](../day30_phase2_project.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
- **Assumptions:** Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
- **Primary pitfall:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Calculate original customer count for each UTC signup cohort month.

**Reasoning:** Build the denominator from customers, including customers who never order.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
)
SELECT cohort_month,
       COUNT(*) AS cohort_size
FROM cohorts
GROUP BY cohort_month
ORDER BY cohort_month;
```

**Expected shape:** One row per cohort month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 1, read from `customers`. Build the answer toward `cohort_month`, and `cohort_size`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 1, expected output: One row per cohort month. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
- **Independent verification:** For sql-30 Exercise 1, independently aggregate `customers` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_size` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_size` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-30 Exercise 1, run `cohorts` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 1, the solution actually uses `WITH`, `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `cohort_month`, and finish with `cohort_month`, and `cohort_size` ordered by `cohort_month`.
- **Alternative/trade-off:** For sql-30 Exercise 1, the chosen form is justified by this lesson-specific rationale: Build the denominator from customers, including customers who never order. Evaluate another form against the concrete expected result (One row per cohort month) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `cohort_size` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.

## Exercise 2 — Query writing

**Prompt:** Calculate active customers and net line revenue for each cohort/order month.

**Reasoning:** Aggregate line items to order grain before cohort joins, then count distinct active customers.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
)
SELECT c.cohort_month,
       ov.order_month,
       COUNT(DISTINCT ov.customer_id) AS active_customers,
       ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM cohorts AS c
JOIN order_values AS ov ON ov.customer_id = c.customer_id
GROUP BY c.cohort_month, ov.order_month
ORDER BY c.cohort_month, ov.order_month;
```

**Expected shape:** One row per observed cohort/order month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 2, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `active_customers`, and `net_revenue`; keep `cohort_month`, and `order_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 2, expected output: One row per observed cohort/order month. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
- **Independent verification:** For sql-30 Exercise 2, independently aggregate `orders`, `order_items`, and `customers` by `cohort_month`, and `order_month`; require one output row for every distinct `cohort_month`, and `order_month` tuple and compare `order_month`, `active_customers`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `active_customers`, and `net_revenue` for the existing `cohort_month`, and `order_month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-30 Exercise 2, run `order_values`, and `cohorts` one at a time. Record each CTE's row count and `cohort_month`, and `order_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `customers`, preserve one row per `cohort_month`, and `order_month`, and finish with `cohort_month`, `order_month`, `active_customers`, and `net_revenue` ordered by `c.cohort_month, ov.order_month`.
- **Alternative/trade-off:** For sql-30 Exercise 2, the chosen form is justified by this lesson-specific rationale: Aggregate line items to order grain before cohort joins, then count distinct active customers. Evaluate another form against the concrete expected result (One row per observed cohort/order month) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `active_customers`, and `net_revenue` for the existing `cohort_month`, and `order_month` tuple and verify the new tuple appears exactly once.

## Exercise 3 — Query writing

**Prompt:** Calculate cohort month offset and retention using original cohort size.

**Reasoning:** Use year-plus-month age components and guard the denominator.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), activity AS (
  SELECT c.cohort_month,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         COUNT(DISTINCT o.customer_id) AS active_customers
  FROM cohorts AS c
  JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY c.cohort_month,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
)
SELECT a.cohort_month,
       (
         EXTRACT(YEAR FROM age(a.order_month, a.cohort_month)) * 12
         + EXTRACT(MONTH FROM age(a.order_month, a.cohort_month))
       )::integer AS month_offset,
       cs.cohort_size,
       a.active_customers,
       ROUND(a.active_customers::numeric / NULLIF(cs.cohort_size, 0), 4) AS retention_rate
FROM activity AS a
JOIN cohort_sizes AS cs USING (cohort_month)
ORDER BY a.cohort_month, month_offset;
```

**Expected shape:** Observed cohort/offset rows with retention from 0 to 1.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 3, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 3, expected output: Observed cohort/offset rows with retention from 0 to 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
- **Independent verification:** For sql-30 Exercise 3, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
- **Intermediate relation check:** For sql-30 Exercise 3, run `cohorts`, `cohort_sizes`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `cohort_month`, and finish with `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` ordered by `a.cohort_month, month_offset`.
- **Alternative/trade-off:** For sql-30 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use year-plus-month age components and guard the denominator. Evaluate another form against the concrete expected result (Observed cohort/offset rows with retention from 0 to 1) and the verification above.
- **Edge case:** Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.

## Exercise 4 — Prediction

**Prompt:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.

**Reasoning:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), activity AS (
  SELECT c.cohort_month,
         (
           EXTRACT(YEAR FROM age(
             date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date,
             c.cohort_month
           )) * 12
           + EXTRACT(MONTH FROM age(
             date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date,
             c.cohort_month
           ))
         )::integer AS month_offset,
         COUNT(DISTINCT o.customer_id) AS active_customers
  FROM cohorts AS c
  JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY c.cohort_month,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), spine AS (
  SELECT cs.cohort_month,
         cs.cohort_size,
         offset_value AS month_offset
  FROM cohort_sizes AS cs
  CROSS JOIN generate_series(0, 12) AS offsets(offset_value)
)
SELECT s.cohort_month,
       s.month_offset,
       s.cohort_size,
       COALESCE(a.active_customers, 0) AS active_customers
FROM spine AS s
LEFT JOIN activity AS a
  ON a.cohort_month = s.cohort_month
 AND a.month_offset = s.month_offset
ORDER BY s.cohort_month, s.month_offset;
```

**Expected shape:** Thirteen rows per cohort.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 4, read from `customers`, `orders`, and `generate_series`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 4, expected output: Thirteen rows per cohort. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
- **Independent verification:** For sql-30 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, `orders`, and `generate_series` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
- **Intermediate relation check:** For sql-30 Exercise 4, run `cohorts`, `cohort_sizes`, `activity`, and `spine` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, `orders`, and `generate_series`, preserve one row per `cohort_month`, and finish with `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` ordered by `s.cohort_month, s.month_offset`.
- **Alternative/trade-off:** For sql-30 Exercise 4, the chosen form is justified by this lesson-specific rationale: Cross join cohort months with generate_series, then left join observed activity at the same offset grain. Evaluate another form against the concrete expected result (Thirteen rows per cohort) and the verification above.
- **Edge case:** Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.

## Exercise 5 — Debugging

**Prompt:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.

**Reasoning:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), metrics AS (
  SELECT c.cohort_month,
         ov.order_month,
         (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer AS month_offset,
         COUNT(DISTINCT ov.customer_id) AS active_customers,
         SUM(ov.order_value) AS revenue
  FROM cohorts AS c
  JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY c.cohort_month, ov.order_month
), per_active AS (
  SELECT metrics.*,
         revenue / NULLIF(active_customers, 0) AS revenue_per_active
  FROM metrics
)
SELECT cohort_month,
       order_month,
       month_offset,
       active_customers,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue_per_active, 2) AS revenue_per_active,
       ROUND(
         AVG(revenue_per_active) OVER (
           PARTITION BY cohort_month
           ORDER BY month_offset
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
         ) * 12,
         2
       ) AS illustrative_annualized_clv
FROM per_active
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month, month_offset;
```

**Expected shape:** One row per observed cohort/month with nullable guarded measures.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 5, expected output: One row per observed cohort/month with nullable guarded measures. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
- **Independent verification:** For sql-30 Exercise 5, choose one complete partition from `orders`, `order_items`, and `customers`; hand-calculate its first, middle, and final window values for `order_month`, `active_customers`, `revenue`, and `revenue_per_active`, then verify output keys remain `cohort_month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-30 Exercise 5, run `order_values`, `cohorts`, `metrics`, and `per_active` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `customers`, preserve one row per `cohort_month`, and finish with `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv` ordered by `cohort_month, month_offset`.
- **Alternative/trade-off:** For sql-30 Exercise 5, the chosen form is justified by this lesson-specific rationale: Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps. Evaluate another form against the concrete expected result (One row per observed cohort/month with nullable guarded measures) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 6 — Extension

**Prompt:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.

**Reasoning:** Calculate violations and compare totals at the same scoped population.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.

```sql
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), metrics AS (
  SELECT c.cohort_month,
         ov.order_month,
         (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer AS month_offset,
         COUNT(DISTINCT ov.customer_id) AS active_customers,
         SUM(ov.order_value) AS revenue
  FROM cohorts AS c
  JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY c.cohort_month, ov.order_month
), scoped AS (
  SELECT m.*, cs.cohort_size
  FROM metrics AS m
  JOIN cohort_sizes AS cs USING (cohort_month)
  WHERE m.month_offset BETWEEN 0 AND 12
)
SELECT COUNT(*) FILTER (
         WHERE active_customers > cohort_size
       ) AS active_exceeds_cohort_violations,
       ROUND(SUM(revenue), 2) AS cohort_revenue,
       ROUND((
         SELECT SUM(ov.order_value)
         FROM order_values AS ov
         JOIN cohorts AS c ON c.customer_id = ov.customer_id
         WHERE (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer BETWEEN 0 AND 12
       ), 2) AS independent_revenue,
       ROUND(
         SUM(revenue) - (
           SELECT SUM(ov.order_value)
           FROM order_values AS ov
           JOIN cohorts AS c ON c.customer_id = ov.customer_id
           WHERE (
             EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
             + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
           )::integer BETWEEN 0 AND 12
         ),
         2
       ) AS revenue_difference
FROM scoped;
```

**Expected shape:** One row with zero retention violations and zero revenue difference.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 6, read from `orders`, `order_items`, and `customers`. Build the answer toward `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-30 Exercise 6, expected output: One row with zero retention violations and zero revenue difference. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
- **Independent verification:** For sql-30 Exercise 6, project `order_id` plus the raw source columns from `orders`, `order_items`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-30 Exercise 6, run `order_values`, `cohorts`, `cohort_sizes`, `metrics`, and `scoped` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-30 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `order_items`, and `customers`, preserve one row per `order_id`, and finish with `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
- **Alternative/trade-off:** For sql-30 Exercise 6, the chosen form is justified by this lesson-specific rationale: Calculate violations and compare totals at the same scoped population. Evaluate another form against the concrete expected result (One row with zero retention violations and zero revenue difference) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
