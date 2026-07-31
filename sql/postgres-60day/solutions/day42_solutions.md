# Day 42 Solutions — Data Quality and Validation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day42_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day42_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Invariant, Orphan, DQ result grain. Its worked-model focus is:
Normalize email with lower(trim(email)), group it, and return groups with COUNT() > 1. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.

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

The goal is to turn scattered checks into one auditable report, then isolate
bad email values. Run the canonical file at
[`day42_solutions.sql`](day42_solutions.sql).

## Exercise 1 — Core-table validation report

Each row is a named check and the number of failing records or duplicate groups.
On the deterministic course seed, every count should be zero.

```sql
SET search_path TO training, public;

SELECT 'customers.null_email' AS check_name,
       COUNT(*) AS failing_rows
FROM customers
WHERE email IS NULL
UNION ALL
SELECT 'customers.duplicate_normalized_email',
       COUNT(*)
FROM (
  SELECT lower(trim(email))
  FROM customers
  GROUP BY lower(trim(email))
  HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'orders.negative_total', COUNT(*)
FROM orders
WHERE total_amount < 0
UNION ALL
SELECT 'orders.orphan_customer', COUNT(*)
FROM orders o
LEFT JOIN customers c USING (customer_id)
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'order_items.orphan_order_or_product', COUNT(*)
FROM order_items oi
LEFT JOIN orders o USING (order_id)
LEFT JOIN products p USING (product_id)
WHERE o.order_id IS NULL OR p.product_id IS NULL
UNION ALL
SELECT 'order_items.invalid_quantity_or_discount', COUNT(*)
FROM order_items
WHERE quantity <= 0 OR discount NOT BETWEEN 0 AND 1
UNION ALL
SELECT 'payments.negative_or_orphan', COUNT(*)
FROM payments p
LEFT JOIN orders o USING (order_id)
WHERE p.amount < 0 OR o.order_id IS NULL
ORDER BY check_name;
```

Expected shape: seven rows with `check_name` and `failing_rows`. A nonzero
result is evidence to investigate, not permission to delete data automatically.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 1, read from `customers`, `orders`, `order_items`, `products`, and `payments`. Build the answer toward `check_name`, and `failing_rows`; keep `check_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 1, expected output: seven rows with `check_name` and `failing_rows`. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name`, and `failing_rows`. The final order is `check_name`.
- **Independent verification:** For sql-42 Exercise 1, project `check_name` plus the raw source columns from `customers`, `orders`, `order_items`, `products`, and `payments` at each join stage; record row count and distinct `check_name`, then assert the final `check_name`, and `failing_rows` values match those staged rows without unintended fanout or loss. Add one row for which `(email IS NULL) OR (total_amount < 0) OR (c.customer_id IS NULL)` is true and one for which it is false; verify only the matching `check_name` value is returned.
- **Intermediate relation check:** For sql-42 Exercise 1, start with the first relation in `customers`, `orders`, `order_items`, `products`, and `payments`; after each join, record total rows and distinct `check_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-42 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, `orders`, `order_items`, `products`, and `payments`, preserve one row per `check_name`, and finish with `check_name`, and `failing_rows` ordered by `check_name`.
- **Alternative/trade-off:** For sql-42 Exercise 1, the chosen form is justified by this lesson-specific rationale: Each row is a named check and the number of failing records or duplicate groups. Evaluate another form against the concrete expected result (seven rows with `check_name` and `failing_rows`. A nonzero result is evidence to investigate, not permission to delete data automatically) and the verification above.
- **Edge case:** Add one row for which `(email IS NULL) OR (total_amount < 0) OR (c.customer_id IS NULL)` is true and one for which it is false; verify only the matching `check_name` value is returned.

## Exercise 2 — Invalid email patterns

```sql
SET search_path TO training, public;

SELECT customer_id, email
FROM customers
WHERE email IS NULL
   OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
