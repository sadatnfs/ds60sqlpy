# Day 14 solutions: Numeric Types, Casting, and Precision

<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers turn on two questions: what type each expression has, and where the rounding happens. Exercises 1 and 5 guard a denominator, Exercise 2 checks text before casting it, Exercises 3 and 6 decide where `ROUND` goes, and Exercise 4 shows what happens when nothing is cast. Attempt the prompts, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day14_solutions.sql
```

Row counts to expect: 300, 5, 4,362, 1, 1 and 1. Every query only reads, the file closes each block with `ROLLBACK`, and the excerpts leave out the `SET search_path` line. Exercise numbers follow [the learner file](../day14_numeric_and_casting.sql); to compare your answer with these without copying, see the study guide's [solution-comparison tips](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Primary pitfall:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Safety:** read-only; all six statements are `SELECT`s, and each block still ends in `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.

**Reasoning:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.

**Clause-by-clause reading:**

- `p.price - p.cost AS margin_amount`: both columns are `numeric`, so the difference is exact to the cent, 24.80 - 8.68 = 16.12 for product 40.
- `(p.price - p.cost) / NULLIF(p.price, 0)`: numeric division. A price of 0 would make the divisor `NULL` and the rate `NULL` instead of raising `division by zero`.
- `ROUND(..., 4)`: four decimal places, so 0.6500 reads as 65%.
- `ORDER BY margin_rate DESC NULLS LAST, p.product_id`: highest rate first, any `NULL` rate at the bottom, and the product ID to order equal rates.

```sql
SELECT
  p.product_id,
  p.price,
  p.cost,
  p.price - p.cost AS margin_amount,
  ROUND((p.price - p.cost) / NULLIF (p.price, 0), 4) AS margin_rate
FROM
  products AS p
ORDER BY
  margin_rate DESC NULLS LAST,
  p.product_id;
```

**Expected shape:** One row per product.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 1, compute `price - cost` and `ROUND((price - cost) / NULLIF(price, 0), 4)` for each of the 300 `products`; no fixture price is 0 or `NULL`.
- **Expected result/shape:** For sql-14 Exercise 1, return 300 rows, one per product, led by seven products tied at a `margin_rate` of 0.6500 (40, 80, 120, 160, 200, 240, 280, in `product_id` order) and ending with product 83 at 0.2599. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
- **Independent verification:** For sql-14 Exercise 1, confirm 300 distinct `product_id` values and that product 40 shows 24.80 - 8.68 = 16.12 and 16.12 / 24.80 = 0.6500. Inside a rolled-back transaction, set product 40's price to 0; the query must not raise a division error, product 40 must move to row 300 with `margin_amount` -8.68 and a `NULL` `margin_rate`, and product 80 must lead.
- **What prints:** 300 rows. No product has a zero price or a missing cost, so no rate is `NULL`; the guard protects against data that might arrive later.
- **Top and bottom:** seven products share the top rate of 0.6500, starting with product 40 (Beauty, 24.80 against a cost of 8.68), then 80 and 120. The lowest is product 83 (Sports, 40.71 against 30.13) at 0.2599. The mean rate is 0.4530.
- **Rounding merges rates:** the 300 products have 274 distinct raw rates but only 116 after rounding to four places. Products 157, 197, 237 and 277 all print 0.6400 although their raw rates run from 0.640035 to 0.639968, so inside such a group `p.product_id`, not the true rate, sets the order.
- **Percent display:** for a report showing 65.00, compute `ROUND(100 * (p.price - p.cost) / NULLIF(p.price, 0), 2)`. Rounding to two places first and then multiplying turns product 83's 0.2599 into 26%.

## Exercise 2: Query writing

**Prompt:** Safely cast a set of text values to numeric only when they match a numeric grammar.

**Reasoning:** Validate with a regex before casting; otherwise return NULL.

**Clause-by-clause reading:**

