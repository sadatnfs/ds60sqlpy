# Day 18 solutions: LAG/LEAD and Intra-Row Comparisons

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each answer below reads a neighbouring row with `LAG` or `LEAD`, and each depends on two choices: which rows share a partition and what order they are read in. Exercises 2, 4 and 5 compute the window inside a CTE so that a later step can subtract from it or filter on it. Try the six prompts first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day18_solutions.sql
```

Row counts to expect: 4,362, 4,362, 200, 438, 46 (in our check) and 300. Everything runs between `BEGIN` and `ROLLBACK`, and the excerpts omit the `SET search_path` line. Exercise numbers match [the learner file](../day18_lag_lead.sql); the study guide explains [how to read a solution](../../STUDY-GUIDE.md#read-a-solution) without just copying it.

## Reading contract

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Primary pitfall:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Safety:** read-only; the six queries change nothing, and `ROLLBACK` closes the transaction.

## Exercise 1: Query writing

**Prompt:** Show each order with the previous order timestamp for that customer.

**Reasoning:** Partition by customer and order by timestamp plus ID.

**Clause-by-clause reading:**

- `LAG(o.order_date) OVER (...)`: the date of the row one step back in the window.
- `PARTITION BY o.customer_id`: each customer's orders form a separate sequence, so the first order of every customer has no previous row.
- `ORDER BY o.order_date, o.order_id` inside `OVER`: defines "previous"; the ID guarantees a fixed order if two dates were equal.
- Outer `ORDER BY o.customer_id, o.order_date, o.order_id`: prints each customer's orders together, oldest first, matching the window order so the output is easy to check by eye.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id) AS previous_order_date
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order; first customer order has NULL previous timestamp.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 1, attach `LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id)` to each of the 4,362 `orders` rows; every buyer has at least 4 orders.
- **Expected result/shape:** For sql-18 Exercise 1, return 4,362 rows, one per order, with `previous_order_date` `NULL` on exactly 438 rows, one per buyer's first order; customer 1's orders 1 to 5 show `NULL` and then the dates of orders 1, 2, 3, and 4. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-18 Exercise 1, confirm 4,362 distinct `order_id` values, 438 `NULL` previous dates, and that every non-null `previous_order_date` is earlier than its row's `order_date`. Inside a rolled-back transaction, add one order for customer 8, who has none; that new one-row partition must show `NULL`, and customer 1's first row must stay order 1 with `NULL`.
- **What prints:** 4,362 rows, one per order. 438 of them, one per ordering customer, have a blank `previous_order_date`; the 62 Brazilian customers are absent because the query starts from `orders`.
- **Checking one customer:** customer 1's order 1 shows no previous date, order 2 shows order 1's date, and so on up to order 5.
- **Link to Exercise 4:** the rows with a blank `previous_order_date` are exactly the 438 first orders that Exercise 4 lists. Order 6 is one of them even though order 5, customer 1's last, prints directly above it.
- **Two `ORDER BY`s:** the one inside `OVER` decides what "previous" means; the one at the end only decides display order. Changing the second leaves every `previous_order_date` the same.

## Exercise 2: Query writing

**Prompt:** Calculate days since each customer's previous order.

**Reasoning:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.

**Clause-by-clause reading:**

- `WITH sequenced AS (SELECT o.*, LAG(o.order_date) OVER (...) AS previous_order_date ...)`: attaches the previous date to every order, using the same window as Exercise 1.
- `order_date - previous_order_date`: subtracting two `timestamptz` values gives an `interval`, for example `7 days 21:21:30.43`.
- `EXTRACT(EPOCH FROM ...) / 86400.0`: turns that interval into seconds and then into fractional days; the `.0` keeps the division decimal.
- `ORDER BY customer_id, order_date, order_id`: the same layout as Exercise 1.

```sql
WITH sequenced AS (
  SELECT
    o.*,
    LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date,
      o.order_id) AS previous_order_date
  FROM
    orders AS o
)
SELECT
  order_id,
  customer_id,
  order_date,
  previous_order_date,
  EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0 AS days_since_previous
