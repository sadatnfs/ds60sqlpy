# Day 10 solutions: DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day10_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are DML, Upsert, Idempotent. Its worked-model focus is:
Run the candidate-selection `SELECT` before the matching `UPDATE`. Compare its keys with `UPDATE ... RETURNING`, verify the affected count, and leave the course transaction at `ROLLBACK`. This preview/modify/reconcile pattern is safer than starting with an unbounded write.

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

These answers align one-for-one with [day10_dml_with_subqueries.sql](../day10_dml_with_subqueries.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
- **Assumptions:** Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
- **Primary pitfall:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Materialize category net revenue into a temporary table with `INSERT ... SELECT`.

**Reasoning:** Declare the temporary schema and aggregate source rows before inserting.

**Clause-by-clause reading:**

- `CREATE TEMP`: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable.
- `INSERT INTO`: adds rows to the named target; an explicit column list prevents accidental position-based mistakes.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_1;

CREATE TEMP TABLE exercise_category_revenue (
  category text PRIMARY KEY,
  revenue numeric NOT NULL
) ON COMMIT DROP;

INSERT INTO exercise_category_revenue (category, revenue)
SELECT
  p.category,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount))
FROM
  order_items AS oi
  JOIN products AS p ON p.product_id = oi.product_id
GROUP BY
  p.category;

SELECT
  category,
  ROUND(revenue, 2) AS revenue
FROM
  exercise_category_revenue
ORDER BY
  revenue DESC,
  category;

ROLLBACK TO SAVEPOINT exercise_1;
```

**Expected shape:** One temporary row per product category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 1, aggregate net revenue, `unit_price * quantity * (1 - discount)`, from `order_items` joined to `products` by `p.category`, and load it with `INSERT ... SELECT` into the temporary table `exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL)`.
- **Expected result/shape:** For sql-10 Exercise 1, expected output: the command tag `INSERT 0 6`, then six rows, one per product category, with columns `category` and `revenue` (rounded to 2 places), ordered by `revenue DESC, category`; `Sports` leads on the course seed.
- **Independent verification:** For sql-10 Exercise 1, rerun the aggregate as a plain `SELECT` and compare each category's revenue with the stored row; confirm that `SELECT COUNT(DISTINCT p.category) FROM order_items oi JOIN products p ON p.product_id = oi.product_id` returns 6, and that the savepoint rollback leaves no `exercise_category_revenue` table.
- **Intermediate relation check:** For sql-10 Exercise 1, run the `SELECT ... GROUP BY p.category` alone and confirm six rows before inserting them.
- **Clause check:** For sql-10 Exercise 1, the solution uses `SAVEPOINT`, `CREATE TEMP TABLE ... ON COMMIT DROP`, `INSERT ... SELECT ... JOIN ... GROUP BY p.category`, a check `SELECT ... ORDER BY revenue DESC, category`, and `ROLLBACK TO SAVEPOINT`.
- **Alternative/trade-off:** For sql-10 Exercise 1, `CREATE TEMP TABLE ... AS SELECT` creates and fills the table in one statement, but it cannot declare the primary key that rejects a duplicate category.
- **Edge case:** Running the same `INSERT ... SELECT` twice fails on the second run with SQLSTATE `23505`, because `category` is the primary key; that is the intended protection against double loading.

## Exercise 2: Query writing

**Prompt:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.

**Reasoning:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.

**Clause-by-clause reading:**

- `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_2;

UPDATE
  employees AS e
SET
  salary = ROUND(e.salary * 1.05, 2)
WHERE
  e.department_id IN (
    SELECT
      d.department_id
    FROM
      departments AS d
    WHERE
      d.name IN ('Sales', 'Engineering'))
RETURNING
  e.employee_id,
  e.full_name,
  e.salary;

