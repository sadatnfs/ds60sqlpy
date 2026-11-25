# Day 54 Solutions: Warehouse Aggregates and Refresh Procedure


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day54_solutions.sql
```

Load the Day 52 warehouse first; the file stops with an exception if
`dwh.fact_sales` is missing. Expect one reconciliation row with a 0.00
difference after the refresh and two empty comparison sets at the end. The
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read the statements in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
but notice that this file is mostly about state. The two starter tables begin
empty, Exercise 2's procedure fills only the newest month, and every later
query describes that partly filled state, which is why Exercise 5 finds 45
months missing.

The project loads monthly category and customer aggregates, adds a
product-month aggregate, refreshes one period idempotently, inventories late
fact risk and reconciles every month to facts. See
[`day54_solutions.sql`](day54_solutions.sql).

## Exercise 1: `agg_sales_product_month`

The answer uses this grain and schema:

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TABLE agg_sales_product_month (
  year int NOT NULL,
  month int NOT NULL,
  product_sk int NOT NULL REFERENCES dim_product (product_sk),
  revenue numeric(14, 2) NOT NULL,
  units bigint NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);

INSERT INTO agg_sales_product_month (year, month, product_sk, revenue, units, orders)
SELECT
  dd.year,
  dd.month,
  fs.product_sk,
  ROUND(SUM(fs.amount), 2),
  SUM(fs.quantity),
  COUNT(DISTINCT fs.order_id)
FROM
  fact_sales fs
  JOIN dim_date dd USING (date_key)
GROUP BY
  dd.year,
  dd.month,
  fs.product_sk;

WITH aggregate_total AS (
  SELECT
    year,
    month,
    SUM(revenue) AS revenue
  FROM
    agg_sales_product_month
  GROUP BY
    year,
    month
),
fact_total AS (
  SELECT
    dd.year,
    dd.month,
    ROUND(SUM(fs.amount), 2) AS revenue
  FROM
    fact_sales fs
    JOIN dim_date dd USING (date_key)
  GROUP BY
    dd.year, dd.month
)
SELECT
  a.year,
  a.month,
  a.revenue AS aggregate_revenue,
  f.revenue AS fact_revenue,
  a.revenue - f.revenue AS difference
FROM
  aggregate_total a
  JOIN fact_total f USING (year, month)
ORDER BY
  a.year,
  a.month;

ROLLBACK;
```

The two sides are aggregated independently before joining, preventing join
fanout. Expected `difference` is zero for every built month. In
`day54_solutions.sql` the same `INSERT` and check run between
`SAVEPOINT exercise_1` and `ROLLBACK TO SAVEPOINT exercise_1`, so the full
build is proven and the table is empty again when Exercise 2 refreshes a
single month.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 1, create `agg_sales_product_month` with `PRIMARY KEY (year, month, product_sk)` and load it by grouping the 13,085 `fact_sales` rows joined to `dim_date` on `date_key` by year, month, and `product_sk`, storing `ROUND(SUM(amount), 2)` as `revenue`, `SUM(quantity)` as `units`, and `COUNT(DISTINCT order_id)` as `orders`; then reconcile it against an independent per-month sum of `fact_sales`.
- **Expected result/shape:** For sql-54 Exercise 1, expected output: the load inserts one row per year, month, and `product_sk` (6,741 rows on our load), and the reconciliation returns one row per month, 46 rows, with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, every `difference` 0.00. The final order is `a.year, a.month`. The solution file runs this full build inside `SAVEPOINT exercise_1` and rolls back to it, so Exercise 2 starts from an empty table.
- **Independent verification:** For sql-54 Exercise 1, confirm that no (year, month, `product_sk`) appears twice, that February 2023 holds 6 product rows with 1,203.26 revenue and 17 units, and that November 2026 holds 234 product rows with 85,364.73 revenue. In the transaction, add 1.00 to the revenue of product 69 in February 2023: the reconciliation shows that month alone with `difference` 1.00. Then delete the February 2023 rows: the inner join drops to 45 months and reports no difference at all, which is the gap Exercise 5 closes.
- **Intermediate relation check:** The `SELECT` feeding the `INSERT` groups 13,085 fact rows into 6,741 (year, month, product_sk) rows on our load. `aggregate_total` then collapses those to 46 months, and `fact_total` independently sums the facts to the same 46 months before the two meet.
- **Clause check:** `PRIMARY KEY (year, month, product_sk)` matches the `GROUP BY`, and `REFERENCES dim_product` blocks orphan products. `COUNT(DISTINCT fs.order_id)` counts orders rather than lines; no order repeats a product here, but the `DISTINCT` keeps the measure right if one ever did.
- **Alternative/trade-off:** A materialized view with the same query would also store the summary, but `REFRESH MATERIALIZED VIEW` rebuilds every month at once. The table form lets Exercise 2 replace one month and leave the rest alone.
- **Edge case:** The reconciliation joins with `JOIN ... USING (year, month)`, so a month that exists only in the facts would silently vanish from the check. Exercise 5 replaces that join with a `FULL JOIN` that reports such months.

