# Day 52 Solutions — Data Warehouse Design, Part 1


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day52_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day52_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Fact table, Dimension, Surrogate key. Its worked-model focus is:
Write the grain beside every table before loading it. Load dimdate and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in factsales. Compare fact row count with source orderitems and check every key resolves once before committing Day 52.

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

Day 52 is intentionally stateful. Unlike most course files, it commits a
course-owned `dwh` schema so Days 53 and 54 can use it. Re-running the learner
file or solution resets **only** that schema with `DROP SCHEMA dwh CASCADE`.

The complete runnable answer is
[`day52_solutions.sql`](day52_solutions.sql). From the `solutions` directory:

```text
psql -X -v ON_ERROR_STOP=1 -d course -f day52_solutions.sql
```

The file first includes `../day52_project3_dwh_part1.sql`, which builds and
commits `dim_date`, Type-2-ready customer/product dimensions, and `fact_sales`.
It then completes both exercises in a second committed transaction.

## Exercise 1 — Add `dim_country`

The solution:

1. creates `dwh.dim_country(country_sk, country_code)`;
2. loads distinct country codes from `training.customers`;
3. adds `country_sk` to `dwh.dim_customer`;
4. backfills it through the existing text country code;
5. adds a foreign key and makes the new key non-null.

This preserves the original `country` attribute in each Type 2 customer row
while also providing a conformed country key. Expected grain is one row per
country code in `dim_country`; every customer-dimension version has exactly one
`country_sk`.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 1, read the target keys from `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-52 Exercise 1, expected output: one row per country code in `dim_country`; every customer-dimension version has exactly one `country_sk`. The final columns are `country`. The final order is `country`.
- **Independent verification:** For sql-52 Exercise 1, materialize the intended `country` target set first; require the command tag/`RETURNING` set to match it, then query `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `country` values in both cases.
- **Intermediate relation check:** For sql-52 Exercise 1, materialize the intended `country` target set first; require the command tag/`RETURNING` set to match it, then query `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` again and prove rollback or idempotent retry.
- **Clause check:** For sql-52 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer`, preserve exactly one summary row, and finish with `country` ordered by `country`.
- **Alternative/trade-off:** For sql-52 Exercise 1, the chosen form is justified by this lesson-specific rationale: The solution: 1. Evaluate another form against the concrete expected result (one row per country code in `dim_country`; every customer-dimension version has exactly one `country_sk`) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `country` values in both cases.

## Exercise 2 — Add `fact_payments`

The answer creates one row per source payment with:

- `payment_id` as the idempotent fact key;
- `order_id` as a degenerate operational reference;
- the payment-day `date_key`;
- the customer version whose validity range contains `payment_date`;
- `amount` and `method` as measures/attributes.

The temporal join is:

```sql
SET search_path TO dwh, training, public;

SELECT p.payment_id,
       p.order_id,
       dd.date_key,
       dc.customer_sk,
       p.amount,
       p.method
FROM training.payments p
JOIN training.orders o USING (order_id)
JOIN dim_date dd ON dd.date_actual = p.payment_date::date
JOIN dim_customer dc
  ON dc.customer_id = o.customer_id
 AND p.payment_date::date >= dc.valid_from
 AND p.payment_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
ORDER BY p.payment_id
LIMIT 20;
```

After running the solution, verify source-to-fact completeness:

```sql
SET search_path TO dwh, training, public;

SELECT (SELECT COUNT(*) FROM dim_country) AS countries,
       (SELECT COUNT(*) FROM fact_payments) AS fact_payment_rows,
       (SELECT COUNT(*) FROM training.payments) AS source_payment_rows,
       (SELECT COUNT(*) FROM dim_customer WHERE country_sk IS NULL)
         AS customers_without_country_key;
