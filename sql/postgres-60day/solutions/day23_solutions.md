# Day 23 solutions — Common Table Expressions (CTEs) Introduction

These answers align one-for-one with [day23_ctes_intro.sql](../day23_ctes_intro.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
- **Assumptions:** Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
- **Primary pitfall:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Build order-level net value in one CTE and summarize it by customer in the outer query.

**Reasoning:** Name the one-row-per-order grain before changing to customer grain.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
)
SELECT ov.customer_id,
       COUNT(*) AS order_count,
       ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM order_values AS ov
GROUP BY ov.customer_id
ORDER BY net_revenue DESC, ov.customer_id;
```

**Expected shape:** One row per ordering customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Use one category-revenue CTE twice to return the highest category and total revenue.

**Reasoning:** A named aggregate can support multiple scalar reads without repeating the business formula.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
WITH category_revenue AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items AS oi
  JOIN products AS p
    ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT (
         SELECT cr.category
         FROM category_revenue AS cr
         ORDER BY cr.revenue DESC, cr.category
         LIMIT 1
       ) AS top_category,
       ROUND((SELECT SUM(cr.revenue) FROM category_revenue AS cr), 2) AS all_revenue;
```

**Expected shape:** One summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Create staged payment reconciliation CTEs at order grain.

**Reasoning:** Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH paid AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_amount
  FROM payments AS p
  GROUP BY p.order_id
), reconciled AS (
  SELECT o.order_id,
         o.total_amount,
         COALESCE(paid.paid_amount, 0) AS paid_amount
  FROM orders AS o
  LEFT JOIN paid
    ON paid.order_id = o.order_id
)
SELECT order_id,
       ROUND(total_amount, 2) AS order_total,
       ROUND(paid_amount, 2) AS paid_amount,
       ROUND(total_amount - paid_amount, 2) AS unpaid_balance
FROM reconciled
ORDER BY ABS(total_amount - paid_amount) DESC, order_id;
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.

**Reasoning:** Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH materialized_orders AS MATERIALIZED (
  SELECT o.order_id
  FROM orders AS o
  WHERE o.status = 'delivered'
), inline_orders AS NOT MATERIALIZED (
  SELECT o.order_id
  FROM orders AS o
  WHERE o.status = 'delivered'
)
SELECT 'materialized' AS variant, COUNT(*) AS row_count
FROM materialized_orders
UNION ALL
SELECT 'not_materialized' AS variant, COUNT(*) AS row_count
FROM inline_orders
ORDER BY variant;
```

**Expected shape:** Two count rows with equal values.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.

**Reasoning:** Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), customer_revenue AS (
  SELECT ov.customer_id,
         SUM(ov.order_value) AS customer_revenue
  FROM order_values AS ov
  GROUP BY ov.customer_id
)
SELECT c.country,
       ROUND(SUM(cr.customer_revenue), 2) AS country_revenue
FROM customer_revenue AS cr
JOIN customers AS c
  ON c.customer_id = cr.customer_id
GROUP BY c.country
ORDER BY country_revenue DESC, c.country;
```

**Expected shape:** One row per country.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.

**Reasoning:** The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
- `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_6;
WITH candidates AS (
  SELECT p.product_id
  FROM products AS p
  ORDER BY p.product_id
  LIMIT 3
), updated AS (
  UPDATE products AS p
  SET price = ROUND(p.price * 1.01, 2)
  WHERE p.product_id IN (SELECT c.product_id FROM candidates AS c)
  RETURNING p.product_id, p.price
)
SELECT COUNT(*) AS updated_rows,
       MIN(product_id) AS first_updated_product,
       MAX(product_id) AS last_updated_product
FROM updated;
ROLLBACK TO SAVEPOINT exercise_6;
```

**Expected shape:** One summary row for a bounded three-product update.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
