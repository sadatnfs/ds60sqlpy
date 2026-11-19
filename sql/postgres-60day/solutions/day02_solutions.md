# Day 02 solutions: Aggregations, GROUP BY, HAVING, Grouping Sets


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day02_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Aggregate, Group grain, Grouping set. Its worked-model focus is:
In the category-revenue query, first identify one joined row as an order line. Next group those rows by product category, calculate the revenue aggregate, and only then apply `HAVING`. Compare that flow with a date predicate in `WHERE`, which removes rows before the category totals are computed.

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

These answers align one-for-one with [day02_aggregates_groupby_having.sql](../day02_aggregates_groupby_having.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
- **Assumptions:** Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
- **Primary pitfall:** Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Count customers by country and order countries by count then country.

**Reasoning:** The output grain is one row per country; include a deterministic secondary sort.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT
  c.country,
  COUNT(*) AS customer_count
FROM
  customers AS c
GROUP BY
  c.country
ORDER BY
  customer_count DESC,
  c.country;
```

**Expected shape:** One row per country.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 1, read from `customers`. Build the answer toward `country`, and `customer_count`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-02 Exercise 1, expected output: One row per country. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
- **Independent verification:** For sql-02 Exercise 1, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-02 Exercise 1, confirm the groups are `country`; then check `customer_count DESC, c.country` before applying the row cap.
- **Clause check:** For sql-02 Exercise 1, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `country`, and finish with `country`, and `customer_count` ordered by `customer_count DESC, c.country`.
- **Alternative/trade-off:** For sql-02 Exercise 1, the chosen form is justified by this lesson-specific rationale: The output grain is one row per country; include a deterministic secondary sort. Evaluate another form against the concrete expected result (One row per country) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `country` tuple and verify the new tuple appears exactly once.

## Exercise 2: Query writing

**Prompt:** Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.

**Reasoning:** Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
  ROUND(AVG(oi.unit_price), 2) AS average_unit_price
FROM
  order_items AS oi
  JOIN products AS p ON p.product_id = oi.product_id
GROUP BY
  p.category
HAVING
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) > 100000
ORDER BY
  net_revenue DESC,
  p.category;
```

**Expected shape:** One row per qualifying category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 2, read from `order_items`, and `products`. Build the answer toward `category`, `net_revenue`, and `average_unit_price`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-02 Exercise 2, expected output: One row per qualifying category. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
- **Independent verification:** For sql-02 Exercise 2, independently aggregate `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `net_revenue`, and `average_unit_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue`, and `average_unit_price` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-02 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `category` so the exact fanout or loss is visible.
- **Clause check:** For sql-02 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, and `products`, preserve one row per `category`, and finish with `category`, `net_revenue`, and `average_unit_price` ordered by `net_revenue DESC, p.category`.
- **Alternative/trade-off:** For sql-02 Exercise 2, the chosen form is justified by this lesson-specific rationale: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`. Evaluate another form against the concrete expected result (One row per qualifying category) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `net_revenue`, and `average_unit_price` for the existing `category` tuple and verify the new tuple appears exactly once.

## Exercise 3: Query writing

**Prompt:** Summarize order count and average total by status, retaining statuses with at least 100 orders.

**Reasoning:** Filter groups after aggregation with `HAVING COUNT(*)`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT
  o.status,
  COUNT(*) AS order_count,
  ROUND(AVG(o.total_amount), 2) AS average_order_total
FROM
  orders AS o
GROUP BY
  o.status
HAVING
  COUNT(*) >= 100
ORDER BY
  order_count DESC,
  o.status;
```

**Expected shape:** One row per qualifying order status.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 3, read from `orders`. Build the answer toward `status`, `order_count`, and `average_order_total`; keep `status` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-02 Exercise 3, expected output: One row per qualifying order status. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
- **Independent verification:** For sql-02 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `average_order_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `average_order_total` for the existing `status` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-02 Exercise 3, confirm the groups are `status`; then check `order_count DESC, o.status` before applying the row cap.
- **Clause check:** For sql-02 Exercise 3, the solution actually uses `FROM`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `status`, and finish with `status`, `order_count`, and `average_order_total` ordered by `order_count DESC, o.status`.
- **Alternative/trade-off:** For sql-02 Exercise 3, the chosen form is justified by this lesson-specific rationale: Filter groups after aggregation with `HAVING COUNT(*)`. Evaluate another form against the concrete expected result (One row per qualifying order status) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `order_count`, and `average_order_total` for the existing `status` tuple and verify the new tuple appears exactly once.

## Exercise 4: Prediction

**Prompt:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.

**Reasoning:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT
  COUNT(*) AS all_rows,
  COUNT(c.email) AS nonnull_email_rows,
  COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_rows
FROM
  customers AS c;
```

**Expected shape:** One row; present plus missing equals total.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 4, read from `customers` and count, in one aggregate query, all rows as `all_rows`, rows with a non-null `email` as `nonnull_email_rows`, and rows whose `email` is NULL as `missing_email_rows`.
- **Expected result/shape:** For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
- **Independent verification:** For sql-02 Exercise 4, confirm `nonnull_email_rows + missing_email_rows = all_rows`; the seed returns 500, 500, and 0 because every seeded customer has an email. In a transaction you roll back, set one customer's `email` to NULL and rerun: expect 500, 499, and 1.
- **Intermediate relation check:** For sql-02 Exercise 4, write `COUNT(*)` and `COUNT(email)` first and compare them; their difference is the number of NULL emails.
- **Clause check:** For sql-02 Exercise 4, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `customers`, preserve exactly one summary row, and finish with `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
- **Alternative/trade-off:** For sql-02 Exercise 4, the chosen form is justified by this lesson-specific rationale: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit. Evaluate another form against the concrete expected result (One row; present plus missing equals total) and the verification above.
- **Edge case:** `COUNT(email)` skips NULL, so a NULL email lowers `nonnull_email_rows` but not `all_rows`; `COUNT(*) FILTER (WHERE email IS NULL)` counts the missing rows explicitly.

## Exercise 5: Debugging

**Prompt:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.

**Reasoning:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT
  e.category,
  ROUND(SUM(e.amount), 2) AS total_expense
FROM
  expenses AS e
GROUP BY
  e.category
HAVING
  SUM(e.amount) > 1000000
ORDER BY
  total_expense DESC,
  e.category;
```

**Expected shape:** One row per expense category over the threshold.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 5, read from `expenses`. Build the answer toward `category`, and `total_expense`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-02 Exercise 5, expected output: One row per expense category over the threshold. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
- **Independent verification:** For sql-02 Exercise 5, independently aggregate `expenses` by `category`; require one output row for every distinct `category` tuple and compare `total_expense` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `total_expense` for the existing `category` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-02 Exercise 5, confirm the groups are `category`; then check `total_expense DESC, e.category` before applying the row cap.
- **Clause check:** For sql-02 Exercise 5, the solution actually uses `FROM`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, preserve one row per `category`, and finish with `category`, and `total_expense` ordered by `total_expense DESC, e.category`.
- **Alternative/trade-off:** For sql-02 Exercise 5, the chosen form is justified by this lesson-specific rationale: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward. Evaluate another form against the concrete expected result (One row per expense category over the threshold) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `total_expense` for the existing `category` tuple and verify the new tuple appears exactly once.

## Exercise 6: Extension

**Prompt:** Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.

**Reasoning:** Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT
  date_trunc('month', o.order_date)::date AS order_month,
  COUNT(*) AS order_count,
  ROUND(SUM(o.total_amount), 2) AS order_revenue,
  COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders
FROM
  orders AS o
WHERE
  o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'
GROUP BY
  date_trunc('month', o.order_date)
ORDER BY
  order_month;
```

**Expected shape:** Up to 12 month rows in chronological order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-02 Exercise 6, read from `orders` placed on or after `date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`, group them by `date_trunc('month', order_date)`, and return each month's order count, summed `total_amount`, and count of `returned` orders.
- **Expected result/shape:** For sql-02 Exercise 6, expected output: Up to 12 month rows in chronological order. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
- **Independent verification:** For sql-02 Exercise 6, confirm that `order_month` values are unique and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`; for one month, recount its `returned` orders directly and compare the result with `returned_orders`.
- **Intermediate relation check:** For sql-02 Exercise 6, run the `WHERE` filter alone and check the earliest `order_date` it keeps before you group by month.
- **Clause check:** For sql-02 Exercise 6, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_month`, and finish with `order_month`, `order_count`, `order_revenue`, and `returned_orders` ordered by `order_month`.
- **Alternative/trade-off:** For sql-02 Exercise 6, the chosen form is justified by this lesson-specific rationale: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable. Evaluate another form against the concrete expected result (Up to 12 month rows in chronological order) and the verification above.
- **Edge case:** The window starts on the first day of the month eleven months ago, so the current, partial month is included; at most 12 rows appear, and a month without orders is absent rather than shown with zero.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
