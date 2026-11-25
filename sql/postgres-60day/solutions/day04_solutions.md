# Day 04 solutions: OUTER JOINs: Preserving Unmatched Rows

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each answer here preserves one side of a join and then reads the `NULL`s it creates. Work through the prompts on your own first, then run the whole file:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day04_solutions.sql
```

It runs six read-only queries inside `BEGIN`/`ROLLBACK` and prints 500, 25, 125, 500, 500 and 1 rows. The prompts are the same as in [the learner file](../day04_outer_joins.sql); for a general method of comparing your query with these, see the study guide's [solution reading notes](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
- **Assumptions:** Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
- **Primary pitfall:** A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
- **Safety:** six `SELECT` statements with no writes; nothing changes even if you drop the `BEGIN`/`ROLLBACK` wrapper.

## Exercise 1: Query writing

**Prompt:** List every customer with order count, including customers with zero orders.

**Reasoning:** Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.

**Clause-by-clause reading:**

- `FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.customer_id`: every customer, once per order, or once with `NULL` order columns if they have none.
- `GROUP BY c.customer_id, c.full_name`: back to one row per customer.
- `COUNT(o.order_id)`: counts only real orders, so a NULL-extended row adds 0.
- `ORDER BY order_count DESC, c.customer_id`: busiest customers first, ID breaking ties.

```sql
SELECT
  c.customer_id,
  c.full_name,
  COUNT(o.order_id) AS order_count
FROM
  customers AS c
  LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.full_name
ORDER BY
  order_count DESC,
  c.customer_id;
```

**Expected shape:** One row per customer; zero is visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 1, start from all 500 `customers` and `LEFT JOIN` the 4,362 `orders`; 62 customers have no orders. Return `customer_id`, `full_name`, and `order_count`.
- **Expected result/shape:** For sql-04 Exercise 1, return 500 rows, one per customer: 33 customers tie at the maximum of 16 orders, starting with customer 12, and the 62 customers without orders show 0 at the bottom. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
- **Independent verification:** For sql-04 Exercise 1, confirm 500 distinct `customer_id` values and that `order_count` sums to 4,362, the size of `orders`. Count rows with `order_count = 0` and expect 62; changing `COUNT(o.order_id)` to `COUNT(*)` would turn each of those zeros into 1.
- **What prints:** 500 rows. Customers 12, 25, 38 and 51 lead with 16 orders each; the last 62 rows are the Brazilian customers with 0.
- **Count to compare:** the `order_count` column sums to 4,362, the number of rows in `orders`. A larger total would mean the join duplicated orders.
- **Gap in the counts:** no customer has 1, 2 or 3 orders; the smallest nonzero count is 4. That makes a stray 1 easy to spot when `COUNT(*)` sneaks in (Exercise 5).
- **Name in the key:** `full_name` is in `GROUP BY` only so it can be displayed. Grouping by `customer_id` alone would also work in PostgreSQL, because it is the primary key.
- **Why `LEFT` matters here:** with an inner join the result shrinks to 438 rows, one per customer who ordered, and the 62 zeros are simply missing. Nothing errors, so the only warning sign is a row count short of 500.

## Exercise 2: Query writing

**Prompt:** Find products that have never appeared in an order item.

**Reasoning:** Left join and retain rows where the right-side primary key is NULL.

**Clause-by-clause reading:**

- `products AS p LEFT JOIN order_items AS oi ON oi.product_id = p.product_id`: every product, with line-item columns `NULL` when it never sold.
- `WHERE oi.order_item_id IS NULL`: keeps only those unmatched products, which is the anti-join.
- `ORDER BY p.product_id`: stable listing order.

```sql
SELECT
  p.product_id,
  p.name,
  p.category
FROM
  products AS p
  LEFT JOIN order_items AS oi ON oi.product_id = p.product_id
WHERE
  oi.order_item_id IS NULL
ORDER BY
  p.product_id;
