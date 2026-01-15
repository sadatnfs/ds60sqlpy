-- Day 10 - Solutions: DML with Subqueries (INSERT/UPDATE/DELETE/UPSERT)
-- Assumes: customers, orders, order_items, products exist. Temporary/staging tables shown as examples.

/*
Exercise 1) Insert top 1000 high-value customers into a marketing list table.
Why: Use a pre-aggregation of lifetime revenue, then INSERT ... SELECT ordered by revenue with LIMIT.
Notes: We'll create a demo table marketing_list(customer_id, lifetime_revenue, added_at). In your environment, adjust schema as needed.
*/
BEGIN;
CREATE TABLE IF NOT EXISTS marketing_list (
  customer_id   BIGINT PRIMARY KEY,
  lifetime_revenue NUMERIC(12,2) NOT NULL,
  added_at      TIMESTAMPTZ NOT NULL DEFAULT now()
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
ROLLBACK; -- remove ROLLBACK to persist

/*
Exercise 2) Upsert product prices from a pricing feed; record updated_at.
Why: INSERT ... ON CONFLICT (unique key) DO UPDATE SET ...
Notes: We'll assume a staging table pricing_feed(sku TEXT, new_price NUMERIC, effective_at TIMESTAMPTZ).
      We'll map sku→product_id via products.sku (ensure unique index on products(sku)).
*/
BEGIN;
-- Example staging table (for demo)
CREATE TEMP TABLE pricing_feed (
  sku TEXT PRIMARY KEY,
  new_price NUMERIC(12,2) NOT NULL,
  effective_at TIMESTAMPTZ NOT NULL
);
-- Example rows (comment out in production)
INSERT INTO pricing_feed VALUES
  ('SKU-001', 19.99, now()),
  ('SKU-002', 24.50, now());

-- Ensure products has updated_at (if not, adapt or skip)
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- Upsert: join feed to products by SKU, then upsert into products by product_id
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
ROLLBACK; -- remove ROLLBACK to persist

-- End of Day 10 solutions