- `FROM (VALUES ('42'), (' 3.14 '), ...) AS sample (raw_value)`: builds a five-row table inline, with one `text` column named `raw_value`.
- `btrim(raw_value)`: removes leading and trailing spaces, so `' 3.14 '` is tested and cast as `'3.14'`.
- `~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'`: an optional sign, then digits with an optional decimal part, or a point followed by digits. `^` and `$` force the whole string to match.
- `CASE WHEN ... THEN btrim(raw_value)::numeric ELSE NULL END`: the cast runs only on rows that passed the test.

```sql
SELECT
  raw_value,
  CASE WHEN btrim(raw_value) ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$' THEN
    btrim(raw_value)::numeric
  ELSE
    NULL
  END AS parsed_numeric
FROM (
  VALUES ('42'),
    (' 3.14 '),
    ('-0.5'),
    ('many'),
    ('')) AS sample (raw_value);
```

**Expected shape:** One row per sample text.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 2, test five inline `VALUES` strings (`'42'`, `' 3.14 '`, `'-0.5'`, `'many'`, and the empty string) against `'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'` after `btrim`, casting to `numeric` only when the pattern matches.
- **Expected result/shape:** For sql-14 Exercise 2, return 5 rows in `VALUES` order: 42, 3.14, -0.5, then `NULL` for `many` and `NULL` for the empty string; the query has no `ORDER BY`. The final columns are `raw_value`, and `parsed_numeric`.
- **Independent verification:** For sql-14 Exercise 2, confirm 5 rows with exactly 2 `NULL` values in `parsed_numeric`. Run `SELECT 'many'::numeric` and `SELECT ''::numeric` on their own; both must fail with `invalid input syntax for type numeric`, which the guard avoids. Note that `'1e3'::numeric` succeeds (1000) but the pattern rejects it, so the guard is stricter than the cast.
- **What prints:** five rows: 42, 3.14 and -0.5 are parsed, while `'many'` and the empty string come back `NULL`.
- **Why the `CASE` matters:** `'many'::numeric` on its own raises `invalid input syntax for type numeric: "many"` and stops the statement, so one bad value would hide the three good ones.
- **Stricter than PostgreSQL:** `'1e3'` and `'NaN'` are valid numeric input (1000 and NaN) but fail this pattern and come back `NULL`, as does `'1,234.50'`. The pattern states what this report accepts; `to_number('1,234.50', '9,999.99')` would read the last one as 1234.50.
- **Built-in test:** on PostgreSQL 16 and later, `pg_input_is_valid(btrim(raw_value), 'numeric')` checks castability without a pattern, but it accepts `'1e3'` and `'NaN'`.
- **Empty versus unreadable:** `''` and `'many'` both end up `NULL`. If a report must tell a blank field from a bad one, add a separate flag column.

## Exercise 3: Query writing

**Prompt:** Show order-item net revenue rounded only after summing.

**Reasoning:** Aggregate exact line expressions first; round the final display value.

**Clause-by-clause reading:**

- `oi.unit_price * oi.quantity * (1 - oi.discount)`: one line's net revenue. `numeric` times `integer` times `numeric` stays `numeric` with four decimals, for example 27.76 * 3 * 1.00 = 83.2800.
- `SUM(...)`: adds an order's lines at full precision.
- `ROUND(..., 2)`: rounds once per order, after the sum.
- `GROUP BY oi.order_id` and `ORDER BY oi.order_id`: one row per order, lowest ID first.

