# Day 19 solutions — Running Aggregates and Moving Windows


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day19_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day19_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cumulative aggregate, Moving window, Observation. Its worked-model focus is:
Aggregate orders to daily revenue, then apply ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.

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

These answers align one-for-one with [day19_running_aggregates.sql](../day19_running_aggregates.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
- **Assumptions:** Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
- **Primary pitfall:** Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Calculate cumulative stored revenue across all orders.

**Reasoning:** Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_revenue
FROM orders AS o
ORDER BY o.order_date, o.order_id;
```

**Expected shape:** One row per order with nondecreasing cumulative revenue.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 1, expected output: One row per order with nondecreasing cumulative revenue. The final columns are `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`. The final order is `o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `cumulative_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-19 Exercise 1, inspect one window partition before projecting; then check `o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-19 Exercise 1, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, `total_amount`, and `cumulative_revenue` ordered by `o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-19 Exercise 1, the chosen form is justified by this lesson-specific rationale: Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`. Evaluate another form against the concrete expected result (One row per order with nondecreasing cumulative revenue) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 2 — Query writing

**Prompt:** Calculate each customer's cumulative stored spend.

**Reasoning:** Partition by customer and reset the explicit row frame for every customer.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS customer_cumulative_spend
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 2, expected output: One row per order. The final columns are `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 2, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `customer_cumulative_spend`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-19 Exercise 2, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-19 Exercise 2, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-19 Exercise 2, the chosen form is justified by this lesson-specific rationale: Partition by customer and reset the explicit row frame for every customer. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 3 — Query writing

**Prompt:** Calculate a trailing seven-order average within each customer.

**Reasoning:** A seven-row frame is based on observations, not seven calendar days.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       ROUND(
         AVG(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
         ),
         2
       ) AS trailing_7_order_average
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order with up to seven observations in its frame.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 3, expected output: One row per order with up to seven observations in its frame. The final columns are `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `trailing_7_order_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-19 Exercise 3, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-19 Exercise 3, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-19 Exercise 3, the chosen form is justified by this lesson-specific rationale: A seven-row frame is based on observations, not seven calendar days. Evaluate another form against the concrete expected result (One row per order with up to seven observations in its frame) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Prediction

**Prompt:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.

**Reasoning:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT row_id,
       sort_value,
       amount,
       SUM(amount) OVER (
         ORDER BY sort_value, row_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS rows_sum,
       SUM(amount) OVER (
         ORDER BY sort_value
         RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS range_sum
FROM (VALUES
  (1, 1, 10),
  (2, 1, 20),
  (3, 2, 5)
) AS sample(row_id, sort_value, amount)
ORDER BY row_id;
```

**Expected shape:** Three rows making the peer difference visible.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`; keep `row_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 4, expected output: Three rows making the peer difference visible. The final columns are `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`. The final order is `row_id`.
- **Independent verification:** For sql-19 Exercise 4, hand-calculate all three peer rows from the inline fixture: `rows_sum` must be `(10, 30, 35)` while `range_sum` must be `(30, 30, 35)` in `row_id` order. Require three unique `row_id` values and explain why the two rows tied at `sort_value = 1` advance separately under `ROWS` but together under `RANGE`.
- **Intermediate relation check:** For sql-19 Exercise 4, inspect one window partition before projecting; then check `row_id` before applying the row cap.
- **Clause check:** For sql-19 Exercise 4, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `row_id`, and finish with `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum` ordered by `row_id`.
- **Alternative/trade-off:** For sql-19 Exercise 4, the chosen form is justified by this lesson-specific rationale: `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time. Evaluate another form against the concrete expected result (Three rows making the peer difference visible) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Debugging

**Prompt:** Reset a running expense total at each category and month.

**Reasoning:** Partition by both reset keys and order by date plus expense ID.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.expense_id,
       e.category,
       e.expense_date,
       e.amount,
       SUM(e.amount) OVER (
         PARTITION BY e.category, date_trunc('month', e.expense_date)
         ORDER BY e.expense_date, e.expense_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS category_month_running_expense
FROM expenses AS e
ORDER BY e.category, e.expense_date, e.expense_id;
```

**Expected shape:** One row per expense.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 5, read from `expenses`. Build the answer toward `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`; keep `expense_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 5, expected output: One row per expense. The final columns are `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`. The final order is `e.category, e.expense_date, e.expense_id`.
- **Independent verification:** For sql-19 Exercise 5, choose one complete partition from `expenses`; hand-calculate its first, middle, and final window values for `amount`, then verify output keys remain `expense_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-19 Exercise 5, inspect one window partition before projecting; then check `e.category, e.expense_date, e.expense_id` before applying the row cap.
- **Clause check:** For sql-19 Exercise 5, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, preserve one row per `expense_id`, and finish with `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense` ordered by `e.category, e.expense_date, e.expense_id`.
- **Alternative/trade-off:** For sql-19 Exercise 5, the chosen form is justified by this lesson-specific rationale: Partition by both reset keys and order by date plus expense ID. Evaluate another form against the concrete expected result (One row per expense) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 6 — Extension

**Prompt:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.

**Reasoning:** Select the last ordered cumulative value and compare it with an independent aggregate.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
WITH running AS (
  SELECT o.order_id,
         o.order_date,
         SUM(o.total_amount) OVER (
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS cumulative_revenue
  FROM orders AS o
), final_running AS (
  SELECT r.cumulative_revenue
  FROM running AS r
  ORDER BY r.order_date DESC, r.order_id DESC
  LIMIT 1
)
SELECT ROUND(fr.cumulative_revenue, 2) AS final_cumulative,
       ROUND(SUM(o.total_amount), 2) AS aggregate_total,
       ROUND(fr.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM final_running AS fr
CROSS JOIN orders AS o
GROUP BY fr.cumulative_revenue;
```

**Expected shape:** One row with zero difference.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `aggregate_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-19 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `aggregate_total`, and `difference`.
- **Independent verification:** For sql-19 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `aggregate_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `aggregate_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-19 Exercise 6, run `running`, and `final_running` one at a time. Record each CTE's row count and `cumulative_revenue` uniqueness before the next stage uses it.
- **Clause check:** For sql-19 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `cumulative_revenue`, and finish with `final_cumulative`, `aggregate_total`, and `difference`.
- **Alternative/trade-off:** For sql-19 Exercise 6, the chosen form is justified by this lesson-specific rationale: Select the last ordered cumulative value and compare it with an independent aggregate. Evaluate another form against the concrete expected result (One row with zero difference) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `aggregate_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
