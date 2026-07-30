# Day 02 solutions — Aggregations, GROUP BY, HAVING, Grouping Sets

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

## Exercise 1 — Query writing

**Prompt:** Count customers by country and order countries by count then country.

**Reasoning:** The output grain is one row per country; include a deterministic secondary sort.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.country,
       COUNT(*) AS customer_count
FROM customers AS c
GROUP BY c.country
ORDER BY customer_count DESC, c.country;
```

**Expected shape:** One row per country.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

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
SELECT p.category,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
       ROUND(AVG(oi.unit_price), 2) AS average_unit_price
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) > 100000
ORDER BY net_revenue DESC, p.category;
```

**Expected shape:** One row per qualifying category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Summarize order count and average total by status, retaining statuses with at least 100 orders.

**Reasoning:** Filter groups after aggregation with `HAVING COUNT(*)`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.status,
       COUNT(*) AS order_count,
       ROUND(AVG(o.total_amount), 2) AS average_order_total
FROM orders AS o
GROUP BY o.status
HAVING COUNT(*) >= 100
ORDER BY order_count DESC, o.status;
```

**Expected shape:** One row per qualifying order status.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.

**Reasoning:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) AS all_rows,
       COUNT(c.email) AS nonnull_email_rows,
       COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_rows
FROM customers AS c;
```

**Expected shape:** One row; present plus missing equals total.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.

**Reasoning:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.category,
       ROUND(SUM(e.amount), 2) AS total_expense
FROM expenses AS e
GROUP BY e.category
HAVING SUM(e.amount) > 1000000
ORDER BY total_expense DESC, e.category;
```

**Expected shape:** One row per expense category over the threshold.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

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
SELECT date_trunc('month', o.order_date)::date AS order_month,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS order_revenue,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders
FROM orders AS o
WHERE o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'
GROUP BY date_trunc('month', o.order_date)
ORDER BY order_month;
```

**Expected shape:** Up to 12 month rows in chronological order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
