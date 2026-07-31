# Day 20 solutions — FIRST_VALUE, LAST_VALUE, NTH_VALUE


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day20_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day20_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Boundary value, Current-row frame, Full-partition frame. Its worked-model focus is:
Order a customer's orders by date and compare default LASTVALUE(totalamount) with the same function over ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. The default often returns the current row's value; the full frame exposes the true final value.

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

These answers align one-for-one with [day20_first_last_value.sql](../day20_first_last_value.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Primary pitfall:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Show every order with the customer's first and last order timestamps.

**Reasoning:** Use one full-partition frame from unbounded preceding through unbounded following.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       FIRST_VALUE(o.order_date) OVER customer_orders AS first_order_date,
       LAST_VALUE(o.order_date) OVER customer_orders AS last_order_date
FROM orders AS o
WINDOW customer_orders AS (
  PARTITION BY o.customer_id
  ORDER BY o.order_date, o.order_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order with constant first/last values per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 1, read from `orders`. Compute `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-20 Exercise 1, expected output: One row per order with constant first/last values per customer. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-20 Exercise 1, evaluate each of `order_date`, `first_order_date`, and `last_order_date` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-20 Exercise 1, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-20 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve exactly one summary row, and finish with `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-20 Exercise 1, the chosen form is justified by this lesson-specific rationale: Use one full-partition frame from unbounded preceding through unbounded following. Evaluate another form against the concrete expected result (One row per order with constant first/last values per customer) and the verification above.
- **Edge case:** Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.

## Exercise 2 — Query writing

**Prompt:** Show each product with the cheapest and most expensive price in its category.

**Reasoning:** Order by price and use a full frame; values tie without needing row identity.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.category,
       p.price,
       FIRST_VALUE(p.price) OVER category_prices AS category_min_price,
       LAST_VALUE(p.price) OVER category_prices AS category_max_price
FROM products AS p
WINDOW category_prices AS (
  PARTITION BY p.category
  ORDER BY p.price, p.product_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 2, read from `products`. Compute `product_id`, `category`, `price`, `category_min_price`, and `category_max_price` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-20 Exercise 2, expected output: One row per product. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-20 Exercise 2, evaluate each of `category_min_price`, and `category_max_price` in a separate control `SELECT` over `products`; require one final row and compare every value. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.
- **Intermediate relation check:** For sql-20 Exercise 2, check `p.category, p.price, p.product_id` before applying the row cap.
- **Clause check:** For sql-20 Exercise 2, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve exactly one summary row, and finish with `product_id`, `category`, `price`, `category_min_price`, and `category_max_price` ordered by `p.category, p.price, p.product_id`.
- **Alternative/trade-off:** For sql-20 Exercise 2, the chosen form is justified by this lesson-specific rationale: Order by price and use a full frame; values tie without needing row identity. Evaluate another form against the concrete expected result (One row per product) and the verification above.
- **Edge case:** Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.

## Exercise 3 — Query writing

**Prompt:** Compare every payment with the first and last payment amount for its order.

**Reasoning:** Partition by order, order by timestamp/payment ID, and keep the full frame.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.payment_id,
       p.order_id,
       p.payment_date,
       p.amount,
       FIRST_VALUE(p.amount) OVER payment_sequence AS first_payment_amount,
       LAST_VALUE(p.amount) OVER payment_sequence AS last_payment_amount
FROM payments AS p
WINDOW payment_sequence AS (
  PARTITION BY p.order_id
  ORDER BY p.payment_date, p.payment_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.order_id, p.payment_date, p.payment_id;
```

**Expected shape:** One row per payment.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 3, read from `payments`. Compute `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-20 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
- **Independent verification:** For sql-20 Exercise 3, evaluate each of `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` in a separate control `SELECT` over `payments`; require one final row and compare every value. Tie two rows on `p.order_id` and give them different `p.payment_id` values; verify `p.order_id, p.payment_date, p.payment_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-20 Exercise 3, check `p.order_id, p.payment_date, p.payment_id` before applying the row cap.
- **Clause check:** For sql-20 Exercise 3, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, preserve exactly one summary row, and finish with `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` ordered by `p.order_id, p.payment_date, p.payment_id`.
- **Alternative/trade-off:** For sql-20 Exercise 3, the chosen form is justified by this lesson-specific rationale: Partition by order, order by timestamp/payment ID, and keep the full frame. Evaluate another form against the concrete expected result (One row per payment) and the verification above.
- **Edge case:** Tie two rows on `p.order_id` and give them different `p.payment_id` values; verify `p.order_id, p.payment_date, p.payment_id` chooses a stable first/last row.

## Exercise 4 — Prediction

**Prompt:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.

**Reasoning:** The default ends at the current row; explicit following reaches the true last row.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT value,
       LAST_VALUE(value) OVER (ORDER BY value) AS default_last_value,
       LAST_VALUE(value) OVER (
         ORDER BY value
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS partition_last_value
FROM (VALUES (10), (20), (30)) AS sample(value)
ORDER BY value;
```

**Expected shape:** Three rows showing default current value and full-frame 30.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`, `default_last_value`, and `partition_last_value`; keep `value` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-20 Exercise 4, expected output: Three rows showing default current value and full-frame 30. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
- **Independent verification:** For sql-20 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `default_last_value`, and `partition_last_value`, then verify output keys remain `value`. Use a one-row partition and a partition tied on `value`; verify `value` and `value` preserve the intended first/last row.
- **Intermediate relation check:** For sql-20 Exercise 4, inspect one window partition before projecting; then check `value` before applying the row cap.
- **Clause check:** For sql-20 Exercise 4, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `value`, and finish with `value`, `default_last_value`, and `partition_last_value` ordered by `value`.
- **Alternative/trade-off:** For sql-20 Exercise 4, the chosen form is justified by this lesson-specific rationale: The default ends at the current row; explicit following reaches the true last row. Evaluate another form against the concrete expected result (Three rows showing default current value and full-frame 30) and the verification above.
- **Edge case:** Use a one-row partition and a partition tied on `value`; verify `value` and `value` preserve the intended first/last row.

## Exercise 5 — Debugging

**Prompt:** Return one first and one last order per customer without using window output as an accidental duplicate report.

**Reasoning:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- window frame: states exactly which rows or peers contribute to the current row's window result.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH annotated AS (
  SELECT o.customer_id,
         FIRST_VALUE(o.order_id) OVER customer_orders AS first_order_id,
         LAST_VALUE(o.order_id) OVER customer_orders AS last_order_id
  FROM orders AS o
  WINDOW customer_orders AS (
    PARTITION BY o.customer_id
    ORDER BY o.order_date, o.order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
SELECT DISTINCT customer_id,
       first_order_id,
       last_order_id
FROM annotated
ORDER BY customer_id;
```

**Expected shape:** One row per customer with orders.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 5, read from `orders`. Compute `customer_id`, `first_order_id`, and `last_order_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-20 Exercise 5, expected output: One row per customer with orders. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
- **Independent verification:** For sql-20 Exercise 5, evaluate each of `first_order_id`, and `last_order_id` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `customer_id` and give them different `customer_id` values; verify `customer_id` chooses a stable first/last row.
- **Intermediate relation check:** For sql-20 Exercise 5, run `annotated` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-20 Exercise 5, the solution actually uses `WITH`, `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve exactly one summary row, and finish with `customer_id`, `first_order_id`, and `last_order_id` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-20 Exercise 5, the chosen form is justified by this lesson-specific rationale: Compute first/last IDs with full-frame windows, then select distinct customer-level output. Evaluate another form against the concrete expected result (One row per customer with orders) and the verification above.
- **Edge case:** Tie two rows on `customer_id` and give them different `customer_id` values; verify `customer_id` chooses a stable first/last row.

## Exercise 6 — Extension

**Prompt:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.

**Reasoning:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `DISTINCT ON`: keeps the first row in each declared group, so its matching leading sort keys determine which row wins.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT DISTINCT ON (o.customer_id)
       o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount
FROM orders AS o
ORDER BY o.customer_id, o.order_date DESC, o.order_id DESC;
```

**Expected shape:** At most one latest order per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-20 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `order_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-20 Exercise 6, expected output: At most one latest order per customer. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-20 Exercise 6, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `customer_id`, `order_id`, `order_date`, and `total_amount` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id DESC` values; verify `o.customer_id, o.order_date DESC, o.order_id DESC` chooses a stable first/last row.
- **Intermediate relation check:** For sql-20 Exercise 6, check `o.customer_id, o.order_date DESC, o.order_id DESC` before applying the row cap.
- **Clause check:** For sql-20 Exercise 6, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `customer_id`, `order_id`, `order_date`, and `total_amount` ordered by `o.customer_id, o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-20 Exercise 6, the chosen form is justified by this lesson-specific rationale: `DISTINCT ON` keeps the first row under its mandatory leading order keys. Evaluate another form against the concrete expected result (At most one latest order per customer) and the verification above.
- **Edge case:** Tie two rows on `o.customer_id` and give them different `o.order_id DESC` values; verify `o.customer_id, o.order_date DESC, o.order_id DESC` chooses a stable first/last row.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
