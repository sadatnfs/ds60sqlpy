# Day 10 solutions — DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day10_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day10_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are DML, Upsert, Idempotent. Its worked-model focus is:
Run the candidate-selection SELECT before the matching UPDATE. Compare its keys with UPDATE ... RETURNING, verify the affected count, and leave the course transaction at ROLLBACK. This preview/modify/reconcile pattern is safer than starting with an unbounded write.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 1 must make “Query writing: Materialize category net revenue into a temporary table with INSERT ... SELECT” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `oi`, `p`, `revenue`, `insert`.
- **Independent verification:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `oi`, `p`, `revenue`, `insert`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 1: Query writing Prompt: Materialize category net revenue into a temporary table with INSERT ... SELECT. Why: Declare the temporary schema and aggregate source rows before inserting. Expected: One temporary row per product category. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - CREATE TEMP: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable. - INSERT INTO: adds rows to the named target; an explicit column list prevents accidental position-based mistakes. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Give Sales and Engineering employees a 5% demonstration raise and return affected rows” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `e`, `d`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, `departments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Give Sales and Engineering employees a 5% demonstration raise and return affected rows. Why: Select departments by key, round exact numeric salary, and inspect RETURNING. Expected: Affected employee rows only; no change persists. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - UPDATE: changes only the target rows selected by its predicate; preview that population before executing. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - RETURNING: shows the rows changed by DML, providing immediate evidence of the affected population. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Delete orders older than one year only when no payment exists, returning candidate keys” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `o`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `payments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 3: Query writing Prompt: Delete orders older than one year only when no payment exists, returning candidate keys. Why: Use correlated NOT EXISTS; foreign-key cascades remain rollback-protected. Expected: Deleted-candidate order rows, then fully restored state. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - DELETE FROM: removes only the predicate-matched rows; the lesson's transaction wrapper makes the example reversible. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - RETURNING: shows the rows changed by DML, providing immediate evidence of the affected population. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 4 must make “Prediction: Run an upsert twice against a temporary key-value table and prove only one row exists for the key” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`.
- **Independent verification:** For Exercise 4, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 4: Prediction Prompt: Run an upsert twice against a temporary key-value table and prove only one row exists for the key. Why: A primary key supplies the conflict target; the second statement updates rather than inserts. Expected: One row for sourcea with the second value. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - CREATE TEMP: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable. - INSERT INTO: adds rows to the named target; an explicit column list prevents accidental position-based mistakes. - UPDATE: changes only the target rows selected by its predicate; preview that population before executing. - VALUES: constructs a small relation explicitly, which makes examples and expected cardinality inspectable. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 5 must make “Debugging: Preview and update a bounded product set while reconciling selected and returned key counts” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `p`, `candidate`, `candidate_count`, `updated_count`.
- **Independent verification:** For Exercise 5, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `p`, `candidate`, `candidate_count`, `updated_count`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 5: Debugging Prompt: Preview and update a bounded product set while reconciling selected and returned key counts. Why: Store candidate keys in a temporary table and update only through that reviewed set. Expected: One summary row with equal candidate and updated counts. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - CREATE TEMP: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable. - UPDATE: changes only the target rows selected by its predicate; preview that population before executing. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first. - RETURNING: shows the rows changed by DML, providing immediate evidence of the affected population. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Extension: Stage product prices and update only rows whose incoming price is nonnegative and actually differs” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `p`, `stage`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `p`, `stage`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Stage product prices and update only rows whose incoming price is nonnegative and actually differs. Why: Use UPDATE ... FROM, validate the stage predicate, and compare with IS DISTINCT FROM. Expected: Returned rows only for valid changed products. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - CREATE TEMP: creates session-local teaching state; the outer transaction and final rollback keep the lesson disposable. - INSERT INTO: adds rows to the named target; an explicit column list prevents accidental position-based mistakes. - UPDATE: changes only the target rows selected by its predicate; preview that population before executing. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first. - RETURNING: shows the rows changed by DML, providing immediate evidence of the affected population. - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
