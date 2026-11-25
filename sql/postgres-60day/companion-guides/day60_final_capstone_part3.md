# Day 60: Final Capstone, Part 3: End-to-End Sign-off

## How to run this lesson

In `./classroom`, pick PostgreSQL, open **sql-60** and choose
**Whole SQL lesson (psql)**. The file wraps four `CREATE OR REPLACE VIEW`
statements and six `CREATE INDEX IF NOT EXISTS` statements in `BEGIN` and
`ROLLBACK`, and the snippet runner would drop that boundary, so nothing you
build here should outlive the run. Your editable copy is saved at
`.learning/sql/sql-60/lesson/workspace/sql/postgres-60day/day60_final_capstone_part3.sql`
in the Docker learning volume. One pass against `advanced_sql_training`
prints, in order: the customer and order quality summaries, two LTV
controls, the Finance budget table (55 rows on our run), the Marketing
retention grid (42 rows), a plain `EXPLAIN` for the Operations query, six
index tags and an `EXPLAIN ANALYZE` of the monthly revenue view. `psql`
halts on the first error, so the first message in the transcript is the one
to fix. The
[study guide's launcher steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom)
cover setup and reset, and the
[contributor notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
is there if you prefer JupyterLab.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 59; stakeholder analytics](day59_final_capstone_part2.md) (whose KPI tables and control totals feed today's sign-off)
  and completed evidence from the full SQL track
- **Artifacts:** [learner SQL](../day60_final_capstone_part3.sql) ·
  [solution reasoning](../solutions/day60_solutions.md) ·
  [executable solution](../solutions/day60_solutions.sql)

## A beginner's mental model for this lesson

Day 60 adds no new SQL feature. It asks whether someone who was not in the
room could rerun your capstone, get the same numbers and tell which of them
to trust. The learner file offers three kinds of proof: quality views that
should report zero problems, a customer LTV view that must reconcile to the
order headers, and plans that show where the time goes.

An **Acceptance criterion** is a condition a query can observe, such as
"`v_dq_customers` reports 0 invalid emails" or "summed LTV minus summed
`orders.total_amount` is 0.00". On our run both held: 500 customers with no
invalid email, country or name, and an LTV total of 2,355,646.89 that
matched the order total to the cent. A criterion no query can check, such as
"dashboards feel fast", has to be rewritten before anyone signs it.

An **Evidence bundle** pairs each claim with its query, the database it ran
against, the printed output and one sentence of interpretation. Dates belong
in it because several results move on their own: the Finance CTEs filter
from `date_trunc('year', now())`, the Operations plan filters on
`now() - interval '180 days'`, and the retention grid takes the six newest
signup months in the data, so the same file prints different rows next
month.

A **Handoff** is the note that lets the next owner operate the work: which
views exist, which indexes were only tried inside the rolled-back
transaction, which numbers follow the clock and who still has to review
what. Exercises 6 and 10 turn parts of that note into rows you can query.

When a result surprises you, read the statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
and count rows after each CTE before you change anything.

## Two worked SQL examples

Both excerpts are the first statements in `day60_final_capstone_part3.sql`
that print rows. They read views the script creates a few lines earlier
inside its `BEGIN`, so pasted alone into a fresh session they fail with
"relation does not exist"; run the whole file.

### Example 1

```sql
SELECT
  *
FROM
  v_dq_customers;
```

**How to read it:** `v_dq_customers` is a one-row summary over every customer. Each column is a
`SUM(CASE ... THEN 1 ELSE 0 END)`: `invalid_email` counts a NULL email or
one that fails the case-insensitive `!~*` pattern
`'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'`, `invalid_country` counts a NULL
or anything other than two uppercase letters, and `invalid_name` counts a
NULL or a name that is blank after `btrim`. `SELECT *` prints those counts
after `total`.

**Expected result/shape:** One row with four columns: `total` 500, and `invalid_email`,
`invalid_country` and `invalid_name` all 0 on the course seed. Zero is the
passing value, so a nonzero count starts a remediation note rather than an
edit to the pattern. On an empty `customers` table `total` would be 0 but
each `SUM(CASE ...)` column would print NULL, because `SUM` over no rows is
NULL.

### Example 2

```sql
SELECT
  *
FROM
  v_dq_orders;
```

**How to read it:** `v_dq_orders` applies the same pattern to `orders`: `total` is `COUNT(*)`,
`negative_amounts` counts rows with `total_amount < 0` and
`missing_customer` counts a NULL `customer_id`. It does not look for zero
amounts, future dates or duplicate orders, so a clean result covers exactly
those two rules and nothing more.

**Expected result/shape:** One row: `total` 4,362, `negative_amounts` 0 and `missing_customer` 0.
The second zero is guaranteed by the schema rather than found by the view,
since `customer_id` is declared `NOT NULL` with a foreign key to
`customers`. The first is an observation: there is no `CHECK` on
`total_amount`, and the smallest amount in the seed is 20.74. Say which is
which in the evidence bundle.

## Learning objectives

- Apply explicit acceptance criteria to data quality, business metrics,
  performance evidence, and documentation.
- Produce a handoff that separates verified results, limitations, and future
  production work.

## Vocabulary and concepts

- **Acceptance criterion:** an observable condition required for sign-off.
- **Evidence bundle:** reproducible query, environment, output, reconciliation,
  and interpretation.
- **Handoff:** documentation that lets another person operate, verify, and
  extend the work safely.

## Worked example / walkthrough

Take customer LTV through the final evidence loop: state one-customer grain and
revenue scope, run the view query, reconcile summed LTV with
`SUM(orders.total_amount)`, capture the result and environment, and record any
exception with owner and next action. Apply the same loop to each deliverable.

## Exercises

Complete these in the [learner SQL](../day60_final_capstone_part3.sql):

1. Classify snapshot-independent versus clock-dependent outputs.
   **Inputs/evidence:** For sql-60 Exercise 1, read the definitions of `v_dq_customers_solution` and `v_customer_ltv_solution` and of the trailing or current-period queries (the learner Finance CTEs and Operations filter call `now()`, and Exercise 4 calls `CURRENT_DATE`), then record each object's clock dependence in an inline `VALUES` fixture with `object_name` and `clock_contract`.
   **Expected result/shape:** For sql-60 Exercise 1, expected output: 3 rows: `v_dq_customers_solution` and `v_customer_ltv_solution` marked `snapshot-independent`, and `trailing/current-period reports` marked `clock-dependent: bind as_of_date`. The final columns are `object_name` and `clock_contract`.
   **Verify:** For sql-60 Exercise 1, inside the solution transaction run `SELECT viewname FROM pg_views WHERE schemaname = 'training' AND definition ~* '(now\(\)|current_date|current_timestamp)'`: it returns 0 rows, which backs both `snapshot-independent` labels. Then create a rolled-back probe view `v_clock_probe AS SELECT CURRENT_DATE AS as_of` and rerun the search: it returns exactly `v_clock_probe`, so the search does detect a clock call.
   **Data check:** The solution lists three entries: `v_dq_customers_solution` and `v_customer_ltv_solution` as snapshot-independent, and "trailing/current-period reports" as clock-dependent with the instruction to bind an `as_of_date`. In the learner file `now()` drives only the Finance CTEs and the Operations filter; every `CREATE VIEW` reads table state alone.
2. Build a named, severity-aware sign-off check result.
   **Inputs/evidence:** For sql-60 Exercise 2, read `invalid_email` from the one-row `v_dq_customers_solution` and compare `SUM(ltv)` from `v_customer_ltv_solution` with `SUM(total_amount)` from `orders`; write each check as one `UNION ALL` branch of `checks` with `check_name`, `observed_value`, `expected_value`, `severity`, and `remediation`, then compute `pass` as `observed_value = expected_value`.
   **Expected result/shape:** For sql-60 Exercise 2, expected output: 2 rows, one per `check_name`: `invalid_customer_emails` (observed 0) and `ltv_reconciles_to_orders` (observed 0.00, the absolute gap between LTV and order totals), both `critical` with `expected_value` 0 and `pass` true. The final columns are `check_name`, `observed_value`, `expected_value`, `severity`, `remediation`, and `pass`. The final order is `severity, check_name`.
   **Verify:** For sql-60 Exercise 2, confirm that `SELECT invalid_email FROM v_dq_customers_solution` returns 0 and that `SUM(ltv)` and `SUM(total_amount)` both return 2,355,646.89, matching the two observed values. In a rolled-back transaction set customer 1's email to `'not-an-email'` (or to NULL): `invalid_customer_emails` then reports observed 1 and `pass` false, so the gate fails on a real defect.
   **Data check:** Both rows are `critical`, so `ORDER BY severity, check_name` falls through to the name: `invalid_customer_emails` (observed 0) prints before `ltv_reconciles_to_orders` (observed 0.00), each with `pass` true. Because `severity` is text, adding `high`, `low` and `medium` checks would sort `medium` after `low`.
3. Remove repeated `LAG` calls while preserving first-month NULL growth.
   **Inputs/evidence:** For sql-60 Exercise 3, read `orders` through two CTEs: `monthly` sums `total_amount` by `date_trunc('month', order_date)::date`, and `with_previous` adds `LAG(revenue) OVER (ORDER BY month)` once as `previous_month`; the outer `SELECT` of `v_monthly_revenue_refactored_solution` derives `month_over_month_growth` from that column.
   **Expected result/shape:** For sql-60 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with `previous_month` and `month_over_month_growth` NULL only on the first row and 13 negative growth values. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
   **Verify:** For sql-60 Exercise 3, compare the refactored view with `v_monthly_revenue_solution` and with the learner `v_monthly_revenue` using `EXCEPT` in both directions: 0 rows each way, and `SUM(revenue)` is 2,355,646.89. In a rolled-back transaction set every February 2023 order's `total_amount` to 0: 2023-02-01 shows `revenue` 0.00, and 2023-03-01 shows `previous_month` 0.00 with NULL growth from `NULLIF` instead of a division error. Deleting the 37 May 2024 orders instead leaves 45 rows and gives 2024-06-01 April's 20,055.03 as `previous_month`, because `LAG` reads the previous row, not the previous calendar month.
   **Data check:** The refactored view returns 46 months, 2023-02-01 through 2026-11-01, with no gaps. The first row has NULL `previous_month` and NULL growth, 2023-03 shows 0.4988, and 13 months are negative, the last being 2026-11 at -0.4984 because November was still open on our run. An `EXCEPT` between the learner view and the refactored one returned 0 rows.
4. Mark an incomplete current month separately.
   **Inputs/evidence:** For sql-60 Exercise 4, read the 46 rows of `v_monthly_revenue_refactored_solution` and add `is_incomplete_month` as `month = date_trunc('month', CURRENT_DATE)::date`.
   **Expected result/shape:** For sql-60 Exercise 4, expected output: 46 rows, one per `month`, newest first, with `is_incomplete_month` true only on the current calendar month (2026-11-01 at 85,364.67 when `CURRENT_DATE` was 2026-11-25) and false on the 45 complete months. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
   **Verify:** For sql-60 Exercise 4, confirm that `COUNT(*) FILTER (WHERE is_incomplete_month)` is 1 of 46 rows and that the flagged month holds `MAX(order_date)`: on the checked load November 2026 had 151 orders over 23 order days against October's 313 over 31. Replace `CURRENT_DATE` with `DATE '2026-10-15'` and the flag moves to 2026-10-01 (170,179.13), which shows the result depends on the clock and needs a bound as-of date.
   **Data check:** Only 2026-11-01 was flagged on our run: 151 orders across 23 order days, against 313 in October. The flag compares with `CURRENT_DATE`, so on 1 December November turns `false` with no data change.
5. Capture and document before/after JSON plan evidence.
   **Inputs/evidence:** For sql-60 Exercise 5, run `SELECT * FROM v_monthly_revenue_refactored_solution ORDER BY month DESC LIMIT 12` alone first (12 rows, 2026-11-01 back to 2025-12-01), then wrap the same statement in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` with seed rows, settings, and statistics unchanged.
   **Expected result/shape:** For sql-60 Exercise 5, expected output: one row in a single `QUERY PLAN` column holding a JSON array with one plan of 8 nodes: `Limit` (12 actual rows), `Sort` (top-N heapsort), `Subquery Scan` on `with_previous`, `WindowAgg`, `Sort`, `Subquery Scan` on `monthly`, a hashed `Aggregate`, and a `Seq Scan` on `orders` (4,362 rows). The final column is `QUERY PLAN`.
   **Verify:** For sql-60 Exercise 5, read each node's `Plan Rows` beside `Actual Rows` times `Actual Loops`: the hashed `Aggregate` plans 4,362 groups and returns 46, and the `Seq Scan` touches all 65 pages of `orders` (`Shared Hit Blocks` plus `Shared Read Blocks`). In a rolled-back transaction run `CREATE STATISTICS orders_month_stats ON (date_trunc('month', order_date)) FROM orders` and `ANALYZE orders`, then explain again: the same 8 nodes return the same 12 rows, but the `Aggregate` estimate drops to 46.
   **Data check:** The JSON holds 8 nodes, from `Limit` down to a `Seq Scan` that reads all 4,362 orders. The hashed `Aggregate` estimates 4,362 groups but returns 46, and the nodes above it carry that estimate until `Limit` stops at 12. None of the five `_day60_solution` indexes appears, because every month needs every order.
6. Produce a release checklist covering operations and known limits.
   **Inputs/evidence:** For sql-60 Exercise 6, list the release checklist as an inline `VALUES` relation with one row per `item`, its current `evidence`, and its `owner`.
   **Expected result/shape:** For sql-60 Exercise 6, expected output: 6 rows, one per checklist `item`: rollback plan, object ownership/privileges, refresh cadence, monitoring and alerts, data contracts, and known limits. The final columns are `item`, `evidence`, and `owner`.
   **Verify:** For sql-60 Exercise 6, confirm 6 rows with no NULL `evidence` or `owner` and no repeated `item`; every row whose `evidence` reads `review required` still needs a named reviewer before release.
   **Data check:** Two rows read `review required`: `object ownership/privileges` (database owner) and `monitoring and alerts` (operations). `refresh cadence` says "not applicable to ordinary views" because nothing here is materialized; that row changes the day a materialized view ships.
7. Map metric lineage from source tables through validation.
   **Inputs/evidence:** For sql-60 Exercise 7, write an inline `VALUES` lineage fixture with one row per published metric (`customer_ltv`, `monthly_revenue`, and `customer_dq`) giving its `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
   **Expected result/shape:** For sql-60 Exercise 7, expected output: 3 rows: `customer_ltv` from customers + orders at customer grain, `monthly_revenue` from orders at calendar-month grain, and `customer_dq` from customers as one snapshot summary. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
   **Verify:** For sql-60 Exercise 7, turn each `validation_query` into a runnable check: `SUM(ltv)` over the 500 rows of `v_customer_ltv_solution`, `SUM(revenue)` over the 46 rows of the refactored monthly view, and `SUM(total_amount)` over `orders` all return 2,355,646.89, and `v_dq_customers_solution` reports 0 invalid emails, countries, and names over 500 customers. A row whose text cannot be rewritten as a `SELECT` with a pass condition is not yet lineage evidence.
   **Data check:** The three rows map `customer_ltv` to customers + orders at customer grain, `monthly_revenue` to orders at calendar-month grain and `customer_dq` to customers as one snapshot summary. `validation_query` holds predicate text such as `SUM(ltv) = SUM(orders.total_amount)`; Exercises 2 and 8 are the queries that actually execute those checks.
8. Reconcile every dashboard subtotal to a simple control.
   **Inputs/evidence:** For sql-60 Exercise 8, sum `revenue` over the 46 rows of `v_monthly_revenue_refactored_solution` as `dashboard_total` and `total_amount` over the 4,362 `orders` as `source_total`, each rounded to 2 places in its own scalar subquery, and subtract them as `difference`.
   **Expected result/shape:** For sql-60 Exercise 8, expected output: one row with `dashboard_total` 2,355,646.89, `source_total` 2,355,646.89, and `difference` 0.00 on the checked load. The final columns are `dashboard_total`, `source_total`, and `difference`.
   **Verify:** For sql-60 Exercise 8, run the two scalar subqueries alone: both return 2,355,646.89. In a rolled-back transaction insert a 100.00 order for customer 1 dated `now()`: both totals become 2,355,746.89 and `difference` stays 0.00, so this control checks the view logic rather than the load. Make the dashboard side skip the open month with `FILTER (WHERE month < date_trunc('month', CURRENT_DATE)::date)` instead, and `difference` becomes -85,364.67, the November revenue that version would hide.
   **Data check:** On our run `dashboard_total` and `source_total` were both 2,355,646.89 with `difference` 0.00. Both sides read `orders`, so a new order raises both equally: this control catches a broken view, not a missed load. Summing discounted order lines instead gives about 2,355,647.12, a 0.23 gap.
9. Test empty, one-row, NULL-heavy, and duplicate-key fixtures.
   **Inputs/evidence:** For sql-60 Exercise 9, build a three-row `VALUES` fixture `edge_fixture(id, email, amount)` with one row whose email and amount are NULL and two rows that share `id` 2 with emails that differ only in case, then count rows, NULL emails, duplicate keys, and non-null amounts.
   **Expected result/shape:** For sql-60 Exercise 9, expected output: one row with `fixture_rows` 3, `null_email_rows` 1, `duplicate_key_rows` 1, and `nonnull_amount_rows` 2. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
   **Verify:** For sql-60 Exercise 9, confirm that `duplicate_key_rows` equals `COUNT(*) - COUNT(DISTINCT id)` (3 - 2 = 1) and `nonnull_amount_rows` equals `COUNT(amount)` (2); `COUNT(DISTINCT lower(email))` is 1, so the two `id` 2 rows also collide after email normalization.
   **Data check:** The two `id` 2 emails differ only in case, and `customers` enforces a case-sensitive `UNIQUE (email)`, so the table would accept both; the seed has no such pair today. Filter the fixture with `WHERE false` and `COUNT` returns 0 where a `SUM(CASE ...)` returns NULL, which is how the learner quality view would report an empty table.
10. Return `PASS`/`FAIL`/`NOT_RUN` for every acceptance criterion.
   **Inputs/evidence:** For sql-60 Exercise 10, list the acceptance criteria as a `VALUES` relation with `criterion`, an `executed` flag, the `observed` value from the solution views, and the `expected` value, then label each criterion `PASS`, `FAIL`, or `NOT_RUN`.
   **Expected result/shape:** For sql-60 Exercise 10, expected output: 3 rows ordered by `criterion`: `customer DQ` PASS, `LTV reconciliation` PASS, and `Windows CI bootstrap` NOT_RUN. The final columns are `criterion` and `result`. The final order is `criterion`.
   **Verify:** For sql-60 Exercise 10, confirm that each PASS row's observed value matches its expected value when queried directly (`SELECT invalid_email FROM v_dq_customers_solution` returns 0) and that the unexecuted criterion reports `NOT_RUN`, never `PASS`.
   **Data check:** `executed` is tested first, so the third row's NULL observed value reaches `NOT_RUN` rather than `FAIL`. Lowercase `customer DQ` sorts first only because this database uses the `en_US.utf8` collation; under `COLLATE "C"` the two capitalized names would come before it.

Link every sign-off claim to executable evidence.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with `SUM(orders.total_amount)`, capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.
- **Comparing the open month with a closed one:** `v_monthly_revenue`
  gives November 2026 a growth of -0.4984 on our run, a partial month set
  against October's full 170,179.13. Flag the month as Exercise 4 does, or
  end the series at the last complete month.
- **Reading future retention cells as churn:** the Marketing grid prints
  0.0000 for offsets that have not happened yet, 15 of its 42 cells on our
  run, including offsets 2 to 6 for the October 2026 cohort. Return NULL for
  months after the current one so that 0 means "observed and gone".
- **Budgeting against a partial month:** the Finance table opens with COGS
  for November 2026, a budget of 576,000.00 against 335,159.36 actual, so
  most of the -240,840.64 variance is days not yet elapsed. Pro-rate the
  budget or leave the open month out.
- **Blaming the plan on missing indexes:** in the `EXPLAIN ANALYZE` of
  `v_monthly_revenue`, the `GroupAggregate` expects 4,362 groups and finds
  46. The gap comes from having no statistics on
  `date_trunc('month', order_date)`; on PostgreSQL 17.12,
  `CREATE STATISTICS` on that expression plus `ANALYZE orders` brought the
  estimate to 46. None of the six learner indexes changes this plan.
- **Assuming both quality views treat NULL alike:** the learner view counts
  a NULL country or name as invalid, but the solution's
  `FILTER (WHERE country !~ '^[A-Z]{2}$')` yields NULL, not true, for a NULL
  country. They agree today only because both columns are `NOT NULL`.
- For any other failure, the
  [recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  starts from the first error and works forward.

## Self-check

- Does every sign-off claim have reproducible evidence and a named limitation
  or owner where applicable?
- Are tutorial views and indexes still rollback-only unless a separate reviewed
  migration explicitly persists them?

## Next step

Review any weak SQL areas, then combine both languages in the
[Python and PostgreSQL engineering bridge](../../../bridge/README.md). The
bridge expects at least Python Day 15 and SQL Day 15.

## Deep dive and reference

Day 60 defines acceptance criteria rather than discrete exercises. The final
submission connects reusable DQ checks, business views, stakeholder outputs,
performance evidence, and a written handoff.

## Deliverable 1: Data quality

- `v_dq_customers`: total rows plus invalid email, country, and name counts.
- `v_dq_orders`: total rows plus negative totals and missing customers.
- Document every nonzero result with remediation, owner, and severity.

## Deliverable 2: Core business views

- Customer LTV at one row per customer, retaining zero-order customers with a
  `LEFT JOIN` from `customers` to `orders` and `COALESCE(..., 0)`.
- Treat `orders.total_amount` as the authoritative revenue measure in this
  capstone. Do not recompute LTV from `order_items`: a line-based total can omit
  header-only orders or disagree with header-level adjustments.
- Monthly order revenue with previous month and safely divided month-over-month
  growth.
- Reconcile summed customer LTV to summed `orders.total_amount`; expected
  difference on the seed is zero.

## Deliverable 3: Stakeholder outputs

- Finance: current-year budget versus actual by month/category.
- Marketing: active customers by signup cohort and lifecycle month 0-6. Select
  the six latest *distinct* signup months before expanding the lifecycle grid.
  Count every signup once in `cohort_size`, count a customer at most once per
  activity month, and report
  `active_customers / NULLIF(cohort_size, 0)` as `retention_rate`. Keeping the
  numerator and denominator visible makes the percentage auditable.
- Operations: an actual plan for recent units by product category.

## Deliverable 4: Performance sign-off

Capture before/after `EXPLAIN (ANALYZE, BUFFERS)` for critical queries and record
dataset size, PostgreSQL version, indexes, timing, buffers, correctness check,
and decision. The requested under-10-second goal applies to the measured learner
machine/dataset; the compact seed does not prove production-scale performance.

## Deliverable 5: Written handoff

Document DQ exceptions, model grain, join rationale, KPI definitions,
reconciliation, freshness-versus-speed tradeoffs, known limitations, and next
steps. Evidence must support every sign-off claim.

## State and safety

The learner file ends with `ROLLBACK`; its views and indexes do not persist.
Replace it with `COMMIT` only as a deliberate reviewed migration. Days 59-60 are
capstone criteria/checkpoints, so measured evidence and documentation are part
of the deliverable, not optional stretch work.

## Ask an AI tutor about this lesson

Treat the tutor as the colleague who inherits this capstone tomorrow. Share
your sign-off table and handoff note, then ask which claim it could not
rerun from what you wrote. [The tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
lists what to share and what to keep private. Hand it this request:

```text
Tutor me through sql-60: Final Capstone, Part 3: End-to-End Sign-Off.

I have completed the direct catalog prerequisite: `sql-59`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day60_final_capstone_part3.md
- Answer-free learner SQL: sql/postgres-60day/day60_final_capstone_part3.sql

Key terms to teach in context: Acceptance criterion, Evidence bundle, Handoff. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with `SUM(orders.total_amount)`, capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-60/ working copy. Never point setup, reset, DDL, or DML
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
