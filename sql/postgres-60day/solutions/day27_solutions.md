# Day 27 solutions: Pivoting/Unpivoting: Crosstabs and Conditional Aggregation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The answers read `orders`, `customers`, `expenses`, `order_items` and
`products`, and two of them use inline `VALUES` samples instead of tables.
Nothing is written. See [Read a solution](../../STUDY-GUIDE.md#read-a-solution)
for the general approach.

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day27_solutions.sql
```

## How these answers fit together

The first two answers pivot with `COUNT(*) FILTER`, the third and sixth
unpivot with a lateral `VALUES` list, and the fourth compares a `NULL` cell
with a zero. The fifth avoids a fixed column list by returning a JSON object
per month. For every pivot, a total column or a direct aggregate tells you
whether the fixed column list missed anything. The learner file is
[day27_pivot_unpivot.sql](../day27_pivot_unpivot.sql).

## Reading contract

- **Focus:** Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
- **Assumptions:** PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
- **Primary pitfall:** Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Pivot order counts by status into one summary row.

**Reasoning:** Use one filtered count per known status and keep an all-orders denominator.

```sql
SELECT
  COUNT(*) FILTER (WHERE o.status = 'placed') AS placed_orders,
  COUNT(*) FILTER (WHERE o.status = 'paid') AS paid_orders,
  COUNT(*) FILTER (WHERE o.status = 'shipped') AS shipped_orders,
  COUNT(*) FILTER (WHERE o.status = 'delivered') AS delivered_orders,
  COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
  COUNT(*) AS all_orders
FROM
  orders AS o;
```

**Expected shape:** Exactly one row.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 1, read from `orders` and pivot the status counts into one row, with one `COUNT(*) FILTER (WHERE status = ...)` column per known status plus `all_orders`.
- **Expected result/shape:** For sql-27 Exercise 1, expected output: Exactly one row. The final columns are `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
- **Independent verification:** For sql-27 Exercise 1, confirm one row with `placed_orders` 873, `paid_orders` 872, `shipped_orders` 873, `delivered_orders` 872, `returned_orders` 872, and `all_orders` 4362; the five status columns must add up to `all_orders`, or an unknown status exists.
- **Intermediate relation check:** There is no `GROUP BY`, so all 4,362 orders form one group and the query returns one row. The five status columns are 873 placed, 872 paid, 873 shipped, 872 delivered and 872 returned.
- **Clause check:** Each `FILTER` tests one status literal. The five counts add to 4,362, the same as `all_orders`, which proves that no order has a status outside the list. If a sixth status appeared, the sum would fall short.
- **Alternative/trade-off:** `SUM(CASE WHEN o.status = 'placed' THEN 1 ELSE 0 END)` gives the same numbers and works in databases without `FILTER`. `FILTER` is shorter and makes the condition easier to see.
- **Edge case:** A misspelled literal such as `'Paid'` silently returns 0, because `COUNT(*) FILTER` returns 0 for no matches rather than raising an error. Compare the sum of the columns with `all_orders` to catch it.

## Exercise 2: Query writing

**Prompt:** Pivot customer counts for US, CA, GB, and DE by segment.

**Reasoning:** Group at segment grain and use filtered counts for known country columns.

```sql
SELECT
  c.segment,
  COUNT(*) FILTER (WHERE c.country = 'US') AS us_customers,
  COUNT(*) FILTER (WHERE c.country = 'CA') AS ca_customers,
  COUNT(*) FILTER (WHERE c.country = 'GB') AS gb_customers,
  COUNT(*) FILTER (WHERE c.country = 'DE') AS de_customers,
  COUNT(*) AS all_customers
FROM
  customers AS c
GROUP BY
  c.segment
ORDER BY
  c.segment NULLS LAST;
```

**Expected shape:** One row per segment.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 2, read the 500 rows of `customers`, group by `segment`, and turn four countries into columns with `COUNT(*) FILTER (WHERE country = ...)`; `all_customers` counts every row in the segment, including the 312 customers in AU, BR, FR, and IN.
- **Expected result/shape:** For sql-27 Exercise 2, expected output: exactly 4 rows of 125 customers each, and every segment maps to one country in this seed: `gold` has 63 GB customers, `platinum` 63 DE, `silver` 63 CA, and `standard` 63 US, with 0 in the other three columns. The final columns are `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`. The final order is `c.segment NULLS LAST`.
- **Independent verification:** For sql-27 Exercise 2, confirm `all_customers` adds to 500 and that each country column adds to its `SELECT COUNT(*) FROM customers WHERE country = ...` count of 63; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET segment = NULL WHERE customer_id = 1` (a US customer) and confirm a fifth row with a NULL segment appears last with 1 US customer, while `standard` drops to 62 and 124.
- **Intermediate relation check:** `GROUP BY c.segment` gives four rows, gold, platinum, silver and standard, each with 125 customers. No customer has a `NULL` segment, so `NULLS LAST` has nothing to move.
- **Clause check:** In this fixture each segment holds exactly two countries, so each row has one nonzero column of 63 and three zeros. Gold has GB, platinum DE, silver CA and standard US; the other 62 customers in each segment are in AU, BR, IN or FR.
- **Alternative/trade-off:** Grouping by `segment, country` gives the same facts as eight long rows with no zeros. The pivot is easier to scan but hides countries without a column unless `all_customers` is kept.
- **Edge case:** The zeros here are real: they come from `COUNT`, which never returns `NULL`. A segment with no customers at all would have no row, not a row of zeros.

## Exercise 3: Query writing

**Prompt:** Unpivot a wide quarterly sample into quarter/amount rows.

**Reasoning:** Use a lateral `VALUES` relation with one output row per source column.

```sql
WITH wide (
  company,
  q1,
  q2,
  q3,
  q4
) AS (
  VALUES ('A', 10::numeric, 20::numeric, 30::numeric, 40::numeric),
    ('B', 5::numeric, NULL::numeric, 15::numeric, 25::numeric))
SELECT
  w.company,
  unpivoted.quarter,
  unpivoted.amount
FROM
  wide AS w
  CROSS JOIN LATERAL (
    VALUES ('Q1', w.q1), ('Q2', w.q2), ('Q3', w.q3), ('Q4', w.q4)) AS unpivoted (quarter, amount)
ORDER BY
  w.company,
  unpivoted.quarter;
```

**Expected shape:** Eight rows from two source rows and four quarters.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 3, no table is read: the `wide` CTE holds two `VALUES` rows, company A with 10, 20, 30, 40 and company B with 5, NULL, 15, 25, and `CROSS JOIN LATERAL (VALUES ...)` turns each row's four quarter columns into four `(quarter, amount)` rows.
- **Expected result/shape:** For sql-27 Exercise 3, expected output: exactly 8 rows, four per company, with B `Q2` kept as a row whose `amount` is NULL. The final columns are `company`, `quarter`, and `amount`. The final order is `w.company, unpivoted.quarter`.
- **Independent verification:** For sql-27 Exercise 3, confirm 8 rows, 4 per company, that `SUM(amount)` is 100 for A and 45 for B, and that exactly one row has `amount IS NULL`; adding `WHERE unpivoted.amount IS NOT NULL` would return 7 rows and lose the fact that B reported nothing for `Q2`.
- **Intermediate relation check:** `wide` is two rows, A and B, with four quarter columns. B's `q2` is `NULL`.
- **Clause check:** The lateral `VALUES` list has four entries, so each input row produces four rows: 2 times 4 is 8. B's `Q2` row is kept with a `NULL` amount, because `VALUES` emits every listed column whatever its value.
- **Alternative/trade-off:** `unnest(ARRAY['Q1','Q2','Q3','Q4'], ARRAY[w.q1, w.q2, w.q3, w.q4])` unpivots the same way. The `VALUES` form keeps each label next to its column, which is harder to get out of step.
- **Edge case:** Add `WHERE unpivoted.amount IS NOT NULL` only if the report should drop missing quarters; that gives 7 rows. Ordering by `quarter` works because `Q1` to `Q4` also sort correctly as text.

## Exercise 4: Prediction

**Prompt:** Compare a missing pivot combination with a real zero and preserve the distinction.

**Reasoning:** Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.

```sql
SELECT
  e.category,
  SUM(e.amount) FILTER (WHERE EXTRACT(MONTH FROM e.expense_date) = 1) AS january_observed_amount,
  COALESCE(SUM(e.amount) FILTER (WHERE EXTRACT(MONTH FROM e.expense_date) = 1), 0) AS january_reported_zero_if_absent
FROM
  expenses AS e
GROUP BY
  e.category
ORDER BY
  e.category;
```

**Expected shape:** One row per expense category with nullable/zero-aware columns.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 4, read the 10000 `expenses` rows (5 categories, 2000 each, dated over the two years before the load), group by `category`, and sum only January rows with `FILTER (WHERE EXTRACT(MONTH FROM expense_date) = 1)`, once raw and once wrapped in `COALESCE(..., 0)`.
- **Expected result/shape:** For sql-27 Exercise 4, expected output: exactly 5 rows; every category has January rows on this load (164 to 192 rows across two Januaries), so both columns match, for example COGS 856904.40 and Marketing 972676.11. The final columns are `category`, `january_observed_amount`, and `january_reported_zero_if_absent`. The final order is `e.category`.
- **Independent verification:** For sql-27 Exercise 4, confirm each category's January row count with `SELECT category, COUNT(*) FROM expenses WHERE EXTRACT(MONTH FROM expense_date) = 1 GROUP BY category`; then, inside `BEGIN ... ROLLBACK`, insert `('Legal', 100, '2026-03-01')` and `('Travel', 0, '2026-01-15')` and confirm Legal returns NULL and 0 (no January rows) while Travel returns 0.00 and 0.00 (a real zero).
- **Intermediate relation check:** `expenses` has 10,000 rows, 2,000 per category across COGS, G&A, Infrastructure, Marketing and Payroll, so the result has five rows.
- **Clause check:** Every category has January expenses, so both columns hold the same numbers; a late-2026 load showed 856,904.40 for COGS. `EXTRACT(MONTH ...)` ignores the year, so a 730-day window can feed two Januaries into one figure.
- **Alternative/trade-off:** To see the two columns differ, restrict the input so January is missing, for example `WHERE EXTRACT(MONTH FROM e.expense_date) <> 1`. Then `january_observed_amount` is `NULL` and the reported column shows 0.
- **Edge case:** The expense dates count back 730 days from the day the fixture was loaded, so which Januaries are included depends on that date. A category with no January expense in the data would appear only if it had other rows.

## Exercise 5: Debugging

**Prompt:** Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.

**Reasoning:** Aggregate category/value pairs into data values so the result schema remains stable.

```sql
WITH category_month AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    p.category,
    ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC'),
    p.category
)
SELECT
  month_start,
  jsonb_object_agg(category, revenue ORDER BY category) AS revenue_by_category
