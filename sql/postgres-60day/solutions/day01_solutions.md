# Day 01 solutions: SELECT, WHERE, ORDER BY, LIMIT/OFFSET

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Every answer below is a single `SELECT` on one table (`orders`, `products` or `customers`), so the work is in the predicate and the sort, not in joins. After your own attempt, run the executable companion:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day01_solutions.sql
```

It wraps all six answers in one `BEGIN`/`ROLLBACK` and assumes `SET search_path TO training, public;`, which is why the snippets say `orders` rather than `training.orders`. Exercises 2 and 3 compare against `CURRENT_TIMESTAMP`, so their row counts shrink as the fixture ages; the counts quoted here are from a fresh load. These answers align one-for-one with [day01_select_where_orderby.sql](../day01_select_where_orderby.sql). The general [solution reading steps](../../STUDY-GUIDE.md#read-a-solution) and the [logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order) apply to every query here.

## Reading contract

- **Focus:** Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
- **Assumptions:** Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
- **Primary pitfall:** Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** List the 20 newest orders with customer ID and total amount.

**Reasoning:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.

**Clause-by-clause reading:**

- `FROM orders AS o`: one row per order. Nothing filters, so all 4,362 orders are candidates.
- `ORDER BY o.order_date DESC`: newest first. Order IDs were handed out customer by customer, so the newest order is not the highest ID.
- `o.order_id DESC`: the unique final key. With it, the 20 rows and their positions are fully determined.
- `LIMIT 20`: applied after the sort, so it keeps the 20 latest orders.
- `SELECT`: four stored columns and no expressions.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  o.order_date
FROM
  orders AS o
ORDER BY
  o.order_date DESC,
  o.order_id DESC
LIMIT 20;
```

**Expected shape:** At most 20 rows; one row per order, newest first.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 1, read the 4,362 `orders` rows, one per `order_id`; `order_date` is `NOT NULL` and holds 4,362 distinct timestamps, so `order_id` only breaks future ties. Project `order_id`, `customer_id`, `total_amount`, and `order_date`.
- **Expected result/shape:** For sql-01 Exercise 1, return exactly 20 rows, one per order, newest first; on a freshly loaded fixture the list starts with order 2258 and ends with order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-01 Exercise 1, confirm 20 rows and 20 distinct `order_id` values, then compare them with `SELECT order_id FROM orders ORDER BY order_date DESC, order_id DESC LIMIT 20`. Inside a rolled-back transaction, copy order 2258's `order_date` onto order 1; the first rows must become 2258, 1, 745, showing the higher ID wins the tie.
- **Print the input first:** `SELECT count(*), count(DISTINCT order_date) FROM orders;` returns 4,362 twice, so the timestamp alone already orders every row today. The ID key is insurance for future data, not a fix for a current tie.
- **Where the logic lives:** only `ORDER BY` decides which 20 rows appear. Delete it and the query still returns 20 rows, but on a fresh load they are simply orders 1 to 20, the first rows the scan reaches.
- **Alternative:** `ORDER BY o.order_date DESC NULLS LAST, o.order_id DESC` spells out NULL placement. `order_date` is declared `NOT NULL`, so it changes nothing here and the shorter form is clearer.
- **Edge case:** inside a transaction, copy the latest `order_date` onto order 1. The two tied orders must then appear with the higher ID first; roll back afterwards.

## Exercise 2: Query writing

**Prompt:** Find the 10 most expensive products created in the last 90 days.

**Reasoning:** Filter the timestamp directly, then sort by price and a stable product key.

**Clause-by-clause reading:**

- `WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'`: compares the stored timestamp with a moving cutoff. On a fresh load only products 276 to 300 are that recent.
- `ORDER BY p.price DESC, p.product_id`: price ranks the survivors and the product ID settles equal prices.
- `LIMIT 10`: keeps the ten most expensive of those recent products.
- `SELECT`: shows `created_at` so a reader can see that every row is inside the window.

```sql
SELECT
  p.product_id,
  p.name,
  p.price,
  p.created_at
FROM
  products AS p
WHERE
  p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
ORDER BY
  p.price DESC,
  p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 product rows; every row is in the 90-day window.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 2, read `products` (300 rows, 300 distinct prices); 25 of them have `created_at` inside the last 90 days, priced from 112.12 to 121.00. Project `product_id`, `name`, `price`, and `created_at`.
- **Expected result/shape:** For sql-01 Exercise 2, return exactly 10 of those 25 recent products, highest price first: product 300 at 121.00 down to product 291 at 117.67. The final columns are `product_id`, `name`, `price`, and `created_at`. The final order is `p.price DESC, p.product_id`.
- **Independent verification:** For sql-01 Exercise 2, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'` returns 25 and that every returned `created_at` passes that test. Inside a rolled-back transaction, set product 299's price to 121.00; the first two rows must then be 299 and 300, because `product_id` ascending breaks the price tie.
- **Print the window first:** `SELECT count(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days';` returns 25 on a fresh load. If an aged fixture drops that count below 10, the answer correctly returns fewer than ten rows.
- **Where the logic lives:** the filter and the sort answer different questions. Prices in this fixture are `10 + 0.37 * product_id`, so they rise with the ID, and the top ten recent products are 300 down to 291.
- **Alternative:** `WHERE p.created_at::date >= CURRENT_DATE - 90` reads naturally but compares calendar days, which admits products from earlier in the boundary day. Casting the column also stops a plain index on `created_at` from helping.
- **Edge case:** a product created exactly 90 days before `CURRENT_TIMESTAMP` is kept because the predicate uses `>=`; one created a microsecond earlier is excluded.

