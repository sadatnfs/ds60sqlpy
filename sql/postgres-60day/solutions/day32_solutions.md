# Day 32 — Solutions: Index Fundamentals


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day32_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day32_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Selectivity, Index scan, Index-only scan. Its worked-model focus is:
Capture a category-filter plan before creating products(category), create the index inside the rollback-only transaction, and rerun the identical query. Record the plan even if PostgreSQL keeps the sequential scan: the compact seed can make reading the table cheaper than traversing an index.

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

Indexes trade storage and write cost for faster access to selected rows. Both
answers run inside a transaction and roll back, so rerunning the document does
not leave demonstration indexes behind.

## Exercise 1 — Index `products(category)` and test a filter

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_solution;
CREATE INDEX idx_products_category_solution
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id,
       name,
       price
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Expected plan shape is not guaranteed. The seeded `products` table has only a
few hundred rows and each category is common, so a sequential scan can be
cheaper even though the index is valid.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 2 — Compare without, with, and after dropping the index

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

CREATE INDEX idx_products_category_compare
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

DROP INDEX idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Record node type, estimated rows, actual rows, planning time, execution time,
and buffers for each plan. On this small dataset, “no visible plan change” is a
valid observation, not a failed exercise.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Pitfalls

- Do not use `SET enable_seqscan = off` as proof that an index is useful; it
  changes the planner's choices instead of demonstrating normal behavior.
- A B-tree handles equality and ordered range predicates, so a hash index is
  rarely needed for a basic equality lookup.
- Index names share a schema namespace, which is why the solution uses unique,
  exercise-specific names.
- Indexes created in the learner script are rolled back at the end of that
  script and are not available on later days.

## Exercise 3 — Predict from selectivity

Count each category before reading the plan. The optimizer may prefer a
sequential scan on this compact seed even when the index is valid and usable.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
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

## Exercise 4 — Index a timestamp range

The solution indexes `payment_date` and uses `[start, end)` bounds. Half-open
windows compose cleanly without double-counting a boundary timestamp.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Match an expression index

An index on `country` does not store `lower(country)`. The solution indexes that
exact expression and repeats it exactly in the predicate.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Preserve the ordering contract

The unordered query is intentionally nondeterministic. Only the query with
`ORDER BY country, customer_id` promises reproducible presentation order; an
index's incidental scan order is not a substitute.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
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
