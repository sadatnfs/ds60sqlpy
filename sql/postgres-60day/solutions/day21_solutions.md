# Day 21 solutions — Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day21_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day21_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Quantile bucket, Percent rank, Cumulative distribution. Its worked-model focus is:
Apply NTILE(4), PERCENTRANK, and CUMEDIST to a five-row VALUES set containing a tie. Observe that buckets need not have equal value ranges and that peer-aware distribution functions treat equal ordering values together.

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

These answers align one-for-one with [day21_distribution_functions.sql](../day21_distribution_functions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
- **Assumptions:** `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
- **Primary pitfall:** A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Assign customers to four stored-spend buckets.

**Reasoning:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH customer_spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS stored_spend
  FROM orders AS o
  GROUP BY o.customer_id
)
SELECT customer_id,
       ROUND(stored_spend, 2) AS stored_spend,
       NTILE(4) OVER (
         ORDER BY stored_spend DESC, customer_id
       ) AS spend_quartile
FROM customer_spend
ORDER BY spend_quartile, stored_spend DESC, customer_id;
```

**Expected shape:** One row per ordering customer with bucket 1–4.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 1, read from `orders`. Build the answer toward `customer_id`, `stored_spend`, and `spend_quartile`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 1, expected output: One row per ordering customer with bucket 1–4. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
- **Independent verification:** For sql-21 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `customer_id`, `stored_spend`, and `spend_quartile`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-21 Exercise 1, run `customer_spend` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-21 Exercise 1, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `customer_id`, `stored_spend`, and `spend_quartile` ordered by `spend_quartile, stored_spend DESC, customer_id`.
- **Alternative/trade-off:** For sql-21 Exercise 1, the chosen form is justified by this lesson-specific rationale: Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker. Evaluate another form against the concrete expected result (One row per ordering customer with bucket 1–4) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 2 — Query writing

**Prompt:** Calculate salary percent rank within each department.

**Reasoning:** Partition by department and rank on salary alone so tied salaries share rank.

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
       PERCENT_RANK() OVER (
         PARTITION BY e.department_id ORDER BY e.salary
       ) AS salary_percent_rank
FROM employees AS e
ORDER BY e.department_id, e.salary, e.employee_id;
```

**Expected shape:** One row per employee with values from 0 to 1.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `salary_percent_rank`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 2, expected output: One row per employee with values from 0 to 1. The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
- **Independent verification:** For sql-21 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `salary_percent_rank`, then verify output keys remain `employee_id`. Give two rows the same `e.department_id` value and different `e.employee_id` values; verify `e.department_id, e.salary, e.employee_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-21 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.salary, e.employee_id` before applying the row cap.
- **Clause check:** For sql-21 Exercise 2, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `department_id`, `salary`, and `salary_percent_rank` ordered by `e.department_id, e.salary, e.employee_id`.
- **Alternative/trade-off:** For sql-21 Exercise 2, the chosen form is justified by this lesson-specific rationale: Partition by department and rank on salary alone so tied salaries share rank. Evaluate another form against the concrete expected result (One row per employee with values from 0 to 1) and the verification above.
- **Edge case:** Give two rows the same `e.department_id` value and different `e.employee_id` values; verify `e.department_id, e.salary, e.employee_id` produces the intended rank and display order.

## Exercise 3 — Query writing

**Prompt:** Calculate cumulative distribution of product price within category.

**Reasoning:** Partition by category and order on price.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.category,
       p.price,
       CUME_DIST() OVER (
         PARTITION BY p.category ORDER BY p.price
       ) AS price_cume_dist
FROM products AS p
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product with cume_dist in (0, 1].

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 3, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `price_cume_dist`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 3, expected output: One row per product with cume_dist in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-21 Exercise 3, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `price_cume_dist`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-21 Exercise 3, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.
- **Clause check:** For sql-21 Exercise 3, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `category`, `price`, and `price_cume_dist` ordered by `p.category, p.price, p.product_id`.
- **Alternative/trade-off:** For sql-21 Exercise 3, the chosen form is justified by this lesson-specific rationale: Partition by category and order on price. Evaluate another form against the concrete expected result (One row per product with cume_dist in (0, 1]) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Prediction

**Prompt:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.

**Reasoning:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT row_id,
       value,
       PERCENT_RANK() OVER (ORDER BY value) AS percent_rank_value,
       CUME_DIST() OVER (ORDER BY value) AS cume_dist_value
FROM (VALUES (1, 10), (2, 10), (3, 20)) AS sample(row_id, value)
ORDER BY row_id;
```

**Expected shape:** Three rows making tie behavior visible.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`; keep `row_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 4, expected output: Three rows making tie behavior visible. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
- **Independent verification:** For sql-21 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `percent_rank_value`, and `cume_dist_value`, then verify output keys remain `row_id`. Give two rows the same `row_id` value and different ``row_id`` values; verify `row_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-21 Exercise 4, inspect one window partition before projecting; then check `row_id` before applying the row cap.
- **Clause check:** For sql-21 Exercise 4, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `row_id`, and finish with `row_id`, `value`, `percent_rank_value`, and `cume_dist_value` ordered by `row_id`.
- **Alternative/trade-off:** For sql-21 Exercise 4, the chosen form is justified by this lesson-specific rationale: Tied values share rank and cumulative endpoint, but the two functions use different formulas. Evaluate another form against the concrete expected result (Three rows making tie behavior visible) and the verification above.
- **Edge case:** Give two rows the same `row_id` value and different ``row_id`` values; verify `row_id` produces the intended rank and display order.

## Exercise 5 — Debugging

**Prompt:** Audit the row count in each customer spend decile rather than assuming exact equality.

**Reasoning:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS total_spend
  FROM orders AS o
  GROUP BY o.customer_id
), bucketed AS (
  SELECT customer_id,
         NTILE(10) OVER (
           ORDER BY total_spend DESC, customer_id
         ) AS decile
  FROM spend
)
SELECT decile,
       COUNT(*) AS customers
FROM bucketed
GROUP BY decile
ORDER BY decile;
```

**Expected shape:** Up to 10 bucket rows with counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 5, read from `orders`. Build the answer toward `decile`, and `customers`; keep `decile` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 5, expected output: Up to 10 bucket rows with counts. The final columns are `decile`, and `customers`. The final order is `decile`.
- **Independent verification:** For sql-21 Exercise 5, independently aggregate `orders` by `decile`; require one output row for every distinct `decile` tuple and compare `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers` for the existing `decile` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-21 Exercise 5, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `decile` uniqueness before the next stage uses it.
- **Clause check:** For sql-21 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `decile`, and finish with `decile`, and `customers` ordered by `decile`.
- **Alternative/trade-off:** For sql-21 Exercise 5, the chosen form is justified by this lesson-specific rationale: NTILE bucket sizes differ by at most one when row count is not divisible by ten. Evaluate another form against the concrete expected result (Up to 10 bucket rows with counts) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `customers` for the existing `decile` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Extension

**Prompt:** Return customers in the top stored-spend decile with their spend and population share.

**Reasoning:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH spend AS (
  SELECT o.customer_id,
         SUM(o.total_amount) AS total_spend
  FROM orders AS o
  GROUP BY o.customer_id
), bucketed AS (
  SELECT customer_id,
         total_spend,
         NTILE(10) OVER (
           ORDER BY total_spend DESC, customer_id
         ) AS decile,
         COUNT(*) OVER () AS population
  FROM spend
)
SELECT customer_id,
       ROUND(total_spend, 2) AS total_spend,
       decile,
       population
FROM bucketed
WHERE decile = 1
ORDER BY total_spend DESC, customer_id;
```

**Expected shape:** Customers in decile 1.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-21 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `total_spend`, `decile`, and `population`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-21 Exercise 6, expected output: Customers in decile 1. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
- **Independent verification:** For sql-21 Exercise 6, run an anti-check that counts rows where NOT ((decile = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `total_spend`, `decile`, and `population` against `orders`. Give two rows the same `total_spend DESC` value and different `customer_id` values; verify `total_spend DESC, customer_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-21 Exercise 6, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-21 Exercise 6, the solution actually uses `WITH`, `FROM`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `customer_id`, and finish with `customer_id`, `total_spend`, `decile`, and `population` ordered by `total_spend DESC, customer_id`.
- **Alternative/trade-off:** For sql-21 Exercise 6, the chosen form is justified by this lesson-specific rationale: Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending. Evaluate another form against the concrete expected result (Customers in decile 1) and the verification above.
- **Edge case:** Give two rows the same `total_spend DESC` value and different `customer_id` values; verify `total_spend DESC, customer_id` produces the intended rank and display order.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
