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

- **Inputs/evidence:** For sql-41 Exercise 2, read from `customers`, `orders`, `order_items`, and `products`. First aggregate at (`country`, `product_id`, `name`) grain, then rank products within each country; build the answer toward `country` and `top_five_products`.
- **Expected result/shape:** For sql-41 Exercise 2, expected output: one row per represented country. `top_five_products` contains at most five product names ordered by `revenue DESC, product_id`; `product_id` is the deterministic tie-breaker. The final columns are `country` and `top_five_products`. The final order is `country`.
- **Independent verification:** For sql-41 Exercise 2, independently aggregate line revenue at (`country`, `product_id`, `name`) grain and rank with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)`. For every country, compare the ordered products used by `string_agg`, require no more than five ranked products, and confirm a country with fewer than five products is not padded.
- **Intermediate relation check:** For sql-41 Exercise 2, run `product_revenue` and confirm (`country`, `product_id`) is unique. Run `ranked` and confirm ranks restart at one inside every country before filtering to ranks 1–5.
- **Clause check:** For sql-41 Exercise 2, the joins first produce order-line rows, the first `GROUP BY` reduces them to one row per country/product, `ROW_NUMBER` ranks without changing that row count, `WHERE product_rank <= 5` keeps the local top five, and the final `GROUP BY country` builds one ordered label per country.
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

```sql
WITH lines AS (
  SELECT c.country,
         p.category,
         oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), cube_rows AS (
  SELECT country,
         category,
         SUM(revenue) AS revenue,
         GROUPING(country, category) AS grouping_mask
  FROM lines
  GROUP BY CUBE (country, category)
)
SELECT country,
       category,
       revenue,
       grouping_mask,
       CASE grouping_mask
         WHEN 0 THEN 'detail'
         WHEN 1 THEN 'country subtotal'
         WHEN 2 THEN 'category subtotal'
         WHEN 3 THEN 'grand total'
       END AS grouping_level
FROM cube_rows
ORDER BY grouping_mask, country, category;
```

Read this in three stages:

1. `lines` establishes the additive order-line measure once. It does not use
   `orders.total_amount`, which would be repeated by the item join.
2. `CUBE(country, category)` expands to four grouping sets:
   `(country, category)`, `(country)`, `(category)`, and `()`.
3. `GROUPING(country, category)` encodes omitted expressions from right to
   left. Therefore `1` means category was omitted (a country subtotal), while
   `2` means country was omitted (a category subtotal). The `CASE` translates
   that machine-friendly mask for a human reader.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 3, calculate line revenue from `orders`, `customers`, `order_items`, and `products`, then aggregate with `CUBE(country, category)`. Build the answer toward `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`.
- **Expected result/shape:** For sql-41 Exercise 3, expected output: every grouping level emitted by the two-dimensional cube. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
- **Independent verification:** For sql-41 Exercise 3, compare mask `0` with an independent (`country`, `category`) aggregate, mask `1` with a country aggregate, and mask `2` with a category aggregate; require exactly one mask `3` row. Within each mask, the sum of `revenue` must equal the independent all-lines revenue total.
- **Intermediate relation check:** For sql-41 Exercise 3, confirm `lines` is at order-line grain. In `cube_rows`, confirm (`grouping_mask`, `country`, `category`) identifies a row at its applicable level and inspect counts separately for masks 0, 1, 2, and 3.
- **Clause check:** For sql-41 Exercise 3, `FROM`/`JOIN` establishes line grain, `GROUP BY CUBE` emits four aggregate grains, `GROUPING` labels which dimensions were omitted, the outer `SELECT` translates the mask, and `ORDER BY` presents detail before progressively broader totals.
- **Alternative/trade-off:** Spell out `GROUPING SETS ((country, category), (country), (category), ())` when the requested levels should be especially visible. Use `CUBE` when all combinations are intended. Omitting `(country, category)` would omit detail.
- **Edge case:** A stored `NULL` in a dimension and a generated subtotal marker can print the same dimension value. Use `grouping_mask`, not `country IS NULL` or `category IS NULL`, to identify the row's grain.

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

```sql
WITH country_input AS (
  SELECT country
  FROM customers
  UNION ALL
  SELECT NULL::text
)
SELECT CASE
         WHEN GROUPING(country) = 1 THEN 'ALL COUNTRIES'
         ELSE COALESCE(country, '(stored null)')
       END AS country_label,
       GROUPING(country) AS is_subtotal,
       COUNT(*) AS customers
