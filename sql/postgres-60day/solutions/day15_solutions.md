# Day 15 solutions: Phase 1 Project: Multi-Dimensional Revenue Report

<!-- beginner-solution-enrichment -->
## How to study and run this solution

The six answers only read data, and together they build one reconciled picture of the fixture: Exercises 1 to 3 summarize single tables, Exercise 4 reconciles three totals for each order, Exercise 5 lines up budgets with expenses, and Exercise 6 prints the control row. Run the companion after your own attempt:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day15_solutions.sql
```

It sets `search_path` to `training, public` and wraps all six queries in `BEGIN`/`ROLLBACK`. Fixture dates are generated relative to load time, so month labels and the sparse first months can differ on your load; counts and money totals that do not depend on the calendar (500 customers, 4,362 orders, 275 sold products, the Exercise 6 row) should match exactly. These answers align one-for-one with [day15_phase1_project.sql](../day15_phase1_project.sql), and the general [solution reading steps](../../STUDY-GUIDE.md#read-a-solution) apply.

## Reading contract

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Primary pitfall:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Safety:** every answer is a read. The companion still wraps them in `BEGIN`/`ROLLBACK`, so experiments such as deleting a budget row or inserting a test customer vanish when it ends.

## Exercise 1: Query writing

**Prompt:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.

**Reasoning:** Left join from customers and aggregate at customer grain.

**Clause-by-clause reading:**

- `FROM customers AS c LEFT JOIN orders AS o`: every customer survives, with one joined row per order, or a single row of NULL order columns for the 62 customers who never ordered.
- `GROUP BY c.customer_id, c.full_name, c.country`: back to one row per customer. Name and country are listed so they can be selected; they cannot split a customer because both depend on the ID.
- `COUNT(o.order_id)`: counts matched orders only, so a customer without orders gets 0.
- `COALESCE(ROUND(SUM(o.total_amount), 2), 0)`: `SUM` over nothing but NULLs is NULL, and the fallback reports 0 because "spent nothing" is the honest reading.
- `MAX(o.order_date)`: stays NULL for customers without orders; there is no latest date to invent.
- `ORDER BY stored_revenue DESC, c.customer_id`: biggest spenders first, and the ID orders the zero-revenue rows at the bottom.

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  COUNT(o.order_id) AS order_count,
  COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_revenue,
  MAX(o.order_date) AS latest_order_date
FROM
  customers AS c
  LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.full_name,
  c.country
ORDER BY
  stored_revenue DESC,
  c.customer_id;
```

**Expected shape:** One row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 1, `LEFT JOIN` all 500 `customers` to their `orders`, then count `o.order_id`, sum `total_amount` with `COALESCE(..., 0)`, and take `MAX(order_date)` per customer.
- **Expected result/shape:** For sql-15 Exercise 1, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21) and ending with the 62 `BR` customers who never ordered, each with 0 orders, 0 revenue, and a `NULL` `latest_order_date`. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
- **Independent verification:** For sql-15 Exercise 1, confirm 500 distinct `customer_id` values, `SUM(order_count)` = 4,362, and `SUM(stored_revenue)` = 2355646.89, matching `orders`. Swap `COUNT(o.order_id)` for `COUNT(*)` and the 62 no-order customers must show 1 instead of 0. Customers 51 and 428 tie at 8970.66, so `c.customer_id` must place 51 first on every run.
- **Count before you trust it:** the result needs 500 rows, matching `SELECT count(*) FROM customers`. The top row is customer 181 (FR) with 16 orders and 9,502.21; the last 62 rows are the BR customers with 0 orders and a NULL `latest_order_date`.
- **The decisive choice:** `LEFT JOIN` together with `COUNT(o.order_id)`. An inner join drops the BR customers and leaves 438 rows; keeping the left join but switching to `COUNT(*)` gives each of them one phantom order.
- **Another valid form:** aggregate `orders` per customer in a CTE, then left join that CTE to `customers`. It mirrors Exercise 4 and stays correct when a second fact table joins later.
- **Something to try:** insert one customer with no orders inside the transaction. The row count rises to 501 and the newcomer sorts among the zero-revenue rows by its ID.

## Exercise 2: Query writing

