# Day 17: Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK (Companion Guide)

## How to run this lesson

Open `./classroom`, pick PostgreSQL, select **sql-17** and press **Whole SQL lesson (psql)**. The script opens a transaction on `advanced_sql_training`, sets the search path, prints two result blocks and rolls back: the 30 biggest-spending customers with three rank columns side by side, then 50 employees ranked by salary inside their department. Nothing is written.

Your editable copy lives at
`.learning/sql/sql-17/lesson/workspace/sql/postgres-60day/day17_rank_functions.sql`.
Add your exercise queries below the two examples and rerun the whole file; `psql` with `ON_ERROR_STOP` halts at the first failing statement, so an error in Exercise 2 means Exercises 3 to 6 never ran. Use **SQL snippet** when you only want to rerun one query.

Course-table loading, resets and the classroom buttons are explained once in the [classroom section](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) of the study guide. The [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is optional.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 16; window-function fundamentals](day16_window_functions_fundamentals.md)
- **Artifacts:** [learner SQL](../day17_rank_functions.sql) ·
  [solution reasoning](../solutions/day17_solutions.md) ·
  [executable solution](../solutions/day17_solutions.sql)

## A beginner's mental model for this lesson

A ranking function reads the rows in a window, sorts them by the window's `ORDER BY`, and writes a position next to every row. It never removes a row: Example 1 ranks all 500 customers before `LIMIT 30` trims the display, and Exercise 1 numbers all 4,362 orders. The three functions differ only when two rows sort as equal. Those rows are **peer rows**, and the fixture has real ones: customers 51 and 428 both spent exactly 8,970.6735.

On those two customers, `ROW_NUMBER` hands out 11 and 12 because it must give every row a different number, `RANK` gives both 11 and then jumps to 13 (a **gap rank**), and `DENSE_RANK` gives both 11 and continues with 12 (a **dense rank**). Which answer is right depends on the question. "Exactly ten customers for a prize" needs `ROW_NUMBER` with a tie-breaker such as `customer_id`; "everyone who placed in the top three spending levels" needs `DENSE_RANK`.

Filtering on a rank takes two steps, because a window value does not exist yet when `WHERE` runs. Compute the rank in a CTE or subquery, then filter the outer query with `WHERE rank_col <= 3`. Exercises 3, 5 and 6 all follow that shape.

## Two worked SQL examples

### Example 1

```sql
WITH cust_rev AS (
  SELECT
    c.customer_id,
    c.full_name,
    COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0) AS revenue
  FROM
    customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    c.customer_id,
    c.full_name
)
SELECT
  customer_id,
  full_name,
  revenue,
  ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_id) AS row_num,
  RANK() OVER (ORDER BY revenue DESC) AS rank_pos,
  DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_pos
FROM
  cust_rev
ORDER BY
  revenue DESC,
  customer_id
LIMIT 30;
```

**How to read it:** `cust_rev` collapses order lines to one revenue figure per customer. Because both joins are `LEFT JOIN`, all 500 customers survive, and `COALESCE` turns the 62 Brazilian customers' NULL sums into 0. The outer query adds three positions computed over one shared ordering, `revenue DESC`. Only `ROW_NUMBER` also sorts by `customer_id`, so it is the only column guaranteed to be unique. `LIMIT 30` acts after every rank is already assigned.

**Expected result/shape:** 30 rows. Customer 181 leads with 9,502.2215, then customers 12 and 25. Rows 11 and 12 are customers 51 and 428, tied at 8,970.6735: `row_num` reads 11 and 12, while `rank_pos` and `dense_rank_pos` both read 11. From row 13 on, `rank_pos` equals `row_num` again but `dense_rank_pos` is one lower, so row 30 (customer 337, 8,480.1065) shows 30, 30 and 29. Outside the cap, the 62 zero-revenue customers would share rank 439 and dense rank 421.

### Example 2

```sql
SELECT
  e.department_id,
  d.name AS department,
  e.employee_id,
  e.full_name,
  e.salary,
  RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_rank
FROM
  employees e
  LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY
  department NULLS LAST,
  dept_rank,
  e.salary DESC,
  e.employee_id
LIMIT 50;
```

