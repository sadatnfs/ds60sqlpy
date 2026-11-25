# Day 52: Data Warehouse Project, Part 1: Star Schema

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-52** and run it with
**Whole SQL lesson (psql)**. This is the file in the course that keeps its
work on purpose: it drops and recreates the `dwh` schema inside
`advanced_sql_training`, loads four tables and ends with `COMMIT`, so Days 53
and 54 can read what you build. A snippet run would skip the `BEGIN`, the
schema reset and that `COMMIT`. Your editable copy is
`.learning/sql/sql-52/lesson/workspace/sql/postgres-60day/day52_project3_dwh_part1.sql`
in the Docker learning volume. A clean rerun prints a `NOTICE` that the drop
cascaded to six objects (a first run says the schema did not exist), then
four `INSERT` tags: 1,747 calendar days on our run, 500 customers, 300
products and 13,085 sales lines, followed by a 50-row revenue table. `psql`
stops at the first error before reaching `COMMIT`, so a failed load leaves the
previous `dwh` schema exactly as it was. Setup, reset and resume are covered
in the [classroom launch steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
JupyterLab users can take the
[contributor notebook path](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
instead.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 51; cash flow](day51_project2_finance_part3.md). Day 51 summarized cash by month straight from `training.payments`; today the same 3,836 payments get their own fact table with date and customer keys, so the 1,831,900.81 payment total is one you can check against.
  Use only the course-owned disposable `dwh` schema; Day 52 resets and commits
  it for Days 53 and 54.
- **Artifacts:** [learner SQL](../day52_project3_dwh_part1.sql) ·
  [solution reasoning](../solutions/day52_solutions.md) ·
  [executable solution](../solutions/day52_solutions.sql)

## A beginner's mental model for this lesson

A warehouse lets you answer "revenue by month and category" without writing a
five-table join each time. Day 52 builds the smallest useful one: a star
schema with one fact table in the middle and three dimensions around it.

A **fact table** holds measurements at one declared grain. Here `fact_sales`
has one row per source order line: 13,085 rows for 4,362 orders, because
3,490 orders have two to five lines and only 872 have a single line. Each row
carries `quantity`, `unit_price`, `discount` and a discounted `amount`, plus
three keys that point outward.

A **dimension** holds the descriptive attributes those keys point to.
`dim_date` has one row per calendar day with year, quarter, month, day name
and a weekend flag; `dim_customer` has one row per customer version with
country and segment; `dim_product` has one row per product version with
category, price and cost. Grouping facts by `dim_product.category` and
`dim_date.month` is exactly what the script's last query does.

A **surrogate key** is a number the warehouse invents for each dimension row,
such as `customer_sk`, instead of reusing the source's `customer_id`. Today
the two line up (customer 1 gets `customer_sk` 1) because every customer has
one version. Day 53 adds a second version for changed customers, and then one
`customer_id` owns two `customer_sk` values; that is why facts store the
surrogate. `dim_date` is the exception, keyed by the readable `yyyymmdd`
integer, 20230213 through 20271125 on our run.

When a count looks wrong, walk the load in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
and count rows after each join; every later warehouse check repeats that habit.

## Two worked SQL examples

Both excerpts are `CREATE TABLE` statements from
`day52_project3_dwh_part1.sql`. They run after `CREATE SCHEMA dwh` and
`SET search_path TO dwh, training, public`, so the unqualified names land in
the new schema rather than in `training`.

### Example 1

```sql
CREATE TABLE dim_date (
  date_key INT PRIMARY KEY, -- yyyymmdd
  date_actual DATE NOT NULL,
  year INT NOT NULL,
  quarter INT NOT NULL,
  month INT NOT NULL,
  day INT NOT NULL,
  day_name TEXT NOT NULL,
  is_weekend BOOLEAN NOT NULL
);
```

**How to read it:** `dim_date` is a calendar, not a copy of any source table. `date_key` is the
primary key and stores the day as an integer such as 20261123, which keeps
fact rows readable and turns a range of keys into a range of days. Every
attribute is `NOT NULL` because the load derives each one from the date:
`extract(quarter ...)`, `to_char(d, 'Dy')` for names like `Mon`, and
`extract(isodow ...) >= 6` for Saturday and Sunday. Nothing in the definition
prevents a missing day; the script avoids gaps by filling the table from
`generate_series`, one row per day.

**Expected result/shape:** The statement prints `CREATE TABLE`. Rows arrive later with `INSERT 0 1747`
on our run: the calendar runs from the earlier of the first order (13
February 2023) and two years before today, to the later of the last order and
one year after today, so the count grows by one for each day you wait before
rerunning. 498 of those days have `is_weekend` true. A quick proof of one row
per day is `SELECT COUNT(*) = COUNT(DISTINCT date_actual) FROM dim_date`,
which should print `t`.

### Example 2

```sql
CREATE TABLE dim_customer (
  customer_sk INT PRIMARY KEY DEFAULT nextval('dim_customer_sk_seq'),
  customer_id INT NOT NULL, -- business key
  full_name TEXT,
  country TEXT,
  segment TEXT,
  valid_from DATE NOT NULL,
  valid_to DATE,
  is_current BOOLEAN NOT NULL DEFAULT TRUE
);
```

**How to read it:** `dim_customer` is shaped for history before it has any. `customer_sk` draws
from `dim_customer_sk_seq`, while `customer_id` is the business key and is
deliberately not unique: a changed customer will later own two rows with the
same `customer_id`. `valid_from`, `valid_to` and `is_current` describe each
version's life span, and today's load gives every row `valid_from` equal to
the customer's `created_at` date, `valid_to` NULL and `is_current` true.
`dim_product` follows the same pattern for products.

**Expected result/shape:** Again only `CREATE TABLE`; the load then prints `INSERT 0 500`, one version
per customer. On our run all 500 surrogates matched their `customer_id`, a
coincidence of insert order that no query should rely on. The load's
`COALESCE(c.segment, 'standard')` never fires on this fixture: the four
segments hold 125 customers each and none is NULL.

## Learning objectives

- Declare fact and dimension grains before creating a star schema.
- Load surrogate keys and validate every fact-to-dimension relationship.

## Vocabulary and concepts

- **Fact table:** measurements/events at a declared business grain.
- **Dimension:** descriptive attributes joined to facts through keys.
- **Surrogate key:** warehouse-owned identifier for a dimension row or version.

## Worked example / walkthrough

Write the grain beside every table before loading it. Load `dim_date` and the
customer/product dimensions, then map each source order item to exactly one date,
customer, and product key in `fact_sales`. Compare fact row count with source
`order_items` and check every key resolves once before committing Day 52.

## Exercises

Complete these in the [learner SQL](../day52_project3_dwh_part1.sql):

1. Add `dim_country` and connect it to customers.
   **Inputs/evidence:** For sql-52 Exercise 1, create `dim_country(country_sk, country_code)` with one row per distinct `training.customers.country`, add `country_sk` to `dim_customer` as a foreign key to it, backfill it from the text `country`, and make it `NOT NULL` before the final `COMMIT`.
   **Expected result/shape:** For sql-52 Exercise 1, expected output: `INSERT 0 8` for the country codes, `UPDATE 500` for the backfill, and `ALTER TABLE` for the `NOT NULL` change, so every customer-dimension version has exactly one `country_sk`. Days 53 and 54 run against this committed state, and Day 53's SCD2 inserts must keep it.
   **Verify:** For sql-52 Exercise 1, right after the backfill, confirm that `SELECT COUNT(*) FROM dim_country` is 8, that no `dim_customer` row has a NULL `country_sk`, and that joining `dim_customer` to `dim_country` on `country_sk` gives `country_code = country` on every row; after a savepoint, an `INSERT` into `dim_customer` without `country_sk` must fail with SQLSTATE `23502`, then roll back to the savepoint.
   **Data check:** The eight codes are AU, BR, CA, DE, FR, GB, IN and US, with 62 or 63 customers each. The rejected insert on our run reported `null value in column "country_sk"`, and it still consumed a number from `dim_customer_sk_seq`, so the next real customer version skips one; a gap in surrogate keys is harmless.
2. Build `fact_payments` at payment grain.
   **Inputs/evidence:** For sql-52 Exercise 2, create `fact_payments` with one row per `training.payments` row, keyed by `payment_id`, and load it by joining each payment to its order, to `dim_date` on the payment date, and to the `dim_customer` version valid on that date.
   **Expected result/shape:** For sql-52 Exercise 2, expected output: `INSERT 0 3836`, one fact row per source payment, then a check row with `countries` 8, `fact_payment_rows` 3836, and `source_payment_rows` 3836. The fact columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`.
   **Verify:** For sql-52 Exercise 2, confirm that `fact_payment_rows` equals `source_payment_rows` (3836) and that `SELECT SUM(amount) FROM fact_payments` equals `SELECT SUM(amount) FROM training.payments` (1831900.81); a join that lost payments would lower the count, and a join to every customer version would raise it.
   **Data check:** All 3,836 payments fall between 15 February 2023 and 24 November 2026, well inside the calendar, and each arrives 0 to 3 days after its order. They cover 3,489 orders, 347 of them paid in more than one installment, so `order_id` repeats in `fact_payments` just as it does in `fact_sales`. By `method`: credit 1,050, paypal 1,040, bank 886 and card 860.
3. State/prove the `fact_sales` grain.
   **Inputs/evidence:** For sql-52 Exercise 3, read from `fact_sales` and count its rows, its distinct `order_id` values, and its distinct `order_item_id` values.
   **Expected result/shape:** For sql-52 Exercise 3, expected output: one row with `fact_rows` 13085, `orders` 4362, and `distinct_order_items` 13085, which shows that `fact_sales` has one row per order line and that `order_id` alone does not identify a row. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
   **Verify:** For sql-52 Exercise 3, confirm that `fact_rows` and `distinct_order_items` both equal `SELECT COUNT(*) FROM training.order_items` (13085) while `orders` is only 4362; `SELECT order_id FROM fact_sales GROUP BY order_id HAVING COUNT(*) > 1` returns 3490 orders, which proves that `order_id` repeats.
   **Data check:** The remaining 872 orders have a single line each, and the longest order has five lines.
4. Add and test unknown dimension members.
   **Inputs/evidence:** For sql-52 Exercise 4, add an unknown member with surrogate key -1 to `dim_country`, `dim_customer`, and `dim_product`, then route a source row whose `customer_id` (-999) has no dimension match to that member with `COALESCE(dc.customer_sk, -1)` after a `LEFT JOIN`.
   **Expected result/shape:** For sql-52 Exercise 4, expected output: three `INSERT 0 1` commands and one row whose `routed_customer_sk` is -1. The final columns are `routed_customer_sk`.
   **Verify:** For sql-52 Exercise 4, confirm that `SELECT customer_sk FROM dim_customer WHERE customer_sk = -1` returns one row and that the routing query returns -1 for `customer_id` -999; replace -999 with 1 and confirm that it returns that customer's real `customer_sk` (1) instead.
   **Data check:** On a warehouse built by the solution, a source `customer_id` of -1 also routes to -1, but only because it matches the unknown member's own `customer_id`. Test with a value such as -999 that cannot collide with that row.
5. Reconcile fact rows and amount to source.
   **Inputs/evidence:** For sql-52 Exercise 5, compare `fact_sales` with `training.order_items`: the two row counts, the total fact `amount`, and the source line total `ROUND(SUM(quantity * unit_price * (1 - discount)), 2)`.
   **Expected result/shape:** For sql-52 Exercise 5, expected output: one row with `fact_rows` and `source_rows` both 13085, `fact_amount` 2355648.13, and `source_amount` 2355647.12; the 1.01 gap comes from rounding each fact line to cents. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
   **Verify:** For sql-52 Exercise 5, confirm equal row counts, then recompute the source with the fact's rounding rule, `SELECT SUM(ROUND(quantity * unit_price * (1 - discount), 2)) FROM training.order_items`, and expect 2355648.13, exactly `fact_amount`; a gap that remains after that would be a real load error.
   **Data check:** 3,362 of the 13,085 source lines have a value with more than two decimal places, and rounding each into the `numeric(12, 2)` column adds up to the 1.01 gap. The once-rounded source total, 2,355,647.12, is itself 0.23 above the 2,355,646.89 stored in `orders.total_amount`.
6. Define a late-arriving date policy.
   **Inputs/evidence:** For sql-52 Exercise 6, left join the 3,836 `training.payments` rows to `dwh.dim_date` on `d.date_actual = p.payment_date::date` and keep only the payments with no calendar row (`d.date_key IS NULL`); the calendar runs from two years before today to one year after today (2023-02-13 to 2027-11-25 on our run).
   **Expected result/shape:** For sql-52 Exercise 6, expected output: zero rows on the course data, because every payment date falls inside the calendar; a late payment would appear as one row per `payment_id`. The final columns are `payment_id` and `payment_date` (the `::date` cast keeps the source column name). The final order is `p.payment_id`.
   **Verify:** For sql-52 Exercise 6, confirm that the left join without the `WHERE` returns 3,836 rows and 3,836 distinct `payment_id` values, so the calendar adds no fanout, and that the `NOT EXISTS` form also returns 0 rows. Then, in a transaction, insert a payment for order 1 dated 2028-01-01: the query returns exactly that new `payment_id` with `payment_date` 2028-01-01, and the unfiltered join rises to 3,837 rows; `ROLLBACK`.
   **Data check:** The solution's query returns no rows on our run: the latest payment, on 24 November 2026, sits a year before the calendar ends on 25 November 2027. The second column prints as `payment_date` because the cast keeps the source name. To see a miss without touching the table, left-join `(VALUES (date '2026-11-24'), (date '2028-01-01'))` to `dim_date`: only the 2028 row comes back with a NULL `date_key`.

Run from a reset and save checks for Days 53 and 54.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** `fact_sales` rows must equal source `order_items` rows.
- **Joining every customer version:** the fact load matches `dim_customer`
  with `AND dc.is_current`. Today the filter changes nothing because each
  customer has one row, but once Day 53 adds versions, dropping it would
  duplicate every sale of a changed customer. Keep it, or match on the version
  valid at `order_date` the way Exercise 2 does for payments.
- **Rerunning over work you care about:** the first statement after `BEGIN`
  is `DROP SCHEMA IF EXISTS dwh CASCADE`. Anything you added to `dwh` by hand,
  including committed Day 53 or 54 experiments, disappears on the rerun.
- **Expecting a fixed calendar:** `dim_date` is sized from `CURRENT_DATE`, so
  its row count (1,747 on our run) and last key change from day to day.
  Compare key coverage, not raw counts, between two runs.
- **Reading the revenue table as complete:** the last query groups 46 months
  by 6 categories into 276 rows, and `LIMIT 50` keeps only the newest. March
  2026 is cut after two categories, Home at 19,422.55 and Sports at 17,326.99,
  so a March total read from this output would be wrong.
- **Loading facts before their dimension rows:** `fact_sales` declares
  `REFERENCES` on all three keys, so inserting facts first fails with a
  foreign-key error. The script's order (dates, customers, products, then
  facts) is part of the design.
- When the error is none of these, the
  [first-error checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  keeps you from editing later statements before the real cause is fixed.

## Self-check

- Does every fact table have a documented, enforced source grain?
- Did the script complete with `COMMIT`, and do all source/fact counts and key
  resolution checks pass?

## Next step

Continue in the same database to
[Day 53; slowly changing dimensions](day53_project3_dwh_part2_scd.md).

## Deep dive and reference

## Project focus

- Define fact and dimension grain with surrogate keys.
- Load date, customer, product, and sales facts from `training`.
- Add a conformed country dimension and a payment fact.

## Stateful behavior

Day 52 is intentionally different from most lessons. It drops and recreates
only the course-owned `dwh` schema, builds its base warehouse, and commits it for
Days 53 and 54. Do not run it against a `dwh` schema containing unrelated work.

The base grains are:

- `dim_date`: one row per calendar date;
- `dim_customer`: Type-2-ready versions keyed by `customer_sk`;
- `dim_product`: Type-2-ready versions keyed by `product_sk`; and
- `fact_sales`: one row per source `order_item_id`.

## Practice map

The six exercises split evenly. Exercises 1, 2 and 4 add objects that Days 53
and 54 will read (`dim_country`, `fact_payments` and the -1 members), so write
them in the learner file above its final `COMMIT`, not in a separate session.
Exercises 3, 5 and 6 are read-only proofs: one row of counts, one row of
reconciled totals and a list that should come back empty. The prompts,
expected tags and checks above are the contract both solution files answer.

## Required Days 52 to 54 sequence

1. Run Day 52 once, either this learner file or `day52_solutions.sql`; it
   commits the base warehouse.
2. Run Day 53 in the same database. It first checks the Exercise 1 country
   link (a `NOT NULL` `country_sk` that points at `dim_country`), adds it only
   if your Day 52 run did not, keeps it in every new SCD2 version, and rolls all
   its changes back.
3. Run Day 54 in the same database; its aggregate/procedure changes roll back.

Day 54 depends on committed Day 52 state, not on Day 53 changes persisting.
Either Day 52 file is a valid starting point for the learner and solution files
of Days 53 and 54.

## Validation and limits

- `fact_sales` rows must equal source `order_items` rows.
- `fact_payments` rows must equal source `payments` rows.
- Every fact date and dimension key must resolve exactly once.
- Use `psql -v ON_ERROR_STOP=1`; a partial warehouse is not a passing load.

## Ask an AI tutor about this lesson

A tutor helps most here as a reviewer of grain statements. Write one sentence
per table ("one row of `fact_payments` is ...") first, then share those
sentences with the counts your run printed and ask where a join could break
them. [The tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) cover
what to share and what to keep private. Send this once your grain sentences
are written:

```text
Tutor me through sql-52: Data Warehouse Project, Part 1: Star Schema.

I have completed the direct catalog prerequisite: `sql-51`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day52_project3_dwh_part1.md
- Answer-free learner SQL: sql/postgres-60day/day52_project3_dwh_part1.sql

Key terms to teach in context: Fact table, Dimension, Surrogate key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Write the grain beside every table before loading it. Load `dim_date` and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in `fact_sales`. Compare fact row count with source `order_items` and check every key resolves once before committing Day 52.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-52/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
