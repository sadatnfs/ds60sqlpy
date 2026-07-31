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

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Classify orders as small, medium, or large by total amount” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `small`, `evidence`, `order_size`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: Classify orders as small, medium, or large by total amount. Why: Validate boundaries and place the highest threshold first. Expected: One row per order with exactly one size label. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `paid_like`, `open_orders`, `returned_orders`, `all_orders`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation. Why: Each COUNT() FILTER or SUM(CASE...) should state its denominator. Expected: One summary row. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - FILTER (WHERE ...): limits one aggregate without removing rows needed by neighboring aggregates.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Label missing customer segments separately from known segment values” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `segment_group`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 3: Query writing Prompt: Label missing customer segments separately from known segment values. Why: Test IS NULL before comparing text values. Expected: One row per customer with an explicit segment label. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the label for 500 when >= 100 appears before >= 500, then repair the branch order”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `corrected_label`, `sample`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `orders`, `order_items`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: Prediction Prompt: Predict the label for 500 when >= 100 appears before >= 500, then repair the branch order. Why: First-match wins, so specific/high thresholds must precede broader/lower ones. Expected: A value of 500 is labeled high. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - VALUES: constructs a small relation explicitly, which makes examples and expected cardinality inspectable. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Replace a CASE expression that returns mixed numeric and text types with one consistent output type” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `value_state`, `sample`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 5: Debugging Prompt: Replace a CASE expression that returns mixed numeric and text types with one consistent output type. Why: All result branches must resolve to a compatible PostgreSQL type. Expected: Three rows with text labels. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - VALUES: constructs a small relation explicitly, which makes examples and expected cardinality inspectable. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 6 must make “Extension: Create payment-method display labels and preserve unknown future methods with an explicit fallback” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `method_label`, `payment_count`, `p`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `method_label`, `payment_count`, `p`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Create payment-method display labels and preserve unknown future methods with an explicit fallback. Why: A simple CASE fits equality mapping; ELSE prevents silent NULL labels. Expected: One row per payment method and display label. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
