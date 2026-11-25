# Day 55 Solutions: BI Drill-down and Subtotals


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day55_solutions.sql
```

Everything here reads course tables only. Compare the 50 versus 56 count, the
mask values and the top-five row counts before the revenue figures; the
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read each query in the
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
In this lesson the decisive clause is almost always `GROUP BY`: plain columns
give one grain, `ROLLUP` gives a hierarchy of grains, `CUBE` gives every
combination and `GROUPING SETS` lists them by hand. Whenever several grains
share one result, look for the `GROUPING(...)` expression in the `SELECT` list
that labels them, and check that the `ORDER BY` uses it.

The two worked exercises compare `ROLLUP` and `CUBE`, then add order status to
a country/category/product top-five drill-down; Exercises 3 to 6 label levels,
cap the drill-down at exactly five rows and protect real unknown members. See
[`day55_solutions.sql`](day55_solutions.sql).

## Exercise 1: Compare row counts

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT
    c.country,
    p.category,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM
    orders o
    JOIN customers c USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
),
rollup_rows AS (
  SELECT
    country,
    category,
    SUM(revenue) AS revenue
  FROM
    line
  GROUP BY
    ROLLUP (country,
    category)
),
cube_rows AS (
SELECT
  country,
  category,
  SUM(revenue) AS revenue
  FROM
    line
  GROUP BY
    CUBE (country,
    category))
  SELECT
    (
      SELECT
        COUNT(*)
      FROM
        rollup_rows) AS rollup_row_count,
  (
    SELECT
      COUNT(*)
    FROM
      cube_rows) AS cube_row_count;
```

Expected shape: one comparison row. `CUBE(country, category)` adds category-only
subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count
is greater on this seed.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 1, join `orders`, `customers`, `order_items`, and `products` into one revenue line per order item (13,085 lines carrying `country` and `category`), group those lines once with `ROLLUP (country, category)` and once with `CUBE (country, category)`, and count the rows each grouping produces.
- **Expected result/shape:** For sql-55 Exercise 1, expected output: one row with `rollup_row_count` 50 and `cube_row_count` 56. Both share the 42 country and category detail rows, the 7 country subtotals, and the grand total; the 6 extra `CUBE` rows are the category-only subtotals. BR has no orders, so it appears in neither grouping.
- **Independent verification:** For sql-55 Exercise 1, rebuild both counts from distinct values: 42 distinct (country, category) pairs plus 7 countries plus 1 total gives 50, and adding the 6 categories gives 56. In a rolled-back transaction, give BR customer 8 one order with a single Apparel line: both counts rise by 2 (52 and 58), one BR detail row and one BR subtotal, while the category-only subtotal count stays 6.
- **Intermediate relation check:** Run `line` alone and confirm it has one row per order line, then run `rollup_rows` and `cube_rows` separately. On the course data they return 50 and 56 rows: 42 detail pairs, 7 country subtotals and 1 grand total in both, plus 6 category-only subtotals in the cube.
- **Clause check:** The only difference between the two CTEs is `ROLLUP` versus `CUBE` in `GROUP BY`. The outer `SELECT` has no `FROM` of its own; two scalar subqueries each count one CTE, which is why the result is a single row with two columns.
- **Alternative/trade-off:** `SELECT 'rollup', count(*) FROM rollup_rows UNION ALL SELECT 'cube', count(*) FROM cube_rows` gives the same numbers as two labeled rows. It is easier to extend to more variants, but it no longer matches the one-row, two-column contract.
- **Edge case:** If a new country appeared with orders in only one category, the rollup would gain two rows (detail and country subtotal) and the cube would gain the same two, because its category subtotal already exists.

## Exercise 2: Status-aware top five

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT
    c.country,
    p.category,
    o.status,
    p.product_id,
    p.name,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM
    orders o
    JOIN customers c USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
),
product_revenue AS (
  SELECT
    country,
    category,
    status,
    product_id,
    name,
    SUM(revenue) AS revenue
  FROM
    line
  GROUP BY
    country,
    category,
    status,
    product_id,
    name
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY country,
      category,
      status ORDER BY revenue DESC,
      product_id) AS product_rank
  FROM
    product_revenue
)
SELECT
  country,
  category,
  status,
  product_id,
  name,
  ROUND(revenue, 2) AS revenue,
  product_rank
