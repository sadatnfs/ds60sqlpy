# Day 17 solutions: Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Four answers rank real tables (`orders`, `products`, `employees`), one ranks three typed-in scores, and two of them filter on the rank in an outer query. After your own attempt, run the companion file:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day17_solutions.sql
```

It sets `search_path` to `training, public` and ends with `ROLLBACK`. Row counts to expect, in order: 4,362, 300, 18, 3, 438 and 12. None of them depend on today's date. The prompts match [the learner file](../day17_rank_functions.sql) one for one; the study guide's [solution reading notes](../../STUDY-GUIDE.md#read-a-solution) cover how to compare your query with these.

## Reading contract

- **Focus:** Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
- **Assumptions:** All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
- **Primary pitfall:** `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
- **Safety:** every statement here is a `SELECT`, and the file still runs inside `BEGIN`/`ROLLBACK`, so a tied test row you insert to try the edge cases disappears when it ends.

## Exercise 1: Query writing

**Prompt:** Number each customer's orders from newest to oldest.

**Reasoning:** Partition by customer and use order date plus order ID as a unique descending order.

**Clause-by-clause reading:**

- `FROM orders AS o`: 4,362 orders, one row each.
- `ROW_NUMBER() OVER (PARTITION BY o.customer_id ...)`: restarts the count at 1 for each customer.
- `ORDER BY o.order_date DESC, o.order_id DESC` inside `OVER`: newest first, with the order ID deciding any timestamp tie.
- Outer `ORDER BY o.customer_id, recency_number`: groups each customer's orders together, newest at the top.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, o.order_id DESC) AS recency_number
FROM
  orders AS o
ORDER BY
  o.customer_id,
  recency_number;
```

**Expected shape:** One row per order with sequence starting at one per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 1, number each of the 4,362 `orders` rows with `ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, o.order_id DESC)`; the 438 buyers have 4 to 16 orders each.
- **Expected result/shape:** For sql-17 Exercise 1, return 4,362 rows, one per order, where each customer's numbers run from 1 up to that customer's order count; customer 1's orders 5, 4, 3, 2, and 1 get numbers 1 to 5, and the 33 customers with 16 orders, such as customer 12, reach 16. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
- **Independent verification:** For sql-17 Exercise 1, confirm that exactly 438 rows have `recency_number` 1, the maximum is 16, and each customer's maximum equals `COUNT(*)` from `orders` grouped by `customer_id`. All `order_date` values are distinct, so inside a rolled-back transaction copy order 5's `order_date` onto order 3; customer 1 must then number orders 5, 3, 4, 2, 1 as 1 to 5, because `o.order_id DESC` breaks the tie.
- **What prints:** 4,362 rows for the 438 customers who ordered. Customer 1 has five orders; order 5 (2026-11-17) gets 1 and order 1 (2026-10-16) gets 5.
- **Proof query:** `SELECT COUNT(*) FILTER (WHERE recency_number = 1)` over this result should equal 438, one newest order per customer.
- **Does the tie-breaker matter here?** Not in this fixture: no customer has two orders with the same `order_date`. It still belongs in the query, because a future duplicate timestamp would otherwise make the numbering change between runs.
- **Wrong function:** `RANK` would give two same-timestamp orders the same number, so "order number 1" could mean two rows.
- **Busiest partitions:** customers 12, 25 and 38 each have 16 orders, the most in the fixture, so their numbering runs to 16; the smallest partitions stop at 4.

## Exercise 2: Query writing

**Prompt:** Rank products by price within category using both `RANK` and `DENSE_RANK`.

**Reasoning:** Rank only on price so equal prices tie; order the final display by product ID.

**Clause-by-clause reading:**

- `FROM products AS p`: 300 products in 6 categories.
- `RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC)`: position by price within the category, with gaps after ties.
- `DENSE_RANK()` over the same window: the same position, without gaps.
- Outer `ORDER BY p.category, p.price DESC, p.product_id`: product ID only fixes display order; it is not part of either rank.

```sql
SELECT
  p.product_id,
  p.category,
  p.price,
  RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC) AS price_rank,
  DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC) AS dense_price_rank
