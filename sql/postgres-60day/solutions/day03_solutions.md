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

- **Inputs/evidence:** For sql-03 Exercise 1, read from `orders`, and `customers`. Build the answer toward `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 1, expected output: One row per order. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-03 Exercise 1, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-03 Exercise 1, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-03 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country` ordered by `o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-03 Exercise 1, the chosen form is justified by this lesson-specific rationale: Join the order foreign key to the customer primary key and qualify every selected column. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

- **Inputs/evidence:** For sql-03 Exercise 2, read from `order_items`, and `products`. Build the answer toward `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`; keep `order_item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 2, expected output: One row per order item. The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
- **Independent verification:** For sql-03 Exercise 2, project `order_item_id` plus the raw source columns from `order_items`, and `products` at each join stage; record row count and distinct `order_item_id`, then assert the final `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
- **Intermediate relation check:** For sql-03 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `order_item_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-03 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, and `products`, preserve one row per `order_item_id`, and finish with `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue` ordered by `oi.order_id, oi.order_item_id`.
- **Alternative/trade-off:** For sql-03 Exercise 2, the chosen form is justified by this lesson-specific rationale: Remain at one row per order item; do not aggregate until the desired grain changes. Evaluate another form against the concrete expected result (One row per order item) and the verification above.
- **Edge case:** Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.

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

- **Inputs/evidence:** For sql-03 Exercise 3, read from `payments`, `orders`, and `customers`. Build the answer toward `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`; keep `payment_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
- **Independent verification:** For sql-03 Exercise 3, project `payment_id` plus the raw source columns from `payments`, `orders`, and `customers` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
- **Intermediate relation check:** For sql-03 Exercise 3, start with the first relation in `payments`, `orders`, and `customers`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-03 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, `orders`, and `customers`, preserve one row per `payment_id`, and finish with `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name` ordered by `p.payment_date DESC, p.payment_id DESC`.
- **Alternative/trade-off:** For sql-03 Exercise 3, the chosen form is justified by this lesson-specific rationale: Follow payments → orders → customers using each declared foreign key. Evaluate another form against the concrete expected result (One row per payment) and the verification above.
- **Edge case:** Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.

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

- **Inputs/evidence:** For sql-03 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `item_total`, and `paid_total`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 4, expected output: One row per order; no six-row multiplication. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
- **Independent verification:** For sql-03 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `item_total`, and `paid_total` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-03 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-03 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, `payments`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `item_total`, and `paid_total` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-03 Exercise 4, the chosen form is justified by this lesson-specific rationale: Aggregate items and payments separately to one row per order before joining those aggregates. Evaluate another form against the concrete expected result (One row per order; no six-row multiplication) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

- **Inputs/evidence:** For sql-03 Exercise 5, read from `orders`, and `customers`. Build the answer toward `joined_rows`, and `distinct_orders`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 5, expected output: Exactly one customer match per order. The final columns are `joined_rows`, and `distinct_orders`.
- **Independent verification:** For sql-03 Exercise 5, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `joined_rows`, and `distinct_orders` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-03 Exercise 5, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-03 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `order_id`, and finish with `joined_rows`, and `distinct_orders`.
- **Alternative/trade-off:** For sql-03 Exercise 5, the chosen form is justified by this lesson-specific rationale: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join. Evaluate another form against the concrete expected result (Exactly one customer match per order) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

- **Inputs/evidence:** For sql-03 Exercise 6, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `net_revenue`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-03 Exercise 6, expected output: One row per country represented by an order. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
- **Independent verification:** For sql-03 Exercise 6, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-03 Exercise 6, start with the first relation in `order_items`, `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-03 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, `orders`, and `customers`, preserve one row per `country`, and finish with `country`, and `net_revenue` ordered by `net_revenue DESC, c.country`.
- **Alternative/trade-off:** For sql-03 Exercise 6, the chosen form is justified by this lesson-specific rationale: Start from line items, join through orders and customers, then aggregate at country grain. Evaluate another form against the concrete expected result (One row per country represented by an order) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `net_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
