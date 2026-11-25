# Day 52 Solutions: Data Warehouse Design, Part 1


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day52_solutions.sql
```

The solution includes the learner file first, so its opening transaction
prints the same tags and revenue table and commits the base warehouse. A
second `BEGIN` then adds the exercise objects and prints, in order:
`INSERT 0 8`, `UPDATE 500` and `INSERT 0 3836` with the 8 / 3,836 / 3,836
check row; the 13,085 / 4,362 / 13,085 grain row; three `INSERT 0 1` tags and
the routed -1; the reconciliation row with its 1.01 gap; and an empty
late-date list before the second `COMMIT`. Because both transactions commit,
a rerun resets `dwh` and rebuilds all of it. The
[solution-reading steps](../../STUDY-GUIDE.md#read-a-solution) show how to set
your transcript beside this one.

## Clause-by-clause reading map

Each warehouse answer begins at the table whose grain its output keeps, so
name that table and its row meaning first, then trace the statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Three warehouse rules tie the six answers together:

- **Grain is a count you can repeat.** The grain and reconciliation queries
  set `COUNT(*)` beside `COUNT(DISTINCT order_item_id)` and beside
  `training.order_items`, and the payment check repeats that comparison
  against `training.payments`.
- **A dimension join must hit exactly one row.** The payment load joins
  `dim_customer` on `customer_id` plus a `valid_from`/`valid_to` range, so
  each payment finds the one version valid on its date even after Day 53
  adds more.
- **A missing key is a policy, not an accident.** The unknown-member answer
  reserves -1 and routes to it explicitly with `COALESCE`, while the late-date
  answer refuses that shortcut for dates and lists the misses instead.

Day 52 is intentionally stateful. Unlike most course files, it commits a
course-owned `dwh` schema so Days 53 and 54 can use it. Re-running the learner
file or solution resets **only** that schema with `DROP SCHEMA dwh CASCADE`.

The complete runnable answer is
[`day52_solutions.sql`](day52_solutions.sql). From the `solutions` directory:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f day52_solutions.sql
```

The file first includes `../day52_project3_dwh_part1.sql`, which builds and
commits `dim_date`, Type-2-ready customer/product dimensions, and `fact_sales`.
It then completes all six exercises in a second committed transaction.

## Exercise 1: Add `dim_country`

The solution:

1. creates `dwh.dim_country(country_sk, country_code)`;
2. loads distinct country codes from `training.customers`;
3. adds `country_sk` to `dwh.dim_customer`;
4. backfills it through the existing text country code;
5. adds a foreign key and makes the new key non-null.

This preserves the original `country` attribute in each Type 2 customer row
while also providing a conformed country key. Expected grain is one row per
country code in `dim_country`; every customer-dimension version has exactly one
`country_sk`.

The `NOT NULL` rule is a contract for every later load: Day 53's SCD2 inserts
must supply `country_sk` for each new version. Day 53 also starts by adding this
same link, inside its rolled-back transaction, when a warehouse was built by the
Day 52 learner base alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 1, create `dim_country(country_sk, country_code)` with one row per distinct `training.customers.country`, add `country_sk` to `dim_customer` as a foreign key to it, backfill it from the text `country`, and make it `NOT NULL` before the final `COMMIT`.
- **Expected result/shape:** For sql-52 Exercise 1, expected output: `INSERT 0 8` for the country codes, `UPDATE 500` for the backfill, and `ALTER TABLE` for the `NOT NULL` change, so every customer-dimension version has exactly one `country_sk`. Days 53 and 54 run against this committed state, and Day 53's SCD2 inserts must keep it.
- **Independent verification:** For sql-52 Exercise 1, right after the backfill, confirm that `SELECT COUNT(*) FROM dim_country` is 8, that no `dim_customer` row has a NULL `country_sk`, and that joining `dim_customer` to `dim_country` on `country_sk` gives `country_code = country` on every row; after a savepoint, an `INSERT` into `dim_customer` without `country_sk` must fail with SQLSTATE `23502`, then roll back to the savepoint.
- **Intermediate relation check:** For sql-52 Exercise 1, load `dim_country` and backfill `country_sk` before you add `NOT NULL`; `SET NOT NULL` fails while any row is still NULL.
- **Clause check:** For sql-52 Exercise 1, the solution uses `CREATE TABLE dim_country` with an identity key and a unique `country_code`, `INSERT ... SELECT DISTINCT country FROM training.customers`, `ALTER TABLE dim_customer ADD COLUMN country_sk int REFERENCES dim_country (country_sk)`, an `UPDATE ... FROM dim_country` backfill, and `ALTER COLUMN country_sk SET NOT NULL`.
- **Alternative/trade-off:** For sql-52 Exercise 1, keeping only the text `country` avoids a join, but the conformed `country_sk` gives every fact and dimension one shared country key; the `NOT NULL` rule then obliges every later load, including Day 53's SCD2 inserts, to supply that key.
- **Edge case:** A customer whose country is missing from `dim_country` keeps a NULL `country_sk` after the backfill, so `SET NOT NULL` fails until `dim_country` gains that code or an explicit unknown member (Exercise 4).

