# Day 41 Solutions: Complex Aggregations


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day41_solutions.sql
```

The script reads only course tables, so it is safe to rerun. Compare the
category and country keys and the `NULL` cells first, then the numbers; the
[study guide's solution routine](../../STUDY-GUIDE.md#read-a-solution) covers
the rest.

## Clause-by-clause reading map

Read each answer in the
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
and for this lesson watch two places in particular. First, the joins: every
answer that sums money starts from `order_items` line revenue, and every count
of orders or customers uses `COUNT(DISTINCT ...)` because the line join repeats
each order. Second, the `GROUP BY`: Exercises 3 and 5 group by several grains
at once, so `GROUPING(...)` in the `SELECT` list is what tells you which grain
a printed row belongs to.

The learner script introduces `FILTER`, conditional aggregation, and
`string_agg`. The exercises turn those techniques into a category dashboard, a
country-level top-product label, a labeled cube, and two `NULL` boundary
checks. The canonical runnable answer is also in
[`day41_solutions.sql`](day41_solutions.sql).

## Exercise 1: Six category dashboard metrics

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
  SELECT
    p.category,
    o.order_id,
    o.customer_id,
    o.order_date,
    oi.quantity,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM
    orders o
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id))
SELECT
  category,
  ROUND(SUM(revenue) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'), 2) AS revenue_30d,
  ROUND(SUM(revenue) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'), 2) AS revenue_90d,
  COUNT(DISTINCT order_id) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days') AS orders_30d,
  SUM(quantity) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days') AS units_30d,
  COUNT(DISTINCT customer_id) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days') AS customers_90d,
  ROUND(SUM(revenue) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days') / NULLIF (COUNT(DISTINCT order_id) FILTER (WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'), 0), 2) AS revenue_per_order_30d
FROM
  lines
GROUP BY
  category
ORDER BY
  revenue_30d DESC NULLS LAST,
  category;
```

