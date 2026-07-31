# Day 47 Solutions — E-commerce Analytics, Part 2


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day47_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day47_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cohort size, Active customer, Retention curve. Its worked-model focus is:
Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.

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

The deliverables are a true retention rate and a tidy six-cohort result suitable
for a line chart. See [`day47_solutions.sql`](day47_solutions.sql).

## Exercises 1 and 2 — Retention rate and chart-ready curves

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), active_months AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), retained AS (
  SELECT c.cohort_month,
         a.order_month,
         (
           EXTRACT(year FROM age(a.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(a.order_month, c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT a.customer_id) AS active_customers
  FROM cohorts c
  JOIN active_months a USING (customer_id)
  GROUP BY c.cohort_month, a.order_month
), curves AS (
  SELECT r.cohort_month,
         r.month_offset,
         s.cohort_size,
         r.active_customers,
         r.active_customers::numeric / NULLIF(s.cohort_size, 0) AS retention_rate
  FROM retained r
  JOIN cohort_sizes s USING (cohort_month)
  WHERE r.month_offset BETWEEN 0 AND 12
), latest_six AS (
  SELECT cohort_month
  FROM cohort_sizes
  ORDER BY cohort_month DESC
  LIMIT 6
)
SELECT cohort_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(retention_rate, 4) AS retention_rate
FROM curves
WHERE cohort_month IN (SELECT cohort_month FROM latest_six)
ORDER BY cohort_month DESC, month_offset;
```

Expected grain: one row per `(cohort_month, month_offset)` for the six newest
signup cohorts, with numerator, denominator, and rate. Chart with
`month_offset` on X, `retention_rate` on Y, and `cohort_month` as the series.
The chart itself is explicitly outside SQL; this answer produces the tidy data
to export or pass to a notebook/BI tool.

## Reasoning, safety, and pitfalls

- `active_months` deliberately deduplicates multiple orders by one customer in
  one month.
- Cohort size is all signups in the cohort, not only customers who eventually
  ordered.
- Cast before division to avoid integer truncation.
- A missing row at an offset is different from a zero-rate row. To force a
  complete retention matrix, cross join cohorts to `generate_series(0, 12)` and
  left join activity.
- The seed is synthetic, so chart shape demonstrates technique rather than a
  business retention benchmark.

## Exercise 1 — Calculate retention rates

`cohort_sizes` supplies the denominator and active distinct customers supply the
numerator. Numeric casting prevents integer truncation.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 1, read from `orders`, `customers`, and `age`. Build the answer toward `cohort_sizes`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 1, expected output: one row per `order_id`. The final columns are `cohort_sizes`.
- **Independent verification:** For sql-47 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `cohort_sizes` against `orders`, `customers`, and `age`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-47 Exercise 1, select `order_id` from `orders`, `customers`, and `age` before adding derived columns.
- **Clause check:** For sql-47 Exercise 1, the solution actually uses `WITH`. Read only those operations: begin at `orders`, `customers`, and `age`, preserve one row per `order_id`, and finish with `cohort_sizes`.
- **Alternative/trade-off:** For sql-47 Exercise 1, the chosen form is justified by this lesson-specific rationale: `cohort_sizes` supplies the denominator and active distinct customers supply the numerator. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 2 — Return six tidy curves

The final rows retain cohort month, offset, size, active count, and rate. “Chart
it” is downstream presentation; SQL should preserve the auditable components.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 2, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `cohort_month DESC, month_offset`.
- **Independent verification:** For sql-47 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Tie two rows on `cohort_month DESC` and give them different `month_offset` values; verify `cohort_month DESC, month_offset` chooses a stable first/last row.
- **Intermediate relation check:** For sql-47 Exercise 2, run `cohorts`, `cohort_sizes`, `active_months`, `retained`, `curves`, and `latest_six` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-47 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `cohort_month`, and finish with `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` ordered by `cohort_month DESC, month_offset`.
- **Alternative/trade-off:** For sql-47 Exercise 2, the chosen form is justified by this lesson-specific rationale: The final rows retain cohort month, offset, size, active count, and rate. Evaluate another form against the concrete expected result (one row per `cohort_month`) and the verification above.
- **Edge case:** Tie two rows on `cohort_month DESC` and give them different `month_offset` values; verify `cohort_month DESC, month_offset` chooses a stable first/last row.

## Exercise 3 — Choose a cohort anchor

Signup month measures post-registration behavior; first-order month measures
repeat purchasing. The answer displays both per customer so the semantic choice
is visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `signup_cohort`, and `first_order_cohort`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `signup_cohort`, and `first_order_cohort`. The final order is `c.customer_id`.
- **Independent verification:** For sql-47 Exercise 3, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `first_order_cohort` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `c.customer_id` and verify `c.customer_id` selects the same row on every run.
- **Intermediate relation check:** For sql-47 Exercise 3, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-47 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, `signup_cohort`, and `first_order_cohort` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-47 Exercise 3, the chosen form is justified by this lesson-specific rationale: Signup month measures post-registration behavior; first-order month measures repeat purchasing. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Use one key absent from `orders`; then tie two candidates on `c.customer_id` and verify `c.customer_id` selects the same row on every run.

## Exercise 4 — Complete the cohort grid

Cross joining cohorts with offsets creates every expected cell. A left join
then turns missing observed activity into zero without losing cohort size.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 4, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 4, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month DESC, x.month_offset`.
- **Independent verification:** For sql-47 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
- **Intermediate relation check:** For sql-47 Exercise 4, run `cohorts`, `sizes`, `offsets`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-47 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `cohort_month`, and finish with `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` ordered by `s.cohort_month DESC, x.month_offset`.
- **Alternative/trade-off:** For sql-47 Exercise 4, the chosen form is justified by this lesson-specific rationale: Cross joining cohorts with offsets creates every expected cell. Evaluate another form against the concrete expected result (one row per `cohort_month`) and the verification above.
- **Edge case:** Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.

## Exercise 5 — Reject negative chronology

The diagnostic returns customers whose first order precedes recorded signup.
Such rows should be corrected or explicitly excluded before retention math.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, `created_at`, and `first_order_at`; keep `customer_id`, and `created_at` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 5, expected output: one row per `customer_id`, and `created_at`. The final columns are `customer_id`, `created_at`, and `first_order_at`. The final order is `c.customer_id`.
- **Independent verification:** For sql-47 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`, and `created_at`; require one output row for every distinct `customer_id`, and `created_at` tuple and compare `first_order_at` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `first_order_at` for the existing `customer_id`, and `created_at` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-47 Exercise 5, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `created_at` so the exact fanout or loss is visible.
- **Clause check:** For sql-47 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and `created_at`, and finish with `customer_id`, `created_at`, and `first_order_at` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-47 Exercise 5, the chosen form is justified by this lesson-specific rationale: The diagnostic returns customers whose first order precedes recorded signup. Evaluate another form against the concrete expected result (one row per `customer_id`, and `created_at`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `first_order_at` for the existing `customer_id`, and `created_at` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Preserve future unknowns

An offset beyond the latest observed month is not a measured zero. The
`is_observable` flag keeps not-yet-available periods distinct.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 6, read from `orders`, and `sample`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-47 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Independent verification:** For sql-47 Exercise 6, project `order_id` plus the raw source columns from `orders`, and `sample` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-47 Exercise 6, run `latest` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-47 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `orders`, and `sample`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Alternative/trade-off:** For sql-47 Exercise 6, the chosen form is justified by this lesson-specific rationale: An offset beyond the latest observed month is not a measured zero. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
