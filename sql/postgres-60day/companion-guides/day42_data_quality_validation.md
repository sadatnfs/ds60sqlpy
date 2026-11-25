# Day 42: Data Quality and Validation

## How to run this lesson

Open **sql-42** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit
`.learning/sql/sql-42/lesson/workspace/sql/postgres-60day/day42_data_quality_validation.sql`.
The file only reads the course tables in `advanced_sql_training`, wrapped in
`BEGIN` and `ROLLBACK`. A clean `psql` run prints six result sets: one profile
row (500 customers, 0 null emails, 0 null countries) and five checks that come
back empty. Empty is the passing answer for every check in this lesson. The
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) has the
launcher steps, and its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
covers the optional notebook.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 41; complex aggregations](day41_complex_aggregations.md) Day 41's grouped counts and `HAVING` filters are the main tools reused here.
- **Artifacts:** [learner SQL](../day42_data_quality_validation.sql) ·
  [solution reasoning](../solutions/day42_solutions.md) ·
  [executable solution](../solutions/day42_solutions.sql)

## A beginner's mental model for this lesson

A data-quality check is a query that returns the rows breaking a rule. Each
rule states an **invariant**, something that should always be true: every
payment belongs to an order, no order total is negative, no two customers
share an email once case and spaces are ignored. On a clean load every check
returns zero rows or a zero count, and that zero is the evidence.

Some rules are already enforced. `orders.customer_id` and both
`order_id` columns in `order_items` and `payments` have foreign keys, so an
**orphan** (a child row whose parent is missing) cannot be inserted today. The
checks still run because constraints can be dropped, disabled during a bulk
load or missing in a copy of the data. Other rules have no constraint at all:
`customers.email` is nullable, and its `UNIQUE` constraint compares exact text,
so `Ann@Example.com` and `ann@example.com ` could both be stored.

Each check also needs a stated **DQ result grain**. "2 duplicate groups" and
"5 duplicate customers" can describe the same data, so a report names what it
counts. Read every query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both profiling queries come from the start of the learner script and run in
its transaction.

### Example 1

```sql
SELECT
  'customers' AS table,
  COUNT(*) AS rows,
  SUM(
    CASE WHEN email IS NULL THEN
      1
    ELSE
      0
    END) AS null_emails,
  SUM(
    CASE WHEN country IS NULL THEN
      1
    ELSE
      0
    END) AS null_country
FROM
  customers;
```

**How to read it:** There is no `GROUP BY`, so all 500 customers collapse into one row. Each
`SUM(CASE WHEN ... IS NULL THEN 1 ELSE 0 END)` counts the rows where one
column is missing, and the literal `'customers' AS table` labels the row so
the same shape could be stacked for other tables.

**Expected result/shape:** One row: `customers`, 500, 0, 0. `country` is `NOT NULL`, so its zero is
guaranteed; `email` is nullable, so its zero is a fact about this load only.

### Example 2

```sql
SELECT
  email,
  COUNT(*) AS cnt
FROM
  customers
GROUP BY
  email
HAVING
  COUNT(*) > 1
ORDER BY
  cnt DESC;
```

**How to read it:** The query groups customers by the exact stored email and keeps only groups
with more than one member. Because the grouping uses the raw text, it can only
find what the `UNIQUE (email)` constraint already prevents.

**Expected result/shape:** Zero rows on a fresh load, and zero rows will stay the answer even after a
case variant such as `CUSTOMER1@example.com` is added. Exercise 5 groups by
`lower(trim(email))` to catch that.

## Learning objectives

- Encode repeatable quality rules with stable names, grains, and failure counts.
- Separate observed failures from remediation policy.

## Vocabulary and concepts

- **Invariant:** a condition expected to remain true for valid data.
- **Orphan:** a foreign-key-like value with no matching parent.
- **DQ result grain:** whether a check counts failing rows, keys, or duplicate
  groups.

## Worked example / walkthrough

Normalize email with `lower(trim(email))`, group it, and return groups with
`COUNT(*) > 1`. Keep the raw emails in a separate detail query: the summary
counts duplicate groups, while remediation needs the member records.

## Exercises

Complete these in the [learner SQL](../day42_data_quality_validation.sql):

1. Build a named core-table validation report.
   **Inputs/evidence:** For sql-42 Exercise 1, write seven single-count queries joined with `UNION ALL`: `NULL` emails and duplicate `lower(trim(email))` keys in `customers`, negative totals and orphan `customer_id` values in `orders`, orphan orders or products and bad quantity or discount in `order_items`, and negative or orphan rows in `payments`; orphans are found with `LEFT JOIN ... WHERE parent key IS NULL`.
   **Expected result/shape:** For sql-42 Exercise 1, return exactly seven rows, one per `check_name`, and every `failing_rows` value is 0 on a fresh load because the course constraints already block these faults. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name` and `failing_rows`. The final order is `check_name`.
   **Verify:** For sql-42 Exercise 1, confirm seven distinct `check_name` values, all with 0; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET email = NULL WHERE customer_id = 1` and confirm `customers.null_email` becomes 1 while the other six stay 0, and separately insert a customer with email `' Customer7@Example.com'` and confirm `customers.duplicate_normalized_email` becomes 1.
   **Data check:** All seven checks return 0 on a fresh load. To see one fire, run `UPDATE customers SET email = NULL WHERE customer_id = 1` inside a transaction: `customers.null_email` becomes 1 while the other six stay at 0, and a `ROLLBACK` restores the row.
