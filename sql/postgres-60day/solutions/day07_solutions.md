# Day 07 solutions — Week 1 Project: From Questions to Queries


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day07_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day07_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Report grain, Reconciliation, Allocation rule. Its worked-model focus is:
Build the report in checkpoints: aggregate net line revenue to order/category, reduce payments to the declared order/method grain, join those stable inputs, and only then roll up country, category, and method. Reconcile revenue before adding cohort month so a new dimension cannot hide fanout.

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

These answers align one-for-one with [day07_week1_project.sql](../day07_week1_project.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
- **Assumptions:** Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
- **Primary pitfall:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Build an order KPI table by status with order count, revenue, average order value, and distinct customers.

**Reasoning:** Aggregate orders at status grain and round only displayed monetary values.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.status,
       COUNT(*) AS order_count,
       COUNT(DISTINCT o.customer_id) AS customer_count,
       ROUND(SUM(o.total_amount), 2) AS revenue,
       ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM orders AS o
GROUP BY o.status
ORDER BY revenue DESC, o.status;
```

**Expected shape:** One row per order status.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 1 must make “Query writing: Build an order KPI table by status with order count, revenue, average order value, and distinct customers” observable through the exact DDL/DML command tag plus one row at status grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`.
- **Independent verification:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 1: Query writing Prompt: Build an order KPI table by status with order count, revenue, average order value, and distinct customers. Why: Aggregate orders at status grain and round only displayed monetary values. Expected: One row per order status. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Return the 20 products with the highest net line revenue.

**Reasoning:** Aggregate order items by product before ranking; use product ID as tie-breaker.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT p.product_id,
       p.name,
       p.category,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM products AS p
JOIN order_items AS oi
  ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY net_revenue DESC, p.product_id
LIMIT 20;
```

**Expected shape:** At most 20 product rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Return the 20 products with the highest net line revenue” at one row per product or product grouping requested. Named evidence columns/objects: `tie`, `evidence`, `net_revenue`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Return the 20 products with the highest net line revenue. Why: Aggregate order items by product before ranking; use product ID as tie-breaker. Expected: At most 20 product rows. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic. - LIMIT: is applied after ordering and is meaningful only when the query first defines which rows come first.
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

**Prompt:** Create a customer summary that retains customers with no orders.

**Reasoning:** Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       c.country,
       COUNT(o.order_id) AS order_count,
       COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_order_total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.country
ORDER BY stored_order_total DESC, c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 3 must make “Query writing: Create a customer summary that retains customers with no orders” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `stored_order_total`, `c`, `o`.
- **Independent verification:** For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `stored_order_total`, `c`, `o`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 3: Query writing Prompt: Create a customer summary that retains customers with no orders. Why: Left join from customers and count/order-sum nullable matches with COALESCE only where zero has clear meaning. Expected: One row per customer. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - COALESCE: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

## Exercise 4 — Debugging

**Prompt:** Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.

**Reasoning:** Aggregate each detail table to order grain first, then join the one-row-per-order relations.

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
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), payment_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       o.status,
       ROUND(o.total_amount, 2) AS stored_total,
       ROUND(it.line_total, 2) AS line_total,
       ROUND(o.total_amount - it.line_total, 2) AS storage_difference,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
       ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM orders AS o
JOIN item_totals AS it
  ON it.order_id = o.order_id
LEFT JOIN payment_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY ABS(o.total_amount - it.line_total) DESC, o.order_id;
```

**Expected shape:** One row per order with signed differences.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 4 returns a table-shaped answer to “Debugging: Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `p`, `stored_total`, `storage_difference`, `unpaid_balance`, `o`, `it`, `pt`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 4, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `payments`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 4: Debugging Prompt: Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows. Why: Aggregate each detail table to order grain first, then join the one-row-per-order relations. Expected: One row per order with signed differences. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - WITH: names an intermediate relation so its grain can be checked before later joins or aggregation. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - COALESCE: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

## Exercise 5 — Prediction

**Prompt:** Build a monthly order trend and explain which months are absent rather than zero.

**Reasoning:** Grouping observed orders alone cannot create empty calendar months.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT date_trunc('month', o.order_date)::date AS order_month,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM orders AS o
GROUP BY date_trunc('month', o.order_date)
ORDER BY order_month;
```

**Expected shape:** One row per observed order month.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 needs the plan evidence for “Prediction: Build a monthly order trend and explain which months are absent rather than zero”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `order_month`, `order_count`, `stored_revenue`, `o`.
- **Independent verification:** For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers. The executable solution's check is: Exercise 5: Prediction Prompt: Build a monthly order trend and explain which months are absent rather than zero. Why: Grouping observed orders alone cannot create empty calendar months. Expected: One row per observed order month. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
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

**Prompt:** Create a compact one-row audit of customer, order, item, and payment coverage.

**Reasoning:** Use scalar subqueries for independent counts; this avoids accidental cross multiplication.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.

```sql
SELECT (SELECT COUNT(*) FROM customers) AS customer_rows,
       (SELECT COUNT(*) FROM orders) AS order_rows,
       (SELECT COUNT(*) FROM order_items) AS order_item_rows,
       (SELECT COUNT(*) FROM payments) AS payment_rows,
       (SELECT COUNT(*) FROM customers AS c
        WHERE NOT EXISTS (
          SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id
        )) AS customers_without_orders;
```

**Expected shape:** Exactly one audit row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Extension: Create a compact one-row audit of customer, order, item, and payment coverage” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Create a compact one-row audit of customer, order, item, and payment coverage. Why: Use scalar subqueries for independent counts; this avoids accidental cross multiplication. Expected: Exactly one audit row. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
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
