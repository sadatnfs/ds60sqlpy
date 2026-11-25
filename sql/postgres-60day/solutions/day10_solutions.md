# Day 10 solutions: DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each answer runs between `SAVEPOINT exercise_N` and `ROLLBACK TO SAVEPOINT exercise_N`, so its write is undone before the next exercise begins. Exercise 1 loads category revenue with `INSERT ... SELECT`, Exercise 2 raises 34 salaries, Exercise 3 deletes old unpaid orders, Exercise 4 runs one upsert twice, Exercise 5 changes five reviewed book prices and Exercise 6 applies staged prices with `UPDATE ... FROM`. Try them first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day10_solutions.sql
```

Look for the tags `INSERT 0 6`, `UPDATE 34`, `DELETE 362`, `INSERT 0 1` twice, `SELECT 5`, and `INSERT 0 3` followed by `UPDATE 3`. The script ends with `ROLLBACK`, and the excerpts below leave out its `SET search_path` line. The exercises match [the learner file](../day10_dml_with_subqueries.sql) one for one; the study guide has notes on [getting the most from a worked solution](../../STUDY-GUIDE.md#read-a-solution).

## Reading contract

- **Focus:** Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
- **Assumptions:** Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
- **Primary pitfall:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
- **Safety:** every write runs inside a savepoint that is rolled back, and the whole script ends with `ROLLBACK`, so the course tables keep their original rows.

## Exercise 1: Query writing

**Prompt:** Materialize category net revenue into a temporary table with `INSERT ... SELECT`.

**Reasoning:** Declare the temporary schema and aggregate source rows before inserting.

**Clause-by-clause reading:**

- `CREATE TEMP TABLE exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL) ON COMMIT DROP`: the target is declared first, with a key that allows one row per category.
- `INSERT INTO exercise_category_revenue (category, revenue) SELECT ...`: the column list pairs with the select list by position, so the category lands in `category` and the sum in `revenue`.
- `SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) ... GROUP BY p.category`: net revenue per category over every order line, stored unrounded.
- `ROUND(revenue, 2) AS revenue ... ORDER BY revenue DESC, category`: rounding happens only for display.
- `SAVEPOINT exercise_1` and `ROLLBACK TO SAVEPOINT exercise_1`: remove the table and its rows before Exercise 2.

```sql
SAVEPOINT exercise_1;

CREATE TEMP TABLE exercise_category_revenue (
  category text PRIMARY KEY,
  revenue numeric NOT NULL
) ON COMMIT DROP;

INSERT INTO exercise_category_revenue (category, revenue)
SELECT
  p.category,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount))
FROM
  order_items AS oi
  JOIN products AS p ON p.product_id = oi.product_id
GROUP BY
  p.category;

SELECT
  category,
  ROUND(revenue, 2) AS revenue
FROM
  exercise_category_revenue
ORDER BY
  revenue DESC,
  category;

