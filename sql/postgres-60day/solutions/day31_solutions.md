# Day 31 — Solutions (EXPLAIN/ANALYZE: Understanding Query Plans)

We learn to read query plans, identify access paths (Seq Scan, Index Scan/Only, Bitmap), join strategies (Nested Loop, Hash Join, Merge Join), and key counters (rows vs actual rows). We also enable timing and buffer reporting.

Setup
- Enable richer output:
  - `EXPLAIN (ANALYZE, BUFFERS, TIMING ON)` for runtime, loop counts, and I/O
  - `SET enable_seqscan = off;` temporarily to test index usage (don’t leave it off)
- Helpful GUCs: `SET random_page_cost = 1.1` (SSD‑like), `SET work_mem` for sort/hash

Exercise 1 — Baseline plan vs indexed plan
```sql
-- Baseline: orders last 30 days (expect Index Scan on orders(order_date))
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders o
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days';
```
What to read
- Node types: Seq Scan vs Index Scan; Filter; Recheck Cond (bitmaps)
- Rows: estimated vs actual (rows= vs actual rows=). Large mismatch ⇒ stale stats; run `ANALYZE orders;`
- Buffers: shared hit vs read; many reads imply I/O bound

Create an index (if missing)
```sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
```
Re‑explain and compare
- Expect Index Scan with fewer pages read; lower total time

Exercise 2 — Join strategies: when a Hash Join wins
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id, c.country
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days';
```
Interpretation
- Hash Join usually chosen when the build side (customers) is small enough; check Hash sizing (batches)
- If you see Nested Loop + Index, ensure the inner index supports the join key

Exercise 3 — Bitmap Index Scan for selective IN lists
```sql
-- If you query many specific product_ids, bitmap may appear
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM order_items oi
WHERE oi.product_id IN (SELECT product_id FROM products WHERE category = 'electronics');
```
Notes
- Bitmap builds a set of row locations then visits heap; good for many scattered hits
- Watch for "Heap Fetches"; Index Only Scan can avoid heap if all columns are in the index and visibility map allows

Exercise 4 — Sort vs Incremental Sort and work_mem
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
ORDER BY customer_id, order_date;
```
Tips
- If you often order by (customer_id, order_date), a multi‑column index may enable Incremental Sort or index ordering
- Increase `work_mem` to avoid external sorts (look for Disk: usage)

Common plan smells and fixes
- Seq Scan on large table without filters ⇒ add predicate/index or partition
- Massive row misestimates ⇒ `ANALYZE`, increase `default_statistics_target` for skewed columns
- Hash Join spilling to disk ⇒ raise `work_mem` for the session, or reduce rows earlier
