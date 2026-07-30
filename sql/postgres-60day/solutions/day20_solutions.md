# Day 20 solutions — FIRST_VALUE, LAST_VALUE, NTH_VALUE

These answers align one-for-one with [day20_first_last_value.sql](../day20_first_last_value.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Primary pitfall:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Show every order with the customer's first and last order timestamps.

**Reasoning:** Use one full-partition frame from unbounded preceding through unbounded following.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       FIRST_VALUE(o.order_date) OVER customer_orders AS first_order_date,
       LAST_VALUE(o.order_date) OVER customer_orders AS last_order_date
FROM orders AS o
WINDOW customer_orders AS (
  PARTITION BY o.customer_id
  ORDER BY o.order_date, o.order_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order with constant first/last values per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Show each product with the cheapest and most expensive price in its category.

**Reasoning:** Order by price and use a full frame; values tie without needing row identity.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.category,
       p.price,
       FIRST_VALUE(p.price) OVER category_prices AS category_min_price,
       LAST_VALUE(p.price) OVER category_prices AS category_max_price
FROM products AS p
WINDOW category_prices AS (
  PARTITION BY p.category
  ORDER BY p.price, p.product_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Compare every payment with the first and last payment amount for its order.

**Reasoning:** Partition by order, order by timestamp/payment ID, and keep the full frame.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.payment_id,
       p.order_id,
       p.payment_date,
       p.amount,
       FIRST_VALUE(p.amount) OVER payment_sequence AS first_payment_amount,
       LAST_VALUE(p.amount) OVER payment_sequence AS last_payment_amount
FROM payments AS p
WINDOW payment_sequence AS (
  PARTITION BY p.order_id
  ORDER BY p.payment_date, p.payment_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.order_id, p.payment_date, p.payment_id;
```

**Expected shape:** One row per payment.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.

**Reasoning:** The default ends at the current row; explicit following reaches the true last row.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT value,
       LAST_VALUE(value) OVER (ORDER BY value) AS default_last_value,
       LAST_VALUE(value) OVER (
         ORDER BY value
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS partition_last_value
FROM (VALUES (10), (20), (30)) AS sample(value)
ORDER BY value;
```

**Expected shape:** Three rows showing default current value and full-frame 30.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Return one first and one last order per customer without using window output as an accidental duplicate report.

**Reasoning:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH annotated AS (
  SELECT o.customer_id,
         FIRST_VALUE(o.order_id) OVER customer_orders AS first_order_id,
         LAST_VALUE(o.order_id) OVER customer_orders AS last_order_id
  FROM orders AS o
  WINDOW customer_orders AS (
    PARTITION BY o.customer_id
    ORDER BY o.order_date, o.order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
SELECT DISTINCT customer_id,
       first_order_id,
       last_order_id
FROM annotated
ORDER BY customer_id;
```

**Expected shape:** One row per customer with orders.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.

**Reasoning:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `DISTINCT ON`: keeps the first row in each declared group, so its matching leading sort keys determine which row wins.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT DISTINCT ON (o.customer_id)
       o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount
FROM orders AS o
ORDER BY o.customer_id, o.order_date DESC, o.order_id DESC;
```

**Expected shape:** At most one latest order per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
