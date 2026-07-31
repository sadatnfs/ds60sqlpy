# Day 09 solutions — Correlated Subqueries and EXISTS


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day09_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day09_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Correlation, Semi-join, Anti-join. Its worked-model focus is:
Read WHERE EXISTS (...) as a yes/no question for one outer customer. The subquery may stop after its first qualifying order, and it never adds order columns or duplicates the customer. Replace it temporarily with a join to see why DISTINCT may become necessary in the join form.

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

These answers align one-for-one with [day09_correlated_subqueries.sql](../day09_correlated_subqueries.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
- **Assumptions:** `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
- **Primary pitfall:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Return customers who have at least one delivered order.

**Reasoning:** `EXISTS` expresses the yes/no question without multiplying customer rows.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
    AND o.status = 'delivered'
)
ORDER BY c.customer_id;
```

**Expected shape:** One row per qualifying customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 1, expected output: One row per qualifying customer. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 1, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-09 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, and `full_name` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-09 Exercise 1, the chosen form is justified by this lesson-specific rationale: `EXISTS` expresses the yes/no question without multiplying customer rows. Evaluate another form against the concrete expected result (One row per qualifying customer) and the verification above.
- **Edge case:** Add one row for which `(EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Exercise 2 — Query writing

**Prompt:** Return products that have never been sold.

**Reasoning:** `NOT EXISTS` correlates on product ID and is not confused by NULL membership.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.name,
       p.category
FROM products AS p
WHERE NOT EXISTS (
  SELECT 1
  FROM order_items AS oi
  WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;
```

**Expected shape:** One row per unsold product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
- **Independent verification:** For sql-09 Exercise 2, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, and `category` against `products`, and `order_items`. Add one row for which `(NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))` is true and one for which it is false; verify only the matching `product_id` value is returned.
- **Intermediate relation check:** For sql-09 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.product_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, and `order_items`, preserve one row per `product_id`, and finish with `product_id`, `name`, and `category` ordered by `p.product_id`.
- **Alternative/trade-off:** For sql-09 Exercise 2, the chosen form is justified by this lesson-specific rationale: `NOT EXISTS` correlates on product ID and is not confused by NULL membership. Evaluate another form against the concrete expected result (One row per unsold product) and the verification above.
- **Edge case:** Add one row for which `(NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))` is true and one for which it is false; verify only the matching `product_id` value is returned.

## Exercise 3 — Query writing

**Prompt:** Return each customer's orders that are above that customer's average order total.

**Reasoning:** Correlate the average to the current order's customer, not to the current order ID.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount
FROM orders AS o
WHERE o.total_amount > (
  SELECT AVG(peer.total_amount)
  FROM orders AS peer
  WHERE peer.customer_id = o.customer_id
)
ORDER BY o.customer_id, o.total_amount DESC, o.order_id;
```

**Expected shape:** Order rows above their own customer average.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 3, expected output: Order rows above their own customer average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
- **Independent verification:** For sql-09 Exercise 3, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-09 Exercise 3, inspect the source keys that survive `WHERE`; then check `o.customer_id, o.total_amount DESC, o.order_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, and `total_amount` ordered by `o.customer_id, o.total_amount DESC, o.order_id`.
- **Alternative/trade-off:** For sql-09 Exercise 3, the chosen form is justified by this lesson-specific rationale: Correlate the average to the current order's customer, not to the current order ID. Evaluate another form against the concrete expected result (Order rows above their own customer average) and the verification above.
- **Edge case:** Add one row for which `(o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 4 — Prediction

**Prompt:** Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.

**Reasoning:** Correlate on the customer key; a matching row alone determines exclusion.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer with no order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 4, expected output: One row per customer with no order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 4, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-09 Exercise 4, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 4, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, and `full_name` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-09 Exercise 4, the chosen form is justified by this lesson-specific rationale: Correlate on the customer key; a matching row alone determines exclusion. Evaluate another form against the concrete expected result (One row per customer with no order) and the verification above.
- **Edge case:** Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.

## Exercise 5 — Debugging

**Prompt:** Return only each customer's most recent order without an arbitrary `LIMIT 1`.

**Reasoning:** Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
- `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date
FROM orders AS o
WHERE o.order_id = (
  SELECT candidate.order_id
  FROM orders AS candidate
  WHERE candidate.customer_id = o.customer_id
  ORDER BY candidate.order_date DESC, candidate.order_id DESC
  LIMIT 1
)
ORDER BY o.customer_id;
```

**Expected shape:** At most one deterministic order per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 5, expected output: At most one deterministic order per customer. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
- **Independent verification:** For sql-09 Exercise 5, run an anti-check that counts rows where NOT ((o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Add one row for which `(o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-09 Exercise 5, inspect the source keys that survive `WHERE`; then check `o.customer_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 5, the solution actually uses `FROM`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, and `order_date` ordered by `o.customer_id`.
- **Alternative/trade-off:** For sql-09 Exercise 5, the chosen form is justified by this lesson-specific rationale: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp. Evaluate another form against the concrete expected result (At most one deterministic order per customer) and the verification above.
- **Edge case:** Add one row for which `(o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 6 — Extension

**Prompt:** Return customers for whom every order has at least one payment, excluding customers with no orders.

**Reasoning:** Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE EXISTS (
  SELECT 1 FROM orders AS any_order
  WHERE any_order.customer_id = c.customer_id
)
  AND NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.order_id
      )
  )
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer satisfying the universal condition.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 6, read from `customers`, `orders`, and `payments`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-09 Exercise 6, expected output: One row per customer satisfying the universal condition. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 6, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, `orders`, and `payments`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-09 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-09 Exercise 6, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, `orders`, and `payments`, preserve one row per `customer_id`, and finish with `customer_id`, and `full_name` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-09 Exercise 6, the chosen form is justified by this lesson-specific rationale: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`. Evaluate another form against the concrete expected result (One row per customer satisfying the universal condition) and the verification above.
- **Edge case:** Add one row for which `(EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
