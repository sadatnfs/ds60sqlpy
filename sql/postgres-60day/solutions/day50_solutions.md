# Day 50 Solutions: Expense and Budget Variance


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day50_solutions.sql
```

The file is read-only. Expect four 125-row results and one 25-row pivot; Exercise 5 has no query of its own. The general steps are in the
[solution routine](../../STUDY-GUIDE.md#read-a-solution).

## Clause-by-clause reading map

Read each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
starting with the two monthly summaries every exercise rebuilds. Once those
are known to hold one row per month and category, the remaining work is
joining, labeling and windowing 125 rows.

This day adds year-over-year context, a greater-than-15% overspend flag, and a
static monthly pivot using the categories present in the course seed. See
[`day50_solutions.sql`](day50_solutions.sql).

## Exercise 1: YoY and budget variance

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    date_trunc('month', expense_date),
    category
),
budget AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    period,
    category
),
joined AS (
  SELECT
    COALESCE(a.month, b.month) AS month,
    COALESCE(a.category, b.category) AS category,
    COALESCE(a.actual, 0) AS actual,
    COALESCE(b.budget, 0) AS budget
  FROM
    actual a
    FULL OUTER JOIN budget b USING (month, category)
),
compared AS (
  SELECT
    *,
    LAG(actual, 12) OVER (PARTITION BY category ORDER BY month) AS prior_year_actual
  FROM
    joined
)
SELECT
  month,
  category,
  ROUND(actual, 2) AS actual,
  ROUND(prior_year_actual, 2) AS prior_year_actual,
  ROUND((actual - prior_year_actual) / NULLIF (prior_year_actual, 0), 4) AS year_over_year_variance_pct,
  ROUND((actual - budget) / NULLIF (budget, 0), 4) AS budget_variance_pct,
  actual > budget * 1.15 AS overspent_by_more_than_15_pct
FROM
  compared
ORDER BY
  month DESC,
  category;
```

Expected grain: one row per month and category, including periods found on only
one side of the actual/budget comparison.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 1, sum the 10,000 `expenses` rows by `date_trunc('month', expense_date)` and `category` in `actual`, sum the 125 `budgets` rows by `period` and `category` in `budget`, `FULL OUTER JOIN` them `USING (month, category)` with missing amounts set to 0, and take `LAG(actual, 12)` within each category for the prior year.
- **Expected result/shape:** For sql-50 Exercise 1, expected output: 125 rows, one per month and category (25 months from 2024-11-01 to 2026-11-01 times 5 categories), including any period found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 1, confirm 125 distinct (`month`, `category`) pairs, 71 rows with the flag true, and 65 rows with a `prior_year_actual` (the first 12 months of each category have none). Recompute the top row by hand: 2026-11 COGS spent 335,159.36 against 398,788.03 in 2025-11 (-0.1596) and a 576,000.00 budget (-0.4181), so the flag is false. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15: a 126th row appears with `budget_variance_pct` `NULL` but the flag true, because the missing budget became 0; `ROLLBACK`.
- **Intermediate relation check:** `actual` reduces 10,000 expenses to 125 month-category rows and `budget` reduces 125 budget rows to 125 groups (the table has no unique key on period and category, so the `SUM` also absorbs any duplicate plan). `joined` stays at 125 rows, and `compared` adds `prior_year_actual` without changing the count.
- **Clause check:** `LAG(actual, 12) OVER (PARTITION BY category ORDER BY month)` looks back 12 rows, which equals 12 months only because each category has all 25 months. Both percentages divide through `NULLIF(..., 0)`, and `actual > budget * 1.15` returns a boolean for the flag column.
- **Alternative/trade-off:** Joining `compared` to itself on `month - interval '12 months'` finds the prior year by date instead of by row position. It survives a missing month, at the price of a second pass over the data.
- **Edge case:** `joined` replaces missing amounts with 0 before the flag is computed. A month with spending but no budget would compare `actual > 0` and be flagged as overspend, which is the case Exercise 6 separates out.

