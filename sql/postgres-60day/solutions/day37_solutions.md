# Day 37 — Solutions (Partitioning and Sharding)

We explore PostgreSQL table partitioning (declarative) for performance and manageability on large tables, and discuss sharding strategies at the application/DB layer. We include creation, indexing, pruning, and maintenance patterns.

Setup
- Declarative partitioning by RANGE/LIST on large fact tables (e.g., orders by order_date)
- Global vs local indexes: in PG, indexes are per-partition; create on each partition or use default partitioned indexes (PG11+)

Exercise 1 — Create a partitioned table by month
```sql
-- Parent table
CREATE TABLE IF NOT EXISTS orders_p (
  order_id     BIGINT NOT NULL,
  customer_id  BIGINT NOT NULL,
  order_date   timestamptz NOT NULL,
  total_amount numeric(12,2) NOT NULL
) PARTITION BY RANGE (order_date);

-- Create monthly partitions (example for 2025 Q1)
CREATE TABLE IF NOT EXISTS orders_2025_01 PARTITION OF orders_p
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS orders_2025_02 PARTITION OF orders_p
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS orders_2025_03 PARTITION OF orders_p
  FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Index per partition (or create a partitioned index on parent in PG11+)
CREATE INDEX IF NOT EXISTS idx_orders_2025_01_date ON orders_2025_01(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_2025_02_date ON orders_2025_02(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_2025_03_date ON orders_2025_03(order_date);
```
Why
- Queries filtered by order_date prune partitions, scanning only relevant ones.

Exercise 2 — Insert, query, and confirm pruning
```sql
-- Insert routes to the right partition based on order_date
INSERT INTO orders_p(order_id, customer_id, order_date, total_amount)
VALUES (101, 1, '2025-02-17 12:00+00', 99.99);

-- Query last 30 days
EXPLAIN (ANALYZE)
SELECT * FROM orders_p
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days';
```
Notes
- Explain output should show only recent partitions scanned.

Exercise 3 — Default partition and maintenance
```sql
-- Default catch-all partition for out-of-range data
CREATE TABLE IF NOT EXISTS orders_default PARTITION OF orders_p DEFAULT;

-- Detach or drop old partitions to purge data quickly
ALTER TABLE orders_p DETACH PARTITION orders_2024_01;  -- archive elsewhere then DROP TABLE orders_2024_01;
```
Guidance
- Automate partition creation/retention with scheduled jobs.
- Consider partitioned foreign keys (PG15+) or enforce via app logic.

Sharding discussion
- Logical sharding by customer/region at app layer; use separate schemas/DBs per shard.
- Router maps shard key → connection. Keep cross-shard joins out of the DB; aggregate in the app or via federation layer.
- Use identical schema per shard; central metadata registry for shard location.