ROLLBACK TO SAVEPOINT exercise_1;
```

**Expected shape:** One temporary row per product category.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 1, aggregate net revenue, `unit_price * quantity * (1 - discount)`, from `order_items` joined to `products` by `p.category`, and load it with `INSERT ... SELECT` into the temporary table `exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL)`.
- **Expected result/shape:** For sql-10 Exercise 1, expected output: the command tag `INSERT 0 6`, then six rows, one per product category, with columns `category` and `revenue` (rounded to 2 places), ordered by `revenue DESC, category`; `Sports` leads on the course seed.
- **Independent verification:** For sql-10 Exercise 1, rerun the aggregate as a plain `SELECT` and compare each category's revenue with the stored row; confirm that `SELECT COUNT(DISTINCT p.category) FROM order_items oi JOIN products p ON p.product_id = oi.product_id` returns 6, and that the savepoint rollback leaves no `exercise_category_revenue` table.
- **What prints:** `CREATE TABLE`, `INSERT 0 6`, then six rows from Sports at 397,427.70 down to Books at 386,192.77. The stored Sports value is 397,427.7030; only the display is rounded.
- **Why declare the table first:** the learner file's `CREATE TEMP TABLE ... AS SELECT` is shorter but cannot declare a primary key. With the key, running the same `INSERT ... SELECT` again fails with SQLSTATE `23505` instead of quietly adding a second row for every category.
- **Checking the load:** run the `SELECT ... GROUP BY p.category` on its own. It returns the same six sums, and `COUNT(DISTINCT p.category)` over the same join is 6.
- **After the savepoint rollback:** the `CREATE` is undone too, so `SELECT * FROM exercise_category_revenue` fails with `relation "exercise_category_revenue" does not exist`.

## Exercise 2: Query writing

**Prompt:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.

**Reasoning:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.

**Clause-by-clause reading:**

- `UPDATE employees AS e SET salary = ROUND(e.salary * 1.05, 2)`: a 5% raise, rounded to cents.
- `WHERE e.department_id IN (SELECT d.department_id FROM departments AS d WHERE d.name IN ('Sales', 'Engineering'))`: the subquery turns two names into department IDs 1 and 2.
- `RETURNING e.employee_id, e.full_name, e.salary`: the new salary of each changed employee.

```sql
SAVEPOINT exercise_2;

UPDATE
  employees AS e
SET
  salary = ROUND(e.salary * 1.05, 2)
WHERE
  e.department_id IN (
    SELECT
      d.department_id
    FROM
      departments AS d
    WHERE
      d.name IN ('Sales', 'Engineering'))
RETURNING
  e.employee_id,
  e.full_name,
  e.salary;

ROLLBACK TO SAVEPOINT exercise_2;
```

**Expected shape:** Affected employee rows only; no change persists.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 2, raise `salary` by 5% (rounded to 2 places) for employees whose `department_id` belongs to the `departments` named `Sales` or `Engineering`, selected with an `IN (SELECT ...)` subquery, inside a savepoint.
- **Expected result/shape:** For sql-10 Exercise 2, expected output: the command tag `UPDATE 34` and 34 returned rows with columns `employee_id`, `full_name`, and `salary` (the new value); after `ROLLBACK TO SAVEPOINT`, no salary has changed.
- **Independent verification:** For sql-10 Exercise 2, before the update, count the targets with `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` (34) and compare with the command tag; after the rollback, compare one returned `employee_id`'s salary with its original value.
- **What prints:** 34 rows and `UPDATE 34`, seventeen employees from each department. Employee 1 shows 42,083.15, up from 40,079.19.
- **Row order:** a bare `RETURNING` has no `ORDER BY`, so rows come back in whatever order the update visited them. The learner file wraps the update in a CTE to sort by `employee_id`.
- **`ROUND` here versus the learner file:** the learner version leaves it out yet stores the same 42,083.15, because `salary` is `numeric(10,2)` and assignment rounds to the column's scale. Writing `ROUND` states the rule instead of relying on the column type.
- **A join form:** `UPDATE employees AS e SET ... FROM departments AS d WHERE d.department_id = e.department_id AND d.name IN (...)` changes the same 34 rows, since each employee matches one department.
- **A typo test:** with `'Engineers'` the tag becomes `UPDATE 17`, Sales only, and the 34-row preview exposes it.

## Exercise 3: Query writing

**Prompt:** Delete orders older than one year only when no payment exists, returning candidate keys.

**Reasoning:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.

**Clause-by-clause reading:**

- `DELETE FROM orders AS o WHERE o.order_date < CURRENT_TIMESTAMP - INTERVAL '1 year'`: orders placed more than a year before the run.
- `AND NOT EXISTS (SELECT 1 FROM payments AS p WHERE p.order_id = o.order_id)`: checked per order; keeps only orders with no payment row.
- `RETURNING o.order_id, o.customer_id, o.order_date`: the removed orders.

```sql
SAVEPOINT exercise_3;

DELETE FROM orders AS o
WHERE o.order_date < CURRENT_TIMESTAMP - INTERVAL '1 year'
  AND NOT EXISTS (
    SELECT
      1
    FROM
      payments AS p
    WHERE
      p.order_id = o.order_id)