```

The two payment counts must match and `customers_without_country_key` must be
zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 2, read from `training.payments`, `training.orders`, `dim_date`, and `dim_customer`. Compute `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-52 Exercise 2, expected output: one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-. The final columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`. The final order is `p.payment_id`.
- **Independent verification:** For sql-52 Exercise 2, evaluate each of `customer_sk`, and `amount` in a separate control `SELECT` over `training.payments`, `training.orders`, `dim_date`, and `dim_customer`; require one final row and compare every value. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `p.payment_id`.
- **Intermediate relation check:** For sql-52 Exercise 2, start with the first relation in `training.payments`, `training.orders`, `dim_date`, and `dim_customer`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-52 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `training.payments`, `training.orders`, `dim_date`, and `dim_customer`, preserve exactly one summary row, and finish with `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method` ordered by `p.payment_id`.
- **Alternative/trade-off:** For sql-52 Exercise 2, the chosen form is justified by this lesson-specific rationale: The answer creates one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-day `date_key`; - the customer version whose vali. Evaluate another form against the concrete expected result (one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `p.payment_id`.

## Required Days 52–54 sequence

1. Run `day52_solutions.sql` once in database `course`; it persists the base
   warehouse plus both Day 52 exercises.
2. Run `day53_solutions.sql` in the same database. It validates SCD work inside
   a transaction and rolls it back.
3. Run `day54_solutions.sql` in the same database. It validates aggregates and
   the refresh procedure inside a transaction and rolls them back.

Day 54 depends on committed Day 52 state, not on rolled-back Day 53 changes.

## Safety and pitfalls

- Do not run Day 52 against a schema named `dwh` that contains unrelated work.
- Use `ON_ERROR_STOP=1`; otherwise `psql` can continue after a failed statement
  and leave a misleading partial exercise.
- Dimension validity uses inclusive date bounds. Close an old version on the
  day before the new version starts.
- A fact load must reconcile to source counts before it is trusted.

## Exercise 3 — State the sales fact grain

`COUNT(*)`, distinct orders, and distinct order-item keys prove that
`fact_sales` is one row per order line. An order can therefore repeat.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 3, read from `fact_sales`. Compute `fact_rows`, `orders`, and `distinct_order_items` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-52 Exercise 3, expected output: one row per order line. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
- **Independent verification:** For sql-52 Exercise 3, evaluate each of `fact_rows`, `orders`, and `distinct_order_items` in a separate control `SELECT` over `fact_sales`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-52 Exercise 3, select `order_id` from `fact_sales` before adding derived columns.
- **Clause check:** For sql-52 Exercise 3, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `fact_sales`, preserve exactly one summary row, and finish with `fact_rows`, `orders`, and `distinct_order_items`.
- **Alternative/trade-off:** For sql-52 Exercise 3, the chosen form is justified by this lesson-specific rationale: `COUNT()`, distinct orders, and distinct order-item keys prove that `fact_sales` is one row per order line. Evaluate another form against the concrete expected result (one row per order line) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 4 — Route unknown members deliberately

The solution reserves surrogate key `-1` in referenced dimensions and shows a
missing natural customer key mapping to it. This policy must not hide a broken
required mapping.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 4, read from `dim_country`, `dim_customer`, and `dim_product`. Build the answer toward `routed_customer_sk`; keep `routed_customer_sk` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-52 Exercise 4, expected output: one row per `routed_customer_sk`. The final columns are `routed_customer_sk`.
- **Independent verification:** For sql-52 Exercise 4, project `routed_customer_sk` plus the raw source columns from `dim_country`, `dim_customer`, and `dim_product` at each join stage; record row count and distinct `routed_customer_sk`, then assert the final `routed_customer_sk` values match those staged rows without unintended fanout or loss. Add one source row with a new `routed_customer_sk`; verify the result gains exactly one row carrying that `routed_customer_sk` value.
- **Intermediate relation check:** For sql-52 Exercise 4, start with the first relation in `dim_country`, `dim_customer`, and `dim_product`; after each join, record total rows and distinct `routed_customer_sk` so the exact fanout or loss is visible.
- **Clause check:** For sql-52 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `dim_country`, `dim_customer`, and `dim_product`, preserve one row per `routed_customer_sk`, and finish with `routed_customer_sk`.
- **Alternative/trade-off:** For sql-52 Exercise 4, the chosen form is justified by this lesson-specific rationale: The solution reserves surrogate key `-1` in referenced dimensions and shows a missing natural customer key mapping to it. Evaluate another form against the concrete expected result (one row per `routed_customer_sk`) and the verification above.
- **Edge case:** Add one source row with a new `routed_customer_sk`; verify the result gains exactly one row carrying that `routed_customer_sk` value.

## Exercise 5 — Reconcile completeness and amount

Fact/source row counts and rounded line amounts appear together. Either a row
or amount difference blocks trust in the warehouse load.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 5, read from `fact_sales`, and `training.order_items`. Compute `fact_rows`, `source_rows`, `fact_amount`, and `source_amount` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-52 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
- **Independent verification:** For sql-52 Exercise 5, evaluate each of `fact_rows`, `source_rows`, `fact_amount`, and `source_amount` in a separate control `SELECT` over `fact_sales`, and `training.order_items`; require one final row and compare every value. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
- **Intermediate relation check:** For sql-52 Exercise 5, select `order_item_id` from `fact_sales`, and `training.order_items` before adding derived columns.
- **Clause check:** For sql-52 Exercise 5, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `fact_sales`, and `training.order_items`, preserve exactly one summary row, and finish with `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
- **Alternative/trade-off:** For sql-52 Exercise 5, the chosen form is justified by this lesson-specific rationale: Fact/source row counts and rounded line amounts appear together. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.

## Exercise 6 — Handle late dates explicitly

The query lists payments outside `dim_date`. The chosen policy is fail and
extend the dimension because silently mapping a real accounting date to unknown
would destroy time analysis.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 6, read from `training.payments`, and `dim_date`. Build the answer toward `payment_id`, and `date`; keep `payment_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-52 Exercise 6, expected output: one row per `payment_id`. The final columns are `payment_id`, and `date`. The final order is `p.payment_id`.
- **Independent verification:** For sql-52 Exercise 6, project `payment_id` plus the raw source columns from `training.payments`, and `dim_date` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, and `date` values match those staged rows without unintended fanout or loss. Add one row for which `(d.date_key IS NULL)` is true and one for which it is false; verify only the matching `payment_id` value is returned.
- **Intermediate relation check:** For sql-52 Exercise 6, start with the first relation in `training.payments`, and `dim_date`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-52 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `training.payments`, and `dim_date`, preserve one row per `payment_id`, and finish with `payment_id`, and `date` ordered by `p.payment_id`.
- **Alternative/trade-off:** For sql-52 Exercise 6, the chosen form is justified by this lesson-specific rationale: The query lists payments outside `dim_date`. Evaluate another form against the concrete expected result (one row per `payment_id`) and the verification above.
- **Edge case:** Add one row for which `(d.date_key IS NULL)` is true and one for which it is false; verify only the matching `payment_id` value is returned.
