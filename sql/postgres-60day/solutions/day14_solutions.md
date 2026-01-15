# Day 14 — Solutions (Numeric Types, Casting, and Precision)

We safely coerce text to numeric, validate aggregates, and compute percentage margins with proper rounding and divide-by-zero protection.

Setup
- Schema: training; tables: products(price or price_text, cost), order_items(unit_price, quantity, discount)
- Casting reminders: `::numeric` is shorthand for `CAST(... AS numeric)`; use explicit scales where appropriate (e.g., numeric(12,2))

Exercise 1 — Convert monetary text fields to numeric and validate
```sql
-- Example where prices may be stored as text with commas
WITH cleaned AS (
  SELECT p.product_id,
         -- Pattern guard: keep only well-formed decimals, else NULL
         CASE
           WHEN p.price ~ '^[0-9]+(\.[0-9]{1,2})?$' THEN p.price::numeric
           ELSE NULL
         END AS price_num
  FROM products p
)
SELECT COUNT(*)                                  AS total_rows,
       COUNT(*) FILTER (WHERE price_num IS NULL) AS bad_rows,
       ROUND(SUM(price_num), 2)                  AS sum_price
FROM cleaned;
```
Line-by-line
- Regex: Accepts integers or decimals with up to 2 fraction digits. Adapt pattern if your data allows more precision.
- CAST/::numeric: Coerces strings that match the pattern; off-pattern values become NULL, counted in `bad_rows`.
- ROUND at the very end for presentation; keep internal math at full precision.
Alternatives
- `to_number(text, '9,999,999.99')` handles commas and fixed formats (requires consistent formatting).
- For bulk, consider a permanent numeric column and a CHECK constraint to prevent invalid inserts.

Exercise 2 — Margin percentage per product, rounded to 1 decimal
```sql
SELECT p.product_id,
       p.name,
       ROUND( ((oi.unit_price - p.cost) / NULLIF(oi.unit_price, 0)) * 100.0 , 1) AS margin_pct
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, oi.unit_price, p.cost
ORDER BY margin_pct DESC NULLS LAST
LIMIT 200;
```
Explanation
- Numerator: (sell price - cost). If costs vary over time, join the appropriate cost table/version-by-date.
- Denominator: `NULLIF(oi.unit_price, 0)` prevents division by zero; returns NULL margin when unit_price is 0.
- Multiply by 100.0 (note the float literal) to ensure floating division before rounding to 1 decimal place.
Pitfalls
- Using integer division (e.g., both numerator/denominator INTEGER) yields truncated results; ensure at least one operand is numeric with scale.
- If cost can be NULL, wrap with COALESCE(cost,0) per business rules, or exclude rows where cost is unknown.

Portable notes
- Instead of FILTER, `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` for ANSI portability.
- Prefer numeric/decimal for money; avoid float for currency storage due to binary rounding. Use float only for intermediate rates if needed.