RETURNING
  o.order_id,
  o.customer_id,
  o.order_date;

ROLLBACK TO SAVEPOINT exercise_3;
```

**Expected shape:** Deleted-candidate order rows, then fully restored state.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 3, delete orders with `order_date` older than one year that have no row in `payments`, using a correlated `NOT EXISTS`, inside a savepoint.
- **Expected result/shape:** For sql-10 Exercise 3, expected output: a `DELETE` command tag and returned rows with columns `order_id`, `customer_id`, and `order_date`, all older than one year (362 rows on a freshly seeded database); after `ROLLBACK TO SAVEPOINT`, every order and its cascaded `order_items` are restored.
- **Independent verification:** For sql-10 Exercise 3, count the candidates first with the same `WHERE` clause in a `SELECT COUNT(*)` and compare with the command tag; after the rollback, confirm that `SELECT COUNT(*) FROM orders` is back to 4,362 and that a deleted `order_id` exists again.
- **What prints:** 362 rows and `DELETE 362` on a freshly loaded database. Of the 1,797 orders older than a year, 1,435 have a payment and stay; the 362 that go all have status `placed`, and the oldest is order 723 from March 2023.
- **The cascade:** `order_items` and `payments` reference `orders` with `ON DELETE CASCADE`, so this delete also removes 1,073 order lines (13,085 drops to 12,012). Count them with the same `WHERE` before deleting so the side effect is no surprise.
- **`NOT IN` instead:** `o.order_id NOT IN (SELECT order_id FROM payments)` also deletes 362, because `payments.order_id` is `NOT NULL`. If that column allowed NULLs, a single NULL would make `NOT IN` match nothing; `NOT EXISTS` has no such trap.
- **A moving cutoff:** `CURRENT_TIMESTAMP - INTERVAL '1 year'` is evaluated at run time, so the count grows as the loaded data ages. The learner file's `now() - interval '365 days'` gives the same cutoff except across a February 29, where the two differ by a day.
- **After the rollback:** `SELECT COUNT(*) FROM orders` is 4,362 again and order 207 is back.

## Exercise 4: Prediction

**Prompt:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.

**Reasoning:** A primary key supplies the conflict target; the second statement updates rather than inserts.

**Clause-by-clause reading:**

- `CREATE TEMP TABLE exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)`: the primary key is what `ON CONFLICT (source_key)` relies on.
- First `INSERT ... VALUES ('source_a', 10) ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value`: no row exists yet, so it inserts.
- Second statement with `12`: the key clashes, so the `DO UPDATE` branch runs. `EXCLUDED` is the row that was proposed, here `('source_a', 12)`.
- `SELECT ... ORDER BY source_key`: shows the final table.

```sql
SAVEPOINT exercise_4;

CREATE TEMP TABLE exercise_feed (
  source_key text PRIMARY KEY,
  source_value numeric NOT NULL
) ON COMMIT DROP;

INSERT INTO exercise_feed (source_key, source_value)
  VALUES ('source_a', 10)
ON CONFLICT (source_key)
  DO UPDATE SET
    source_value = EXCLUDED.source_value;

INSERT INTO exercise_feed (source_key, source_value)
  VALUES ('source_a', 12)
ON CONFLICT (source_key)
  DO UPDATE SET
    source_value = EXCLUDED.source_value;

SELECT
  source_key,
  source_value
FROM
  exercise_feed
ORDER BY
  source_key;