Expected shape: one row for each category in `training.products`, with six
metric columns. A category with no qualifying recent activity can have `NULL`
windowed sums. `NULLIF` makes revenue per order `NULL` instead of raising a
division-by-zero error.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 1, join `orders`, `order_items`, and `products` once in a `lines` CTE (13,085 rows, one per order line) carrying `category`, `order_id`, `customer_id`, `order_date`, `quantity`, and line revenue `unit_price * quantity * (1 - discount)`; every metric is a `FILTER` over that relation with 30-day or 90-day windows anchored at `CURRENT_TIMESTAMP`.
- **Expected result/shape:** For sql-41 Exercise 1, return 6 rows, one per sold category (`Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, `Sports`); the window values move with the load date because the seed dates are relative to it. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
- **Independent verification:** For sql-41 Exercise 1, confirm 6 rows with unique `category`, `revenue_90d >= revenue_30d` on every row, and `revenue_per_order_30d` within 0.01 of `revenue_30d / orders_30d`; recompute `Books` with a plain `WHERE p.category = 'Books' AND o.order_date >= CURRENT_TIMESTAMP - interval '30 days'` query and match `revenue_30d`, `orders_30d`, and `units_30d`; then, in a rolled-back transaction, insert a product in a new `Garden` category and confirm the result still has 6 rows, because categories come from order lines.
- **Intermediate relation check:** Print `lines` with `SELECT count(*), count(DISTINCT order_id) FROM lines`. It is at order-line grain, so the first count is larger than the second; that gap is the fanout `COUNT(DISTINCT order_id)` protects `orders_30d` against.
- **Clause check:** Each of the six measures carries its own window in `FILTER`, and there is no `WHERE`, so a category with no recent orders still gets a row. `NULLIF` in the last column turns a zero recent-order count into `NULL` instead of a division error.
- **Alternative/trade-off:** Moving `WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'` into `lines` would shrink the scan, but it would silently drop any category whose lines are all older than 90 days. Keep the window in `FILTER` when every category must appear.
- **Edge case:** If `units_30d` is `NULL` for a category, `orders_30d` must be `0` and `revenue_per_order_30d` must be `NULL`; seeing `0` in the money columns means someone added `COALESCE` without deciding the policy.

## Exercise 2: Top five product names per country

Rank at `(country, product)` grain before aggregating names. This avoids the
common mistake of applying `LIMIT 5` to the entire result instead of five
products per country.

```sql
SET search_path TO training, public;

WITH product_revenue AS (
  SELECT
    c.country,
    p.product_id,
    p.name,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    customers c
    JOIN orders o USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
  GROUP BY
    c.country, p.product_id, p.name
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC,
      product_id) AS product_rank
  FROM
    product_revenue
)
SELECT
  country,
  string_agg(name, ', ' ORDER BY product_rank) AS top_five_products
FROM
  ranked
WHERE
  product_rank <= 5
GROUP BY
  country
ORDER BY
  country;
```

Expected shape: one row per represented country and one comma-separated label
ordered from highest to lowest product revenue.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 2, join `customers`, `orders`, `order_items`, and `products`, sum line revenue at (`country`, `product_id`, `name`) grain in `product_revenue`, rank it with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)` in `ranked`, and keep ranks 1 to 5 for `string_agg`.
- **Expected result/shape:** For sql-41 Exercise 2, return 7 rows, one per country with orders (`AU`, `CA`, `DE`, `FR`, `GB`, `IN`, `US`; `BR` has no orders), each listing exactly five names in rank order, for example `AU` = `Product 238, Product 207, Product 251, Product 261, Product 243`. The final columns are `country` and `top_five_products`. The final order is `country`.
- **Independent verification:** For sql-41 Exercise 2, rerun `ranked` alone with `WHERE country = 'AU' AND product_rank <= 5` and match the five `AU` names in order; confirm every country bought 275 distinct products, so no list is short; then add `WHERE o.order_id = 1` inside `product_revenue` and confirm one row whose list has only the order's two products, `Product 79, Product 48`, with no padding.
- **Intermediate relation check:** For sql-41 Exercise 2, run `product_revenue` and confirm (`country`, `product_id`) is unique. Run `ranked` and confirm ranks restart at one inside every country before filtering to ranks 1-5.
- **Clause check:** For sql-41 Exercise 2, the joins first produce order-line rows, the first `GROUP BY` reduces them to one row per country/product, `ROW_NUMBER` ranks without changing that row count, `WHERE product_rank <= 5` keeps the local top five, and the final `GROUP BY country` builds one ordered label per country.
- **Alternative/trade-off:** `array_to_string((array_agg(name ORDER BY revenue DESC, product_id))[1:5], ', ')` over `product_revenue` skips the `ranked` CTE and matches all seven labels on this fixture. It still sorts every product a country bought (275 in each of the seven) before slicing, and the rank is no longer a column you can print to check ties, so the `ROW_NUMBER` form is easier to verify.
- **Edge case:** If two products in one country have identical revenue, `product_id` decides which one is ranked first, so rerunning the query never swaps them inside `top_five_products`.

## Reasoning, safety, and pitfalls

- Compute line revenue from `order_items`; do not multiply `orders.total_amount`
  after joining to items because that would repeat the order total per line.
- Use `DISTINCT` inside counts when the input is at line-item grain.
- Add a deterministic tie-breaker (`product_id`) to `ROW_NUMBER`.
- Both answers are read-only and safe to run repeatedly.

## Exercise 3: Compare grouping sets and CUBE

The `CUBE(country, category)` answer emits detail, both one-dimensional
subtotals, and the grand total. `GROUPING(country, category)` identifies each
generated level.

```sql
WITH lines AS (
  SELECT
    c.country,
    p.category,
    oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
  FROM
    orders o
    JOIN customers c USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
),
cube_rows AS (
  SELECT
    country,
    category,
    SUM(revenue) AS revenue,
    GROUPING (country,
    category) AS grouping_mask
  FROM
    lines
  GROUP BY
    CUBE (country,
    category))
  SELECT
    country,
    category,
    revenue,
    grouping_mask,
    CASE grouping_mask
    WHEN 0 THEN
      'detail'
    WHEN 1 THEN
      'country subtotal'
    WHEN 2 THEN
      'category subtotal'
    WHEN 3 THEN
      'grand total'
    END AS grouping_level
  FROM
    cube_rows
  ORDER BY
    grouping_mask,
    country,
    category;
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