```sql
SELECT
  oi.order_id,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_order_revenue
FROM
  order_items AS oi
GROUP BY
  oi.order_id
ORDER BY
  oi.order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 3, sum `unit_price * quantity * (1 - discount)` over the 13,085 `order_items` rows per `order_id` and round each order total to 2 places.
- **Expected result/shape:** For sql-14 Exercise 3, return 4,362 rows, one per order, starting with order 1 at 240.20 (two item lines) and order 2 at 417.94. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
- **Independent verification:** For sql-14 Exercise 3, confirm 4,362 distinct `order_id` values, matching `SELECT COUNT(DISTINCT order_id) FROM order_items`, and 0 rows where `net_order_revenue` differs from `orders.total_amount` after joining on `order_id`; the returned values add up to 2355646.89, the same as `SELECT SUM(total_amount) FROM orders`.
- **What prints:** 4,362 rows, one per order. Orders have one to five lines, with 872 or 873 orders at each size.
- **First rows:** order 1 is 83.28 + 156.92 = 240.20, then order 2 at 417.94 and order 3 at 601.73, which are customer 1's first three order totals.
- **Matches the stored totals:** joined to `orders`, all 4,362 values equal `total_amount` to the cent, so the fixture's totals follow the same rule: add the exact lines, then round once per order.
- **A discounted line:** order 2's third line is 56.99 * 1 * 0.95 = 54.1405. Added exactly to 136.20 and 227.60 it gives 417.9405, which rounds to 417.94. Rounding every line before adding would shift the cents of 156 orders in this table.
- **Discounts:** 9,517 of the 13,085 lines carry no discount, 2,380 take 0.05 and 1,188 take 0.15.
- **A third grand total:** these per-order values add up to 2,355,646.89. Exercise 6 rounds per line and gets 2,355,648.13, or once overall and gets 2,355,647.12. The grain at which you round changes the total.

## Exercise 4: Prediction

**Prompt:** Compare integer division with numeric division for 1 divided by 4.

**Reasoning:** At least one operand must be numeric to preserve the fraction.

**Clause-by-clause reading:**

- `1 / 4 AS integer_division`: two integer literals, so integer division drops the fraction and returns 0.
- `1::numeric / 4 AS numeric_division`: casting one side is enough; the 4 is promoted, the division is numeric and prints 0.25000000000000000000.
- No `FROM`: both columns are constant expressions, so the query returns a single row.

```sql
SELECT
  1 / 4 AS integer_division,
  1::numeric / 4 AS numeric_division;
```

**Expected shape:** One row showing 0 and 0.25.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 4, evaluate the two constant expressions `1 / 4` and `1::numeric / 4` with no `FROM` clause; no table is read.
- **Expected result/shape:** For sql-14 Exercise 4, return one row: `integer_division` 0 and `numeric_division` 0.25000000000000000000. The final columns are `integer_division`, and `numeric_division`.
- **Independent verification:** For sql-14 Exercise 4, confirm one row with 0 and 0.25000000000000000000. Run `SELECT 7 / 2, -7 / 2, 1 / 4.0` and expect 3, -3, and 0.25000000000000000000, which shows integer division truncates toward zero; `SELECT 1 / 0` must fail with `division by zero`.
- **What prints:** one row with 0 and 0.25000000000000000000. `pg_typeof` reports `integer` and `numeric`.
- **No table involved:** without a `FROM`, the result is one row whatever `orders`, `order_items` and `products` contain; adding rows to them leaves the output unchanged.
- **Toward zero, not down:** `7 / 2` is 3 and `-7 / 2` is -3. Integer division truncates toward zero rather than taking the floor.
- **Twenty decimals:** numeric division of small values returns scale 20, for both 1/4 and 1/3. Wrap it in `ROUND` to choose the display scale.
- **`1.0 / 4`:** a literal with a decimal point is already `numeric`, so it gives the same 0.25 without a cast.

## Exercise 5: Debugging

**Prompt:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.

**Reasoning:** Aggregate payment amount and count distinct order IDs at one common scope.

**Clause-by-clause reading:**

- `SUM(p.amount)`: 1,831,900.81 across all 3,836 payment rows.
- `COUNT(DISTINCT p.order_id)`: 3,489 orders; 3,142 were paid in one payment and 347 in two.
- `NULLIF(..., 0)`: an empty `payments` table gives a `NULL` average instead of an error.
- `ROUND(..., 2)`: applied once, to the final ratio.

```sql
SELECT
  ROUND(SUM(p.amount) / NULLIF (COUNT(DISTINCT p.order_id), 0), 2) AS average_paid_amount_per_order
