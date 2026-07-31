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

- **Inputs/evidence:** For sql-07 Exercise 1, read from `orders`. Build the answer toward `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`; keep `status` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-07 Exercise 1, expected output: One row per order status. The final columns are `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`. The final order is `revenue DESC, o.status`.
- **Independent verification:** For sql-07 Exercise 1, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, `customer_count`, `revenue`, and `average_order_value` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, `customer_count`, and `revenue` for the existing `status` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-07 Exercise 1, confirm the groups are `status`; then check `revenue DESC, o.status` before applying the row cap.
- **Clause check:** For sql-07 Exercise 1, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `status`, and finish with `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value` ordered by `revenue DESC, o.status`.
- **Alternative/trade-off:** For sql-07 Exercise 1, the chosen form is justified by this lesson-specific rationale: Aggregate orders at status grain and round only displayed monetary values. Evaluate another form against the concrete expected result (One row per order status) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, `customer_count`, and `revenue` for the existing `status` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-07 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, `category`, and `net_revenue`; keep `product_id`, `name`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-07 Exercise 2, expected output: At most 20 product rows. The final columns are `product_id`, `name`, `category`, and `net_revenue`. The final order is `net_revenue DESC, p.product_id`.
- **Independent verification:** For sql-07 Exercise 2, assert no more than 20 rows, no duplicate `product_id`, `name`, and `category`, and no adjacent pair that violates `net_revenue DESC, p.product_id`. Rejoin the returned keys to `products`, and `order_items` to confirm `product_id`, `name`, `category`, and `net_revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `net_revenue DESC, p.product_id`.
- **Intermediate relation check:** For sql-07 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
- **Clause check:** For sql-07 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `products`, and `order_items`, preserve one row per `product_id`, `name`, and `category`, and finish with `product_id`, `name`, `category`, and `net_revenue` ordered by `net_revenue DESC, p.product_id`.
- **Alternative/trade-off:** For sql-07 Exercise 2, the chosen form is justified by this lesson-specific rationale: Aggregate order items by product before ranking; use product ID as tie-breaker. Evaluate another form against the concrete expected result (At most 20 product rows) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `net_revenue DESC, p.product_id`.

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

- **Inputs/evidence:** For sql-07 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`; keep `customer_id`, `full_name`, and `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-07 Exercise 3, expected output: One row per customer. The final columns are `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`. The final order is `stored_order_total DESC, c.customer_id`.
- **Independent verification:** For sql-07 Exercise 3, independently aggregate `customers`, and `orders` by `customer_id`, `full_name`, and `country`; require one output row for every distinct `customer_id`, `full_name`, and `country` tuple and compare `order_count`, and `stored_order_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_order_total` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-07 Exercise 3, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-07 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, `full_name`, and `country`, and finish with `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total` ordered by `stored_order_total DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-07 Exercise 3, the chosen form is justified by this lesson-specific rationale: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning. Evaluate another form against the concrete expected result (One row per customer) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_order_total` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-07 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-07 Exercise 4, expected output: One row per order with signed differences. The final columns are `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`. The final order is `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
- **Independent verification:** For sql-07 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-07 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-07 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, `payments`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance` ordered by `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
- **Alternative/trade-off:** For sql-07 Exercise 4, the chosen form is justified by this lesson-specific rationale: Aggregate each detail table to order grain first, then join the one-row-per-order relations. Evaluate another form against the concrete expected result (One row per order with signed differences) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

- **Inputs/evidence:** For sql-07 Exercise 5, read from `orders`. Build the answer toward `order_month`, `order_count`, and `stored_revenue`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-07 Exercise 5, expected output: One row per observed order month. The final columns are `order_month`, `order_count`, and `stored_revenue`. The final order is `order_month`.
- **Independent verification:** For sql-07 Exercise 5, independently aggregate `orders` by `order_id`; require one output row for every distinct `order_id` tuple and compare `order_month`, `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_month`, `order_count`, and `stored_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-07 Exercise 5, confirm the groups are `order_id`; then check `order_month` before applying the row cap.
- **Clause check:** For sql-07 Exercise 5, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_month`, `order_count`, and `stored_revenue` ordered by `order_month`.
- **Alternative/trade-off:** For sql-07 Exercise 5, the chosen form is justified by this lesson-specific rationale: Grouping observed orders alone cannot create empty calendar months. Evaluate another form against the concrete expected result (One row per observed order month) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_month`, `order_count`, and `stored_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-07 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Compute `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-07 Exercise 6, expected output: Exactly one audit row. The final columns are `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
- **Independent verification:** For sql-07 Exercise 6, evaluate each of `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` in a separate control `SELECT` over `customers`, `orders`, `order_items`, and `payments`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-07 Exercise 6, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-07 Exercise 6, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `customers`, `orders`, `order_items`, and `payments`, preserve exactly one summary row, and finish with `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
- **Alternative/trade-off:** For sql-07 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use scalar subqueries for independent counts; this avoids accidental cross multiplication. Evaluate another form against the concrete expected result (Exactly one audit row) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
