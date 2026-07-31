# Day 11 solutions — CASE Expressions and Conditional Logic


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day11_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day11_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Searched CASE, Simple CASE, Short-circuit ordering. Its worked-model focus is:
Take a three-tier amount classification and test values just below, exactly at, and just above each boundary. Because CASE stops at the first match, place the most specific or highest-threshold conditions before broader ones.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 1, read from `orders`. Compute `order_id`, `total_amount`, and `order_size` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-11 Exercise 1, expected output: One row per order with exactly one size label. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
- **Independent verification:** For sql-11 Exercise 1, evaluate each of `total_amount`, and `order_size` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-11 Exercise 1, check `o.order_id` before applying the row cap.
- **Clause check:** For sql-11 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve exactly one summary row, and finish with `order_id`, `total_amount`, and `order_size` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-11 Exercise 1, the chosen form is justified by this lesson-specific rationale: Validate boundaries and place the highest threshold first. Evaluate another form against the concrete expected result (One row per order with exactly one size label) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 2, read from `orders`. Compute `paid_like`, `open_orders`, `returned_orders`, and `all_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-11 Exercise 2, expected output: One summary row. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
- **Independent verification:** For sql-11 Exercise 2, evaluate each of `open_orders`, `returned_orders`, and `all_orders` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-11 Exercise 2, count the input rows from `orders`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
- **Clause check:** For sql-11 Exercise 2, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `orders`, preserve exactly one summary row, and finish with `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
- **Alternative/trade-off:** For sql-11 Exercise 2, the chosen form is justified by this lesson-specific rationale: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator. Evaluate another form against the concrete expected result (One summary row) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 3, read from `customers`. Compute `customer_id`, `segment`, and `segment_group` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-11 Exercise 3, expected output: One row per customer with an explicit segment label. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
- **Independent verification:** For sql-11 Exercise 3, evaluate each of `segment`, and `segment_group` in a separate control `SELECT` over `customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-11 Exercise 3, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-11 Exercise 3, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve exactly one summary row, and finish with `customer_id`, `segment`, and `segment_group` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-11 Exercise 3, the chosen form is justified by this lesson-specific rationale: Test `IS NULL` before comparing text values. Evaluate another form against the concrete expected result (One row per customer with an explicit segment label) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `amount`, and `corrected_label`; keep `corrected_label` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-11 Exercise 4, expected output: A value of 500 is labeled high. The final columns are `amount`, and `corrected_label`. The final order is `amount`.
- **Independent verification:** For sql-11 Exercise 4, reselect the returned keys directly from the source; require unique `corrected_label` where the expected grain is one row per key and confirm the projected `amount`, and `corrected_label` against the inline `VALUES` fixture. Add one source row with a new `corrected_label`; verify the result gains exactly one row carrying that `corrected_label` value.
- **Intermediate relation check:** For sql-11 Exercise 4, check `amount` before applying the row cap.
- **Clause check:** For sql-11 Exercise 4, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `corrected_label`, and finish with `amount`, and `corrected_label` ordered by `amount`.
- **Alternative/trade-off:** For sql-11 Exercise 4, the chosen form is justified by this lesson-specific rationale: First-match wins, so specific/high thresholds must precede broader/lower ones. Evaluate another form against the concrete expected result (A value of 500 is labeled high) and the verification above.
- **Edge case:** Add one source row with a new `corrected_label`; verify the result gains exactly one row carrying that `corrected_label` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 5, read from the inline `VALUES` fixture. Build the answer toward `value`, and `value_state`; keep `value` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-11 Exercise 5, expected output: Three rows with text labels. The final columns are `value`, and `value_state`. The final order is `value NULLS FIRST`.
- **Independent verification:** For sql-11 Exercise 5, reselect the returned keys directly from the source; require unique `value` where the expected grain is one row per key and confirm the projected `value`, and `value_state` against the inline `VALUES` fixture. Add one source row with a new `value`; verify the result gains exactly one row carrying that `value` value.
- **Intermediate relation check:** For sql-11 Exercise 5, check `value NULLS FIRST` before applying the row cap.
- **Clause check:** For sql-11 Exercise 5, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `value`, and finish with `value`, and `value_state` ordered by `value NULLS FIRST`.
- **Alternative/trade-off:** For sql-11 Exercise 5, the chosen form is justified by this lesson-specific rationale: All result branches must resolve to a compatible PostgreSQL type. Evaluate another form against the concrete expected result (Three rows with text labels) and the verification above.
- **Edge case:** Add one source row with a new `value`; verify the result gains exactly one row carrying that `value` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 6, read from `payments`. Compute `method`, `method_label`, and `payment_count` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-11 Exercise 6, expected output: One row per payment method and display label. The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
- **Independent verification:** For sql-11 Exercise 6, evaluate each of `payment_count` in a separate control `SELECT` over `payments`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `payment_count` for the existing `method` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-11 Exercise 6, confirm the groups are `method`; then check `p.method` before applying the row cap.
- **Clause check:** For sql-11 Exercise 6, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `payments`, preserve one row per `method`, and finish with `method`, `method_label`, and `payment_count` ordered by `p.method`.
- **Alternative/trade-off:** For sql-11 Exercise 6, the chosen form is justified by this lesson-specific rationale: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels. Evaluate another form against the concrete expected result (One row per payment method and display label) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `payment_count` for the existing `method` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