FROM
  ranked
WHERE
  product_rank <= 5
ORDER BY
  country,
  category,
  status,
  product_rank;
```

Expected grain: up to five rows per `(country, category, status)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 2, sum line revenue (`unit_price * quantity * (1 - discount)`) per `country`, `category`, `status`, `product_id`, and `name` (7,566 product rows), then number the products inside each (country, category, status) group with `ROW_NUMBER()` ordered by `revenue DESC, product_id` and keep numbers 1 to 5.
- **Expected result/shape:** For sql-55 Exercise 2, expected output: 1,050 rows, exactly five for each of the 210 (country, category, status) groups (7 countries, 6 categories, 5 statuses, each group holding 30 to 42 products), with columns `country`, `category`, `status`, `product_id`, `name`, `revenue` (rounded to 2 places), and `product_rank`. The final order is `country, category, status, product_rank`; the first group is AU, Apparel, `delivered`, led by product 241 at 793.36.
- **Independent verification:** For sql-55 Exercise 2, check that AU, Apparel, `delivered` lists products 241, 223, 163, 121, and 97 (793.36 down to 727.36), with product 109 sixth at 651.77, and that no (country, category, status, `product_id`) repeats. In a rolled-back transaction, add a 150.00 line for product 109 to AU order 47 (delivered): product 109 moves to rank 1 at 801.77, product 97 drops out, and the group still returns five rows.
- **Intermediate relation check:** `line` is at order-line grain; `product_revenue` must be unique on (country, category, status, product_id), which you can prove by comparing its `count(*)` with a `count(DISTINCT (country, category, status, product_id))`. `ranked` keeps that row count and only adds `product_rank`.
- **Clause check:** `PARTITION BY country, category, status` restarts the numbering for each of the 210 groups, and `ORDER BY revenue DESC, product_id` breaks revenue ties by id. The outer `WHERE product_rank <= 5` then keeps at most five rows per group.
- **Alternative/trade-off:** A `LATERAL` subquery with `ORDER BY revenue DESC, product_id LIMIT 5` per (country, category, status) gives the same rows. It reads naturally as "top five for each group" but needs a separate list of groups to drive it.
- **Edge case:** A status group with fewer than five sold products would return fewer rows rather than padding; on this data all 210 groups are full, so the result has exactly 1,050 rows.

## Reasoning, safety, and pitfalls

- `CUBE` grows quickly: three dimensions produce up to eight grouping sets,
  before considering the number of distinct dimension values.
- `NULL` can mean a subtotal or a real null dimension value. Include
  `GROUPING(...)` flags in user-facing subtotal reports when ambiguity exists.
- Aggregate product revenue before ranking.
- `ROW_NUMBER` plus `product_id` yields exactly five deterministic rows when at
  least five products exist; `RANK` can return more because of ties.

## Exercise 3: Enumerate ROLLUP levels