FROM
  products AS p
ORDER BY
  p.category,
  p.price DESC,
  p.product_id;
```

**Expected shape:** One row per product with two rank semantics.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 2, rank the 300 `products` within each of the 6 categories (50 products each) by `p.price DESC`, once with `RANK()` and once with `DENSE_RANK()`.
- **Expected result/shape:** For sql-17 Exercise 2, return 300 rows, one per product; `Apparel` starts with product 295 at 119.15, 289 at 116.93, and 283 at 114.71 ranked 1, 2, and 3, and both rank columns end at 50 in every category. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
- **Independent verification:** For sql-17 Exercise 2, confirm 300 rows and zero rows where `price_rank <> dense_price_rank`, since every category has 50 distinct prices. Inside a rolled-back transaction, set product 289's price to 119.15; `Apparel` must then show products 289 and 295 at rank 1 and dense rank 1, product 283 at rank 3 but dense rank 2, and product 277 at rank 4 but dense rank 3.
- **What prints:** 300 rows, 50 per category, ranks 1 to 50. Apparel starts with product 295 at 119.15.
- **The surprise in this data:** every category has 50 different prices, so `price_rank` and `dense_price_rank` are equal on all 300 rows. The query is still right; the data simply has no ties to show the difference.
- **Testing the tie rule:** inside a transaction, `UPDATE products SET price = 119.15 WHERE product_id = 289`. Apparel's ranks now read 1, 1, 3 under `RANK` and 1, 1, 2 under `DENSE_RANK`. Roll back afterwards.
- **A common slip:** writing `ORDER BY p.price DESC, p.product_id` inside `OVER` makes the tie impossible, which defeats the purpose of using rank functions.

## Exercise 3: Query writing

**Prompt:** Return the three highest-priced products per category, including price ties.

**Reasoning:** Compute `DENSE_RANK` in a CTE and filter outside.

**Clause-by-clause reading:**

- `ranked`: every product plus its `DENSE_RANK` by price within its category, still 300 rows.
- Outer `WHERE price_rank <= 3`: keeps the top three price levels per category. It works here because the rank already exists as a column.
- `ORDER BY category, price_rank, product_id`: tied products, if any, list in ID order.

```sql
WITH ranked AS (
  SELECT
    p.*,
    DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC) AS price_rank
  FROM
    products AS p
)
SELECT
  product_id,
  name,
  category,
  price,
  price_rank
FROM
  ranked
WHERE
  price_rank <= 3
ORDER BY
  category,
  price_rank,
  product_id;
