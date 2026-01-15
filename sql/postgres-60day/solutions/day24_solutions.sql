-- Day 24 - Solutions: Recursive CTEs (Hierarchies)
-- Assumes: employees(id, manager_id, first_name, last_name), products(product_id, category, parent_category) example

/*
Exercise 1) From a given department head, list all reports with depth and path.
Why: WITH RECURSIVE; accumulate path to prevent cycles and provide breadcrumbs.
*/
WITH RECURSIVE tree AS (
  SELECT e.id, e.manager_id, 0 AS depth,
         (ARRAY[e.id]) AS path
  FROM employees e
  WHERE e.id = 1  -- parameterize for a given root
  UNION ALL
  SELECT c.id, c.manager_id, t.depth + 1,
         t.path || c.id
  FROM employees c
  JOIN tree t ON c.manager_id = t.id
  WHERE NOT c.id = ANY(t.path)
)
SELECT id, manager_id, depth, path
FROM tree
ORDER BY depth, id
LIMIT 500;

/*
Exercise 2) From a product, walk up to root category and return full lineage.
Assume products(category) with a categories(parent_category) tree.
*/
WITH RECURSIVE up AS (
  SELECT p.product_id, c.category, c.parent_category
  FROM products p
  JOIN categories c ON c.category = p.category
  WHERE p.product_id = 42
  UNION ALL
  SELECT up.product_id, c.category, c.parent_category
  FROM up
  JOIN categories c ON c.category = up.parent_category
)
SELECT * FROM up;

/*
Exercise 3) Count number of reports at each depth across the org.
*/
WITH RECURSIVE org AS (
  SELECT e.id, e.manager_id, 0 AS depth
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT c.id, c.manager_id, org.depth + 1
  FROM employees c JOIN org ON c.manager_id = org.id
)
SELECT depth, COUNT(*) AS nodes
FROM org
GROUP BY depth
ORDER BY depth;