## Exercise 3: Query writing

**Prompt:** Show customers from GB or DE created in the last year, newest first.

**Reasoning:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.

**Clause-by-clause reading:**

- `WHERE c.country IN ('GB', 'DE')`: shorthand for two equality tests joined by `OR`.
- `AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'`: both conditions must hold for a customer to stay.
- `ORDER BY c.created_at DESC, c.customer_id`: newest first, with the ascending ID as the tie-breaker. Exercise 1 breaks ties with a descending ID instead; either direction works as long as the key is unique.
- No `LIMIT`: the prompt asks for every GB and DE customer in the window.

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  c.created_at
FROM
  customers AS c
WHERE
  c.country IN ('GB', 'DE')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'
ORDER BY
  c.created_at DESC,
  c.customer_id;
```

**Expected shape:** Only GB/DE customers from the declared window.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 3, read `customers` (500 rows); 119 were created in the last year, of which 15 are `GB` and 14 are `DE`. Project `customer_id`, `full_name`, `country`, and `created_at`.
- **Expected result/shape:** For sql-01 Exercise 3, return 29 rows on a freshly loaded fixture, all `GB` or `DE` and all created within one year, newest first starting with customer 172. The final columns are `customer_id`, `full_name`, `country`, and `created_at`. The final order is `c.created_at DESC, c.customer_id`.
- **Independent verification:** For sql-01 Exercise 3, group the one-year window by `country` and confirm `GB` 15 plus `DE` 14 equals the 29 returned rows; grouping the output by `country` must show only those two values. The 29 rows carry 29 distinct `created_at` values, so `customer_id` only matters if a tie is added.
- **Print the pieces separately:** count GB and DE customers without the date condition (126, 63 of each), then with it (29 on a fresh load: 15 GB and 14 DE). The gap shows the date predicate is doing work.
- **Where the logic lives:** the `AND`. Writing `country = 'GB' OR country = 'DE' AND created_at >= ...` without parentheses binds `AND` first and returns every GB customer regardless of date.
- **Alternative:** `c.country = ANY (ARRAY['GB', 'DE'])` is equivalent and convenient when the country list arrives as a parameter.
- **Edge case:** `country` is `NOT NULL`, but it is case-sensitive text. A row stored as `gb` would be silently excluded by `IN ('GB', 'DE')`.

## Exercise 4: Prediction

**Prompt:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.

**Reasoning:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.

**Clause-by-clause reading:**

- `COUNT(*) FILTER (WHERE c.email IS NULL)`: counts customers whose email is missing.
- `COUNT(*) FILTER (WHERE c.email IS NOT NULL)`: counts the rest.
- `COUNT(*)`: every customer, the control total for the other two.
- No `GROUP BY`, so the whole table collapses into one summary row.

```sql
SELECT
  COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_count,
  COUNT(*) FILTER (WHERE c.email IS NOT NULL) AS present_email_count,
  COUNT(*) AS customer_count
FROM
  customers AS c;
```

**Expected shape:** Exactly one summary row with counts whose sum equals all customers.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 4, read all 500 `customers` rows; `email` is nullable but currently filled on every row. The query returns counts only, so no customer key appears.
- **Expected result/shape:** For sql-01 Exercise 4, return exactly one row: `missing_email_count` 0, `present_email_count` 500, `customer_count` 500. The final columns are `missing_email_count`, `present_email_count`, and `customer_count`.
- **Independent verification:** For sql-01 Exercise 4, confirm 0 + 500 equals `customer_count` and matches `SELECT COUNT(*) FROM customers`. Inside a rolled-back transaction, set customer 1's `email` to `NULL` and rerun; the counts must become 1, 499, and 500, proving `COUNT(email)` skips the `NULL` while `COUNT(*)` keeps the row.
- **Run the broken form first:** `SELECT count(*) FROM customers WHERE email = NULL;` returns 0, and so does `email <> NULL`, because neither comparison is ever true. That is the prediction the prompt asks for.
- **Where the logic lives:** the `IS NULL` and `IS NOT NULL` tests inside `FILTER`. On this fixture the row reads 0 missing, 500 present, 500 total.
- **Alternative:** `COUNT(c.email)` counts non-NULL emails directly, and `COUNT(*) - COUNT(c.email)` gives the missing number. It is shorter, but the `FILTER` form states each rule in words a reviewer can check.
- **Edge case:** an empty string is not NULL. Inside a transaction, set one email to `''` and another to NULL; only the second moves into `missing_email_count`.

## Exercise 5: Debugging

**Prompt:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.

**Reasoning:** Define the business ranking first; use a unique final key for tied prices.

**Clause-by-clause reading:**

- `ORDER BY p.price DESC, p.product_id`: the repair. It defines "top" as the highest price and uses the product ID for equal prices.
- `LIMIT 10`: now cuts a ranked list instead of an arbitrary one.
- `SELECT`: three stored columns, enough to see the ranking.

```sql
SELECT
  p.product_id,
  p.name,
  p.price
