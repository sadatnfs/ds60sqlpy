# Day 51 Solutions — Cash Flow and Operating Margin


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day51_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day51_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cash-in, Cash-out, Seasonal average. Its worked-model focus is:
Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.

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

The project finishes with monthly operating margin and a three-month seasonal
cash projection. See [`day51_solutions.sql`](day51_solutions.sql).

## Exercise 1 — Monthly operating margin

The prompt defines operating cost as `COGS + Payroll + Infrastructure + G&A`;
Marketing is deliberately excluded.

```sql
SET search_path TO training, public;

WITH cash AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY date_trunc('month', payment_date)
), operating_expense AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) FILTER (
           WHERE category IN ('COGS', 'Payroll', 'Infrastructure', 'G&A')
         ) AS operating_cost
  FROM expenses
  GROUP BY date_trunc('month', expense_date)
)
SELECT COALESCE(c.month, e.month) AS month,
       ROUND(COALESCE(c.cash_in, 0), 2) AS cash_in,
       ROUND(COALESCE(e.operating_cost, 0), 2) AS operating_cost,
       ROUND(
         (COALESCE(c.cash_in, 0) - COALESCE(e.operating_cost, 0))
           / NULLIF(c.cash_in, 0),
         4
       ) AS operating_margin
FROM cash c
FULL OUTER JOIN operating_expense e USING (month)
ORDER BY month DESC;
```

Expected grain: one row per month appearing in either payments or operating
expenses. Margin is `NULL` when there is no cash-in denominator.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 1, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, `operating_cost`, and `operating_margin`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 1, expected output: one row per month appearing in either payments or operating expenses. The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
- **Independent verification:** For sql-51 Exercise 1, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, `operating_cost`, and `operating_margin` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
- **Intermediate relation check:** For sql-51 Exercise 1, run `cash`, and `operating_expense` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-51 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, and `expenses`, preserve one row per `month`, and finish with `month`, `cash_in`, `operating_cost`, and `operating_margin` ordered by `month DESC`.
- **Alternative/trade-off:** For sql-51 Exercise 1, the chosen form is justified by this lesson-specific rationale: The prompt defines operating cost as `COGS + Payroll + Infrastructure + G&A`; Marketing is deliberately excluded. Evaluate another form against the concrete expected result (one row per month appearing in either payments or operating expenses) and the verification above.
- **Edge case:** Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.

## Exercise 2 — Next three months by matching calendar month

The phrase “matching months” is interpreted as the same calendar month in
earlier years.

```sql
SET search_path TO training, public;

WITH cash AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY date_trunc('month', payment_date)
), expense AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) AS cash_out
  FROM expenses
  GROUP BY date_trunc('month', expense_date)
), historical AS (
  SELECT COALESCE(c.month, e.month) AS month,
         COALESCE(c.cash_in, 0) - COALESCE(e.cash_out, 0) AS net_cash
  FROM cash c
  FULL OUTER JOIN expense e USING (month)
), future AS (
  SELECT (
           date_trunc('month', CURRENT_DATE)
           + n * interval '1 month'
         )::date AS forecast_month
  FROM generate_series(1, 3) AS g(n)
)
SELECT f.forecast_month,
       ROUND(AVG(h.net_cash), 2) AS projected_net_cash,
       COUNT(h.month) AS matching_historical_months
FROM future f
LEFT JOIN historical h
  ON EXTRACT(month FROM h.month) = EXTRACT(month FROM f.forecast_month)
 AND h.month < f.forecast_month
GROUP BY f.forecast_month
ORDER BY f.forecast_month;
```

Expected shape: exactly three future month rows. The count column shows how much
history supports each estimate; a `NULL` projection means there was none.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 2, read from `payments`, `expenses`, `h.month`, and `f.forecast_month`. Build the answer toward `forecast_month`, `projected_net_cash`, and `matching_historical_months`; keep `forecast_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 2, expected output: exactly three future month rows. The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `f.forecast_month`.
- **Independent verification:** For sql-51 Exercise 2, independently aggregate `payments`, `expenses`, `h.month`, and `f.forecast_month` by `forecast_month`; require one output row for every distinct `forecast_month` tuple and compare `projected_net_cash`, and `matching_historical_months` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `projected_net_cash`, and `matching_historical_months` for the existing `forecast_month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-51 Exercise 2, run `cash`, `expense`, `historical`, and `future` one at a time. Record each CTE's row count and `forecast_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-51 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, `expenses`, `h.month`, and `f.forecast_month`, preserve one row per `forecast_month`, and finish with `forecast_month`, `projected_net_cash`, and `matching_historical_months` ordered by `f.forecast_month`.
- **Alternative/trade-off:** For sql-51 Exercise 2, the chosen form is justified by this lesson-specific rationale: The phrase “matching months” is interpreted as the same calendar month in earlier years. Evaluate another form against the concrete expected result (exactly three future month rows. The count column shows how much history supports each estimate; a `NULL` projection means there was none) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `projected_net_cash`, and `matching_historical_months` for the existing `forecast_month` tuple and verify the new tuple appears exactly once.