**How to read it:** `PARTITION BY e.department_id` restarts the ranking in every department, so each department has its own rank 1. `LEFT JOIN departments` only supplies the name; every employee has a department, so no NULL appears. The final `ORDER BY` sorts by department name, which puts Engineering first, not department 1 (Sales).

**Expected result/shape:** 50 rows: all 17 Engineering staff (ranks 1 to 17, led by Employee 98 at 47,760.62), all 17 in Finance, and 16 of HR's 17. The `LIMIT` cuts HR's rank 17, Employee 3, plus all of Marketing, Operations and Sales. All 100 salaries in this fixture are different, so `RANK` never ties here and behaves like `ROW_NUMBER`; tie behaviour only shows in Example 1 and in Exercise 4.

## Learning objectives

- Choose a ranking function whose tie behavior matches the requirement.
- Produce deterministic top-N-per-group results.

## Vocabulary and concepts

- **Peer rows:** rows equal on the window's `ORDER BY` expressions.
- **Gap rank:** `RANK` gives peers the same rank and leaves gaps afterward.
- **Dense rank:** `DENSE_RANK` gives peers the same rank without gaps.

## Worked example / walkthrough

Rank two products with equal revenue using `ROW_NUMBER`, `RANK`, and
`DENSE_RANK`. Add `product_id` as the last `ORDER BY` key when the requirement
is exactly five deterministic rows; omit that tie-breaker when equal metrics
must share a business rank.

## Practice assumptions and review method

