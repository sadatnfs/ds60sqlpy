# Day 10 solutions — DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT

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

## Exercise 1 — Query writing

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
SELECT p.category,
       SUM(oi.unit_price * oi.quantity * (1 - oi.discount))
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
GROUP BY p.category;
SELECT category, ROUND(revenue, 2) AS revenue
FROM exercise_category_revenue
ORDER BY revenue DESC, category;
ROLLBACK TO SAVEPOINT exercise_1;
```

**Expected shape:** One temporary row per product category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

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
UPDATE employees AS e
SET salary = ROUND(e.salary * 1.05, 2)
WHERE e.department_id IN (
  SELECT d.department_id
  FROM departments AS d
  WHERE d.name IN ('Sales', 'Engineering')
)
RETURNING e.employee_id, e.full_name, e.salary;
ROLLBACK TO SAVEPOINT exercise_2;
```

**Expected shape:** Affected employee rows only; no change persists.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

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
    SELECT 1
    FROM payments AS p
    WHERE p.order_id = o.order_id
  )
RETURNING o.order_id, o.customer_id, o.order_date;
ROLLBACK TO SAVEPOINT exercise_3;
```

**Expected shape:** Deleted-candidate order rows, then fully restored state.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

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
DO UPDATE SET source_value = EXCLUDED.source_value;
INSERT INTO exercise_feed (source_key, source_value)
VALUES ('source_a', 12)
ON CONFLICT (source_key)
DO UPDATE SET source_value = EXCLUDED.source_value;
SELECT source_key, source_value
FROM exercise_feed
ORDER BY source_key;
ROLLBACK TO SAVEPOINT exercise_4;
```

**Expected shape:** One row for `source_a` with the second value.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

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
SELECT p.product_id
FROM products AS p
WHERE p.category = 'Books'
ORDER BY p.product_id
LIMIT 5;
WITH updated AS (
  UPDATE products AS p
  SET price = ROUND(p.price * 0.99, 2)
  WHERE p.product_id IN (
    SELECT candidate.product_id
    FROM exercise_product_candidates AS candidate
  )
  RETURNING p.product_id
)
SELECT (SELECT COUNT(*) FROM exercise_product_candidates) AS candidate_count,
       COUNT(*) AS updated_count
FROM updated;
ROLLBACK TO SAVEPOINT exercise_5;
```

**Expected shape:** One summary row with equal candidate and updated counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

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
SELECT p.product_id,
       ROUND(p.price * 1.01, 2)
FROM products AS p
ORDER BY p.product_id
LIMIT 3;
UPDATE products AS p
SET price = stage.new_price
FROM exercise_price_stage AS stage
WHERE stage.product_id = p.product_id
  AND stage.new_price >= 0
  AND p.price IS DISTINCT FROM stage.new_price
RETURNING p.product_id, p.price;
ROLLBACK TO SAVEPOINT exercise_6;
```

**Expected shape:** Returned rows only for valid changed products.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
