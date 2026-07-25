-- Day 29 solutions: pattern matching
SET search_path TO training, public;

-- Exercise 1: customer1 followed by exactly two digits.
SELECT customer_id, full_name, email
FROM customers
WHERE email ~* '^customer1[0-9]{2}@example\.com$'
ORDER BY customer_id;

-- Exercise 2: require both "home" and "product" lexemes.
SELECT product_id, name, category
FROM products
WHERE to_tsvector('english', name || ' ' || category)
      @@ to_tsquery('english', 'home & product')
ORDER BY product_id;
