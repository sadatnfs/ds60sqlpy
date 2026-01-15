-- Day 14 - Solutions: Numeric Types, Casting, and Precision
-- Assumes: products(price text or numeric), order_items(unit_price numeric, quantity int, discount numeric)

/*
Exercise 1) Convert monetary text fields to numeric and validate sums.
Why: Use to_number for messy text (commas), fall back to CAST where clean; validate with simple aggregates.
*/
-- Example: suppose products.price_text stores values like '1,234.50'
-- SELECT SUM(to_number(price_text, '9,999,999.99')) AS total_price FROM products;

/*
If price is already numeric, demonstrate a safe coercion from text to numeric in a staging/CTE:
*/
WITH cleaned AS (
  SELECT p.product_id,
         CASE
           WHEN p.price ~ '^[0-9]+(\.[0-9]{1,2})?$' THEN CAST(p.price AS numeric)
           ELSE NULL
         END AS price_num
  FROM products p
)
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE price_num IS NULL) AS bad_rows,
       ROUND(SUM(price_num), 2) AS sum_price
FROM cleaned;

/*
Exercise 2) Compute margin percentages rounded to 1 decimal and sort.
Why: Use NULLIF to avoid divide-by-zero, casting to numeric with scale.
*/
SELECT p.product_id,
       p.name,
       ROUND( ((oi.unit_price - p.cost) / NULLIF(oi.unit_price, 0)) * 100.0 , 1) AS margin_pct
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, oi.unit_price, p.cost
ORDER BY margin_pct DESC NULLS LAST
LIMIT 200;

-- Portable alternatives:
-- Instead of FILTER, use SUM(CASE WHEN ... THEN 1 ELSE 0 END)
-- Instead of ::numeric, use CAST(... AS numeric)

-- End of Day 14 solutions
