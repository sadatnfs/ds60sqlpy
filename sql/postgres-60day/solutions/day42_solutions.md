# Day 42 Solutions — Data Quality and Validation

The goal is to turn scattered checks into one auditable report, then isolate
bad email values. Run the canonical file at
[`day42_solutions.sql`](day42_solutions.sql).

## Exercise 1 — Core-table validation report

Each row is a named check and the number of failing records or duplicate groups.
On the deterministic course seed, every count should be zero.

```sql
SET search_path TO training, public;

SELECT 'customers.null_email' AS check_name,
       COUNT(*) AS failing_rows
FROM customers
WHERE email IS NULL
UNION ALL
SELECT 'customers.duplicate_normalized_email',
       COUNT(*)
FROM (
  SELECT lower(trim(email))
  FROM customers
  GROUP BY lower(trim(email))
  HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'orders.negative_total', COUNT(*)
FROM orders
WHERE total_amount < 0
UNION ALL
SELECT 'orders.orphan_customer', COUNT(*)
FROM orders o
LEFT JOIN customers c USING (customer_id)
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'order_items.orphan_order_or_product', COUNT(*)
FROM order_items oi
LEFT JOIN orders o USING (order_id)
LEFT JOIN products p USING (product_id)
WHERE o.order_id IS NULL OR p.product_id IS NULL
UNION ALL
SELECT 'order_items.invalid_quantity_or_discount', COUNT(*)
FROM order_items
WHERE quantity <= 0 OR discount NOT BETWEEN 0 AND 1
UNION ALL
SELECT 'payments.negative_or_orphan', COUNT(*)
FROM payments p
LEFT JOIN orders o USING (order_id)
WHERE p.amount < 0 OR o.order_id IS NULL
ORDER BY check_name;
```

Expected shape: seven rows with `check_name` and `failing_rows`. A nonzero
result is evidence to investigate, not permission to delete data automatically.

## Exercise 2 — Invalid email patterns

```sql
SET search_path TO training, public;

SELECT customer_id, email
FROM customers
WHERE email IS NULL
   OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
ORDER BY customer_id;
```

The seed should return zero rows. The regex is a practical course check, not a
complete implementation of every valid RFC email address.

## Reasoning, safety, and pitfalls

- Normalize with `lower(trim(email))` before duplicate detection.
- Anti-join checks remain valuable even with foreign keys: imports or disabled
  constraints can violate assumptions.
- `COUNT(*)` over the duplicate subquery counts duplicate groups, not all rows
  participating in those groups. Label it accordingly.
- Keep validation queries read-only. Fix source data or use a reviewed
  remediation transaction after examining the exact failures.

## Exercise 3 — Explain CHECK and NULL

SQL CHECK rejects FALSE but accepts UNKNOWN. `NOT NULL` is therefore a separate
schema rule when absence is invalid; the catalog query confirms both course
amount columns declare it.

## Exercise 4 — Reconcile order totals

Line values aggregate to one row per order before comparison. The one-cent
tolerance is an explicit currency rule and failing order IDs remain visible.

## Exercise 5 — Retain duplicate evidence

The normalized email is the grouping key, but `array_agg` preserves raw variants
needed to diagnose case/whitespace differences.

## Exercise 6 — Detect inclusive range overlap

Promotion pairs share a product, are compared once, and overlap when each start
is no later than the other end. Touching inclusive endpoints therefore count.
