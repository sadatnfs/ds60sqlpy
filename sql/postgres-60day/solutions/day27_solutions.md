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

- **Inputs/evidence:** For sql-27 Exercise 1, read from `orders`. Build the answer toward `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 1, expected output: Exactly one row. The final columns are `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
- **Independent verification:** For sql-27 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-27 Exercise 1, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-27 Exercise 1, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
- **Alternative/trade-off:** For sql-27 Exercise 1, the chosen form is justified by this lesson-specific rationale: Use one filtered count per known status and keep an all-orders denominator. Evaluate another form against the concrete expected result (Exactly one row) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

- **Inputs/evidence:** For sql-27 Exercise 2, read from `customers`. Build the answer toward `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`; keep `segment` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 2, expected output: One row per segment. The final columns are `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`. The final order is `c.segment NULLS LAST`.
- **Independent verification:** For sql-27 Exercise 2, independently aggregate `customers` by `segment`; require one output row for every distinct `segment` tuple and compare `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `us_customers`, `ca_customers`, and `gb_customers` for the existing `segment` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-27 Exercise 2, inspect the source keys that survive `WHERE`; then confirm the groups are `segment`; then check `c.segment NULLS LAST` before applying the row cap.
- **Clause check:** For sql-27 Exercise 2, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `segment`, and finish with `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers` ordered by `c.segment NULLS LAST`.
- **Alternative/trade-off:** For sql-27 Exercise 2, the chosen form is justified by this lesson-specific rationale: Group at segment grain and use filtered counts for known country columns. Evaluate another form against the concrete expected result (One row per segment) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `us_customers`, `ca_customers`, and `gb_customers` for the existing `segment` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-27 Exercise 3, read from `wide`. Build the answer toward `company`, `quarter`, and `amount`; keep `company` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 3, expected output: Eight rows from two source rows and four quarters. The final columns are `company`, `quarter`, and `amount`. The final order is `w.company, unpivoted.quarter`.
- **Independent verification:** For sql-27 Exercise 3, project `company` plus the raw source columns from `wide` at each join stage; record row count and distinct `company`, then assert the final `company`, `quarter`, and `amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `company`; verify the result gains exactly one row carrying that `company` value.
- **Intermediate relation check:** For sql-27 Exercise 3, start with the first relation in `wide`; after each join, record total rows and distinct `company` so the exact fanout or loss is visible.
- **Clause check:** For sql-27 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `wide`, preserve one row per `company`, and finish with `company`, `quarter`, and `amount` ordered by `w.company, unpivoted.quarter`.
- **Alternative/trade-off:** For sql-27 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use a lateral `VALUES` relation with one output row per source column. Evaluate another form against the concrete expected result (Eight rows from two source rows and four quarters) and the verification above.
- **Edge case:** Add one source row with a new `company`; verify the result gains exactly one row carrying that `company` value.

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

- **Inputs/evidence:** For sql-27 Exercise 4, read from `expenses`. Build the answer toward `category`, `january_observed_amount`, and `january_reported_zero_if_absent`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 4, expected output: One row per expense category with nullable/zero-aware columns. The final columns are `category`, `january_observed_amount`, and `january_reported_zero_if_absent`. The final order is `e.category`.
- **Independent verification:** For sql-27 Exercise 4, independently aggregate `expenses` by `category`; require one output row for every distinct `category` tuple and compare `january_observed_amount` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `january_observed_amount` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-27 Exercise 4, inspect the source keys that survive `WHERE`; then confirm the groups are `category`; then check `e.category` before applying the row cap.
- **Clause check:** For sql-27 Exercise 4, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, preserve one row per `category`, and finish with `category`, `january_observed_amount`, and `january_reported_zero_if_absent` ordered by `e.category`.
- **Alternative/trade-off:** For sql-27 Exercise 4, the chosen form is justified by this lesson-specific rationale: Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero. Evaluate another form against the concrete expected result (One row per expense category with nullable/zero-aware columns) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `january_observed_amount` for the existing `category` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-27 Exercise 5, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, and `revenue_by_category`; keep `month_start` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 5, expected output: One row per UTC month with a JSON object of category revenue. The final columns are `month_start`, and `revenue_by_category`. The final order is `month_start`.
- **Independent verification:** For sql-27 Exercise 5, independently aggregate `orders`, `order_items`, and `products` by `month_start`; require one output row for every distinct `month_start` tuple and compare `revenue_by_category` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_by_category` for the existing `month_start` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-27 Exercise 5, run `category_month` one at a time. Record each CTE's row count and `month_start` uniqueness before the next stage uses it.
- **Clause check:** For sql-27 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `month_start`, and finish with `month_start`, and `revenue_by_category` ordered by `month_start`.
- **Alternative/trade-off:** For sql-27 Exercise 5, the chosen form is justified by this lesson-specific rationale: Aggregate category/value pairs into data values so the result schema remains stable. Evaluate another form against the concrete expected result (One row per UTC month with a JSON object of category revenue) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `revenue_by_category` for the existing `month_start` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-27 Exercise 6, read from `wide`. Build the answer toward `company`, `q1`, and `q2`; keep `company` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-27 Exercise 6, expected output: Two reconstructed rows matching the source. The final columns are `company`, `q1`, and `q2`. The final order is `company`.
- **Independent verification:** For sql-27 Exercise 6, independently aggregate `wide` by `company`; require one output row for every distinct `company` tuple and compare `q1`, and `q2` tuple by tuple. Repeat with `NULL` in `company`, and `q1` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-27 Exercise 6, run `long` one at a time. Record each CTE's row count and `company` uniqueness before the next stage uses it.
- **Clause check:** For sql-27 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `wide`, preserve one row per `company`, and finish with `company`, `q1`, and `q2` ordered by `company`.
- **Alternative/trade-off:** For sql-27 Exercise 6, the chosen form is justified by this lesson-specific rationale: Unpivot with lateral values, then use conditional aggregation keyed by company. Evaluate another form against the concrete expected result (Two reconstructed rows matching the source) and the verification above.
- **Edge case:** Repeat with `NULL` in `company`, and `q1` and state whether the row is kept, rejected, or classified.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
