# Day 15 solutions — Phase 1 Project: Multi-Dimensional Revenue Report


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day15_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day15_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Metric contract, Dimensional report, Control total. Its worked-model focus is:
Build one stable orderlines relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.

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

These answers align one-for-one with [day15_phase1_project.sql](../day15_phase1_project.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Primary pitfall:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.

**Reasoning:** Left join from customers and aggregate at customer grain.

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
       COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_revenue,
       MAX(o.order_date) AS latest_order_date
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.country
ORDER BY stored_revenue DESC, c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`; keep `customer_id`, `full_name`, and `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
- **Independent verification:** For sql-15 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, `full_name`, and `country`; require one output row for every distinct `customer_id`, `full_name`, and `country` tuple and compare `order_count`, `stored_revenue`, and `latest_order_date` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `stored_revenue DESC` and verify `c.customer_id` selects the same row on every run.
- **Intermediate relation check:** For sql-15 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-15 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, `full_name`, and `country`, and finish with `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date` ordered by `stored_revenue DESC, c.customer_id`.
- **Alternative/trade-off:** For sql-15 Exercise 1, the chosen form is justified by this lesson-specific rationale: Left join from customers and aggregate at customer grain. Evaluate another form against the concrete expected result (One row per customer) and the verification above.
- **Edge case:** Use one key absent from `orders`; then tie two candidates on `stored_revenue DESC` and verify `c.customer_id` selects the same row on every run.

## Exercise 2 — Query writing

**Prompt:** Create a product profitability table from net order-line revenue and catalog cost.

**Reasoning:** Calculate line revenue and line cost at item grain, then aggregate to product.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.name,
       p.category,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
       ROUND(SUM(p.cost * oi.quantity), 2) AS catalog_cost,
       ROUND(
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount))
           - SUM(p.cost * oi.quantity),
         2
       ) AS gross_profit
FROM products AS p
JOIN order_items AS oi
  ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY gross_profit DESC, p.product_id;
```

**Expected shape:** One row per sold product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`; keep `product_id`, `name`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 2, expected output: One row per sold product. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
- **Independent verification:** For sql-15 Exercise 2, independently aggregate `products`, and `order_items` by `product_id`, `name`, and `category`; require one output row for every distinct `product_id`, `name`, and `category` tuple and compare `units_sold`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units_sold`, and `net_revenue` for the existing `product_id`, and `name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-15 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
- **Clause check:** For sql-15 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, and `order_items`, preserve one row per `product_id`, `name`, and `category`, and finish with `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit` ordered by `gross_profit DESC, p.product_id`.
- **Alternative/trade-off:** For sql-15 Exercise 2, the chosen form is justified by this lesson-specific rationale: Calculate line revenue and line cost at item grain, then aggregate to product. Evaluate another form against the concrete expected result (One row per sold product) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `units_sold`, and `net_revenue` for the existing `product_id`, and `name` tuple and verify the new tuple appears exactly once.

## Exercise 3 — Query writing

**Prompt:** Build a UTC monthly order-status report with counts and stored revenue.

**Reasoning:** Derive one reporting month and group by month/status.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS utc_month,
       o.status,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM orders AS o
GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), o.status
ORDER BY utc_month, o.status;
```

**Expected shape:** One row per observed month and status.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 3, read from `orders`. Build the answer toward `utc_month`, `status`, `order_count`, and `stored_revenue`; keep `status` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 3, expected output: One row per observed month and status. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
- **Independent verification:** For sql-15 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `status` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-15 Exercise 3, confirm the groups are `status`; then check `utc_month, o.status` before applying the row cap.
- **Clause check:** For sql-15 Exercise 3, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `status`, and finish with `utc_month`, `status`, `order_count`, and `stored_revenue` ordered by `utc_month, o.status`.
- **Alternative/trade-off:** For sql-15 Exercise 3, the chosen form is justified by this lesson-specific rationale: Derive one reporting month and group by month/status. Evaluate another form against the concrete expected result (One row per observed month and status) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `status` tuple and verify the new tuple appears exactly once.

## Exercise 4 — Debugging

**Prompt:** Reconcile stored order total, computed line total, and paid total without multiplying details.

**Reasoning:** Aggregate items and payments independently to order grain before joining.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH line_totals AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), paid_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(o.total_amount, 2) AS stored_total,
       ROUND(lt.line_total, 2) AS line_total,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
       ROUND(o.total_amount - lt.line_total, 2) AS stored_minus_lines,
       ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM orders AS o
JOIN line_totals AS lt
  ON lt.order_id = o.order_id
LEFT JOIN paid_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY ABS(o.total_amount - lt.line_total) DESC, o.order_id;
```

