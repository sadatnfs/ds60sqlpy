# Day 42 Solutions: Data Quality and Validation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day42_solutions.sql
```

The file only reads, so it can run as often as you like. Expect seven zero
counts, two catalog rows, and four empty results for the email, total and
promotion checks. The
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Most queries here return nothing on the course data, so judge them by what
they would return: plant one bad row per rule inside a transaction, rerun, and
check that only that rule fires before rolling back.

The goal is to turn scattered checks into one auditable report, then isolate
bad email values. Run the canonical file at
[`day42_solutions.sql`](day42_solutions.sql).

## Exercise 1: Core-table validation report

Each row is a named check and the number of failing records or duplicate groups.
On the deterministic course seed, every count should be zero.

```sql
SET search_path TO training, public;

SELECT
  'customers.null_email' AS check_name,
  COUNT(*) AS failing_rows
FROM
  customers
WHERE
  email IS NULL
UNION ALL
SELECT
  'customers.duplicate_normalized_email',
  COUNT(*)
FROM (
  SELECT
    lower(trim(email))
  FROM
    customers
  GROUP BY
    lower(trim(email))
  HAVING
    COUNT(*) > 1) duplicates
UNION ALL
SELECT
  'orders.negative_total',
  COUNT(*)
FROM
  orders
WHERE
  total_amount < 0
UNION ALL
SELECT
  'orders.orphan_customer',
  COUNT(*)
FROM
  orders o
  LEFT JOIN customers c USING (customer_id)
WHERE
  c.customer_id IS NULL
UNION ALL
SELECT
  'order_items.orphan_order_or_product',
  COUNT(*)
FROM
  order_items oi
  LEFT JOIN orders o USING (order_id)
  LEFT JOIN products p USING (product_id)
WHERE
  o.order_id IS NULL
  OR p.product_id IS NULL
UNION ALL
SELECT
  'order_items.invalid_quantity_or_discount',
  COUNT(*)
FROM
  order_items
WHERE
  quantity <= 0
  OR discount NOT BETWEEN 0 AND 1
UNION ALL
SELECT
  'payments.negative_or_orphan',
  COUNT(*)
FROM
  payments p
  LEFT JOIN orders o USING (order_id)
WHERE
  p.amount < 0
  OR o.order_id IS NULL
ORDER BY
  check_name;
```

Expected shape: seven rows with `check_name` and `failing_rows`. A nonzero
result is evidence to investigate, not permission to delete data automatically.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 1, write seven single-count queries joined with `UNION ALL`: `NULL` emails and duplicate `lower(trim(email))` keys in `customers`, negative totals and orphan `customer_id` values in `orders`, orphan orders or products and bad quantity or discount in `order_items`, and negative or orphan rows in `payments`; orphans are found with `LEFT JOIN ... WHERE parent key IS NULL`.
- **Expected result/shape:** For sql-42 Exercise 1, return exactly seven rows, one per `check_name`, and every `failing_rows` value is 0 on a fresh load because the course constraints already block these faults. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name` and `failing_rows`. The final order is `check_name`.
- **Independent verification:** For sql-42 Exercise 1, confirm seven distinct `check_name` values, all with 0; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET email = NULL WHERE customer_id = 1` and confirm `customers.null_email` becomes 1 while the other six stay 0, and separately insert a customer with email `' Customer7@Example.com'` and confirm `customers.duplicate_normalized_email` becomes 1.
- **Intermediate relation check:** Each of the seven branches is a separate `SELECT` that returns exactly one row: a fixed `check_name` and a `COUNT(*)`. The orphan branches start from the child table and `LEFT JOIN` the parent, so a missing parent shows up as a `NULL` key.
- **Clause check:** `UNION ALL` stacks the seven rows without removing any, and the final `ORDER BY check_name` sorts the whole union, not the last branch. Only the first branch names its columns; the later ones inherit `check_name` and `failing_rows` by position.
- **Alternative/trade-off:** One `SELECT` per table with several `COUNT(*) FILTER (WHERE ...)` columns scans each table once, but returns a wide row per table instead of the long `check_name`, `failing_rows` shape that a monitoring job can append to a history table.
- **Edge case:** `customers.duplicate_normalized_email` counts duplicate groups, while the other six count rows. Two customers sharing one address score 1, not 2, so a reader comparing counts across checks needs that grain stated. This branch also keeps `NULL` emails, so two customers with no email would form one `NULL` group and score 1 here as well as 2 in `customers.null_email`.

## Exercise 2: Invalid email patterns

```sql
SET search_path TO training, public;

SELECT
  customer_id,
  email
FROM
  customers
WHERE
  email IS NULL
  OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
ORDER BY
  customer_id;