## Exercise 2: Add `fact_payments`

The answer creates one row per source payment with:

- `payment_id` as the idempotent fact key;
- `order_id` as a degenerate operational reference;
- the payment-day `date_key`;
- the customer version whose validity range contains `payment_date`;
- `amount` and `method` as measures/attributes.

The table declares the fact grain and its dimension keys, and the load joins
each payment to its order, its payment date, and the customer version that was
valid on that date:

```sql
SET search_path TO dwh, training, public;

CREATE TABLE fact_payments (
  payment_id bigint PRIMARY KEY,
  order_id int NOT NULL,
  date_key int NOT NULL REFERENCES dim_date (date_key),
  customer_sk int NOT NULL REFERENCES dim_customer (customer_sk),
  amount numeric(12, 2) NOT NULL,
  method text NOT NULL
);

INSERT INTO fact_payments (payment_id, order_id, date_key, customer_sk, amount, method)
SELECT
  p.payment_id,
  p.order_id,
  dd.date_key,
  dc.customer_sk,
  p.amount,
  p.method
FROM
  training.payments p
  JOIN training.orders o USING (order_id)
  JOIN dim_date dd ON dd.date_actual = p.payment_date::date
  JOIN dim_customer dc ON dc.customer_id = o.customer_id
    AND p.payment_date::date >= dc.valid_from
    AND p.payment_date::date <= COALESCE(dc.valid_to, 'infinity'::date);
```

After running the solution, verify source-to-fact completeness:

```sql
SET search_path TO dwh, training, public;

SELECT
  (
    SELECT
      COUNT(*)
    FROM
      dim_country) AS countries,
  (
    SELECT
      COUNT(*)
    FROM
      fact_payments) AS fact_payment_rows,
  (
    SELECT
      COUNT(*)
    FROM
      training.payments) AS source_payment_rows,
  (
    SELECT
      COUNT(*)
    FROM
      dim_customer
    WHERE
      country_sk IS NULL) AS customers_without_country_key;
```

