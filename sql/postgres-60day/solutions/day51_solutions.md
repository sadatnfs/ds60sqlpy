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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** Pre-aggregation or a differently ordered join pipeline is valid only if it prevents fanout and reconciles to the same scoped control total.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Build a cash balance

Payment and expense entries are unioned at month grain. Net flow is accumulated
with a running SUM, and LAG supplies the next month's beginning balance.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Preserve one-sided months

A calendar spine spans both sources, then left joins monthly cash and costs.
This retains expense-only and payment-only periods with an explicit zero policy.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Explain undefined margin

`NULLIF(cash_in, 0)` preserves NULL for an undefined ratio. A companion status
column explains the reason instead of leaving consumers to guess.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.
