-- Day 4: LEFT/RIGHT/FULL OUTER JOINs and NULL handling
-- BEGINNER WORKFLOW — sql-04: Outer Joins
-- Guide: sql/postgres-60day/companion-guides/day04_outer_joins.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-04/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, products, payments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
-- Assumptions: Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
-- Pitfall: A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
-- Predict row grain and NULL/order behavior before executing each example.

-- LEFT JOIN: customers without orders
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY orders ASC, c.customer_id
LIMIT 25;

-- RIGHT JOIN: products that appear in orders (or not)
SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
FROM order_items oi
RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY sold_qty ASC, p.product_id
LIMIT 25;

-- FULL OUTER JOIN: payments vs orders.
-- A payment foreign key prevents an orphan payment in this dataset, while an
-- order may legitimately have no payment. Keep both keys visible when auditing.
SELECT o.order_id,
       p.payment_id,
       p.order_id AS payment_order_id,
       o.total_amount,
       p.amount AS payment_amount
FROM orders o
FULL OUTER JOIN payments p ON p.order_id = o.order_id
WHERE o.order_id IS NULL OR p.order_id IS NULL
ORDER BY COALESCE(o.order_id, p.order_id), p.payment_id; -- mismatches

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every customer with order count, including customers with zero orders.
--    Hint: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
--    Inputs: For sql-04 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `order_count`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 1, expected output: One row per customer; zero is visible. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
--    Verify: For sql-04 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-04 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
-- 2. [Query writing] Find products that have never appeared in an order item.
--    Hint: Left join and retain rows where the right-side primary key is NULL.
--    Inputs: For sql-04 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
--    Verify: For sql-04 Exercise 2, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `product_id`, `name`, and `category` values match those staged rows without unintended fanout or loss. Add one row for which `(oi.order_item_id IS NULL)` is true and one for which it is false; verify only the matching `product_id` value is returned.
--    Hint ladder, rung 1: For sql-04 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
-- 3. [Query writing] Compare monthly budgets and expenses by category with a full outer join.
--    Hint: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
--    Inputs: For sql-04 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, and `actual_amount`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 3, expected output: One row per category/month present in either source. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
--    Verify: For sql-04 Exercise 3, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, and `actual_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
--    Hint ladder, rung 1: For sql-04 Exercise 3, run `expense_months`, and `budget_months` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
--    Hint: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
--    Inputs: For sql-04 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `delivered_orders`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 4, expected output: One row per customer, including zero delivered orders. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
--    Verify: For sql-04 Exercise 4, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `delivered_orders` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `delivered_orders` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-04 Exercise 4, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
-- 5. [Debugging] Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
--    Hint: Count a non-nullable right-side key that becomes NULL for an unmatched row.
--    Inputs: For sql-04 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `order_count`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 5, expected output: One row per customer with correct zero counts. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
--    Verify: For sql-04 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-04 Exercise 5, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
-- 6. [Extension] Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
--    Hint: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
--    Inputs: For sql-04 Exercise 6, read from `products`, and `order_items`. Build the answer toward `matched_products`, `unsold_products`, and `orphan_item_product_ids`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-04 Exercise 6, expected output: One summary row with three mutually interpretable counts. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
--    Verify: For sql-04 Exercise 6, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `matched_products`, `unsold_products`, and `orphan_item_product_ids` values match those staged rows without unintended fanout or loss. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.
--    Hint ladder, rung 1: For sql-04 Exercise 6, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.

ROLLBACK;
