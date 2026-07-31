# Day 27 solutions — Pivoting/Unpivoting: Crosstabs and Conditional Aggregation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day27_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day27_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Pivot, Unpivot, Conditional aggregation. Its worked-model focus is:
At one row per quarter, calculate SUM(amount) FILTER (WHERE method = 'card') and parallel columns for the other known methods. Reconcile the sum of pivot columns to the long-form payment total and decide whether absent combinations display as NULL or zero.

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

These answers align one-for-one with [day27_pivot_unpivot.sql](../day27_pivot_unpivot.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
- **Assumptions:** PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
- **Primary pitfall:** Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Pivot order counts by status into one summary row.

**Reasoning:** Use one filtered count per known status and keep an all-orders denominator.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) FILTER (WHERE o.status = 'placed') AS placed_orders,
       COUNT(*) FILTER (WHERE o.status = 'paid') AS paid_orders,
       COUNT(*) FILTER (WHERE o.status = 'shipped') AS shipped_orders,
       COUNT(*) FILTER (WHERE o.status = 'delivered') AS delivered_orders,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
       COUNT(*) AS all_orders
FROM orders AS o;
```

**Expected shape:** Exactly one row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exactly one row.
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

## Exercise 2 — Query writing

**Prompt:** Pivot customer counts for US, CA, GB, and DE by segment.

**Reasoning:** Group at segment grain and use filtered counts for known country columns.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.segment,
       COUNT(*) FILTER (WHERE c.country = 'US') AS us_customers,
       COUNT(*) FILTER (WHERE c.country = 'CA') AS ca_customers,
       COUNT(*) FILTER (WHERE c.country = 'GB') AS gb_customers,
       COUNT(*) FILTER (WHERE c.country = 'DE') AS de_customers,
       COUNT(*) AS all_customers
FROM customers AS c
GROUP BY c.segment
ORDER BY c.segment NULLS LAST;
```

**Expected shape:** One row per segment.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** One row per segment.
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

## Exercise 3 — Query writing

**Prompt:** Unpivot a wide quarterly sample into quarter/amount rows.

**Reasoning:** Use a lateral `VALUES` relation with one output row per source column.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH wide(company, q1, q2, q3, q4) AS (
  VALUES
    ('A', 10::numeric, 20::numeric, 30::numeric, 40::numeric),
    ('B', 5::numeric, NULL::numeric, 15::numeric, 25::numeric)
)
SELECT w.company,
       unpivoted.quarter,
       unpivoted.amount
FROM wide AS w
CROSS JOIN LATERAL (
  VALUES
    ('Q1', w.q1),
    ('Q2', w.q2),
    ('Q3', w.q3),
    ('Q4', w.q4)
) AS unpivoted(quarter, amount)
ORDER BY w.company, unpivoted.quarter;
```

**Expected shape:** Eight rows from two source rows and four quarters.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Eight rows from two source rows and four quarters.
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

## Exercise 4 — Prediction

**Prompt:** Compare a missing pivot combination with a real zero and preserve the distinction.

**Reasoning:** Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.category,
       SUM(e.amount) FILTER (
         WHERE EXTRACT(MONTH FROM e.expense_date) = 1
       ) AS january_observed_amount,
       COALESCE(
         SUM(e.amount) FILTER (
           WHERE EXTRACT(MONTH FROM e.expense_date) = 1
         ),
         0
       ) AS january_reported_zero_if_absent
FROM expenses AS e
GROUP BY e.category
ORDER BY e.category;
```

**Expected shape:** One row per expense category with nullable/zero-aware columns.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** One row per expense category with nullable/zero-aware columns.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
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

## Exercise 5 — Debugging

**Prompt:** Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.

**Reasoning:** Aggregate category/value pairs into data values so the result schema remains stable.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       jsonb_object_agg(category, revenue ORDER BY category) AS revenue_by_category
FROM category_month
GROUP BY month_start
ORDER BY month_start;
```

**Expected shape:** One row per UTC month with a JSON object of category revenue.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** One row per UTC month with a JSON object of category revenue.
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

## Exercise 6 — Extension

**Prompt:** Round-trip a wide sample to long form and back, verifying values and NULLs.

**Reasoning:** Unpivot with lateral values, then use conditional aggregation keyed by company.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH wide(company, q1, q2) AS (
  VALUES
    ('A', 10::numeric, 20::numeric),
    ('B', NULL::numeric, 5::numeric)
), long AS (
  SELECT w.company, u.quarter, u.amount
  FROM wide AS w
  CROSS JOIN LATERAL (
    VALUES ('Q1', w.q1), ('Q2', w.q2)
  ) AS u(quarter, amount)
)
SELECT company,
       MAX(amount) FILTER (WHERE quarter = 'Q1') AS q1,
       MAX(amount) FILTER (WHERE quarter = 'Q2') AS q2
FROM long
GROUP BY company
ORDER BY company;
```

**Expected shape:** Two reconstructed rows matching the source.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Two reconstructed rows matching the source.
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

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