```

**Expected shape:** One row per unsold product.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 2, `LEFT JOIN` all 300 `products` to the 13,085 `order_items` and keep only rows where `oi.order_item_id IS NULL`; the items use 275 distinct products.
- **Expected result/shape:** For sql-04 Exercise 2, return 25 rows, one per product that has never been sold: products 276 through 300. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
- **Independent verification:** For sql-04 Exercise 2, confirm 300 products minus 275 sold products leaves the 25 returned rows, and that `SELECT COUNT(*) FROM products p WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)` also returns 25. Inside a rolled-back transaction, add one `order_items` row for product 300; the result must drop to 24 rows, ending at product 299.
- **What prints:** 25 rows, products 276 to 300. Books has five of them and the other five categories four each.
- **Why this key:** `order_item_id` is the primary key of `order_items`, so it is never `NULL` on a real line item. Testing a nullable column could mistake a real match for a missing one.
- **Same answer, other form:** `WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)` returns the same 25 products and states the intent more directly.
- **Cross-check:** these are the same 25 products that Example 2 listed with `sold_qty` 0.
- **What `IS NULL` is testing:** after the join, a product with sales appears once per line item, and `oi.order_item_id` holds a real ID on each of those rows. Only the 25 NULL-extended rows have it empty, so the filter removes every sold product completely rather than some of its rows.

## Exercise 3: Query writing

**Prompt:** Compare monthly budgets and expenses by category with a full outer join.

**Reasoning:** Aggregate each side to the same category/month grain before joining; preserve keys from either side.

**Clause-by-clause reading:**

- `expense_months`: sums `expenses` to one row per category and `date_trunc('month', expense_date)`.
- `budget_months`: sums `budgets` to one row per category and period.
- `FULL JOIN ... ON em.category = bm.category AND em.period = bm.period`: keeps a category-month that exists on either side.
- `COALESCE(bm.category, em.category)` and `COALESCE(bm.period, em.period)`: one key column, whichever side supplied it.
- `ROUND(..., 2)` and `ORDER BY period, category`.

```sql
WITH expense_months AS (
  SELECT
    e.category,
    date_trunc('month', e.expense_date)::date AS period,
    SUM(e.amount) AS actual_amount
  FROM
    expenses AS e
  GROUP BY
    e.category,
    date_trunc('month', e.expense_date)
),
budget_months AS (
  SELECT
    b.category,
    b.period,
    SUM(b.amount) AS budget_amount
  FROM
    budgets AS b
  GROUP BY
    b.category,
    b.period
)
SELECT
  COALESCE(bm.category, em.category) AS category,
  COALESCE(bm.period, em.period) AS period,
  ROUND(bm.budget_amount, 2) AS budget_amount,
  ROUND(em.actual_amount, 2) AS actual_amount
FROM
  budget_months AS bm
  FULL JOIN expense_months AS em ON em.category = bm.category
    AND em.period = bm.period
  ORDER BY
    period,
    category;
```

**Expected shape:** One row per category/month present in either source.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 3, aggregate `budgets` (125 rows) and `expenses` (10,000 rows) separately to one row per category and month, then `FULL JOIN` the two; each side has 125 category-month keys over 25 months and 5 categories.
- **Expected result/shape:** For sql-04 Exercise 3, return 125 rows, one per category and month, from the oldest budget month to the current month; on the fixture every key exists on both sides, so no amount is `NULL`. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
- **Independent verification:** For sql-04 Exercise 3, confirm 125 distinct `(category, period)` pairs and zero `NULL` values in either amount column. Inside a rolled-back transaction, delete the `COGS` expenses for the oldest month; the result must still have 125 rows, now with one `NULL` `actual_amount`, while an inner join would drop to 124.
- **What prints:** 125 rows, 5 categories times 25 months from 2024-11 to 2026-11. In this fixture both sides cover the same 125 cells, so no row has a `NULL` budget or actual.
- **Partial months:** expenses start on 2024-11-26, so November 2024 COGS shows 72,384.36 actual against a 654,000.00 budget. The last month is cut short in the same way, depending on the load date.
- **Why aggregate first:** a full month holds 68 to 96 expenses per category but only one budget row. Joining raw rows would repeat that budget once per expense before summing.
- **What the full join protects against:** delete a budget row in a test copy and the month still appears, with `budget_amount` `NULL`. An inner join would hide the month entirely.
- **A first finding:** in our check, actual spending exceeded the budget in 72 of the 125 category-months.

## Exercise 4: Prediction

**Prompt:** Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.

**Reasoning:** Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.

**Clause-by-clause reading:**

- `LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'delivered'`: only delivered orders can match; every customer is still preserved.
- `COUNT(o.order_id) AS delivered_orders`: 0 when no delivered order matched.
- `GROUP BY c.customer_id, c.full_name` and `ORDER BY delivered_orders DESC, c.customer_id`.

```sql
SELECT
  c.customer_id,
  c.full_name,
  COUNT(o.order_id) AS delivered_orders