**Prompt:** Create a product profitability table from net order-line revenue and catalog cost.

**Reasoning:** Calculate line revenue and line cost at item grain, then aggregate to product.

**Clause-by-clause reading:**

- `FROM products AS p JOIN order_items AS oi`: one row per order line with the product's catalog `cost` attached. The inner join drops products 276 to 300, which were never sold.
- `SUM(oi.quantity)`: units sold.
- `SUM(oi.unit_price * oi.quantity * (1 - oi.discount))`: net revenue, combined per line before summing because the discount (0, 0.05 or 0.15) changes from line to line.
- `SUM(p.cost * oi.quantity)`: catalog cost of the units sold. The cost comes from `products`, so it is today's catalog cost rather than a cost recorded at sale time.
- `gross_profit`: the difference of the two sums, rounded once at the end rather than per line.
- `ORDER BY gross_profit DESC, p.product_id`: most profitable product first, with the ID settling equal profits.

```sql
SELECT
  p.product_id,
  p.name,
  p.category,
  SUM(oi.quantity) AS units_sold,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
  ROUND(SUM(p.cost * oi.quantity), 2) AS catalog_cost,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) - SUM(p.cost * oi.quantity), 2) AS gross_profit
FROM
  products AS p
  JOIN order_items AS oi ON oi.product_id = p.product_id
GROUP BY
  p.product_id,
  p.name,
  p.category
ORDER BY
  gross_profit DESC,
  p.product_id;
```

**Expected shape:** One row per sold product.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 2, inner-join `products` to `order_items` and, per product, sum `quantity`, net line revenue, catalog cost `p.cost * oi.quantity`, and their difference as `gross_profit`.
- **Expected result/shape:** For sql-15 Exercise 2, return 275 rows, one per product that has sold at least once, led by product 271 (Apparel, 160 units, `gross_profit` 10939.20) and ending with product 3 at 323.61; products 276 to 300 have no item rows and are left out. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
- **Independent verification:** For sql-15 Exercise 2, confirm 275 distinct `product_id` values, `SUM(units_sold)` = 39,257, and `SUM(net_revenue)` = 2355647.12, the item-level total. Inside a rolled-back transaction, insert one `order_items` row for product 300 on order 1; the result must grow to 276 rows with product 300 at 1 unit sold.
- **Expected size:** 275 rows, one per product that appears in `order_items`. Product 271 (Apparel) leads with 160 units, 17,643.20 net revenue and 10,939.20 gross profit, followed by 237 (Home) and 262 (Beauty). No product shows a loss on this fixture.
- **Why the math stays per line:** `SUM(oi.unit_price) * SUM(oi.quantity)` multiplies two unrelated totals. Price, quantity and discount belong to the same line and must be combined before aggregation.
- **Worth noticing:** `oi.unit_price` equals the catalog `price` on all 13,085 lines, so here the discount is the only reason net revenue sits below list revenue. Real order lines drift from the catalog, which is why revenue uses the line price and not `p.price`.
- **Something to try:** to show unsold products with zero profit, start from `products`, `LEFT JOIN` the items and wrap each sum in `COALESCE`; the row count becomes 300.

## Exercise 3: Query writing

**Prompt:** Build a UTC monthly order-status report with counts and stored revenue.

**Reasoning:** Derive one reporting month and group by month/status.

**Clause-by-clause reading:**

- `date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date`: converts the `timestamptz` to UTC wall-clock time, truncates to the first of the month and casts to `date` for display.
- `GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), o.status`: groups on the same truncation without the cast, which produces identical buckets.
- `COUNT(*)` and `ROUND(SUM(o.total_amount), 2)`: the order count and stored revenue in each bucket.
- `ORDER BY utc_month, o.status`: oldest month first, then status as text, so delivered, paid, placed, returned, shipped.

```sql
SELECT
  date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS utc_month,
  o.status,
  COUNT(*) AS order_count,
  ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM
  orders AS o
GROUP BY
  date_trunc('month', o.order_date AT TIME ZONE 'UTC'),
  o.status
ORDER BY
  utc_month,
  o.status;
```