- **Inputs/evidence:** For sql-41 Exercise 3, build a `lines` CTE of order-line revenue with each line's customer `country` and product `category` (13,085 rows), then aggregate it with `GROUP BY CUBE (country, category)` and label `GROUPING(country, category)` as `grouping_mask` and `grouping_level`.
- **Expected result/shape:** For sql-41 Exercise 3, return 56 rows: 42 detail rows (7 countries times 6 categories, mask `0`), 7 country subtotals (mask `1`), 6 category subtotals (mask `2`), and one grand total (mask `3`) of 2355647.1235. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
- **Independent verification:** For sql-41 Exercise 3, count rows per `grouping_mask` (42, 7, 6, 1) and confirm that `revenue` sums to 2355647.1235 within each mask; check one cell such as `AU`/`Apparel` = 54277.4215 against a plain filtered sum; then replace `CUBE` with `GROUPING SETS ((country), (category), ())` and confirm 14 rows, because the 42 country-by-category detail rows are the level that list omits.
- **Intermediate relation check:** For sql-41 Exercise 3, confirm `lines` is at order-line grain. In `cube_rows`, confirm (`grouping_mask`, `country`, `category`) identifies a row at its applicable level and inspect counts separately for masks 0, 1, 2, and 3.
- **Clause check:** For sql-41 Exercise 3, `FROM`/`JOIN` establishes line grain, `GROUP BY CUBE` emits four aggregate grains, `GROUPING` labels which dimensions were omitted, the outer `SELECT` translates the mask, and `ORDER BY` presents detail before progressively broader totals.
- **Alternative/trade-off:** Spell out `GROUPING SETS ((country, category), (country), (category), ())` when the requested levels should be especially visible. Use `CUBE` when all combinations are intended. Omitting `(country, category)` would omit detail.
- **Edge case:** A stored `NULL` in a dimension and a generated subtotal marker can print the same dimension value. Use `grouping_mask`, not `country IS NULL` or `category IS NULL`, to identify the row's grain.

## Exercise 4: State metric populations with FILTER

Each status/time population appears beside its aggregate, making several
country metrics readable without repeating the whole grouped relation.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 4, join `orders` to `customers` (4,362 order rows), group by `c.country`, and compute every measure with `COUNT` or `SUM` plus `FILTER (WHERE o.status = ...)` over the same rows; `status` has five values (`placed`, `paid`, `shipped`, `delivered`, `returned`).
- **Expected result/shape:** For sql-41 Exercise 4, return 7 rows, one per country with orders; `BR` is absent because none of its 62 customers ordered. `AU` shows 613 orders, 123 paid orders, 66338.06 paid revenue, 66707.95 returned revenue, and 62 customers. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
- **Independent verification:** For sql-41 Exercise 4, confirm `orders` sums to 4362, `paid_orders` to 872, and `paid_revenue` to 478068.36, matching `SELECT count(*), sum(total_amount) FROM orders WHERE status = 'paid'`; then rewrite the join as `customers LEFT JOIN orders` and observe that `BR` appears with `orders = 1` from `COUNT(*)` but `customers = 0`, so a left-join version must count `o.order_id`.
- **Intermediate relation check:** There is no CTE here. Run `SELECT count(*) FROM orders o JOIN customers c USING (customer_id)` and compare it with `SELECT count(*) FROM orders`; they match because each order has exactly one customer, so `COUNT(*)` counts orders and `SUM(o.total_amount)` adds each order once.
- **Clause check:** `GROUP BY c.country` sets the grain, and every status split lives in a `FILTER` beside its own aggregate: `COUNT(*) FILTER (WHERE o.status = 'paid')` for `paid_orders` and the matching `SUM(o.total_amount)` filters for the two revenue columns. `COUNT(DISTINCT o.customer_id)` counts each customer once, however many orders they placed.
- **Alternative/trade-off:** `SUM(CASE WHEN o.status = 'paid' THEN o.total_amount END)` returns the same values, including `NULL` for a country with no paid orders, but the population is buried inside each expression. `FILTER` keeps the condition visible next to the column it defines.
- **Edge case:** A country with orders but none `returned` would print `NULL` for `returned_revenue` while `orders` stays positive; that is "no returned orders", not "returned orders worth zero". In the course data all seven countries have between 122 and 127 returned orders out of 613 to 634, so you only see that `NULL` if you narrow the input, for example to one week.

## Exercise 5: Distinguish stored and generated NULLs

`GROUPING(country)` is one only for the generated subtotal. A stored NULL, if
allowed by the model, keeps grouping flag zero and receives a different label.

