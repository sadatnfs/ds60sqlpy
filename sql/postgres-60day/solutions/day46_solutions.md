# Day 46 Solutions — E-commerce Analytics, Part 1


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day46_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day46_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are LTV, Signup cohort, Lifecycle offset. Its worked-model focus is:
Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.

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

This project begins with explicit lifetime-value segments and signup-cohort
revenue. The canonical executable answer is
[`day46_solutions.sql`](day46_solutions.sql).

## Exercise 1 — Gold, silver, and bronze LTV by country

The thresholds below are example business policy. Confirm or tune them for a
real organization rather than presenting them as statistically derived.

```sql
SET search_path TO training, public;

WITH lifetime AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country
), segmented AS (
  SELECT *,
         CASE
           WHEN ltv >= 20000 THEN 'gold'
           WHEN ltv >= 10000 THEN 'silver'
           ELSE 'bronze'
         END AS ltv_segment
  FROM lifetime
)
SELECT country,
       ltv_segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM segmented
GROUP BY country, ltv_segment
ORDER BY country, avg_ltv DESC;
```

Expected grain: one row per `(country, ltv_segment)`. The `LEFT JOIN` retains
customers with no orders and assigns them zero LTV.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 1, read from `customers`, and `orders`. Build the answer toward `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`; keep `country`, and `ltv_segment` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 1, expected output: one row per `(country, ltv_segment)`. The final columns are `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`. The final order is `country, avg_ltv DESC`.
- **Independent verification:** For sql-46 Exercise 1, independently aggregate `customers`, and `orders` by `country`, and `ltv_segment`; require one output row for every distinct `country`, and `ltv_segment` tuple and compare `customers`, `avg_ltv`, and `total_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers`, `avg_ltv`, and `total_ltv` for the existing `country`, and `ltv_segment` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-46 Exercise 1, run `lifetime`, and `segmented` one at a time. Record each CTE's row count and `country`, and `ltv_segment` uniqueness before the next stage uses it.
- **Clause check:** For sql-46 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `country`, and `ltv_segment`, and finish with `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv` ordered by `country, avg_ltv DESC`.
- **Alternative/trade-off:** For sql-46 Exercise 1, the chosen form is justified by this lesson-specific rationale: The thresholds below are example business policy. Evaluate another form against the concrete expected result (one row per `(country, ltv_segment)`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `customers`, `avg_ltv`, and `total_ltv` for the existing `country`, and `ltv_segment` tuple and verify the new tuple appears exactly once.

## Exercise 2 — Cohort revenue at month offsets 0 through 12

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), monthly_customer AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), cohort_revenue AS (
  SELECT c.cohort_month,
         mc.order_month,
         (
           EXTRACT(year FROM age(mc.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(mc.order_month, c.cohort_month))
         )::int AS month_offset,
         SUM(mc.revenue) AS revenue
  FROM cohorts c
  JOIN monthly_customer mc USING (customer_id)
  GROUP BY c.cohort_month, mc.order_month
)
SELECT cohort_month,
       month_offset,
       ROUND(revenue, 2) AS revenue
FROM cohort_revenue
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```

Expected grain: one row per cohort and lifecycle month. A missing offset means
that cohort generated no orders in that lifecycle month; it is not automatically
equivalent to a stored zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, and `revenue`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 2, expected output: one row per cohort and lifecycle month. The final columns are `cohort_month`, `month_offset`, and `revenue`. The final order is `cohort_month DESC, month_offset`.
- **Independent verification:** For sql-46 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, and `revenue` values match those staged rows without unintended fanout or loss. Add one row for which `(month_offset BETWEEN 0 AND 12)` is true and one for which it is false; verify only the matching `cohort_month` value is returned.
- **Intermediate relation check:** For sql-46 Exercise 2, run `cohorts`, `monthly_customer`, and `cohort_revenue` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-46 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `cohort_month`, and finish with `cohort_month`, `month_offset`, and `revenue` ordered by `cohort_month DESC, month_offset`.
- **Alternative/trade-off:** For sql-46 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected grain: one row per cohort and lifecycle month. Evaluate another form against the concrete expected result (one row per cohort and lifecycle month) and the verification above.
- **Edge case:** Add one row for which `(month_offset BETWEEN 0 AND 12)` is true and one for which it is false; verify only the matching `cohort_month` value is returned.

## Reasoning, safety, and pitfalls

- Use one customer row in the LTV CTE; joining items without first controlling
  grain can inflate totals.
- `age()` exposes both years and months. Using only `EXTRACT(month ...)` wraps
  after 11 and breaks multi-year offsets.
- Signup month defines the cohort here, while LTV includes all available order
  history.
- These answers are read-only and repeatable.

## Exercise 3 — Compare relative and fixed segments

`NTILE(4)` is recalculated over the current population, so another customer's
arrival can move a boundary. Fixed monetary thresholds are stable but require a
reviewed business policy. The executable answer displays both.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`. The final order is `ltv DESC, customer_id`.
- **Independent verification:** For sql-46 Exercise 3, choose one complete partition from `customers`, and `orders`; hand-calculate its first, middle, and final window values for `ltv`, `population_quartile`, and `fixed_segment`, then verify output keys remain `customer_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-46 Exercise 3, run `lifetime` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-46 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, `ltv`, `population_quartile`, and `fixed_segment` ordered by `ltv DESC, customer_id`.
- **Alternative/trade-off:** For sql-46 Exercise 3, the chosen form is justified by this lesson-specific rationale: `NTILE(4)` is recalculated over the current population, so another customer's arrival can move a boundary. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Build a customer-grain feature row

The `behavior` CTE aggregates orders once per customer. Its outer join preserves
no-order customers and supports LTV, frequency, average order value, and recency
without mixing grains.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 4, read from `orders`, and `customers`. Build the answer toward `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`. The final order is `ltv DESC, c.customer_id`.
- **Independent verification:** For sql-46 Exercise 4, project `customer_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-46 Exercise 4, run `behavior` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-46 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order` ordered by `ltv DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-46 Exercise 4, the chosen form is justified by this lesson-specific rationale: The `behavior` CTE aggregates orders once per customer. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 5 — Prevent LTV fanout

Line revenue is reduced to one row per order before it becomes customer LTV.
Payments would need their own order-grain aggregation; joining both raw sources
would multiply values.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 5, read from `orders`, and `order_items`. Build the answer toward `customer_id`, and `line_ltv`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 5, expected output: one row per order before it becomes customer LTV. The final columns are `customer_id`, and `line_ltv`. The final order is `line_ltv DESC, customer_id`.
- **Independent verification:** For sql-46 Exercise 5, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `line_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `line_ltv` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-46 Exercise 5, run `order_value` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-46 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `order_items`, preserve one row per `customer_id`, and finish with `customer_id`, and `line_ltv` ordered by `line_ltv DESC, customer_id`.
- **Alternative/trade-off:** For sql-46 Exercise 5, the chosen form is justified by this lesson-specific rationale: Line revenue is reduced to one row per order before it becomes customer LTV. Evaluate another form against the concrete expected result (one row per order before it becomes customer LTV) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `line_ltv` for the existing `customer_id` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Retain no-order customers

The answer keeps the LEFT JOIN outer and applies `COALESCE` only after grouping.
A WHERE predicate on order columns would accidentally remove the intended
zero-LTV population.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, and `activity_status`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-46 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, and `activity_status`. The final order is `c.customer_id`.
- **Independent verification:** For sql-46 Exercise 6, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `ltv`, and `activity_status` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `ltv`, and `activity_status` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-46 Exercise 6, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-46 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, `ltv`, and `activity_status` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-46 Exercise 6, the chosen form is justified by this lesson-specific rationale: The answer keeps the LEFT JOIN outer and applies `COALESCE` only after grouping. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `ltv`, and `activity_status` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
