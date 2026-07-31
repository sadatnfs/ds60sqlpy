# Day 26 solutions — CTEs with Window Functions: Layered Analytics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day26_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day26_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Layered analytics, Window input grain, QUALIFY alternative. Its worked-model focus is:
Create monthly totals in one CTE, add LAG(total) in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the LAG layer makes the prior value visible and lets you inspect both values before interpreting the percentage.

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

These answers align one-for-one with [day26_ctes_with_windows.sql](../day26_ctes_with_windows.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
- **Assumptions:** Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
- **Primary pitfall:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Calculate monthly stored revenue and its prior-month value/change.

**Reasoning:** Aggregate to month in a CTE, then lag the monthly measure.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), compared AS (
  SELECT month_start,
         revenue,
         LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM monthly
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_revenue, 2) AS previous_revenue,
       ROUND(revenue - previous_revenue, 2) AS change
FROM compared
ORDER BY month_start;
```

**Expected shape:** One row per observed month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 1, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `change`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 1, expected output: One row per observed month. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
- **Independent verification:** For sql-26 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `change` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-26 Exercise 1, run `monthly`, and `compared` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 1, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `month_start`, `revenue`, `previous_revenue`, and `change` ordered by `month_start`.
- **Alternative/trade-off:** For sql-26 Exercise 1, the chosen form is justified by this lesson-specific rationale: Aggregate to month in a CTE, then lag the monthly measure. Evaluate another form against the concrete expected result (One row per observed month) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 2 — Query writing

**Prompt:** Rank product categories by net revenue within each UTC order month.

**Reasoning:** Aggregate month/category first, then rank the stable aggregate.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  JOIN products AS p
    ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       category,
       ROUND(revenue, 2) AS revenue,
       DENSE_RANK() OVER (
         PARTITION BY month_start ORDER BY revenue DESC
       ) AS revenue_rank
FROM category_month
ORDER BY month_start, revenue_rank, category;
```

**Expected shape:** One row per observed month/category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 2, expected output: One row per observed month/category. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
- **Independent verification:** For sql-26 Exercise 2, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `revenue_rank`, then verify output keys remain `category`. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
- **Intermediate relation check:** For sql-26 Exercise 2, run `category_month` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `category`, and finish with `month_start`, `category`, `revenue`, and `revenue_rank` ordered by `month_start, revenue_rank, category`.
- **Alternative/trade-off:** For sql-26 Exercise 2, the chosen form is justified by this lesson-specific rationale: Aggregate month/category first, then rank the stable aggregate. Evaluate another form against the concrete expected result (One row per observed month/category) and the verification above.
- **Edge case:** Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.

## Exercise 3 — Query writing

**Prompt:** Return the top three category revenue levels per month.

**Reasoning:** Rank in one CTE and filter the window result outside.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
), ranked AS (
  SELECT category_month.*,
         DENSE_RANK() OVER (
           PARTITION BY month_start ORDER BY revenue DESC
         ) AS revenue_rank
  FROM category_month
)
SELECT month_start, category, ROUND(revenue, 2) AS revenue, revenue_rank
FROM ranked
WHERE revenue_rank <= 3
ORDER BY month_start, revenue_rank, category;
```

**Expected shape:** Top three revenue ranks for each observed month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 3, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 3, expected output: Top three revenue ranks for each observed month. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
- **Independent verification:** For sql-26 Exercise 3, project `category` plus the raw source columns from `orders`, `order_items`, and `products` at each join stage; record row count and distinct `category`, then assert the final `month_start`, `category`, `revenue`, and `revenue_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
- **Intermediate relation check:** For sql-26 Exercise 3, run `category_month`, and `ranked` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `category`, and finish with `month_start`, `category`, `revenue`, and `revenue_rank` ordered by `month_start, revenue_rank, category`.
- **Alternative/trade-off:** For sql-26 Exercise 3, the chosen form is justified by this lesson-specific rationale: Rank in one CTE and filter the window result outside. Evaluate another form against the concrete expected result (Top three revenue ranks for each observed month) and the verification above.
- **Edge case:** Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.

