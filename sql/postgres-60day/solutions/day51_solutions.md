# Day 51 Solutions: Cash Flow and Operating Margin


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day51_solutions.sql
```

The solution file only reads data. Confirm that three forecast rows appear
and that each beginning balance matches the prior ending balance before you
compare amounts; the
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Follow each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
In this lesson the pattern repeats: each source table becomes a monthly CTE,
and only then do the months meet through `FULL OUTER JOIN`, a `LEFT JOIN`
from a calendar spine, or `UNION ALL`. Check each monthly CTE for one row per
month before reading what combines them, and read window functions last.

The project finishes with monthly operating margin, a three-month seasonal
cash projection, a cash versus booked revenue comparison, a cash roll-forward,
a gap-free month list and a guarded margin. See
[`day51_solutions.sql`](day51_solutions.sql).

## Exercise 1: Monthly operating margin

The prompt defines operating cost as `COGS + Payroll + Infrastructure + G&A`;
Marketing is deliberately excluded.

```sql
SET search_path TO training, public;

WITH cash AS (
  SELECT
    date_trunc('month', payment_date)::date AS month,
    SUM(amount) AS cash_in
  FROM
    payments
  GROUP BY
    date_trunc('month', payment_date)
),
operating_expense AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    SUM(amount) FILTER (WHERE category IN ('COGS', 'Payroll', 'Infrastructure', 'G&A')) AS operating_cost
  FROM
    expenses
  GROUP BY
    date_trunc('month', expense_date))
SELECT
  COALESCE(c.month, e.month) AS month,
  ROUND(COALESCE(c.cash_in, 0), 2) AS cash_in,
  ROUND(COALESCE(e.operating_cost, 0), 2) AS operating_cost,
  ROUND((COALESCE(c.cash_in, 0) - COALESCE(e.operating_cost, 0)) / NULLIF (c.cash_in, 0), 4) AS operating_margin
FROM
  cash c
  FULL OUTER JOIN operating_expense e USING (month)
ORDER BY
  month DESC;
```

Expected grain: one row per month appearing in either payments or operating
expenses. Margin is `NULL` when there is no cash-in denominator.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 1, sum `payments.amount` by payment month in `cash`, sum `expenses.amount` by expense month for the four operating categories (COGS, Payroll, Infrastructure, G&A, not Marketing) in `operating_expense`, and `FULL OUTER JOIN` the two `USING (month)`.
- **Expected result/shape:** For sql-51 Exercise 1, expected output: 46 rows, one per month appearing in either payments or operating expenses (2023-02-01 to 2026-11-01). The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
- **Independent verification:** For sql-51 Exercise 1, confirm 46 distinct months, and that the 21 months before expenses begin (2023-02 to 2024-10) show `operating_cost` 0.00 and a margin of exactly 1.0000. Recompute the top row: 2026-11 has 76,045.60 cash in and 1,362,737.02 operating cost (that month's 1,712,274.61 of expenses minus 349,537.59 of Marketing), so the margin is -16.9200. Then, in a transaction, delete the 77 payments from 2025-03: that month stays with `cash_in` 0.00, cost 1,747,681.27, and a `NULL` margin instead of a division error; `ROLLBACK`.
- **Intermediate relation check:** `cash` is one row per payment month and `operating_expense` one row per expense month; the second covers only the last two years. Count both, then count the full join: it should equal the number of distinct months across the two tables, here the payment months, since expenses never appear alone.
- **Clause check:** `SUM(amount) FILTER (WHERE category IN (...))` defines operating cost as four categories and leaves Marketing out. That choice is policy, so it is written into the query. `NULLIF(c.cash_in, 0)` makes the margin `NULL` instead of an error when a month has costs and no cash.
- **Alternative/trade-off:** A `WHERE category IN (...)` inside `operating_expense` would give the same sums; the `FILTER` form keeps room for other cost columns from the same scan, such as a separate marketing total.
- **Edge case:** A month with expenses but no payments would get `cash_in` 0 and a `NULL` margin through `NULLIF`. Months with cash but no expenses get a margin of 1.0000, which is arithmetically right and analytically misleading; Exercise 6 adds the status column that explains it.

## Exercise 2: Next three months by matching calendar month

The phrase “matching months” is interpreted as the same calendar month in
earlier years.

```sql
SET search_path TO training, public;