ORDER BY customer_id;
```

The seed should return zero rows. The regex is a practical course check, not a
complete implementation of every valid RFC email address.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `email`. The final order is `customer_id`.
- **Independent verification:** For sql-42 Exercise 2, run an anti-check that counts rows where NOT ((email IS NULL OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Repeat with `NULL` in `customer_id`, and `email` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-42 Exercise 2, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
- **Clause check:** For sql-42 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `email` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-42 Exercise 2, the chosen form is justified by this lesson-specific rationale: The seed should return zero rows. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `customer_id`, and `email` and state whether the row is kept, rejected, or classified.

## Reasoning, safety, and pitfalls

- Normalize with `lower(trim(email))` before duplicate detection.
- Anti-join checks remain valuable even with foreign keys: imports or disabled
  constraints can violate assumptions.
- `COUNT(*)` over the duplicate subquery counts duplicate groups, not all rows
  participating in those groups. Label it accordingly.
- Keep validation queries read-only. Fix source data or use a reviewed
  remediation transaction after examining the exact failures.

## Exercise 3 — Explain CHECK and NULL

SQL CHECK rejects FALSE but accepts UNKNOWN. `NOT NULL` is therefore a separate
schema rule when absence is invalid; the catalog query confirms both course
amount columns declare it.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 3, read from `information_schema.columns`. Build the answer toward `table_name`, `column_name`, and `is_nullable`; keep `table_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 3, expected output: one row per `table_name`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
- **Independent verification:** For sql-42 Exercise 3, run an anti-check that counts rows where NOT ((table_schema = 'training' AND table_name IN ('orders', 'payments') AND column_name IN ('total_amount', 'amount'))); require unique `table_name` where the expected grain is one row per key and confirm the projected `table_name`, `column_name`, and `is_nullable` against `information_schema.columns`. Repeat with `NULL` in `table_name`, and `column_name` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-42 Exercise 3, inspect the source keys that survive `WHERE`; then check `table_name, column_name` before applying the row cap.
- **Clause check:** For sql-42 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `information_schema.columns`, preserve one row per `table_name`, and finish with `table_name`, `column_name`, and `is_nullable` ordered by `table_name, column_name`.
- **Alternative/trade-off:** For sql-42 Exercise 3, the chosen form is justified by this lesson-specific rationale: SQL CHECK rejects FALSE but accepts UNKNOWN. Evaluate another form against the concrete expected result (one row per `table_name`) and the verification above.
- **Edge case:** Repeat with `NULL` in `table_name`, and `column_name` and state whether the row is kept, rejected, or classified.

## Exercise 4 — Reconcile order totals

Line values aggregate to one row per order before comparison. The one-cent
tolerance is an explicit currency rule and failing order IDs remain visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 4, read from `order_items`, and `orders`. Build the answer toward `order_id`, `total_amount`, `line_total`, and `difference`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 4, expected output: one row per order before comparison. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
- **Independent verification:** For sql-42 Exercise 4, project `order_id` plus the raw source columns from `order_items`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `total_amount`, `line_total`, and `difference` values match those staged rows without unintended fanout or loss. Add one row for which `(ABS(o.total_amount - c.line_total) > 0.01)` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-42 Exercise 4, run `calculated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-42 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `total_amount`, `line_total`, and `difference` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-42 Exercise 4, the chosen form is justified by this lesson-specific rationale: Line values aggregate to one row per order before comparison. Evaluate another form against the concrete expected result (one row per order before comparison) and the verification above.
- **Edge case:** Add one row for which `(ABS(o.total_amount - c.line_total) > 0.01)` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 5 — Retain duplicate evidence

The normalized email is the grouping key, but `array_agg` preserves raw variants
needed to diagnose case/whitespace differences.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 5, read from `customers`. Build the answer toward `normalized_email`, `raw_variants`, and `rows`; keep `normalized_email`, and `raw_variants` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 5, expected output: one row per `normalized_email`, and `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
- **Independent verification:** For sql-42 Exercise 5, independently aggregate `customers` by `normalized_email`, and `raw_variants`; require one output row for every distinct `normalized_email`, and `raw_variants` tuple satisfying `(email IS NOT NULL)` and compare `rows` tuple by tuple. Add duplicate source candidates for `normalized_email`, and `raw_variants`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-42 Exercise 5, inspect the source keys that survive `WHERE`; then confirm the groups are `normalized_email`, and `raw_variants`; then check `normalized_email` before applying the row cap.
- **Clause check:** For sql-42 Exercise 5, the solution actually uses `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `normalized_email`, and `raw_variants`, and finish with `normalized_email`, `raw_variants`, and `rows` ordered by `normalized_email`.
- **Alternative/trade-off:** For sql-42 Exercise 5, the chosen form is justified by this lesson-specific rationale: The normalized email is the grouping key, but `array_agg` preserves raw variants needed to diagnose case/whitespace differences. Evaluate another form against the concrete expected result (one row per `normalized_email`, and `raw_variants`) and the verification above.
- **Edge case:** Add duplicate source candidates for `normalized_email`, and `raw_variants`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 6 — Detect inclusive range overlap

Promotion pairs share a product, are compared once, and overlap when each start
is no later than the other end. Touching inclusive endpoints therefore count.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 6, read from `promotions`. Build the answer toward `promotion_a`, `promotion_b`, and `product_id`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-42 Exercise 6, expected output: one row per `product_id`. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
- **Independent verification:** For sql-42 Exercise 6, project `product_id` plus the raw source columns from `promotions` at each join stage; record row count and distinct `product_id`, then assert the final `promotion_a`, `promotion_b`, and `product_id` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-42 Exercise 6, start with the first relation in `promotions`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-42 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `promotions`, preserve one row per `product_id`, and finish with `promotion_a`, `promotion_b`, and `product_id` ordered by `a.product_id, promotion_a, promotion_b`.
- **Alternative/trade-off:** For sql-42 Exercise 6, the chosen form is justified by this lesson-specific rationale: Promotion pairs share a product, are compared once, and overlap when each start is no later than the other end. Evaluate another form against the concrete expected result (one row per `product_id`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
