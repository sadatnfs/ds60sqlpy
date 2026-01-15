# Day 22 — Solutions (Advanced Windows: Frames, Percentiles, Exclusion, Distribution)

We dive deeper into window framing, distribution functions (percent_rank, cume_dist), and EXCLUDE frame clauses. These tools enable precise analytics without extra joins.

Setup
- Tables: orders(order_date, total_amount, customer_id), order_items, products
- Key idea: The window ORDER BY + frame define what rows each function sees

Exercise 1 — percent_rank and cume_dist on order totals per month
```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS m,
         o.order_id,
         o.total_amount
  FROM orders o
)
SELECT m,
       order_id,
       total_amount,
       ROUND(percent_rank() OVER (PARTITION BY m ORDER BY total_amount), 4) AS pct_rank,
       ROUND(cume_dist()   OVER (PARTITION BY m ORDER BY total_amount), 4) AS cume
FROM monthly
ORDER BY m, total_amount, order_id
LIMIT 200;
```
Explanation
- percent_rank = (rank - 1)/(n - 1): 0 for smallest, 1 for largest when n>1
- cume_dist = cumulative distribution: fraction of rows <= current

Exercise 2 — Rolling sum with value-ties using RANGE vs ROWS
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d, SUM(o.total_amount) AS rev
  FROM orders o GROUP BY 1
)
SELECT d,
       rev,
       SUM(rev) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)   AS sum7_rows,
       SUM(rev) OVER (ORDER BY d RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW) AS sum7_range
FROM daily
ORDER BY d
LIMIT 100;
```
Notes
- ROWS counts rows; RANGE counts peers with same ORDER BY value. For dates, RANGE by time interval expands to all rows in the interval window even if some dates missing

Exercise 3 — EXCLUDE frame to compute peer-contrast metrics
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d, SUM(o.total_amount) AS rev
  FROM orders o GROUP BY 1
)
SELECT d,
       rev,
       AVG(rev) OVER (
         ORDER BY d
         ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
         EXCLUDE CURRENT ROW
       ) AS neighbor_avg_excl_self
FROM daily
ORDER BY d
LIMIT 120;
```
Why
- EXCLUDE CURRENT ROW removes the self-value from the frame; useful to compare against neighbors only

Pitfalls
- Default frames differ across engines; be explicit with ROWS/RANGE and EXCLUDE as needed
