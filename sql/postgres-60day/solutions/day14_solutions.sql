-- Day 14 solutions: numeric functions and casts
SET search_path TO training, public;

-- Exercise 1: floor/ceiling values and $25 price buckets.
SELECT product_id,
       name,
       price,
       FLOOR(price) AS price_floor,
       CEIL(price) AS price_ceiling,
       FLOOR(price / 25) * 25 AS bucket_start,
       FLOOR(price / 25) * 25 + 25 AS bucket_end
FROM products
ORDER BY price, product_id;

-- Exercise 2: JSONB scalar extraction yields text; the explicit cast documents it.
SELECT (attributes->>'channel')::text AS channel,
       COUNT(*) AS customers
FROM customers
GROUP BY (attributes->>'channel')::text
ORDER BY customers DESC, channel;
