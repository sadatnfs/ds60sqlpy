# Day 11 solutions: CASE Expressions and Conditional Logic

<!-- beginner-solution-enrichment -->
## How to study and run this solution

These answers use `CASE` three ways: to label each row (Exercises 1 and 3), to count inside one aggregate row (Exercise 2) and to map codes to display names (Exercise 6). Exercises 4 and 5 run on tiny `VALUES` lists so you can see branch order and branch types without any table. Try them yourself first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day11_solutions.sql
```

The six results have 4,362, 1, 500, 3, 3 and 4 rows. The script only reads data and ends with `ROLLBACK`; the snippets below omit its `SET search_path` line. They match [the learner file](../day11_case_expressions.sql) exercise for exercise, and the study guide explains [how to learn from a finished answer](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
- **Assumptions:** Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
- **Primary pitfall:** Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
- **Safety:** read-only; four queries read `orders`, `customers` and `payments`, two read inline `VALUES`, and the transaction ends in `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Classify orders as small, medium, or large by total amount.

**Reasoning:** Validate boundaries and place the highest threshold first.

**Clause-by-clause reading:**

- `FROM orders AS o`: 4,362 orders, one row each, no grouping.
- `CASE WHEN o.total_amount >= 500 THEN 'large' WHEN o.total_amount >= 100 THEN 'medium' ELSE 'small' END`: tested top to bottom; an order of 503.35 stops at the first branch.
- `AS order_size`: the label column added beside each order.
- `ORDER BY o.order_id`: one row per order in ID order.

```sql
SELECT
  o.order_id,
  o.total_amount,
  CASE WHEN o.total_amount >= 500 THEN
    'large'
  WHEN o.total_amount >= 100 THEN
    'medium'
  ELSE
    'small'
  END AS order_size
FROM
  orders AS o
ORDER BY
  o.order_id;
```

**Expected shape:** One row per order with exactly one size label.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 1, read from `orders` and label every order with a searched `CASE`: `large` when `total_amount >= 500`, `medium` when it is at least 100, otherwise `small`; no `GROUP BY` is needed.
- **Expected result/shape:** For sql-11 Exercise 1, return 4,362 rows, one per order, each with exactly one label; order 1 (240.20) is `medium`, order 3 (601.73) is `large`, and order 5 (105.84) is `medium`. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
- **Independent verification:** For sql-11 Exercise 1, confirm 4362 rows, one per `order_id`, and that counting the labels gives 2410 `large`, 1603 `medium`, and 349 `small`; then evaluate the same `CASE` on `VALUES (99.99), (100), (499.99), (500)` and expect `small`, `medium`, `medium`, and `large`.
- **Label counts:** 2,410 `large` (503.35 to 1,432.49), 1,603 `medium` (102.14 to 499.20) and 349 `small` (20.74 to 98.44). They add to 4,362.
- **Boundaries the data never tests:** no order costs exactly 100 or 500, so `>` and `>=` give the same counts here. Only the four `VALUES` test values prove the rule is right.
- **Why the order matters:** swap the first two branches and every order of 100 or more becomes `medium`; `large` would disappear.
- **A `NULL` total:** every comparison would be unknown and the order would fall to `ELSE 'small'`. A nullable column needs its own `WHEN o.total_amount IS NULL` branch placed first.

## Exercise 2: Query writing

**Prompt:** Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.

**Reasoning:** Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.

**Clause-by-clause reading:**

- `COUNT(*) FILTER (WHERE o.status IN ('paid', 'shipped', 'delivered')) AS paid_like`: orders whose payment has gone through.
- `COUNT(*) FILTER (WHERE o.status = 'placed') AS open_orders` and the `returned` count: one status each.
- `COUNT(*) AS all_orders`: the denominator, with no filter.
- No `GROUP BY`: the whole table is one group, so the result is one row.

```sql
SELECT
  COUNT(*) FILTER (WHERE o.status IN ('paid', 'shipped', 'delivered')) AS paid_like,
  COUNT(*) FILTER (WHERE o.status = 'placed') AS open_orders,
  COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
  COUNT(*) AS all_orders
FROM
  orders AS o;
```

