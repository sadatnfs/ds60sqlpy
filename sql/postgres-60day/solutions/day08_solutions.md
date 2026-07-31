# Day 08 solutions — Scalar and Inline Subqueries


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day08_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day08_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Scalar subquery, Inline view, Uncorrelated subquery. Its worked-model focus is:
For each customer, the learner needs one first-order date. MIN(orderdate) returns exactly one value, including NULL when no order exists. Contrast that with selecting raw order dates, which can raise “more than one row returned by a subquery used as an expression.”

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-08 Exercise 1, expected output: Order rows above the global average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
- **Independent verification:** For sql-08 Exercise 1, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-08 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.total_amount DESC, o.order_id` before applying the row cap.
- **Clause check:** For sql-08 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, and `total_amount` ordered by `o.total_amount DESC, o.order_id`.
- **Alternative/trade-off:** For sql-08 Exercise 1, the chosen form is justified by this lesson-specific rationale: The aggregate subquery is guaranteed to return exactly one value. Evaluate another form against the concrete expected result (Order rows above the global average) and the verification above.
- **Edge case:** Add one row for which `(o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))` is true and one for which it is false; verify only the matching `order_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 2, read from `customers`. Build the answer toward `country`, `country_customers`, and `all_customers`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-08 Exercise 2, expected output: One row per country with a common global total. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
- **Independent verification:** For sql-08 Exercise 2, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_customers`, and `all_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `all_customers` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-08 Exercise 2, confirm the groups are `country`; then check `country_customers DESC, c.country` before applying the row cap.
- **Clause check:** For sql-08 Exercise 2, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `country`, and finish with `country`, `country_customers`, and `all_customers` ordered by `country_customers DESC, c.country`.
- **Alternative/trade-off:** For sql-08 Exercise 2, the chosen form is justified by this lesson-specific rationale: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row. Evaluate another form against the concrete expected result (One row per country with a common global total) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `country_customers`, and `all_customers` for the existing `country` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 3, read from `orders`, and `customers`. Build the answer toward `customer_id`, `full_name`, and `latest_order_date`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-08 Exercise 3, expected output: One row per customer. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
- **Independent verification:** For sql-08 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `latest_order_date` against `orders`, and `customers`. Tie two rows on `latest_order_date DESC NULLS LAST` and give them different `c.customer_id` values; verify `latest_order_date DESC NULLS LAST, c.customer_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-08 Exercise 3, inspect the source keys that survive `WHERE`; then check `latest_order_date DESC NULLS LAST, c.customer_id` before applying the row cap.
- **Clause check:** For sql-08 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `full_name`, and `latest_order_date` ordered by `latest_order_date DESC NULLS LAST, c.customer_id`.
- **Alternative/trade-off:** For sql-08 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use `MAX` to guarantee one result and let customers without orders receive NULL. Evaluate another form against the concrete expected result (One row per customer) and the verification above.
- **Edge case:** Tie two rows on `latest_order_date DESC NULLS LAST` and give them different `c.customer_id` values; verify `latest_order_date DESC NULLS LAST, c.customer_id` chooses a stable first/last row.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 4, read from `products`. Compute `no_row_becomes_null` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-08 Exercise 4, expected output: One row whose boolean result is true. The final columns are `no_row_becomes_null`.
- **Independent verification:** For sql-08 Exercise 4, evaluate each of `no_row_becomes_null` in a separate control `SELECT` over `products`; require one final row and compare every value. Repeat with `NULL` in `no_row_becomes_null` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-08 Exercise 4, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-08 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `products`, preserve exactly one summary row, and finish with `no_row_becomes_null`.
- **Alternative/trade-off:** For sql-08 Exercise 4, the chosen form is justified by this lesson-specific rationale: Use a deliberately impossible product key and test the scalar result with `IS NULL`. Evaluate another form against the concrete expected result (One row whose boolean result is true) and the verification above.
- **Edge case:** Repeat with `NULL` in `no_row_becomes_null` and state whether the row is kept, rejected, or classified.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 5, read from `products`. Build the answer toward `category`, `category_max_price`, and `global_max_price`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-08 Exercise 5, expected output: One row per category with a scalar global maximum for comparison. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
- **Independent verification:** For sql-08 Exercise 5, independently aggregate `products` by `category`; require one output row for every distinct `category` tuple and compare `category_max_price`, and `global_max_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `category_max_price`, and `global_max_price` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-08 Exercise 5, confirm the groups are `category`; then check `p.category` before applying the row cap.
- **Clause check:** For sql-08 Exercise 5, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `category`, and finish with `category`, `category_max_price`, and `global_max_price` ordered by `p.category`.
- **Alternative/trade-off:** For sql-08 Exercise 5, the chosen form is justified by this lesson-specific rationale: Choose the business reduction explicitly; this answer uses maximum price. Evaluate another form against the concrete expected result (One row per category with a scalar global maximum for comparison) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `category_max_price`, and `global_max_price` for the existing `category` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-08 Exercise 6, read from `customers`. Build the answer toward `country`, `country_customers`, and `customer_share`; keep `country`, and `customer_count` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-08 Exercise 6, expected output: One row per country with country share. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
- **Independent verification:** For sql-08 Exercise 6, independently aggregate `customers` by `country`, and `customer_count`; require one output row for every distinct `country`, and `customer_count` tuple and compare `country_customers`, and `customer_share` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `customer_share` for the existing `country`, and `customer_count` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-08 Exercise 6, run `global` one at a time. Record each CTE's row count and `country`, and `customer_count` uniqueness before the next stage uses it.
- **Clause check:** For sql-08 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `country`, and `customer_count`, and finish with `country`, `country_customers`, and `customer_share` ordered by `customer_share DESC, c.country`.
- **Alternative/trade-off:** For sql-08 Exercise 6, the chosen form is justified by this lesson-specific rationale: Compute the global total once, then cross join the guaranteed one-row relation. Evaluate another form against the concrete expected result (One row per country with country share) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `country_customers`, and `customer_share` for the existing `country`, and `customer_count` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
