# Day 41 Solutions — Complex Aggregations


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day41_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day41_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are FILTER clause, Conditional aggregate, Ordered aggregation. Its worked-model focus is:
Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.

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

The learner script introduces `FILTER`, conditional aggregation, and
`string_agg`. The two exercises turn those techniques into a category dashboard
and a country-level top-product label. The canonical runnable answer is also in
[`day41_solutions.sql`](day41_solutions.sql).

## Exercise 1 — Six category dashboard metrics

Build one row per product category containing:

1. revenue in the last 30 days;
2. revenue in the last 90 days;
3. distinct orders in the last 30 days;
4. units in the last 30 days;
5. distinct customers in the last 90 days; and
6. revenue per order in the last 30 days.

```sql
SET search_path TO training, public;

WITH lines AS (
  SELECT p.category,
         o.order_id,
         o.customer_id,
         o.order_date,
         oi.quantity,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT category,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ), 2) AS revenue_30d,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ), 2) AS revenue_90d,
       COUNT(DISTINCT order_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS orders_30d,
       SUM(quantity) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS units_30d,
       COUNT(DISTINCT customer_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ) AS customers_90d,
       ROUND(
         SUM(revenue) FILTER (
           WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
         )
         / NULLIF(
             COUNT(DISTINCT order_id) FILTER (
               WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
             ),
             0
           ),
         2
       ) AS revenue_per_order_30d
FROM lines
GROUP BY category
ORDER BY revenue_30d DESC NULLS LAST, category;
```

Expected shape: one row for each category in `training.products`, with six
metric columns. A category with no qualifying recent activity can have `NULL`
windowed sums. `NULLIF` makes revenue per order `NULL` instead of raising a
division-by-zero error.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 1, read from `orders`, `order_items`, `products`, and `training.products`. Build the answer toward `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 1, expected output: one row for each category in `training.products`, with six metric columns. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
- **Independent verification:** For sql-41 Exercise 1, independently aggregate `orders`, `order_items`, `products`, and `training.products` by `category`; require one output row for every distinct `category` tuple and compare `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_30d`, `revenue_90d`, and `orders_30d` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-41 Exercise 1, run `lines` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-41 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, `products`, and `training.products`, preserve one row per `category`, and finish with `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d` ordered by `revenue_30d DESC NULLS LAST, category`.
- **Alternative/trade-off:** For sql-41 Exercise 1, the chosen form is justified by this lesson-specific rationale: Build one row per product category containing: 1. Evaluate another form against the concrete expected result (one row for each category in `training.products`, with six metric columns) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `revenue_30d`, `revenue_90d`, and `orders_30d` for the existing `category` tuple and verify the new tuple appears exactly once.

## Exercise 2 — Top five product names per country

Rank at `(country, product)` grain before aggregating names. This avoids the
common mistake of applying `LIMIT 5` to the entire result instead of five
products per country.

```sql
SET search_path TO training, public;

