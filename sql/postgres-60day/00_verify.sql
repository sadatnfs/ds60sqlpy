-- 00_verify.sql
-- Fail-fast invariants for the deterministic PostgreSQL course dataset.
-- Run after 00_setup.sql. The DO block raises an exception if any invariant
-- fails; the final query provides a compact human-readable profile.

SET search_path TO training, public;

DO $course_invariants$
DECLARE
  expected_orders bigint;
  expected_items bigint;
  expected_payments bigint;
BEGIN
  SELECT SUM(4 + (customer_id % 13))
  INTO expected_orders
  FROM customers
  WHERE country <> 'BR';

  SELECT SUM(1 + (order_id % 5))
  INTO expected_items
  FROM orders;

  SELECT SUM(CASE WHEN order_id % 10 = 0 THEN 2 ELSE 1 END)
  INTO expected_payments
  FROM orders
  WHERE status <> 'placed';

  IF (SELECT COUNT(*) FROM customers) <> 500
     OR (SELECT COUNT(DISTINCT country) FROM customers) <> 8
     OR (SELECT COUNT(DISTINCT segment) FROM customers) <> 4 THEN
    RAISE EXCEPTION 'customer seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM products) <> 300
     OR (SELECT COUNT(DISTINCT category) FROM products) <> 6
     OR EXISTS (SELECT 1 FROM products WHERE cost > price) THEN
    RAISE EXCEPTION 'product seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM orders) <> expected_orders
     OR (SELECT COUNT(DISTINCT customer_id) FROM orders) <> 438
     OR (
       SELECT COUNT(*)
       FROM customers c
       WHERE NOT EXISTS (
         SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
       )
     ) <> 62
     OR (
       SELECT array_agg(country ORDER BY country)
       FROM (
         SELECT country
         FROM customers
         EXCEPT
         SELECT c.country
         FROM customers c
         JOIN orders o USING (customer_id)
       ) countries_without_orders
     ) <> ARRAY['BR']::text[]
     OR (SELECT COUNT(DISTINCT date_trunc('month', order_date)) FROM orders) < 36
     OR EXISTS (
       SELECT 1
       FROM orders o
       JOIN customers c USING (customer_id)
       WHERE o.order_date < c.created_at
     ) THEN
    RAISE EXCEPTION 'order seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM order_items) <> expected_items
     OR (SELECT COUNT(DISTINCT product_id) FROM order_items) <> 275
     OR (
       SELECT COUNT(*)
       FROM products p
       WHERE NOT EXISTS (
         SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id
       )
     ) <> 25
     OR EXISTS (
       SELECT 1
       FROM order_items oi
       JOIN orders o USING (order_id)
       JOIN products p USING (product_id)
       WHERE o.order_date < p.created_at
     )
     OR EXISTS (
       SELECT 1
       FROM orders o
       LEFT JOIN (
         SELECT
           order_id,
           round(SUM(unit_price * quantity * (1 - discount)), 2) AS calculated_total
         FROM order_items
         GROUP BY order_id
       ) totals USING (order_id)
       WHERE totals.order_id IS NULL
          OR o.total_amount <> totals.calculated_total
     ) THEN
    RAISE EXCEPTION 'order-item seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM events) <> 20000
     OR (SELECT COUNT(DISTINCT customer_id) FROM events) <> 500
     OR (SELECT COUNT(DISTINCT event_type) FROM events) <> 5
     OR (
       SELECT COUNT(*)
       FROM (
         SELECT DISTINCT customer_id FROM orders
         INTERSECT
         SELECT DISTINCT customer_id FROM events
       ) overlap
     ) <> 438 THEN
    RAISE EXCEPTION 'event seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM employees) <> 100
     OR (SELECT COUNT(*) FROM departments) <> 6
     OR (SELECT COUNT(DISTINCT department_id) FROM employees) <> 6
     OR (SELECT COUNT(*) FROM expenses) <> 10000
     OR (SELECT COUNT(*) FROM budgets) <> 125
     OR (SELECT COUNT(*) FROM promotions) <> 200
     OR (SELECT COUNT(DISTINCT product_id) FROM promotions) <> 200
     OR EXISTS (
       SELECT 1
       FROM promotions pr
       JOIN products p USING (product_id)
       WHERE pr.start_date < p.created_at::date
     )
     OR (SELECT COUNT(*) FROM xml_docs) <> 1000 THEN
    RAISE EXCEPTION 'supporting-table seed invariant failed';
  END IF;

  IF (SELECT COUNT(*) FROM payments) <> expected_payments
     OR EXISTS (SELECT 1 FROM payments WHERE payment_date > CURRENT_TIMESTAMP)
     OR EXISTS (
       SELECT 1
       FROM payments p
       JOIN orders o USING (order_id)
       WHERE p.payment_date < o.order_date
     )
     OR EXISTS (
       SELECT 1
       FROM orders o
       JOIN payments p USING (order_id)
       WHERE o.status = 'placed'
     )
     OR EXISTS (
       SELECT 1
       FROM orders o
       WHERE o.status <> 'placed'
         AND NOT EXISTS (
           SELECT 1 FROM payments p WHERE p.order_id = o.order_id
         )
     )
     OR NOT EXISTS (
       SELECT 1
       FROM payments
       GROUP BY order_id
       HAVING COUNT(*) > 1
     )
     OR EXISTS (
       SELECT 1
       FROM orders o
       JOIN (
         SELECT order_id, SUM(amount) AS paid
         FROM payments
         GROUP BY order_id
       ) p USING (order_id)
       WHERE p.paid > o.total_amount
     )
     OR NOT EXISTS (
       SELECT 1
       FROM orders o
       JOIN (
         SELECT order_id, SUM(amount) AS paid
         FROM payments
         GROUP BY order_id
       ) p USING (order_id)
       WHERE p.paid < o.total_amount
     ) THEN
    RAISE EXCEPTION 'payment seed invariant failed';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM order_items oi
    LEFT JOIN orders o USING (order_id)
    LEFT JOIN products p USING (product_id)
    WHERE o.order_id IS NULL OR p.product_id IS NULL
  ) THEN
    RAISE EXCEPTION 'foreign-key coverage invariant failed';
  END IF;
END
$course_invariants$;

SELECT 'customers' AS object_name,
       COUNT(*) AS row_count,
       COUNT(DISTINCT country) AS distinct_dimension_values
FROM customers
UNION ALL
SELECT 'orders', COUNT(*), COUNT(DISTINCT customer_id)
FROM orders
UNION ALL
SELECT 'order_items', COUNT(*), COUNT(DISTINCT product_id)
FROM order_items
UNION ALL
SELECT 'payments', COUNT(*), COUNT(DISTINCT method)
FROM payments
UNION ALL
SELECT 'events', COUNT(*), COUNT(DISTINCT customer_id)
FROM events
UNION ALL
SELECT 'employees', COUNT(*), COUNT(DISTINCT department_id)
FROM employees
UNION ALL
SELECT 'promotions', COUNT(*), COUNT(DISTINCT product_id)
FROM promotions
ORDER BY object_name;
