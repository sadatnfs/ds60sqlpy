-- Day 05 - Solutions: CROSS and SELF JOINs
-- Assumes: orders, order_items, products, employees

/*
Exercise 1) For each customer, find the closest two orders in time.
Why: Use LAG/LEAD to compute gaps between consecutive orders per customer, then pick the two smallest gaps per customer.
Note: If a customer has fewer than 3 orders, there may be fewer than two gaps.
*/
WITH ordered AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS prev_dt,
         LEAD(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS next_dt
  FROM orders o
), gaps AS (
  SELECT customer_id,
         order_id,
         order_date,
         CASE WHEN prev_dt IS NOT NULL THEN EXTRACT(EPOCH FROM (order_date - prev_dt)) ELSE NULL END AS gap_from_prev,
         CASE WHEN next_dt IS NOT NULL THEN EXTRACT(EPOCH FROM (next_dt - order_date)) ELSE NULL END AS gap_to_next
  FROM ordered
), flattened AS (
  -- Flatten to one row per gap with direction label
  SELECT customer_id,
         order_id,
         'prev' AS gap_side,
         gap_from_prev AS gap_seconds
  FROM gaps WHERE gap_from_prev IS NOT NULL
  UNION ALL
  SELECT customer_id,
         order_id,
         'next' AS gap_side,
         gap_to_next AS gap_seconds
  FROM gaps WHERE gap_to_next IS NOT NULL
), ranked AS (
  SELECT customer_id,
         order_id,
         gap_side,
         gap_seconds,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY gap_seconds ASC, order_id ASC) AS rn
  FROM flattened
)
SELECT customer_id, order_id, gap_side, gap_seconds
FROM ranked
WHERE rn <= 2
ORDER BY customer_id, rn;

/*
Exercise 2) Generate all unique pairs of products within each category and count co-purchases.
Why: Self-join order_items on the same order to get co-purchased pairs; enforce p1<p2 to avoid duplicates and self-pairs.
*/
WITH lines AS (
  SELECT oi.order_id, oi.product_id, p.category
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
)
SELECT l1.category,
       l1.product_id AS product_id_a,
       l2.product_id AS product_id_b,
       COUNT(*) AS co_purchases
FROM lines l1
JOIN lines l2
  ON l1.order_id = l2.order_id
 AND l1.product_id < l2.product_id
GROUP BY l1.category, l1.product_id, l2.product_id
ORDER BY co_purchases DESC, l1.category
LIMIT 200;

/*
Exercise 3) Employee hierarchy: (employee, manager) and (manager, director) chains.
Why: Self-join employees to itself multiple times to climb hierarchy levels.
*/
SELECT e.employee_id AS employee_id,
       e.first_name || ' ' || e.last_name AS employee_name,
       m.employee_id AS manager_id,
       m.first_name || ' ' || m.last_name AS manager_name,
       d.employee_id AS director_id,
       d.first_name || ' ' || d.last_name AS director_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN employees d ON m.manager_id = d.employee_id
ORDER BY employee_id
LIMIT 200;

-- End of Day 05 solutions
