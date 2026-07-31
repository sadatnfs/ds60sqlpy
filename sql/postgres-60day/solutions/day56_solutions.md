# Day 56 Solutions — CUBE and Percentiles


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day56_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day56_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Dimensional explosion, Primary payment method, Continuous percentile. Its worked-model focus is:
Aggregate payments at (orderid, method), select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at (month, category, orderid) before computing p50/p90; whole order totals would repeat across categories.

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

The exercises add payment method to a multidimensional cube and calculate
category-attributable order-value percentiles by month. See
[`day56_solutions.sql`](day56_solutions.sql).

## Exercise 1 — Add payment method and measure cube growth

An order can have more than one payment. The answer defines its primary method
as the method with the greatest total paid amount, breaking ties by method name.
Reducing to one method prevents order lines from being duplicated; unpaid
orders remain visible.

```sql
SET search_path TO training, public;

WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS paid_amount
  FROM payments
  GROUP BY order_id, method
), ranked_payment AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY order_id ORDER BY paid_amount DESC, method
         ) AS payment_rank
  FROM payment_by_method
), primary_payment AS (
  SELECT order_id, method
  FROM ranked_payment
  WHERE payment_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  LEFT JOIN primary_payment pp USING (order_id)
), cube_two AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
), cube_three AS (
  SELECT country, category, payment_method, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category, payment_method)
)
SELECT (SELECT COUNT(*) FROM cube_two) AS two_dimension_rows,
       (SELECT COUNT(*) FROM cube_three) AS three_dimension_rows;
```

Expected shape: one row; `three_dimension_rows` should be larger.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 1, read from `payments`, `orders`, `customers`, `order_items`, and `products`. Compute `two_dimension_rows`, and `three_dimension_rows` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-56 Exercise 1, expected output: one row; `three_dimension_rows` should be larger. The final columns are `two_dimension_rows`, and `three_dimension_rows`.
- **Independent verification:** For sql-56 Exercise 1, evaluate each of `two_dimension_rows`, and `three_dimension_rows` in a separate control `SELECT` over `payments`, `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
- **Intermediate relation check:** For sql-56 Exercise 1, run `payment_by_method`, `ranked_payment`, `primary_payment`, `line`, `cube_two`, and `cube_three` one at a time. Record each CTE's row count and `payment_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-56 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, `orders`, `customers`, `order_items`, and `products`, preserve exactly one summary row, and finish with `two_dimension_rows`, and `three_dimension_rows`.
- **Alternative/trade-off:** For sql-56 Exercise 1, the chosen form is justified by this lesson-specific rationale: An order can have more than one payment. Evaluate another form against the concrete expected result (one row; `three_dimension_rows` should be larger) and the verification above.
- **Edge case:** Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.

## Exercise 2 — Category-month p50 and p90

The metric is each category's contribution to an order, not the entire order
total repeated for every category.

```sql
SET search_path TO training, public;

WITH category_orders AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         p.category,
         o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY date_trunc('month', o.order_date), p.category, o.order_id
)
SELECT month,
       category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p90_order_value
FROM category_orders
GROUP BY month, category
ORDER BY month DESC, category;
```

