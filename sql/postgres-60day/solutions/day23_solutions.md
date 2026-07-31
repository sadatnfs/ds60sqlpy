# Day 23 solutions — Common Table Expressions (CTEs) Introduction


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day23_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day23_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are CTE, Inlining, Materialization. Its worked-model focus is:
Trace orderlines at one row per order, then topcustomers at one row per customer, then the final top-N presentation. Run each CTE body independently while developing and verify its key uniqueness before adding the next stage.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 1, read from `orders`, and `order_items`. Build the answer toward `customer_id`, `order_count`, and `net_revenue`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-23 Exercise 1, expected output: One row per ordering customer. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
- **Independent verification:** For sql-23 Exercise 1, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `net_revenue` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-23 Exercise 1, run `order_values` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-23 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `order_items`, preserve one row per `customer_id`, and finish with `customer_id`, `order_count`, and `net_revenue` ordered by `net_revenue DESC, ov.customer_id`.
- **Alternative/trade-off:** For sql-23 Exercise 1, the chosen form is justified by this lesson-specific rationale: Name the one-row-per-order grain before changing to customer grain. Evaluate another form against the concrete expected result (One row per ordering customer) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, and `net_revenue` for the existing `customer_id` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 2, read from `order_items`, and `products`. Compute `top_category`, and `all_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-23 Exercise 2, expected output: One summary row. The final columns are `top_category`, and `all_revenue`.
- **Independent verification:** For sql-23 Exercise 2, evaluate each of `all_revenue` in a separate control `SELECT` over `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
- **Intermediate relation check:** For sql-23 Exercise 2, run `category_revenue` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-23 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `order_items`, and `products`, preserve exactly one summary row, and finish with `top_category`, and `all_revenue`.
- **Alternative/trade-off:** For sql-23 Exercise 2, the chosen form is justified by this lesson-specific rationale: A named aggregate can support multiple scalar reads without repeating the business formula. Evaluate another form against the concrete expected result (One summary row) and the verification above.
- **Edge case:** Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 3, read from `payments`, and `orders`. Build the answer toward `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-23 Exercise 3, expected output: One row per order. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
- **Independent verification:** For sql-23 Exercise 3, project `order_id` plus the raw source columns from `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_total`, `paid_amount`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-23 Exercise 3, run `paid`, and `reconciled` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-23 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `order_total`, `paid_amount`, and `unpaid_balance` ordered by `ABS(total_amount - paid_amount) DESC, order_id`.
- **Alternative/trade-off:** For sql-23 Exercise 3, the chosen form is justified by this lesson-specific rationale: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 4, read from `orders`, `materialized_orders`, and `inline_orders`. Build the answer toward `variant`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-23 Exercise 4, expected output: Two count rows with equal values. The final columns are `variant`, and `row_count`. The final order is `variant`.
- **Independent verification:** For sql-23 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `variant`, and `row_count` against `orders`, `materialized_orders`, and `inline_orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-23 Exercise 4, inspect the source keys that survive `WHERE`; then check `variant` before applying the row cap.
- **Clause check:** For sql-23 Exercise 4, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `materialized_orders`, and `inline_orders`, preserve one row per `order_id`, and finish with `variant`, and `row_count` ordered by `variant`.
- **Alternative/trade-off:** For sql-23 Exercise 4, the chosen form is justified by this lesson-specific rationale: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment. Evaluate another form against the concrete expected result (Two count rows with equal values) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `country`, and `country_revenue`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-23 Exercise 5, expected output: One row per country. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
- **Independent verification:** For sql-23 Exercise 5, independently aggregate `orders`, `order_items`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-23 Exercise 5, run `order_values`, and `customer_revenue` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
- **Clause check:** For sql-23 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `customers`, preserve one row per `country`, and finish with `country`, and `country_revenue` ordered by `country_revenue DESC, c.country`.
- **Alternative/trade-off:** For sql-23 Exercise 5, the chosen form is justified by this lesson-specific rationale: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`. Evaluate another form against the concrete expected result (One row per country) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `country_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-23 Exercise 6, read the target keys from `products` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-23 Exercise 6, expected output: One summary row for a bounded three-product update. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
- **Independent verification:** For sql-23 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `products` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.
- **Intermediate relation check:** For sql-23 Exercise 6, run `candidates`, and `updated` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-23 Exercise 6, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, `ORDER BY`, `LIMIT`, and `RETURNING`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `updated_rows`, `first_updated_product`, and `last_updated_product`.
- **Alternative/trade-off:** For sql-23 Exercise 6, the chosen form is justified by this lesson-specific rationale: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation. Evaluate another form against the concrete expected result (One summary row for a bounded three-product update) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
