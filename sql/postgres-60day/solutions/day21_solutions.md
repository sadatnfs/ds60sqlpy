# Day 21 — Solutions: Distribution Functions

The learner script introduces `NTILE` and `PERCENT_RANK`. These answers use the
tables created by `00_setup.sql` and match both exercises in
`day21_distribution_functions.sql`.

## Exercise 1 — Product deciles by units sold in the last 90 days

First aggregate to one row per product, then apply `NTILE(10)`. The `LEFT JOIN`
keeps products with no qualifying sales, and the `product_id` tie-breaker makes
bucket assignment deterministic when products have equal unit counts.

```sql
SET search_path TO training, public;

WITH product_units AS (
  SELECT p.product_id,
         p.name,
         p.category,
         COALESCE(
           SUM(oi.quantity) FILTER (
             WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
           ),
           0
         ) AS units_90d
  FROM products p
  LEFT JOIN order_items oi ON oi.product_id = p.product_id
  LEFT JOIN orders o ON o.order_id = oi.order_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT product_id,
       name,
       category,
       units_90d,
       NTILE(10) OVER (ORDER BY units_90d DESC, product_id) AS sales_decile
FROM product_units
ORDER BY sales_decile, units_90d DESC, product_id;
```

Expected shape: one row per product. Decile `1` contains the highest-volume
products and decile `10` the lowest-volume products. `NTILE` balances row
counts; it does not promise that tied values stay in the same bucket.

## Exercise 2 — Order percentile rank within each customer

```sql
SET search_path TO training, public;

SELECT customer_id,
       order_id,
       total_amount,
       ROUND(
         PERCENT_RANK() OVER (
           PARTITION BY customer_id
           ORDER BY total_amount
         )::numeric,
         4
       ) AS customer_percentile_rank
FROM orders
ORDER BY customer_id, total_amount, order_id;
```

Expected shape: one row per order. Within each customer, the smallest total has
rank `0`; the largest has rank `1` when that customer has more than one order.
Equal totals share a rank. The ascending sort is intentional: a higher
percentile means a higher-value order.

## Pitfalls

- Aggregate before applying `NTILE`; otherwise each order line, not each
  product, would be bucketed.
- `PERCENT_RANK` returns `double precision`, so cast to `numeric` before using
  PostgreSQL's two-argument `ROUND`.
- A 90-day window is relative to execution time. The deterministic setup keeps
  recent orders so this result does not become empty.
