# Day 54 Solutions — Warehouse Aggregates and Refresh Procedure

Run [`day52_solutions.sql`](day52_solutions.sql) first in the same database.
Day 54 creates and tests aggregate objects inside a transaction, then rolls
everything back. The complete runnable answer is
[`day54_solutions.sql`](day54_solutions.sql).

## Exercise 1 — `agg_sales_product_month`

The answer uses this grain and schema:

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TABLE agg_sales_product_month (
  year int NOT NULL,
  month int NOT NULL,
  product_sk int NOT NULL REFERENCES dim_product(product_sk),
  revenue numeric(14,2) NOT NULL,
  units bigint NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);

INSERT INTO agg_sales_product_month(
  year, month, product_sk, revenue, units, orders
)
SELECT dd.year,
       dd.month,
       fs.product_sk,
       ROUND(SUM(fs.amount), 2),
       SUM(fs.quantity),
       COUNT(DISTINCT fs.order_id)
FROM fact_sales fs
JOIN dim_date dd USING (date_key)
GROUP BY dd.year, dd.month, fs.product_sk;

WITH aggregate_total AS (
  SELECT year, month, SUM(revenue) AS revenue
  FROM agg_sales_product_month
  GROUP BY year, month
), fact_total AS (
  SELECT dd.year, dd.month, ROUND(SUM(fs.amount), 2) AS revenue
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  GROUP BY dd.year, dd.month
)
SELECT a.year,
       a.month,
       a.revenue AS aggregate_revenue,
       f.revenue AS fact_revenue,
       a.revenue - f.revenue AS difference
FROM aggregate_total a
JOIN fact_total f USING (year, month)
ORDER BY a.year, a.month;

ROLLBACK;
```

The two sides are aggregated independently before joining, preventing join
fanout. Expected `difference` is zero for every built month.

## Exercise 2 — Refresh all aggregates for `(year, month)`

The executable solution creates:

```text
dwh.refresh_sales_aggregates_solution(p_year int, p_month int)
```

Within one procedure call it:

1. deletes the target month from category, customer, and product aggregates;
2. inserts category revenue and units;
3. inserts customer revenue and distinct orders;
4. inserts product revenue, units, and distinct orders.

The delete-then-insert design is idempotent for a target period. The answer
discovers the latest fact month and calls the procedure for that month, then
reconciles product aggregate revenue with `fact_sales`.

To inspect the result after running the canonical file, remember that it ends
with `ROLLBACK`; the aggregate objects intentionally will not persist.

## Required Days 52–54 sequence

```text
psql -X -v ON_ERROR_STOP=1 -d course -f day52_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day53_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day54_solutions.sql
```

Day 52 persists course-owned warehouse state. Days 53 and 54 prove their
solutions and roll back. Day 54 does not require Day 53 changes to persist.

## Reasoning, state, and pitfalls

- State the aggregate grain in the primary key; otherwise duplicate loads can
  silently inflate reports.
- Delete and rebuild all related aggregates in one transaction so readers do
  not observe mismatched periods.
- Reconcile totals after every refresh and treat nonzero differences as a load
  failure.
- The compact seed does not justify aggregate tables for performance; this is a
  warehouse-design exercise.
- Reconcile independently aggregated sides; joining aggregates to detail rows
  before summing can fan out both measures.

## Exercise 3 — Account for late facts

The period inventory identifies every loaded month. A late fact requires
refreshing its own affected period, not merely the newest month.

## Exercise 4 — Refresh atomically

Delete and all aggregate inserts run in one transaction through the procedure.
Failure rolls back the whole period instead of leaving partial tables.

## Exercise 5 — Make reconciliation NULL-safe

FULL JOIN preserves a period missing on either side, and coalesced arithmetic
turns that absence into a visible nonzero difference.

## Exercise 6 — Prove idempotency

The answer snapshots category aggregates, reruns the same latest period, and
uses two-way `EXCEPT`. Both difference sets must be empty.
