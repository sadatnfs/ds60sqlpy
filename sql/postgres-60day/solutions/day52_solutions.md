# Day 52 Solutions: Data Warehouse Design, Part 1


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day52_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Fact table, Dimension, Surrogate key. Its worked-model focus is:
Write the grain beside every table before loading it. Load `dim_date` and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in `fact_sales`. Compare fact row count with source `order_items` and check every key resolves once before committing Day 52.

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
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f day52_solutions.sql
```

The file first includes `../day52_project3_dwh_part1.sql`, which builds and
commits `dim_date`, Type-2-ready customer/product dimensions, and `fact_sales`.
It then completes all six exercises in a second committed transaction.

## Exercise 1: Add `dim_country`

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

The `NOT NULL` rule is a contract for every later load: Day 53's SCD2 inserts
must supply `country_sk` for each new version. Day 53 also starts by adding this
same link, inside its rolled-back transaction, when a warehouse was built by the
Day 52 learner base alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 1, create `dim_country(country_sk, country_code)` with one row per distinct `training.customers.country`, add `country_sk` to `dim_customer` as a foreign key to it, backfill it from the text `country`, and make it `NOT NULL` before the final `COMMIT`.
- **Expected result/shape:** For sql-52 Exercise 1, expected output: `INSERT 0 8` for the country codes, `UPDATE 500` for the backfill, and `ALTER TABLE` for the `NOT NULL` change, so every customer-dimension version has exactly one `country_sk`. Days 53 and 54 run against this committed state, and Day 53's SCD2 inserts must keep it.
- **Independent verification:** For sql-52 Exercise 1, right after the backfill, confirm that `SELECT COUNT(*) FROM dim_country` is 8, that no `dim_customer` row has a NULL `country_sk`, and that joining `dim_customer` to `dim_country` on `country_sk` gives `country_code = country` on every row; after a savepoint, an `INSERT` into `dim_customer` without `country_sk` must fail with SQLSTATE `23502`, then roll back to the savepoint.
- **Intermediate relation check:** For sql-52 Exercise 1, load `dim_country` and backfill `country_sk` before you add `NOT NULL`; `SET NOT NULL` fails while any row is still NULL.
- **Clause check:** For sql-52 Exercise 1, the solution uses `CREATE TABLE dim_country` with an identity key and a unique `country_code`, `INSERT ... SELECT DISTINCT country FROM training.customers`, `ALTER TABLE dim_customer ADD COLUMN country_sk int REFERENCES dim_country (country_sk)`, an `UPDATE ... FROM dim_country` backfill, and `ALTER COLUMN country_sk SET NOT NULL`.
- **Alternative/trade-off:** For sql-52 Exercise 1, keeping only the text `country` avoids a join, but the conformed `country_sk` gives every fact and dimension one shared country key; the `NOT NULL` rule then obliges every later load, including Day 53's SCD2 inserts, to supply that key.
- **Edge case:** A customer whose country is missing from `dim_country` keeps a NULL `country_sk` after the backfill, so `SET NOT NULL` fails until `dim_country` gains that code or an explicit unknown member (Exercise 4).

## Exercise 2: Add `fact_payments`

The answer creates one row per source payment with:

- `payment_id` as the idempotent fact key;
- `order_id` as a degenerate operational reference;
- the payment-day `date_key`;
- the customer version whose validity range contains `payment_date`;
- `amount` and `method` as measures/attributes.

The temporal join is:

```sql
SET search_path TO dwh, training, public;

SELECT
  p.payment_id,
  p.order_id,
  dd.date_key,
  dc.customer_sk,
  p.amount,
  p.method
FROM
  training.payments p
  JOIN training.orders o USING (order_id)
  JOIN dim_date dd ON dd.date_actual = p.payment_date::date
  JOIN dim_customer dc ON dc.customer_id = o.customer_id
    AND p.payment_date::date >= dc.valid_from
    AND p.payment_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
  ORDER BY
    p.payment_id
  LIMIT 20;
```

After running the solution, verify source-to-fact completeness:

```sql
SET search_path TO dwh, training, public;

