# Day 17 solutions — Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day17_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day17_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Peer rows, Gap rank, Dense rank. Its worked-model focus is:
Rank two products with equal revenue using ROWNUMBER, RANK, and DENSERANK. Add productid as the last ORDER BY key when the requirement is exactly five deterministic rows; omit that tie-breaker when equal metrics must share a business rank.

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

These answers align one-for-one with [day17_rank_functions.sql](../day17_rank_functions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
- **Assumptions:** All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
- **Primary pitfall:** `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Number each customer's orders from newest to oldest.

**Reasoning:** Partition by customer and use order date plus order ID as a unique descending order.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       ROW_NUMBER() OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date DESC, o.order_id DESC
       ) AS recency_number
FROM orders AS o
ORDER BY o.customer_id, recency_number;
```

**Expected shape:** One row per order with sequence starting at one per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `recency_number`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 1, expected output: One row per order with sequence starting at one per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
- **Independent verification:** For sql-17 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, then verify output keys remain `order_id`. Give two rows the same `o.customer_id` value and different `recency_number` values; verify `o.customer_id, recency_number` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, recency_number` before applying the row cap.
- **Clause check:** For sql-17 Exercise 1, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, and `recency_number` ordered by `o.customer_id, recency_number`.
- **Alternative/trade-off:** For sql-17 Exercise 1, the chosen form is justified by this lesson-specific rationale: Partition by customer and use order date plus order ID as a unique descending order. Evaluate another form against the concrete expected result (One row per order with sequence starting at one per customer) and the verification above.
- **Edge case:** Give two rows the same `o.customer_id` value and different `recency_number` values; verify `o.customer_id, recency_number` produces the intended rank and display order.

## Exercise 2 — Query writing

**Prompt:** Rank products by price within category using both `RANK` and `DENSE_RANK`.

**Reasoning:** Rank only on price so equal prices tie; order the final display by product ID.

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
       RANK() OVER (
         PARTITION BY p.category ORDER BY p.price DESC
       ) AS price_rank,
       DENSE_RANK() OVER (
         PARTITION BY p.category ORDER BY p.price DESC
       ) AS dense_price_rank
FROM products AS p
ORDER BY p.category, p.price DESC, p.product_id;
```

**Expected shape:** One row per product with two rank semantics.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 2, read from `products`. Build the answer toward `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 2, expected output: One row per product with two rank semantics. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
- **Independent verification:** For sql-17 Exercise 2, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `price_rank`, and `dense_price_rank`, then verify output keys remain `product_id`. Give two rows the same `p.category` value and different `p.product_id` values; verify `p.category, p.price DESC, p.product_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 2, inspect one window partition before projecting; then check `p.category, p.price DESC, p.product_id` before applying the row cap.
- **Clause check:** For sql-17 Exercise 2, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank` ordered by `p.category, p.price DESC, p.product_id`.
- **Alternative/trade-off:** For sql-17 Exercise 2, the chosen form is justified by this lesson-specific rationale: Rank only on price so equal prices tie; order the final display by product ID. Evaluate another form against the concrete expected result (One row per product with two rank semantics) and the verification above.
- **Edge case:** Give two rows the same `p.category` value and different `p.product_id` values; verify `p.category, p.price DESC, p.product_id` produces the intended rank and display order.

## Exercise 3 — Query writing

**Prompt:** Return the three highest-priced products per category, including price ties.

**Reasoning:** Compute `DENSE_RANK` in a CTE and filter outside.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH ranked AS (
  SELECT p.*,
         DENSE_RANK() OVER (
           PARTITION BY p.category ORDER BY p.price DESC
         ) AS price_rank
  FROM products AS p
)
SELECT product_id,
       name,
       category,
       price,
       price_rank
FROM ranked
WHERE price_rank <= 3
ORDER BY category, price_rank, product_id;
```

**Expected shape:** At least three price levels per category where available.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 3, read from `products`. Build the answer toward `product_id`, `name`, `category`, `price`, and `price_rank`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 3, expected output: At least three price levels per category where available. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
- **Independent verification:** For sql-17 Exercise 3, run an anti-check that counts rows where NOT ((price_rank <= 3)); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, `category`, `price`, and `price_rank` against `products`. Give two rows the same `category` value and different `product_id` values; verify `category, price_rank, product_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 3, run `ranked` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-17 Exercise 3, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `name`, `category`, `price`, and `price_rank` ordered by `category, price_rank, product_id`.
- **Alternative/trade-off:** For sql-17 Exercise 3, the chosen form is justified by this lesson-specific rationale: Compute `DENSE_RANK` in a CTE and filter outside. Evaluate another form against the concrete expected result (At least three price levels per category where available) and the verification above.
- **Edge case:** Give two rows the same `category` value and different `product_id` values; verify `category, price_rank, product_id` produces the intended rank and display order.

## Exercise 4 — Prediction

**Prompt:** Compare row number, rank, and dense rank on values 100, 100, and 90.

**Reasoning:** Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT sample_id,
       score,
       ROW_NUMBER() OVER (ORDER BY score DESC, sample_id) AS row_number_value,
       RANK() OVER (ORDER BY score DESC) AS rank_value,
       DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_value
FROM (VALUES (1, 100), (2, 100), (3, 90)) AS sample(sample_id, score)
ORDER BY sample_id;
```

**Expected shape:** Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`; keep `sample_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
- **Independent verification:** For sql-17 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `score`, `row_number_value`, `rank_value`, and `dense_rank_value`, then verify output keys remain `sample_id`. Give two rows the same `sample_id` value and different ``sample_id`` values; verify `sample_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 4, inspect one window partition before projecting; then check `sample_id` before applying the row cap.
- **Clause check:** For sql-17 Exercise 4, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `sample_id`, and finish with `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value` ordered by `sample_id`.
- **Alternative/trade-off:** For sql-17 Exercise 4, the chosen form is justified by this lesson-specific rationale: Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie. Evaluate another form against the concrete expected result (Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2) and the verification above.
- **Edge case:** Give two rows the same `sample_id` value and different ``sample_id`` values; verify `sample_id` produces the intended rank and display order.

## Exercise 5 — Debugging

**Prompt:** Return exactly one latest order per customer even when timestamps tie.

**Reasoning:** Use row number with the unique order ID as final tie-breaker.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH numbered AS (
  SELECT o.*,
         ROW_NUMBER() OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date DESC, o.order_id DESC
         ) AS recency_number
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date,
       total_amount
FROM numbered
WHERE recency_number = 1
ORDER BY customer_id;
```

**Expected shape:** At most one row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 5, expected output: At most one row per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
- **Independent verification:** For sql-17 Exercise 5, run an anti-check that counts rows where NOT ((recency_number = 1)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, and `total_amount` against `orders`. Give two rows the same `customer_id` value and different ``order_id`` values; verify `customer_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 5, run `numbered` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-17 Exercise 5, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, and `total_amount` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-17 Exercise 5, the chosen form is justified by this lesson-specific rationale: Use row number with the unique order ID as final tie-breaker. Evaluate another form against the concrete expected result (At most one row per customer) and the verification above.
- **Edge case:** Give two rows the same `customer_id` value and different ``order_id`` values; verify `customer_id` produces the intended rank and display order.

## Exercise 6 — Extension

**Prompt:** Rank employee salaries within department and show only the top two distinct salary levels.

**Reasoning:** Dense rank includes all employees tied at either of the top two salary values.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH ranked AS (
  SELECT e.*,
         DENSE_RANK() OVER (
           PARTITION BY e.department_id ORDER BY e.salary DESC
         ) AS salary_rank
  FROM employees AS e
)
SELECT employee_id,
       full_name,
       department_id,
       salary,
       salary_rank
FROM ranked
WHERE salary_rank <= 2
ORDER BY department_id, salary_rank, employee_id;
```

**Expected shape:** Top two salary levels per department.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-17 Exercise 6, expected output: Top two salary levels per department. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
- **Independent verification:** For sql-17 Exercise 6, run an anti-check that counts rows where NOT ((salary_rank <= 2)); require unique `employee_id` where the expected grain is one row per key and confirm the projected `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank` against `employees`. Give two rows the same `department_id` value and different `employee_id` values; verify `department_id, salary_rank, employee_id` produces the intended rank and display order.
- **Intermediate relation check:** For sql-17 Exercise 6, run `ranked` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-17 Exercise 6, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank` ordered by `department_id, salary_rank, employee_id`.
- **Alternative/trade-off:** For sql-17 Exercise 6, the chosen form is justified by this lesson-specific rationale: Dense rank includes all employees tied at either of the top two salary values. Evaluate another form against the concrete expected result (Top two salary levels per department) and the verification above.
- **Edge case:** Give two rows the same `department_id` value and different `employee_id` values; verify `department_id, salary_rank, employee_id` produces the intended rank and display order.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