2. Detect invalid/null customer emails.
   **Inputs/evidence:** For sql-42 Exercise 2, read `customers.customer_id` and `email` and keep a row when `email IS NULL` or when `email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'`; the explicit `NULL` branch is needed because a regex test on `NULL` is unknown, not true.
   **Expected result/shape:** For sql-42 Exercise 2, return 0 rows on a fresh load, because all 500 addresses have the form `customerN@example.com`; when rows do appear there is one per failing `customer_id`. The final columns are `customer_id` and `email`. The final order is `customer_id`.
   **Verify:** For sql-42 Exercise 2, confirm 0 rows and that `SELECT count(*) FROM customers WHERE email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'` returns 500; then, inside `BEGIN ... ROLLBACK`, set customer 1's email to `'customer1(at)example.com'` and customer 2's to `NULL` and confirm exactly those two rows appear, the second only because of the `email IS NULL` branch.
   **Data check:** Zero rows: every one of the 500 addresses has the form `customerN@example.com`. Store `'customer1(at)example.com'` instead and that customer appears; a `NULL` email also appears, because the `email IS NULL` branch catches what the regex comparison would leave unknown.
3. Explain CHECK behavior for NULL without `NOT NULL`.
   **Inputs/evidence:** For sql-42 Exercise 3, read `information_schema.columns` filtered to `table_schema = 'training'`, tables `orders` and `payments`, and columns `total_amount` and `amount`; the catalog shows `NOT NULL`, which is a separate rule from the `CHECK (amount >= 0)` constraint on `payments`.
   **Expected result/shape:** For sql-42 Exercise 3, return 2 rows, one per (`table_name`, `column_name`): `orders`/`total_amount` and `payments`/`amount`, both with `is_nullable = NO`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
   **Verify:** For sql-42 Exercise 3, confirm the two rows and that `SELECT NULL::numeric >= 0` returns `NULL`, which a `CHECK` treats as a pass; then, inside `BEGIN ... ROLLBACK`, run `ALTER TABLE payments ALTER COLUMN amount DROP NOT NULL`, confirm `INSERT INTO payments (order_id, amount, method) VALUES (1, NULL, 'card')` succeeds, and confirm the same insert with `-1` fails on `payments_amount_check`.
   **Data check:** Two rows: `orders.total_amount` and `payments.amount`, both with `is_nullable = NO`. The `CHECK (amount >= 0)` on payments would let a `NULL` through, since `NULL >= 0` is unknown and a check only rejects false; the separate `NOT NULL` rule is what blocks it.
4. Reconcile order totals with calculated line revenue.
   **Inputs/evidence:** For sql-42 Exercise 4, sum `quantity * unit_price * (1 - discount)` from `order_items` by `order_id` in a `calculated` CTE (4,362 rows, one per order), join it to `orders` on `order_id`, and keep orders whose `ABS(o.total_amount - c.line_total)` exceeds the one-cent tolerance `0.01`.
   **Expected result/shape:** For sql-42 Exercise 4, return 0 rows on a fresh load: 2,855 of the 4,362 orders differ from their line sums, but never by more than 0.0045, because stored totals keep two decimals and discounted line sums keep four. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
   **Verify:** For sql-42 Exercise 4, confirm 0 rows, then replace the test with `o.total_amount <> c.line_total` and confirm 2,855 rows with a maximum absolute difference of 0.0045; finally, inside `BEGIN ... ROLLBACK`, add 0.02 to order 3's `total_amount` and confirm one row: `order_id` 3, `total_amount` 601.75, `line_total` 601.7295, and `difference` 0.0205.
   **Data check:** Zero rows. Drop the tolerance and test `o.total_amount <> c.line_total` instead, and 2,855 of the 4,362 orders appear, none off by more than 0.0045. Stored totals have two decimals while discounted line sums keep four.
