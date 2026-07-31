# Day 18 solutions — LAG/LEAD and Intra-Row Comparisons


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day18_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day18_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Offset, Default value, Calendar spine. Its worked-model focus is:
At monthly grain, place revenue beside LAG(revenue) OVER (ORDER BY month). The first row has no predecessor and returns NULL. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.

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

These answers align one-for-one with [day18_lag_lead.sql](../day18_lag_lead.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Primary pitfall:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Show each order with the previous order timestamp for that customer.

**Reasoning:** Partition by customer and order by timestamp plus ID.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       LAG(o.order_date) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
       ) AS previous_order_date
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

**Expected shape:** One row per order; first customer order has NULL previous timestamp.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `previous_order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 1, expected output: One row per order; first customer order has NULL previous timestamp. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-18 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `previous_order_date`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-18 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
- **Clause check:** For sql-18 Exercise 1, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, and `previous_order_date` ordered by `o.customer_id, o.order_date, o.order_id`.
- **Alternative/trade-off:** For sql-18 Exercise 1, the chosen form is justified by this lesson-specific rationale: Partition by customer and order by timestamp plus ID. Evaluate another form against the concrete expected result (One row per order; first customer order has NULL previous timestamp) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 2 — Query writing

**Prompt:** Calculate days since each customer's previous order.

**Reasoning:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH sequenced AS (
  SELECT o.*,
         LAG(o.order_date) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
         ) AS previous_order_date
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date,
       previous_order_date,
       EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0 AS days_since_previous
FROM sequenced
ORDER BY customer_id, order_date, order_id;
```

**Expected shape:** One row per order with nullable interval/days.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 2, expected output: One row per order with nullable interval/days. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
- **Independent verification:** For sql-18 Exercise 2, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-18 Exercise 2, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-18 Exercise 2, the solution actually uses `WITH`, `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous` ordered by `customer_id, order_date, order_id`.
- **Alternative/trade-off:** For sql-18 Exercise 2, the chosen form is justified by this lesson-specific rationale: Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders. Evaluate another form against the concrete expected result (One row per order with nullable interval/days) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 3 — Query writing

**Prompt:** Show each promotion with the next promotion start date for the same product.

**Reasoning:** Partition by product and define a stable chronological order.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT pr.promotion_id,
       pr.product_id,
       pr.start_date,
       LEAD(pr.start_date) OVER (
         PARTITION BY pr.product_id
         ORDER BY pr.start_date, pr.promotion_id
       ) AS next_promotion_start
FROM promotions AS pr
ORDER BY pr.product_id, pr.start_date, pr.promotion_id;
```

**Expected shape:** One row per promotion; last product promotion has NULL next date.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 3, read from `promotions`. Build the answer toward `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`; keep `promotion_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 3, expected output: One row per promotion; last product promotion has NULL next date. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
- **Independent verification:** For sql-18 Exercise 3, choose one complete partition from `promotions`; hand-calculate its first, middle, and final window values for `product_id`, `start_date`, and `next_promotion_start`, then verify output keys remain `promotion_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-18 Exercise 3, inspect one window partition before projecting; then check `pr.product_id, pr.start_date, pr.promotion_id` before applying the row cap.
- **Clause check:** For sql-18 Exercise 3, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `promotions`, preserve one row per `promotion_id`, and finish with `promotion_id`, `product_id`, `start_date`, and `next_promotion_start` ordered by `pr.product_id, pr.start_date, pr.promotion_id`.
- **Alternative/trade-off:** For sql-18 Exercise 3, the chosen form is justified by this lesson-specific rationale: Partition by product and define a stable chronological order. Evaluate another form against the concrete expected result (One row per promotion; last product promotion has NULL next date) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Prediction

**Prompt:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.

**Reasoning:** NULL means there is no prior observation; preserve that semantic state.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH sequenced AS (
  SELECT o.*,
         LAG(o.order_id) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
         ) AS previous_order_id
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date
FROM sequenced
WHERE previous_order_id IS NULL
ORDER BY customer_id;
```

**Expected shape:** One row per customer's first order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 4, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 4, expected output: One row per customer's first order. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
- **Independent verification:** For sql-18 Exercise 4, run an anti-check that counts rows where NOT ((previous_order_id IS NULL)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Repeat with `NULL` in `order_id`, and `customer_id` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-18 Exercise 4, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-18 Exercise 4, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, and `order_date` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-18 Exercise 4, the chosen form is justified by this lesson-specific rationale: NULL means there is no prior observation; preserve that semantic state. Evaluate another form against the concrete expected result (One row per customer's first order) and the verification above.
- **Edge case:** Repeat with `NULL` in `order_id`, and `customer_id` and state whether the row is kept, rejected, or classified.

## Exercise 5 — Debugging

**Prompt:** Compute month-over-month stored-revenue change after aggregating to month grain.

**Reasoning:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), compared AS (
  SELECT month_start,
         revenue,
         LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM monthly
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_revenue, 2) AS previous_revenue,
       ROUND(revenue - previous_revenue, 2) AS revenue_change
FROM compared
ORDER BY month_start;
```

**Expected shape:** One row per month with nullable first change.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `revenue_change`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 5, expected output: One row per month with nullable first change. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
- **Independent verification:** For sql-18 Exercise 5, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `revenue_change` against `orders`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
- **Intermediate relation check:** For sql-18 Exercise 5, run `monthly`, and `compared` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-18 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `month`, and finish with `month_start`, `revenue`, `previous_revenue`, and `revenue_change` ordered by `month_start`.
- **Alternative/trade-off:** For sql-18 Exercise 5, the chosen form is justified by this lesson-specific rationale: Aggregate first; applying lag to raw orders would compare adjacent orders rather than months. Evaluate another form against the concrete expected result (One row per month with nullable first change) and the verification above.
- **Edge case:** Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.

## Exercise 6 — Extension

**Prompt:** Compare each product price with the next higher price in its category.

**Reasoning:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
- `PARTITION BY`: restarts a window calculation independently for each partition key.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.category,
       p.price,
       LEAD(p.price) OVER (
         PARTITION BY p.category
         ORDER BY p.price, p.product_id
       ) AS next_price
FROM products AS p
ORDER BY p.category, p.price, p.product_id;
```

**Expected shape:** One row per product with nullable next price.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 6, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `next_price`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-18 Exercise 6, expected output: One row per product with nullable next price. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-18 Exercise 6, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `next_price`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-18 Exercise 6, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.
- **Clause check:** For sql-18 Exercise 6, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `category`, `price`, and `next_price` ordered by `p.category, p.price, p.product_id`.
- **Alternative/trade-off:** For sql-18 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use ascending price order and product ID to define adjacency; equal prices remain separate rows. Evaluate another form against the concrete expected result (One row per product with nullable next price) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
