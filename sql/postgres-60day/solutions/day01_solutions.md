# Day 01 solutions — SELECT, WHERE, ORDER BY, LIMIT/OFFSET

These answers align one-for-one with [day01_select_where_orderby.sql](../day01_select_where_orderby.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
- **Assumptions:** Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
- **Primary pitfall:** Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List the 20 newest orders with customer ID and total amount.

**Reasoning:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 20;
```

**Expected shape:** At most 20 rows; one row per order, newest first.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Find the 10 most expensive products created in the last 90 days.

**Reasoning:** Filter the timestamp directly, then sort by price and a stable product key.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT p.product_id,
       p.name,
       p.price,
       p.created_at
FROM products AS p
WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
ORDER BY p.price DESC, p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 product rows; every row is in the 90-day window.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Show customers from GB or DE created in the last year, newest first.

**Reasoning:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       c.country,
       c.created_at
FROM customers AS c
WHERE c.country IN ('GB', 'DE')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'
ORDER BY c.created_at DESC, c.customer_id;
```

**Expected shape:** Only GB/DE customers from the declared window.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.

**Reasoning:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_count,
       COUNT(*) FILTER (WHERE c.email IS NOT NULL) AS present_email_count,
       COUNT(*) AS customer_count
FROM customers AS c;
```

**Expected shape:** Exactly one summary row with counts whose sum equals all customers.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.

**Reasoning:** Define the business ranking first; use a unique final key for tied prices.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT p.product_id,
       p.name,
       p.price
FROM products AS p
ORDER BY p.price DESC, p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 rows, highest prices first, stable across repeated runs on unchanged data.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.

**Reasoning:** Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
WITH first_page AS (
  SELECT o.order_id,
         o.order_date
  FROM orders AS o
  ORDER BY o.order_date DESC, o.order_id DESC
  LIMIT 10
), cursor_row AS (
  SELECT fp.order_date,
         fp.order_id
  FROM first_page AS fp
  ORDER BY fp.order_date, fp.order_id
  LIMIT 1
)
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
CROSS JOIN cursor_row AS cursor
WHERE (o.order_date, o.order_id) < (cursor.order_date, cursor.order_id)
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 10;
```

**Expected shape:** Up to 10 rows strictly after the first page with no overlap.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
