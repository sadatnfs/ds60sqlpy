-- Day 02 solutions: aggregates, GROUP BY, and HAVING
SET search_path TO training, public;

-- Exercise 1: payment totals by method, limited with HAVING.
SELECT method,
       COUNT(*) AS payment_rows,
       ROUND(SUM(amount), 2) AS total_payments
FROM payments
GROUP BY method
HAVING SUM(amount) > 1000000
ORDER BY total_payments DESC, method;

-- Exercise 2: average customer age, expressed in days, by country.
SELECT country,
       COUNT(*) AS customers,
       ROUND(
         AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at)) / 86400)::numeric,
         1
       ) AS avg_customer_age_days
FROM customers
GROUP BY country
ORDER BY avg_customer_age_days DESC, country;

-- Exercise 3: the five categories with the greatest gross margin.
-- The prompt defines gross margin as (catalog price - cost) * quantity.
SELECT p.category,
       ROUND(SUM((p.price - p.cost) * oi.quantity), 2) AS gross_margin
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY gross_margin DESC, p.category
LIMIT 5;
