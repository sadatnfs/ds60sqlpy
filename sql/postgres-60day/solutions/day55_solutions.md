# Day 55 Solutions — BI Drill-down and Subtotals


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day55_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day55_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are ROLLUP, CUBE, GROUPING flag. Its worked-model focus is:
Compare ROLLUP(country, category) with CUBE(country, category). Both include detail, country subtotal, and grand total; CUBE also adds category-only subtotals. Use GROUPING(country) and GROUPING(category) to label each level, then reconcile the grand total with source line revenue.

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

The two exercises compare `ROLLUP` and `CUBE`, then add order status to a
country/category/product top-five drill-down. See
[`day55_solutions.sql`](day55_solutions.sql).

## Exercise 1 — Compare row counts

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT c.country,
         p.category,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), rollup_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY ROLLUP (country, category)
), cube_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
)
SELECT (SELECT COUNT(*) FROM rollup_rows) AS rollup_row_count,
       (SELECT COUNT(*) FROM cube_rows) AS cube_row_count;
```

Expected shape: one comparison row. `CUBE(country, category)` adds category-only
subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count
is greater on this seed.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 1, read from `orders`, `customers`, `order_items`, and `products`. Compute `rollup_row_count`, and `cube_row_count` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-55 Exercise 1, expected output: one comparison row. `CUBE(country, category)` adds category-only subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count is greater on this seed. The final columns are `rollup_row_count`, and `cube_row_count`.
- **Independent verification:** For sql-55 Exercise 1, evaluate each of `rollup_row_count`, and `cube_row_count` in a separate control `SELECT` over `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-55 Exercise 1, run `line`, `rollup_rows`, and `cube_rows` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-55 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve exactly one summary row, and finish with `rollup_row_count`, and `cube_row_count`.
- **Alternative/trade-off:** For sql-55 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected shape: one comparison row. Evaluate another form against the concrete expected result (one comparison row. `CUBE(country, category)` adds category-only subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count is greater on this seed) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 2 — Status-aware top five

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT c.country,
         p.category,
         o.status,
         p.product_id,
         p.name,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), product_revenue AS (
  SELECT country,
         category,
         status,
         product_id,
         name,
         SUM(revenue) AS revenue
  FROM line
  GROUP BY country, category, status, product_id, name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country, category, status
           ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       category,
       status,
       product_id,
       name,
       ROUND(revenue, 2) AS revenue,
       product_rank
FROM ranked
WHERE product_rank <= 5
ORDER BY country, category, status, product_rank;
```

Expected grain: up to five rows per `(country, category, status)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 2, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-55 Exercise 2, expected output: up to five rows per `(country, category, status)`. The final columns are `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`. The final order is `country, category, status, product_rank`.
- **Independent verification:** For sql-55 Exercise 2, project `product_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `product_id`, then assert the final `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `country` value and different `product_rank` values; verify `country, category, status, product_rank` produces the intended rank and display order.
- **Intermediate relation check:** For sql-55 Exercise 2, run `line`, `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-55 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve one row per `product_id`, and finish with `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank` ordered by `country, category, status, product_rank`.
- **Alternative/trade-off:** For sql-55 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected grain: up to five rows per `(country, category, status)`. Evaluate another form against the concrete expected result (up to five rows per `(country, category, status)`) and the verification above.
- **Edge case:** Give two rows the same `country` value and different `product_rank` values; verify `country, category, status, product_rank` produces the intended rank and display order.

## Reasoning, safety, and pitfalls

- `CUBE` grows quickly: three dimensions produce up to eight grouping sets,
  before considering the number of distinct dimension values.
- `NULL` can mean a subtotal or a real null dimension value. Include
  `GROUPING(...)` flags in user-facing subtotal reports when ambiguity exists.
- Aggregate product revenue before ranking.
- `ROW_NUMBER` plus `product_id` yields exactly five deterministic rows when at
  least five products exist; `RANK` can return more because of ties.

## Exercise 3 — Enumerate ROLLUP levels

PostgreSQL's `GROUPING(country, category)` returns a bit mask: detail, country
subtotal, and grand total have stable numeric identities.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 3, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `revenue`, and `grouping_mask`; keep `country`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-55 Exercise 3, expected output: one row per `country`, and `category`. The final columns are `country`, `category`, `revenue`, and `grouping_mask`. The final order is `grouping_mask, country, category`.
- **Independent verification:** For sql-55 Exercise 3, independently aggregate `orders`, `customers`, `order_items`, and `products` by `country`, and `category`; require one output row for every distinct `country`, and `category` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-55 Exercise 3, run `line` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-55 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve one row per `country`, and `category`, and finish with `country`, `category`, `revenue`, and `grouping_mask` ordered by `grouping_mask, country, category`.
- **Alternative/trade-off:** For sql-55 Exercise 3, the chosen form is justified by this lesson-specific rationale: PostgreSQL's `GROUPING(country, category)` returns a bit mask: detail, country subtotal, and grand total have stable numeric identities. Evaluate another form against the concrete expected result (one row per `country`, and `category`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.

## Exercise 4 — Label levels from the bit mask

The display label is derived from that mask, not from `column IS NULL`. This
keeps machine-readable level identity beside human-readable text.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 4, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `level_id`, `level_name`, `country`, `category`, and `revenue`; keep `level_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-55 Exercise 4, expected output: one row per `level_id`. The final columns are `level_id`, `level_name`, `country`, `category`, and `revenue`. The final order is `level_id, country, category`.
- **Independent verification:** For sql-55 Exercise 4, independently aggregate `orders`, `customers`, `order_items`, and `products` by `level_id`; require one output row for every distinct `level_id` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `level_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-55 Exercise 4, run `line` one at a time. Record each CTE's row count and `level_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-55 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve one row per `level_id`, and finish with `level_id`, `level_name`, `country`, `category`, and `revenue` ordered by `level_id, country, category`.
- **Alternative/trade-off:** For sql-55 Exercise 4, the chosen form is justified by this lesson-specific rationale: The display label is derived from that mask, not from `column IS NULL`. Evaluate another form against the concrete expected result (one row per `level_id`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `level_id` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Return exactly five products

Revenue aggregates before ranking. `ROW_NUMBER` with `product_id` as final key
limits every partition deterministically even when revenue ties.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 5, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-55 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `country, position`.
- **Independent verification:** For sql-55 Exercise 5, project `order_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one row for which `(position <= 5)` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-55 Exercise 5, run `revenue`, and `ranked` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-55 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` ordered by `country, position`.
- **Alternative/trade-off:** For sql-55 Exercise 5, the chosen form is justified by this lesson-specific rationale: Revenue aggregates before ranking. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one row for which `(position <= 5)` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 6 — Preserve unknown versus ALL

The stored member label and generated-total flag are separate fields. A real
NULL/unknown member retains flag zero; ALL has flag one.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 6, read from `customers`. Build the answer toward `display_country`, `is_generated_total`, and `customers`; keep `display_country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-55 Exercise 6, expected output: one row per `display_country`. The final columns are `display_country`, `is_generated_total`, and `customers`. The final order is `is_generated_total, display_country`.
- **Independent verification:** For sql-55 Exercise 6, independently aggregate `customers` by `display_country`; require one output row for every distinct `display_country` tuple and compare `is_generated_total`, and `customers` tuple by tuple. Repeat with `NULL` in `display_country`, and `is_generated_total` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-55 Exercise 6, confirm the groups are `display_country`; then check `is_generated_total, display_country` before applying the row cap.
- **Clause check:** For sql-55 Exercise 6, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `display_country`, and finish with `display_country`, `is_generated_total`, and `customers` ordered by `is_generated_total, display_country`.
- **Alternative/trade-off:** For sql-55 Exercise 6, the chosen form is justified by this lesson-specific rationale: The stored member label and generated-total flag are separate fields. Evaluate another form against the concrete expected result (one row per `display_country`) and the verification above.
- **Edge case:** Repeat with `NULL` in `display_country`, and `is_generated_total` and state whether the row is kept, rejected, or classified.
