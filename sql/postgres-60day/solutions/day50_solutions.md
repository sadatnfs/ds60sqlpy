# Day 50 Solutions — Expense and Budget Variance


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day50_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day50_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Variance, Budget-only row, Static pivot. Its worked-model focus is:
Aggregate actuals and budgets independently at (month, category), full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with NULLIF(budget, 0); only then pivot the five known categories.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

This day adds year-over-year context, a greater-than-15% overspend flag, and a
static monthly pivot using the categories present in the course seed. See
[`day50_solutions.sql`](day50_solutions.sql).

## Exercise 1 — YoY and budget variance

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY date_trunc('month', expense_date), category
), budget AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY period, category
), joined AS (
  SELECT COALESCE(a.month, b.month) AS month,
         COALESCE(a.category, b.category) AS category,
         COALESCE(a.actual, 0) AS actual,
         COALESCE(b.budget, 0) AS budget
  FROM actual a
  FULL OUTER JOIN budget b USING (month, category)
), compared AS (
  SELECT *,
         LAG(actual, 12) OVER (
           PARTITION BY category ORDER BY month
         ) AS prior_year_actual
  FROM joined
)
SELECT month,
       category,
       ROUND(actual, 2) AS actual,
       ROUND(prior_year_actual, 2) AS prior_year_actual,
       ROUND((actual - prior_year_actual) / NULLIF(prior_year_actual, 0), 4)
         AS year_over_year_variance_pct,
       ROUND((actual - budget) / NULLIF(budget, 0), 4) AS budget_variance_pct,
       actual > budget * 1.15 AS overspent_by_more_than_15_pct
FROM compared
ORDER BY month DESC, category;
```

Expected grain: one row per month and category, including periods found on only
one side of the actual/budget comparison.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 1, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-50 Exercise 1, expected output: one row per month and category, including periods found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 1, project `month` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, then assert the final `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
- **Intermediate relation check:** For sql-50 Exercise 1, run `actual`, `budget`, `joined`, and `compared` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-50 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, and `budgets`, preserve one row per `month`, and finish with `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct` ordered by `month DESC, category`.
- **Alternative/trade-off:** For sql-50 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected grain: one row per month and category, including periods found on only one side of the actual/budget comparison. Evaluate another form against the concrete expected result (one row per month and category, including periods found on only one side of the actual/budget comparison) and the verification above.
- **Edge case:** Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.

## Exercise 2 — Monthly variance pivot

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY date_trunc('month', expense_date), category
), variance AS (
  SELECT b.period AS month,
         b.category,
         COALESCE(a.actual, 0) - b.amount AS variance
  FROM budgets b
  LEFT JOIN actual a
    ON a.month = b.period
   AND a.category = b.category
)
SELECT month,
       ROUND(SUM(variance) FILTER (WHERE category = 'COGS'), 2) AS cogs,
       ROUND(SUM(variance) FILTER (WHERE category = 'Marketing'), 2) AS marketing,
       ROUND(SUM(variance) FILTER (WHERE category = 'Payroll'), 2) AS payroll,
       ROUND(SUM(variance) FILTER (WHERE category = 'Infrastructure'), 2)
         AS infrastructure,
       ROUND(SUM(variance) FILTER (WHERE category = 'G&A'), 2) AS general_admin
FROM variance
GROUP BY month
ORDER BY month DESC;
```

Expected shape: one row per budget month and one variance column per known
category.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 2, read from `expenses`, and `budgets`. Build the answer toward `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-50 Exercise 2, expected output: one row per budget month and one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
- **Independent verification:** For sql-50 Exercise 2, independently aggregate `expenses`, and `budgets` by `month`; require one output row for every distinct `month` tuple and compare `cogs`, `marketing`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cogs`, `marketing`, and `payroll` for the existing `month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-50 Exercise 2, run `actual`, and `variance` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-50 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, and `budgets`, preserve one row per `month`, and finish with `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin` ordered by `month DESC`.
- **Alternative/trade-off:** For sql-50 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected shape: one row per budget month and one variance column per known category. Evaluate another form against the concrete expected result (one row per budget month and one variance column per known category) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `cogs`, `marketing`, and `payroll` for the existing `month` tuple and verify the new tuple appears exactly once.

## Reasoning, safety, and pitfalls

- Positive variance means actual spending exceeded budget because the formula
  is `actual - budget`.
- `LAG(..., 12)` assumes every category has one row for every month. Build a
  category/month spine when periods can be missing.
- The pivot is intentionally static. New categories require a new column or a
  long-form BI result.
- Treat zero or absent budgets explicitly; `NULL` percentage is safer than a
  fabricated infinite or zero rate.

## Exercise 3 — Preserve missing-budget meaning

