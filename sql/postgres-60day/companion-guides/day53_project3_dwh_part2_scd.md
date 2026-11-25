# Day 53: Data Warehouse Project, Part 2: SCD Type 2

## How to run this lesson

In `./classroom`, pick PostgreSQL, open **sql-53** and run it with
**Whole SQL lesson (psql)**. Day 53 is the warehouse lesson that keeps
nothing: it opens `BEGIN` inside `advanced_sql_training`, versions ten
customers and ten products in the committed Day 52 `dwh` schema, prints its
checks and ends with `ROLLBACK`, so Day 54 still finds the Day 52 warehouse.
A snippet run would skip that `BEGIN` and could leave half a change behind.
Your editable copy is
`.learning/sql/sql-53/lesson/workspace/sql/postgres-60day/day53_project3_dwh_part2_scd.sql`
in the Docker learning volume. On a base built by the Day 52 solution, the
transcript opens with two `NOTICE` lines saying `dim_country` and
`country_sk` already exist, `INSERT 0 0` and `UPDATE 0`; then come `SELECT 10`
and `INSERT 0 10` for customers, a check row of 511 versions with 0
mismatched country keys, a ten-row version list, `SELECT 10` and
`INSERT 0 10` for products, and `ROLLBACK`. On a base from the Day 52 learner
file alone, those opening statements build the country link instead
(`INSERT 0 8`, `UPDATE 500`) and the check reads 510, because that base has no
-1 unknown member. `psql` stops at the first error and the open transaction
dies with it, so a failed run changes nothing. Setup and resume live in the
[classroom launch steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
JupyterLab users can take the
[contributor notebook path](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
instead.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Run and verify committed Day 52 left one version per customer, every one current with an open `valid_to`; today is the first time a `customer_id` owns two rows.
  [Day 52; star-schema warehouse](day52_project3_dwh_part1.md) in the same
  database.
- **Artifacts:** [learner SQL](../day53_project3_dwh_part2_scd.sql) ·
  [solution reasoning](../solutions/day53_solutions.md) ·
  [executable solution](../solutions/day53_solutions.sql)

## A beginner's mental model for this lesson

Customers change. When customer 1 moves from the standard segment to gold, a
report about October should still see the segment customer 1 had in October,
and a report about November should see gold. Overwriting the row loses the
first answer; Day 53 keeps both.

**SCD Type 2** (slowly changing dimension, Type 2) keeps history by adding
rows instead of overwriting them. The solution's change stamps an end date on
customer 1's standard row in `dim_customer`, sets its `is_current` to false
and inserts a gold row beside it, so the dimension grows from 501 rows to 502.

A **business key** is the source identity every version shares: both rows
carry `customer_id` 1. The surrogate `customer_sk` differs per version (1 for
the standard row, a fresh sequence number for the gold row), and the surrogate
is what fact rows store, so each sale points at one specific version.

A **validity interval** is the span of days one version applies, from
`valid_from` to `valid_to`. Both ends are inclusive in this course and a NULL
`valid_to` means the version is still open. Inclusive ends force the closed
row to stop one day before its successor starts; if both rows claimed the
boundary day, a sale on that day would match two versions.

The learner file starts its ten new customer versions today, and no order is
dated today or later (the newest is 23 November 2026 on our fixture), so every
historical sale still belongs to an old version. The solution backdates its
change 30 days instead, which splits customer 1's sales across two versions
and gives the as-of join something to prove. Read that join in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order):
the `FROM` side is one row per order line, every dimension join must add
exactly one partner, and 13,085 lines in must stay 13,085 out.

## Two worked SQL examples

Both excerpts come from `day53_project3_dwh_part2_scd.sql` and run inside its
`BEGIN`, after `SET search_path TO dwh, training, public`, so `dim_customer`
resolves to the Day 52 table while the source is named in full as
`training.customers`. Everything they write disappears at the final
`ROLLBACK`.

### Example 1

```sql
CREATE TEMP TABLE changed_customers AS
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  CASE WHEN c.segment = 'platinum' THEN
    'gold'
  ELSE
    'platinum'
  END AS segment
FROM
  training.customers c
ORDER BY
  c.customer_id
LIMIT 10;
```

**How to read it:** `CREATE TEMP TABLE ... AS SELECT` runs a query and stores its rows in a
session-only table, `changed_customers`, that vanishes when the connection
closes. The `CASE` invents a change for the first ten customers by
`customer_id`: a platinum customer drops to gold and everyone else becomes
platinum. Name and country are copied unchanged, so segment is the only
attribute that can differ from the current dimension row.

**Expected result/shape:** `psql` prints `SELECT 10`, not a result grid. The stored segments for
customers 1 to 10 read platinum, platinum, platinum, gold, platinum,
platinum, platinum, gold, platinum, platinum: customers 4 and 8 were platinum
in the source and drop to gold. All ten now differ from their dimension rows,
so all ten will version. To see them, add
`SELECT * FROM changed_customers ORDER BY customer_id` before the `ROLLBACK`.

### Example 2

```sql
WITH current_dim AS (
  SELECT
    dc.*
  FROM
    dim_customer dc
  WHERE
    dc.is_current
),
diffs AS (
  SELECT
    s.customer_id,
    s.full_name,
    s.country,
    s.segment
  FROM
    changed_customers s
    JOIN current_dim dc ON dc.customer_id = s.customer_id
  WHERE
    coalesce(s.full_name, '') <> coalesce(dc.full_name, '')
    OR coalesce(s.country, '') <> coalesce(dc.country, '')
    OR coalesce(s.segment, '') <> coalesce(dc.segment, '')
),
closed AS (
  UPDATE
    dim_customer dc
  SET
    valid_to = CURRENT_DATE -1,
    is_current = FALSE
  FROM
    diffs d
  WHERE
    dc.customer_id = d.customer_id
    AND dc.is_current
  RETURNING
    dc.customer_id)
  -- A new version carries every attribute, including the Day 52 country_sk.
  -- The scalar lookup returns NULL for a country missing from dim_country (the
  -- NOT NULL rule then rejects the whole statement, so no row is closed) and
  -- raises an error if dim_country repeats a code. An inner join would instead
  -- drop that customer's new version after its old row had been closed.
  INSERT INTO dim_customer (customer_id, full_name, country, segment, country_sk, valid_from, valid_to, is_current)
  SELECT
    d.customer_id,
    d.full_name,
    d.country,
    d.segment,
    (
      SELECT
        co.country_sk
      FROM
        dim_country co
      WHERE
        co.country_code = d.country), CURRENT_DATE, NULL, TRUE
  FROM
    diffs d;
```

**How to read it:** Example 2 is a data-changing CTE chain, not a displayed query result. The CTEs `current_dim`, `diffs`, and `closed` identify changed customers, close each former current row, and insert one successor into `dim_customer` that carries every attribute, including the `country_sk` that Day 52 Exercise 1 made mandatory. Because the close and the insert are one statement, a failed `country_sk` lookup undoes the close as well. Read the command tag for the inserted-row count, then verify one current version per customer and non-overlapping validity periods; a successful command tag alone does not prove Type-2 history is correct.

**Expected result/shape:** The whole chain prints one tag, `INSERT 0 10`; the `UPDATE` inside `closed`
reports nothing of its own, yet it runs, because PostgreSQL executes every
data-changing CTE once and to completion even when the final statement never
reads it. Afterward customers 1 to 10 each own two rows: the original, now
closed at yesterday, and a new one from today with `valid_to` NULL. The first
check prints 511 versions on our run (500 originals, the -1 unknown member
from the Day 52 solution and 10 new rows) with 0 mismatched country keys. The
second lists customers 1 to 10 with 2 versions each; `first_seen` is the
customer's `created_at` date (8 October 2026 for customer 1, 9 May 2026 for
customer 10) and `last_seen` is today, since the open row's NULL `valid_to`
becomes `CURRENT_DATE`.