**Expected shape:** One summary row.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 2, count the 4,362 `orders` rows four ways in one pass with `COUNT(*) FILTER (WHERE ...)`: `paid`, `shipped`, or `delivered` as `paid_like`, `placed` as `open_orders`, `returned` as `returned_orders`, and all rows as `all_orders`.
- **Expected result/shape:** For sql-11 Exercise 2, return one row: `paid_like` 2617, `open_orders` 873, `returned_orders` 872, and `all_orders` 4362. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
- **Independent verification:** For sql-11 Exercise 2, confirm `GROUP BY status` returns shipped 873, paid 872, and delivered 872 (adding up to 2617), placed 873, and returned 872, and that the three filtered counts add up to `all_orders`. Inside a rolled-back transaction, set order 1 from `paid` to `cancelled`; `paid_like` must drop to 2616 while `all_orders` stays 4362.
- **What prints:** one row: 2,617 paid-like, 873 open, 872 returned and 4,362 in all.
- **The buckets are complete:** 2,617 + 873 + 872 = 4,362, so no status falls outside the three buckets. A future status such as `cancelled` would show up as a gap between the sum and `all_orders`.
- **`FILTER` versus `SUM(CASE ...)`:** `SUM(CASE WHEN o.status = 'placed' THEN 1 ELSE 0 END)` gives the same 873. Dropping the `ELSE 0` still gives 873, because `SUM` skips `NULL`s, but a status with no orders would then show `NULL` instead of 0.
- **One pass, several counts:** four `GROUP BY status` rows would carry the same information, but this layout puts the buckets side by side for a dashboard.

## Exercise 3: Query writing

**Prompt:** Label missing customer segments separately from known segment values.

**Reasoning:** Test `IS NULL` before comparing text values.

**Clause-by-clause reading:**

- `CASE WHEN c.segment IS NULL THEN 'missing'`: checked first, so a missing segment never reaches the text comparisons.
- `WHEN c.segment IN ('gold', 'platinum') THEN 'premium'`: the two top tiers.
- `ELSE 'core'`: everything else, which in this fixture means `silver` and `standard`.
- `ORDER BY c.customer_id`: one row per customer.

```sql
SELECT
  c.customer_id,
  c.segment,
  CASE WHEN c.segment IS NULL THEN
    'missing'
  WHEN c.segment IN ('gold', 'platinum') THEN
    'premium'
  ELSE
    'core'
  END AS segment_group
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with an explicit segment label.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 3, read from `customers` and label each `segment` as `missing` when it is NULL, `premium` for `gold` or `platinum`, and `core` otherwise; return one row per customer.
- **Expected result/shape:** For sql-11 Exercise 3, return 500 rows, one per customer: customer 1 (`standard`) and customer 2 (`silver`) map to `core`, customer 3 (`gold`) and customer 4 (`platinum`) map to `premium`. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
- **Independent verification:** For sql-11 Exercise 3, confirm 500 rows, one per `customer_id`; the seed gives 250 `premium` and 250 `core` rows and no `missing` row because every seeded customer has a segment. In a transaction you roll back, set one `segment` to NULL and confirm that customer becomes `missing`, not `core`.
- **What prints:** 500 rows: 250 `premium` and 250 `core`. Each of the four segments has 125 customers, and none is `NULL`, so `missing` never appears.
- **Why `IS NULL` comes first:** if `ELSE 'core'` caught a `NULL` segment, a customer with no recorded tier would be reported as a known core customer.
- **Why not a simple CASE:** `CASE c.segment WHEN NULL THEN 'missing'` compares with `=` and never matches, so it would silently label missing segments `core`.
- **Checking the test:** inside a transaction you roll back, set one customer's `segment` to `NULL`; one `missing` row appears and either `premium` or `core` drops to 249.

## Exercise 4: Prediction

**Prompt:** Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.

**Reasoning:** First-match wins, so specific/high thresholds must precede broader/lower ones.

**Clause-by-clause reading:**

- `FROM (VALUES (50::numeric), (100::numeric), (500::numeric)) AS sample (amount)`: three test amounts, one on each side of the thresholds.
- `CASE WHEN amount >= 500 THEN 'high' WHEN amount >= 100 THEN 'medium' ELSE 'low' END`: the repaired order, highest threshold first.
- `ORDER BY amount`: smallest test value first.

```sql
SELECT
  amount,
  CASE WHEN amount >= 500 THEN
    'high'
  WHEN amount >= 100 THEN
    'medium'
  ELSE
    'low'
  END AS corrected_label