FROM
  category_month
GROUP BY
  month_start
ORDER BY
  month_start;
```

**Expected shape:** One row per UTC month with a JSON object of category revenue.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 5, read `orders`, `order_items`, and `products`, round net item revenue per UTC month and `category` in `category_month`, then fold each month's six rows into one JSONB value with `jsonb_object_agg(category, revenue ORDER BY category)`.
- **Expected result/shape:** For sql-27 Exercise 5, expected output: one row per UTC month (46 on this load), each object holding all 6 category keys; the first month is `{"Home": 30.20, "Books": 279.76, "Beauty": 94.00, "Sports": 175.41, "Apparel": 407.05, "Electronics": 216.84}`, because JSONB stores keys shorter first, not in the `ORDER BY` order. The final columns are `month_start`, and `revenue_by_category`. The final order is `month_start`.
- **Independent verification:** For sql-27 Exercise 5, confirm every object has 6 keys with `jsonb_object_keys`, and that summing `jsonb_each_text` values over all months gives 2355647.24, slightly above the unrounded 2355647.12 because each cell was rounded first; a missing key such as `revenue_by_category -> 'Toys'` returns NULL, and `jsonb_object_agg` over `VALUES ('a', 1), (NULL, 2)` fails with `field name must not be null`.
- **Intermediate relation check:** `category_month` has one row per month and category, rounded to two decimals. In the checked data that was 46 months with all six categories each, 276 rows.
- **Clause check:** `jsonb_object_agg(category, revenue ...)` folds the six rows of a month into one object, so the result has one row per month. On a late-2026 load the first month, February 2023, shows Apparel at 407.05 and Home at 30.20.
- **Alternative/trade-off:** Six `FILTER` columns would also work today, but a seventh category would be silently dropped. The JSON object picks up new keys without changing the column list, at the cost of needing JSON functions to read it.
- **Edge case:** Because each cell is rounded before it goes into the object, adding all the cells gives 2,355,647.24, while the unrounded item total is 2,355,647.12. Reconcile against the unrounded total and expect a few cents of rounding.

## Exercise 6: Extension

**Prompt:** Round-trip a wide sample to long form and back, verifying values and NULLs.

**Reasoning:** Unpivot with lateral values, then use conditional aggregation keyed by company.

```sql
WITH wide (
  company,
  q1,
  q2
) AS (
  VALUES ('A', 10::numeric, 20::numeric),
    ('B', NULL::numeric, 5::numeric)
),
long AS (
  SELECT
    w.company, u.quarter, u.amount
  FROM
    wide AS w
    CROSS JOIN LATERAL (
      VALUES ('Q1', w.q1), ('Q2', w.q2)) AS u (quarter, amount))
  SELECT
    company,
    MAX(amount) FILTER (WHERE quarter = 'Q1') AS q1,
    MAX(amount) FILTER (WHERE quarter = 'Q2') AS q2
  FROM
    long
  GROUP BY
    company
  ORDER BY
    company;