## Exercise 2: Monthly variance pivot

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    date_trunc('month', expense_date),
    category
),
variance AS (
  SELECT
    b.period AS month,
    b.category,
    COALESCE(a.actual, 0) - b.amount AS variance
  FROM
    budgets b
    LEFT JOIN actual a ON a.month = b.period
      AND a.category = b.category
)
  SELECT
    month,
    ROUND(SUM(variance) FILTER (WHERE category = 'COGS'), 2) AS cogs,
    ROUND(SUM(variance) FILTER (WHERE category = 'Marketing'), 2) AS marketing,
    ROUND(SUM(variance) FILTER (WHERE category = 'Payroll'), 2) AS payroll,
    ROUND(SUM(variance) FILTER (WHERE category = 'Infrastructure'), 2) AS infrastructure,
    ROUND(SUM(variance) FILTER (WHERE category = 'G&A'), 2) AS general_admin
  FROM
    variance
GROUP BY
  month
ORDER BY
  month DESC;
```

Expected shape: one row per budget month and one variance column per known
category.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 2, sum `expenses` by month and category in `actual`, start `variance` from the 125 `budgets` rows with a `LEFT JOIN` to `actual`, compute `actual - budget` per row, and spread it into one column per category with `SUM(variance) FILTER (WHERE category = ...)`.
- **Expected result/shape:** For sql-50 Exercise 2, expected output: 25 rows, one per budget month from 2026-11-01 down to 2024-11-01, with one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
- **Independent verification:** For sql-50 Exercise 2, confirm 25 distinct months and that the five columns of each row add up to that month's total spend minus its total budget: for 2026-11, -240,840.64 + 135,537.59 - 342,178.22 + 41,001.63 + 175,254.25 = -231,225.39, the same as `SUM(expenses.amount) - SUM(budgets.amount)` for that month. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15 and rerun: the pivot is unchanged at 25 rows, so the November reconciliation is now off by exactly 1,000.00, because spending without a budget row never enters `variance`; `ROLLBACK`.
- **Intermediate relation check:** `actual` again has 125 rows. `variance` starts from the 125 budget rows and attaches spending with a `LEFT JOIN`, then the outer query groups by month, giving 25 rows with five category columns each.
- **Clause check:** Each `SUM(variance) FILTER (WHERE category = '...')` sees one row per month on this data, so the sum just moves that value into its column. The alias `general_admin` replaces `G&A`, which is not a convenient column name.
- **Alternative/trade-off:** `crosstab` from the `tablefunc` extension builds the same layout from a category list, and a BI tool can pivot the long Exercise 3 output itself. Both avoid editing SQL when a category is added.
- **Edge case:** Starting from `budgets` means spending with no budget row never reaches the pivot, and a sixth category would be dropped by every `FILTER`. Neither happens on the course data, which is why the reconciliation check matters.

## Reasoning, safety, and pitfalls

- Positive variance means actual spending exceeded budget because the formula
  is `actual - budget`.
- `LAG(..., 12)` assumes every category has one row for every month. Build a
  category/month spine when periods can be missing.
- The pivot is intentionally static. New categories require a new column or a
  long-form BI result.
- Treat zero or absent budgets explicitly; `NULL` percentage is safer than a
  fabricated infinite or zero rate.

## Exercise 3: Preserve missing-budget meaning

The FULL JOIN retains actual-only and budget-only rows. Status is assigned before
display-time `COALESCE`, so missing planning data is not relabeled zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 3, build the same 125-row `actual` and `budget` summaries, `FULL JOIN` them `USING (month, category)`, keep `a.actual` and `b.budget` without `COALESCE`, and label each row from which side's key is `NULL`.
- **Expected result/shape:** For sql-50 Exercise 3, expected output: 125 rows, one per `month` and `category`, every one labeled `comparable` on the course data. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 3, confirm 125 rows, all `comparable`, with no `NULL` in `actual` or `budget`. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: a 126th row appears at the top labeled `no actual` with `actual` shown as `NULL`, not 0. Roll back and insert a `Travel` expense of 1,000 on 2026-11-15 instead: its row is labeled `missing budget` with `budget` `NULL`; `ROLLBACK`.
- **Intermediate relation check:** The two summaries each hold 125 rows and match one to one, so the `FULL JOIN ... USING (month, category)` returns 125 rows, every one labeled `comparable`.
- **Clause check:** With `USING`, `a.category` and `b.category` still name each side's own column, so `b.category IS NULL` means the budget side had no row. The `CASE` checks keys, not amounts, because a key is never `NULL` on a side that matched.
- **Alternative/trade-off:** Testing `b.budget IS NULL` gives the same result here, since `amount` is `NOT NULL` in `budgets`. Testing the join key stays correct even if a future table allows a `NULL` amount, which would make `SUM` return `NULL`.
- **Edge case:** A budget row spelled `Cogs` instead of `COGS` does not match. You get two rows for that month, one `missing budget` and one `no actual`, and neither compares the real figures.

## Exercise 4: Calculate YTD windows

The `monthly` CTE first establishes canonical coalesced keys. Windows then
partition by category and calendar year and order by month.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 4, build `monthly` from the 125-row expense and budget summaries with a `FULL JOIN` and coalesced `month` and `category`, then run three running `SUM` windows partitioned by `category` and `EXTRACT(year FROM month)` and ordered by `month`.
- **Expected result/shape:** For sql-50 Exercise 4, expected output: 125 rows, one per `month` and `category`, in 15 partitions (5 categories times the years 2024, 2025, and 2026). The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 4, hand-check COGS: the 2024 partition has only two rows, so 2024-11 shows 72,384.36 against 654,000.00 and 2024-12 shows 545,878.91 against 1,266,000.00; 2025-01 restarts at 430,421.17 against 570,000.00; and 2026-11 shows 4,508,769.63 against 6,600,000.00, a `variance_ytd` of -2,091,230.37, equal to summing that year's COGS rows directly. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: that row shows `budget_ytd` 7,200,000.00 but `actual_ytd` and `variance_ytd` unchanged from November, because `actual - budget` is `NULL` on a one-sided row; `ROLLBACK`.
- **Intermediate relation check:** `monthly` builds the 125 joined rows with coalesced keys. The windows then split them into 15 partitions: five categories in each of three calendar years.
- **Clause check:** There is no frame clause, so each `SUM` uses the default frame from the partition's first row to the current month, a running total. `EXTRACT(year FROM month)` in `PARTITION BY` restarts the total each January.
- **Alternative/trade-off:** `date_trunc('year', month)` partitions the same way and keeps a date type, and writing `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` states the frame explicitly. Both return identical numbers on this data.
- **Edge case:** On a one-sided row `actual - budget` is `NULL`, so `variance_ytd` skips that month while `actual_ytd` or `budget_ytd` still counts it. The three columns then stop agreeing. No such row exists in the course data, so insert one to see it.

## Exercise 5: Normalize joined keys once

Every later expression references `monthly.month` and `monthly.category`,
avoiding inconsistent use of nullable columns from one join side.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 5, write a short note on why every window and filter must use the coalesced keys `monthly.month` and `monthly.category` from Exercise 4 instead of `a.month` or `a.category` from one side of the `FULL JOIN`; Exercise 4's `monthly` CTE is the repaired query, so cite its results as evidence and mark anything you did not run as an assumption.
- **Expected result/shape:** For sql-50 Exercise 5, expected output: a written note with six fields, `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`, whose `evidence` quotes the 125 rows of `monthly` with zero `NULL` months and zero `NULL` categories.
- **Independent verification:** For sql-50 Exercise 5, show that the broken and repaired forms agree today: partitioning by `a.category, EXTRACT(year FROM a.month)` returns the same 125 rows and totals as Exercise 4, because every key matches. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01 and run both: the repaired form gives that row a `budget_ytd` of 7,200,000.00, while the broken form puts it in a `NULL` partition with 600,000.00, so it never joins the COGS total; `ROLLBACK`, and name the `fallback` and `rollback_limit` entries that cover this case.
- **Intermediate relation check:** The evidence for this written answer is Exercise 4's `monthly` relation: 125 rows, one per month and category, with zero `NULL` months and zero `NULL` categories. Quote those three counts in the `evidence` field.
- **Clause check:** A complete answer reads roughly: `decision`, every window and filter uses `monthly.month` and `monthly.category`; `owner`, whoever maintains the budget report; `failure_response`, stop and recount when a key is `NULL`; `fallback`, rebuild from a month and category spine; `rollback_limit`, report results can be regenerated, so nothing is lost.
- **Alternative/trade-off:** A spine built from `generate_series` over months, cross joined to the five categories and left joined to both summaries, guarantees every key exists. It also makes the 12-row `LAG` in Exercise 1 exactly 12 months.
- **Edge case:** The counterexample is a budget-only row windowed by `a.category`: it lands in a `NULL` partition and its budget disappears from the category's running total. That is what the `fallback` entry has to handle.

## Exercise 6: Separate unbudgeted spend

The CASE checks missing and zero budgets before normal overspend. This prevents
an absent plan from becoming an ordinary variance percentage.

Aggregate both sources independently before joining them. If raw expense rows
are joined to a monthly budget first, the budget is repeated once per expense:

```sql
WITH expense_monthly AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    1,
    2
),
budget_monthly AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    1,
    2
),
monthly AS (
  SELECT
    COALESCE(e.month, b.month) AS month,
    COALESCE(e.category, b.category) AS category,
    e.actual,
    b.budget
  FROM
    expense_monthly e
    FULL JOIN budget_monthly b USING (month, category))