FROM
  customers AS c
  LEFT JOIN orders AS o ON o.customer_id = c.customer_id
    AND o.status = 'delivered'
GROUP BY
  c.customer_id,
  c.full_name
ORDER BY
  delivered_orders DESC,
  c.customer_id;
```

**Expected shape:** One row per customer, including zero delivered orders.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 4, start from all 500 `customers` and `LEFT JOIN` `orders` with `o.status = 'delivered'` inside the `ON` clause; 872 orders are delivered.
- **Expected result/shape:** For sql-04 Exercise 4, return 500 rows, one per customer: 7 customers lead with 4 delivered orders, starting with customer 38, and 69 customers show 0. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
- **Independent verification:** For sql-04 Exercise 4, confirm 500 rows and that `delivered_orders` sums to 872, matching `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`. Move the status test from `ON` to `WHERE` and the result must shrink to 431 customers, because the 69 zero rows are filtered out.
- **What prints:** 500 rows. The most delivered orders any customer has is 4 (customers 38, 103 and 233 are first), and 69 customers show 0.
- **Where the 69 come from:** 62 never ordered, and 7 more (customers 39, 169, 234, 299, 364, 429 and 494) each have four orders, none of them delivered.
- **The `WHERE` version:** moving the status test to `WHERE` returns only 431 rows. All 69 zero rows are gone, because their `o.status` is `NULL` and fails the test.
- **Checking the 431:** that is the number of customers with at least one delivered order, so the `WHERE` form silently answers a different question.
- **Status mix:** orders are spread almost evenly over five statuses, 872 or 873 each, so about one order in five is delivered. That is why no customer shows more than 4 delivered orders even though some placed 16.
- **Column total:** the 500 `delivered_orders` values add up to 872, exactly the delivered rows in `orders`. A larger sum would mean the join duplicated orders; a smaller one would mean some were filtered out.

## Exercise 5: Debugging

**Prompt:** Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.

**Reasoning:** Count a non-nullable right-side key that becomes NULL for an unmatched row.

**Clause-by-clause reading:**

- `customers AS c LEFT JOIN orders AS o`: as in Exercise 1.
- `COUNT(o.order_id)`: the repair; the broken version used `COUNT(*)`.
- `GROUP BY c.customer_id` and `ORDER BY c.customer_id`.

```sql
SELECT
  c.customer_id,
  COUNT(o.order_id) AS order_count
FROM
  customers AS c
  LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with correct zero counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 5, start from all 500 `customers` and `LEFT JOIN` `orders`, counting `o.order_id` rather than `*`; 62 customers have no orders.
