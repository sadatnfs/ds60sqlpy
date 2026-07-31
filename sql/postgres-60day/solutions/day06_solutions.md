# Day 06 solutions — Set Operations: UNION, INTERSECT, EXCEPT


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day06_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day06_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Set operation, Union compatibility, Duplicate semantics. Its worked-model focus is:
Project only orderid from orders and payments before applying EXCEPT. Because set operations compare every projected column, adding an unrelated amount or timestamp would change the meaning from “missing order IDs” to “missing complete tuples.”

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

These answers align one-for-one with [day06_set_operations.sql](../day06_set_operations.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Primary pitfall:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Return customer IDs that have either an order or a support event.

**Reasoning:** `UNION` expresses set membership and removes duplicates across both sources.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.customer_id
FROM orders AS o
UNION
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;
```

**Expected shape:** One distinct customer ID per qualifying customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 1, read from `orders`, and `events`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 1, expected output: One distinct customer ID per qualifying customer. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 1, run an anti-check that counts rows where NOT ((e.event_type = 'support')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `orders`, and `events`. Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-06 Exercise 1, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
- **Clause check:** For sql-06 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `events`, preserve one row per `customer_id`, and finish with `customer_id` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-06 Exercise 1, the chosen form is justified by this lesson-specific rationale: `UNION` expresses set membership and removes duplicates across both sources. Evaluate another form against the concrete expected result (One distinct customer ID per qualifying customer) and the verification above.
- **Edge case:** Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Exercise 2 — Query writing

**Prompt:** Return customer IDs that have both an order and a support event.

**Reasoning:** `INTERSECT` keeps keys present in both compatible sets.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.customer_id
FROM orders AS o
INTERSECT
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;
```

**Expected shape:** One distinct customer ID in both sets.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 2, read from `orders`, and `events`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 2, expected output: One distinct customer ID in both sets. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 2, run an anti-check that counts rows where NOT ((e.event_type = 'support')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `orders`, and `events`. Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-06 Exercise 2, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
- **Clause check:** For sql-06 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `events`, preserve one row per `customer_id`, and finish with `customer_id` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-06 Exercise 2, the chosen form is justified by this lesson-specific rationale: `INTERSECT` keeps keys present in both compatible sets. Evaluate another form against the concrete expected result (One distinct customer ID in both sets) and the verification above.
- **Edge case:** Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Exercise 3 — Query writing

**Prompt:** Return customers who have no orders.

**Reasoning:** `EXCEPT` subtracts the order-customer set from all customers.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id
FROM customers AS c
EXCEPT
SELECT o.customer_id
FROM orders AS o
ORDER BY customer_id;
```

**Expected shape:** One row per customer absent from orders.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 3, expected output: One row per customer absent from orders. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `customers`, and `orders`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-06 Exercise 3, check `customer_id` before applying the row cap.
- **Clause check:** For sql-06 Exercise 3, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-06 Exercise 3, the chosen form is justified by this lesson-specific rationale: `EXCEPT` subtracts the order-customer set from all customers. Evaluate another form against the concrete expected result (One row per customer absent from orders) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 4 — Prediction

**Prompt:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.

**Reasoning:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH combined_all AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION ALL
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
), combined_distinct AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
)
SELECT 'UNION ALL' AS operation,
       COUNT(*) AS row_count
FROM combined_all
UNION ALL
SELECT 'UNION' AS operation,
       COUNT(*) AS row_count
FROM combined_distinct
ORDER BY operation;
```

**Expected shape:** Two labeled summary rows showing all-count >= distinct-count.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 4, read from `orders`. Build the answer toward `operation`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 4, expected output: Two labeled summary rows showing all-count >= distinct-count. The final columns are `operation`, and `row_count`. The final order is `operation`.
- **Independent verification:** For sql-06 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `operation`, and `row_count` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-06 Exercise 4, run `combined_all`, and `combined_distinct` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-06 Exercise 4, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `operation`, and `row_count` ordered by `operation`.
- **Alternative/trade-off:** For sql-06 Exercise 4, the chosen form is justified by this lesson-specific rationale: `UNION ALL` preserves every input row; `UNION` returns distinct rows. Evaluate another form against the concrete expected result (Two labeled summary rows showing all-count >= distinct-count) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 5 — Debugging

**Prompt:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.

**Reasoning:** Each branch below returns one text label and one numeric amount at the same report grain.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT 'order_revenue'::text AS measure,
       SUM(o.total_amount)::numeric AS amount
FROM orders AS o
UNION ALL
SELECT 'expense'::text AS measure,
       SUM(e.amount)::numeric AS amount
FROM expenses AS e
ORDER BY measure;
```

**Expected shape:** Rows identify revenue and expense measures with compatible types.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 5, read from `orders`, and `expenses`. Build the answer toward `measure`, and `amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 5, expected output: Rows identify revenue and expense measures with compatible types. The final columns are `measure`, and `amount`. The final order is `measure`.
- **Independent verification:** For sql-06 Exercise 5, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `measure`, and `amount` against `orders`, and `expenses`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-06 Exercise 5, check `measure` before applying the row cap.
- **Clause check:** For sql-06 Exercise 5, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `expenses`, preserve one row per `order_id`, and finish with `measure`, and `amount` ordered by `measure`.
- **Alternative/trade-off:** For sql-06 Exercise 5, the chosen form is justified by this lesson-specific rationale: Each branch below returns one text label and one numeric amount at the same report grain. Evaluate another form against the concrete expected result (Rows identify revenue and expense measures with compatible types) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 6 — Extension

**Prompt:** Return the symmetric difference between customers with orders and customers with support events.

**Reasoning:** Subtract each set from the other, then union the two differences.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH ordering_customers AS (
  SELECT DISTINCT o.customer_id
  FROM orders AS o
), support_customers AS (
  SELECT DISTINCT e.customer_id
  FROM events AS e
  WHERE e.event_type = 'support'
), only_orders AS (
  SELECT customer_id FROM ordering_customers
  EXCEPT
  SELECT customer_id FROM support_customers
), only_support AS (
  SELECT customer_id FROM support_customers
  EXCEPT
  SELECT customer_id FROM ordering_customers
)
SELECT customer_id, 'orders_only' AS source
FROM only_orders
UNION ALL
SELECT customer_id, 'support_only' AS source
FROM only_support
ORDER BY customer_id, source;
```

**Expected shape:** Customers present in exactly one of the two source sets.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 6, read from `orders`, and `events`. Build the answer toward `customer_id`, and `source`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-06 Exercise 6, expected output: Customers present in exactly one of the two source sets. The final columns are `customer_id`, and `source`. The final order is `customer_id, source`.
- **Independent verification:** For sql-06 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `source` against `orders`, and `events`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-06 Exercise 6, run `ordering_customers`, `support_customers`, `only_orders`, and `only_support` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-06 Exercise 6, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `events`, preserve one row per `customer_id`, and finish with `customer_id`, and `source` ordered by `customer_id, source`.
- **Alternative/trade-off:** For sql-06 Exercise 6, the chosen form is justified by this lesson-specific rationale: Subtract each set from the other, then union the two differences. Evaluate another form against the concrete expected result (Customers present in exactly one of the two source sets) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
