# Day 21 solutions — Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST

These answers align one-for-one with [day21_distribution_functions.sql](../day21_distribution_functions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
- **Assumptions:** `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
- **Primary pitfall:** A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Assign customers to four stored-spend buckets.

**Reasoning:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH customer_spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS stored_spend
  FROM orders AS o
  GROUP BY o.customer_id
)
SELECT customer_id,
       ROUND(stored_spend, 2) AS stored_spend,
       NTILE(4) OVER (
         ORDER BY stored_spend DESC, customer_id
       ) AS spend_quartile
FROM customer_spend
ORDER BY spend_quartile, stored_spend DESC, customer_id;
```

**Expected shape:** One row per ordering customer with bucket 1–4.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Calculate salary percent rank within each department.

**Reasoning:** Partition by department and rank on salary alone so tied salaries share rank.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.department_id,
       e.salary,
       PERCENT_RANK() OVER (
         PARTITION BY e.department_id ORDER BY e.salary
       ) AS salary_percent_rank
FROM employees AS e
ORDER BY e.department_id, e.salary, e.employee_id;
```

**Expected shape:** One row per employee with values from 0 to 1.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Calculate cumulative distribution of product price within category.

**Reasoning:** Partition by category and order on price.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.category,
       p.price,
       CUME_DIST() OVER (
         PARTITION BY p.category ORDER BY p.price
       ) AS price_cume_dist
FROM products AS p
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product with cume_dist in (0, 1].

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.

**Reasoning:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT row_id,
       value,
       PERCENT_RANK() OVER (ORDER BY value) AS percent_rank_value,
       CUME_DIST() OVER (ORDER BY value) AS cume_dist_value
FROM (VALUES (1, 10), (2, 10), (3, 20)) AS sample(row_id, value)
ORDER BY row_id;
```

**Expected shape:** Three rows making tie behavior visible.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Audit the row count in each customer spend decile rather than assuming exact equality.

**Reasoning:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS total_spend
  FROM orders AS o
  GROUP BY o.customer_id
), bucketed AS (
  SELECT customer_id,
         NTILE(10) OVER (
           ORDER BY total_spend DESC, customer_id
         ) AS decile
  FROM spend
)
SELECT decile,
       COUNT(*) AS customers
FROM bucketed
GROUP BY decile
ORDER BY decile;
```

**Expected shape:** Up to 10 bucket rows with counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Return customers in the top stored-spend decile with their spend and population share.

**Reasoning:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS total_spend
  FROM orders AS o
  GROUP BY o.customer_id
), bucketed AS (
  SELECT customer_id,
         total_spend,
         NTILE(10) OVER (
           ORDER BY total_spend DESC, customer_id
         ) AS decile,
         COUNT(*) OVER () AS population
  FROM spend
)
SELECT customer_id,
       ROUND(total_spend, 2) AS total_spend,
       decile,
       population
FROM bucketed
WHERE decile = 1
ORDER BY total_spend DESC, customer_id;
```

**Expected shape:** Customers in decile 1.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