**Expected shape:** One row per observed month and status.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 3, group all 4,362 `orders` by UTC month (`date_trunc('month', o.order_date AT TIME ZONE 'UTC')`) and `status`, counting orders and summing `total_amount`.
- **Expected result/shape:** For sql-15 Exercise 3, return 224 rows, one per observed month and status pair, starting with `2023-02-01` `delivered` (1 order, 986.42); 46 months times 5 statuses would give 230, but the first three months lack 6 of the pairs. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
- **Independent verification:** For sql-15 Exercise 3, confirm 224 distinct (`utc_month`, `status`) pairs and that the `order_count` values add up to 4,362; `2023-02-01` must show only `delivered` and `shipped`. Inside a rolled-back transaction, insert one order with status `cancelled`; the result must grow to 225 rows with the new pair in the current month at 1 order.
- **Expected size:** 224 month and status rows across 46 months on the load used here, not 46 times 5 = 230. The earliest months are sparse (the very first has only `delivered` and `shipped`), and a combination with no orders simply has no row.
- **Totals to reconcile:** `order_count` must add to 4,362, and each status to 872 or 873 across all months.
- **Another valid form:** `GROUP BY 1, 2` refers to select-list positions. It is shorter, but the named expression survives someone inserting a column at the front of the select list.
- **Something to try:** run `SET TIME ZONE 'Pacific/Auckland'`, then rerun this query and a copy without `AT TIME ZONE 'UTC'`. Only the copy should move orders that sit near a month boundary.

## Exercise 4: Debugging

**Prompt:** Reconcile stored order total, computed line total, and paid total without multiplying details.

**Reasoning:** Aggregate items and payments independently to order grain before joining.

**Clause-by-clause reading:**

- `line_totals`: one row per order holding its net line revenue, 4,362 rows because every order has at least one item.
- `paid_totals`: collapses the 3,836 payments to 3,489 paid orders, which is where the 347 split payments stop being a fanout risk.
- `FROM orders AS o JOIN line_totals AS lt`: an inner join is safe here because no order lacks lines.
- `LEFT JOIN paid_totals AS pt`: keeps the 873 `placed` orders, which have no payments at all.
- `COALESCE(pt.paid_total, 0)`: an order with no payments has paid zero, so the fallback is the correct value, not a disguise.
- `ORDER BY ABS(o.total_amount - lt.line_total) DESC, o.order_id`: the largest stored-versus-lines disagreement first.

```sql
WITH line_totals AS (
  SELECT
    oi.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM
    order_items AS oi
  GROUP BY
    oi.order_id
),
paid_totals AS (
  SELECT
    p.order_id,
    SUM(p.amount) AS paid_total
  FROM
    payments AS p
  GROUP BY
    p.order_id
)
SELECT
  o.order_id,
  ROUND(o.total_amount, 2) AS stored_total,
  ROUND(lt.line_total, 2) AS line_total,
  ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
  ROUND(o.total_amount - lt.line_total, 2) AS stored_minus_lines,
  ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM
  orders AS o
  JOIN line_totals AS lt ON lt.order_id = o.order_id
  LEFT JOIN paid_totals AS pt ON pt.order_id = o.order_id
ORDER BY
  ABS(o.total_amount - lt.line_total) DESC,
  o.order_id;
```

**Expected shape:** One row per order with differences.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 4, pre-aggregate `order_items` to `line_totals` and `payments` to `paid_totals`, one row per `order_id` each, then join both to `orders` (inner to line totals, left to payments).
- **Expected result/shape:** For sql-15 Exercise 4, return 4,362 rows, one per order; every `stored_minus_lines` is 0.00 after rounding (2,855 orders differ by under half a cent), so the order falls back to `order_id`, starting with order 21. 1,072 rows have a positive `unpaid_balance`, 873 of them `placed` orders with no payment row. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
- **Independent verification:** For sql-15 Exercise 4, confirm 4,362 distinct `order_id` values, 0 rows with a negative `unpaid_balance`, and that `SUM(unpaid_balance)` is 523746.08, which equals 2355646.89 stored minus 1831900.81 paid. Inside a rolled-back transaction, set order 1's `total_amount` to 250.20; order 1 must jump to the first row with `stored_minus_lines` and `unpaid_balance` both 10.00.
- **What the rows show:** 4,362 rows. `stored_minus_lines` rounds to 0.00 for every order (the largest raw gap is 0.0045), so the sort is ranking sub-cent rounding. The informative column is `unpaid_balance`: the 873 placed orders owe their full total, and 199 paid, shipped, delivered or returned orders carry a positive balance of up to 716.24, adding to 53,902.98.
- **The decisive choice:** aggregating both detail tables before the join. Joining `order_items` and `payments` directly to `orders` pairs every line with every payment, so a two-payment order would report double its line total.
- **Another valid form:** correlated subqueries such as `(SELECT SUM(amount) FROM payments WHERE order_id = o.order_id)` return the same numbers and cannot fan out, at the cost of one lookup per order.
- **Something to try:** sum `unpaid_balance` over the whole result. It should equal stored revenue minus payments from Exercise 6, 523,746.08.