FROM
  products AS p
ORDER BY
  p.price DESC,
  p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 rows, highest prices first, stable across repeated runs on unchanged data.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 5, read all 300 `products` rows; every price is distinct, from product 1 up to product 300 at 121.00. Project `product_id`, `name`, and `price`.
- **Expected result/shape:** For sql-01 Exercise 5, return exactly 10 rows, products 300 down to 291 with prices 121.00 down to 117.67, identical on every rerun. The final columns are `product_id`, `name`, and `price`. The final order is `p.price DESC, p.product_id`.
- **Independent verification:** For sql-01 Exercise 5, confirm 10 distinct `product_id` values and that `SELECT COUNT(DISTINCT price) FROM products` returns 300, so the current fixture has no price tie. Inside a rolled-back transaction, set product 299's price to 121.00; the top three must read 299, 300, 298 on every run.
- **Compare broken and fixed:** `SELECT product_id, name, price FROM products LIMIT 10;` returns products 1 to 10 at 10.37 to 13.70, the cheapest rows, only because that is the physical order of a freshly loaded table. The repaired query returns products 300 down to 291 (121.00 to 117.67).
- **Why the original is nondeterministic:** without `ORDER BY`, SQL promises no row order. Scan order matches insertion order today, but an update, a vacuum or a parallel plan can change which ten rows arrive first.
- **Alternative:** `FETCH FIRST 10 ROWS ONLY` is the standard spelling of `LIMIT 10`. `FETCH FIRST 10 ROWS WITH TIES` would return extra rows if the tenth price were shared, which breaks the at-most-ten contract.
- **Edge case:** prices are unique in this fixture, so `p.product_id` never decides a position. Tie two prices inside a transaction to watch the lower ID win.

## Exercise 6: Extension

**Prompt:** Return the second page of 10 newest orders using the same deterministic order, LIMIT 10 and OFFSET 10.

**Reasoning:** A page is a bounded segment of a defined order. Start from the
same order as page one. The order timestamp alone can tie, so include the unique
order ID. On an unchanged fixture, skipping exactly ten rows and keeping ten
more produces the second page.

**Clause-by-clause reading:**

- `FROM orders AS o` supplies one row per order.
- `SELECT` keeps the order identity, customer identity, amount and timestamp.
- `ORDER BY o.order_date DESC, o.order_id DESC` defines a unique newest-first order.
- `OFFSET 10` skips ten rows in that order.
- `LIMIT 10` caps the rows remaining after the skip.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  o.order_date
FROM
  orders AS o
ORDER BY
  o.order_date DESC,
  o.order_id DESC
LIMIT 10 OFFSET 10;
```

**Expected shape:** At most 10 rows, one row per order, equal to positions 11 through 20 of the unchanged ordered input. The projected columns remain `order_id`,
`customer_id`, `total_amount` and `order_date`; pagination does not aggregate
orders or change what an output row means.

### Reasoning and verification

- **Inputs/evidence:** For sql-01 Exercise 6, read the 4,362 `orders` rows at one row per `order_id`, sorted by the Exercise 1 key, and compare pages only on an unchanged fixture.
- **Expected result/shape:** For sql-01 Exercise 6, return 10 rows equal to positions 11 through 20 of the ordered input, one row per `order_id`; on a freshly loaded fixture the page runs from order 1500 to order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Verify:** For sql-01 Exercise 6, list the first 20 ordered IDs (2258 through 743) and confirm the page equals the last 10 of them, from 1500 to 743, with no ID shared with page one (2258 through 3014).
- **Uniqueness and overlap:** Check that no order ID repeats within the page or appears on both pages. When fewer than twenty source rows exist, the second page is shorter or empty.
- **Tie case:** Give two orders equal timestamps and different IDs. The ID tie-breaker still fixes their order.
- **Alternative/trade-off:** An offset is easy to reason about for this stable fixture. Large offsets require the database to find and discard preceding rows. Changes between page requests can also shift positions. The later `sql-scale-01` workshop teaches keyset cursors after their prerequisites.

No joins, subqueries or CTEs are needed to express this first pagination task.
Those mechanisms are introduced in their own lessons.

## Final self-check

- Why can the worked margin query sort by `gross_margin` but not filter on it, and how would you filter on margin instead?
- If you delete `ORDER BY` from Exercise 1, which 20 orders does your copy print, and why is that not a promise?
- What does `email = NULL` return, and which column in Exercise 4 proves the two counts add up to 500?
- Does page two from Exercise 6 share any `order_id` with page one?
- Does the companion transcript end with `ROLLBACK` and no `ERROR`?