FROM (
  VALUES (50::numeric),
    (100::numeric),
    (500::numeric)) AS sample (amount)
ORDER BY
  amount;
```

**Expected shape:** A value of 500 is labeled high.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 4, label the three amounts in the inline `VALUES (50), (100), (500)` fixture with a searched `CASE` that tests `amount >= 500` before `amount >= 100`, so the first matching branch is the most specific.
- **Expected result/shape:** For sql-11 Exercise 4, return 3 rows: 50 is `low`, 100 is `medium`, and 500 is `high`. The final columns are `amount`, and `corrected_label`. The final order is `amount`.
- **Independent verification:** For sql-11 Exercise 4, confirm the 3 labels above, then swap the two `WHEN` branches so `amount >= 100` is tested first; 500 must come back as `medium`, which is the bug being corrected. Add `499.99` and `99.99` to the fixture; the corrected `CASE` must return `medium` and `low`.
- **What prints:** 50 `low`, 100 `medium`, 500 `high`.
- **The broken version:** with `>= 100` first, 500 matches that branch and prints `medium`; the `high` branch is unreachable for every input.
- **Why these three values:** 100 and 500 sit exactly on the thresholds, which is where a branch-order or `>`/`>=` mistake shows; 50 checks the `ELSE`.
- **No table needed:** `VALUES` builds the test rows in the query itself, so the check runs the same on any database.
- **Closed ranges instead:** `WHEN amount >= 100 AND amount < 500 THEN 'medium'` works in any branch position, at the cost of writing each threshold twice; a typo in one copy leaves a gap or an overlap.
- **On the real table:** the corrected rule over `orders.total_amount` gives 2,410 `high`, 1,603 `medium` and 349 `low`, the Exercise 1 counts under different names.

## Exercise 5: Debugging

**Prompt:** Replace a CASE expression that returns mixed numeric and text types with one consistent output type.

**Reasoning:** All result branches must resolve to a compatible PostgreSQL type.

**Clause-by-clause reading:**

- `FROM (VALUES (NULL::integer), (0), (2)) AS sample (value)`: a missing value, a zero and an ordinary number. The `::integer` on the first row sets the column type.
- `CASE WHEN value IS NULL THEN 'missing' WHEN value = 0 THEN 'zero' ELSE 'nonzero' END`: every branch returns text.
- `ORDER BY value NULLS FIRST`: the `NULL` row first, then 0 and 2.

```sql
SELECT
  value,
  CASE WHEN value IS NULL THEN
    'missing'
  WHEN value = 0 THEN
    'zero'
  ELSE
    'nonzero'
  END AS value_state
FROM (
  VALUES (NULL::integer),
    (0),
    (2)) AS sample (value)
ORDER BY
  value NULLS FIRST;