- **Focus:** Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
- **Assumptions:** All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
- **Failure to watch for:** `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
- **Review loop:** before each run, write down which rows you expect to share a rank and what number comes after them; then find those rows in the output and check the gap (or its absence) by eye.

## Exercises

Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.

Exercises 1 and 5 number orders per customer, Exercises 2 and 3 rank product prices, Exercise 4 uses three hand-typed scores and Exercise 6 ranks salaries. Before each run, say whether ties are possible in that data and which function the wording asks for.

1. **Query writing:** Number each customer's orders from newest to oldest.
   **Progressive hint:** Partition by customer and use order date plus order ID as a unique descending order.
   **Your forecast:** how many rows print, and what number does customer 1's order from 2026-11-17 get?
   **Inputs/evidence:** For sql-17 Exercise 1, number each of the 4,362 `orders` rows with `ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, o.order_id DESC)`; the 438 buyers have 4 to 16 orders each.
   **Expected result/shape:** For sql-17 Exercise 1, return 4,362 rows, one per order, where each customer's numbers run from 1 up to that customer's order count; customer 1's orders 5, 4, 3, 2, and 1 get numbers 1 to 5, and the 33 customers with 16 orders, such as customer 12, reach 16. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
   **Verify:** For sql-17 Exercise 1, confirm that exactly 438 rows have `recency_number` 1, the maximum is 16, and each customer's maximum equals `COUNT(*)` from `orders` grouped by `customer_id`. All `order_date` values are distinct, so inside a rolled-back transaction copy order 5's `order_date` onto order 3; customer 1 must then number orders 5, 3, 4, 2, 1 as 1 to 5, because `o.order_id DESC` breaks the tie.
2. **Query writing:** Rank products by price within category using both `RANK` and `DENSE_RANK`.
   **Progressive hint:** Rank only on price so equal prices tie; order the final display by product ID.
   **Your forecast:** each category has 50 products at 50 different prices. Will the two rank columns ever disagree?
   **Inputs/evidence:** For sql-17 Exercise 2, rank the 300 `products` within each of the 6 categories (50 products each) by `p.price DESC`, once with `RANK()` and once with `DENSE_RANK()`.
   **Expected result/shape:** For sql-17 Exercise 2, return 300 rows, one per product; `Apparel` starts with product 295 at 119.15, 289 at 116.93, and 283 at 114.71 ranked 1, 2, and 3, and both rank columns end at 50 in every category. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
   **Verify:** For sql-17 Exercise 2, confirm 300 rows and zero rows where `price_rank <> dense_price_rank`, since every category has 50 distinct prices. Inside a rolled-back transaction, set product 289's price to 119.15; `Apparel` must then show products 289 and 295 at rank 1 and dense rank 1, product 283 at rank 3 but dense rank 2, and product 277 at rank 4 but dense rank 3.
3. **Query writing:** Return the three highest-priced products per category, including price ties.
   **Progressive hint:** Compute `DENSE_RANK` in a CTE and filter outside.
   **Your forecast:** with six categories and no repeated prices, how many rows come back? What would change if two Apparel products shared the top price?
   **Inputs/evidence:** For sql-17 Exercise 3, apply `DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC)` inside the `ranked` CTE, then keep `price_rank <= 3` in the outer query.
   **Expected result/shape:** For sql-17 Exercise 3, return 18 rows, three per category for the 6 categories; `Apparel` keeps products 295, 289, and 283, and `Books` keeps 300 at 121.00, 294 at 118.78, and 288 at 116.56. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
   **Verify:** For sql-17 Exercise 3, confirm 18 rows, no `price_rank` above 3, and that each kept price is among the three highest from `SELECT category, price FROM products ORDER BY category, price DESC`. Inside a rolled-back transaction, set product 289's price to 119.15; the result must grow to 19 rows, with `Apparel` returning 289 and 295 at rank 1, 283 at rank 2, and 277 at rank 3.
4. **Prediction:** Compare row number, rank, and dense rank on values 100, 100, and 90.
   **Progressive hint:** Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
   **Your forecast:** write the three columns for the row scoring 90 before you run anything.
   **Inputs/evidence:** For sql-17 Exercise 4, rank the three-row `VALUES` fixture `(1, 100), (2, 100), (3, 90)` by `score DESC` with `ROW_NUMBER()` (tie broken by `sample_id`), `RANK()`, and `DENSE_RANK()`.
   **Expected result/shape:** For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
   **Verify:** For sql-17 Exercise 4, check by hand that samples 1 and 2 tie at 100, so only `row_number_value` separates them (1 and 2), while sample 3 gets 3, 3, and 2. Add `(4, 90)` to the fixture; the four rows must read 1/1/1, 2/1/1, 3/3/2, and 4/3/2.
5. **Debugging:** Return exactly one latest order per customer even when timestamps tie.
   **Progressive hint:** Use row number with the unique order ID as final tie-breaker.
   **Your forecast:** how many customers have at least one order, and therefore how many rows should print?
   **Inputs/evidence:** For sql-17 Exercise 5, number orders with `ROW_NUMBER()` partitioned by `o.customer_id` and ordered by `o.order_date DESC, o.order_id DESC` in the `numbered` CTE, then keep `recency_number = 1`.
   **Expected result/shape:** For sql-17 Exercise 5, return 438 rows, one latest order per buyer, with no rows for the 62 customers who never ordered; customer 1's row is order 5 for 105.84 and customer 500's is order 4362 for 951.76. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
   **Verify:** For sql-17 Exercise 5, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MAX(order_date) FROM orders GROUP BY customer_id` on both columns; the kept orders total 252375.44. Inside a rolled-back transaction, copy order 5's `order_date` onto order 3; customer 1 must still return order 5, because `o.order_id DESC` breaks the tie.
6. **Extension:** Rank employee salaries within department and show only the top two distinct salary levels.
   **Progressive hint:** Dense rank includes all employees tied at either of the top two salary values.
   **Your forecast:** are there salary ties in this table? Use your answer to predict the row count.
   **Inputs/evidence:** For sql-17 Exercise 6, apply `DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC)` to the 100 `employees` rows in the `ranked` CTE, then keep `salary_rank <= 2`.
   **Expected result/shape:** For sql-17 Exercise 6, return 12 rows, two per department for the 6 departments; department 1 keeps employee 97 at 47681.43 and employee 91 at 47206.29, and department 4 keeps employee 100 at 47919.00 and employee 94 at 47443.86. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
   **Verify:** For sql-17 Exercise 6, confirm 12 rows and that each department's two salaries are its two highest from `SELECT department_id, salary FROM employees ORDER BY department_id, salary DESC`; no department has a salary tie. Inside a rolled-back transaction, set employee 91's salary to 47681.43; the result must grow to 13 rows, with employees 91 and 97 at rank 1 and employee 85 (46731.15) at rank 2 in department 1.