## Learning objectives

- Close one current dimension version and insert its successor atomically.
- Resolve facts to the dimension version valid on their event date.

## Vocabulary and concepts

- **SCD Type 2:** slowly changing dimension design that preserves version
  history as new rows.
- **Business key:** stable source identity shared by all versions.
- **Validity interval:** the dates or timestamps for which one version applies.

## Worked example / walkthrough

For one changed customer, locate exactly one current row, set its `valid_to` to
the day before the new version, and insert the successor at `CURRENT_DATE`.
Then as-of join a fact date using inclusive bounds and verify it resolves to one
surrogate key, not zero and not two.

## Exercises

Complete these in the [learner SQL](../day53_project3_dwh_part2_scd.sql):

1. Map facts to the effective SCD Type 2 version.
   **Inputs/evidence:** For sql-53 Exercise 1, map every `training.order_items` row to `dim_date`, to the `dim_customer` version whose `valid_from <= order_date::date <= COALESCE(valid_to, 'infinity')`, and to the matching `dim_product` version, after the Exercise 2 change gave customer 1 a second version.
   **Expected result/shape:** For sql-53 Exercise 1, expected output: the temporary table `fact_sales_temporal_solution`, one row per `order_item_id`, with columns `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; the check row reports `mapped_fact_rows = 13085`, `source_item_rows = 13085`, and `customer_versions = 2`.
   **Verify:** For sql-53 Exercise 1, confirm that `SELECT COUNT(DISTINCT order_item_id) FROM fact_sales_temporal_solution` also returns 13,085, so no item was duplicated by overlapping versions or lost in a validity gap; for customer 1, check that orders dated before the change map to the closed version's `customer_sk` and later orders to the current one.
   **Data check:** On our run the distinct count is 13,085, and customer 1's 15 order lines split 5 and 10: the two orders before 26 October (the first on 16 October) map to `customer_sk` 1, and the three from 26 October to 17 November map to the gold version. The split moves with `CURRENT_DATE`, because the change takes effect 30 days before today.
2. Add/set audit columns on inserts and closes.
   **Inputs/evidence:** For sql-53 Exercise 2, add `updated_by text NOT NULL DEFAULT CURRENT_USER` and `updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP` to `dim_customer` and `dim_product`, then apply one staged segment change for customer 1 as an SCD2 close-and-insert whose new version also carries `country_sk`.
   **Expected result/shape:** For sql-53 Exercise 2, expected output: two `ALTER TABLE` command tags for the audit columns, then `SELECT 1`, `UPDATE 1`, and `INSERT 0 1` for the staged change; the closed and the new customer 1 rows both carry `updated_by = 'day53_solution'`.
   **Verify:** For sql-53 Exercise 2, query `information_schema.columns` for `table_schema = 'dwh'` and both tables and confirm the two new columns with `is_nullable = 'NO'`; after a savepoint, `UPDATE dim_customer SET updated_by = NULL WHERE customer_id = 1` must fail with SQLSTATE `23502` (not-null violation), then roll back to the savepoint.
   **Data check:** `information_schema.columns` returns four rows, both columns on both tables, all with `is_nullable = 'NO'`, and the NULL update fails with `null value in column "updated_by" of relation "dim_customer" violates not-null constraint`. The 500 rows the change did not touch hold the role that ran `ALTER TABLE` (`postgres` in our container, `admin` in the classroom), because adding a column with a default fills existing rows. The gold row's `customer_sk` was 512 on our run rather than the next number after 500: Day 52's rejected test insert and one earlier learner run had drawn from `dim_customer_sk_seq`, and `ROLLBACK` never returns sequence values.
3. Diagnose same-day date-grain version closure.
   **Inputs/evidence:** For sql-53 Exercise 3, list customer 1's versions from `dim_customer` with `valid_from`, `valid_to`, and the flag `invalid_range = (valid_to IS NOT NULL AND valid_to < valid_from)`.
   **Expected result/shape:** For sql-53 Exercise 3, expected output: two rows ordered by `valid_from`, both with `invalid_range = false`; the closed version ends on `CURRENT_DATE - 31`, the day before the current version begins on `CURRENT_DATE - 30`.
   **Verify:** For sql-53 Exercise 3, after a savepoint, apply a second change for customer 1 with the same effective date: closing the current version at `effective_date - 1` gives it a `valid_to` earlier than its `valid_from`, so the flag becomes `true` for that row. That is why date-grain versions cannot order two changes on one date.
   **Data check:** On our run the two rows span 8 to 25 October 2026 and 26 October onward. A second change also effective 26 October would close the gold row at 25 October, one day before its own `valid_from`, and `invalid_range` turns `t` for that row only.
4. Detect overlapping effective ranges per natural key.
   **Inputs/evidence:** For sql-53 Exercise 4, self-join `dim_customer` on `customer_id` with `b.customer_sk > a.customer_sk`, keeping pairs whose inclusive ranges overlap: `a.valid_from <= COALESCE(b.valid_to, 'infinity')` and `b.valid_from <= COALESCE(a.valid_to, 'infinity')`.
   **Expected result/shape:** For sql-53 Exercise 4, expected output: zero rows with columns `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`, ordered by `a.customer_id, version_a, version_b`, because every customer's versions are disjoint after the Exercise 2 change.
   **Verify:** For sql-53 Exercise 4, after a savepoint, set the closed version's `valid_to` to the new version's `valid_from` and confirm that exactly one row appears for `customer_id = 1`; each overlapping pair is reported once because of `b.customer_sk > a.customer_sk`.
   **Data check:** With the standard row's `valid_to` moved to 26 October, the self-join returns `customer_id` 1 with versions 1 and 512 on our run. The Exercise 1 count would still read 13,085 with that overlap, because customer 1 ordered nothing on 26 October: a one-day overlap duplicates only facts dated that day, which is why the pairwise check exists beside the count.
5. Make an unchanged-source rerun idempotent.
   **Inputs/evidence:** For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
   **Expected result/shape:** For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
   **Verify:** For sql-53 Exercise 5, confirm that `staged_customer_change` holds one row (customer 1, `Customer 1`, US, `gold`) and that customer 1's current `dim_customer` row carries the same three values, so the count is 0. Then, after a savepoint, run `UPDATE staged_customer_change SET segment = 'silver'` and rerun the comparison: it reports 1 before any close or insert runs; roll back to the savepoint.
   **Data check:** Changing the staged segment to silver makes the comparison report 1. Comparing against `training.customers` instead also reports 1 with nothing altered, because the source still says standard for customer 1 while the dimension says gold; that false change is why the replay reads `desired_customer_state`.
6. Define a same-day change sequence policy.
   **Inputs/evidence:** For sql-53 Exercise 6, model two same-day versions with half-open `tstzrange` values, `[2026-01-15 09:00+00, 2026-01-15 12:00+00)` and `[2026-01-15 12:00+00, infinity)`, instead of inclusive date ranges.
   **Expected result/shape:** For sql-53 Exercise 6, expected output: one row with columns `first_version` and `second_version` showing the two ranges; they meet at 12:00 without overlapping, because the `)` upper bound is exclusive.
   **Verify:** For sql-53 Exercise 6, confirm that `first_version && second_version` returns `false`, `first_version -|- second_version` (adjacent) returns `true`, and that `'2026-01-15 12:00+00'::timestamptz <@ second_version` returns `true` while the same test against `first_version` returns `false`.
   **Data check:** The three tests print `f`, `t` and `t`, and the membership test against `first_version` prints `f`. `upper(first_version)` and `lower(second_version)` are both `2026-01-15 12:00:00+00`, so noon belongs to the second version alone. For contrast, PostgreSQL stores `daterange('2026-10-08', '2026-10-25', '[]')` as `[2026-10-08,2026-10-26)`: discrete date ranges are rewritten half-open, while `tstzrange` keeps the bounds you write.

Check multiple-current versions, gaps, and overlaps.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Temporal fact mapping count must equal source item count.
- **Writing the answers below the learner's own change:** the learner
  section already versioned customer 1 today, so pasting the solution's
  statements above the learner `ROLLBACK` closes that new row at 25 October,
  before it began. On our run that version showed `invalid_range` true, the
  overlap check returned one pair, and the fact table held 13,095 rows for
  13,085 lines, because customer 1's ten later lines matched two versions.
  Run the exercises on the Day 52 state, as the solution file does, or
  remove the learner change first.
- **Joining on `is_current`:** after the change, a join on `customer_id`
  plus `dc.is_current` sends all 15 of customer 1's lines to the gold version,
  including the 5 sold while customer 1 was standard. The count still reads
  13,085, so only a per-customer check exposes it.
- **Closing at today instead of yesterday:** `valid_to = CURRENT_DATE` makes
  the old and new rows both valid today, and any order dated today would map
  twice. Keep the `- 1`.
- **Running without Day 52:** when `dwh.dim_customer` is missing, the
  solution's `DO` block stops with
  `Run Day 52 (the learner file or day52_solutions.sql) before Day 53`; run
  and commit Day 52, then rerun the whole file.
- **`null value in column "country_sk"` (SQLSTATE `23502`):** a new version
  needs the Day 52 country key. Look it up in `dim_country` for the version's
  own `country`, and add a missing country code to `dim_country` before the
  load rather than dropping the `NOT NULL` rule.
- Anything else goes through the
  [first-error checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  before you edit a later statement.

## Self-check

- Are close and insert operations in one atomic transaction?
- Does temporal fact mapping preserve the source fact count exactly?

## Next step

Continue in the same database to
[Day 54; warehouse aggregates](day54_project3_dwh_part3_aggregations.md).

## Deep dive and reference

## Project focus

- Detect changed customer and product attributes.
- Close the old current row and insert a new version.
- Map historical facts to the dimension version valid on the fact date.

## Preconditions and state

Run Day 52 first in the same database, either its learner file or
`day52_solutions.sql`. Day 53 reads the committed `dwh` schema but performs its
changes inside a transaction and rolls them back.

The file's first statements restore the Day 52 Exercise 1 contract: every
`dim_customer` version has a `NOT NULL` `country_sk` that points at
`dim_country`. They are idempotent. After a Day 52 run that completed
Exercise 1, they print two `NOTICE` lines, `INSERT 0 0`, and `UPDATE 0`; after
the Day 52 base load alone, they create and backfill the link (`INSERT 0 8`,
`UPDATE 500`) inside the rolled-back transaction. `IF NOT EXISTS` adopts an
existing table without checking its shape, so the SCD2 insert looks
`country_sk` up with a scalar subquery: a country missing from `dim_country`
yields NULL, which the `NOT NULL` rule rejects with SQLSTATE `23502`, and a
repeated country code raises SQLSTATE `21000`.

The learner stages deterministic changes for ten customers and ten products.
For each changed business key, the current row closes at `CURRENT_DATE - 1`,
and the replacement starts at `CURRENT_DATE`.

## Practice map

Exercise 2 has to run first: its backdated change creates the second
customer 1 version that Exercises 1, 3, 4 and 5 inspect, which is why the
solution file places it above Exercise 1. Exercise 6 stands alone on two
literal ranges. Everything sits inside one transaction that ends in
`ROLLBACK`, so Day 54 still reads the Day 52 warehouse whatever you try here.
The prompts, expected tags and checks above are the contract both solution
files answer.

## SCD reasoning

- Close and insert are one atomic transaction.
- `customer_id` and `product_id` are business keys; their surrogate keys identify
  versions.
- Inclusive bounds require the old row to end one day before the new row starts.
- A production dimension should prevent more than one current row per business
  key and overlapping validity ranges.

## Validation and limits

- Temporal fact mapping count must equal source item count.
- A lower count signals a date/version gap; a higher count signals overlapping
  versions.
- Audit defaults cover inserts but do not explain update actors; set them on
  close operations too.
- The course uses date-grain validity. Timestamp-effective changes require a
  different boundary model.

## Ask an AI tutor about this lesson

Boundary dates are where a tutor earns its keep today. Write down customer
1's two validity intervals and the date of each of its orders, then ask the
tutor which version each order should map to and why. The
[tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) say what to share
and what to keep private. Open with this request:

```text
Tutor me through sql-53: Data Warehouse Project, Part 2: Slowly Changing Dimensions.

I have completed the direct catalog prerequisite: `sql-52`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day53_project3_dwh_part2_scd.md
- Answer-free learner SQL: sql/postgres-60day/day53_project3_dwh_part2_scd.sql

Key terms to teach in context: SCD Type 2, Business key, Validity interval. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For one changed customer, locate exactly one current row, set its `valid_to` to the day before the new version, and insert the successor at `CURRENT_DATE`. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key, not zero and not two.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-53/ working copy. Never point setup, reset, DDL, or DML
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