## Exercise 2: Refresh all aggregates for `(year, month)`

The executable solution creates:

```text
dwh.refresh_sales_aggregates_solution(p_year int, p_month int)
```

Within one procedure call it:

1. deletes the target month from category, customer, and product aggregates;
2. inserts category revenue and units;
3. inserts customer revenue and distinct orders;
4. inserts product revenue, units, and distinct orders.

The delete-then-insert design is idempotent for a target period. The answer
discovers the latest fact month and calls the procedure for that month, then
reconciles product aggregate revenue with `fact_sales`.

To inspect the result after running the canonical file, remember that it ends
with `ROLLBACK`; the aggregate objects intentionally will not persist.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 2, write `refresh_sales_aggregates_solution(p_year, p_month)` so it deletes that month from `agg_sales_category_month`, `agg_sales_customer_month`, and `agg_sales_product_month` and reinserts it from `fact_sales` joined to `dim_date` (and to `dim_product` for the category); call it for the newest fact month, then reconcile the product aggregate against `fact_sales` for the months it holds.
- **Expected result/shape:** For sql-54 Exercise 2, expected output: the procedure returns nothing; the call leaves 6 category rows, 73 customer rows, and 234 product rows, all for November 2026 on our load, and the reconciliation returns 1 row with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` (2026, 11, 85,364.73, 85,364.73, 0.00 on our load). The query has no `ORDER BY` because it returns one month.
- **Independent verification:** For sql-54 Exercise 2, check that all three tables sum to 85,364.73 revenue, that the category `units` total 1,399, and that the customer `orders` total 151, the same as `COUNT(DISTINCT order_id)` for that month in `fact_sales`. Call the procedure again for 2026-11 and then for 2030-01, a month with no facts: the counts stay 6, 73, and 234. Call it for 2023-02: the counts become 12, 75, and 240, and the reconciliation returns 2 rows, both with `difference` 0.00.
- **Intermediate relation check:** After the `DO` block finds the newest year and month and calls the procedure, each aggregate holds only that month: 6 category rows plus one row for every customer and product with facts in it. `aggregate_total` therefore has a single row.
- **Clause check:** `p_year` and `p_month` filter all three `DELETE` statements and all three `INSERT ... SELECT` statements, so every table is rebuilt for the same period. In the check, `WHERE (dd.year, dd.month) IN (...)` limits `fact_total` to the refreshed month so untouched months are not compared.
- **Alternative/trade-off:** `INSERT ... ON CONFLICT DO UPDATE` could upsert the month instead, but it leaves behind a stale row for any category or customer that no longer has facts. Deleting first and inserting fresh rows avoids that.
- **Edge case:** The procedure has no `COMMIT`, so it runs inside the caller's transaction and the final `ROLLBACK` undoes it. Calling it for a month with no facts empties that month in every aggregate, which is the correct result.

## Required Days 52 to 54 sequence

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f day52_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f day53_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f day54_solutions.sql
```

Day 52 persists course-owned warehouse state. Days 53 and 54 prove their
solutions and roll back. Day 54 does not require Day 53 changes to persist.
Either Day 52 file, learner or solution, is a valid starting point for these
solutions.

## Reasoning, state, and pitfalls

- State the aggregate grain in the primary key; otherwise duplicate loads can
  silently inflate reports.