FROM
  sequenced
ORDER BY
  customer_id,
  order_date,
  order_id;
```

**Expected shape:** One row per order with nullable interval/days.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 2, compute `previous_order_date` with `LAG` in the `sequenced` CTE, then convert the gap to days with `EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0`.
- **Expected result/shape:** For sql-18 Exercise 2, return 4,362 rows, one per order, with 438 `NULL` gaps; customer 1's four gaps are each 7.9005282256944444 days, and the 3,924 non-null gaps run from 2.2882 to 296.6473 days and average 65.4524. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
- **Independent verification:** For sql-18 Exercise 2, confirm 3,924 non-null `days_since_previous` values and none at zero or below, since no customer has two orders at the same instant. Inside a rolled-back transaction, add an order for customer 1 with order 5's exact `order_date`; it sorts after order 5 by `order_id` and must show a gap of exactly 0.
- **What prints:** 4,362 rows; 3,924 have a gap and 438 first orders keep `NULL`, because subtracting from `NULL` gives `NULL`.
- **Customer 1:** every gap is 7.89 days. Casting both sides to `date` first would print 8, which counts calendar days crossed rather than time elapsed.
- **Range:** gaps run from 2.28 to 296.63 days, averaging 65.45. Frequent buyers have short, even gaps; customers with four orders spread them over many months.
- **Units:** `days_since_previous` is a plain number of days, not an `interval`. Multiply by 24 for hours, or select the raw subtraction if you want PostgreSQL's own `7 days 21:21:30` display.
- **Why the CTE:** a window function cannot be used inside another expression's `WHERE`, and naming `previous_order_date` once keeps the subtraction readable.

## Exercise 3: Query writing

**Prompt:** Show each promotion with the next promotion start date for the same product.

**Reasoning:** Partition by product and define a stable chronological order.

**Clause-by-clause reading:**

- `LEAD(pr.start_date) OVER (...)`: the start date of the following promotion.
- `PARTITION BY pr.product_id`: compares promotions only within the same product.
- `ORDER BY pr.start_date, pr.promotion_id` inside `OVER`: chronological, with the ID settling equal start dates.
- Outer `ORDER BY pr.product_id, pr.start_date, pr.promotion_id`: groups each product's promotions together.

```sql
SELECT
  pr.promotion_id,
  pr.product_id,
  pr.start_date,
  LEAD(pr.start_date) OVER (PARTITION BY pr.product_id ORDER BY pr.start_date, pr.promotion_id) AS next_promotion_start
FROM
  promotions AS pr
ORDER BY
  pr.product_id,
  pr.start_date,
  pr.promotion_id;
```

**Expected shape:** One row per promotion; last product promotion has NULL next date.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 3, attach `LEAD(pr.start_date) OVER (PARTITION BY pr.product_id ORDER BY pr.start_date, pr.promotion_id)` to each of the 200 `promotions` rows, which cover 200 different products.
- **Expected result/shape:** For sql-18 Exercise 3, return 200 rows, one per promotion, and every `next_promotion_start` is `NULL`, because no product has a second promotion; the first row is promotion 7 for product 1. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
- **Independent verification:** For sql-18 Exercise 3, confirm that `SELECT product_id FROM promotions GROUP BY product_id HAVING COUNT(*) > 1` returns no rows, which explains the 200 `NULL` values. Inside a rolled-back transaction, copy promotion 7 for product 1 with both dates moved 30 days later; promotion 7 must then show the copy's `start_date` as its next start, while the copy shows `NULL`, leaving 201 rows with 200 `NULL` values.
- **What prints:** 200 rows, one per promotion, covering products 1 to 285.
- **The surprise:** every product in this fixture has exactly one promotion, so each partition holds one row and `next_promotion_start` is `NULL` on all 200 rows. The query is still correct; the data simply has no "next" yet.
- **What `NULL` means here:** no later promotion is recorded for the product. It does not say the current promotion never ends; that is what `end_date`, which this query leaves out, records.
- **Proving it works:** inside `BEGIN`, insert a second promotion for product 1 that starts after promotion 7. Promotion 7 then shows the new start date, the new row shows `NULL`, and `ROLLBACK` removes the test row.

## Exercise 4: Prediction

**Prompt:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.

**Reasoning:** NULL means there is no prior observation; preserve that semantic state.

**Clause-by-clause reading:**

- `WITH sequenced AS (... LAG(o.order_id) OVER (...) AS previous_order_id ...)`: records the ID of each customer's previous order.
- `WHERE previous_order_id IS NULL`: keeps rows with no earlier order in their partition, the first orders. The filter must sit outside the CTE because `WHERE` runs before window functions.
- `ORDER BY customer_id`: one row per customer, so the customer ID alone is a unique sort key.

```sql
WITH sequenced AS (
  SELECT
    o.*,
    LAG(o.order_id) OVER (PARTITION BY o.customer_id ORDER BY o.order_date,
      o.order_id) AS previous_order_id
  FROM
    orders AS o
)
SELECT
  order_id,
  customer_id,
  order_date