## Exercise 4 — Prediction

**Prompt:** Calculate each category's cumulative share of monthly revenue in descending contribution order.

**Reasoning:** Divide running category revenue by the full monthly total; use explicit frames.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       category,
       ROUND(revenue, 2) AS revenue,
       ROUND(
         SUM(revenue) OVER (
           PARTITION BY month_start
           ORDER BY revenue DESC, category
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) / NULLIF(SUM(revenue) OVER (PARTITION BY month_start), 0),
         4
       ) AS cumulative_revenue_share
FROM category_month
ORDER BY month_start, revenue DESC, category;
```

**Expected shape:** One row per month/category with final share equal to one.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `cumulative_revenue_share`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 4, expected output: One row per month/category with final share equal to one. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
- **Independent verification:** For sql-26 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `cumulative_revenue_share`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-26 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `month`, and finish with `month_start`, `category`, `revenue`, and `cumulative_revenue_share` ordered by `month_start, revenue DESC, category`.
- **Alternative/trade-off:** For sql-26 Exercise 4, the chosen form is justified by this lesson-specific rationale: Divide running category revenue by the full monthly total; use explicit frames. Evaluate another form against the concrete expected result (One row per month/category with final share equal to one) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Debugging

**Prompt:** Calculate a three-month moving average after building a dense month calendar.

**Reasoning:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH bounds AS (
  SELECT MIN(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS first_month,
         MAX(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS last_month
  FROM orders AS o
), calendar AS (
  SELECT generate_series(first_month, last_month, INTERVAL '1 month')::date AS month_start
  FROM bounds
), monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), dense AS (
  SELECT c.month_start,
         COALESCE(m.revenue, 0) AS revenue
  FROM calendar AS c
  LEFT JOIN monthly AS m USING (month_start)
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(
         AVG(revenue) OVER (
           ORDER BY month_start
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
         ),
         2
       ) AS moving_3_month_average
FROM dense
ORDER BY month_start;
```

**Expected shape:** A continuous chronological month series.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, and `moving_3_month_average`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 5, expected output: A continuous chronological month series. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
- **Independent verification:** For sql-26 Exercise 5, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `moving_3_month_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-26 Exercise 5, run `bounds`, `calendar`, `monthly`, and `dense` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `month_start`, `revenue`, and `moving_3_month_average` ordered by `month_start`.
- **Alternative/trade-off:** For sql-26 Exercise 5, the chosen form is justified by this lesson-specific rationale: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way. Evaluate another form against the concrete expected result (A continuous chronological month series) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 6 — Extension

**Prompt:** Reconcile the final cumulative monthly revenue with the independent order total.

**Reasoning:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), running AS (
  SELECT month_start,
         SUM(revenue) OVER (
           ORDER BY month_start
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS cumulative_revenue
  FROM monthly
), final AS (
  SELECT cumulative_revenue
  FROM running
  ORDER BY month_start DESC
  LIMIT 1
)
SELECT ROUND(final.cumulative_revenue, 2) AS final_cumulative,
       ROUND(SUM(o.total_amount), 2) AS independent_total,
       ROUND(final.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM final
CROSS JOIN orders AS o
GROUP BY final.cumulative_revenue;
```

**Expected shape:** One row with zero difference.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `independent_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-26 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `independent_total`, and `difference`.
- **Independent verification:** For sql-26 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `independent_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `independent_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-26 Exercise 6, run `monthly`, `running`, and `final` one at a time. Record each CTE's row count and `cumulative_revenue` uniqueness before the next stage uses it.
- **Clause check:** For sql-26 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `cumulative_revenue`, and finish with `final_cumulative`, `independent_total`, and `difference`.
- **Alternative/trade-off:** For sql-26 Exercise 6, the chosen form is justified by this lesson-specific rationale: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals. Evaluate another form against the concrete expected result (One row with zero difference) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `independent_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
