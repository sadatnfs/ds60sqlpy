# Day 01 solutions — SELECT, WHERE, ORDER BY, LIMIT/OFFSET


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day01_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day01_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Projection, Predicate, Deterministic ordering. Its worked-model focus is:
Trace the first learner query in logical order: FROM training.customers produces candidate rows, WHERE country IN ('US', 'CA') filters them, ORDER BY createdat DESC, customerid DESC fixes their order, and LIMIT 10 keeps the first ten. Remove the customerid tie-breaker and explain why rows with equal timestamps no longer have a guaranteed relative order.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 1, expected output: At most 20 rows; one row per order, newest first. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-01 Exercise 1, assert the result has at most 20 rows, no duplicate `order_id`, and no adjacent pair out of `(order_date DESC, order_id DESC)` order. Check that each projected `customer_id`, `total_amount`, and `order_date` matches the same `orders.order_id` source row. Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.
- **Intermediate relation check:** For sql-01 Exercise 1, check `o.order_date DESC, o.order_id DESC` before applying the row cap.
- **Clause check:** For sql-01 Exercise 1, the solution actually uses `FROM`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, and `order_date` ordered by `o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`. Evaluate another form against the concrete expected result (At most 20 rows; one row per order, newest first) and the verification above.
- **Edge case:** Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 2, read from `products`. Build the answer toward `product_id`, `name`, `price`, and `created_at`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 2, expected output: At most 10 product rows; every row is in the 90-day window. The final columns are `product_id`, `name`, `price`, and `created_at`. The final order is `p.price DESC, p.product_id`.
- **Independent verification:** For sql-01 Exercise 2, assert no more than 10 rows, no duplicate `product_id`, and no adjacent pair that violates `p.price DESC, p.product_id`. Rejoin the returned keys to `products` to confirm `product_id`, `name`, `price`, and `created_at` came from the same source rows. Tie two rows on `p.price DESC` and give them different `p.product_id` values; verify `p.price DESC, p.product_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-01 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.price DESC, p.product_id` before applying the row cap.
- **Clause check:** For sql-01 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `name`, `price`, and `created_at` ordered by `p.price DESC, p.product_id`.
- **Alternative/trade-off:** For sql-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: Filter the timestamp directly, then sort by price and a stable product key. Evaluate another form against the concrete expected result (At most 10 product rows; every row is in the 90-day window) and the verification above.
- **Edge case:** Tie two rows on `p.price DESC` and give them different `p.product_id` values; verify `p.price DESC, p.product_id` chooses a stable first/last row.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 3, read from `customers`. Build the answer toward `customer_id`, `full_name`, `country`, and `created_at`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 3, expected output: Only GB/DE customers from the declared window. The final columns are `customer_id`, `full_name`, `country`, and `created_at`. The final order is `c.created_at DESC, c.customer_id`.
- **Independent verification:** For sql-01 Exercise 3, run an anti-check that counts rows where NOT ((c.country IN ('GB', 'DE') AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, `country`, and `created_at` against `customers`. Give two rows the same `c.created_at DESC` value and different `c.customer_id` values; verify `c.created_at DESC, c.customer_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `c.created_at DESC, c.customer_id` before applying the row cap.
- **Clause check:** For sql-01 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `full_name`, `country`, and `created_at` ordered by `c.created_at DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties. Evaluate another form against the concrete expected result (Only GB/DE customers from the declared window) and the verification above.
- **Edge case:** Give two rows the same `c.created_at DESC` value and different `c.customer_id` values; verify `c.created_at DESC, c.customer_id` produces the intended rank and display order.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 4, read from `customers`. Build the answer toward `missing_email_count`, `present_email_count`, and `customer_count`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 4, expected output: Exactly one summary row with counts whose sum equals all customers. The final columns are `missing_email_count`, `present_email_count`, and `customer_count`.
- **Independent verification:** For sql-01 Exercise 4, assert exactly one row. Independently run `SELECT COUNT(*) FROM customers`; verify `missing_email_count + present_email_count = customer_count` and that `customer_count` equals the independent count. Repeat with `NULL` in `email` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-01 Exercise 4, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-01 Exercise 4, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `missing_email_count`, `present_email_count`, and `customer_count`.
- **Alternative/trade-off:** For sql-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`. Evaluate another form against the concrete expected result (Exactly one summary row with counts whose sum equals all customers) and the verification above.
- **Edge case:** Repeat with `NULL` in `email` and state whether the row is kept, rejected, or classified.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 5, read from `products`. Build the answer toward `product_id`, `name`, and `price`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 5, expected output: At most 10 rows, highest prices first, stable across repeated runs on unchanged data. The final columns are `product_id`, `name`, and `price`. The final order is `p.price DESC, p.product_id`.
- **Independent verification:** For sql-01 Exercise 5, assert no more than 10 rows, no duplicate `product_id`, and no adjacent pair that violates `p.price DESC, p.product_id`. Rejoin the returned keys to `products` to confirm `product_id`, `name`, and `price` came from the same source rows. Give two rows the same `p.price DESC` value and different `p.product_id` values; verify `p.price DESC, p.product_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-01 Exercise 5, check `p.price DESC, p.product_id` before applying the row cap.
- **Clause check:** For sql-01 Exercise 5, the solution actually uses `FROM`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `name`, and `price` ordered by `p.price DESC, p.product_id`.
- **Alternative/trade-off:** For sql-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Define the business ranking first; use a unique final key for tied prices. Evaluate another form against the concrete expected result (At most 10 rows, highest prices first, stable across repeated runs on unchanged data) and the verification above.
- **Edge case:** Give two rows the same `p.price DESC` value and different `p.product_id` values; verify `p.price DESC, p.product_id` produces the intended rank and display order.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 6, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-01 Exercise 6, expected output: Up to 10 rows strictly after the first page with no overlap. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-01 Exercise 6, assert no more than 10 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_date DESC, o.order_id DESC`. Rejoin the returned keys to `orders` to confirm `order_id`, `customer_id`, `total_amount`, and `order_date` came from the same source rows. Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.
- **Intermediate relation check:** For sql-01 Exercise 6, run `first_page`, and `cursor_row` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-01 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, and `order_date` ordered by `o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order. Evaluate another form against the concrete expected result (Up to 10 rows strictly after the first page with no overlap) and the verification above.
- **Edge case:** Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