WITH cash AS (
  SELECT
    date_trunc('month', payment_date)::date AS month,
    SUM(amount) AS cash_in
  FROM
    payments
  GROUP BY
    date_trunc('month', payment_date)
),
expense AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    SUM(amount) AS cash_out
  FROM
    expenses
  GROUP BY
    date_trunc('month', expense_date)
),
historical AS (
  SELECT
    COALESCE(c.month, e.month) AS month,
    COALESCE(c.cash_in, 0) - COALESCE(e.cash_out, 0) AS net_cash
  FROM
    cash c
    FULL OUTER JOIN expense e USING (month)
),
future AS (
  SELECT
    (date_trunc('month', CURRENT_DATE) + n * interval '1 month')::date AS forecast_month
  FROM
    generate_series(1, 3) AS g (n))
SELECT
  f.forecast_month,
  ROUND(AVG(h.net_cash), 2) AS projected_net_cash,
  COUNT(h.month) AS matching_historical_months
FROM
  future f
  LEFT JOIN historical h ON EXTRACT(month FROM h.month) = EXTRACT(month FROM f.forecast_month)
    AND h.month < f.forecast_month
GROUP BY
  f.forecast_month
ORDER BY
  f.forecast_month;
```

Expected shape: exactly three future month rows. The count column shows how much
history supports each estimate; a `NULL` projection means there was none.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 2, build monthly net cash in `historical` from a `FULL OUTER JOIN` of payment and expense totals, generate the next three calendar months after `CURRENT_DATE` in `future`, and `LEFT JOIN` each one to the earlier months with the same calendar month number.
- **Expected result/shape:** For sql-51 Exercise 2, expected output: exactly three rows, one per future `forecast_month` (2026-12-01, 2027-01-01, and 2027-02-01 when run in November 2026). The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `forecast_month`.
- **Independent verification:** For sql-51 Exercise 2, run in November 2026, confirm the counts 3, 3, and 4, then recompute the first row by hand: the Decembers 2023, 2024, and 2025 have net cash 11,201.99, -2,102,060.09, and -2,062,784.20, whose mean is -1,384,547.43. February averages four months (2023 to 2026), so it is -941,106.45. Then, in a transaction, insert a 100.00 payment dated 2026-12-02 and rerun: the December projection does not change, because `h.month < f.forecast_month` keeps a month out of its own forecast; `ROLLBACK`.
- **Intermediate relation check:** `historical` is one row per month with net cash. `future` is three rows from `generate_series(1, 3)`. The `LEFT JOIN` then pairs each future month with the past months that share its calendar month, so each future row matches 3 or 4 history rows before `GROUP BY` collapses it again.
- **Clause check:** The join condition compares `EXTRACT(month ...)` on both sides and adds `h.month < f.forecast_month`. `COUNT(h.month)` counts only matched history, so a future month with no history would show 0 and a `NULL` projection instead of being dropped.
- **Alternative/trade-off:** A weighted average that favors recent years, or a trailing 12-month average, would react faster to the large expenses that started two years ago; the seasonal-naive average is simpler and shows its evidence count.
- **Edge case:** Because expenses only exist in recent years, each average blends small positive years with large negative ones. Restricting `historical` to months with expense data would give a different and arguably fairer projection.

## Reasoning, safety, and pitfalls

- Cash flow uses payments, not booked order revenue.
- The operating-margin definition is course policy; real financial statements
  may classify categories differently.
- A seasonal average needs multiple years to be convincing. Treat a one-point
  average as a naive forecast and disclose the sample count.
- Both answers are read-only.

## Exercise 3: Separate cash and booked revenue

Orders are grouped by order month and payments by payment month. Displaying both
reveals timing differences; combining them under one unlabeled “revenue” metric
would be misleading.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 3, read from `orders` and `payments`; sum `total_amount` by order month as `booked_order_revenue` and left join the payments summed by payment month as `cash_received`, using `COALESCE(..., 0)` for months without payments.
- **Expected result/shape:** For sql-51 Exercise 3, expected output: one row per order month, ordered by `month`; `cash_received` is lower than `booked_order_revenue` in most months because unpaid orders bring no cash. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
- **Independent verification:** For sql-51 Exercise 3, confirm 46 unique months, that `SUM(booked_order_revenue)` is 2,355,646.89 and `SUM(cash_received)` is 1,831,900.81 (the same as `SELECT SUM(amount) FROM payments`), and that cash is lower than bookings in 45 months and equal only in 2023-02 (1,203.26). Then, in a transaction, insert a 100.00 payment dated 2026-12-02: the result keeps 46 rows and the same cash total, now 100.00 short of `payments`, because the query starts from order months and drops a payment-only month; `ROLLBACK`.
- **Intermediate relation check:** The derived table `p` is one row per payment month. The outer query starts from `orders`, one row per order, and left joins `p` on the order month, so each payment-month total repeats on every order of that month until `GROUP BY` collapses them.
- **Clause check:** `p.cash_received` is in the `GROUP BY` so it can be selected without an aggregate. Summing it instead would multiply it by the number of orders in the month. `COALESCE` turns a month with orders but no payments into 0.
- **Alternative/trade-off:** Aggregating orders to months in their own CTE and full-joining to payment months, as in Exercise 1, would also keep payment-only months; here the order months drive the result, which matches the question about booked revenue.
- **Edge case:** A payment made in the month after its order raises the next month's cash, so booked revenue and cash received measure different timing and should not be combined into one unlabeled margin. About 150 payments on the course data (148 on our load) cross a month boundary this way.

## Exercise 4: Build a cash balance

Payment and expense entries are unioned at month grain. Net flow is accumulated
with a running SUM, and LAG supplies the next month's beginning balance.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 4, stack the 3,836 payments (as `cash_in`) and the 10,000 expenses (as `cash_out`) with `UNION ALL`, group them to monthly totals in `flow`, add a running `SUM(cash_in - cash_out) OVER (ORDER BY month)` in `balances`, and read the previous ending balance with `LAG(ending_cash, 1, 0)`.
- **Expected result/shape:** For sql-51 Exercise 4, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, starting from a declared opening balance of 0. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
- **Independent verification:** For sql-51 Exercise 4, hand-check the first two rows: 2023-02 begins at 0 and ends at 1,203.26, and 2023-03 begins at 1,203.26 and ends at 2,350.50. Confirm with `LAG` that every `beginning_cash` equals the previous row's `ending_cash`, and that the last `ending_cash`, -48,651,949.19, equals 1,831,900.81 of payments minus 50,483,850.00 of expenses. There is one window with no `PARTITION BY`, so nothing resets; in a transaction, delete the 77 payments from 2025-03 and confirm that month keeps its row with `cash_in` 0 and every later ending balance drops by 38,915.28; `ROLLBACK`.
- **Intermediate relation check:** Inside `flow`, the derived table `entries` stacks 3,836 payments and 10,000 expenses with `UNION ALL`, each row carrying a 0 in the other column. `flow` groups them to one row per month and `balances` adds net cash and the running ending balance.
- **Clause check:** `SUM(cash_in - cash_out) OVER (ORDER BY month)` builds the ending balance from a declared opening balance of 0. `LAG(ending_cash, 1, 0::numeric)` reads the previous row's ending balance as the beginning balance, using 0 for the first month.
- **Alternative/trade-off:** Computing `beginning_cash` as `ending_cash - net_cash` gives the same values without a second window; `LAG` makes the roll-forward explicit and is easier to check row against row.
- **Edge case:** The window has no `PARTITION BY`, so a single partition runs through every month. If a month were missing, the roll-forward would silently skip it; building `flow` from Exercise 5's spine keeps every month in the chain.

## Exercise 5: Preserve one-sided months

A calendar spine spans both sources, then left joins monthly cash and costs.
This retains expense-only and payment-only periods with an explicit zero policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 5, find the first and last dates across `payments` and `expenses` in `bounds`, expand them into calendar months with `generate_series` in `months`, and `LEFT JOIN` the monthly totals `cash` and `costs` to that spine.
- **Expected result/shape:** For sql-51 Exercise 5, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with 0 where a side has no rows. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `month`.
- **Independent verification:** For sql-51 Exercise 5, confirm 46 months and show the bug being repaired: an inner join of `cash` and `costs` returns only 25 rows (2024-11 to 2026-11), losing the 21 months that have payments but no expenses. Then, in a transaction, delete the 77 payments from 2025-03 and rerun: the spine still returns 46 rows, with 2025-03 showing `cash_in` 0 and `cash_out` 2,154,691.38; `ROLLBACK`.
- **Intermediate relation check:** `bounds` is one row with the earliest and latest date across both tables. `months` expands it with `generate_series` into one row per calendar month. `cash` and `costs` are monthly totals that the spine left joins.
- **Clause check:** Both joins are `LEFT JOIN` from `months`, so the spine decides which months exist and `COALESCE` turns missing totals into 0. `LEAST` and `GREATEST` pick the outer edges of the two date ranges so neither table is cut short.
- **Alternative/trade-off:** The `FULL OUTER JOIN` in Exercise 1 keeps months that appear in either table, but it cannot invent a month that appears in neither; the spine can.
- **Edge case:** On this data every month has payments, so the spine adds no new rows. Delete one month of payments and expenses in a rolled-back transaction: the spine keeps that month with two zeros while the full join loses it.

## Exercise 6: Explain undefined margin

`NULLIF(cash_in, 0)` preserves NULL for an undefined ratio. A companion status
column explains the reason instead of leaving consumers to guess.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 6, use the two-row `VALUES` list `toy` (2026-01 with 0 cash in and 100 cost; 2026-02 with 500 in and 300 cost) instead of the course tables, divide through `NULLIF(cash_in, 0)`, and label the result with a `CASE`.
- **Expected result/shape:** For sql-51 Exercise 6, expected output: 2 rows, one per `toy` month: 2026-01-01 with a `NULL` margin and `undefined: zero cash in`, and 2026-02-01 with 0.4 and `defined`. The final columns are `month`, `operating_margin`, and `margin_status`.
- **Independent verification:** For sql-51 Exercise 6, confirm the two rows above and that the first raises no division-by-zero error. Then add a third `toy` row, `(date '2026-03-01', NULL, 100)`: its margin is also `NULL`, but the status says `defined`, because `cash_in = 0` is unknown for a `NULL` and falls to `ELSE`, so a `WHEN cash_in IS NULL` branch is needed to tell missing cash from zero cash.
- **Intermediate relation check:** `toy` is a two-row `VALUES` list with one zero-cash month and one normal month. There is no grouping; each input row produces one output row.
- **Clause check:** `(cash_in - operating_cost) / NULLIF(cash_in, 0)` returns `NULL` for the first row instead of raising a division-by-zero error. The `CASE` then labels that row `undefined: zero cash in`, so a reader can tell an undefined margin from a missing row.
- **Alternative/trade-off:** `COALESCE(..., 0)` on the margin would hide the problem by reporting a 0 margin for a month that lost 100. Keeping `NULL` plus a status is the honest form for a report.
- **Edge case:** A `NULL` cash value is a different case from 0: `NULLIF(NULL, 0)` is `NULL` too, but `cash_in = 0` is unknown, so the `CASE` returns `defined`. Add a `WHEN cash_in IS NULL` branch if source data can be missing.