ROLLBACK TO SAVEPOINT exercise_4;
```

**Expected shape:** One row for `source_a` with the second value.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 4, create the temporary table `exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)` and run `INSERT ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value` twice for `source_a`, first with `10` and then with `12`.
- **Expected result/shape:** For sql-10 Exercise 4, expected output: both statements print `INSERT 0 1`, and the final `SELECT` returns one row ordered by `source_key` with columns `source_key` and `source_value`: `('source_a', 12)`.
- **Independent verification:** For sql-10 Exercise 4, confirm that `SELECT COUNT(*) FROM exercise_feed WHERE source_key = 'source_a'` returns 1 after the second run; add `RETURNING (xmax = 0) AS inserted` to each upsert to see `true` for the first run and `false` for the second.
- **What prints:** `INSERT 0 1` twice, then one row, `source_a | 12`. The tag still says `INSERT` when the conflict branch updated the row.
- **Telling the runs apart:** add `RETURNING (xmax = 0) AS inserted`; the first statement returns `t`, the second `f`. This leans on a PostgreSQL system column, so use it for debugging, not for application logic.
- **`DO NOTHING` instead:** the second statement prints `INSERT 0 0` and the table keeps 10. That is idempotent too, but the newer value is dropped.
- **Without the key:** remove `PRIMARY KEY` and the very first upsert fails with SQLSTATE `42P10`, `there is no unique or exclusion constraint matching the ON CONFLICT specification`.
- **Plain `INSERT` twice:** the second fails with `duplicate key value violates unique constraint "exercise_feed_pkey"`, detail `Key (source_key)=(source_a) already exists`.

## Exercise 5: Debugging

**Prompt:** Preview and update a bounded product set while reconciling selected and returned key counts.

**Reasoning:** Store candidate keys in a temporary table and update only through that reviewed set.

**Clause-by-clause reading:**

- `CREATE TEMP TABLE exercise_product_candidates ON COMMIT DROP AS SELECT p.product_id ... WHERE p.category = 'Books' ORDER BY p.product_id LIMIT 5`: freezes the reviewed keys 6, 12, 18, 24 and 30.
- `WITH updated AS (UPDATE products AS p SET price = ROUND(p.price * 0.99, 2) WHERE p.product_id IN (SELECT ... FROM exercise_product_candidates) RETURNING p.product_id)`: the write can reach only keys in that table.
- Outer `SELECT (SELECT COUNT(*) FROM exercise_product_candidates) AS candidate_count, COUNT(*) AS updated_count FROM updated`: one row comparing the two counts.

```sql
SAVEPOINT exercise_5;

CREATE TEMP TABLE exercise_product_candidates ON COMMIT DROP AS
SELECT
  p.product_id
FROM
  products AS p
WHERE
  p.category = 'Books'
ORDER BY
  p.product_id
LIMIT 5;

WITH updated AS (
  UPDATE
    products AS p
  SET
    price = ROUND(p.price * 0.99, 2)
  WHERE
    p.product_id IN (
      SELECT
        candidate.product_id
      FROM
        exercise_product_candidates AS candidate)
    RETURNING
      p.product_id
)
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      exercise_product_candidates) AS candidate_count,
  COUNT(*) AS updated_count
FROM
  updated;

ROLLBACK TO SAVEPOINT exercise_5;
```

**Expected shape:** One summary row with equal candidate and updated counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 5, store the first five `Books` product keys in the temporary table `exercise_product_candidates`, then lower those products' `price` by 1% through a data-modifying CTE that updates only keys in that table.
- **Expected result/shape:** For sql-10 Exercise 5, expected output: one summary row with columns `candidate_count` and `updated_count`, both `5`.
- **Independent verification:** For sql-10 Exercise 5, list the candidate `product_id` values before the update and compare them with the keys returned by the `UPDATE`'s `RETURNING` clause; after `ROLLBACK TO SAVEPOINT`, confirm that each candidate's `price` equals its original value.
- **What prints:** `SELECT 5` for the candidate table, then `candidate_count 5 | updated_count 5`. Prices 12.22, 14.44, 16.66, 18.88 and 21.10 become 12.10, 14.30, 16.49, 18.69 and 20.89.
- **Why freeze the keys:** `WHERE p.category = 'Books'` alone would lower all 50 book prices. The candidate table limits the write to the five keys you looked at.
- **What a mismatch means:** if a candidate product had been deleted between review and update, `updated_count` would drop to 4 while `candidate_count` stayed 5. Treat any difference as a reason to roll back.
- **`ORDER BY` before `LIMIT`:** without it, "the first five books" are whichever rows the scan meets first; `ORDER BY p.product_id` makes the set repeatable.

## Exercise 6: Extension

**Prompt:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.

**Reasoning:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.

**Clause-by-clause reading:**

- `CREATE TEMP TABLE exercise_price_stage (product_id integer PRIMARY KEY, new_price numeric)`: incoming prices, one per product; `new_price` may be NULL.
- `INSERT ... SELECT p.product_id, ROUND(p.price * 1.01, 2) ... ORDER BY p.product_id LIMIT 3`: stages a 1% rise for products 1, 2 and 3.
- `UPDATE products AS p SET price = stage.new_price FROM exercise_price_stage AS stage WHERE stage.product_id = p.product_id`: pairs each product with its staged row.
- `AND stage.new_price >= 0 AND p.price IS DISTINCT FROM stage.new_price`: skips invalid prices and rows that would not change.
- `RETURNING p.product_id, p.price`: the new prices.

```sql
SAVEPOINT exercise_6;