```sql
WITH country_input AS (
  SELECT
    country
  FROM
    customers
  UNION ALL
  SELECT
    NULL::text
)
SELECT
  CASE WHEN GROUPING (country) = 1 THEN
    'ALL COUNTRIES'
  ELSE
    COALESCE(country, '(stored null)')
  END AS country_label,
  GROUPING (country) AS is_subtotal,
  COUNT(*) AS customers
FROM
  country_input
GROUP BY
  GROUPING SETS ((country),
    ())
ORDER BY
  is_subtotal,
  country_label;
```

The extra `NULL::text` is input data inside a CTE; it is not passed to
`GROUPING`. PostgreSQL evaluates `GROUPING(country)` for each output group:
the stored-NULL detail group receives `0`, and the generated grand total
receives `1`. The labels branch on that flag before using `COALESCE`.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 5, read `customers.country` (500 rows) and append one controlled `NULL::text` row with `UNION ALL` in a `country_input` CTE; group by `GROUPING SETS ((country), ())`, and use `GROUPING(country)` to build `country_label`, `is_subtotal`, and `customers`.
- **Expected result/shape:** For sql-41 Exercise 5, return 10 rows: 8 country rows and one `(stored null)` row with 1 customer, all with `is_subtotal = 0`, plus one `ALL COUNTRIES` row with `is_subtotal = 1` and 501 customers. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
- **Independent verification:** For sql-41 Exercise 5, confirm exactly one row has `is_subtotal = 1` and that the nine detail `customers` values sum to its 501; confirm `(stored null)` carries `is_subtotal = 0`; then remove the `UNION ALL` branch and confirm 9 rows with a 500 total. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
- **Intermediate relation check:** For sql-41 Exercise 5, first count `country_input` and confirm it has exactly one more row than `customers`. Then inspect detail groups (`is_subtotal = 0`) separately from the one grand-total group (`is_subtotal = 1`).
- **Clause check:** For sql-41 Exercise 5, `UNION ALL` appends the controlled stored NULL, `GROUPING SETS` creates detail and grand-total grains, `GROUPING(country)` distinguishes them, and `CASE` assigns non-overlapping labels.
- **Alternative/trade-off:** On a production table that already permits and contains stored NULL countries, omit the fixture row. Keep the `GROUPING`-first label logic unchanged.
- **Edge case:** Never write `GROUPING(NULL)` to simulate data. `GROUPING` must refer to an expression in the current grouping specification; put a NULL in the input relation to test stored-NULL behavior.

## Exercise 6: Return a typed empty collection

`array_agg` over no qualifying inputs is NULL. The answer uses
`COALESCE(..., '{}'::text[])`; the explicit type must match the aggregate type.

```sql
SELECT
  COALESCE(array_agg(email) FILTER (WHERE false), '{}'::text[]) AS empty_email_array
FROM
  customers;
```

There is no `GROUP BY`, so the aggregate query returns one scalar row even
though no input qualifies for the aggregate. `array_agg` first produces SQL
`NULL`; `COALESCE` then substitutes an empty array of the same `text[]` type.
An empty array is a real, non-NULL value whose `cardinality` is zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)`, which sees all 500 rows but aggregates none, and wrap it in `COALESCE(..., '{}'::text[])` so both branches are `text[]`.
- **Expected result/shape:** For sql-41 Exercise 6, return exactly one row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
- **Independent verification:** For sql-41 Exercise 6, select the uncoalesced filtered `array_agg` and confirm `IS NULL` is true, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`; then replace the fallback with a bare `ARRAY[]` and confirm the error `cannot determine type of empty array`.
- **Intermediate relation check:** For sql-41 Exercise 6, run `SELECT array_agg(email) FILTER (WHERE false) FROM customers` first and observe one row containing SQL NULL. Then add `COALESCE` and observe one row containing `{}`.
- **Clause check:** For sql-41 Exercise 6, `FROM customers` supplies the input relation, aggregate `FILTER` gives `array_agg` zero qualifying rows, the aggregate still creates one scalar group, and `SELECT` applies the typed fallback.
- **Alternative/trade-off:** Return SQL NULL when “not computed” is materially different from “computed and empty.” Return an empty array when downstream callers should be able to iterate without a NULL branch.
- **Edge case:** A table with zero rows behaves the same for this scalar aggregate: one output row, NULL before `COALESCE`, and an empty `text[]` afterwards.