PostgreSQL's `GROUPING(country, category)` returns a bit mask: detail, country
subtotal, and grand total have stable numeric identities.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 3, first write down the grouping sets of `ROLLUP (country, category, month)` (4 sets, from full detail to the grand total) and of `CUBE` on the same columns (8 sets), then run `ROLLUP (country, category)` over the order-item revenue lines and expose `GROUPING (country, category)` as `grouping_mask`.
- **Expected result/shape:** For sql-55 Exercise 3, expected output: 50 rows with columns `country`, `category`, `revenue`, and `grouping_mask`, ordered by `grouping_mask, country, category`: 42 detail rows with mask 0 (AU Apparel 54,277.4215), 7 country subtotals with mask 1 (AU 330,947.6960), and 1 grand total with mask 3 (2,355,647.1235). No row has mask 2, because `ROLLUP` never totals a category across countries.
- **Independent verification:** For sql-55 Exercise 3, count the rows per mask (42, 7, 1) and confirm that the 7 mask 1 rows add up to the mask 3 total of 2,355,647.1235. In a rolled-back transaction, give BR customer 8 one order with a 20.00 Apparel line: the result grows to 52 rows (43 with mask 0, 8 with mask 1), and BR shows 20.0000 at both the detail and subtotal level.
- **Intermediate relation check:** `line` has no `GROUP BY`; it is one row per order line with country, category and unrounded line revenue. Count it, then run the final query without `ORDER BY` and group its output by `grouping_mask`: you should see 42 rows with mask `0`, 7 with mask `1` and 1 with mask `3`, and the mask `0` rows for AU should add up to AU's mask `1` row of 330,947.70.
- **Clause check:** `GROUPING(country, category)` reads the two arguments as bits, country first, so `1` means only category was rolled away and `3` means both were. `ROLLUP (country, category)` never drops country while keeping category, which is why mask `2` cannot appear.
- **Alternative/trade-off:** Writing `GROUPING SETS ((country, category), (country), ())` produces the same 50 rows and makes the hierarchy explicit; `ROLLUP` is the shorter spelling of exactly that list.
- **Edge case:** The grand total row (mask `3`, revenue 2355647.1235) must equal the sum of the 42 detail rows; if it does not, the line revenue was computed differently in the two places. Because `ORDER BY grouping_mask` comes first, the total is the last row, the reverse of Example 1, where `NULLS FIRST` put it on top.

## Exercise 4: Label levels from the bit mask

The display label is derived from that mask, not from `column IS NULL`. This
keeps machine-readable level identity beside human-readable text.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 4, group the same order-item revenue lines with `ROLLUP (country, category)` and return `GROUPING (country, category)` as `level_id`, plus a `CASE` on that same mask that maps 0, 1, and 3 to `level_name` values 'country/category detail', 'country subtotal', and 'grand total'.
- **Expected result/shape:** For sql-55 Exercise 4, expected output: the same 50 rows as Exercise 3 with columns `level_id`, `level_name`, `country`, `category`, and `revenue`, ordered by `level_id, country, category`: 42 rows at level 0, 7 at level 1, and 1 at level 3, and no `NULL` `level_name`.
- **Independent verification:** For sql-55 Exercise 4, count rows per `level_id` and `level_name` (42, 7, 1) and confirm each `level_id` maps to exactly one name. In a rolled-back transaction, run `ALTER TABLE products ALTER COLUMN category DROP NOT NULL` and set product 241's category to `NULL`: level 0 grows to 49 rows, 7 of them with a stored `NULL` category, and all 7 still say 'country/category detail' because the label reads the mask, not the column.
- **Intermediate relation check:** Use the same `line` CTE as Exercise 3 (no payments, so no fan-out) and confirm the 50-row output carries only `level_id` values `0`, `1` and `3`. Then compare it row by row with Exercise 3: the country, category and revenue columns are identical, and only the two label columns at the front are new.
- **Clause check:** The `CASE GROUPING (country, category)` expression maps each mask to a readable `level_name`, while `level_id` keeps the raw mask for code that filters or joins on it. Both come from `GROUPING`, not from testing `country IS NULL`, so a future customer with a stored `NULL` country could never be mislabeled as a subtotal.
- **Alternative/trade-off:** A small `VALUES` lookup of (mask, name) joined on `level_id` would work too and keeps names in one place if several reports share them; the inline `CASE` is simpler for three levels.
- **Edge case:** Switching the `GROUP BY` to `CUBE` would emit six mask `2` rows (category totals across all countries), and this `CASE` has no branch for them, so their `level_name` would be `NULL` and they would sort between the country subtotals and the grand total. Add a `WHEN 2` branch before changing the grouping.

## Exercise 5: Return exactly five products