## Reasoning, safety, and pitfalls

- Cash flow uses payments, not booked order revenue.
- The operating-margin definition is course policy; real financial statements
  may classify categories differently.
- A seasonal average needs multiple years to be convincing. Treat a one-point
  average as a naive forecast and disclose the sample count.
- Both answers are read-only.

## Exercise 3 — Separate cash and booked revenue

Orders are grouped by order month and payments by payment month. Displaying both
reveals timing differences; combining them under one unlabeled “revenue” metric
would be misleading.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 3, read from `orders`, and `payments`. Build the answer toward `month`, `booked_order_revenue`, and `cash_received`; keep `cash_received` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 3, expected output: one row per `cash_received`. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
- **Independent verification:** For sql-51 Exercise 3, independently aggregate `orders`, and `payments` by `cash_received`; require one output row for every distinct `cash_received` tuple and compare `booked_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `booked_order_revenue` for the existing `cash_received` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-51 Exercise 3, start with the first relation in `orders`, and `payments`; after each join, record total rows and distinct `cash_received` so the exact fanout or loss is visible.
- **Clause check:** For sql-51 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `payments`, preserve one row per `cash_received`, and finish with `month`, `booked_order_revenue`, and `cash_received` ordered by `month`.
- **Alternative/trade-off:** For sql-51 Exercise 3, the chosen form is justified by this lesson-specific rationale: Orders are grouped by order month and payments by payment month. Evaluate another form against the concrete expected result (one row per `cash_received`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `booked_order_revenue` for the existing `cash_received` tuple and verify the new tuple appears exactly once.

## Exercise 4 — Build a cash balance

Payment and expense entries are unioned at month grain. Net flow is accumulated
with a running SUM, and LAG supplies the next month's beginning balance.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 4, read from `payments`, and `expenses`. Build the answer toward `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 4, expected output: one row per `month`. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
- **Independent verification:** For sql-51 Exercise 4, choose one complete partition from `payments`, and `expenses`; hand-calculate its first, middle, and final window values for `beginning_cash`, `cash_in`, and `cash_out`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-51 Exercise 4, run `flow`, and `balances` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-51 Exercise 4, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, and `expenses`, preserve one row per `month`, and finish with `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash` ordered by `month`.
- **Alternative/trade-off:** For sql-51 Exercise 4, the chosen form is justified by this lesson-specific rationale: Payment and expense entries are unioned at month grain. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Preserve one-sided months

A calendar spine spans both sources, then left joins monthly cash and costs.
This retains expense-only and payment-only periods with an explicit zero policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 5, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, and `cash_out`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 5, expected output: one row per `month`. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `m.month`.
- **Independent verification:** For sql-51 Exercise 5, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, and `cash_out` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
- **Intermediate relation check:** For sql-51 Exercise 5, run `bounds`, `months`, `cash`, and `costs` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-51 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, and `expenses`, preserve one row per `month`, and finish with `month`, `cash_in`, and `cash_out` ordered by `m.month`.
- **Alternative/trade-off:** For sql-51 Exercise 5, the chosen form is justified by this lesson-specific rationale: A calendar spine spans both sources, then left joins monthly cash and costs. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.

## Exercise 6 — Explain undefined margin

`NULLIF(cash_in, 0)` preserves NULL for an undefined ratio. A companion status
column explains the reason instead of leaving consumers to guess.

### Reasoning and verification

- **Inputs/evidence:** For sql-51 Exercise 6, read from `toy`. Build the answer toward `month`, `operating_margin`, and `margin_status`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-51 Exercise 6, expected output: one row per `month`. The final columns are `month`, `operating_margin`, and `margin_status`.
- **Independent verification:** For sql-51 Exercise 6, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `operating_margin`, and `margin_status` against `toy`. Repeat with `NULL` in `month`, and `operating_margin` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-51 Exercise 6, select `month` from `toy` before adding derived columns.
- **Clause check:** For sql-51 Exercise 6, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at `toy`, preserve one row per `month`, and finish with `month`, `operating_margin`, and `margin_status`.
- **Alternative/trade-off:** For sql-51 Exercise 6, the chosen form is justified by this lesson-specific rationale: `NULLIF(cash_in, 0)` preserves NULL for an undefined ratio. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Repeat with `NULL` in `month`, and `operating_margin` and state whether the row is kept, rejected, or classified.