## Exercise 5: Prediction

**Prompt:** Compare monthly budgets with actual expenses and preserve missing sides.

**Reasoning:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.

**Clause-by-clause reading:**

- `actual`: expenses summed per category and calendar month. `expense_date` is a `date`, so no time zone is involved in the truncation.
- `planned`: budgets summed per category and `period`. The table already has one row per pair, so this `SUM` is defensive.
- `FULL JOIN ... ON a.category = p.category AND a.period = p.period`: keeps a pair found on either side, matched or not.
- `COALESCE(p.category, a.category)` and `COALESCE(p.period, a.period)`: take the key from whichever side exists.
- `budget_amount`, `actual_amount` and `variance`: left NULL when a side is missing, so `variance` is NULL too instead of pretending one side was zero.
- `ORDER BY period, category`: these names are output aliases, so the sort uses the coalesced keys.

```sql
WITH actual AS (
  SELECT
    e.category,
    date_trunc('month', e.expense_date)::date AS period,
    SUM(e.amount) AS amount
  FROM
    expenses AS e
  GROUP BY
    e.category,
    date_trunc('month', e.expense_date)
),
planned AS (
  SELECT
    b.category,
    b.period,
    SUM(b.amount) AS amount
  FROM
    budgets AS b
  GROUP BY
    b.category,
    b.period
)
SELECT
  COALESCE(p.category, a.category) AS category,
  COALESCE(p.period, a.period) AS period,
  ROUND(p.amount, 2) AS budget_amount,
  ROUND(a.amount, 2) AS actual_amount,
  ROUND(a.amount - p.amount, 2) AS variance
FROM
  planned AS p
  FULL JOIN actual AS a ON a.category = p.category
    AND a.period = p.period
  ORDER BY
    period,
    category;
```

**Expected shape:** One row per category/month in either source.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 5, sum the 10,000 `expenses` rows by `category` and calendar month, sum the 125 `budgets` rows by `category` and `period`, then `FULL JOIN` the two summaries on both keys.
- **Expected result/shape:** For sql-15 Exercise 5, return 125 rows, 5 categories (`COGS`, `G&A`, `Infrastructure`, `Marketing`, `Payroll`) times 25 months from `2024-11-01` to `2026-11-01`; on the fixture every pair has both a budget and an actual, so no column is `NULL`. The first row is `COGS` for `2024-11-01` with 654000.00 budgeted against 72384.36 spent. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
- **Independent verification:** For sql-15 Exercise 5, confirm 125 distinct (`category`, `period`) pairs; joining raw `budgets` to raw `expenses` instead returns 10,000 rows, one per expense, which is the fanout the two summaries prevent. Inside a rolled-back transaction, add a `Travel` budget for `2026-11-01` and a `Legal` expense dated `2026-11-10`; both must appear, `Travel` with a `NULL` actual and `Legal` with a `NULL` budget, and both with a `NULL` variance.
- **Prediction to write first:** five categories (COGS, G&A, Infrastructure, Marketing, Payroll) over 25 months give 125 rows on each side. The key sets match exactly on this fixture, so the full join returns 125 rows with no NULL budget or actual.
- **Why a full join anyway:** the fixture happens to be complete and the query must not depend on that. An inner join would silently drop a month spent without a budget, and a left join from `planned` would drop unbudgeted spending.
- **Another valid form:** build the key set with `SELECT category, period FROM planned UNION SELECT category, period FROM actual`, then left join both CTEs to it. Longer, but the "either source" rule is spelled out.
- **Something to try:** delete one `budgets` row inside the transaction. The result still has 125 rows, and that pair now shows NULL `budget_amount` and NULL `variance` rather than a variance equal to the whole actual.

