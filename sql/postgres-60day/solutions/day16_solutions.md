# Day 16 solutions — Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day16_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day16_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Window, Partition, Frame. Its worked-model focus is:
Pre-aggregate net revenue to one row per category, then calculate SUM(revenue) OVER () beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.

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

These answers align one-for-one with [day16_window_functions_fundamentals.sql](../day16_window_functions_fundamentals.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
- **Assumptions:** Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
- **Primary pitfall:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Show each order with the customer's average order total.

**Reasoning:** Partition by customer ID and keep one output row per order.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS customer_average
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_average`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-16 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-16 Exercise 1, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, and `customer_average` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-16 Exercise 1, the chosen form is justified by this lesson-specific rationale: Partition by customer ID and keep one output row per order. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 2 — Query writing

**Prompt:** Show each employee salary with department average, minimum, and maximum.

**Reasoning:** Partition all three window aggregates by department.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.department_id,
       e.salary,
       ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id), 2) AS department_average,
       MIN(e.salary) OVER (PARTITION BY e.department_id) AS department_minimum,
       MAX(e.salary) OVER (PARTITION BY e.department_id) AS department_maximum
FROM employees AS e
ORDER BY e.department_id, e.employee_id;
```

**Expected shape:** One row per employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 2, expected output: One row per employee. The final columns are `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`. The final order is `e.department_id, e.employee_id`.
- **Independent verification:** For sql-16 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `department_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-16 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.employee_id` before applying the row cap.
- **Clause check:** For sql-16 Exercise 2, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum` ordered by `e.department_id, e.employee_id`.
- **Alternative/trade-off:** For sql-16 Exercise 2, the chosen form is justified by this lesson-specific rationale: Partition all three window aggregates by department. Evaluate another form against the concrete expected result (One row per employee) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 3 — Query writing

**Prompt:** Calculate every order's share of its customer's stored revenue.

**Reasoning:** Use a partition total denominator and guard it with `NULLIF`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       ROUND(
         o.total_amount
           / NULLIF(SUM(o.total_amount) OVER (PARTITION BY o.customer_id), 0),
         4
       ) AS customer_revenue_share
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order with shares summing near one per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 3, expected output: One row per order with shares summing near one per customer. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_revenue_share`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-16 Exercise 3, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-16 Exercise 3, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-16 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use a partition total denominator and guard it with `NULLIF`. Evaluate another form against the concrete expected result (One row per order with shares summing near one per customer) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Prediction

**Prompt:** Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.

**Reasoning:** Grouping collapses to one row per customer; a window preserves every order row.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH grouped AS (
  SELECT o.customer_id, AVG(o.total_amount) AS average_total
  FROM orders AS o
  GROUP BY o.customer_id
), windowed AS (
  SELECT o.order_id,
         AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS average_total
  FROM orders AS o
)
SELECT 'grouped' AS method, COUNT(*) AS row_count FROM grouped
UNION ALL
SELECT 'windowed' AS method, COUNT(*) AS row_count FROM windowed
ORDER BY method;
```

**Expected shape:** Two labeled count rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 4, read from `orders`. Build the answer toward `method`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 4, expected output: Two labeled count rows. The final columns are `method`, and `row_count`. The final order is `method`.
- **Independent verification:** For sql-16 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `method`, and `row_count` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-16 Exercise 4, run `grouped`, and `windowed` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-16 Exercise 4, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `method`, and `row_count` ordered by `method`.
- **Alternative/trade-off:** For sql-16 Exercise 4, the chosen form is justified by this lesson-specific rationale: Grouping collapses to one row per customer; a window preserves every order row. Evaluate another form against the concrete expected result (Two labeled count rows) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 5 — Debugging

**Prompt:** Return orders above their customer average without placing a window function in `WHERE`.

**Reasoning:** Compute the window value in a CTE, then filter the named column outside.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH scored AS (
  SELECT o.*,
         AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_average
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       total_amount,
       ROUND(customer_average, 2) AS customer_average
FROM scored
WHERE total_amount > customer_average
ORDER BY customer_id, total_amount DESC, order_id;
```

**Expected shape:** Order rows above their customer mean.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_average`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 5, expected output: Order rows above their customer mean. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `customer_id, total_amount DESC, order_id`.
- **Independent verification:** For sql-16 Exercise 5, run an anti-check that counts rows where NOT ((total_amount > customer_average)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `total_amount`, and `customer_average` against `orders`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-16 Exercise 5, run `scored` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-16 Exercise 5, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `total_amount`, and `customer_average` ordered by `customer_id, total_amount DESC, order_id`.
- **Alternative/trade-off:** For sql-16 Exercise 5, the chosen form is justified by this lesson-specific rationale: Compute the window value in a CTE, then filter the named column outside. Evaluate another form against the concrete expected result (Order rows above their customer mean) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 6 — Extension

**Prompt:** Show order count and revenue context at both customer and country levels in the same row.

**Reasoning:** Use different partitions for independent analytical contexts.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       c.country,
       COUNT(*) OVER (PARTITION BY o.customer_id) AS customer_order_count,
       SUM(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_revenue,
       SUM(o.total_amount) OVER (PARTITION BY c.country) AS country_revenue
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY c.country, o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order with customer and country totals.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-16 Exercise 6, read from `orders`, and `customers`. Build the answer toward `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-16 Exercise 6, expected output: One row per order with customer and country totals. The final columns are `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`. The final order is `c.country, o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-16 Exercise 6, choose one complete partition from `orders`, and `customers`; hand-calculate its first, middle, and final window values for `customer_order_count`, `customer_revenue`, and `country_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-16 Exercise 6, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-16 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue` ordered by `c.country, o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-16 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use different partitions for independent analytical contexts. Evaluate another form against the concrete expected result (One row per order with customer and country totals) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
