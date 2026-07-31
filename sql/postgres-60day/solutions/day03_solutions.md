# Day 03 solutions — INNER JOINs: Relational Linking and Predicate Placement


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day03_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day03_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Join key, Cardinality, Fanout. Its worked-model focus is:
Follow one orders row through the orderitems join. It becomes one row per line item, so summing orders.totalamount at that point repeats the order total. The learner query instead calculates value from each line and aggregates at the requested customer or category grain.

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

These answers align one-for-one with [day03_inner_joins.sql](../day03_inner_joins.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
- **Assumptions:** Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
- **Primary pitfall:** A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List orders with customer names and countries.

**Reasoning:** Join the order foreign key to the customer primary key and qualify every selected column.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.order_date,
       o.total_amount,
       c.customer_id,
       c.full_name,
       c.country
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC, o.order_id DESC;
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List orders with customer names and countries” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: List orders with customer names and countries. Why: Join the order foreign key to the customer primary key and qualify every selected column. Expected: One row per order. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Calculate each order item's net line revenue with the product name and category.

**Reasoning:** Remain at one row per order item; do not aggregate until the desired grain changes.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT oi.order_item_id,
       oi.order_id,
       p.product_id,
       p.name,
       p.category,
       oi.quantity,
       ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2) AS line_revenue
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
ORDER BY oi.order_id, oi.order_item_id;
```

**Expected shape:** One row per order item.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Calculate each order item's net line revenue with the product name and category” at one row at one row per order item grain. Named evidence columns/objects: `evidence`, `line_revenue`, `oi`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row at one row per order item grain; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Calculate each order item's net line revenue with the product name and category. Why: Remain at one row per order item; do not aggregate until the desired grain changes. Expected: One row per order item. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** List payments with order status and customer name.

**Reasoning:** Follow payments → orders → customers using each declared foreign key.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.payment_id,
       p.payment_date,
       p.amount,
       p.method,
       o.order_id,
       o.status,
       c.full_name
FROM payments AS p
JOIN orders AS o
  ON o.order_id = p.order_id
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY p.payment_date DESC, p.payment_id DESC;
```

**Expected shape:** One row per payment.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: List payments with order status and customer name” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `p`, `o`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `payments`, `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 3: Query writing Prompt: List payments with order status and customer name. Why: Follow payments → orders → customers using each declared foreign key. Expected: One row per payment. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.

**Reasoning:** Aggregate items and payments separately to one row per order before joining those aggregates.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH item_totals AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS item_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), payment_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(it.item_total, 2) AS item_total,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total
FROM orders AS o
JOIN item_totals AS it
  ON it.order_id = o.order_id
LEFT JOIN payment_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY o.order_id;
```

**Expected shape:** One row per order; no six-row multiplication.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation”. Show both compared result shapes at one row per order before joining those aggregates, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `item_total`, `oi`, `paid_total`, `p`, `o`, `it`, `pt`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `order_items`, `payments`, `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: Prediction Prompt: Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation. Why: Aggregate items and payments separately to one row per order before joining those aggregates. Expected: One row per order; no six-row multiplication. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - COALESCE: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Repair a customer/order join whose `ON` clause compares unrelated IDs.

**Reasoning:** Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.

```sql
SELECT COUNT(*) AS joined_rows,
       COUNT(DISTINCT o.order_id) AS distinct_orders
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id;
```

**Expected shape:** Exactly one customer match per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 requires a written prediction and the observed result for “Debugging: Repair a customer/order join whose ON clause compares unrelated IDs”. Show both compared result shapes at one row per customer or the customer grouping key named by the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `joined_rows`, `distinct_orders`, `o`, `c`.
- **Independent verification:** For Exercise 5, run the two forms over the identical rows in `orders`, `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 5: Debugging Prompt: Repair a customer/order join whose ON clause compares unrelated IDs. Why: Join orders.customerid to customers.customerid; verify output cannot exceed the order count for an inner many-to-one join. Expected: Exactly one customer match per order. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree.
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

**Prompt:** Calculate net line revenue by customer country without double-counting order totals.

**Reasoning:** Start from line items, join through orders and customers, then aggregate at country grain.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.country,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM order_items AS oi
JOIN orders AS o
  ON o.order_id = oi.order_id
JOIN customers AS c
  ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC, c.country;
```

**Expected shape:** One row per country represented by an order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Extension: Calculate net line revenue by customer country without double-counting order totals” observable through the exact DDL/DML command tag plus one row at country grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `net_revenue`, `oi`, `o`, `c`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `net_revenue`, `oi`, `o`, `c`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Calculate net line revenue by customer country without double-counting order totals. Why: Start from line items, join through orders and customers, then aggregate at country grain. Expected: One row per country represented by an order. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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
