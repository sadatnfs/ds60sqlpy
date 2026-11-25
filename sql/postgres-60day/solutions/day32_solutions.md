# Day 32: Solutions: Index Fundamentals


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Every answer creates its indexes inside `BEGIN ... ROLLBACK`, so running the
file twice leaves the schema unchanged. Plans will match these notes in
shape and row counts but not in timing. See
[Read a solution](../../STUDY-GUIDE.md#read-a-solution) for the general
approach.

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day32_solutions.sql
```

## How these answers fit together

The first three answers stay on `products`, a 300-row, 3-page table where
each of six categories holds exactly 50 rows. No index can beat reading
three pages, so every plan there is a sequential scan, and the lesson is in
recording that honestly. The fourth and fifth answers move to `payments`
and `customers`, where the index is chosen, and the fifth adds an expression
index whose statistics lag behind it. The sixth leaves indexes aside and
shows that only `ORDER BY` fixes output order.

The executable file runs all six answers in one transaction. It creates
`idx_products_category_solution`, then drops it and creates it again to
plan the same filter without and with the index, then adds the `payments`
and expression indexes. The two Markdown blocks below each open their own transaction and
start with `DROP INDEX IF EXISTS`, so either can be pasted into `psql` on
its own. The learner file is
[day32_index_fundamentals.sql](../day32_index_fundamentals.sql).

## Exercise 1: Index `products(category)` and test a filter

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_solution;

CREATE INDEX idx_products_category_solution ON products (category);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  product_id,
  name,
  price
FROM
  products
WHERE
  category = 'Electronics';

ROLLBACK;
```

Expected plan shape is not guaranteed. The seeded `products` table has only a
few hundred rows and each category is common, so a sequential scan can be
cheaper even though the index is valid.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 1, read `products` (300 rows on 3 pages, six categories of 50), create `idx_products_category_solution` on `category`, and plan `SELECT product_id, name, price ... WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`.
- **Expected result/shape:** For sql-32 Exercise 1, expected output: a `Seq Scan on products` plan with estimated and actual `rows=50`, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; the index exists but is not chosen. The final columns are `product_id`, `name`, and `price`.
- **Independent verification:** For sql-32 Exercise 1, confirm `SELECT COUNT(*) FROM products WHERE category = 'Electronics'` returns 50, the plan's actual rows, and that actual plus removed rows equal 300; then, in the same transaction, `SET LOCAL enable_seqscan = off` and confirm the plan becomes a `Bitmap Index Scan on idx_products_category_solution` with the same 50 rows, and that `category = 'Toys'` keeps the `Seq Scan` with 0 actual rows and 300 removed.

- **Intermediate relation check:** `SELECT COUNT(*) FROM products WHERE category = 'Electronics'` returns 50 of 300 rows, one sixth of the table.
- **Clause check:** `DROP INDEX IF EXISTS` makes the block safe to rerun, `CREATE INDEX` prints its tag, and the plan is `Seq Scan on products` with `Rows Removed by Filter: 250` and `Buffers: shared hit=3`.
- **Alternative/trade-off:** `SET LOCAL enable_seqscan = off` makes PostgreSQL pick a `Bitmap Index Scan` on the new index, at a higher estimated cost. That proves the index is usable, not that it helps.
- **Edge case:** Querying a category with no products, such as `'Garden'`, returns 0 rows; the estimate stays small but the sequential scan still reads all 3 pages.

## Exercise 2: Drop and re-create the index, then compare plans

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_solution;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  product_id,
  name,
  price
FROM
  products
WHERE
  category = 'Electronics';

CREATE INDEX idx_products_category_solution ON products (category);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  product_id,
  name,
  price
FROM
  products
WHERE
  category = 'Electronics';

ROLLBACK;
```

Record node type, estimated rows, actual rows, planning time, execution time,
and buffers for each plan. On this small dataset, “no visible plan change” is a
valid observation, not a failed exercise.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 2, drop `idx_products_category_solution` with `DROP INDEX IF EXISTS`, plan `SELECT product_id, name, price FROM products WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`, re-create the index on `products (category)`, and plan the same query again.
- **Expected result/shape:** For sql-32 Exercise 2, expected output: two plans that are both `Seq Scan on products` with 50 actual rows, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; re-creating the index changes nothing on this 3-page table. The final columns are `product_id`, `name`, and `price`.
- **Independent verification:** For sql-32 Exercise 2, confirm `SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_products_category_solution'` returns 0 after the `DROP` and 1 after the `CREATE`; then run the query once without `EXPLAIN` and confirm it returns the same 50 products as both plans, `product_id` 2 through 296.

- **Intermediate relation check:** Both plans return the same 50 products, `product_id` 2 through 296; compare them with one plain `SELECT` before reading the plans.
- **Clause check:** The block drops Exercise 1's index, plans the query, re-creates the index and plans it again. On this seed both plans are `Seq Scan on products` over 3 buffers; only the planning buffers differ.
- **Alternative/trade-off:** Planning with `EXPLAIN` alone would skip execution and still show whether the index is chosen; `ANALYZE, BUFFERS` adds the 3-page read count that explains why it is not.
- **Edge case:** Two identical plans are the expected outcome here, not a failed experiment. Record them as evidence that the table is too small for this index to matter.

## Pitfalls

- Do not use `SET enable_seqscan = off` as proof that an index is useful; it
  changes the planner's choices instead of demonstrating normal behavior.
- A B-tree handles equality and ordered range predicates, so a hash index is
  rarely needed for a basic equality lookup.
- Index names share a schema namespace, which is why the solution uses unique,
  exercise-specific names.
- Indexes created in the learner script are rolled back at the end of that
  script and are not available on later days.

## Exercise 3: Predict from selectivity

Count each category before reading the plan. The optimizer may prefer a
sequential scan on this compact seed even when the index is valid and usable.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 3, read `products`, count rows per `category` with `GROUP BY category`, then plan `SELECT product_id FROM products WHERE category = 'Electronics'` while the category index from the previous answer still exists.
- **Expected result/shape:** For sql-32 Exercise 3, expected output: exactly 6 frequency rows, `Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, and `Sports`, each with 50 products and listed alphabetically because every count ties; the plan is a `Seq Scan` with 50 actual rows. The final columns are `category`, and `products`. The final order is `products DESC, category`.
- **Independent verification:** For sql-32 Exercise 3, confirm the counts sum to 300 and that `pg_stats.most_common_freqs` for `products.category` shows 0.16666667 for all six values; then, inside `BEGIN ... ROLLBACK`, move 49 `Electronics` rows to `Home`, run `ANALYZE products`, and confirm the frequency query now starts with `Home` at 99 and ends with `Electronics` at 1, while the plan stays a `Seq Scan` with 1 actual row because 3 pages are still cheaper than an index probe.

- **Intermediate relation check:** The frequency query returns six rows, `Apparel`, `Beauty`, `Books`, `Electronics`, `Home` and `Sports`, each with 50 products. Every count ties, so the second sort key, `category`, decides the order and it comes out alphabetical.
- **Clause check:** `GROUP BY category` with `COUNT(*)`, then `ORDER BY products DESC, category`, followed by the same Electronics plan as before.
- **Alternative/trade-off:** `pg_stats.most_common_freqs` for `products.category` shows the planner's own view of these frequencies, about 0.1667 each, without counting rows.
- **Edge case:** Because every category has the same frequency, no category is selective enough to change the plan. A skewed column, where one value is rare, is where an index starts to win.

## Exercise 4: Index a timestamp range

The solution indexes `payment_date` and uses `[start, end)` bounds. Half-open
windows compose cleanly without double-counting a boundary timestamp.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 4, read `payments` (3,836 rows on 29 pages), create `idx_payments_date_solution` on `payment_date`, and plan `SELECT payment_id, amount` for the half-open window `payment_date >= CURRENT_TIMESTAMP - interval '180 days' AND payment_date < CURRENT_TIMESTAMP`.
- **Expected result/shape:** For sql-32 Exercise 4, expected output: a `Bitmap Heap Scan on payments` over a `Bitmap Index Scan on idx_payments_date_solution` with both bounds in the `Index Cond`, 1,340 actual rows on this load, and `Heap Blocks: exact=29`. The final columns are `payment_id`, and `amount`.
- **Independent verification:** For sql-32 Exercise 4, confirm the same window counted without `EXPLAIN` matches the plan's actual rows (1,340 on this load), and that the two adjacent half-open windows of 180 to 90 days and 90 to 0 days ago add up to it (632 + 708); then on `VALUES (timestamp '2026-01-01 00:00:00')` confirm `BETWEEN` places that instant in both one-day windows that meet at midnight, while `>= start AND < end` places it only in the later one.

- **Intermediate relation check:** `payments` has 3,836 rows on 29 pages, and the 180-day window keeps about 1,340 of them. Count them without `EXPLAIN` first.
- **Clause check:** The plan is a `Bitmap Heap Scan on payments` over a `Bitmap Index Scan on idx_payments_date_solution`, with both bounds in the `Index Cond` and `Heap Blocks: exact=29`.
- **Alternative/trade-off:** `BETWEEN start AND end` includes both ends, so two adjacent windows would count a payment at the shared boundary twice. `>= start AND < end` assigns each instant to exactly one window.
- **Edge case:** The bitmap scan visits all 29 heap pages, so it saves almost nothing over a sequential scan on this table. A 7-day window would touch far fewer pages.

## Exercise 5: Match an expression index

An index on `country` does not store `lower(country)`. The solution indexes that
exact expression and repeats it exactly in the predicate.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 5, read `customers` (500 rows, country codes stored in uppercase), create `idx_customers_lower_country_solution` on the expression `lower(country)`, and plan `SELECT customer_id FROM customers WHERE lower(country) = 'us'`.
- **Expected result/shape:** For sql-32 Exercise 5, expected output: a `Bitmap Heap Scan on customers` over a `Bitmap Index Scan on idx_customers_lower_country_solution` with `Index Cond: (lower(country) = 'us'::text)`, an estimate of `rows=2`, and 63 actual rows. The final columns are `customer_id`.
- **Independent verification:** For sql-32 Exercise 5, confirm `COUNT(*)` with `lower(country) = 'us'` and with `country = 'US'` both return 63; then, inside `BEGIN ... ROLLBACK`, show that a plain index on `customers (country)` alone leaves the plan as `Seq Scan on customers` with `Filter: (lower(country) = 'us'::text)`, and that running `ANALYZE customers` after creating the expression index raises its estimate from `rows=2` to `rows=63`.

- **Intermediate relation check:** `SELECT COUNT(*) FROM customers WHERE lower(country) = 'us'` returns 63, the same as `country = 'US'`, because every stored code is uppercase.
- **Clause check:** The plan uses `Bitmap Index Scan on idx_customers_lower_country_solution` with `Index Cond: (lower(country) = 'us'::text)`, but estimates `rows=2` against 63 actual rows.
- **Alternative/trade-off:** If the data is always uppercase, `country = 'US'` with a plain index on `country` is simpler. The expression index is for input you cannot normalize.
- **Edge case:** The `rows=2` estimate is the default guess for an expression without statistics. Run `ANALYZE customers;` after creating the index and the estimate becomes 63, because `ANALYZE` gathers statistics on indexed expressions too.

## Exercise 6: Preserve the ordering contract

The unordered query is intentionally nondeterministic. Only the query with
`ORDER BY country, customer_id` promises reproducible presentation order; an
index's incidental scan order is not a substitute.

### Reasoning and verification

- **Inputs/evidence:** For sql-32 Exercise 6, read `customers` twice with `LIMIT 10`: once with no `ORDER BY`, as a control, and once with `ORDER BY country, customer_id`; no index is created for this answer.
- **Expected result/shape:** For sql-32 Exercise 6, expected output: 10 rows from each query; the unordered control happens to return customers 1 to 10 cycling through `US`, `CA`, `GB`, `DE`, `FR`, `IN`, `AU`, and `BR`, while the ordered query returns the first ten of the 62 `AU` customers, ids 7, 15, 23, 31, 39, 47, 55, 63, 71, and 79. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
- **Independent verification:** For sql-32 Exercise 6, confirm the ordered ids match `SELECT customer_id FROM customers WHERE country = 'AU' ORDER BY customer_id LIMIT 10`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET country = country WHERE customer_id = 1` and confirm the unordered control now returns ids 2 to 11 while the ordered query still returns 7 through 79.

- **Intermediate relation check:** The unordered query happens to return customers 1 to 10, cycling through `US`, `CA`, `GB`, `DE`, `FR`, `IN`, `AU` and `BR`, which is insertion order and nothing more.
- **Clause check:** The ordered query sorts by `country`, then `customer_id`, and returns ten `AU` customers: 7, 15, 23 and so on, every eighth id.
- **Alternative/trade-off:** An index on `(country, customer_id)` could return the ordered rows without a sort, but the `ORDER BY` must stay; the index only makes it cheaper.
- **Edge case:** After an `UPDATE` moves some rows to new pages, the unordered query can return a different ten rows. The ordered one cannot, because `customer_id` breaks every tie.

## When the category index starts to win

The `products` answers keep a sequential scan because the table is three
pages. To see the same index chosen, build a throwaway table 1,000 times
larger inside a transaction, with one rare category added:

```sql
BEGIN;
CREATE TEMP TABLE big_products AS
SELECT
  g AS product_id,
  CASE WHEN g % 1000 = 0 THEN
    'Garden'
  ELSE
    (ARRAY['Apparel', 'Beauty', 'Books', 'Electronics', 'Home', 'Sports'])[1 + g % 6]
  END AS category
FROM
  generate_series(1, 300000) AS g;

CREATE INDEX ON big_products (category);

ANALYZE big_products;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  product_id
FROM
  big_products
WHERE
  category = 'Garden';

ROLLBACK;
```

The table is 1,664 pages. `'Garden'` matches 300 rows, and the bitmap scan
reads 3 index pages plus the 300 heap pages that hold them, about a fifth
of the table. `'Electronics'` matches 50,000 rows; the planner still picks
a bitmap scan, but it touches 1,622 of the 1,664 pages, so almost all of
the saving is in skipping the filter check on the other 250,000 rows. The
same index is a big win for the rare value and a small one for the common
value. That is the selectivity argument from the third answer, made
visible.

## Final self-check

1. Why does `products` keep a sequential scan for every category, while
   `orders` switches to a bitmap scan for a 30-day window?
2. What does `Heap Blocks: exact=29` on `payments` tell you about the value
   of that index for a 180-day window?
3. Why was the expression index estimate `rows=2`, and what single command
   fixes it?
4. Which of these proves an index helps: the `CREATE INDEX` tag, a plan
   with `enable_seqscan = off`, or a plan under normal settings with fewer
   buffers? Why?
