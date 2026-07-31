# Day 32 — Solutions: Index Fundamentals


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day32_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day32_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Selectivity, Index scan, Index-only scan. Its worked-model focus is:
Capture a category-filter plan before creating products(category), create the index inside the rollback-only transaction, and rerun the identical query. Record the plan even if PostgreSQL keeps the sequential scan: the compact seed can make reading the table cheaper than traversing an index.

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

Indexes trade storage and write cost for faster access to selected rows. Both
answers run inside a transaction and roll back, so rerunning the document does
not leave demonstration indexes behind.

## Exercise 1 — Index `products(category)` and test a filter

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_solution;
CREATE INDEX idx_products_category_solution
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id,
       name,
       price
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Expected plan shape is not guaranteed. The seeded `products` table has only a
few hundred rows and each category is common, so a sequential scan can be
cheaper even though the index is valid.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_solution`, and `idx_products_category_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-32 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `price`.
- **Independent verification:** For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
- **Clause check:** For sql-32 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `products`, `training.idx_products_category_solution`, and `idx_products_category_solution`, preserve one row per `product_id`, and finish with `product_id`, `name`, and `price`.
- **Alternative/trade-off:** For sql-32 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected plan shape is not guaranteed. Evaluate another form against the concrete expected result (one row per `product_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 2 — Compare without, with, and after dropping the index

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

CREATE INDEX idx_products_category_compare
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

DROP INDEX idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Record node type, estimated rows, actual rows, planning time, execution time,
and buffers for each plan. On this small dataset, “no visible plan change” is a
valid observation, not a failed exercise.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 2, run the underlying read-only query over `products`, `training.idx_products_category_compare`, and `idx_products_category_compare` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-32 Exercise 2, expected output: one row per `product_id`. The final columns are `product_id`.
- **Independent verification:** For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
- **Clause check:** For sql-32 Exercise 2, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `products`, `training.idx_products_category_compare`, and `idx_products_category_compare`, preserve one row per `product_id`, and finish with `product_id`.
- **Alternative/trade-off:** For sql-32 Exercise 2, the chosen form is justified by this lesson-specific rationale: Record node type, estimated rows, actual rows, planning time, execution time, and buffers for each plan. Evaluate another form against the concrete expected result (one row per `product_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- Do not use `SET enable_seqscan = off` as proof that an index is useful; it
  changes the planner's choices instead of demonstrating normal behavior.
- A B-tree handles equality and ordered range predicates, so a hash index is
  rarely needed for a basic equality lookup.
- Index names share a schema namespace, which is why the solution uses unique,
  exercise-specific names.
- Indexes created in the learner script are rolled back at the end of that
  script and are not available on later days.

## Exercise 3 — Predict from selectivity

Count each category before reading the plan. The optimizer may prefer a
sequential scan on this compact seed even when the index is valid and usable.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-32 Exercise 3, expected output: one row per `category`. The final columns are `category`, and `products`. The final order is `products DESC, category`.
- **Independent verification:** For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows.
- **Clause check:** For sql-32 Exercise 3, the solution actually uses `FROM`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `category`, and finish with `category`, and `products` ordered by `products DESC, category`.
- **Alternative/trade-off:** For sql-32 Exercise 3, the chosen form is justified by this lesson-specific rationale: Count each category before reading the plan. Evaluate another form against the concrete expected result (one row per `category`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Index a timestamp range

The solution indexes `payment_date` and uses `[start, end)` bounds. Half-open
windows compose cleanly without double-counting a boundary timestamp.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 4, run the underlying read-only query over `payments`, and `idx_payments_date_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-32 Exercise 4, expected output: one row per `payment_id`. The final columns are `payment_id`, and `amount`.
- **Independent verification:** For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows.
- **Clause check:** For sql-32 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `payments`, and `idx_payments_date_solution`, preserve one row per `payment_id`, and finish with `payment_id`, and `amount`.
- **Alternative/trade-off:** For sql-32 Exercise 4, the chosen form is justified by this lesson-specific rationale: The solution indexes `payment_date` and uses `[start, end)` bounds. Evaluate another form against the concrete expected result (one row per `payment_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 5 — Match an expression index

An index on `country` does not store `lower(country)`. The solution indexes that
exact expression and repeats it exactly in the predicate.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 5, run the underlying read-only query over `customers`, and `idx_customers_lower_country_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-32 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`.
- **Independent verification:** For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
- **Clause check:** For sql-32 Exercise 5, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `customers`, and `idx_customers_lower_country_solution`, preserve one row per `customer_id`, and finish with `customer_id`.
- **Alternative/trade-off:** For sql-32 Exercise 5, the chosen form is justified by this lesson-specific rationale: An index on `country` does not store `lower(country)`. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 6 — Preserve the ordering contract

The unordered query is intentionally nondeterministic. Only the query with
`ORDER BY country, customer_id` promises reproducible presentation order; an
index's incidental scan order is not a substitute.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 6, read from `customers`. Build the answer toward `customer_id`, and `country`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-32 Exercise 6, expected output: at most 10 rows keyed by `customer_id`. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
- **Independent verification:** For sql-32 Exercise 6, assert no more than 10 rows, no duplicate `customer_id`, and no adjacent pair that violates `country, customer_id`. Rejoin the returned keys to `customers` to confirm `customer_id`, and `country` came from the same source rows. Run with 10 minus one and 10 plus one eligible rows; require the output cap of 10 while retaining `country, customer_id`.
- **Intermediate relation check:** For sql-32 Exercise 6, check `country, customer_id` before applying the row cap.
- **Clause check:** For sql-32 Exercise 6, the solution actually uses `FROM`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `country` ordered by `country, customer_id`.
- **Alternative/trade-off:** For sql-32 Exercise 6, the chosen form is justified by this lesson-specific rationale: The unordered query is intentionally nondeterministic. Evaluate another form against the concrete expected result (at most 10 rows keyed by `customer_id`) and the verification above.
- **Edge case:** Run with 10 minus one and 10 plus one eligible rows; require the output cap of 10 while retaining `country, customer_id`.
