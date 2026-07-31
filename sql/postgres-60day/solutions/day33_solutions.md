# Day 33 — Solutions: Composite and Partial Indexes


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day33_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day33_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Leftmost prefix, Included column, Partial index. Its worked-model focus is:
For a query filtering customerid and a date range, compare (customerid, orderdate) with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.

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

Composite indexes are most useful when their leading columns match common
filter or ordering patterns. Partial indexes contain only rows satisfying an
immutable predicate.

## Exercise 1 — Composite index on `(category, created_at)`

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_created_solution;
CREATE INDEX idx_products_category_created_solution
  ON products(category, created_at);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id,
       name,
       created_at
FROM products
WHERE category = 'Electronics'
  AND created_at >= CURRENT_TIMESTAMP - interval '6 years'
ORDER BY created_at DESC;

ROLLBACK;
```

The equality condition on the leading `category` column lets the B-tree narrow
the search before applying the `created_at` range and can also support the
`ORDER BY created_at, product_id`. A predicate on `created_at` alone cannot use the leftmost
`category` key as efficiently.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_created_solution`, and `idx_products_category_created_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at DESC`.
- **Independent verification:** For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
- **Clause check:** For sql-33 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, `training.idx_products_category_created_solution`, and `idx_products_category_created_solution`, preserve one row per `product_id`, and finish with `product_id`, `name`, and `created_at` ordered by `created_at DESC`.
- **Alternative/trade-off:** For sql-33 Exercise 1, the chosen form is justified by this lesson-specific rationale: The equality condition on the leading `category` column lets the B-tree narrow the search before applying the `created_at` range and can also support `ORDER BY created_at, product_id`. Evaluate another form against the concrete expected result (one row per `product_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 2 — Partial index for high-value orders

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_orders_high_value_solution;
CREATE INDEX idx_orders_high_value_solution
  ON orders(total_amount, order_date)
  WHERE total_amount > 1000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id,
       total_amount,
       order_date
FROM orders
WHERE total_amount > 1000
  AND order_date >= CURRENT_TIMESTAMP - interval '365 days'
ORDER BY total_amount DESC;

ROLLBACK;
```

The query repeats the partial predicate in a form the planner can prove implies
the index condition. The index excludes lower-value orders, reducing its size.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 2, run the underlying read-only query over `orders`, `training.idx_orders_high_value_solution`, and `idx_orders_high_value_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `total_amount`, and `order_date`. The final order is `total_amount DESC`.
- **Independent verification:** For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-33 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `training.idx_orders_high_value_solution`, and `idx_orders_high_value_solution`, preserve one row per `order_id`, and finish with `order_id`, `total_amount`, and `order_date` ordered by `total_amount DESC`.
- **Alternative/trade-off:** For sql-33 Exercise 2, the chosen form is justified by this lesson-specific rationale: The query repeats the partial predicate in a form the planner can prove implies the index condition. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- Partial-index predicates cannot contain volatile or merely stable expressions
  such as `CURRENT_TIMESTAMP - interval '90 days'`. A fixed business condition
  such as `total_amount > 1000` is valid.
- A logically similar parameterized predicate may not be provably compatible
  with a partial index at planning time.
- Column order matters in a composite B-tree. Design it for real query shapes,
  not simply for every column mentioned by a query.
- Small course tables may still receive sequential scans. Judge the design and
  inspect the plan; do not force a node type.

## Exercise 3 — Test the leftmost-prefix limitation

Filtering only `created_at` omits the composite index's first search column.
PostgreSQL may still inspect the index in some conditions, but the query cannot
seek through a known category prefix.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 3, expected output: one row per `product_id`. The final columns are `product_id`, and `created_at`.
- **Independent verification:** For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
- **Clause check:** For sql-33 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, and `created_at`.
- **Alternative/trade-off:** For sql-33 Exercise 3, the chosen form is justified by this lesson-specific rationale: Filtering only `created_at` omits the composite index's first search column. Evaluate another form against the concrete expected result (one row per `product_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Cover customer order history

`customer_id, order_date` are search/order keys. `status` and `total_amount` are
included payload, which can support an index-only scan without widening the
search key.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 4, run the underlying read-only query over `orders`, and `idx_orders_history_cover_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
- **Independent verification:** For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-33 Exercise 4, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `idx_orders_history_cover_solution`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, `status`, and `total_amount` ordered by `order_date DESC`.
- **Alternative/trade-off:** For sql-33 Exercise 4, the chosen form is justified by this lesson-specific rationale: `customer_id, order_date` are search/order keys. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 5 — Prove partial-index eligibility

`total_amount > 1200` implies the stored `> 1000` predicate; `> 500` does not.
Eligibility and final selection are separate planner decisions.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-33 Exercise 5, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-33 Exercise 5, the chosen form is justified by this lesson-specific rationale: `total_amount > 1200` implies the stored `> 1000` predicate; `> 500` does not. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 6 — Evaluate the NULL subset

The answer first measures NULL prevalence, then builds a NULL-only index.
Whether it is worthwhile depends on query frequency, subset size, and added
write/storage cost—not on syntax alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 6, run the underlying read-only query over `customers`, `idx_customers_null_segment_solution`, and `customers.segment` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-33 Exercise 6, expected output: one row per `customer_id`. The final columns are `all_customers`, and `null_segments`.
- **Independent verification:** For sql-33 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-33 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
- **Clause check:** For sql-33 Exercise 6, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `customers`, `idx_customers_null_segment_solution`, and `customers.segment`, preserve one row per `customer_id`, and finish with `all_customers`, and `null_segments`.
- **Alternative/trade-off:** For sql-33 Exercise 6, the chosen form is justified by this lesson-specific rationale: The answer first measures NULL prevalence, then builds a NULL-only index. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