FROM
  payments AS p;
```

**Expected shape:** Exactly one summary row.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 5, read from `payments` and divide the total paid amount by the number of distinct paid orders, `SUM(amount) / NULLIF(COUNT(DISTINCT order_id), 0)`, rounded to 2 places.
- **Expected result/shape:** For sql-14 Exercise 5, return one row, `average_paid_amount_per_order` 525.05. The final columns are `average_paid_amount_per_order`.
- **Independent verification:** For sql-14 Exercise 5, confirm one row with 525.05, which is 1831900.81 divided by 3489 distinct paid orders; compare it with `ROUND(AVG(amount), 2)` (477.55), which divides by the 3836 payment rows instead.
- **What prints:** one row, 525.05.
- **The bug it fixes:** order 10 was paid as 71.72 + 71.71. `AVG(amount)` counts it twice, which is how 3,836 rows produce 477.55 instead of 525.05.
- **Unpaid orders:** 873 orders have no payment row and stay out of the denominator. The question asks per paid order, so that is right; an average over all orders would start from `orders` with a `LEFT JOIN`.
- **Why no cast is needed:** `COUNT` returns `bigint`, but `SUM(amount)` is `numeric`, so the division keeps its fraction. Dividing two counts would not.

## Exercise 6: Extension

**Prompt:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.

**Reasoning:** This diagnostic makes the consequence of early rounding visible.

**Clause-by-clause reading:**

- `SUM(ROUND(line, 2)) AS sum_of_rounded_lines`: rounds each of the 13,085 lines to the cent, then adds.
- `ROUND(SUM(line), 2) AS rounded_exact_total`: adds the exact line values, then rounds once.
- The third column repeats both expressions and subtracts, because a `SELECT` list cannot refer to its own aliases.

```sql
SELECT
  SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2)) AS sum_of_rounded_lines,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS rounded_exact_total,
  SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2)) - ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS rounding_difference
FROM
  order_items AS oi;
```

**Expected shape:** One row with two totals and their signed difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-14 Exercise 6, read from `order_items` and compare the sum of line totals rounded per line, `SUM(ROUND(unit_price * quantity * (1 - discount), 2))`, with the exact sum rounded once, `ROUND(SUM(unit_price * quantity * (1 - discount)), 2)`.
- **Expected result/shape:** For sql-14 Exercise 6, return one row: `sum_of_rounded_lines` 2355648.13, `rounded_exact_total` 2355647.12, and `rounding_difference` 1.01. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
- **Independent verification:** For sql-14 Exercise 6, confirm one row with 2355648.13, 2355647.12, and a `rounding_difference` of 1.01; the difference is the per-line rounding accumulated over 13085 lines, so a report must state which rounding rule it uses.
- **What prints:** one row: 2,355,648.13, 2,355,647.12 and a difference of 1.01.
- **The exact figure:** the unrounded sum is 2,355,647.1235, so rounding once lands closest to it. Rounding each line drifts up by about a dollar.
- **Per-order rounding:** Exercise 3 rounds per order and its values add up to 2,355,646.89, the sum of `orders.total_amount`. Three rounding grains give three totals within 1.24 of each other.
- **Writing it once:** a CTE that computes the two totals and an outer `SELECT` that subtracts them avoids typing the line formula four times.

## Final self-check

- Why does `cast(total_amount AS int)` never differ from `round(total_amount, 0)` in Example 1?
- What does `1 / 4` return, and what is the smallest change that makes it 0.25?
- Which of the five strings in Exercise 2 would abort a plain `::numeric` cast?
- Why does `AVG(amount)` give 477.55 when the average per paid order is 525.05?
- Which total from Exercise 6 would you publish, and how would you explain the 1.01 gap?