ROLLBACK TO SAVEPOINT exercise_2;
```

**Expected shape:** Affected employee rows only; no change persists.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 2, raise `salary` by 5% (rounded to 2 places) for employees whose `department_id` belongs to the `departments` named `Sales` or `Engineering`, selected with an `IN (SELECT ...)` subquery, inside a savepoint.
- **Expected result/shape:** For sql-10 Exercise 2, expected output: the command tag `UPDATE 34` and 34 returned rows with columns `employee_id`, `full_name`, and `salary` (the new value); after `ROLLBACK TO SAVEPOINT`, no salary has changed.
- **Independent verification:** For sql-10 Exercise 2, before the update, count the targets with `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` (34) and compare with the command tag; after the rollback, compare one returned `employee_id`'s salary with its original value.
- **Intermediate relation check:** For sql-10 Exercise 2, the department subquery returns two `department_id` values; the `UPDATE` must touch only employees in those two departments.
- **Clause check:** For sql-10 Exercise 2, the solution uses `UPDATE employees AS e SET salary = ROUND(e.salary * 1.05, 2) WHERE e.department_id IN (SELECT ...) RETURNING e.employee_id, e.full_name, e.salary`.
- **Alternative/trade-off:** For sql-10 Exercise 2, `UPDATE ... FROM departments d WHERE d.department_id = e.department_id AND d.name IN (...)` is equivalent here because each employee matches at most one department row.
- **Edge case:** A misspelled department name, such as `'Engineers'`, matches nothing and produces `UPDATE 17` for Sales only; compare the command tag with the preview count to catch it.

## Exercise 3: Query writing

**Prompt:** Delete orders older than one year only when no payment exists, returning candidate keys.

**Reasoning:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.

**Clause-by-clause reading:**

- `DELETE FROM`: removes only the predicate-matched rows; the lesson's transaction wrapper makes the example reversible.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_3;

DELETE FROM orders AS o
WHERE o.order_date < CURRENT_TIMESTAMP - INTERVAL '1 year'
  AND NOT EXISTS (
    SELECT
      1
    FROM
      payments AS p
    WHERE
      p.order_id = o.order_id)
RETURNING
  o.order_id,
  o.customer_id,
  o.order_date;

ROLLBACK TO SAVEPOINT exercise_3;
```

**Expected shape:** Deleted-candidate order rows, then fully restored state.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 3, delete orders with `order_date` older than one year that have no row in `payments`, using a correlated `NOT EXISTS`, inside a savepoint.
- **Expected result/shape:** For sql-10 Exercise 3, expected output: a `DELETE` command tag and returned rows with columns `order_id`, `customer_id`, and `order_date`, all older than one year (362 rows on a freshly seeded database); after `ROLLBACK TO SAVEPOINT`, every order and its cascaded `order_items` are restored.
- **Independent verification:** For sql-10 Exercise 3, count the candidates first with the same `WHERE` clause in a `SELECT COUNT(*)` and compare with the command tag; after the rollback, confirm that `SELECT COUNT(*) FROM orders` is back to 4,362 and that a deleted `order_id` exists again.
- **Intermediate relation check:** For sql-10 Exercise 3, `SELECT COUNT(*) FROM order_items WHERE order_id IN (...candidates...)` shows how many line items the `ON DELETE CASCADE` foreign key would remove with the orders.
- **Clause check:** For sql-10 Exercise 3, the solution uses `DELETE FROM orders AS o WHERE o.order_date < CURRENT_TIMESTAMP - INTERVAL '1 year' AND NOT EXISTS (SELECT 1 FROM payments AS p WHERE p.order_id = o.order_id) RETURNING ...`.
- **Alternative/trade-off:** For sql-10 Exercise 3, `NOT IN (SELECT order_id FROM payments)` gives the same result only while `payments.order_id` can never be NULL; `NOT EXISTS` stays correct either way.
- **Edge case:** Because the cutoff uses `CURRENT_TIMESTAMP`, the candidate count grows as the seed ages; compare the preview and the command tag in the same transaction.

## Exercise 4: Prediction

**Prompt:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.

