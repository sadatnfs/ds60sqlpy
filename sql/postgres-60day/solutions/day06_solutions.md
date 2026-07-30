# Day 06 solutions — Set Operations: UNION, INTERSECT, EXCEPT

These answers align one-for-one with [day06_set_operations.sql](../day06_set_operations.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Primary pitfall:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Return customer IDs that have either an order or a support event.

**Reasoning:** `UNION` expresses set membership and removes duplicates across both sources.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.customer_id
FROM orders AS o
UNION
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;
```

**Expected shape:** One distinct customer ID per qualifying customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Return customer IDs that have both an order and a support event.

**Reasoning:** `INTERSECT` keeps keys present in both compatible sets.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.customer_id
FROM orders AS o
INTERSECT
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;
```

**Expected shape:** One distinct customer ID in both sets.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Return customers who have no orders.

**Reasoning:** `EXCEPT` subtracts the order-customer set from all customers.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id
FROM customers AS c
EXCEPT
SELECT o.customer_id
FROM orders AS o
ORDER BY customer_id;
```

**Expected shape:** One row per customer absent from orders.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.

**Reasoning:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH combined_all AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION ALL
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
), combined_distinct AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
)
SELECT 'UNION ALL' AS operation,
       COUNT(*) AS row_count
FROM combined_all
UNION ALL
SELECT 'UNION' AS operation,
       COUNT(*) AS row_count
FROM combined_distinct
ORDER BY operation;
```

**Expected shape:** Two labeled summary rows showing all-count >= distinct-count.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.

**Reasoning:** Each branch below returns one text label and one numeric amount at the same report grain.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT 'order_revenue'::text AS measure,
       SUM(o.total_amount)::numeric AS amount
FROM orders AS o
UNION ALL
SELECT 'expense'::text AS measure,
       SUM(e.amount)::numeric AS amount
FROM expenses AS e
ORDER BY measure;
```

**Expected shape:** Rows identify revenue and expense measures with compatible types.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Return the symmetric difference between customers with orders and customers with support events.

**Reasoning:** Subtract each set from the other, then union the two differences.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH ordering_customers AS (
  SELECT DISTINCT o.customer_id
  FROM orders AS o
), support_customers AS (
  SELECT DISTINCT e.customer_id
  FROM events AS e
  WHERE e.event_type = 'support'
), only_orders AS (
  SELECT customer_id FROM ordering_customers
  EXCEPT
  SELECT customer_id FROM support_customers
), only_support AS (
  SELECT customer_id FROM support_customers
  EXCEPT
  SELECT customer_id FROM ordering_customers
)
SELECT customer_id, 'orders_only' AS source
FROM only_orders
UNION ALL
SELECT customer_id, 'support_only' AS source
FROM only_support
ORDER BY customer_id, source;
```

**Expected shape:** Customers present in exactly one of the two source sets.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
