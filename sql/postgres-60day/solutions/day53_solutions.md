# Day 53 Solutions — SCD Type 2 and Temporal Fact Keys

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
