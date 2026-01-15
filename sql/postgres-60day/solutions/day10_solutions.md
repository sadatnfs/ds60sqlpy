# Day 10 — Solutions (DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT)

We practice data-modification statements that are driven by subqueries: INSERT ... SELECT, and INSERT ... ON CONFLICT (UPSERT). We wrap examples in transactions and ROLLBACK for safety during learning.

Setup
- Schema: training; tables: customers, orders, order_items, products
- Safety: Use `BEGIN; ... ROLLBACK;` while exploring so no persistent changes occur. Replace ROLLBACK with COMMIT to persist.

Exercise 1 — Insert top 1000 high-value customers into a marketing list
Goal: Compute lifetime revenue (LTV) per customer by aggregating order line values, then insert top 1000 into a table `marketing_list` with customer_id and lifetime_revenue.

Reference solution
```sql
BEGIN;
CREATE TABLE IF NOT EXISTS marketing_list (
  customer_id      BIGINT PRIMARY KEY,
  lifetime_revenue NUMERIC(12,2) NOT NULL,
  added_at         TIMESTAMPTZ   NOT NULL DEFAULT now()
);

WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, ROUND(SUM(order_value),2) AS lifetime_revenue
  FROM order_values
  GROUP BY customer_id
)
INSERT INTO marketing_list(customer_id, lifetime_revenue)
SELECT customer_id, lifetime_revenue
FROM ltv
ORDER BY lifetime_revenue DESC
LIMIT 1000
ON CONFLICT (customer_id) DO UPDATE
  SET lifetime_revenue = EXCLUDED.lifetime_revenue,
      added_at = now();
ROLLBACK; -- swap to COMMIT to persist
```
Line-by-line
- CREATE TABLE IF NOT EXISTS: idempotent; run safely multiple times. `customer_id` is PK to allow UPSERT behavior.
- order_values CTE: Aggregate to one row per order to avoid double-counting when joining customers later; we keep customer_id to roll up per customer.
- ltv CTE: Sum order totals per customer → lifetime revenue; ROUND for presentation.
- INSERT ... SELECT: Streams the computed rows into the target table, sorted by revenue and limited to top 1000. ORDER BY + LIMIT is respected by Postgres for INSERT target when used directly in the SELECT.
- ON CONFLICT (customer_id) DO UPDATE: If an entry already exists, update revenue and timestamp. The special table `EXCLUDED` holds values from the would-be inserted row.
Tips and pitfalls
- If you define "lifetime_revenue" differently (e.g., include taxes/shipping/returns), align the CTE to your business definition.
- To keep historical snapshots of marketing lists, use a partitioned table (by date) or write to a new table name per snapshot instead of UPSERTing.
- Validate results: Compare `SELECT COUNT(*) FROM marketing_list;` and top/bottom values.

Exercise 2 — Upsert product prices from a pricing feed
Goal: Load a (staging) feed of new prices keyed by SKU, map SKUs to product_id, then upsert into products while stamping `updated_at`.

Reference solution
```sql
BEGIN;
-- Example staging table for demo
CREATE TEMP TABLE pricing_feed (
  sku TEXT PRIMARY KEY,
  new_price NUMERIC(12,2) NOT NULL,
  effective_at TIMESTAMPTZ NOT NULL
);
-- Example rows (for testing only)
INSERT INTO pricing_feed VALUES
  ('SKU-001', 19.99, now()),
  ('SKU-002', 24.50, now());

-- Ensure products has an updated_at column (idempotent)
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- Map feed SKUs to product ids, then upsert
WITH mapped AS (
  SELECT p.product_id, f.new_price, f.effective_at
  FROM pricing_feed f
  JOIN products p ON p.sku = f.sku
)
INSERT INTO products(product_id, price, updated_at)
SELECT product_id, new_price, effective_at
FROM mapped
ON CONFLICT (product_id) DO UPDATE
  SET price = EXCLUDED.price,
      updated_at = EXCLUDED.updated_at;
ROLLBACK; -- swap to COMMIT to persist
```
Explanation
- CREATE TEMP TABLE: Lives for the session only; ideal for staging.
- ALTER TABLE ... ADD COLUMN IF NOT EXISTS: Avoids errors if the column is already present.
- CTE mapped: Joins feed to canonical products by SKU. If there are unexpected SKUs, they will be dropped here; alternatively capture them via a LEFT JOIN and write rejects to an audit table.
- INSERT ... ON CONFLICT: Uses product_id as the unique key to upsert. Many teams maintain `products(product_id)` as PK and a separate unique index on `products(sku)`. Adjust the conflict target to your uniqueness constraint (e.g., `(sku)`).
- Time semantics: We stamp `updated_at` from the feed's effective time; alternatively use `now()` for the moment of application.
Checks and hardening
- Constrain prices to be positive: add a CHECK (price >= 0).
- If feeds can contain stale updates, consider `WHERE products.updated_at IS NULL OR EXCLUDED.updated_at >= products.updated_at` in the DO UPDATE clause.
- Wrap in a transaction and COMMIT atomically if part of a larger pipeline.

Delete patterns (bonus)
- Use DELETE with a subquery to remove staging rows after successful upsert:
```sql
DELETE FROM pricing_feed pf
USING products p
WHERE p.sku = pf.sku; -- clears staged rows that mapped successfully
```

Smoke tests
- Count upserts: Compare `SELECT COUNT(*) FROM pricing_feed;` with updated row count in `products` over the same SKUs.
- Spot-check prices: `SELECT sku, price, updated_at FROM products WHERE sku IN ('SKU-001','SKU-002');`
