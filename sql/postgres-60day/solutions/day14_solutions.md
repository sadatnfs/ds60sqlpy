# Day 14 solutions — Numeric Types, Casting, and Precision

These answers align one-for-one with [day14_numeric_and_casting.sql](../day14_numeric_and_casting.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Primary pitfall:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.

**Reasoning:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.price,
       p.cost,
       p.price - p.cost AS margin_amount,
       ROUND((p.price - p.cost) / NULLIF(p.price, 0), 4) AS margin_rate
FROM products AS p
ORDER BY margin_rate DESC NULLS LAST, p.product_id;
```

**Expected shape:** One row per product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Safely cast a set of text values to numeric only when they match a numeric grammar.

**Reasoning:** Validate with a regex before casting; otherwise return NULL.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.

```sql
SELECT raw_value,
       CASE
         WHEN btrim(raw_value) ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
           THEN btrim(raw_value)::numeric
         ELSE NULL
       END AS parsed_numeric
FROM (VALUES ('42'), (' 3.14 '), ('-0.5'), ('many'), ('')) AS sample(raw_value);
```

**Expected shape:** One row per sample text.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Show order-item net revenue rounded only after summing.

**Reasoning:** Aggregate exact line expressions first; round the final display value.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT oi.order_id,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_order_revenue
FROM order_items AS oi
GROUP BY oi.order_id
ORDER BY oi.order_id;
```

**Expected shape:** One row per order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Compare integer division with numeric division for 1 divided by 4.

**Reasoning:** At least one operand must be numeric to preserve the fraction.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.

```sql
SELECT 1 / 4 AS integer_division,
       1::numeric / 4 AS numeric_division;
```

**Expected shape:** One row showing 0 and 0.25.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.

**Reasoning:** Aggregate payment amount and count distinct order IDs at one common scope.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.

```sql
SELECT ROUND(
         SUM(p.amount) / NULLIF(COUNT(DISTINCT p.order_id), 0),
         2
       ) AS average_paid_amount_per_order
FROM payments AS p;
```

**Expected shape:** Exactly one summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.

**Reasoning:** This diagnostic makes the consequence of early rounding visible.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.

```sql
SELECT SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2)) AS sum_of_rounded_lines,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS rounded_exact_total,
       SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2))
         - ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2)
         AS rounding_difference
FROM order_items AS oi;
```

**Expected shape:** One row with two totals and their signed difference.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