CREATE TEMP TABLE exercise_price_stage (
  product_id integer PRIMARY KEY,
  new_price numeric
) ON COMMIT DROP;

INSERT INTO exercise_price_stage (product_id, new_price)
SELECT
  p.product_id,
  ROUND(p.price * 1.01, 2)
FROM
  products AS p
ORDER BY
  p.product_id
LIMIT 3;

UPDATE
  products AS p
SET
  price = stage.new_price
FROM
  exercise_price_stage AS stage
WHERE
  stage.product_id = p.product_id
  AND stage.new_price >= 0
  AND p.price IS DISTINCT FROM stage.new_price
RETURNING
  p.product_id,
  p.price;

ROLLBACK TO SAVEPOINT exercise_6;
```

**Expected shape:** Returned rows only for valid changed products.

### Reasoning and verification

- **Inputs/evidence:** For sql-10 Exercise 6, stage new prices for the first three products in the temporary table `exercise_price_stage`, then run `UPDATE products ... FROM exercise_price_stage` only where `stage.new_price >= 0` and `p.price IS DISTINCT FROM stage.new_price`.
- **Expected result/shape:** For sql-10 Exercise 6, expected output: the command tag `UPDATE 3` and three returned rows ordered by `p.product_id` with columns `product_id` and `price`: `(1, 10.47)`, `(2, 10.85)`, and `(3, 11.22)` on the course seed.
- **Independent verification:** For sql-10 Exercise 6, add a staged row with a negative price and one whose price equals the current price, rerun the update after a savepoint, and confirm that neither key is returned; then confirm the original prices after `ROLLBACK TO SAVEPOINT`.
- **What prints:** `INSERT 0 3`, then (1, 10.47), (2, 10.85), (3, 11.22) and `UPDATE 3`. The old prices were 10.37, 10.74 and 11.11.
- **Testing the guards:** stage (1, 10.47), (2, -5) and (3, 11.11) instead, where 11.11 is product 3's current price; only product 1 comes back.
- **Without `>= 0`:** the -5 row reaches `products` and the statement fails on `products_price_check`, the table's `CHECK (price >= 0)`. The guard skips the bad row instead of aborting the whole update.
- **`IS DISTINCT FROM` versus `<>`:** they agree whenever both sides have values. A staged NULL never gets that far, because `NULL >= 0` is unknown and the row is skipped before it can reach the `NOT NULL` price column.
- **Why `UPDATE ... FROM`:** one statement applies every staged row. A correlated `SET price = (SELECT new_price ...)` with no `WHERE EXISTS` would try to set every unstaged product's price to NULL and fail.

## Final self-check

- Your preview count says 34 but the tag says `UPDATE 17`. What is the likely cause, and how would you confirm it?
- How many order lines disappear with the 362 unpaid orders, and which constraint removes them?
- Which tags does Exercise 4 print, and how can you tell which run inserted the row?
- Why does Exercise 5 store the candidate keys first instead of filtering on `category` in the `UPDATE`?
- What happens to a staged price of -5 with and without the `stage.new_price >= 0` guard?