- Delete and rebuild all related aggregates in one transaction so readers do
  not observe mismatched periods.
- Reconcile totals after every refresh and treat nonzero differences as a load
  failure.
- The compact seed does not justify aggregate tables for performance; this is a
  warehouse-design exercise.
- Reconcile independently aggregated sides; joining aggregates to detail rows
  before summing can fan out both measures.

## Exercise 3: Account for late facts

The period inventory identifies every loaded month. A late fact requires
refreshing its own affected period, not merely the newest month.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 3, group the 13,085 `fact_sales` rows joined to `dim_date` by year and month, counting the fact rows and taking `MAX(date_actual)` as the latest loaded day of each month.
- **Expected result/shape:** For sql-54 Exercise 3, expected output: 46 rows, one per year and month from February 2023 to November 2026, with columns `year`, `month`, `fact_rows`, and `latest_fact_date`, ordered by `dd.year DESC, dd.month DESC`. On our load October 2026 has 965 rows ending 2026-10-31, the partial November 2026 has 468 rows ending 2026-11-23, and February 2023 has 6 rows, all on 2023-02-13.
- **Independent verification:** For sql-54 Exercise 3, confirm that `fact_rows` adds up to 13,085. In a transaction, insert a late fact for order 3739, product 69, `order_item_id` 999999, `date_key` 20230220, and amount 35.53: February 2023 rises to 7 rows with `latest_fact_date` 2023-02-20. If February 2023 was already refreshed, the Exercise 5 reconciliation now shows it with 1,203.26 against 1,238.79, a `difference` of -35.53, until the procedure is called for 2023-02 again; `ROLLBACK`.
- **Intermediate relation check:** `fact_sales` joined to `dim_date` stays at 13,085 rows, one per order line, and `GROUP BY dd.year, dd.month` turns them into 46 periods. No aggregate table is read; the inventory comes straight from facts.
- **Clause check:** `COUNT(*)` gives the fact rows per month and `MAX(dd.date_actual)` the last day that has facts, which shows whether a month is complete. The descending order puts the newest, still filling month first. On a fresh load the oldest month, February 2023, has only 6 fact rows, while recent full months approach a thousand.
- **Alternative/trade-off:** Detecting late facts properly needs a load timestamp on each fact, compared with the time each month was last refreshed. This warehouse has no such column, so the query can list periods that might need a rebuild but not prove which did.
- **Edge case:** Add one fact dated in an older month: that month's `fact_rows` rises by one while its aggregate rows stay as they were. Refreshing only the newest month leaves the difference, and Exercise 5's check would report it.

## Exercise 4: Refresh atomically

