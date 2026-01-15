# Day 40 — Solutions (Advanced Analytic Functions)

We go deeper into analytics with hypothetical‑set aggregates, ordered‑set functions, ranking nuances, and advanced window framing patterns that solve real reporting needs. We emphasize correct semantics and performance considerations.

Setup
- Tables: orders(order_id, customer_id, order_date, total_amount), order_items(...), customers(...)
- Glossary
  - Ordered‑set aggregates: percentile_cont/percentile_disc ... WITHIN GROUP (ORDER BY ...)
  - Hypothetical‑set aggregates: rank/percent_rank/cume_dist/dense_rank for a hypothetical row WITHIN GROUP (ORDER BY ...)
  - Window frames: UNBOUNDED, PRECEDING/FOLLOWING, EXCLUDE

Exercise 1 — Hypothetical rank of a target order total
```sql
-- Where would a hypothetical value rank within the distribution of order totals in the last 90 days?
WITH span AS (
  SELECT o.total_amount
  FROM orders o
  WHERE o.order_date >= current_date - interval '90 days'
)
SELECT rank(42.00)          WITHIN GROUP (ORDER BY total_amount) AS hyp_rank,
       percent_rank(42.00)  WITHIN GROUP (ORDER BY total_amount) AS hyp_percent_rank,
       cume_dist(42.00)     WITHIN GROUP (ORDER BY total_amount) AS hyp_cume
FROM span;
```
Explanation
- Hypothetical‑set aggregates treat the provided value as if it were inserted and return its rank or distribution location.
- Use cases: threshold setting, pricing tiers, SLA cutoffs.

Exercise 2 — Percentiles by segment (ordered‑set aggregates)
```sql
SELECT COALESCE(c.segment,'standard') AS segment,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY o.total_amount) AS p50,
       percentile_cont(0.90) WITHIN GROUP (ORDER BY o.total_amount) AS p90,
       COUNT(*) AS n
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY COALESCE(c.segment,'standard')
ORDER BY segment;
```
Notes
- Ordered‑set aggregates compute per‑group quantiles directly; this is typically faster and clearer than self‑joins or window emulation.

Exercise 3 — Top‑K per partition with stable tie‑breaking
```sql
WITH line_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.quantity*oi.unit_price*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
), ranked AS (
  SELECT category, product_id, revenue,
         ROW_NUMBER()  OVER (PARTITION BY category ORDER BY revenue DESC, product_id ASC)  AS rn,
         RANK()        OVER (PARTITION BY category ORDER BY revenue DESC)                  AS rnk,
         DENSE_RANK()  OVER (PARTITION BY category ORDER BY revenue DESC)                  AS drnk
  FROM line_rev
)
SELECT category, product_id, revenue, rn, rnk, drnk
FROM ranked
WHERE rn <= 3  -- guarantees exactly 3 even with ties (secondary key breaks ties)
ORDER BY category, rn;
```
Why
- ROW_NUMBER gives deterministic top‑K; RANK/DENSE_RANK show tie behavior differences for audit and display.

Exercise 4 — Neighbor‑only comparisons with EXCLUDE
```sql
-- Compare a day’s revenue to the average of its 3‑day neighbors excluding itself
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS rev
  FROM orders o
  GROUP BY 1
)
SELECT d,
       rev,
       ROUND(
         AVG(rev) OVER (
           ORDER BY d
           ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
           EXCLUDE CURRENT ROW
         )
       ,2) AS neighbor_avg
FROM daily
ORDER BY d DESC
LIMIT 60;
```
Notes
- EXCLUDE CURRENT ROW removes the self‑value; think “context but not me.” Useful in outlier detection and smoothing.

Exercise 5 — Within‑group shares and complements
```sql
-- Product share within category and its complement ("others") per category
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.quantity*oi.unit_price*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id=oi.product_id
  GROUP BY p.category, oi.product_id
)
SELECT category,
       product_id,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category),0), 4) AS share,
       ROUND(1 - (revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category),0)), 4) AS others_share
FROM prod_rev
ORDER BY category, share DESC
LIMIT 200;
```
Reasoning
- Window denominator avoids extra joins; complements often used for “others” bucket in charts.

Exercise 6 — Caution around running quantiles
- Postgres ordered‑set aggregates are not window functions; a *running* median/quantile needs custom approaches (e.g., PL/pgSQL state, sorted arrays with percentile_disc across slices, or extensions).
- For fixed windows, compute subsets in a CTE and aggregate per window using joins or bucketing.

Performance and correctness tips
- Always include deterministic secondary keys in ORDER BY for rank/row_number to ensure stable outputs.
- Use ROWS frames for exact window widths; RANGE expands to peers and may surprise.
- Avoid large per‑row hypothetical calls inside big scans; pre‑aggregate to reduce input size.
