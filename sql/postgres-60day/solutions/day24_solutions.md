# Day 24 — Solutions (Recursive CTEs: Trees, Paths, and Tallies)

We use WITH RECURSIVE to traverse hierarchies, build paths, compute depths, and do running rollups. Recursive CTEs elegantly replace loops for tree problems inside SQL.

Setup
- Example hierarchy: categories(id, parent_id, name) or employees(employee_id, manager_id, name)
- Syntax: WITH RECURSIVE t AS (base UNION ALL step) SELECT ... FROM t

Exercise 1 — Walk an org chart top-down (root → leaves)
```sql
WITH RECURSIVE org AS (
  -- base: top-level managers (no manager)
  SELECT e.employee_id,
         e.manager_id,
         e.first_name || ' ' || e.last_name AS name,
         0 AS depth,
         (e.first_name || ' ' || e.last_name)::text AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  -- step: attach direct reports
  SELECT c.employee_id,
         c.manager_id,
         c.first_name || ' ' || c.last_name AS name,
         p.depth + 1 AS depth,
         (p.path || ' > ' || (c.first_name || ' ' || c.last_name)) AS path
  FROM employees c
  JOIN org p ON p.employee_id = c.manager_id
)
SELECT employee_id, manager_id, depth, name, path
FROM org
ORDER BY path
LIMIT 200;
```
Explanation
- Base picks roots (manager_id NULL). Step joins children to parents and increments depth. Path concatenates names.
- ORDER BY path yields preorder traversal; for large trees add a guard to prevent cycles.

Exercise 2 — Find all ancestors of a node (bottom-up)
```sql
WITH RECURSIVE ancestors AS (
  SELECT e.employee_id, e.manager_id, 0 AS depth
  FROM employees e
  WHERE e.employee_id = :target_id
  UNION ALL
  SELECT p.employee_id, p.manager_id, depth + 1
  FROM employees p
  JOIN ancestors a ON a.manager_id = p.employee_id
)
SELECT *
FROM ancestors
ORDER BY depth;
```
Why
- Start at the target and repeatedly join to its manager. depth grows upward.

Exercise 3 — Category rollups from leaves to root
```sql
WITH RECURSIVE tree AS (
  SELECT c.category_id, c.parent_id
  FROM categories c
  UNION ALL
  SELECT c.category_id, c.parent_id
  FROM categories c
  JOIN tree t ON c.parent_id = t.category_id
), leaf_sales AS (
  SELECT p.category_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category_id
), ascend AS (
  -- map each node to all of its ancestors (including self)
  WITH RECURSIVE up AS (
    SELECT c.category_id AS node, c.category_id AS anc
    FROM categories c
    UNION ALL
    SELECT u.node, c.parent_id AS anc
    FROM up u JOIN categories c ON c.category_id = u.anc
    WHERE c.parent_id IS NOT NULL
  )
  SELECT node AS category_id, anc
  FROM up
)
SELECT a.anc AS rollup_category,
       ROUND(SUM(COALESCE(ls.revenue,0)),2) AS rollup_revenue
FROM ascend a
LEFT JOIN leaf_sales ls ON ls.category_id = a.category_id
GROUP BY a.anc
ORDER BY rollup_revenue DESC
LIMIT 200;
```
Notes
- ascend relates each node to all ancestors. Summing leaf revenues by ancestor yields rollups.
- For large graphs, consider indexing and cycle guards.

Pitfalls
- Infinite recursion on cycles: add a visited list or a max depth constraint.
- Performance: Recursive CTEs can be expensive; test with EXPLAIN and add indexes on join keys.
