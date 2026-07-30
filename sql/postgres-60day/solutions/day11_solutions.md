# Day 11 solutions — CASE Expressions and Conditional Logic

These answers align one-for-one with [day11_case_expressions.sql](../day11_case_expressions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
- **Assumptions:** Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
- **Primary pitfall:** Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Classify orders as small, medium, or large by total amount.

**Reasoning:** Validate boundaries and place the highest threshold first.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT o.order_id,
       o.total_amount,
       CASE
         WHEN o.total_amount >= 500 THEN 'large'
         WHEN o.total_amount >= 100 THEN 'medium'
         ELSE 'small'
       END AS order_size
FROM orders AS o
ORDER BY o.order_id;
```

**Expected shape:** One row per order with exactly one size label.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.

**Reasoning:** Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) FILTER (WHERE o.status IN ('paid', 'shipped', 'delivered')) AS paid_like,
       COUNT(*) FILTER (WHERE o.status = 'placed') AS open_orders,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
       COUNT(*) AS all_orders
FROM orders AS o;
```

**Expected shape:** One summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Label missing customer segments separately from known segment values.

**Reasoning:** Test `IS NULL` before comparing text values.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.segment,
       CASE
         WHEN c.segment IS NULL THEN 'missing'
         WHEN c.segment IN ('gold', 'platinum') THEN 'premium'
         ELSE 'core'
       END AS segment_group
FROM customers AS c
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer with an explicit segment label.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.

**Reasoning:** First-match wins, so specific/high thresholds must precede broader/lower ones.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT amount,
       CASE
         WHEN amount >= 500 THEN 'high'
         WHEN amount >= 100 THEN 'medium'
         ELSE 'low'
       END AS corrected_label
FROM (VALUES (50::numeric), (100::numeric), (500::numeric)) AS sample(amount)
ORDER BY amount;
```

**Expected shape:** A value of 500 is labeled high.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Replace a CASE expression that returns mixed numeric and text types with one consistent output type.

**Reasoning:** All result branches must resolve to a compatible PostgreSQL type.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT value,
       CASE
         WHEN value IS NULL THEN 'missing'
         WHEN value = 0 THEN 'zero'
         ELSE 'nonzero'
       END AS value_state
FROM (VALUES (NULL::integer), (0), (2)) AS sample(value)
ORDER BY value NULLS FIRST;
```

**Expected shape:** Three rows with text labels.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Create payment-method display labels and preserve unknown future methods with an explicit fallback.

**Reasoning:** A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.method,
       CASE p.method
         WHEN 'card' THEN 'Card'
         WHEN 'paypal' THEN 'PayPal'
         WHEN 'bank' THEN 'Bank transfer'
         WHEN 'credit' THEN 'Store credit'
         ELSE 'Other'
       END AS method_label,
       COUNT(*) AS payment_count
FROM payments AS p
GROUP BY p.method
ORDER BY p.method;
```

**Expected shape:** One row per payment method and display label.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