Revenue aggregates before ranking. `ROW_NUMBER` with `product_id` as final key
limits every partition deterministically even when revenue ties.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 5, sum order-item revenue per `country`, `product_id`, and `name` (1,925 rows, 275 products in each of 7 countries), then number the products inside each country with `ROW_NUMBER()` ordered by `revenue DESC, product_id` as `position` and keep positions 1 to 5.
- **Expected result/shape:** For sql-55 Exercise 5, expected output: 35 rows, one per country and `position` 1 to 5, with columns `country`, `product_id`, `name`, `revenue`, and `position`. The final order is `country, position`; AU starts with product 238 at 3,319.3310, followed by products 207, 251, 261, and 243 (2,692.5745).
- **Independent verification:** For sql-55 Exercise 5, confirm that no (country, `product_id`) repeats and that AU product 233 sits sixth at 2,684.2590. In a rolled-back transaction, add a line for product 233 to AU order 46 with `unit_price` 166.31 and `discount` 0.95 (8.3155): products 233 and 243 tie at 2,692.5745, `RANK() <= 5` now returns 36 rows, and `ROW_NUMBER` still returns 35, giving position 5 to product 233 because it has the lower `product_id`.
- **Intermediate relation check:** `revenue` holds one row per (country, product) and `ranked` adds `position` without changing that count. The final result has 35 rows, five for each of the seven countries with orders. The rows are products, not orders: the columns are `country`, `product_id`, `name`, `revenue` and `position`, and the check for duplicates is on (country, `product_id`).
- **Clause check:** `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)` gives every product a distinct position, so `WHERE position <= 5` can never return six rows even when two products tie on revenue.
- **Alternative/trade-off:** `RANK()` with the same window would keep tied products together but may return more than five rows; choose it only if the report promises "all products at the top five revenue levels".
- **Edge case:** If products 238 and 207 in AU had equal revenue, `ROW_NUMBER` would place 207 first because of the `product_id` tie-breaker, and the order would stay the same on every run.

## Exercise 6: Preserve unknown versus ALL

The stored member label and generated-total flag are separate fields. A real
NULL/unknown member retains flag zero; ALL has flag one.

### Reasoning and verification

- **Inputs/evidence:** For sql-55 Exercise 6, read the 500 `customers` rows and group them with `GROUPING SETS ((country), ())`, returning `GROUPING (country)` as `is_generated_total` and a `display_country` that says 'ALL' only when that flag is 1 and '(unknown member)' for a stored `NULL` country.
- **Expected result/shape:** For sql-55 Exercise 6, expected output: 9 rows with columns `display_country`, `is_generated_total`, and `customers`, ordered by `is_generated_total, display_country`: eight countries including BR (62 or 63 customers each, flag 0), then `ALL` with 500 and flag 1.
- **Independent verification:** For sql-55 Exercise 6, compare each country row with `SELECT country, COUNT(*) FROM customers GROUP BY country` and confirm the eight counts add up to the `ALL` row. `country` is `NOT NULL` (default 'US'), so in a rolled-back transaction run `ALTER TABLE customers ALTER COLUMN country DROP NOT NULL` and insert one customer with a `NULL` country: the result has 10 rows, a '(unknown member)' row with 1 customer and flag 0, and `ALL` at 501.
- **Intermediate relation check:** There is no CTE. Run `SELECT country, count(*) FROM customers GROUP BY country` and confirm eight countries of 62 or 63 customers each, which match the eight detail rows; the `ALL` row should be 500.
- **Clause check:** `GROUPING SETS ((country), ())` asks for the per-country rows plus one total. The `CASE` tests `GROUPING (country) = 1` first, so only the generated total becomes `ALL`, and a stored `NULL` country would fall through to `COALESCE(country, '(unknown member)')`.
- **Alternative/trade-off:** Two queries combined with `UNION ALL`, one grouped and one ungrouped, give the same rows, but you would have to add the `is_generated_total` flag by hand instead of reading it from `GROUPING`.
- **Edge case:** The course customers have no `NULL` country, so `(unknown member)` does not appear today; the column is also `NOT NULL`, so in a transaction run `ALTER TABLE customers ALTER COLUMN country DROP NOT NULL`, insert one customer with `country = NULL`, and it shows up as its own `(unknown member)` detail row with 1 customer and `is_generated_total = 0`, while `ALL` becomes 501.