WITH product_revenue AS (
  SELECT c.country,
         p.product_id,
         p.name,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY c.country, p.product_id, p.name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       string_agg(name, ', ' ORDER BY product_rank) AS top_five_products
FROM ranked
WHERE product_rank <= 5
GROUP BY country
ORDER BY country;
```

Expected shape: one row per represented country and one comma-separated label
ordered from highest to lowest product revenue.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 2, read from `customers`, `orders`, `order_items`, and `products`. Build the answer toward `country`, and `top_five_products`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 2, expected output: one row per represented country and one comma-separated label ordered from highest to lowest product revenue. The final columns are `country`, and `top_five_products`. The final order is `country`.
- **Independent verification:** For sql-41 Exercise 2, independently aggregate `customers`, `orders`, `order_items`, and `products` by `country`; require one output row for every distinct `country` tuple satisfying `(product_rank <= 5)` and compare `top_five_products` tuple by tuple. Give two rows the same `country` value and different ``country`` values; verify `country` produces the intended rank and display order.
- **Intermediate relation check:** For sql-41 Exercise 2, run `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
- **Clause check:** For sql-41 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, `orders`, `order_items`, and `products`, preserve one row per `country`, and finish with `country`, and `top_five_products` ordered by `country`.
- **Alternative/trade-off:** For sql-41 Exercise 2, the chosen form is justified by this lesson-specific rationale: Rank at `(country, product)` grain before aggregating names. Evaluate another form against the concrete expected result (one row per represented country and one comma-separated label ordered from highest to lowest product revenue) and the verification above.
- **Edge case:** Give two rows the same `country` value and different ``country`` values; verify `country` produces the intended rank and display order.

## Reasoning, safety, and pitfalls

- Compute line revenue from `order_items`; do not multiply `orders.total_amount`
  after joining to items because that would repeat the order total per line.
- Use `DISTINCT` inside counts when the input is at line-item grain.
- Add a deterministic tie-breaker (`product_id`) to `ROW_NUMBER`.
- Both answers are read-only and safe to run repeatedly.

## Exercise 3 — Compare grouping sets and CUBE

The `CUBE(country, category)` answer emits detail, both one-dimensional
subtotals, and the grand total. `GROUPING(country, category)` identifies each
generated level.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 3, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `revenue`, and `grouping_mask`; keep `country`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 3, expected output: one row per `country`, and `category`. The final columns are `country`, `category`, `revenue`, and `grouping_mask`. The final order is `grouping_mask, country, category`.
- **Independent verification:** For sql-41 Exercise 3, independently aggregate `orders`, `customers`, `order_items`, and `products` by `country`, and `category`; require one output row for every distinct `country`, and `category` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-41 Exercise 3, run `lines` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-41 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `products`, preserve one row per `country`, and `category`, and finish with `country`, `category`, `revenue`, and `grouping_mask` ordered by `grouping_mask, country, category`.
- **Alternative/trade-off:** For sql-41 Exercise 3, the chosen form is justified by this lesson-specific rationale: The `CUBE(country, category)` answer emits detail, both one-dimensional subtotals, and the grand total. Evaluate another form against the concrete expected result (one row per `country`, and `category`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.

## Exercise 4 — State metric populations with FILTER

Each status/time population appears beside its aggregate, making several
country metrics readable without repeating the whole grouped relation.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 4, read from `orders`, and `customers`. Build the answer toward `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 4, expected output: one row per `country`. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
- **Independent verification:** For sql-41 Exercise 4, independently aggregate `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `orders`, `paid_orders`, and `paid_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-41 Exercise 4, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-41 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `country`, and finish with `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers` ordered by `c.country`.
- **Alternative/trade-off:** For sql-41 Exercise 4, the chosen form is justified by this lesson-specific rationale: Each status/time population appears beside its aggregate, making several country metrics readable without repeating the whole grouped relation. Evaluate another form against the concrete expected result (one row per `country`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `orders`, `paid_orders`, and `paid_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Distinguish stored and generated NULLs

`GROUPING(country)` is one only for the generated subtotal. A stored NULL, if
allowed by the model, keeps grouping flag zero and receives a different label.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 5, read from `customers`. Build the answer toward `country_label`, `is_subtotal`, and `customers`; keep `country_label`, and `is_subtotal` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 5, expected output: one row per `country_label`, and `is_subtotal`. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
- **Independent verification:** For sql-41 Exercise 5, independently aggregate `customers` by `country_label`, and `is_subtotal`; require one output row for every distinct `country_label`, and `is_subtotal` tuple and compare `customers` tuple by tuple. Repeat with `NULL` in `GROUPING` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-41 Exercise 5, confirm the groups are `country_label`, and `is_subtotal`; then check `is_subtotal, country_label` before applying the row cap.
- **Clause check:** For sql-41 Exercise 5, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `country_label`, and `is_subtotal`, and finish with `country_label`, `is_subtotal`, and `customers` ordered by `is_subtotal, country_label`.
- **Alternative/trade-off:** For sql-41 Exercise 5, the chosen form is justified by this lesson-specific rationale: `GROUPING(country)` is one only for the generated subtotal. Evaluate another form against the concrete expected result (one row per `country_label`, and `is_subtotal`) and the verification above.
- **Edge case:** Repeat with `NULL` in `GROUPING` and state whether the row is kept, rejected, or classified.

## Exercise 6 — Return a typed empty collection

`array_agg` over no qualifying inputs is NULL. The answer uses
`COALESCE(..., '{}'::text[])`; the explicit type must match the aggregate type.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 6, read from `customers`. Build the answer toward `empty_email_array`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-41 Exercise 6, expected output: one row per `customer_id`. The final columns are `empty_email_array`.
- **Independent verification:** For sql-41 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `empty_email_array` against `customers`. Repeat with `NULL` in `empty_email_array` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-41 Exercise 6, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-41 Exercise 6, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `empty_email_array`.
- **Alternative/trade-off:** For sql-41 Exercise 6, the chosen form is justified by this lesson-specific rationale: `array_agg` over no qualifying inputs is NULL. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `empty_email_array` and state whether the row is kept, rejected, or classified.