FROM
  sequenced
WHERE
  previous_order_id IS NULL
ORDER BY
  customer_id;
```

**Expected shape:** One row per customer's first order.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 4, attach `LAG(o.order_id)` per customer, ordered by `o.order_date, o.order_id`, in the `sequenced` CTE, then keep the rows where `previous_order_id IS NULL`.
- **Expected result/shape:** For sql-18 Exercise 4, return 438 rows, one first order per buyer, with no rows for the 62 customers who never ordered; customer 1 returns order 1 and customer 500 returns order 4353. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
- **Independent verification:** For sql-18 Exercise 4, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MIN(order_date) FROM orders GROUP BY customer_id`; their `total_amount` values add up to 236703.47. `order_id`, `customer_id`, and `order_date` are all `NOT NULL`, so test with inserts instead: inside a rolled-back transaction, add an order for customer 1 dated one day before order 1 and an order for customer 8; the result must grow to 439 rows, and customer 1 must return the new order instead of order 1.
- **What prints:** 438 rows, one per customer who has ordered. The first three are order 1 (customer 1), order 6 (customer 2) and order 12 (customer 3).
- **Why `order_id` is lagged:** `order_id` is never `NULL` in a real row, so a `NULL` lag can only mean "no earlier row". Lagging a column that may itself be empty would blur that signal.
- **Filtering too early:** restricting `orders` to recent dates inside the CTE makes the earliest order in that range look like a first order. In our check a 90-day filter returned 290 such rows, none guaranteed to be a real first purchase.
- **The fake-date trap:** `COALESCE(LAG(order_date), '1900-01-01')` still finds 438 rows, but now a later gap calculation would report a 126-year wait.

## Exercise 5: Debugging

**Prompt:** Compute month-over-month stored-revenue change after aggregating to month grain.

**Reasoning:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.

**Clause-by-clause reading:**

- `WITH monthly AS (... GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'))`: one revenue row per UTC month; `::date` makes `month_start` a plain date.
- `compared AS (... LAG(revenue) OVER (ORDER BY month_start) ...)`: no partition, because all months form one sequence.
- `ROUND(revenue - previous_revenue, 2) AS revenue_change`: the month-over-month change, `NULL` for the first month.
- `ORDER BY month_start`: oldest month first.

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    SUM(o.total_amount) AS revenue
  FROM
    orders AS o
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
compared AS (
  SELECT
    month_start,
    revenue,
    LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM
    monthly
)
SELECT
  month_start,
  ROUND(revenue, 2) AS revenue,
  ROUND(previous_revenue, 2) AS previous_revenue,
  ROUND(revenue - previous_revenue, 2) AS revenue_change
FROM
  compared
ORDER BY
  month_start;