## Common mistakes and how to recover

- **Picking the function by habit:** `RANK` and `DENSE_RANK` agree until the first tie. In Example 1 they part ways at customers 51 and 428, and by row 30 they differ by one. A "top three levels" filter written with `RANK <= 3` and with `DENSE_RANK <= 3` can return different customers.
- **Adding the tie-breaker to `RANK`:** `RANK() OVER (ORDER BY revenue DESC, customer_id)` gives customers 51 and 428 ranks 11 and 12, so the tie the business asked to keep disappears. Put the unique key only in the `ROW_NUMBER` ordering.
- **`ROW_NUMBER` without a unique ordering:** for "latest order per customer", `ORDER BY order_date DESC` alone happens to work today because no customer has two orders at the same timestamp. One duplicate timestamp later, PostgreSQL may pick either row on each run. Add `order_id DESC`.
- **Filtering a window in `WHERE`:** `WHERE ROW_NUMBER() OVER (...) = 1` is an error, because windows are computed after `WHERE`. Wrap the ranking in a CTE first.
- **Forgetting zero-revenue customers:** an inner join in Example 1 ranks only 438 customers and the 62 Brazilian customers vanish from the bottom of the list instead of sharing rank 439.

If the whole script stopped partway, the study guide's [failure recovery notes](../../STUDY-GUIDE.md#recover-from-common-failures) explain how to restart cleanly.

## Self-check

- Is the requirement “exactly N rows” or “all rows tied in the top N ranks”?
- Does the ordering include a stable key where deterministic selection matters?

## Next step

Continue to [Day 18; LAG and LEAD](day18_lag_lead.md).

## Deep dive and reference

Learning objectives
- Assign row ordinals and ranks within partitions using ORDER BY
- Choose the correct rank function for ties and pagination
- Build top-k per group, leaderboards, and tie-aware analytics

Why this matters
Ranking underpins “top N per X”, de-duplicating, and cohort benchmarking. Picking the right function controls tie behavior, which changes results and business meaning.

Core concepts and deep dive
- ROW_NUMBER() OVER (PARTITION BY k ORDER BY t): assigns 1,2,3… with no ties (deterministic if ORDER BY unique). Use for de-duplication (keep first per key).
- RANK(): equal sort values receive the same rank; leaves gaps after ties (1,1,3…).
- DENSE_RANK(): equal values share rank without gaps (1,1,2…).
- ORDER BY determinism: When values tie, add a tiebreaker column to produce stable ordering (e.g., ORDER BY amt DESC, order_id ASC).

Patterns
- Top-k per group: WHERE rn <= k after wrapping ROW_NUMBER in a subquery/CTE.
- Category leaders: DENSE_RANK by revenue within category; pick rank <= 3 for top-3 allowing ties.
- Latest records per entity: ROW_NUMBER ordered by timestamp DESC; keep rn=1.

Pitfalls
- Using RANK when you need exactly k rows per group; ties may exceed k (use ROW_NUMBER) or allow overflow intentionally.
- Non-deterministic ordering when ORDER BY is not unique; results can fluctuate.

Further reading
- Ranking: https://www.postgresql.org/docs/17/functions-window.html#FUNCTIONS-WINDOW-TABLE

## Ask an AI tutor about this lesson

A tutor is optional. One useful exercise: ask it to give you five made-up scores with two ties and quiz you on all three rank columns before showing the answer. The prompt below points at the guide and the answer-free learner file and keeps `solutions/` closed; setup notes are in the study guide's [tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-17: Ranking with ROW_NUMBER, RANK, and DENSE_RANK.

I have completed the direct catalog prerequisite: `sql-16`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day17_rank_functions.md
- Answer-free learner SQL: sql/postgres-60day/day17_rank_functions.sql

Key terms to teach in context: Peer rows, Gap rank, Dense rank. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Rank two products with equal revenue using `ROW_NUMBER`, `RANK`, and `DENSE_RANK`. Add `product_id` as the last `ORDER BY` key when the requirement is exactly five deterministic rows; omit that tie-breaker when equal metrics must share a business rank.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-17/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