**Expected shape:** One row per order with differences.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 4, expected output: One row per order with differences. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
- **Independent verification:** For sql-15 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-15 Exercise 4, run `line_totals`, and `paid_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-15 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, `payments`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance` ordered by `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
- **Alternative/trade-off:** For sql-15 Exercise 4, the chosen form is justified by this lesson-specific rationale: Aggregate items and payments independently to order grain before joining. Evaluate another form against the concrete expected result (One row per order with differences) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 5 — Prediction

**Prompt:** Compare monthly budgets with actual expenses and preserve missing sides.

**Reasoning:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.

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
WITH actual AS (
  SELECT e.category,
         date_trunc('month', e.expense_date)::date AS period,
         SUM(e.amount) AS amount
  FROM expenses AS e
  GROUP BY e.category, date_trunc('month', e.expense_date)
), planned AS (
  SELECT b.category,
         b.period,
         SUM(b.amount) AS amount
  FROM budgets AS b
  GROUP BY b.category, b.period
)
SELECT COALESCE(p.category, a.category) AS category,
       COALESCE(p.period, a.period) AS period,
       ROUND(p.amount, 2) AS budget_amount,
       ROUND(a.amount, 2) AS actual_amount,
       ROUND(a.amount - p.amount, 2) AS variance
FROM planned AS p
FULL JOIN actual AS a
  ON a.category = p.category
 AND a.period = p.period
ORDER BY period, category;
```

**Expected shape:** One row per category/month in either source.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 5, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, `actual_amount`, and `variance`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 5, expected output: One row per category/month in either source. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
- **Independent verification:** For sql-15 Exercise 5, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, `actual_amount`, and `variance` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
- **Intermediate relation check:** For sql-15 Exercise 5, run `actual`, and `planned` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-15 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, and `budgets`, preserve one row per `category`, and finish with `category`, `period`, `budget_amount`, `actual_amount`, and `variance` ordered by `period, category`.
- **Alternative/trade-off:** For sql-15 Exercise 5, the chosen form is justified by this lesson-specific rationale: Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero. Evaluate another form against the concrete expected result (One row per category/month in either source) and the verification above.
- **Edge case:** Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.

## Exercise 6 — Extension

**Prompt:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.

**Reasoning:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.

```sql
WITH customer_kpis AS (
  SELECT COUNT(*) AS customers
  FROM customers
), order_kpis AS (
  SELECT COUNT(*) AS orders,
         SUM(total_amount) AS stored_revenue
  FROM orders
), line_kpis AS (
  SELECT SUM(unit_price * quantity * (1 - discount)) AS computed_revenue
  FROM order_items
), payment_kpis AS (
  SELECT SUM(amount) AS payments
  FROM payments
)
SELECT c.customers,
       o.orders,
       ROUND(o.stored_revenue, 2) AS stored_revenue,
       ROUND(l.computed_revenue, 2) AS computed_revenue,
       ROUND(p.payments, 2) AS payments
FROM customer_kpis AS c
CROSS JOIN order_kpis AS o
CROSS JOIN line_kpis AS l
CROSS JOIN payment_kpis AS p;
```

**Expected shape:** Exactly one summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-15 Exercise 6, expected output: Exactly one summary row. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
- **Independent verification:** For sql-15 Exercise 6, project `customer_id` plus the raw source columns from `customers`, `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `customer_id`, then assert the final `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-15 Exercise 6, run `customer_kpis`, `order_kpis`, `line_kpis`, and `payment_kpis` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-15 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `customers`, `orders`, `order_items`, and `payments`, preserve one row per `customer_id`, and finish with `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
- **Alternative/trade-off:** For sql-15 Exercise 6, the chosen form is justified by this lesson-specific rationale: Compute independent one-row aggregates, then cross join them to avoid detail multiplication. Evaluate another form against the concrete expected result (Exactly one summary row) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