```

The seed should return zero rows. The regex is a practical course check, not a
complete implementation of every valid RFC email address.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 2, read `customers.customer_id` and `email` and keep a row when `email IS NULL` or when `email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'`; the explicit `NULL` branch is needed because a regex test on `NULL` is unknown, not true.
- **Expected result/shape:** For sql-42 Exercise 2, return 0 rows on a fresh load, because all 500 addresses have the form `customerN@example.com`; when rows do appear there is one per failing `customer_id`. The final columns are `customer_id` and `email`. The final order is `customer_id`.
- **Independent verification:** For sql-42 Exercise 2, confirm 0 rows and that `SELECT count(*) FROM customers WHERE email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'` returns 500; then, inside `BEGIN ... ROLLBACK`, set customer 1's email to `'customer1(at)example.com'` and customer 2's to `NULL` and confirm exactly those two rows appear, the second only because of the `email IS NULL` branch.
- **Intermediate relation check:** The query reads all 500 customers and keeps those whose email is missing or fails the pattern. Every stored address matches, so the result is empty.
- **Clause check:** `!~*` is a case-insensitive "does not match", which is why the pattern can use uppercase `[A-Z]` ranges. The `email IS NULL` branch is needed because `NULL !~* '...'` is unknown and `WHERE` would silently drop that customer.
- **Alternative/trade-off:** A `CHECK` constraint with the same regex would reject bad emails at insert time. The query is still useful before adding such a constraint, since `ALTER TABLE ... ADD CONSTRAINT` fails if any existing row breaks it.
- **Edge case:** The pattern allows `a@b.co` and rejects addresses with non-ASCII letters such as `josé@example.com`. It is a practical filter for this course, not a full email validator, so flagged rows need a person to review them.

## Reasoning, safety, and pitfalls

- Normalize with `lower(trim(email))` before duplicate detection.
- Anti-join checks remain valuable even with foreign keys: imports or disabled
  constraints can violate assumptions.
- `COUNT(*)` over the duplicate subquery counts duplicate groups, not all rows
  participating in those groups. Label it accordingly.
- Keep validation queries read-only. Fix source data or use a reviewed
  remediation transaction after examining the exact failures.

## Exercise 3: Explain CHECK and NULL

SQL CHECK rejects FALSE but accepts UNKNOWN. `NOT NULL` is therefore a separate
schema rule when absence is invalid; the catalog query confirms both course
amount columns declare it.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 3, read `information_schema.columns` filtered to `table_schema = 'training'`, tables `orders` and `payments`, and columns `total_amount` and `amount`; the catalog shows `NOT NULL`, which is a separate rule from the `CHECK (amount >= 0)` constraint on `payments`.
- **Expected result/shape:** For sql-42 Exercise 3, return 2 rows, one per (`table_name`, `column_name`): `orders`/`total_amount` and `payments`/`amount`, both with `is_nullable = NO`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
- **Independent verification:** For sql-42 Exercise 3, confirm the two rows and that `SELECT NULL::numeric >= 0` returns `NULL`, which a `CHECK` treats as a pass; then, inside `BEGIN ... ROLLBACK`, run `ALTER TABLE payments ALTER COLUMN amount DROP NOT NULL`, confirm `INSERT INTO payments (order_id, amount, method) VALUES (1, NULL, 'card')` succeeds, and confirm the same insert with `-1` fails on `payments_amount_check`.
- **Intermediate relation check:** `information_schema.columns` has one row per column of every visible table; the three filters keep the two money columns in `training`, giving 2 rows.
- **Clause check:** `is_nullable` is a text column that reads `YES` or `NO`. Both rows say `NO`, so these columns carry the `NOT NULL` rule that their `CHECK (... >= 0)` constraints cannot provide on their own.
- **Alternative/trade-off:** `pg_attribute.attnotnull` joined to `pg_class` gives the same fact and is PostgreSQL-specific; `information_schema` is the portable view and is easier to read for a short audit.
- **Edge case:** Run the same query for `customers.email` and it reports `YES`. Combined with `UNIQUE (email)`, which treats every `NULL` as distinct, that means many customers could share a missing email without breaking any constraint.

## Exercise 4: Reconcile order totals