SELECT
  (
    SELECT
      COUNT(*)
    FROM
      dim_country) AS countries,
  (
    SELECT
      COUNT(*)
    FROM
      fact_payments) AS fact_payment_rows,
  (
    SELECT
      COUNT(*)
    FROM
      training.payments) AS source_payment_rows,
  (
    SELECT
      COUNT(*)
    FROM
      dim_customer
    WHERE
      country_sk IS NULL) AS customers_without_country_key;
```

The two payment counts must match and `customers_without_country_key` must be
zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 2, create `fact_payments` with one row per `training.payments` row, keyed by `payment_id`, and load it by joining each payment to its order, to `dim_date` on the payment date, and to the `dim_customer` version valid on that date.
- **Expected result/shape:** For sql-52 Exercise 2, expected output: `INSERT 0 3836`, one fact row per source payment, then a check row with `countries` 8, `fact_payment_rows` 3836, and `source_payment_rows` 3836. The fact columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`.
- **Independent verification:** For sql-52 Exercise 2, confirm that `fact_payment_rows` equals `source_payment_rows` (3836) and that `SELECT SUM(amount) FROM fact_payments` equals `SELECT SUM(amount) FROM training.payments` (1831900.81); a join that lost payments would lower the count, and a join to every customer version would raise it.
- **Intermediate relation check:** For sql-52 Exercise 2, join `training.payments` to `orders`, `dim_date`, and `dim_customer` one table at a time and check that the row count stays 3836 after each join.
- **Clause check:** For sql-52 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `training.payments`, `training.orders`, `dim_date`, and `dim_customer`, preserve one row per source payment, and finish with `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method` ordered by `p.payment_id`.
- **Alternative/trade-off:** For sql-52 Exercise 2, the chosen form is justified by this lesson-specific rationale: The answer creates one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-day `date_key`; - the customer version whose vali. Evaluate another form against the concrete expected result (one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-) and the verification above.
- **Edge case:** A payment whose date falls outside `dim_date` would be dropped silently by the inner join; Exercise 6 lists such payments with a `LEFT JOIN ... WHERE d.date_key IS NULL` check.

## Required Days 52 to 54 sequence

1. Run `day52_solutions.sql` once in `advanced_sql_training`; it persists the
   base warehouse plus the Day 52 exercise objects: `dim_country`, the
   `NOT NULL` `country_sk`, `fact_payments`, and the `-1` unknown members.
2. Run `day53_solutions.sql` in the same database. It validates SCD work inside
   a transaction and rolls it back.
3. Run `day54_solutions.sql` in the same database. It validates aggregates and
   the refresh procedure inside a transaction and rolls them back.

Day 54 depends on committed Day 52 state, not on rolled-back Day 53 changes.
The learner Day 53 and Day 54 files also accept this state, and the Day 53 and
Day 54 solutions also accept a warehouse built by the Day 52 learner file alone.

## Safety and pitfalls

- Do not run Day 52 against a schema named `dwh` that contains unrelated work.
- Use `ON_ERROR_STOP=1`; otherwise `psql` can continue after a failed statement
  and leave a misleading partial exercise.
- Dimension validity uses inclusive date bounds. Close an old version on the
  day before the new version starts.
- A fact load must reconcile to source counts before it is trusted.

## Exercise 3: State the sales fact grain

`COUNT(*)`, distinct orders, and distinct order-item keys prove that
`fact_sales` is one row per order line. An order can therefore repeat.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 3, read from `fact_sales` and count its rows, its distinct `order_id` values, and its distinct `order_item_id` values.
- **Expected result/shape:** For sql-52 Exercise 3, expected output: one row with `fact_rows` 13085, `orders` 4362, and `distinct_order_items` 13085, which shows that `fact_sales` has one row per order line and that `order_id` alone does not identify a row. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
- **Independent verification:** For sql-52 Exercise 3, confirm that `fact_rows` and `distinct_order_items` both equal `SELECT COUNT(*) FROM training.order_items` (13085) while `orders` is only 4362; `SELECT order_id FROM fact_sales GROUP BY order_id HAVING COUNT(*) > 1` returns 3490 orders, which proves that `order_id` repeats.
- **Intermediate relation check:** For sql-52 Exercise 3, compare `COUNT(*)` with `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT order_item_id)`; the key is the column whose distinct count equals the row count.
- **Clause check:** For sql-52 Exercise 3, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `fact_sales`, preserve exactly one summary row, and finish with `fact_rows`, `orders`, and `distinct_order_items`.
- **Alternative/trade-off:** For sql-52 Exercise 3, the chosen form is justified by this lesson-specific rationale: `COUNT()`, distinct orders, and distinct order-item keys prove that `fact_sales` is one row per order line. Evaluate another form against the concrete expected result (one row per order line) and the verification above.
- **Edge case:** Matching counts on today's data do not stop a later duplicate load; only a unique constraint on `order_item_id` enforces the grain.