Expected grain: one row per represented `(month, category)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `p50_order_value`, and `p90_order_value`; keep `month`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-56 Exercise 2, expected output: one row per represented `(month, category)`. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
- **Independent verification:** For sql-56 Exercise 2, independently aggregate `orders`, `order_items`, and `products` by `month`, and `category`; require one output row for every distinct `month`, and `category` tuple and compare `p50_order_value`, and `p90_order_value` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50_order_value`, and `p90_order_value` for the existing `month`, and `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-56 Exercise 2, run `category_orders` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-56 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `month`, and `category`, and finish with `month`, `category`, `p50_order_value`, and `p90_order_value` ordered by `month DESC, category`.
- **Alternative/trade-off:** For sql-56 Exercise 2, the chosen form is justified by this lesson-specific rationale: The metric is each category's contribution to an order, not the entire order total repeated for every category. Evaluate another form against the concrete expected result (one row per represented `(month, category)`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `p50_order_value`, and `p90_order_value` for the existing `month`, and `category` tuple and verify the new tuple appears exactly once.

## Reasoning, safety, and pitfalls

- Joining all payment rows to lines would multiply revenue for split-payment
  orders. Define a payment attribution policy before adding that dimension.
- Aggregate by `(order_id, method)` before ranking so split payments using the
  same method are compared by their total paid amount.
- The method-name tie-break makes the primary-method policy deterministic.
- `percentile_cont` interpolates and returns a floating type; cast to numeric
  before two-argument `ROUND`.
- Percentiles need enough observations. Always accompany production percentiles
  with sample counts.

## Exercise 3 — Measure raw fanout

The raw payment/item join reports joined rows and distinct source keys. Orders
with several rows on both sides demonstrate the multiplication risk.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 3, read from `orders`, `order_items`, and `payments`. Build the answer toward `raw_join_rows`, `distinct_items`, and `distinct_payments`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-56 Exercise 3, expected output: one row per `order_id`. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
- **Independent verification:** For sql-56 Exercise 3, project `order_id` plus the raw source columns from `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `order_id`, then assert the final `raw_join_rows`, `distinct_items`, and `distinct_payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-56 Exercise 3, start with the first relation in `orders`, `order_items`, and `payments`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-56 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `orders`, `order_items`, and `payments`, preserve one row per `order_id`, and finish with `raw_join_rows`, `distinct_items`, and `distinct_payments`.
- **Alternative/trade-off:** For sql-56 Exercise 3, the chosen form is justified by this lesson-specific rationale: The raw payment/item join reports joined rows and distinct source keys. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 4 — Attribute at order grain

Payment policy reduces methods to one order-level label; line revenue also
reduces to one order row. The windowed grand total reconciles attribution.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 4, read from `payments`, and `order_items`. Build the answer toward `reporting_method`, `revenue`, and `reconciled_total`; keep `payment_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-56 Exercise 4, expected output: one row per `payment_id`. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
- **Independent verification:** For sql-56 Exercise 4, choose one complete partition from `payments`, and `order_items`; hand-calculate its first, middle, and final window values for `revenue`, and `reconciled_total`, then verify output keys remain `payment_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-56 Exercise 4, run `method`, `lines`, and `attributed` one at a time. Record each CTE's row count and `payment_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-56 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, and `order_items`, preserve one row per `payment_id`, and finish with `reporting_method`, `revenue`, and `reconciled_total` ordered by `reporting_method`.
- **Alternative/trade-off:** For sql-56 Exercise 4, the chosen form is justified by this lesson-specific rationale: Payment policy reduces methods to one order-level label; line revenue also reduces to one order row. Evaluate another form against the concrete expected result (one row per `payment_id`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Match percentile grain

`category_order` emits one observation per category/order before calculating
P50. A line-item percentile would answer a different question.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 5, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, and `p50`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-56 Exercise 5, expected output: one row per `category`. The final columns are `category`, `observations`, and `p50`. The final order is `category`.
- **Independent verification:** For sql-56 Exercise 5, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-56 Exercise 5, run `category_order` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-56 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `category`, and finish with `category`, `observations`, and `p50` ordered by `category`.
- **Alternative/trade-off:** For sql-56 Exercise 5, the chosen form is justified by this lesson-specific rationale: `category_order` emits one observation per category/order before calculating P50. Evaluate another form against the concrete expected result (one row per `category`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `p50` for the existing `category` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Compare percentile definitions

Continuous P50 can interpolate; discrete P50 is an observed order value. The
observation count is retained so even-sized groups can be interpreted.

### Reasoning and verification

- **Inputs/evidence:** For sql-56 Exercise 6, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, `continuous_p50`, and `discrete_p50`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-56 Exercise 6, expected output: one row per `category`. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
- **Independent verification:** For sql-56 Exercise 6, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `continuous_p50`, and `discrete_p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `continuous_p50`, and `discrete_p50` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-56 Exercise 6, run `category_order` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-56 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `category`, and finish with `category`, `observations`, `continuous_p50`, and `discrete_p50` ordered by `category`.
- **Alternative/trade-off:** For sql-56 Exercise 6, the chosen form is justified by this lesson-specific rationale: Continuous P50 can interpolate; discrete P50 is an observed order value. Evaluate another form against the concrete expected result (one row per `category`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `continuous_p50`, and `discrete_p50` for the existing `category` tuple and verify the new tuple appears exactly once.
