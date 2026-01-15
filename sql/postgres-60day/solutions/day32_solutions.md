# Day 32 — Solutions (Index Fundamentals)

We cover index types, creation, selectivity, multi-column order, covering/Index Only Scans, and statistics. Examples include btree (most common), hash, GIN/GiST for specialized data, and BRIN for large append-only tables.

Setup
- Tables: orders(order_id, customer_id, order_date, total_amount), customers(email, country), products(name, sku, extra jsonb)
- Index types overview
  - btree: equality, range, ORDER BY
  - hash: equality only (rarely used; improved since PG10)
  - GIN: array containment, JSONB @>, trigram (text search)
  - GiST: geometric, ranges, KNN
  - BRIN: very large tables where values correlate with physical location

Exercise 1 — Create a selective time filter index and verify usage
```sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days';
```
Why
- Time-slicing is common; btree on order_date enables fast range scans.
- Check plan shows Index Scan (or Bitmap) with few buffer reads vs Seq Scan.

Exercise 2 — Multi-column index and sort order
```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);

-- Filter by customer, ordered by date: can read in index order (no sort)
EXPLAIN (ANALYZE)
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = 123
ORDER BY order_date DESC
LIMIT 50;
```
Notes
- Index leftmost prefix rule: predicates/sort must align with (customer_id, order_date). Reversing ORDER BY may still be satisfied backward.
- For frequent queries ordering by both, the composite index avoids a sort.

Exercise 3 — Covering index and Index Only Scan
```sql
-- Index includes columns needed by the query; visibility map permitting, engine can avoid heap fetch
CREATE INDEX IF NOT EXISTS idx_orders_cover ON orders(order_date, total_amount) INCLUDE (order_id);

EXPLAIN (ANALYZE)
SELECT order_date, total_amount, order_id
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days';
```
Explanation
- INCLUDE (order_id) stores the extra column in index payload for Index Only Scan while keeping key order on (order_date, total_amount).
- Check plan node: Index Only Scan (if visibility map conditions met).

Exercise 4 — JSONB and text search indexes (GIN, trigram)
```sql
-- JSONB containment
CREATE INDEX IF NOT EXISTS idx_products_extra_gin ON products USING gin (extra jsonb_path_ops);
SELECT product_id FROM products WHERE extra @> '{"meta": {"channel": "email"}}';

-- Trigram for ILIKE / %foo%
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
SELECT product_id FROM products WHERE name ILIKE '%wireless%';
```
Why
- GIN accelerates containment and key-existence predicates on JSONB.
- Trigram index speeds infix ILIKE/regex scans on text.

Exercise 5 — BRIN for huge append-only tables
```sql
CREATE INDEX IF NOT EXISTS idx_orders_brin_date ON orders USING brin (order_date);
-- Best when table has natural physical correlation with order_date and you scan large ranges
```
Caveats
- Run ANALYZE after bulk loads; statistics guide the planner.
- Keep indexes lean; every index slows writes. Create what queries need.
