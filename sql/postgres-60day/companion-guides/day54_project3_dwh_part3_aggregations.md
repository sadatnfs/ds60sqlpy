# Day 54: Data Warehouse Project, Part 3: Aggregates

## How to run this lesson

Open **sql-54** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit
`.learning/sql/sql-54/lesson/workspace/sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql`.
The script needs the `dwh` star schema that Day 52 committed to
`advanced_sql_training`; if `fact_sales` is missing, run the Day 52 learner
file or `day52_solutions.sql` first. Inside `BEGIN` and `ROLLBACK` it creates
two aggregate tables, loads them from the facts and runs two data-quality
queries, so a clean `psql` run prints `CREATE TABLE`, `INSERT 0 276`,
`INSERT 0 3912` and two empty result sets. The
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) has the
launcher steps, and its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
covers the optional notebook.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Review [Day 53; slowly changing dimensions](day53_project3_dwh_part2_scd.md) The Day 52 warehouse must exist in the database; Day 53's SCD changes were rolled back and are not needed here.
  and retain the committed Day 52 warehouse in the same database. Day 54 does
  not depend on Day 53's rolled-back changes.
- **Artifacts:** [learner SQL](../day54_project3_dwh_part3_aggregations.sql) ·
  [solution reasoning](../solutions/day54_solutions.md) ·
  [executable solution](../solutions/day54_solutions.sql)

## A beginner's mental model for this lesson

An **aggregate table** stores a summary that a report would otherwise compute
from `fact_sales` every time. Day 52's fact table has 13,085 order lines over
46 months, 6 product categories and 438 customers. Summed by (year, month,
category) that becomes 276 rows; by (year, month, customer_sk) it becomes
3,912 rows. Each aggregate is only trustworthy if its primary key matches the
grouping that fills it and if its revenue still matches the facts after every
load.

