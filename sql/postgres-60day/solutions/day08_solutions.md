# Day 08 solutions — Scalar and Inline Subqueries

These answers align one-for-one with [day08_scalar_inline_subqueries.sql](../day08_scalar_inline_subqueries.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
- **Assumptions:** A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
- **Primary pitfall:** Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Return orders whose total exceeds the overall average order total.

**Reasoning:** The aggregate subquery is guaranteed to return exactly one value.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount
FROM orders AS o
WHERE o.total_amount > (
  SELECT AVG(all_orders.total_amount)
  FROM orders AS all_orders
)
ORDER BY o.total_amount DESC, o.order_id;
```

**Expected shape:** Order rows above the global average.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Add the total customer count as a scalar column beside each country-level customer count.

**Reasoning:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.country,
       COUNT(*) AS country_customers,
       (SELECT COUNT(*) FROM customers) AS all_customers
FROM customers AS c
GROUP BY c.country
ORDER BY country_customers DESC, c.country;
```

**Expected shape:** One row per country with a common global total.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Show each customer with their latest order timestamp using a scalar correlated subquery.

**Reasoning:** Use `MAX` to guarantee one result and let customers without orders receive NULL.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       (
         SELECT MAX(o.order_date)
         FROM orders AS o
         WHERE o.customer_id = c.customer_id
       ) AS latest_order_date
FROM customers AS c
ORDER BY latest_order_date DESC NULLS LAST, c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Demonstrate that a scalar subquery with no matching rows returns NULL.

**Reasoning:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.

```sql
SELECT (
         SELECT p.price
         FROM products AS p
         WHERE p.product_id = -1
       ) IS NULL AS no_row_becomes_null;
```

**Expected shape:** One row whose boolean result is true.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.

**Reasoning:** Choose the business reduction explicitly; this answer uses maximum price.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.category,
       MAX(p.price) AS category_max_price,
       (SELECT MAX(all_products.price) FROM products AS all_products) AS global_max_price
FROM products AS p
GROUP BY p.category
ORDER BY p.category;
```

**Expected shape:** One row per category with a scalar global maximum for comparison.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.

**Reasoning:** Compute the global total once, then cross join the guaranteed one-row relation.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH global AS (
  SELECT COUNT(*)::numeric AS customer_count
  FROM customers
)
SELECT c.country,
       COUNT(*) AS country_customers,
       ROUND(COUNT(*) / NULLIF(global.customer_count, 0), 4) AS customer_share
FROM customers AS c
CROSS JOIN global
GROUP BY c.country, global.customer_count
ORDER BY customer_share DESC, c.country;
```

**Expected shape:** One row per country with country share.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