```

**Expected shape:** One row per month with nullable first change.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 5, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then apply `LAG(revenue) OVER (ORDER BY month_start)` to those monthly rows and compute `revenue_change = revenue - previous_revenue`.
- **Expected result/shape:** For sql-18 Exercise 5, return 46 rows, one per UTC month with orders; on a fixture loaded on 2026-11-25 the first row is `2023-02-01` with revenue 1203.26 and `NULL` comparisons, and the last is the partial month `2026-11-01` with 85364.67, a change of -84814.46 from 170179.13. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
- **Independent verification:** For sql-18 Exercise 5, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `revenue_change`, and the `revenue` values add up to 2355646.89, the total of `orders.total_amount`.
- **What prints:** 46 rows in our check, February 2023 to November 2026. The first row has `NULL` previous revenue and change; March 2023 rises by 600.17 to 1,803.43.
- **Reconciliation:** the 46 monthly revenues add up to 2,355,646.89, the total of `orders.total_amount`, so no order is lost or counted twice.
- **The broken version:** applying `LAG` directly to `orders` returns 4,362 rows comparing each order with the one before it; no month total appears anywhere.
- **Reading the last row:** the newest month is incomplete, so its large drop (-84,814.46 in our check) says more about the date of the load than about sales.

## Exercise 6: Extension

**Prompt:** Compare each product price with the next higher price in its category.

**Reasoning:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.

**Clause-by-clause reading:**

- `LEAD(p.price) OVER (...)`: the price of the next product in the sequence.
- `PARTITION BY p.category`: six sequences of 50 products.
- `ORDER BY p.price, p.product_id` inside `OVER`: cheapest first; the ID would decide between equal prices.
- Outer `ORDER BY p.category, p.price, p.product_id`: prints each category's ladder from cheapest to dearest.

```sql
SELECT
  p.product_id,
  p.category,
  p.price,
  LEAD(p.price) OVER (PARTITION BY p.category ORDER BY p.price, p.product_id) AS next_price
FROM
  products AS p
ORDER BY
  p.category,
  p.price,
  p.product_id;
```

**Expected shape:** One row per product with nullable next price.

### Reasoning and verification

- **Inputs/evidence:** For sql-18 Exercise 6, attach `LEAD(p.price) OVER (PARTITION BY p.category ORDER BY p.price, p.product_id)` to each of the 300 `products` rows across 6 categories.
- **Expected result/shape:** For sql-18 Exercise 6, return 300 rows, one per product, with `next_price` `NULL` only on the 6 most expensive products, one per category; `Apparel` starts with product 1 at 10.37 followed by 12.59, and `Sports` ends with product 299 at 120.63. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
- **Independent verification:** For sql-18 Exercise 6, confirm 294 non-null `next_price` values and that `next_price - price` is exactly 2.22 on all of them, because each category's prices rise in even steps. Inside a rolled-back transaction, set product 7's price to 10.37; product 1 must then show a `next_price` of 10.37 (the tie is broken by `p.product_id`) and product 7 must show 14.81.
- **What prints:** 300 rows. Apparel starts at 10.37 (product 1) with `next_price` 12.59, then 12.59 to 14.81, and so on.
- **A regular ladder:** within every category consecutive prices differ by exactly 2.22, so every non-blank `next_price - price` is 2.22.
- **The six blanks:** the most expensive product in each category has no next price, from product 295 (Apparel, 119.15) to product 300 (Books, 121.00).
- **Same answer with `LAG`:** reverse the window to `ORDER BY p.price DESC, p.product_id DESC` and `LAG(p.price)` returns the same next price on every row. Flipping the order swaps the two functions.
- **Ties:** no category has two equal prices, so `p.product_id` never decides anything in this data; it is there so the answer stays fixed if prices are ever edited.

## Final self-check

- Why do 438 orders, not 500, have no previous order date?
- What changes in Example 1 if `PARTITION BY customer_id` is removed?
- Why does Exercise 3 print `NULL` on every row, and how would you show that the query still works?
- When is `LAG(revenue, 12)` not the same as "the same month last year"?
- Why must Exercise 4's `IS NULL` filter sit outside the CTE?