**Reasoning:** A primary key supplies the conflict target; the second statement updates rather than inserts.

**Clause-by-clause reading:**

- `CREATE TEMP`: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable.
- `INSERT INTO`: adds rows to the named target; an explicit column list prevents accidental position-based mistakes.
- `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_4;

CREATE TEMP TABLE exercise_feed (
  source_key text PRIMARY KEY,
  source_value numeric NOT NULL
) ON COMMIT DROP;

INSERT INTO exercise_feed (source_key, source_value)
  VALUES ('source_a', 10)
ON CONFLICT (source_key)
  DO UPDATE SET
    source_value = EXCLUDED.source_value;

INSERT INTO exercise_feed (source_key, source_value)
  VALUES ('source_a', 12)
ON CONFLICT (source_key)
  DO UPDATE SET
    source_value = EXCLUDED.source_value;

SELECT
  source_key,
  source_value
FROM
  exercise_feed
ORDER BY
  source_key;

ROLLBACK TO SAVEPOINT exercise_4;
```

**Expected shape:** One row for `source_a` with the second value.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 4, create the temporary table `exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)` and run `INSERT ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value` twice for `source_a`, first with `10` and then with `12`.
- **Expected result/shape:** For sql-10 Exercise 4, expected output: both statements print `INSERT 0 1`, and the final `SELECT` returns one row ordered by `source_key` with columns `source_key` and `source_value`: `('source_a', 12)`.
- **Independent verification:** For sql-10 Exercise 4, confirm that `SELECT COUNT(*) FROM exercise_feed WHERE source_key = 'source_a'` returns 1 after the second run; add `RETURNING (xmax = 0) AS inserted` to each upsert to see `true` for the first run and `false` for the second.
- **Intermediate relation check:** For sql-10 Exercise 4, select the table after the first upsert: it holds `('source_a', 10)`, so the second statement must update that row rather than add one.
- **Clause check:** For sql-10 Exercise 4, the solution uses `CREATE TEMP TABLE ... PRIMARY KEY`, two `INSERT ... VALUES ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value`, and `SELECT ... ORDER BY source_key`.
- **Alternative/trade-off:** For sql-10 Exercise 4, `ON CONFLICT DO NOTHING` would keep `10` and silently ignore the new value; `MERGE` can express the same upsert but does not use `ON CONFLICT`'s concurrency guarantee.
- **Edge case:** Without a unique index on `source_key`, `ON CONFLICT (source_key)` fails with SQLSTATE `42P10` (no unique or exclusion constraint matching the specification).

## Exercise 5: Debugging

**Prompt:** Preview and update a bounded product set while reconciling selected and returned key counts.

**Reasoning:** Store candidate keys in a temporary table and update only through that reviewed set.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `CREATE TEMP`: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable.
- `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
- `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_5;

CREATE TEMP TABLE exercise_product_candidates ON COMMIT DROP AS
SELECT
  p.product_id
FROM
  products AS p
WHERE
  p.category = 'Books'
ORDER BY
  p.product_id
LIMIT 5;

WITH updated AS (
  UPDATE
    products AS p
  SET
    price = ROUND(p.price * 0.99, 2)
  WHERE
    p.product_id IN (
      SELECT
        candidate.product_id
      FROM
        exercise_product_candidates AS candidate)
    RETURNING
      p.product_id
)
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      exercise_product_candidates) AS candidate_count,
  COUNT(*) AS updated_count
FROM
  updated;