## Exercise 4: Route unknown members deliberately

The solution reserves surrogate key `-1` in referenced dimensions and shows a
missing natural customer key mapping to it. This policy must not hide a broken
required mapping.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 4, add an unknown member with surrogate key -1 to `dim_country`, `dim_customer`, and `dim_product`, then route a source row whose `customer_id` (-999) has no dimension match to that member with `COALESCE(dc.customer_sk, -1)` after a `LEFT JOIN`.
- **Expected result/shape:** For sql-52 Exercise 4, expected output: three `INSERT 0 1` commands and one row whose `routed_customer_sk` is -1. The final columns are `routed_customer_sk`.
- **Independent verification:** For sql-52 Exercise 4, confirm that `SELECT customer_sk FROM dim_customer WHERE customer_sk = -1` returns one row and that the routing query returns -1 for `customer_id` -999; replace -999 with 1 and confirm that it returns that customer's real `customer_sk` (1) instead.
- **Intermediate relation check:** For sql-52 Exercise 4, insert the unknown members first and query each one by its -1 key before you test the routing `LEFT JOIN`.
- **Clause check:** For sql-52 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `dim_country`, `dim_customer`, and `dim_product`, preserve one routed row, and finish with `routed_customer_sk`.
- **Alternative/trade-off:** For sql-52 Exercise 4, the chosen form is justified by this lesson-specific rationale: The solution reserves surrogate key `-1` in referenced dimensions and shows a missing natural customer key mapping to it. Evaluate another form against the concrete expected result (one row per `routed_customer_sk`) and the verification above.
- **Edge case:** `dim_country.country_sk` is `GENERATED ALWAYS AS IDENTITY`, so inserting -1 needs `OVERRIDING SYSTEM VALUE`; the other dimensions accept -1 directly because their keys only default from a sequence.

## Exercise 5: Reconcile completeness and amount

Fact/source row counts and rounded line amounts appear together. Either a row
or amount difference blocks trust in the warehouse load.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 5, compare `fact_sales` with `training.order_items`: the two row counts, the total fact `amount`, and the source line total `ROUND(SUM(quantity * unit_price * (1 - discount)), 2)`.
- **Expected result/shape:** For sql-52 Exercise 5, expected output: one row with `fact_rows` and `source_rows` both 13085, `fact_amount` 2355648.13, and `source_amount` 2355647.12; the 1.01 gap comes from rounding each fact line to cents. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
- **Independent verification:** For sql-52 Exercise 5, confirm equal row counts, then recompute the source with the fact's rounding rule, `SELECT SUM(ROUND(quantity * unit_price * (1 - discount), 2)) FROM training.order_items`, and expect 2355648.13, exactly `fact_amount`; a gap that remains after that would be a real load error.
- **Intermediate relation check:** For sql-52 Exercise 5, count rows first, then compare totals; when the totals differ, check whether the fact rounds each line before summing.
- **Clause check:** For sql-52 Exercise 5, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `fact_sales`, and `training.order_items`, preserve exactly one summary row, and finish with `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
- **Alternative/trade-off:** For sql-52 Exercise 5, the chosen form is justified by this lesson-specific rationale: Fact/source row counts and rounded line amounts appear together. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Rounding per line and rounding the total once are both defensible, but a reconciliation must apply the same rule on both sides before it calls a difference an error.

## Exercise 6: Handle late dates explicitly

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