FROM country_input
GROUP BY GROUPING SETS ((country), ())
ORDER BY is_subtotal, country_label;
```

The extra `NULL::text` is input data inside a CTE; it is not passed to
`GROUPING`. PostgreSQL evaluates `GROUPING(country)` for each output group:
the stored-NULL detail group receives `0`, and the generated grand total
receives `1`. The labels branch on that flag before using `COALESCE`.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 5, read `customers.country` and append one controlled `NULL::text` input row in a `country_input` CTE. Apply `GROUPING(country)` to the grouped expression and build `country_label`, `is_subtotal`, and `customers`.
- **Expected result/shape:** For sql-41 Exercise 5, expected output: one detail row per distinct input country with `is_subtotal = 0`, including a `(stored null)` row, plus exactly one `ALL COUNTRIES` row with `is_subtotal = 1`. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
- **Independent verification:** For sql-41 Exercise 5, require exactly one row with `is_subtotal = 1`, require the `(stored null)` row to have `is_subtotal = 0`, and verify that detail-row `customers` sum to the grand-total `customers`. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
- **Intermediate relation check:** For sql-41 Exercise 5, first count `country_input` and confirm it has exactly one more row than `customers`. Then inspect detail groups (`is_subtotal = 0`) separately from the one grand-total group (`is_subtotal = 1`).
- **Clause check:** For sql-41 Exercise 5, `UNION ALL` appends the controlled stored NULL, `GROUPING SETS` creates detail and grand-total grains, `GROUPING(country)` distinguishes them, and `CASE` assigns non-overlapping labels.
- **Alternative/trade-off:** On a production table that already permits and contains stored NULL countries, omit the fixture row. Keep the `GROUPING`-first label logic unchanged.
- **Edge case:** Never write `GROUPING(NULL)` to simulate data. `GROUPING` must refer to an expression in the current grouping specification; put a NULL in the input relation to test stored-NULL behavior.

## Exercise 6 — Return a typed empty collection

`array_agg` over no qualifying inputs is NULL. The answer uses
`COALESCE(..., '{}'::text[])`; the explicit type must match the aggregate type.

```sql
SELECT COALESCE(
         array_agg(email) FILTER (WHERE false),
         '{}'::text[]
       ) AS empty_email_array
FROM customers;
```

There is no `GROUP BY`, so the aggregate query returns one scalar row even
though no input qualifies for the aggregate. `array_agg` first produces SQL
`NULL`; `COALESCE` then substitutes an empty array of the same `text[]` type.
An empty array is a real, non-NULL value whose `cardinality` is zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)` and use a same-type `COALESCE` fallback. Build the answer toward `empty_email_array`.
- **Expected result/shape:** For sql-41 Exercise 6, expected output: exactly one scalar row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
- **Independent verification:** For sql-41 Exercise 6, assert that the uncoalesced filtered `array_agg` result is `NULL`, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`.
- **Intermediate relation check:** For sql-41 Exercise 6, run `SELECT array_agg(email) FILTER (WHERE false) FROM customers` first and observe one row containing SQL NULL. Then add `COALESCE` and observe one row containing `{}`.
- **Clause check:** For sql-41 Exercise 6, `FROM customers` supplies the input relation, aggregate `FILTER` gives `array_agg` zero qualifying rows, the aggregate still creates one scalar group, and `SELECT` applies the typed fallback.
- **Alternative/trade-off:** Return SQL NULL when “not computed” is materially different from “computed and empty.” Return an empty array when downstream callers should be able to iterate without a NULL branch.
- **Edge case:** A table with zero rows behaves the same for this scalar aggregate: one output row, NULL before `COALESCE`, and an empty `text[]` afterwards.
