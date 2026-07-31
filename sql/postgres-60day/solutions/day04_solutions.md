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

- **Inputs/evidence:** For sql-04 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `order_count`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 1, expected output: One row per customer; zero is visible. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
- **Independent verification:** For sql-04 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-04 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-04 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and `full_name`, and finish with `customer_id`, `full_name`, and `order_count` ordered by `order_count DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-04 Exercise 1, the chosen form is justified by this lesson-specific rationale: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`. Evaluate another form against the concrete expected result (One row per customer; zero is visible) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-04 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
- **Independent verification:** For sql-04 Exercise 2, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `product_id`, `name`, and `category` values match those staged rows without unintended fanout or loss. Add one row for which `(oi.order_item_id IS NULL)` is true and one for which it is false; verify only the matching `product_id` value is returned.
- **Intermediate relation check:** For sql-04 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-04 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, and `order_items`, preserve one row per `product_id`, and finish with `product_id`, `name`, and `category` ordered by `p.product_id`.
- **Alternative/trade-off:** For sql-04 Exercise 2, the chosen form is justified by this lesson-specific rationale: Left join and retain rows where the right-side primary key is NULL. Evaluate another form against the concrete expected result (One row per unsold product) and the verification above.
- **Edge case:** Add one row for which `(oi.order_item_id IS NULL)` is true and one for which it is false; verify only the matching `product_id` value is returned.

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

- **Inputs/evidence:** For sql-04 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, and `actual_amount`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 3, expected output: One row per category/month present in either source. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
- **Independent verification:** For sql-04 Exercise 3, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, and `actual_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
- **Intermediate relation check:** For sql-04 Exercise 3, run `expense_months`, and `budget_months` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-04 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, and `budgets`, preserve one row per `category`, and finish with `category`, `period`, `budget_amount`, and `actual_amount` ordered by `period, category`.
- **Alternative/trade-off:** For sql-04 Exercise 3, the chosen form is justified by this lesson-specific rationale: Aggregate each side to the same category/month grain before joining; preserve keys from either side. Evaluate another form against the concrete expected result (One row per category/month present in either source) and the verification above.
- **Edge case:** Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.

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

- **Inputs/evidence:** For sql-04 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `delivered_orders`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 4, expected output: One row per customer, including zero delivered orders. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
- **Independent verification:** For sql-04 Exercise 4, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `delivered_orders` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `delivered_orders` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-04 Exercise 4, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-04 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and `full_name`, and finish with `customer_id`, `full_name`, and `delivered_orders` ordered by `delivered_orders DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-04 Exercise 4, the chosen form is justified by this lesson-specific rationale: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers. Evaluate another form against the concrete expected result (One row per customer, including zero delivered orders) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `delivered_orders` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-04 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `order_count`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 5, expected output: One row per customer with correct zero counts. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
- **Independent verification:** For sql-04 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-04 Exercise 5, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-04 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id`, and `order_count` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-04 Exercise 5, the chosen form is justified by this lesson-specific rationale: Count a non-nullable right-side key that becomes NULL for an unmatched row. Evaluate another form against the concrete expected result (One row per customer with correct zero counts) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id` tuple and verify the new tuple appears exactly once.

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

- **Inputs/evidence:** For sql-04 Exercise 6, read from `products`, and `order_items`. Build the answer toward `matched_products`, `unsold_products`, and `orphan_item_product_ids`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-04 Exercise 6, expected output: One summary row with three mutually interpretable counts. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
- **Independent verification:** For sql-04 Exercise 6, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `matched_products`, `unsold_products`, and `orphan_item_product_ids` values match those staged rows without unintended fanout or loss. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.
- **Intermediate relation check:** For sql-04 Exercise 6, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-04 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `products`, and `order_items`, preserve one row per `product_id`, and finish with `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
- **Alternative/trade-off:** For sql-04 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero. Evaluate another form against the concrete expected result (One summary row with three mutually interpretable counts) and the verification above.
- **Edge case:** Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