SELECT
  month,
  category,
  actual,
  budget,
  CASE WHEN budget IS NULL THEN
    'unbudgeted spend'
  WHEN actual IS NULL THEN
    'budget without spend'
  WHEN budget = 0 THEN
    'zero budget'
  WHEN actual > budget THEN
    'overspend'
  ELSE
    'within budget'
  END AS status
FROM
  monthly
ORDER BY
  month,
  category;
```

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 6, aggregate `expenses` and `budgets` independently to (`month`, `category`) before joining.
- **Expected result/shape:** For sql-50 Exercise 6, expected output: 125 rows, one per (`month`, `category`) found in either source, with `actual`, `budget`, and `status`, ordered by `month, category` (oldest first); 72 rows are `overspend` and 53 are `within budget`.
- **Independent verification:** For sql-50 Exercise 6, reconcile the totals: `actual` sums to 50,483,850.00 and `budget` to 51,198,000.00, the same as `SUM(amount)` on each source table, while joining raw `expenses` to `budgets` instead sums the budget to 4,098,331,000.00 because each plan repeats once per expense (13 to 96 times). Then, in a transaction, test each missing case: a `Travel` expense on 2026-11-15 gives `unbudgeted spend`, a COGS budget for 2026-12-01 gives `budget without spend`, and setting the 2026-11 G&A budget to 0 gives `zero budget`; `ROLLBACK` after each.
- **Intermediate relation check:** `expense_monthly` and `budget_monthly` each hold 125 rows, `monthly` joins them into 125, and the `CASE` labels 72 rows `overspend` and 53 `within budget`. No other status occurs on the course data.
- **Clause check:** The `CASE` order matters: a missing budget, then missing spending, then a zero budget are tested before any comparison, so `actual > budget` only runs when both values exist and the budget is positive. This result is sorted oldest month first.
- **Alternative/trade-off:** A tier for `actual > budget * 1.15` would match Exercise 1's flag and split the 72 overspend rows into minor and serious cases. Keep the missing-plan tests ahead of it.
- **Edge case:** The status totals reconcile with the sources: `actual` sums to 50,483,850.00 and `budget` to 51,198,000.00, matching each table's own total. Joining raw expenses would repeat each budget 13 to 96 times, depending on that month's expense count.