```

**Expected shape:** Three rows with text labels.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 5, classify the three values in the inline `VALUES (NULL::integer), (0), (2)` fixture with a `CASE` whose first branch is `value IS NULL`.
- **Expected result/shape:** For sql-11 Exercise 5, return 3 rows: `NULL` is `missing`, 0 is `zero`, and 2 is `nonzero`, with the `NULL` row first. The final columns are `value`, and `value_state`. The final order is `value NULLS FIRST`.
- **Independent verification:** For sql-11 Exercise 5, confirm 3 rows with three different `value_state` labels. Remove the `IS NULL` branch and the `NULL` row must fall through to `ELSE` as `nonzero`, because `NULL = 0` is unknown rather than true; drop `NULLS FIRST` and the `NULL` row must sort last.
- **What prints:** three rows: `missing` for the `NULL`, `zero` for 0 and `nonzero` for 2.
- **The broken version:** mixing `'missing'` with an integer branch fails with `invalid input syntax for type integer: "missing"`, because PostgreSQL picks integer as the result type and tries to convert the text.
- **Casting does not help:** `'missing'::text` alongside integers gives `CASE types integer and text cannot be matched`. Return text from every branch, or `value::text` if the number itself should show.
- **Zero is not missing:** the `IS NULL` branch comes first and `value = 0` second, so 0 is never reported as absent.
- **Why `NULLS FIRST`:** ascending order puts `NULL` last by default in PostgreSQL, so the clause lifts the `missing` row to the top where it is easy to spot.
- **Showing the number:** `ELSE value::text` would print `2` instead of `nonzero`; the column stays text, so the branch types still agree.

## Exercise 6: Extension

**Prompt:** Create payment-method display labels and preserve unknown future methods with an explicit fallback.

**Reasoning:** A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.

**Clause-by-clause reading:**

- `CASE p.method WHEN 'card' THEN 'Card' WHEN 'paypal' THEN 'PayPal' ... ELSE 'Other' END`: a simple CASE, one equality test per code.
- `COUNT(*) AS payment_count` with `GROUP BY p.method`: payments per method.
- `method_label` is not in `GROUP BY`, which is allowed because it depends only on the grouped `p.method`.
- `ORDER BY p.method`: alphabetical by code.

```sql
SELECT
  p.method,
  CASE p.method
  WHEN 'card' THEN
    'Card'
  WHEN 'paypal' THEN
    'PayPal'
  WHEN 'bank' THEN
    'Bank transfer'
  WHEN 'credit' THEN
    'Store credit'
  ELSE
    'Other'
  END AS method_label,
  COUNT(*) AS payment_count
FROM
  payments AS p
GROUP BY
  p.method
ORDER BY
  p.method;
```

**Expected shape:** One row per payment method and display label.

### Reasoning and verification

- **Inputs/evidence:** For sql-11 Exercise 6, read from `payments`, group by `method`, count payments per method, and map each method to a display label with a simple `CASE p.method WHEN ... END` that keeps an `ELSE 'Other'` fallback.
- **Expected result/shape:** For sql-11 Exercise 6, return 4 rows, one per payment method: `bank` as `Bank transfer` (886), `card` as `Card` (860), `credit` as `Store credit` (1050), and `paypal` as `PayPal` (1040). The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
- **Independent verification:** For sql-11 Exercise 6, confirm 4 rows (`bank` 886, `card` 860, `credit` 1050, `paypal` 1040) whose counts add up to `SELECT COUNT(*) FROM payments` (3836); then evaluate the same `CASE` on `VALUES ('crypto')` and confirm it returns `Other`, not NULL.
- **What prints:** four rows: `bank` (Bank transfer) 886, `card` (Card) 860, `credit` (Store credit) 1,050 and `paypal` (PayPal) 1,040.
- **Totals:** 886 + 860 + 1,050 + 1,040 = 3,836, every payment counted once.
- **The fallback:** `CASE 'crypto' WHEN 'card' THEN 'Card' ... ELSE 'Other' END` returns `Other`. Without the `ELSE`, a new method would display as a blank label.
- **Simple or searched:** a lookup of exact codes reads best as a simple CASE; ranges or `NULL` tests need the searched form.

## Final self-check

- In Example 1, why are all 50 labels `XL`, and what happens if the `>= 300` branch moves to the top?
- Why does Exercise 2's first three counts adding to 4,362 matter?
- Why must the `IS NULL` test come first in Exercise 3?
- Which two different errors can mixed branch types raise in Exercise 5?
- What would Exercise 6 print for a new method if the `ELSE` were removed?