- **Expected result/shape:** For sql-04 Exercise 5, return 500 rows in `customer_id` order; customer 1 has 5 orders, customer 8 has 0, and customer 500 has 10. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
- **Independent verification:** For sql-04 Exercise 5, confirm `order_count` sums to 4,362 across 438 nonzero rows and 62 zero rows. The buggy `COUNT(*)` version sums to 4,424 instead, because each of the 62 unmatched customers contributes one all-`NULL` joined row.
- **What prints:** 500 rows in customer order. Customer 1 shows 5 and customer 8 shows 0.
- **Seeing the bug:** with `COUNT(*)`, customer 8 and the other 61 customers without orders show 1, because each still contributes one NULL-extended row.
- **Why it is detectable here:** every customer who ordered has at least 4 orders, so any count of exactly 1 in this fixture is the bug. Real data rarely makes it that easy.
- **Proof query:** `SELECT COUNT(*) FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)` returns 62, the number of zeros the repaired query should show.
- **Where the 1 comes from:** for customer 8 the join produces a single row with the customer's columns filled in and every `o.` column `NULL`. `COUNT(*)` counts that row; `COUNT(o.order_id)` sees the `NULL` key and skips it. For customers who ordered, both forms agree, so the bug shows only on the 62 zero rows.
- **Column total:** the repaired `order_count` column sums to 4,362, the row count of `orders`, spread over 438 buyers. The `COUNT(*)` version sums to 4,424, the extra 62 being one phantom order per non-buyer.

## Exercise 6: Extension

**Prompt:** Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.

**Reasoning:** Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.

**Clause-by-clause reading:**

- `products AS p FULL JOIN order_items AS oi ON oi.product_id = p.product_id`: matched pairs, unsold products, and any line items whose product does not exist.
- `COUNT(DISTINCT p.product_id) FILTER (WHERE ... oi.product_id IS NOT NULL)`: products with at least one sale.
- `FILTER (WHERE p.product_id IS NOT NULL AND oi.product_id IS NULL)`: products with none.
- `COUNT(DISTINCT oi.product_id) FILTER (WHERE p.product_id IS NULL ...)`: product IDs used only in line items.

```sql
SELECT
  COUNT(DISTINCT p.product_id) FILTER (WHERE p.product_id IS NOT NULL
    AND oi.product_id IS NOT NULL) AS matched_products,
  COUNT(DISTINCT p.product_id) FILTER (WHERE p.product_id IS NOT NULL
    AND oi.product_id IS NULL) AS unsold_products,
  COUNT(DISTINCT oi.product_id) FILTER (WHERE p.product_id IS NULL
    AND oi.product_id IS NOT NULL) AS orphan_item_product_ids
FROM
  products AS p
  FULL JOIN order_items AS oi ON oi.product_id = p.product_id;
```

**Expected shape:** One summary row with three mutually interpretable counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-04 Exercise 6, `FULL JOIN` all 300 `products` to the 13,085 `order_items` on `product_id`, which produces 13,110 joined rows, and count distinct product keys by match state.
- **Expected result/shape:** For sql-04 Exercise 6, return exactly one row: `matched_products` 275, `unsold_products` 25, and `orphan_item_product_ids` 0. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
- **Independent verification:** For sql-04 Exercise 6, confirm 275 + 25 equals `SELECT COUNT(*) FROM products` and that 13,110 joined rows equal 13,085 items plus the 25 unsold products. The orphan count must be 0, because `order_items.product_id` is a foreign key to `products` and cannot point at a missing product.
- **What prints:** one row: 275 matched, 25 unsold, 0 orphan product IDs. 275 plus 25 is the full 300 products.
- **Why `DISTINCT`:** the joined relation has 13,110 rows, one per line item (13,085) plus one per unsold product (25). Without `DISTINCT`, `matched_products` would count line items, not products.
- **Why orphans are 0:** `order_items.product_id` has a foreign key to `products`, so the database refuses a line item for a missing product. The column is still worth keeping, because an extract loaded without that constraint can contain orphans.
- **Link to earlier answers:** the 25 unsold products are the same ones Exercise 2 and Example 2 found.

## Final self-check

- Why did Example 1 show only Brazilian customers?
- What does `COUNT(*)` return for customer 8 after a left join, and why?
- How many customers does the `WHERE o.status = 'delivered'` version keep, and which ones go missing?
- In Exercise 3, what would a `NULL` `budget_amount` tell you?
- Why does Exercise 6 need `COUNT(DISTINCT ...)`?