## Exercise 6: Extension

**Prompt:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.

**Reasoning:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.

**Clause-by-clause reading:**

- Four one-row CTEs: `customer_kpis` counts `customers`, `order_kpis` counts and sums `orders`, `line_kpis` sums net revenue from `order_items`, and `payment_kpis` sums `payments`.
- `CROSS JOIN`: one row times one row times one row times one row is still one row, so no measure can be repeated.
- `ROUND(..., 2)`: applied only to the three money columns, at display time.

```sql
WITH customer_kpis AS (
  SELECT
    COUNT(*) AS customers
  FROM
    customers
),
order_kpis AS (
  SELECT
    COUNT(*) AS orders,
    SUM(total_amount) AS stored_revenue
  FROM
    orders
),
line_kpis AS (
  SELECT
    SUM(unit_price * quantity * (1 - discount)) AS computed_revenue
  FROM
    order_items
),
payment_kpis AS (
  SELECT
    SUM(amount) AS payments
  FROM
    payments
)
SELECT
  c.customers,
  o.orders,
  ROUND(o.stored_revenue, 2) AS stored_revenue,
  ROUND(l.computed_revenue, 2) AS computed_revenue,
  ROUND(p.payments, 2) AS payments
FROM
  customer_kpis AS c
  CROSS JOIN order_kpis AS o
  CROSS JOIN line_kpis AS l
  CROSS JOIN payment_kpis AS p;
```

**Expected shape:** Exactly one summary row.

### Reasoning and verification

- **Inputs/evidence:** For sql-15 Exercise 6, compute each total in its own single-row CTE (customer count, order count and stored revenue, line revenue from `order_items`, and payment sum) and `CROSS JOIN` the four one-row results.
- **Expected result/shape:** For sql-15 Exercise 6, return one row: 500 customers, 4,362 orders, `stored_revenue` 2355646.89, `computed_revenue` 2355647.12, and `payments` 1831900.81. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
- **Independent verification:** For sql-15 Exercise 6, confirm each value against its own query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` returns 1831900.81. Then sum `o.total_amount` after `orders JOIN order_items` and get 8633041.53, more than 3.6 times the stored figure; that fanout is why every total is computed before the `CROSS JOIN`.
- **The row to expect:** 500 customers, 4,362 orders, stored revenue 2,355,646.89, computed revenue 2,355,647.12 and payments 1,831,900.81.
- **Reading the gaps:** stored and computed revenue differ by 0.23 of cent rounding. Payments trail stored revenue by 523,746.08: 469,843.10 from the unpaid `placed` orders plus the 53,902.98 of partial balances found in Exercise 4.
- **What the tempting version prints:** `FROM customers JOIN orders JOIN payments` yields 3,836 rows, and `SUM(o.total_amount)` over them gives 1,926,711.58, which both drops the placed orders and counts each split-payment order twice.
- **Another valid form:** four scalar subqueries in one `SELECT` with no `FROM`. The result is identical; the CTE names help when a fifth metric arrives.
- **Applying the add-a-row check:** a summary has no per-customer rows to gain, so inserting a test customer must leave exactly one output row while `customers` moves from 500 to 501 and the four other columns stay put. Any other change means that customer leaked into a join.

## Final self-check

- Which three money figures in the Exercise 6 row should your other reports reconcile to, and which revenue definition does each one use?
- Why does Exercise 1 count `o.order_id` rather than `*`, and what would the 62 BR customers show otherwise?
- In Exercise 4, which orders carry a nonzero `unpaid_balance`, and why is `COALESCE` right there but wrong for Exercise 5's missing budgets?
- After `SET TIME ZONE 'Pacific/Auckland'`, does your Exercise 3 result change? Should it?
- Did the companion finish at `ROLLBACK` without an `ERROR` line?
