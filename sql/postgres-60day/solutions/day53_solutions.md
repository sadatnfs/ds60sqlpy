# Day 53 Solutions — SCD Type 2 and Temporal Fact Keys


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day53_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day53_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are SCD Type 2, Business key, Validity interval. Its worked-model focus is:
For one changed customer, locate exactly one current row, set its validto to the day before the new version, and insert the successor at CURRENTDATE. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key—not zero and not two.

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

Run [`day52_solutions.sql`](day52_solutions.sql) first in the same database.
Day 53 reads that committed `dwh` state but wraps its own changes in a
transaction and rolls them back. The full answer is
[`day53_solutions.sql`](day53_solutions.sql).

## Exercise 1 — Resolve dimension versions by fact date

The exercise requires the customer and product surrogate keys whose validity
intervals contain each source order date.

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TEMP TABLE fact_sales_temporal_solution AS
SELECT o.order_id,
       oi.order_item_id,
       dd.date_key,
       dc.customer_sk,
       dp.product_sk,
       oi.quantity,
       oi.unit_price,
       oi.discount,
       oi.unit_price * oi.quantity * (1 - oi.discount) AS amount
FROM training.orders o
JOIN training.order_items oi USING (order_id)
JOIN dim_date dd ON dd.date_actual = o.order_date::date
JOIN dim_customer dc
  ON dc.customer_id = o.customer_id
 AND o.order_date::date >= dc.valid_from
 AND o.order_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
JOIN dim_product dp
  ON dp.product_id = oi.product_id
 AND o.order_date::date >= dp.valid_from
 AND o.order_date::date <= COALESCE(dp.valid_to, 'infinity'::date);

SELECT (SELECT COUNT(*) FROM fact_sales_temporal_solution) AS mapped_fact_rows,
       (SELECT COUNT(*) FROM training.order_items) AS source_item_rows;

ROLLBACK;
```

Expected result: `mapped_fact_rows` equals `source_item_rows`. A lower count
means a date or dimension-version gap; a higher count means overlapping
validity ranges caused one fact to match more than one version.

The executable solution also stages a deterministic customer change effective
30 days ago, closes the previous current row at `effective_date - 1`, inserts a
new current row, and then performs this temporal mapping.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 1, read from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`. Build the answer toward `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-53 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`.
- **Independent verification:** For sql-53 Exercise 1, project `order_id` plus the raw source columns from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-53 Exercise 1, start with the first relation in `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-53 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`, preserve one row per `order_id`, and finish with `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`.
- **Alternative/trade-off:** For sql-53 Exercise 1, the chosen form is justified by this lesson-specific rationale: The exercise requires the customer and product surrogate keys whose validity intervals contain each source order date. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 2 — Audit columns

Inside the Day 53 transaction, the answer adds:

```sql
BEGIN;
SET search_path TO dwh, training, public;

ALTER TABLE dim_customer
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE dim_product
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ROLLBACK;
```

The SCD close and insert explicitly stamp `updated_by = 'day53_solution'`.
Because the executable answer rolls back, these columns do not remain after the
lesson.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 2, change only `dim_customer`, and `dim_product` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `information_schema.columns` rows.
- **Expected result/shape:** For sql-53 Exercise 2, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `updated_by`, and `day53_solution`.
- **Independent verification:** For sql-53 Exercise 2, inspect `information_schema.columns` for `dim_customer`, and `dim_product`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-53 Exercise 2, inspect `information_schema.columns` for `dim_customer`, and `dim_product`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-53 Exercise 2, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `dim_customer`, and `dim_product` or label it as proposed policy.
- **Alternative/trade-off:** For sql-53 Exercise 2, the chosen form is justified by this lesson-specific rationale: Inside the Day 53 transaction, the answer adds: The SCD close and insert explicitly stamp `updated_by = 'day53_solution'`. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

## Reasoning, state, and pitfalls

- A Type 2 change is two operations in one transaction: close the current
  version, then insert the replacement.
- `valid_from <= fact_date <= COALESCE(valid_to, infinity)` matches the
  course's inclusive-date convention.
- Enforce one current row per business key in a production warehouse, commonly
  with a partial unique index on the business key where `is_current`.
- Audit defaults cover inserts, not meaningful update actors; set audit values
  explicitly when closing versions.
- Do not run this before Day 52; the executable file raises a clear exception if
  `dwh.dim_customer` is absent.

## Exercise 3 — Diagnose same-day changes