```

**Expected shape:** At least three price levels per category where available.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 3, apply `DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC)` inside the `ranked` CTE, then keep `price_rank <= 3` in the outer query.
- **Expected result/shape:** For sql-17 Exercise 3, return 18 rows, three per category for the 6 categories; `Apparel` keeps products 295, 289, and 283, and `Books` keeps 300 at 121.00, 294 at 118.78, and 288 at 116.56. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
- **Independent verification:** For sql-17 Exercise 3, confirm 18 rows, no `price_rank` above 3, and that each kept price is among the three highest from `SELECT category, price FROM products ORDER BY category, price DESC`. Inside a rolled-back transaction, set product 289's price to 119.15; the result must grow to 19 rows, with `Apparel` returning 289 and 295 at rank 1, 283 at rank 2, and 277 at rank 3.
- **What prints:** 18 rows, three per category. Apparel shows 295 (119.15), 289 (116.93) and 283 (114.71). The most expensive product overall is 300 in Books at 121.00.
- **Ties widen the answer:** with no repeated prices you get exactly 3 per category. If two Apparel products shared 119.15, Apparel would return 4 rows, both tied products at level 1 plus the next two levels. That is what "including price ties" asks for.
- **`ROW_NUMBER` instead:** always 18 rows, even with ties, and one of the tied products would be dropped based on whatever breaks the tie.
- **Where the filter goes:** `WHERE DENSE_RANK() OVER (...) <= 3` in a single query is rejected, because window functions are not allowed in `WHERE`.

## Exercise 4: Prediction

**Prompt:** Compare row number, rank, and dense rank on values 100, 100, and 90.

**Reasoning:** Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.

**Clause-by-clause reading:**

- `VALUES (1, 100), (2, 100), (3, 90) AS sample (sample_id, score)`: three typed rows; samples 1 and 2 tie.
- `ROW_NUMBER() OVER (ORDER BY score DESC, sample_id)`: the only ordering that includes the ID.
- `RANK()` and `DENSE_RANK()` over `ORDER BY score DESC`: the tie stays a tie.
- Outer `ORDER BY sample_id`: shows the samples in ID order, not rank order.

```sql
SELECT
  sample_id,
  score,
  ROW_NUMBER() OVER (ORDER BY score DESC, sample_id) AS row_number_value,
  RANK() OVER (ORDER BY score DESC) AS rank_value,
  DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_value
FROM (
  VALUES (1, 100),
    (2, 100),
    (3, 90)) AS sample (sample_id, score)
ORDER BY
  sample_id;
```

**Expected shape:** Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 4, rank the three-row `VALUES` fixture `(1, 100), (2, 100), (3, 90)` by `score DESC` with `ROW_NUMBER()` (tie broken by `sample_id`), `RANK()`, and `DENSE_RANK()`.
- **Expected result/shape:** For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
- **Independent verification:** For sql-17 Exercise 4, check by hand that samples 1 and 2 tie at 100, so only `row_number_value` separates them (1 and 2), while sample 3 gets 3, 3, and 2. Add `(4, 90)` to the fixture; the four rows must read 1/1/1, 2/1/1, 3/3/2, and 4/3/2.
- **What prints:** sample 1: 1, 1, 1. Sample 2: 2, 1, 1. Sample 3 (score 90): 3, 3, 2.
- **Reading the last row:** `RANK` skips to 3 because two rows sit above it. `DENSE_RANK` gives 2 because only one distinct score sits above it.
- **Moving the ID:** add `sample_id` to the `RANK` ordering and you get 1, 2, 3, identical to `ROW_NUMBER`; the tie is gone.
- **Edge case:** a fourth row scoring 100 changes the 90 row to `RANK` 4 and leaves its `DENSE_RANK` at 2.

## Exercise 5: Debugging

**Prompt:** Return exactly one latest order per customer even when timestamps tie.

**Reasoning:** Use row number with the unique order ID as final tie-breaker.

**Clause-by-clause reading:**

- `numbered`: every order with its newest-first number per customer, as in Exercise 1.
- Outer `WHERE recency_number = 1`: one row per customer, chosen by the number rather than by a date comparison.
- `ORDER BY customer_id`.

```sql
WITH numbered AS (
  SELECT
    o.*,
    ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC,
      o.order_id DESC) AS recency_number
  FROM
    orders AS o
)
SELECT
  order_id,
  customer_id,
  order_date,
  total_amount
FROM
  numbered
WHERE
  recency_number = 1
ORDER BY
  customer_id;
