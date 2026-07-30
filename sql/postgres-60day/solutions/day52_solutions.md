# Day 52 Solutions — Data Warehouse Design, Part 1

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

## Exercise 4 — Route unknown members deliberately

The solution reserves surrogate key `-1` in referenced dimensions and shows a
missing natural customer key mapping to it. This policy must not hide a broken
required mapping.

## Exercise 5 — Reconcile completeness and amount

Fact/source row counts and rounded line amounts appear together. Either a row
or amount difference blocks trust in the warehouse load.

## Exercise 6 — Handle late dates explicitly

The query lists payments outside `dim_date`. The chosen policy is fail and
extend the dimension because silently mapping a real accounting date to unknown
would destroy time analysis.
