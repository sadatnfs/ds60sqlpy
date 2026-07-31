# Day 04 solutions — OUTER JOINs: Preserving Unmatched Rows


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day04_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day04_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Preserved side, NULL-extended row, Anti-join. Its worked-model focus is:
Start from products and left-join orderitems. A product with no line item still appears, with oi.productid IS NULL. Moving a right-side filter from ON into WHERE removes that row; run both shapes and explain the change.

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

These answers align one-for-one with [day04_outer_joins.sql](../day04_outer_joins.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
- **Assumptions:** Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
- **Primary pitfall:** A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List every customer with order count, including customers with zero orders.

**Reasoning:** Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY order_count DESC, c.customer_id;
```

**Expected shape:** One row per customer; zero is visible.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List every customer with order count, including customers with zero orders” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `order_count`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: List every customer with order count, including customers with zero orders. Why: Start from customers, left join orders, and count the nullable order key rather than COUNT(). Expected: One row per customer; zero is visible. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Find products that have never appeared in an order item.

**Reasoning:** Left join and retain rows where the right-side primary key is NULL.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.name,
       p.category
FROM products AS p
LEFT JOIN order_items AS oi
  ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL
ORDER BY p.product_id;
```

**Expected shape:** One row per unsold product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Find products that have never appeared in an order item” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Find products that have never appeared in an order item. Why: Left join and retain rows where the right-side primary key is NULL. Expected: One row per unsold product. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Compare monthly budgets and expenses by category with a full outer join.

**Reasoning:** Aggregate each side to the same category/month grain before joining; preserve keys from either side.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH expense_months AS (
  SELECT e.category,
         date_trunc('month', e.expense_date)::date AS period,
         SUM(e.amount) AS actual_amount
  FROM expenses AS e
  GROUP BY e.category, date_trunc('month', e.expense_date)
), budget_months AS (
  SELECT b.category,
         b.period,
         SUM(b.amount) AS budget_amount
  FROM budgets AS b
  GROUP BY b.category, b.period
)
SELECT COALESCE(bm.category, em.category) AS category,
       COALESCE(bm.period, em.period) AS period,
       ROUND(bm.budget_amount, 2) AS budget_amount,
       ROUND(em.actual_amount, 2) AS actual_amount
FROM budget_months AS bm
FULL JOIN expense_months AS em
  ON em.category = bm.category
 AND em.period = bm.period
ORDER BY period, category;
```

**Expected shape:** One row per category/month present in either source.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 3 requires a written prediction and the observed result for “Query writing: Compare monthly budgets and expenses by category with a full outer join”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `actual_amount`, `e`, `budget_amount`, `b`, `category`, `bm`, `em`.
- **Independent verification:** For Exercise 3, run the two forms over the identical rows in `expenses`, `budgets`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 3: Query writing Prompt: Compare monthly budgets and expenses by category with a full outer join. Why: Aggregate each side to the same category/month grain before joining; preserve keys from either side. Expected: One row per category/month present in either source. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - COALESCE: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.

**Reasoning:** Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       COUNT(o.order_id) AS delivered_orders
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
 AND o.status = 'delivered'
GROUP BY c.customer_id, c.full_name
ORDER BY delivered_orders DESC, c.customer_id;
```

**Expected shape:** One row per customer, including zero delivered orders.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Preserve every customer while counting only delivered orders; compare a status predicate in ON with the same predicate in WHERE”. Show both compared result shapes at one row per customer or the customer grouping key named by the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `delivered_orders`, `c`, `o`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `customers`, `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: Prediction Prompt: Preserve every customer while counting only delivered orders; compare a status predicate in ON with the same predicate in WHERE. Why: Place o.status = 'delivered' in ON; WHERE would remove NULL-extended customers. Expected: One row per customer, including zero delivered orders. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.

**Reasoning:** Count a non-nullable right-side key that becomes NULL for an unmatched row.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer with correct zero counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Repair COUNT() in a left-join order count so customers without orders report zero rather than one” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `order_count`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 5, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 5: Debugging Prompt: Repair COUNT() in a left-join order count so customers without orders report zero rather than one. Why: Count a non-nullable right-side key that becomes NULL for an unmatched row. Expected: One row per customer with correct zero counts. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.

**Reasoning:** Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(DISTINCT p.product_id) FILTER (
         WHERE p.product_id IS NOT NULL AND oi.product_id IS NOT NULL
       ) AS matched_products,
       COUNT(DISTINCT p.product_id) FILTER (
         WHERE p.product_id IS NOT NULL AND oi.product_id IS NULL
       ) AS unsold_products,
       COUNT(DISTINCT oi.product_id) FILTER (
         WHERE p.product_id IS NULL AND oi.product_id IS NOT NULL
       ) AS orphan_item_product_ids
FROM products AS p
FULL JOIN order_items AS oi
  ON oi.product_id = p.product_id;
```

**Expected shape:** One summary row with three mutually interpretable counts.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Extension: Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `matched`, `evidence`, `matched_products`, `unsold_products`, `orphan_item_product_ids`, `p`, `oi`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `matched`, `evidence`, `matched_products`, `unsold_products`, `orphan_item_product_ids`, `p`, `oi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys. Why: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero. Expected: One summary row with three mutually interpretable counts. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - FILTER (WHERE ...): limits one aggregate without removing rows needed by neighboring aggregates.
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
