# Day 60 Solution — End-to-End Capstone Sign-off


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day60_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day60_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Acceptance criterion, Evidence bundle, Handoff. Its worked-model focus is:
Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.

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

Day 60 has acceptance criteria, not discrete exercises. The final submission
must connect data quality, transformation, analytics, performance evidence, and
documented tradeoffs. The executable reference is
[`day60_solutions.sql`](day60_solutions.sql).

## Success criteria

Sign off only when:

1. critical queries complete in under 10 seconds **on the learner's measured
   dataset and machine**;
2. data-quality checks pass or every exception has an owner and explanation;
3. business totals reconcile across views and source tables; and
4. the write-up records grain, assumptions, before/after plans, compromises,
   known limits, and next steps.

The compact seed makes the 10-second target easy; it does not prove
production-scale performance.

## Deliverable 1 — Reusable DQ views

The learner creates `v_dq_customers` and `v_dq_orders`. The reference solution
uses a suffixed customer view so it cannot collide with a learner's view:

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_dq_customers_solution AS
SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (
         WHERE email IS NULL
            OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
       ) AS invalid_email,
       COUNT(*) FILTER (WHERE country !~ '^[A-Z]{2}$') AS invalid_country,
       COUNT(*) FILTER (WHERE trim(full_name) = '') AS invalid_name
FROM customers;

SELECT * FROM v_dq_customers_solution;

SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE total_amount < 0) AS negative_amounts,
       COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer
FROM orders;

ROLLBACK;
```

Expected shape: one customer summary row and one order summary row. The course
seed should report zero failures.

## Deliverable 2 — Core business views and reconciliation

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_customer_ltv_solution AS
SELECT c.customer_id,
       c.country,
       COALESCE(SUM(o.total_amount), 0)::numeric(14,2) AS ltv
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.country;

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
)
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous_month,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY month))
           / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
         4
       ) AS month_over_month_growth
FROM monthly;

SELECT (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         AS customer_ltv_total,
       (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS order_total,
       (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         - (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS difference;

ROLLBACK;
```

Expected reconciliation: `difference = 0.00`. The monthly view has one row per
represented order month; it does not manufacture missing months.

## Deliverable 3 — Stakeholder-ready outputs

The learner file contains three runnable outputs:

- Finance: YTD actual, budget, and variance at `(month, category)` grain.
- Marketing: active customers by signup cohort and lifecycle month 0–6. A full
  retention rate additionally needs the cohort-size denominator from Day 47.
- Operations: an `EXPLAIN` of recent units by product category.

For each output, record the consumer, business definition, result grain,
freshness expectation, and at least one reconciliation or sanity check.

## Deliverable 4 — Performance sign-off

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_date_day60_solution ON orders(order_date);
CREATE INDEX idx_orders_customer_day60_solution ON orders(customer_id);
CREATE INDEX idx_order_items_order_day60_solution ON order_items(order_id);
CREATE INDEX idx_expenses_date_day60_solution ON expenses(expense_date);
CREATE INDEX idx_budgets_period_day60_solution ON budgets(period);

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
)
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous_month,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY month))
           / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
         4
       ) AS month_over_month_growth
FROM monthly;

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM v_monthly_revenue_solution
ORDER BY month DESC
LIMIT 12;

ROLLBACK;
```

Capture actual execution time and buffers before and after candidate indexes.
The transaction rolls back both views and indexes.

## Deliverable 5 — Written sign-off

The final write-up must cover:

- DQ exceptions and remediation;
- source entities, analytical grain, and join rationale;
- KPI definitions and reconciliation evidence;
- before/after `EXPLAIN (ANALYZE, BUFFERS)` evidence;
- freshness versus performance tradeoffs;
- known limitations and next steps; and
- whether the learner-file success criteria were met on the measured setup.

Do not replace evidence with “an index should help.” A complete capstone records
the query, dataset size, environment, plan, timing, correctness check, and
decision.

## Safety and state assumptions

- Both learner and solution files end with `ROLLBACK`; replace it with `COMMIT`
  only in a deliberate migration after reviewing object names and ownership.
- `CREATE VIEW` without `OR REPLACE` is intentional in the reference transaction
  and expects a clean course setup.
- Days 59–60 are sign-off checkpoints, so some deliverables are documentation
  and measured evidence rather than new SQL exercises.

## Exercise 1 — Identify clock dependence

Snapshot summaries depend only on table state. Trailing/current-period reports
also depend on the clock and need a bound `as_of_date` for reproducible review.

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

## Exercise 2 — Return executable sign-off checks

Each check contains observed/expected values, computed pass status, severity,
and remediation. A typed label cannot substitute for the equality expression.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 3 — Calculate LAG once

`monthly` establishes grain; `with_previous` computes LAG one time; the outer
query calculates growth. The first month remains NULL because it has no valid
comparison.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A different window or subquery shape is valid only with the same partition, peer, frame, tie, and output-order semantics.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Flag an incomplete month

The current calendar month is marked explicitly. Production evaluation should
bind an as-of date and avoid comparing a partial period with a complete one.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A different window or subquery shape is valid only with the same partition, peer, frame, tie, and output-order semantics.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Retain structured plan evidence

`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` captures plan shape, estimates, actual
rows, buffer activity, and timing. Evidence applies only to the tested server,
data volume, parameters, and cache state.

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

## Exercise 6 — Complete the operational release checklist

Rollback, ownership, privileges, refresh, monitoring, contracts, and limits all
have named owners/evidence. Query correctness alone is not production readiness.

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

## Exercise 7 — Publish lineage

Every published metric maps to sources, transformation grain, and a validation
query. This gives Codex and human maintainers a compact impact-analysis trail.

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

## Exercise 8 — Reconcile dashboard totals

Monthly-view revenue is summed and compared with the simplest order total.
Nonzero difference blocks sign-off before any optimization is accepted.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
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

## Exercise 9 — Test edge fixtures

The in-query fixture represents NULL, one-row-like, and duplicate-key cases
without changing course data. Counts expose assumptions that production
constraints or quarantine rules must enforce.

### Reasoning and verification

- **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
- **Independent verification:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
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

## Exercise 10 — Distinguish FAIL from NOT_RUN

Executed checks compare observed and expected values. An unexecuted Windows CI
bootstrap remains `NOT_RUN`; prose or confidence must never upgrade it to PASS.

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
