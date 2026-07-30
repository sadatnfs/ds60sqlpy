# Day 18 solutions — LAG/LEAD and Intra-Row Comparisons

These answers align one-for-one with [day18_lag_lead.sql](../day18_lag_lead.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Primary pitfall:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Show each order with the previous order timestamp for that customer.

**Reasoning:** Partition by customer and order by timestamp plus ID.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       LAG(o.order_date) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
       ) AS previous_order_date
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order; first customer order has NULL previous timestamp.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Calculate days since each customer's previous order.

**Reasoning:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH sequenced AS (
  SELECT o.*,
         LAG(o.order_date) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
         ) AS previous_order_date
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date,
       previous_order_date,
       EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0 AS days_since_previous
FROM sequenced
ORDER BY customer_id, order_date, order_id;
```

**Expected shape:** One row per order with nullable interval/days.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Show each promotion with the next promotion start date for the same product.

**Reasoning:** Partition by product and define a stable chronological order.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT pr.promotion_id,
       pr.product_id,
       pr.start_date,
       LEAD(pr.start_date) OVER (
         PARTITION BY pr.product_id
         ORDER BY pr.start_date, pr.promotion_id
       ) AS next_promotion_start
FROM promotions AS pr
ORDER BY pr.product_id, pr.start_date, pr.promotion_id;
```

**Expected shape:** One row per promotion; last product promotion has NULL next date.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.

**Reasoning:** NULL means there is no prior observation; preserve that semantic state.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH sequenced AS (
  SELECT o.*,
         LAG(o.order_id) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
         ) AS previous_order_id
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date
FROM sequenced
WHERE previous_order_id IS NULL
ORDER BY customer_id;
```

**Expected shape:** One row per customer's first order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Compute month-over-month stored-revenue change after aggregating to month grain.

**Reasoning:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), compared AS (
  SELECT month_start,
         revenue,
         LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM monthly
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_revenue, 2) AS previous_revenue,
       ROUND(revenue - previous_revenue, 2) AS revenue_change
FROM compared
ORDER BY month_start;
```

**Expected shape:** One row per month with nullable first change.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Compare each product price with the next higher price in its category.

**Reasoning:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.

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
       LEAD(p.price) OVER (
         PARTITION BY p.category
         ORDER BY p.price, p.product_id
       ) AS next_price
FROM products AS p
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product with nullable next price.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