Delete and all aggregate inserts run in one transaction through the procedure.
Failure rolls back the whole period instead of leaving partial tables.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 4, after the Exercise 2 call has deleted and reinserted the newest month inside the open transaction, group `agg_sales_category_month` by year and month, counting the category rows and summing their revenue.
- **Expected result/shape:** For sql-54 Exercise 4, expected output: one row per refreshed month, 1 row on our load (2026, 11, 6 category rows, 85,364.73 revenue), with columns `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
- **Independent verification:** For sql-54 Exercise 4, list the six categories for the month (Apparel 14,026.26, Beauty 13,151.38, Books 15,823.05, Electronics 13,811.36, Home 12,125.38, and Sports 16,427.30 on our load) and confirm that they add up to the reported revenue. Call the procedure for 2023-02 as well: the query returns 2 rows, 2026-11 first and then 2023-02 with 6 rows and 1,203.26. After the file's `ROLLBACK`, `to_regclass('dwh.agg_sales_category_month')` returns `NULL`.
- **Intermediate relation check:** `agg_sales_category_month` holds only the rows the procedure wrote, so the grouping returns one month. `category_rows` is 6 because every category sold in that month.
- **Clause check:** `SUM(revenue)` per month must equal the fact revenue reconciled in Exercise 2. `COUNT(*)` against the number of categories with facts in that month shows whether the refresh missed one.
- **Alternative/trade-off:** The procedure could also capture `GET DIAGNOSTICS ... ROW_COUNT` after each `INSERT` and return the counts directly, which avoids a separate summary query but hides whether the stored rows still match.
- **Edge case:** `dim_product.category` allows `NULL`, while the aggregate column does not. A product without a category would make the insert fail, and because the deletes are in the same transaction the error undoes them too, leaving the old month intact.

## Exercise 5: Make reconciliation NULL-safe

FULL JOIN preserves a period missing on either side, and coalesced arithmetic
turns that absence into a visible nonzero difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 5, sum `agg_sales_category_month` revenue by year and month in `aggregate_total`, sum the `fact_sales` amounts joined to `dim_date` by year and month in `fact_total`, and `FULL JOIN` the two on year and month, keeping the rows where `a.revenue IS DISTINCT FROM f.revenue`.
- **Expected result/shape:** For sql-54 Exercise 5, expected output: 45 rows on our load, one for every fact month the aggregate does not hold (all but the refreshed November 2026), with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, ordered by `year, month`. Each row has a `NULL` `aggregate_revenue` and a `difference` equal to minus its fact revenue, for example -1,203.26 for February 2023.
- **Independent verification:** For sql-54 Exercise 5, call the procedure for 2023-02 and confirm that the result drops to 44 rows, now starting at March 2023. Then insert a category row for 2030-01 (Books, 10.00 revenue, 1 unit) that has no facts: it appears with a `NULL` `fact_revenue` and a `difference` of 10.00, for 45 rows. An inner join with `<>` would return neither kind of row; `ROLLBACK`.
- **Intermediate relation check:** `aggregate_total` has one row, the refreshed month, and `fact_total` has 46. The `FULL JOIN` yields 46 rows; the filter keeps the 45 months whose revenue differs, all of them because the aggregate side is missing.
- **Clause check:** `a.revenue IS DISTINCT FROM f.revenue` treats a `NULL` and a number as different, so missing months are reported. `COALESCE` on both sides makes the `difference` column a real number instead of `NULL`.
- **Alternative/trade-off:** Two `NOT EXISTS` queries, one per side, plus a value comparison would find the same problems. The `FULL JOIN` does all three in one statement and keeps both revenues on the same row.
- **Edge case:** Rewriting the filter as `a.revenue <> f.revenue` returns zero rows here, because comparing with `NULL` is unknown. That empty result would look like a perfect reconciliation while 45 months are missing.

## Exercise 6: Prove idempotency

The answer snapshots category aggregates, reruns the same latest period, and
uses two-way `EXCEPT`. Both difference sets must be empty.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 6, copy `agg_sales_category_month` into the temporary table `aggregate_snapshot_before`, call the refresh again for the same newest month, and compare the snapshot with the live table using `EXCEPT` in both directions, labeling each side.
- **Expected result/shape:** For sql-54 Exercise 6, expected output: 0 rows on the course data, because the second refresh deletes and rewrites the same 6 category rows with the same values. The final columns are `side`, `year`, `month`, `category`, `revenue`, and `units`, where `side` is `before_minus_after` or `after_minus_before`; the query has no `ORDER BY`.
- **Independent verification:** For sql-54 Exercise 6, check that the snapshot and the live table both hold 6 rows with 85,364.73 revenue after the rerun. Then, in a transaction, insert a late November 2026 fact (order 3739, product 69, `order_item_id` 999999, `date_key` 20261120, amount 35.53) between the snapshot and the rerun: the query returns 2 Home rows, `before_minus_after` with 12,125.38 and 209 units and `after_minus_before` with 12,160.91 and 210 units, which proves that the comparison catches a real change; `ROLLBACK`.
- **Intermediate relation check:** `aggregate_snapshot_before` copies the 6 category rows. The second `DO` block reruns the refresh for the same month, and the table again holds 6 rows.
- **Clause check:** `EXCEPT` compares whole rows, including `revenue` and `units`, and the query runs it in both directions joined with `UNION ALL`. One direction alone would miss rows that exist only after, or only before, the rerun.
- **Alternative/trade-off:** Comparing just `COUNT(*)` and `SUM(revenue)` before and after is quicker but weaker: a revenue shift between two categories would leave both unchanged.
- **Edge case:** `EXCEPT` removes duplicate rows, so it cannot notice a row loaded twice; the primary key prevents that here. The temporary snapshot is created inside the transaction, so `ROLLBACK` removes it with everything else.