5. Retain raw case variants in a normalized-email duplicate report.
   **Inputs/evidence:** For sql-42 Exercise 5, read `customers` rows with a non-`NULL` email, group by `lower(trim(email))`, keep groups with `COUNT(*) > 1`, and report the raw spellings with `array_agg(email ORDER BY email)` next to the normalized key.
   **Expected result/shape:** For sql-42 Exercise 5, return 0 rows on a fresh load, because no two emails differ only by case or surrounding spaces; when duplicates exist there is one row per `normalized_email`, with every raw spelling in `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
   **Verify:** For sql-42 Exercise 5, confirm 0 rows; then, inside `BEGIN ... ROLLBACK`, insert a customer with email `' Customer7@Example.com'` and confirm one row: `normalized_email` = `customer7@example.com`, `raw_variants` = `{customer7@example.com," Customer7@Example.com"}`, and `rows` = 2. The broken version that selects only the normalized key returns the same row without the two spellings.
   **Data check:** Zero rows on a fresh load, because no two emails differ only by case or spaces. Insert a customer with `' Customer7@Example.com'` and one row appears, with `raw_variants` holding both stored spellings and `rows` equal to 2.
6. Detect overlapping inclusive promotion ranges.
   **Inputs/evidence:** For sql-42 Exercise 6, join `promotions` (200 rows) to itself on `product_id` with `b.promotion_id > a.promotion_id`, so each pair is tested once, and keep pairs where `a.start_date <= b.end_date AND b.start_date <= a.end_date`, which treats a shared endpoint date as an overlap.
   **Expected result/shape:** For sql-42 Exercise 6, return 0 rows on a fresh load, because the 200 promotions cover 200 different products; when overlaps exist there is one row per overlapping pair (`promotion_a`, `promotion_b`), not per product. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
   **Verify:** For sql-42 Exercise 6, confirm 0 rows and that `count(DISTINCT product_id)` equals `count(*)` (200) in `promotions`; then, inside `BEGIN ... ROLLBACK`, copy promotion 1 with `start_date = end_date` (touching) and promotion 2 with `start_date = end_date + 1` (a one-day gap) and confirm exactly one pair: promotion 1 with the touching copy, for product 43.
   **Data check:** Zero rows: the 200 promotions each cover a different product, so no product has two ranges to compare. Insert a second promotion for one product starting on another's `end_date` and the pair appears, since both endpoints are inclusive.

For one rule, return both a summary and failing-record detail.

## Self-check

- Does every check expose its name, result grain, expected result, and observed
  failure count?
- Can a zero result be rerun on future data without implying a permanent
  guarantee?

## Next step

Continue to [Day 43; logical backup and recovery](day43_backup_recovery.md).

## Deep dive and reference

## What you will learn

- Profile nulls and normalized duplicates.
- Check referential, range, quantity, and discount invariants.
- Return repeatable validation results with named checks and failure counts.

## How the learner script uses the current schema

The starter profiles `customers.email` and `customers.country`, searches for
duplicate emails, checks `order_items` and `payments` for orphan orders, and
looks for negative order/payment amounts. Foreign keys and checks should keep
many failures at zero, but the queries protect future imports and schema
changes.

## Validation design

- Give each rule a stable `check_name` and `failing_rows`.
- Normalize email with `lower(trim(email))` before duplicate grouping.
- Use anti-joins to test relationships even when foreign keys exist.
- Keep observed failures separate from remediation policy.
- Report the grain: duplicate groups, failing records, and orphan keys are
  different counts.

## Practice map

Exercise 1 gathers seven rules into one report, Exercises 2 and 5 look at
customer emails, Exercise 3 inspects which columns reject `NULL`, Exercise 4
reconciles stored order totals with line sums and Exercise 6 compares
promotion date ranges. Each prompt above also appears, word for word, in the
learner file.

## Pitfalls and validation

- The course email regex is a pragmatic check, not the full email RFC.
- A zero count means the checked rule passed on this snapshot, not that future
  loads are guaranteed clean.
- Do not auto-delete failed rows from a validation query.
- The deterministic seed should return zero for every core failure check and no
  invalid emails.

## Expanded practice lab

Prompts 3-6 progress from constraint semantics to reconciliations and diagnostic
evidence. SQL CHECK constraints pass both TRUE and UNKNOWN, so nullable fields
need a separate `NOT NULL` rule when NULL is invalid.

Reconcile stored totals to line revenue at order grain and use a one-cent
tolerance deliberately. A duplicate report should retain raw email variants.
For inclusive promotion dates, ranges overlap when each start is less than or
equal to the other range's end; compare each pair only once.

## Ask an AI tutor about this lesson

Ask a tutor to describe one bad row per check, then insert each of them
yourself inside a transaction and confirm that only the intended check
fires. The prompt below opens that conversation, and the
[tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) explain how the
course uses tutors:

```text
Tutor me through sql-42: Data Quality and Validation.

I have completed the direct catalog prerequisite: `sql-41`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
- Answer-free learner SQL: sql/postgres-60day/day42_data_quality_validation.sql

Key terms to teach in context: Invariant, Orphan, DQ result grain. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Normalize email with `lower(trim(email))`, group it, and return groups with `COUNT(*) > 1`. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-42/ working copy. Never point setup, reset, DDL, or DML
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