Refreshing means rebuilding one period: delete that month's rows from every
aggregate, insert them again from facts, and do both inside one transaction so
nobody sees a half-built month. Done this way the refresh is an **idempotent
refresh**: running it twice leaves identical rows. A **late-arriving fact**,
an order line that lands after its month was summarized, breaks that promise
for the older month unless that month is refreshed too. Read every query here
in [logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both definitions come from the learner script and run in its transaction
before the full loads.

### Example 1

```sql
CREATE TABLE agg_sales_category_month (
  year INT NOT NULL,
  month INT NOT NULL,
  category TEXT NOT NULL,
  revenue NUMERIC(14, 2) NOT NULL,
  PRIMARY KEY (year, month, category)
);
```

**How to read it:** The table has no measure besides `revenue`; its whole design is the
composite primary key `(year, month, category)`. That key states the grain:
one row per category per calendar month, so a second load of the same month
fails instead of doubling revenue.

**Expected result/shape:** `psql` prints `CREATE TABLE`. Confirm the key with
`\d agg_sales_category_month`, which lists `agg_sales_category_month_pkey`.
The full load that follows inserts 276 rows, every category in each of the
46 months, and a second identical `INSERT` would stop with a duplicate-key
error.

### Example 2

```sql
CREATE TABLE agg_sales_customer_month (
  year INT NOT NULL,
  month INT NOT NULL,
  customer_sk INT NOT NULL,
  revenue NUMERIC(14, 2) NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);
```

**How to read it:** Same pattern at a finer grain: `customer_sk` replaces `category` in both the
columns and the key. Unlike the solution's version, this one has no
`REFERENCES dim_customer`, which is why the script ends with an orphan-key
check.

**Expected result/shape:** `psql` prints `CREATE TABLE`; the later load inserts 3,912 rows, the same
number as customer and order-month pairs in the course orders. The orphan
query returns zero rows, but only because the load joined real facts, not
because a constraint enforces it.

## Learning objectives

- Build aggregate tables with an enforced monthly grain.
- Refresh one period idempotently and reconcile it with warehouse facts.

## Vocabulary and concepts

- **Aggregate table:** persisted summaries at a coarser fact grain.
- **Idempotent refresh:** a rebuild whose repeated execution yields the same
  target-period rows.
- **Late-arriving fact:** a fact received after its reporting period was first
  built.

## Worked example / walkthrough

For one target year/month, delete category, customer, and product aggregate
rows, rebuild each independently from facts, and commit or roll back the whole
unit together. Reconcile each table's period revenue with a fact-only control
before considering the refresh successful.

## Exercises

Complete these in the
[learner SQL](../day54_project3_dwh_part3_aggregations.sql):

1. Add and validate `agg_sales_product_month`.
   **Inputs/evidence:** For sql-54 Exercise 1, create `agg_sales_product_month` with `PRIMARY KEY (year, month, product_sk)` and load it by grouping the 13,085 `fact_sales` rows joined to `dim_date` on `date_key` by year, month, and `product_sk`, storing `ROUND(SUM(amount), 2)` as `revenue`, `SUM(quantity)` as `units`, and `COUNT(DISTINCT order_id)` as `orders`; then reconcile it against an independent per-month sum of `fact_sales`.
   **Expected result/shape:** For sql-54 Exercise 1, expected output: the load inserts one row per year, month, and `product_sk` (6,741 rows on our load), and the reconciliation returns one row per month, 46 rows, with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, every `difference` 0.00. The final order is `a.year, a.month`. The solution file runs this full build inside `SAVEPOINT exercise_1` and rolls back to it, so Exercise 2 starts from an empty table.
   **Verify:** For sql-54 Exercise 1, confirm that no (year, month, `product_sk`) appears twice, that February 2023 holds 6 product rows with 1,203.26 revenue and 17 units, and that November 2026 holds 234 product rows with 85,364.73 revenue. In the transaction, add 1.00 to the revenue of product 69 in February 2023: the reconciliation shows that month alone with `difference` 1.00. Then delete the February 2023 rows: the inner join drops to 45 months and reports no difference at all, which is the gap Exercise 5 closes.
   **Data check:** The solution file builds every month inside `SAVEPOINT exercise_1`: the table holds 6,741 product and month rows on our load, and the reconciliation returns 46 months, all with difference 0.00, before `ROLLBACK TO SAVEPOINT` empties it again for Exercise 2. Each fact amount already has two decimals, so rounding per product never drifts from the month total.
2. Refresh all aggregates for a supplied year/month.
   **Inputs/evidence:** For sql-54 Exercise 2, write `refresh_sales_aggregates_solution(p_year, p_month)` so it deletes that month from `agg_sales_category_month`, `agg_sales_customer_month`, and `agg_sales_product_month` and reinserts it from `fact_sales` joined to `dim_date` (and to `dim_product` for the category); call it for the newest fact month, then reconcile the product aggregate against `fact_sales` for the months it holds.
   **Expected result/shape:** For sql-54 Exercise 2, expected output: the procedure returns nothing; the call leaves 6 category rows, 73 customer rows, and 234 product rows, all for November 2026 on our load, and the reconciliation returns 1 row with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` (2026, 11, 85,364.73, 85,364.73, 0.00 on our load). The query has no `ORDER BY` because it returns one month.
   **Verify:** For sql-54 Exercise 2, check that all three tables sum to 85,364.73 revenue, that the category `units` total 1,399, and that the customer `orders` total 151, the same as `COUNT(DISTINCT order_id)` for that month in `fact_sales`. Call the procedure again for 2026-11 and then for 2030-01, a month with no facts: the counts stay 6, 73, and 234. Call it for 2023-02: the counts become 12, 75, and 240, and the reconciliation returns 2 rows, both with `difference` 0.00.
   **Data check:** After the procedure refreshes the newest loaded month, the reconciliation returns one row for that month with difference 0.00. The month is partial, since order dates stop near the load date, so its revenue is far below a full month's.
3. Explain late-fact effects on closed months.
   **Inputs/evidence:** For sql-54 Exercise 3, group the 13,085 `fact_sales` rows joined to `dim_date` by year and month, counting the fact rows and taking `MAX(date_actual)` as the latest loaded day of each month.
   **Expected result/shape:** For sql-54 Exercise 3, expected output: 46 rows, one per year and month from February 2023 to November 2026, with columns `year`, `month`, `fact_rows`, and `latest_fact_date`, ordered by `dd.year DESC, dd.month DESC`. On our load October 2026 has 965 rows ending 2026-10-31, the partial November 2026 has 468 rows ending 2026-11-23, and February 2023 has 6 rows, all on 2023-02-13.
   **Verify:** For sql-54 Exercise 3, confirm that `fact_rows` adds up to 13,085. In a transaction, insert a late fact for order 3739, product 69, `order_item_id` 999999, `date_key` 20230220, and amount 35.53: February 2023 rises to 7 rows with `latest_fact_date` 2023-02-20. If February 2023 was already refreshed, the Exercise 5 reconciliation now shows it with 1,203.26 against 1,238.79, a `difference` of -35.53, until the procedure is called for 2023-02 again; `ROLLBACK`.
   **Data check:** Expect 46 periods, newest first. Full recent months hold 800 to 965 fact rows, the newest partial month fewer, and the oldest month only a handful, with `latest_fact_date` showing the last loaded day of each. A late fact in any listed month needs that month refreshed.
4. Implement transactional delete/insert for one month.
   **Inputs/evidence:** For sql-54 Exercise 4, after the Exercise 2 call has deleted and reinserted the newest month inside the open transaction, group `agg_sales_category_month` by year and month, counting the category rows and summing their revenue.
   **Expected result/shape:** For sql-54 Exercise 4, expected output: one row per refreshed month, 1 row on our load (2026, 11, 6 category rows, 85,364.73 revenue), with columns `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
   **Verify:** For sql-54 Exercise 4, list the six categories for the month (Apparel 14,026.26, Beauty 13,151.38, Books 15,823.05, Electronics 13,811.36, Home 12,125.38, and Sports 16,427.30 on our load) and confirm that they add up to the reported revenue. Call the procedure for 2023-02 as well: the query returns 2 rows, 2026-11 first and then 2023-02 with 6 rows and 1,203.26. After the file's `ROLLBACK`, `to_regclass('dwh.agg_sales_category_month')` returns `NULL`.
   **Data check:** The category aggregate holds one month, the refreshed one, with 6 category rows and the same revenue that Exercise 2 reconciled. After `ROLLBACK`, `to_regclass('dwh.agg_sales_category_month')` returns `NULL`, which proves the transaction removed the table and the procedure's writes together.
5. Make missing-side reconciliation NULL-safe.
   **Inputs/evidence:** For sql-54 Exercise 5, sum `agg_sales_category_month` revenue by year and month in `aggregate_total`, sum the `fact_sales` amounts joined to `dim_date` by year and month in `fact_total`, and `FULL JOIN` the two on year and month, keeping the rows where `a.revenue IS DISTINCT FROM f.revenue`.
   **Expected result/shape:** For sql-54 Exercise 5, expected output: 45 rows on our load, one for every fact month the aggregate does not hold (all but the refreshed November 2026), with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, ordered by `year, month`. Each row has a `NULL` `aggregate_revenue` and a `difference` equal to minus its fact revenue, for example -1,203.26 for February 2023.
   **Verify:** For sql-54 Exercise 5, call the procedure for 2023-02 and confirm that the result drops to 44 rows, now starting at March 2023. Then insert a category row for 2030-01 (Books, 10.00 revenue, 1 unit) that has no facts: it appears with a `NULL` `fact_revenue` and a `difference` of 10.00, for 45 rows. An inner join with `<>` would return neither kind of row; `ROLLBACK`.
   **Data check:** Expect 45 rows: every month except the refreshed one, each with a `NULL` aggregate revenue and a difference equal to minus that month's fact revenue. An inner join with `<>` would return nothing and wrongly report a clean reconciliation.
6. Prove the refresh is idempotent.
   **Inputs/evidence:** For sql-54 Exercise 6, copy `agg_sales_category_month` into the temporary table `aggregate_snapshot_before`, call the refresh again for the same newest month, and compare the snapshot with the live table using `EXCEPT` in both directions, labeling each side.
   **Expected result/shape:** For sql-54 Exercise 6, expected output: 0 rows on the course data, because the second refresh deletes and rewrites the same 6 category rows with the same values. The final columns are `side`, `year`, `month`, `category`, `revenue`, and `units`, where `side` is `before_minus_after` or `after_minus_before`; the query has no `ORDER BY`.
   **Verify:** For sql-54 Exercise 6, check that the snapshot and the live table both hold 6 rows with 85,364.73 revenue after the rerun. Then, in a transaction, insert a late November 2026 fact (order 3739, product 69, `order_item_id` 999999, `date_key` 20261120, amount 35.53) between the snapshot and the rerun: the query returns 2 Home rows, `before_minus_after` with 12,125.38 and 209 units and `after_minus_before` with 12,160.91 and 210 units, which proves that the comparison catches a real change; `ROLLBACK`.
   **Data check:** Both directions of the comparison are empty: rerunning the refresh deleted and rewrote the same 6 category rows with the same revenue and units, so no row differs before and after.

Refresh twice and compare row counts and totals.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Every refreshed month's aggregate
  revenue must equal fact revenue. Reconcile right after each refresh and treat
  any nonzero difference as a failed load.
- **`relation "fact_sales" does not exist`:** the Day 52 warehouse is missing
  or was dropped. Rerun Day 52, then this file.
- **Duplicate key on refresh:** the month was inserted again without deleting
  it first. The primary key is doing its job; delete the period before the
  insert.
- **A clean reconciliation that hides missing months:** joining aggregate and
  fact totals with an inner join drops a month missing on either side. Use a
  `FULL JOIN` and `IS DISTINCT FROM`, as in Exercise 5.
- **Half-refreshed month:** deleting in one statement and inserting in a later
  autocommitted one lets readers see an empty month. Keep both in one
  transaction or procedure call.
- More recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does each primary key exactly match the documented aggregate grain?
- Can a late fact be incorporated through a deliberate period backfill?

## Next step

Continue to [Day 55; BI drill-downs](day55_project4_bi_part1.md).

## Deep dive and reference

## Project focus

- Build monthly category and customer aggregate tables.
- Add a monthly product aggregate with a declared primary-key grain.
- Refresh one period idempotently and reconcile it to facts.

## Preconditions and state

Run Day 52 first in the same database, either its learner file or
`day52_solutions.sql`; Day 54 uses only the base warehouse. The learner creates
its aggregate tables, loads them, performs data-quality checks, and rolls the
entire Day 54 transaction back.

The starter grains are `(year, month, category)` and
`(year, month, customer_sk)`. Revenue is summed from `fact_sales.amount`; date
attributes come from `dim_date`.

## Practice map

Exercise 1 adds a product-month aggregate, Exercises 2 and 4 refresh one month
across all three tables, Exercise 3 inventories the loaded periods that late
facts could touch, Exercise 5 makes the reconciliation catch missing months
and Exercise 6 proves a rerun changes nothing. Each prompt above also appears,
word for word, in the learner file.

## Refresh design

- Delete and insert all related aggregates in one transaction.
- A period rebuild is idempotent when the primary-key grain is correct.
- Filter facts through `dim_date.year` and `dim_date.month`.
- Aggregate each side independently before reconciliation to prevent fanout.

## Validation and limits

- Every refreshed month's aggregate revenue must equal fact revenue.
- Orphan surrogate keys must be zero.
- Late facts require rerunning affected periods or a deliberate backfill window.
- The compact seed does not need aggregates for speed; this is a warehouse
  serving-pattern exercise.
- Day 54 does not require rolled-back Day 53 audit/SCD changes.

## Ask an AI tutor about this lesson

A tutor is handy for talking through why a late order line from last spring
leaves a closed month stale, but the reconciliation numbers must come from
your own run. If you use one, paste this prompt and read the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-54: Data Warehouse Project, Part 3: Aggregate Tables.

I have completed the direct catalog prerequisite: `sql-53`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day54_project3_dwh_part3_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql

Key terms to teach in context: Aggregate table, Idempotent refresh, Late-arriving fact. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-54/ working copy. Never point setup, reset, DDL, or DML
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