Inclusive DATE ranges cannot order two changes on one day without overlap or an
invalid close-before-open interval. The answer surfaces invalid ranges.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 3, read from `dim_customer`. Build the answer toward `customer_id`, `valid_from`, `valid_to`, and `invalid_range`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-53 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `valid_from`, `valid_to`, and `invalid_range`. The final order is `valid_from`.
- **Independent verification:** For sql-53 Exercise 3, run an anti-check that counts rows where NOT ((customer_id = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `valid_from`, `valid_to`, and `invalid_range` against `dim_customer`. Add one row for which `(customer_id = 1)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-53 Exercise 3, inspect the source keys that survive `WHERE`; then check `valid_from` before applying the row cap.
- **Clause check:** For sql-53 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `dim_customer`, preserve one row per `customer_id`, and finish with `customer_id`, `valid_from`, `valid_to`, and `invalid_range` ordered by `valid_from`.
- **Alternative/trade-off:** For sql-53 Exercise 3, the chosen form is justified by this lesson-specific rationale: Inclusive DATE ranges cannot order two changes on one day without overlap or an invalid close-before-open interval. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one row for which `(customer_id = 1)` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Exercise 4 — Detect overlapping versions

The self-join compares each customer-version pair once and applies the inclusive
overlap condition. Any row can map one fact date to multiple surrogates.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 4, read from `dim_customer`. Build the answer toward `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-53 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`. The final order is `a.customer_id, version_a, version_b`.
- **Independent verification:** For sql-53 Exercise 4, project `customer_id` plus the raw source columns from `dim_customer` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-53 Exercise 4, start with the first relation in `dim_customer`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-53 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `dim_customer`, preserve one row per `customer_id`, and finish with `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to` ordered by `a.customer_id, version_a, version_b`.
- **Alternative/trade-off:** For sql-53 Exercise 4, the chosen form is justified by this lesson-specific rationale: The self-join compares each customer-version pair once and applies the inclusive overlap condition. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 5 — Gate unchanged reruns

`IS DISTINCT FROM` compares nullable attributes safely. The replay must use the
same staged desired state that produced the new version—not the unchanged base
table—otherwise the deliberate segment change looks like a new change again.

```sql
WITH desired_customer_state AS (
  SELECT customer_id, full_name, country, segment
  FROM staged_customer_change
)
SELECT COUNT(*) AS unchanged_rows_that_would_version
FROM dim_customer current_version
JOIN desired_customer_state desired USING (customer_id)
WHERE current_version.is_current
  AND (
    current_version.full_name IS DISTINCT FROM desired.full_name
    OR current_version.country IS DISTINCT FROM desired.country
    OR current_version.segment IS DISTINCT FROM desired.segment
  );
```

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
- **Expected result/shape:** For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
- **Independent verification:** For sql-53 Exercise 5, rerun the nullable-safe attribute comparison against `desired_customer_state`; require zero differences. Then alter one staged attribute and require exactly one difference before applying any close/insert statements.
- **Intermediate relation check:** For sql-53 Exercise 5, prove `desired_customer_state` and the current dimension are each unique on `customer_id` before comparing attributes.
- **Clause check:** For sql-53 Exercise 5, `IS DISTINCT FROM` compares nullable attributes, while `dc.is_current` restricts the check to the one version that a replay would consider.
- **Alternative/trade-off:** For sql-53 Exercise 5, the chosen form is justified by this lesson-specific rationale: `IS DISTINCT FROM` compares nullable attributes safely. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** A duplicate `customer_id` in desired state must fail a uniqueness gate before versioning; do not let the join multiply candidate changes.

## Exercise 6 — Define a same-day policy

Half-open `tstzrange` examples show how effective timestamps can order changes.
They require trustworthy source effective time or sequence, not load-time guesswork.

### Reasoning and verification

- **Inputs/evidence:** For sql-53 Exercise 6, read from `training.customers`, `dim_customer`, and `changed_customers`. Compute `first_version`, and `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-53 Exercise 6, expected output: exactly one aggregate summary row. The final columns are `first_version`, and `ROLLBACK`.
- **Independent verification:** For sql-53 Exercise 6, evaluate each of `first_version`, and `ROLLBACK` in a separate control `SELECT` over `training.customers`, `dim_customer`, and `changed_customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-53 Exercise 6, select `customer_id` from `training.customers`, `dim_customer`, and `changed_customers` before adding derived columns.
- **Clause check:** For sql-53 Exercise 6, the solution actually uses `SELECT`. Read only those operations: begin at `training.customers`, `dim_customer`, and `changed_customers`, preserve exactly one summary row, and finish with `first_version`, and `ROLLBACK`.
- **Alternative/trade-off:** For sql-53 Exercise 6, the chosen form is justified by this lesson-specific rationale: Half-open `tstzrange` examples show how effective timestamps can order changes. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
