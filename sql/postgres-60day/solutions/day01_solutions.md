# Day 01 solutions — SELECT, WHERE, ORDER BY, LIMIT/OFFSET


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day01_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day01_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Projection, Predicate, Deterministic ordering. Its worked-model focus is:
Trace the first learner query in logical order: FROM training.customers produces candidate rows, WHERE country IN ('US', 'CA') filters them, ORDER BY createdat DESC, customerid DESC fixes their order, and LIMIT 10 keeps the first ten. Remove the customerid tie-breaker and explain why rows with equal timestamps no longer have a guaranteed relative order.

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

These answers align one-for-one with [day01_select_where_orderby.sql](../day01_select_where_orderby.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
- **Assumptions:** Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
- **Primary pitfall:** Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List the 20 newest orders with customer ID and total amount.

**Reasoning:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 20;
```

**Expected shape:** At most 20 rows; one row per order, newest first.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List the 20 newest orders with customer ID and total amount” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `id`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: List the 20 newest orders with customer ID and total amount. Why: Sort by orderdate DESC and add orderid DESC as a unique tie-breaker before applying LIMIT. Expected: At most 20 rows; one row per order, newest first. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
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

**Prompt:** Find the 10 most expensive products created in the last 90 days.

**Reasoning:** Filter the timestamp directly, then sort by price and a stable product key.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT p.product_id,
       p.name,
       p.price,
       p.created_at
FROM products AS p
WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
ORDER BY p.price DESC, p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 product rows; every row is in the 90-day window.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Find the 10 most expensive products created in the last 90 days” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Find the 10 most expensive products created in the last 90 days. Why: Filter the timestamp directly, then sort by price and a stable product key. Expected: At most 10 product rows; every row is in the 90-day window. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
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

**Prompt:** Show customers from GB or DE created in the last year, newest first.

**Reasoning:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       c.country,
       c.created_at
FROM customers AS c
WHERE c.country IN ('GB', 'DE')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'
ORDER BY c.created_at DESC, c.customer_id;
```

**Expected shape:** Only GB/DE customers from the declared window.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Show customers from GB or DE created in the last year, newest first” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `gb`, `de`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 3: Query writing Prompt: Show customers from GB or DE created in the last year, newest first. Why: Use IN for the country set, combine the time condition with AND, and break timestamp ties. Expected: Only GB/DE customers from the declared window. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.

**Reasoning:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_count,
       COUNT(*) FILTER (WHERE c.email IS NOT NULL) AS present_email_count,
       COUNT(*) AS customer_count
FROM customers AS c;
```

**Expected shape:** Exactly one summary row with counts whose sum equals all customers.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict which rows survive email = NULL, then write a query that counts missing and present emails correctly”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `missing_email_count`, `present_email_count`, `customer_count`, `c`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: Prediction Prompt: Predict which rows survive email = NULL, then write a query that counts missing and present emails correctly. Why: Comparisons with NULL are unknown; use IS NULL and IS NOT NULL. Expected: Exactly one summary row with counts whose sum equals all customers. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - FILTER (WHERE ...): limits one aggregate without removing rows needed by neighboring aggregates.
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

**Prompt:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.

**Reasoning:** Define the business ranking first; use a unique final key for tied prices.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT p.product_id,
       p.name,
       p.price
FROM products AS p
ORDER BY p.price DESC, p.product_id
LIMIT 10;
```

**Expected shape:** At most 10 rows, highest prices first, stable across repeated runs on unchanged data.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 needs the plan evidence for “Debugging: Repair a top-price query that uses LIMIT 10 without ORDER BY and explain why the original is nondeterministic”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `p`, `limit`.
- **Independent verification:** For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `products` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers. The executable solution's check is: Exercise 5: Debugging Prompt: Repair a top-price query that uses LIMIT 10 without ORDER BY and explain why the original is nondeterministic. Why: Define the business ranking first; use a unique final key for tied prices. Expected: At most 10 rows, highest prices first, stable across repeated runs on unchanged data. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
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

**Prompt:** Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.

**Reasoning:** Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
WITH first_page AS (
  SELECT o.order_id,
         o.order_date
  FROM orders AS o
  ORDER BY o.order_date DESC, o.order_id DESC
  LIMIT 10
), cursor_row AS (
  SELECT fp.order_date,
         fp.order_id
  FROM first_page AS fp
  ORDER BY fp.order_date, fp.order_id
  LIMIT 1
)
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
CROSS JOIN cursor_row AS cursor
WHERE (o.order_date, o.order_id) < (cursor.order_date, cursor.order_id)
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 10;
```

**Expected shape:** Up to 10 rows strictly after the first page with no overlap.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Extension: Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than OFFSET” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `o`, `fp`, `cursor`, `offset`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `o`, `fp`, `cursor`, `offset`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than OFFSET. Why: Use the last (orderdate, orderid) pair from page one and compare row values in the same descending order. Expected: Up to 10 rows strictly after the first page with no overlap. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
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
