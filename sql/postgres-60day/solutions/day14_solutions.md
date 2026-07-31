# Day 14 solutions — Numeric Types, Casting, and Precision


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day14_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day14_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Exact numeric, Scale, Type coercion. Its worked-model focus is:
Evaluate 1 / 3, 1::numeric / 3, and ROUND(1::numeric / NULLIF(3, 0), 2). Explain the result type at each step and why guarding the denominator belongs before rounding.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 1, read from `products`. Build the answer toward `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`; keep `product_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-14 Exercise 1, expected output: One row per product. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
- **Independent verification:** For sql-14 Exercise 1, reselect the returned keys directly from the source; require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate` against `products`. Repeat with `NULL` in `product_id`, and `price` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-14 Exercise 1, check `margin_rate DESC NULLS LAST, p.product_id` before applying the row cap.
- **Clause check:** For sql-14 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `products`, preserve one row per `product_id`, and finish with `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate` ordered by `margin_rate DESC NULLS LAST, p.product_id`.
- **Alternative/trade-off:** For sql-14 Exercise 1, the chosen form is justified by this lesson-specific rationale: Keep exact numeric arithmetic and guard the denominator with `NULLIF`. Evaluate another form against the concrete expected result (One row per product) and the verification above.
- **Edge case:** Repeat with `NULL` in `product_id`, and `price` and state whether the row is kept, rejected, or classified.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 2, read from the inline `VALUES` fixture. Build the answer toward `raw_value`, and `parsed_numeric`; keep `parsed_numeric` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-14 Exercise 2, expected output: One row per sample text. The final columns are `raw_value`, and `parsed_numeric`.
- **Independent verification:** For sql-14 Exercise 2, reselect the returned keys directly from the source; require unique `parsed_numeric` where the expected grain is one row per key and confirm the projected `raw_value`, and `parsed_numeric` against the inline `VALUES` fixture. Add one source row with a new `parsed_numeric`; verify the result gains exactly one row carrying that `parsed_numeric` value.
- **Intermediate relation check:** For sql-14 Exercise 2, select `parsed_numeric` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-14 Exercise 2, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `parsed_numeric`, and finish with `raw_value`, and `parsed_numeric`.
- **Alternative/trade-off:** For sql-14 Exercise 2, the chosen form is justified by this lesson-specific rationale: Validate with a regex before casting; otherwise return NULL. Evaluate another form against the concrete expected result (One row per sample text) and the verification above.
- **Edge case:** Add one source row with a new `parsed_numeric`; verify the result gains exactly one row carrying that `parsed_numeric` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 3, read from `order_items`. Build the answer toward `order_id`, and `net_order_revenue`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-14 Exercise 3, expected output: One row per order. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
- **Independent verification:** For sql-14 Exercise 3, independently aggregate `order_items` by `order_id`; require one output row for every distinct `order_id` tuple and compare `net_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_order_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-14 Exercise 3, confirm the groups are `order_id`; then check `oi.order_id` before applying the row cap.
- **Clause check:** For sql-14 Exercise 3, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, preserve one row per `order_id`, and finish with `order_id`, and `net_order_revenue` ordered by `oi.order_id`.
- **Alternative/trade-off:** For sql-14 Exercise 3, the chosen form is justified by this lesson-specific rationale: Aggregate exact line expressions first; round the final display value. Evaluate another form against the concrete expected result (One row per order) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `net_order_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 4, read from `orders`, `order_items`, and `products`. Compute `integer_division`, and `numeric_division` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-14 Exercise 4, expected output: One row showing 0 and 0.25. The final columns are `integer_division`, and `numeric_division`.
- **Independent verification:** For sql-14 Exercise 4, evaluate each of `integer_division`, and `numeric_division` in a separate control `SELECT` over `orders`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-14 Exercise 4, select `order_id` from `orders`, `order_items`, and `products` before adding derived columns.
- **Clause check:** For sql-14 Exercise 4, the solution actually uses `SELECT`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve exactly one summary row, and finish with `integer_division`, and `numeric_division`.
- **Alternative/trade-off:** For sql-14 Exercise 4, the chosen form is justified by this lesson-specific rationale: At least one operand must be numeric to preserve the fraction. Evaluate another form against the concrete expected result (One row showing 0 and 0.25) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 5, read from `payments`. Build the answer toward `average_paid_amount_per_order`; keep `payment_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-14 Exercise 5, expected output: Exactly one summary row. The final columns are `average_paid_amount_per_order`.
- **Independent verification:** For sql-14 Exercise 5, reselect the returned keys directly from the source; require unique `payment_id` where the expected grain is one row per key and confirm the projected `average_paid_amount_per_order` against `payments`. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
- **Intermediate relation check:** For sql-14 Exercise 5, select `payment_id` from `payments` before adding derived columns.
- **Clause check:** For sql-14 Exercise 5, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `payments`, preserve one row per `payment_id`, and finish with `average_paid_amount_per_order`.
- **Alternative/trade-off:** For sql-14 Exercise 5, the chosen form is justified by this lesson-specific rationale: Aggregate payment amount and count distinct order IDs at one common scope. Evaluate another form against the concrete expected result (Exactly one summary row) and the verification above.
- **Edge case:** Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 6, read from `order_items`. Build the answer toward `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`; keep `order_item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-14 Exercise 6, expected output: One row with two totals and their signed difference. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
- **Independent verification:** For sql-14 Exercise 6, reselect the returned keys directly from the source; require unique `order_item_id` where the expected grain is one row per key and confirm the projected `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference` against `order_items`. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
- **Intermediate relation check:** For sql-14 Exercise 6, select `order_item_id` from `order_items` before adding derived columns.
- **Clause check:** For sql-14 Exercise 6, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `order_items`, preserve one row per `order_item_id`, and finish with `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
- **Alternative/trade-off:** For sql-14 Exercise 6, the chosen form is justified by this lesson-specific rationale: This diagnostic makes the consequence of early rounding visible. Evaluate another form against the concrete expected result (One row with two totals and their signed difference) and the verification above.
- **Edge case:** Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
