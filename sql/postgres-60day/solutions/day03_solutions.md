# Day 03 — Solutions (INNER JOINs and Predicate Placement)

Detailed explanations of each join pattern and how to avoid fanout.

Setup
- Facts: orders, order_items, payments; Dimensions: customers, products
- Heuristic: Pre‑aggregate facts before joining two 1:N relationships to avoid row multiplication

Exercise 1 — Revenue by customer country for last 90 days
```sql
WITH order_revenue AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_date >= now() - interval '90 days'
  GROUP BY o.order_id, o.customer_id
)
SELECT c.country,
       ROUND(SUM(orv.order_revenue),2) AS revenue_90d
FROM order_revenue orv
JOIN customers c ON c.customer_id = orv.customer_id
GROUP BY c.country
ORDER BY revenue_90d DESC;
```
Why it works
- Aggregate line items to the order level first. Then the join to customers is 1:1, so no duplication.
- Time filter is applied in the CTE to reduce rows early.

Exercise 2 — Gross margin per category
```sql
SELECT p.category,
       ROUND(SUM( (oi.unit_price - p.cost) * oi.quantity * (1 - oi.discount) ), 2) AS gross_margin
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY gross_margin DESC;
```
Explanation
- Margin formula: (sell_price - unit_cost) × effective_quantity. Discounts reduce revenue, so include (1 - discount).
- Group by category to aggregate across SKUs.
Pitfall
- If cost is NULL for some products, (price - NULL) yields NULL; wrap cost with COALESCE(cost,0) if appropriate.

Exercise 3 — Fixing fanout with pre‑aggregation
```sql
WITH order_totals AS (
  SELECT o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id
),
payments_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_amount
  FROM payments p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(o.order_revenue,2) AS order_revenue,
       ROUND(pt.paid_amount,2) AS paid_amount,
       ROUND(o.order_revenue - COALESCE(pt.paid_amount,0),2) AS balance
FROM order_totals o
LEFT JOIN payments_totals pt ON pt.order_id = o.order_id
ORDER BY o.order_id
LIMIT 100;
```
Line‑by‑line
- order_totals: 1 row per order with revenue. payments_totals: 1 row per order with total paid.
- LEFT JOIN: Preserve orders with no payments (paid_amount becomes NULL). COALESCE to treat NULL as 0 for balance.
- This pattern avoids N×M explosion from joining two raw 1:N tables.