```

**Expected shape:** At most one row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 5, number orders with `ROW_NUMBER()` partitioned by `o.customer_id` and ordered by `o.order_date DESC, o.order_id DESC` in the `numbered` CTE, then keep `recency_number = 1`.
- **Expected result/shape:** For sql-17 Exercise 5, return 438 rows, one latest order per buyer, with no rows for the 62 customers who never ordered; customer 1's row is order 5 for 105.84 and customer 500's is order 4362 for 951.76. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
- **Independent verification:** For sql-17 Exercise 5, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MAX(order_date) FROM orders GROUP BY customer_id` on both columns; the kept orders total 252375.44. Inside a rolled-back transaction, copy order 5's `order_date` onto order 3; customer 1 must still return order 5, because `o.order_id DESC` breaks the tie.
- **What prints:** 438 rows, one per customer with orders. The oldest "latest order" belongs to customer 429 (2026-02-01); the newest is from 2026-11-23.
- **The tempting shortcut:** joining `orders` to `SELECT customer_id, MAX(order_date)` also returns 438 rows today, but returns two rows for a customer whose two newest orders share a timestamp. The `ROW_NUMBER` version cannot.
- **Seeing the bug:** drop `o.order_id DESC` from the window ordering. The result is identical on this data, which is exactly why the bug survives testing; insert a second order for customer 1 at 2026-11-17 09:47:32.140775 inside a transaction to expose it.
- **Customers with no orders:** the 62 Brazilian customers are absent, since the query starts from `orders`.

## Exercise 6: Extension

**Prompt:** Rank employee salaries within department and show only the top two distinct salary levels.

**Reasoning:** Dense rank includes all employees tied at either of the top two salary values.

**Clause-by-clause reading:**

- `ranked`: every employee with a `DENSE_RANK` by salary within the department.
- Outer `WHERE salary_rank <= 2`: the top two salary levels, keeping everyone tied at either level.
- `ORDER BY department_id, salary_rank, employee_id`.

```sql
WITH ranked AS (
  SELECT
    e.*,
    DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS salary_rank
  FROM
    employees AS e
)
SELECT
  employee_id,
  full_name,
  department_id,
  salary,
  salary_rank
FROM
  ranked
WHERE
  salary_rank <= 2
ORDER BY
  department_id,
  salary_rank,
  employee_id;
```

**Expected shape:** Top two salary levels per department.

### Reasoning and verification

- **Inputs/evidence:** For sql-17 Exercise 6, apply `DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC)` to the 100 `employees` rows in the `ranked` CTE, then keep `salary_rank <= 2`.
- **Expected result/shape:** For sql-17 Exercise 6, return 12 rows, two per department for the 6 departments; department 1 keeps employee 97 at 47681.43 and employee 91 at 47206.29, and department 4 keeps employee 100 at 47919.00 and employee 94 at 47443.86. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
- **Independent verification:** For sql-17 Exercise 6, confirm 12 rows and that each department's two salaries are its two highest from `SELECT department_id, salary FROM employees ORDER BY department_id, salary DESC`; no department has a salary tie. Inside a rolled-back transaction, set employee 91's salary to 47681.43; the result must grow to 13 rows, with employees 91 and 97 at rank 1 and employee 85 (46731.15) at rank 2 in department 1.
- **What prints:** 12 rows, two per department. Department 1 lists Employee 97 (47,681.43) then 91 (47,206.29); department 2 lists 98 then 92.
- **Why exactly two:** all 100 salaries differ, so each level holds one person. Salaries grow with employee ID in this fixture, which is why the top earners are the highest IDs and the department heads (Employees 1 to 6) rank last.
- **Count to compare:** the same query with `ROW_NUMBER` also returns 12 here. Give two Sales staff the same top salary inside a transaction and the dense-rank version returns 3 Sales rows while `ROW_NUMBER` still returns 2.
- **Distinct levels versus people:** "top two salary levels" counts levels, so `RANK <= 2` would be wrong after a two-way tie at the top: both tied people get 1 and the next person gets 3, which falls outside the filter.

## Final self-check

- In Example 1, which three numbers do customers 51 and 428 get, and what does row 13 show in each column?
- Why are `price_rank` and `dense_price_rank` equal on every row of Exercise 2?
- Exercise 5 gives the same answer with or without `order_id DESC`. Why keep it?
- Which function answers "everyone in the top two salary levels", and how many rows would one tie at the top add?
- Why must Exercises 3, 5 and 6 compute the rank in a CTE before filtering it?