Line values aggregate to one row per order before comparison. The one-cent
tolerance is an explicit currency rule and failing order IDs remain visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 4, sum `quantity * unit_price * (1 - discount)` from `order_items` by `order_id` in a `calculated` CTE (4,362 rows, one per order), join it to `orders` on `order_id`, and keep orders whose `ABS(o.total_amount - c.line_total)` exceeds the one-cent tolerance `0.01`.
- **Expected result/shape:** For sql-42 Exercise 4, return 0 rows on a fresh load: 2,855 of the 4,362 orders differ from their line sums, but never by more than 0.0045, because stored totals keep two decimals and discounted line sums keep four. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
- **Independent verification:** For sql-42 Exercise 4, confirm 0 rows, then replace the test with `o.total_amount <> c.line_total` and confirm 2,855 rows with a maximum absolute difference of 0.0045; finally, inside `BEGIN ... ROLLBACK`, add 0.02 to order 3's `total_amount` and confirm one row: `order_id` 3, `total_amount` 601.75, `line_total` 601.7295, and `difference` 0.0205.
- **Intermediate relation check:** `calculated` turns 13,085 lines into 4,362 order rows, one per order, and the inner join pairs each with its header. The `WHERE` then removes every order within a cent, leaving none.
- **Clause check:** `ABS(o.total_amount - c.line_total) > 0.01` is the tolerance rule. Line sums carry four decimals after discounts while `total_amount` is rounded to cents, so 2,855 orders differ by up to 0.0045 without being wrong.
- **Alternative/trade-off:** Comparing `ROUND(c.line_total, 2)` with `total_amount` and testing equality states the rounding rule directly. All 4,362 orders pass that stricter test on the course data, but a total rounded the other way at exactly half a cent would be reported.
- **Edge case:** The inner join hides an order with no lines. None exists in this load, but a `LEFT JOIN` with `COALESCE(c.line_total, 0)` would report such an order as a full-amount difference instead of skipping it.

## Exercise 5: Retain duplicate evidence

The normalized email is the grouping key, but `array_agg` preserves raw variants
needed to diagnose case/whitespace differences.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 5, read `customers` rows with a non-`NULL` email, group by `lower(trim(email))`, keep groups with `COUNT(*) > 1`, and report the raw spellings with `array_agg(email ORDER BY email)` next to the normalized key.
- **Expected result/shape:** For sql-42 Exercise 5, return 0 rows on a fresh load, because no two emails differ only by case or surrounding spaces; when duplicates exist there is one row per `normalized_email`, with every raw spelling in `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
- **Independent verification:** For sql-42 Exercise 5, confirm 0 rows; then, inside `BEGIN ... ROLLBACK`, insert a customer with email `' Customer7@Example.com'` and confirm one row: `normalized_email` = `customer7@example.com`, `raw_variants` = `{customer7@example.com," Customer7@Example.com"}`, and `rows` = 2. The broken version that selects only the normalized key returns the same row without the two spellings.
- **Intermediate relation check:** `WHERE email IS NOT NULL` keeps all 500 customers, `GROUP BY` makes 500 normalized groups of one, and `HAVING COUNT(*) > 1` removes every group.
- **Clause check:** `array_agg(email ORDER BY email)` keeps every stored spelling in a stable order, so the person cleaning the data sees exactly which rows to merge. `lower(trim(email))` appears in both `SELECT` and `GROUP BY`, so the two always agree.
- **Alternative/trade-off:** A window form, `COUNT(*) OVER (PARTITION BY lower(trim(email)))`, returns one row per customer with the group size beside it. That is better for a fix-up script and worse for a summary.
- **Edge case:** `trim` removes spaces only at the ends. A tab, a trailing newline or a space inside the address survives normalization, so pasted data may need `regexp_replace(email, '\s', '', 'g')` as well.

## Exercise 6: Detect inclusive range overlap

Promotion pairs share a product, are compared once, and overlap when each start
is no later than the other end. Touching inclusive endpoints therefore count.

### Reasoning and verification

- **Inputs/evidence:** For sql-42 Exercise 6, join `promotions` (200 rows) to itself on `product_id` with `b.promotion_id > a.promotion_id`, so each pair is tested once, and keep pairs where `a.start_date <= b.end_date AND b.start_date <= a.end_date`, which treats a shared endpoint date as an overlap.
- **Expected result/shape:** For sql-42 Exercise 6, return 0 rows on a fresh load, because the 200 promotions cover 200 different products; when overlaps exist there is one row per overlapping pair (`promotion_a`, `promotion_b`), not per product. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
- **Independent verification:** For sql-42 Exercise 6, confirm 0 rows and that `count(DISTINCT product_id)` equals `count(*)` (200) in `promotions`; then, inside `BEGIN ... ROLLBACK`, copy promotion 1 with `start_date = end_date` (touching) and promotion 2 with `start_date = end_date + 1` (a one-day gap) and confirm exactly one pair: promotion 1 with the touching copy, for product 43.
- **Intermediate relation check:** The self-join pairs each promotion with every other promotion for the same product. With exactly one promotion per product in this load, there are no such pairs at all.
- **Clause check:** `b.promotion_id > a.promotion_id` keeps each pair once instead of twice and drops self-pairs. `a.start_date <= b.end_date AND b.start_date <= a.end_date` is the inclusive overlap test, so ranges that share one day count.
- **Alternative/trade-off:** `daterange(a.start_date, a.end_date, '[]') && daterange(b.start_date, b.end_date, '[]')` says the same thing with range types. An exclusion constraint using `gist` could then forbid overlaps outright.
- **Edge case:** Ranges that touch, one ending on 2026-01-31 and the next starting on 2026-01-31, overlap under this rule. If promotions end before their `end_date` day, change both tests to `<` instead.