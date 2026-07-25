-- Day 08 solutions: scalar and inline subqueries
SET search_path TO training, public;

-- Exercise 1: largest single order for each country, using a correlated scalar subquery.
SELECT country,
       (
         SELECT MAX(o.total_amount)
         FROM orders o
         JOIN customers c2 ON c2.customer_id = o.customer_id
         WHERE c2.country = country_list.country
       ) AS largest_order
FROM (SELECT DISTINCT country FROM customers) AS country_list
ORDER BY largest_order DESC NULLS LAST, country;

-- Exercise 2: first order date for every customer. Customers without orders retain NULL.
SELECT c.customer_id,
       c.full_name,
       (
         SELECT MIN(o.order_date)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS first_order_date
FROM customers c
ORDER BY c.customer_id;