The FULL JOIN retains actual-only and budget-only rows. Status is assigned before
display-time `COALESCE`, so missing planning data is not relabeled zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `budget`, and `comparison_status`; keep `month`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-50 Exercise 3, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 3, project `month`, and `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, and `category`, then assert the final `month`, `category`, `actual`, `budget`, and `comparison_status` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`, and `category`; verify the result gains exactly one row carrying that `month`, and `category` value.
- **Intermediate relation check:** For sql-50 Exercise 3, run `actual`, and `budget` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-50 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, and `budgets`, preserve one row per `month`, and `category`, and finish with `month`, `category`, `actual`, `budget`, and `comparison_status` ordered by `month DESC, category`.
- **Alternative/trade-off:** For sql-50 Exercise 3, the chosen form is justified by this lesson-specific rationale: The FULL JOIN retains actual-only and budget-only rows. Evaluate another form against the concrete expected result (one row per `month`, and `category`) and the verification above.
- **Edge case:** Add one source row with a new `month`, and `category`; verify the result gains exactly one row carrying that `month`, and `category` value.

## Exercise 4 — Calculate YTD windows

The `monthly` CTE first establishes canonical coalesced keys. Windows then
partition by category and calendar year and order by month.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 4, read from `expenses`, `budgets`, and `month`. Build the answer toward `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`; keep `month`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-50 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
- **Independent verification:** For sql-50 Exercise 4, choose one complete partition from `expenses`, `budgets`, and `month`; hand-calculate its first, middle, and final window values for `variance_ytd`, then verify output keys remain `month`, and `category`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-50 Exercise 4, run `monthly` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-50 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, `budgets`, and `month`, preserve one row per `month`, and `category`, and finish with `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd` ordered by `month DESC, category`.
- **Alternative/trade-off:** For sql-50 Exercise 4, the chosen form is justified by this lesson-specific rationale: The `monthly` CTE first establishes canonical coalesced keys. Evaluate another form against the concrete expected result (one row per `month`, and `category`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Normalize joined keys once

Every later expression references `monthly.month` and `monthly.category`,
avoiding inconsistent use of nullable columns from one join side.

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 5, complete the normalize joined keys before applying windows written analysis and support its claims with read-only evidence from `monthly.month`, and `monthly.category`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-50 Exercise 5, expected output: a completed the normalize joined keys before applying windows written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-50 Exercise 5, check the normalize joined keys before applying windows written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-50 Exercise 5, check the normalize joined keys before applying windows written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-50 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `monthly.month`, and `monthly.category` or label it as proposed policy.
- **Alternative/trade-off:** For sql-50 Exercise 5, the chosen form is justified by this lesson-specific rationale: Every later expression references `monthly.month` and `monthly.category`, avoiding inconsistent use of nullable columns from one join side. Evaluate another form against the concrete expected result (a completed the normalize joined keys before applying windows written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 6 — Separate unbudgeted spend

The CASE checks missing and zero budgets before normal overspend. This prevents
an absent plan from becoming an ordinary variance percentage.

Aggregate both sources independently before joining them. If raw expense rows
are joined to a monthly budget first, the budget is repeated once per expense:

```sql
WITH expense_monthly AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1, 2
), budget_monthly AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY 1, 2
), monthly AS (
  SELECT COALESCE(e.month, b.month) AS month,
         COALESCE(e.category, b.category) AS category,
         e.actual,
         b.budget
  FROM expense_monthly e
  FULL JOIN budget_monthly b USING (month, category)
)
SELECT month,
       category,
       actual,
       budget,
       CASE
         WHEN budget IS NULL THEN 'unbudgeted spend'
         WHEN actual IS NULL THEN 'budget without spend'
         WHEN budget = 0 THEN 'zero budget'
         WHEN actual > budget THEN 'overspend'
         ELSE 'within budget'
       END AS status
FROM monthly
ORDER BY month, category;
```

### Reasoning and verification

- **Inputs/evidence:** For sql-50 Exercise 6, aggregate `expenses` into `expense_monthly` and `budgets` into `budget_monthly`, each keyed by (`month`, `category`), before the `FULL JOIN`.
- **Expected result/shape:** For sql-50 Exercise 6, expected output: one row per (`month`, `category`) found on either side, with `actual`, `budget`, and `status`, ordered by `month, category`.
- **Independent verification:** For sql-50 Exercise 6, separately sum each source by (`month`, `category`) and compare those controls to `actual` and `budget`. Their grand totals must equal the corresponding totals after the join; no monthly budget may be multiplied by the number of expense rows.
- **Intermediate relation check:** For sql-50 Exercise 6, prove `expense_monthly` and `budget_monthly` are each unique on (`month`, `category`) before joining; then inspect actual-only and budget-only keys.
- **Clause check:** For sql-50 Exercise 6, each `GROUP BY` establishes the join grain, `FULL JOIN ... USING (month, category)` preserves one-sided keys, and `COALESCE` creates the canonical output key before `CASE` assigns status.
- **Alternative/trade-off:** For sql-50 Exercise 6, the chosen form is justified by this lesson-specific rationale: The CASE checks missing and zero budgets before normal overspend. Evaluate another form against the concrete expected result (one row per `category`, and `status`) and the verification above.
- **Edge case:** Add one actual-only month/category, one budget-only month/category, and one zero-budget row; require `unbudgeted spend`, `budget without spend`, and `zero budget` respectively.