```

**Expected shape:** Two reconstructed rows matching the source.

### Reasoning and verification

- **Inputs/evidence:** For sql-27 Exercise 6, no table is read: the `wide` CTE holds A with 10 and 20 and B with NULL and 5; `long` unpivots it into four `(company, quarter, amount)` rows, and the outer query pivots back with `MAX(amount) FILTER (WHERE quarter = ...)` grouped by `company`.
- **Expected result/shape:** For sql-27 Exercise 6, expected output: exactly 2 rows, A with 10 and 20 and B with NULL and 5, identical to `wide`. The final columns are `company`, `q1`, and `q2`. The final order is `company`.
- **Independent verification:** For sql-27 Exercise 6, confirm `long` has 4 rows with one NULL `amount`, and that both `SELECT * FROM wide EXCEPT SELECT ...` and the reverse return 0 rows, since `EXCEPT` treats the two NULLs as equal; then pivot `VALUES ('A', 'Q1', 10), ('A', 'Q1', 99), ('A', 'Q2', 20)` and confirm `q1` shows 99, because `MAX` silently hides a duplicate quarter that a `COUNT(*)` of 3 would reveal.
- **Intermediate relation check:** `long` has four rows, two quarters for each of A and B, including B's `Q1` row whose amount is `NULL`.
- **Clause check:** `MAX(amount) FILTER (WHERE quarter = 'Q1')` picks the one value per company and quarter. For B it sees only a `NULL`, so it returns `NULL`, and the rebuilt rows are A 10 and 20, then B `NULL` and 5, matching `wide`.
- **Alternative/trade-off:** `TABLE wide EXCEPT` the rebuilt query returns no rows, and it treats two `NULL` values as equal. A join on `q1 = q1` would wrongly report company B as a mismatch.
- **Edge case:** `MAX` hides duplicates. If `long` held two `Q2` rows for A, the rebuild would keep only the larger one; check `COUNT(*)` per company and quarter if duplicates are possible.

## Final self-check

- Which answers need a total column to show that the fixed column list is
  complete?
- Why is the 0 in the segment pivot a real value while a `NULL` in the
  expense pivot is a missing one?
- How many rows does a lateral `VALUES` unpivot return for 3 input rows and
  5 listed columns?
- When would you choose a JSON object over fixed pivot columns?