ROLLBACK TO SAVEPOINT exercise_5;
```

**Expected shape:** One summary row with equal candidate and updated counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 5, store the first five `Books` product keys in the temporary table `exercise_product_candidates`, then lower those products' `price` by 1% through a data-modifying CTE that updates only keys in that table.
- **Expected result/shape:** For sql-10 Exercise 5, expected output: one summary row with columns `candidate_count` and `updated_count`, both `5`.
- **Independent verification:** For sql-10 Exercise 5, list the candidate `product_id` values before the update and compare them with the keys returned by the `UPDATE`'s `RETURNING` clause; after `ROLLBACK TO SAVEPOINT`, confirm that each candidate's `price` equals its original value.
- **Intermediate relation check:** For sql-10 Exercise 5, `SELECT product_id FROM exercise_product_candidates ORDER BY product_id` returns the five reviewed keys before any price changes.
- **Clause check:** For sql-10 Exercise 5, the solution uses `CREATE TEMP TABLE ... AS SELECT ... ORDER BY p.product_id LIMIT 5`, then `WITH updated AS (UPDATE ... WHERE p.product_id IN (SELECT ...) RETURNING p.product_id)` and an outer `SELECT` of the two counts.
- **Alternative/trade-off:** For sql-10 Exercise 5, updating with `WHERE p.category = 'Books'` directly would change all 50 books; the candidate table bounds the write to the five reviewed keys.
- **Edge case:** If a candidate key were deleted before the update, `updated_count` would be lower than `candidate_count`, which is exactly the mismatch this reconciliation is designed to expose.

## Exercise 6: Extension

**Prompt:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.

**Reasoning:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.

**Clause-by-clause reading:**

- `CREATE TEMP`: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable.
- `INSERT INTO`: adds rows to the named target; an explicit column list prevents accidental position-based mistakes.
- `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
- `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
- savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.

```sql
SAVEPOINT exercise_6;

CREATE TEMP TABLE exercise_price_stage (
  product_id integer PRIMARY KEY,
  new_price numeric
) ON COMMIT DROP;

INSERT INTO exercise_price_stage (product_id, new_price)
SELECT
  p.product_id,
  ROUND(p.price * 1.01, 2)
FROM
  products AS p
ORDER BY
  p.product_id
LIMIT 3;

UPDATE
  products AS p
SET
  price = stage.new_price
FROM
  exercise_price_stage AS stage
WHERE
  stage.product_id = p.product_id
  AND stage.new_price >= 0
  AND p.price IS DISTINCT FROM stage.new_price
RETURNING
  p.product_id,
  p.price;

ROLLBACK TO SAVEPOINT exercise_6;
```

**Expected shape:** Returned rows only for valid changed products.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 6, stage new prices for the first three products in the temporary table `exercise_price_stage`, then run `UPDATE products ... FROM exercise_price_stage` only where `stage.new_price >= 0` and `p.price IS DISTINCT FROM stage.new_price`.
- **Expected result/shape:** For sql-10 Exercise 6, expected output: the command tag `UPDATE 3` and three returned rows ordered by `p.product_id` with columns `product_id` and `price`: `(1, 10.47)`, `(2, 10.85)`, and `(3, 11.22)` on the course seed.
- **Independent verification:** For sql-10 Exercise 6, add a staged row with a negative price and one whose price equals the current price, rerun the update after a savepoint, and confirm that neither key is returned; then confirm the original prices after `ROLLBACK TO SAVEPOINT`.
- **Intermediate relation check:** For sql-10 Exercise 6, `SELECT stage.product_id, p.price, stage.new_price FROM exercise_price_stage stage JOIN products p USING (product_id)` shows the three before/after pairs that the update should apply.
- **Clause check:** For sql-10 Exercise 6, the solution uses `CREATE TEMP TABLE`, `INSERT ... SELECT ... LIMIT 3`, and `UPDATE products AS p SET price = stage.new_price FROM exercise_price_stage AS stage WHERE ... RETURNING p.product_id, p.price`.
- **Alternative/trade-off:** For sql-10 Exercise 6, `p.price <> stage.new_price` behaves the same only when neither side is NULL; `IS DISTINCT FROM` also treats a change to or from NULL as a difference.
- **Edge case:** A staged `new_price` of NULL fails `stage.new_price >= 0` (unknown is not true), so it is skipped instead of reaching the `NOT NULL` price column.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
