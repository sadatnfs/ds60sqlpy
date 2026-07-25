-- Day 12 solutions: string functions
SET search_path TO training, public;

-- Exercise 1: normalize country codes.
SELECT customer_id,
       country AS raw_country,
       UPPER(TRIM(country)) AS normalized_country
FROM customers
ORDER BY customer_id;

-- Exercise 2: build the requested product label.
SELECT product_id,
       category || ' - ' || name || ' ($'
         || to_char(price, 'FM999999990.00') || ')' AS full_label
FROM products
ORDER BY category, name;