The two payment counts must match and `customers_without_country_key` must be
zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 2, create `fact_payments` with one row per `training.payments` row, keyed by `payment_id`, and load it by joining each payment to its order, to `dim_date` on the payment date, and to the `dim_customer` version valid on that date.
- **Expected result/shape:** For sql-52 Exercise 2, expected output: `INSERT 0 3836`, one fact row per source payment, then a check row with `countries` 8, `fact_payment_rows` 3836, and `source_payment_rows` 3836. The fact columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`.
- **Independent verification:** For sql-52 Exercise 2, confirm that `fact_payment_rows` equals `source_payment_rows` (3836) and that `SELECT SUM(amount) FROM fact_payments` equals `SELECT SUM(amount) FROM training.payments` (1831900.81); a join that lost payments would lower the count, and a join to every customer version would raise it.
- **Intermediate relation check:** For sql-52 Exercise 2, join `training.payments` to `orders`, `dim_date`, and `dim_customer` one table at a time and check that the row count stays 3836 after each join.
- **Clause check:** `CREATE TABLE fact_payments` declares `payment_id bigint PRIMARY KEY`, so loading the same payment twice fails instead of doubling cash. The `INSERT ... SELECT` reads `training.payments`, joins `training.orders` `USING (order_id)` to learn the customer, joins `dim_date` on `date_actual = p.payment_date::date`, and joins `dim_customer` on `customer_id` with the payment date between `valid_from` and `COALESCE(valid_to, 'infinity'::date)`. The check is three scalar subqueries in one `SELECT`, which is why it prints a single row.
- **Alternative/trade-off:** Filtering on `dc.is_current`, as the `fact_sales` load does, gives the same 3,836 rows today but would tie a 2023 payment to whichever version is current on the day you reload. The date-range join costs one extra predicate and stays right after Day 53 closes old versions. A `LEFT JOIN` with `COALESCE(..., -1)` would also keep every payment, yet it would hide a broken customer mapping behind the unknown member.
- **Edge case:** A payment whose date falls outside `dim_date` would be dropped silently by the inner join; Exercise 6 lists such payments with a `LEFT JOIN ... WHERE d.date_key IS NULL` check.

## Required Days 52 to 54 sequence

1. Run `day52_solutions.sql` once in `advanced_sql_training`; it persists the
   base warehouse plus the Day 52 exercise objects: `dim_country`, the
   `NOT NULL` `country_sk`, `fact_payments`, and the `-1` unknown members.
2. Run `day53_solutions.sql` in the same database. It validates SCD work inside
   a transaction and rolls it back.
3. Run `day54_solutions.sql` in the same database. It validates aggregates and
   the refresh procedure inside a transaction and rolls them back.

Day 54 depends on committed Day 52 state, not on rolled-back Day 53 changes.
The learner Day 53 and Day 54 files also accept this state, and the Day 53 and
Day 54 solutions also accept a warehouse built by the Day 52 learner file alone.

## Safety and pitfalls

- Do not run Day 52 against a schema named `dwh` that contains unrelated work.
- Use `ON_ERROR_STOP=1`; otherwise `psql` can continue after a failed statement
  and leave a misleading partial exercise.
- Dimension validity uses inclusive date bounds. Close an old version on the
  day before the new version starts.
- A fact load must reconcile to source counts before it is trusted.

## Exercise 3: State the sales fact grain

`COUNT(*)`, distinct orders, and distinct order-item keys prove that
`fact_sales` is one row per order line. An order can therefore repeat.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 3, read from `fact_sales` and count its rows, its distinct `order_id` values, and its distinct `order_item_id` values.
- **Expected result/shape:** For sql-52 Exercise 3, expected output: one row with `fact_rows` 13085, `orders` 4362, and `distinct_order_items` 13085, which shows that `fact_sales` has one row per order line and that `order_id` alone does not identify a row. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
- **Independent verification:** For sql-52 Exercise 3, confirm that `fact_rows` and `distinct_order_items` both equal `SELECT COUNT(*) FROM training.order_items` (13085) while `orders` is only 4362; `SELECT order_id FROM fact_sales GROUP BY order_id HAVING COUNT(*) > 1` returns 3490 orders, which proves that `order_id` repeats.
- **Intermediate relation check:** For sql-52 Exercise 3, compare `COUNT(*)` with `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT order_item_id)`; the key is the column whose distinct count equals the row count.
- **Clause check:** One `SELECT` over `fact_sales` with three aggregates and no `GROUP BY`, so it returns one row even on an empty table, where it would print 0, 0, 0. `COUNT(DISTINCT order_item_id)` carries the proof: it equals `COUNT(*)` only when no line was loaded twice.
- **Alternative/trade-off:** `SELECT order_item_id FROM fact_sales GROUP BY order_item_id HAVING COUNT(*) > 1` lists the duplicates themselves rather than a summary, which helps more once the counts disagree; on this load it returns zero rows. A `UNIQUE (order_item_id)` constraint would make the check permanent, and the base `fact_sales` definition has none, only its three foreign keys.
- **Edge case:** Matching counts on today's data do not stop a later duplicate load; only a unique constraint on `order_item_id` enforces the grain.

## Exercise 4: Route unknown members deliberately

The solution reserves surrogate key `-1` in referenced dimensions and shows a
missing natural customer key mapping to it. This policy must not hide a broken
required mapping.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 4, add an unknown member with surrogate key -1 to `dim_country`, `dim_customer`, and `dim_product`, then route a source row whose `customer_id` (-999) has no dimension match to that member with `COALESCE(dc.customer_sk, -1)` after a `LEFT JOIN`.
- **Expected result/shape:** For sql-52 Exercise 4, expected output: three `INSERT 0 1` commands and one row whose `routed_customer_sk` is -1. The final columns are `routed_customer_sk`.
- **Independent verification:** For sql-52 Exercise 4, confirm that `SELECT customer_sk FROM dim_customer WHERE customer_sk = -1` returns one row and that the routing query returns -1 for `customer_id` -999; replace -999 with 1 and confirm that it returns that customer's real `customer_sk` (1) instead.
- **Intermediate relation check:** For sql-52 Exercise 4, insert the unknown members first and query each one by its -1 key before you test the routing `LEFT JOIN`.
- **Clause check:** The three `INSERT ... VALUES` statements write -1 straight into each key column. `dim_country` needs `OVERRIDING SYSTEM VALUE` because its key is an identity column, and the customer row also sets `country_sk = -1` so the new `NOT NULL` rule holds. The routing query left-joins a one-row `VALUES (-999)` source to `dim_customer` `USING (customer_id)`, and `COALESCE(dc.customer_sk, -1)` turns the unmatched NULL into the reserved key.
- **Alternative/trade-off:** Rejecting the row with an inner join plus a count check is the stricter policy, and it is the one the late-date answer picks for dates. An unknown member suits facts that must be counted before their dimension catches up; a regular count of facts on `customer_sk = -1` keeps that bucket visible instead of letting it absorb real mapping errors.
- **Edge case:** `dim_country.country_sk` is `GENERATED ALWAYS AS IDENTITY`, so inserting -1 needs `OVERRIDING SYSTEM VALUE`; the other dimensions accept -1 directly because their keys only default from a sequence.

## Exercise 5: Reconcile completeness and amount

Fact/source row counts and rounded line amounts appear together. Either a row
or amount difference blocks trust in the warehouse load.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 5, compare `fact_sales` with `training.order_items`: the two row counts, the total fact `amount`, and the source line total `ROUND(SUM(quantity * unit_price * (1 - discount)), 2)`.
- **Expected result/shape:** For sql-52 Exercise 5, expected output: one row with `fact_rows` and `source_rows` both 13085, `fact_amount` 2355648.13, and `source_amount` 2355647.12; the 1.01 gap comes from rounding each fact line to cents. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
- **Independent verification:** For sql-52 Exercise 5, confirm equal row counts, then recompute the source with the fact's rounding rule, `SELECT SUM(ROUND(quantity * unit_price * (1 - discount), 2)) FROM training.order_items`, and expect 2355648.13, exactly `fact_amount`; a gap that remains after that would be a real load error.
- **Intermediate relation check:** For sql-52 Exercise 5, count rows first, then compare totals; when the totals differ, check whether the fact rounds each line before summing.
- **Clause check:** Four scalar subqueries in one `SELECT`: two `COUNT(*)` values and two sums. The fact side sums the stored `amount`, already rounded to cents per line by its `numeric(12, 2)` column, while the source side sums the raw `quantity * unit_price * (1 - discount)` and rounds once at the end, which is where the 1.01 difference comes from.
- **Alternative/trade-off:** Recomputing the source as `SUM(ROUND(quantity * unit_price * (1 - discount), 2))` makes both totals 2,355,648.13, and a `FULL JOIN` on `order_item_id` that compares each line's amount would name the exact lines if they ever drifted. The one-row form is enough for a load gate; the line-level join is what you run after the gate fails.
- **Edge case:** Rounding per line and rounding the total once are both defensible, but a reconciliation must apply the same rule on both sides before it calls a difference an error.

## Exercise 6: Handle late dates explicitly

The query lists payments outside `dim_date`. The chosen policy is fail and
extend the dimension because silently mapping a real accounting date to unknown
would destroy time analysis.

### Reasoning and verification

- **Inputs/evidence:** For sql-52 Exercise 6, left join the 3,836 `training.payments` rows to `dwh.dim_date` on `d.date_actual = p.payment_date::date` and keep only the payments with no calendar row (`d.date_key IS NULL`); the calendar runs from two years before today to one year after today (2023-02-13 to 2027-11-25 on our run).
- **Expected result/shape:** For sql-52 Exercise 6, expected output: zero rows on the course data, because every payment date falls inside the calendar; a late payment would appear as one row per `payment_id`. The final columns are `payment_id` and `payment_date` (the `::date` cast keeps the source column name). The final order is `p.payment_id`.
- **Independent verification:** For sql-52 Exercise 6, confirm that the left join without the `WHERE` returns 3,836 rows and 3,836 distinct `payment_id` values, so the calendar adds no fanout, and that the `NOT EXISTS` form also returns 0 rows. Then, in a transaction, insert a payment for order 1 dated 2028-01-01: the query returns exactly that new `payment_id` with `payment_date` 2028-01-01, and the unfiltered join rises to 3,837 rows; `ROLLBACK`.
- **Intermediate relation check:** Start from `SELECT COUNT(*) FROM training.payments` (3,836), then add the left join to `dim_date` on the cast date: it must still return 3,836 rows, because the calendar holds one row per day. Only then does `WHERE d.date_key IS NULL` filter, and on our run it removes all 3,836.
- **Clause check:** `FROM training.payments p LEFT JOIN dim_date d ON d.date_actual = p.payment_date::date`, then `WHERE d.date_key IS NULL` keeps payments with no calendar row, and `ORDER BY p.payment_id` makes the list stable. The NULL test sits in `WHERE`, after the join, which is what makes this an anti-join; moved into `ON`, it would keep every payment instead.
- **Alternative/trade-off:** `WHERE NOT EXISTS (SELECT 1 FROM dim_date d WHERE d.date_actual = p.payment_date::date)` states the same anti-join directly and also returns zero rows here. The policy matters more than the syntax: this answer fails the load and extends the calendar, whereas routing late dates to an unknown date key would keep the payment but drop its month from every report.
- **Edge case:** `payment_date` is a `timestamptz`, and the `::date` cast uses the session time zone (UTC on our run). The 202 payments stamped at 23:00 UTC or later would move to the next day in a zone east of UTC, so check `SHOW timezone` before trusting a boundary day. A far-future test row such as `VALUES (date '2028-01-01')` left-joined to `dim_date` proves the query can report a miss at all.