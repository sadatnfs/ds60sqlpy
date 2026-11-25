# Day 06 solutions: Set Operations: UNION, INTERSECT, EXCEPT

<!-- beginner-solution-enrichment -->
## How to study and run this solution

These six answers use all four set operators. Exercises 1 to 3 compare the same two customer sets three ways, Exercise 4 counts what `ALL` keeps, Exercise 5 lines up columns of different meaning, and Exercise 6 builds a symmetric difference out of two `EXCEPT`s. Try them first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day06_solutions.sql
```

Expect 500, 438, 62, 2, 2 and 62 rows. Every statement only reads, each block ends in `ROLLBACK`, and the excerpts below omit the `SET search_path` line. Exercises are numbered as in [the learner file](../day06_set_operations.sql); the study guide's [guidance on comparing answers](../../STUDY-GUIDE.md#read-a-solution) helps you judge a different but correct query.

## Reading contract

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Primary pitfall:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Safety:** read-only; every statement is a `SELECT`, and each block still closes with `ROLLBACK`.

## Exercise 1: Query writing

**Prompt:** Return customer IDs that have either an order or a support event.

**Reasoning:** `UNION` expresses set membership and removes duplicates across both sources.

**Clause-by-clause reading:**

- `SELECT o.customer_id FROM orders AS o`: the first branch, 4,362 rows with repeats, since customers have 4 to 16 orders each.
- `UNION SELECT e.customer_id FROM events AS e WHERE e.event_type = 'support'`: the second branch, 4,000 rows. Its `WHERE` filters only this branch; the orders branch has none.
- `UNION` without `ALL`: removes repeats across and within both branches, so each ID appears once.
- `ORDER BY customer_id`: sorts the combined result by the first branch's column name.

```sql
SELECT
  o.customer_id
FROM
  orders AS o
UNION
SELECT
  e.customer_id
FROM
  events AS e
WHERE
  e.event_type = 'support'
ORDER BY
  customer_id;
```

**Expected shape:** One distinct customer ID per qualifying customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 1, combine `customer_id` from all 4,362 `orders` rows with `customer_id` from the 4,000 `events` rows whose `event_type` is `support`; every one of the 500 customers has support events, while only 438 have orders.
- **Expected result/shape:** For sql-06 Exercise 1, return 500 rows, one per distinct customer, customer 1 through customer 500, because `UNION` removes the duplicates from the 8,362 combined input rows. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 1, confirm 500 distinct values and that `UNION ALL` over the same two branches returns 8,362 rows. Inside a rolled-back transaction, delete customer 8's support events; customer 8 has no orders, so the result must drop to 499 rows.
- **What prints:** 500 rows, customer 1 to customer 500 with no gaps.
- **Why every customer appears:** each of the 500 customers has eight support events, so the support branch alone already covers everyone. The 62 Brazilian customers come in through that branch only.
- **With `ALL`:** `UNION ALL` returns 8,362 rows, 4,362 order rows plus 4,000 support events. `UNION` does the de-duplication that a `SELECT DISTINCT` would otherwise need.
- **Filter placement:** `WHERE e.event_type = 'support'` belongs to the events branch alone and never touches the orders branch or the combined set. To filter the combined IDs, wrap the `UNION` in a subquery and filter outside it.

## Exercise 2: Query writing

**Prompt:** Return customer IDs that have both an order and a support event.

**Reasoning:** `INTERSECT` keeps keys present in both compatible sets.

**Clause-by-clause reading:**

- First branch: every `customer_id` in `orders`, repeats included.
- `INTERSECT`: keeps an ID only when it also appears in the second branch, and returns each surviving ID once.
- Second branch: `customer_id` from support events.
- `ORDER BY customer_id`: one sort for the final result.

```sql
SELECT
  o.customer_id
FROM
  orders AS o
INTERSECT
SELECT
  e.customer_id
FROM
  events AS e
WHERE
  e.event_type = 'support'
ORDER BY
  customer_id;
```

**Expected shape:** One distinct customer ID in both sets.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 2, intersect the distinct `customer_id` values from `orders` (438 buyers) with those from `events` filtered to `event_type = 'support'` (all 500 customers).
- **Expected result/shape:** For sql-06 Exercise 2, return 438 rows, one per customer found in both sets; customer 8 and the other 61 customers without orders are missing. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 2, confirm the 438 rows match `SELECT DISTINCT customer_id FROM orders` exactly, since every buyer also has support events. Inside a rolled-back transaction, delete customer 1's support events; the result must drop to 437 rows without customer 1.
- **What prints:** 438 rows, customer 1 first and 500 last.
- **Same as the order customers:** because every customer has support events, the intersection equals the 438 distinct customers in `orders`. With this fixture, a query that forgot the support branch would print the same rows, so test the logic on the counts, not just the output.
- **`INTERSECT ALL`:** keeps each ID as many times as the smaller branch has it, the lesser of the customer's order count and 8. That gives 3,164 rows, for example 5 rows for customer 1, who has five orders.
- **No `DISTINCT` needed:** the branches repeat IDs, but plain `INTERSECT` returns distinct rows on its own.

## Exercise 3: Query writing

**Prompt:** Return customers who have no orders.

**Reasoning:** `EXCEPT` subtracts the order-customer set from all customers.

**Clause-by-clause reading:**

- `SELECT c.customer_id FROM customers AS c`: all 500 customer IDs, each once.
- `EXCEPT SELECT o.customer_id FROM orders AS o`: removes every ID that appears in `orders`, however many times it appears there.
- `ORDER BY customer_id`: lowest ID first.

```sql
SELECT
  c.customer_id
FROM
  customers AS c
EXCEPT
SELECT
  o.customer_id
FROM
  orders AS o
ORDER BY
  customer_id;
```

**Expected shape:** One row per customer absent from orders.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 3, subtract the `customer_id` values in `orders` from the 500 `customers` keys with `EXCEPT`.
- **Expected result/shape:** For sql-06 Exercise 3, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`. The final order is `customer_id`.
- **Independent verification:** For sql-06 Exercise 3, confirm a `NOT EXISTS` anti-join and a `NOT IN (SELECT customer_id FROM orders)` filter both return the same 62 customers. Inside a rolled-back transaction, insert one order for customer 8; the result must drop to 61 rows.
- **What prints:** 62 rows: 8, 16, 24 and every eighth ID up to 496.
- **Who they are:** all 62 are the Brazilian customers. Every other country has orders for every customer.
- **Same answer, other forms:** `NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)` and `LEFT JOIN orders ... WHERE o.order_id IS NULL` both return the same 62 rows.
- **The `NOT IN` trap:** `WHERE c.customer_id NOT IN (SELECT customer_id FROM orders)` also gives 62, but only because `orders.customer_id` has no `NULL`s. Add a single `NULL` to the subquery and it returns 0 rows, while `EXCEPT` still returns 62.
- **Count check:** 500 customers less the 438 distinct IDs in `orders` leaves 62. Joining the result back to `customers` and grouping by `country` prints a single row, BR with 62.
- **Branch order:** `orders EXCEPT customers` would return no rows, since every ordering customer exists in `customers`.

## Exercise 4: Prediction

**Prompt:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.

**Reasoning:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.

**Clause-by-clause reading:**

- `combined_all`: paid or shipped statuses `UNION ALL` shipped or delivered statuses, keeping every row from both branches.
- `combined_distinct`: the same two branches joined with `UNION`, so only distinct status values remain.
- Final query: two one-row `COUNT(*)` queries stacked with `UNION ALL`, each carrying a text label in `operation`.
- `ORDER BY operation`: `'UNION'` sorts before `'UNION ALL'`, so the distinct count prints first.

```sql
WITH combined_all AS (
  SELECT
    o.status
  FROM
    orders AS o
  WHERE
    o.status IN ('paid', 'shipped')
  UNION ALL
  SELECT
    o.status
  FROM
    orders AS o
  WHERE
    o.status IN ('shipped', 'delivered')
),
combined_distinct AS (
  SELECT
    o.status
  FROM
    orders AS o
  WHERE
    o.status IN ('paid', 'shipped')
  UNION
  SELECT
    o.status
  FROM
    orders AS o
  WHERE
    o.status IN ('shipped', 'delivered'))
SELECT
  'UNION ALL' AS operation,
  COUNT(*) AS row_count
FROM
  combined_all
UNION ALL
SELECT
  'UNION' AS operation,
  COUNT(*) AS row_count
FROM
  combined_distinct
ORDER BY
  operation;
```

**Expected shape:** Two labeled summary rows showing all-count >= distinct-count.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 4, read `status` from `orders` twice, once for `paid` or `shipped` and once for `shipped` or `delivered`, then count the combined rows under `UNION ALL` and under `UNION`.
- **Expected result/shape:** For sql-06 Exercise 4, return two rows: `UNION` with `row_count` 3 and `UNION ALL` with `row_count` 3490. The final columns are `operation`, and `row_count`. The final order is `operation`.
- **Independent verification:** For sql-06 Exercise 4, confirm that `UNION ALL` returns 3490 rows, the sum of the two branch counts (1745 + 1745), while `UNION` returns 3 because it keeps only the distinct statuses `delivered`, `paid`, and `shipped`; the `shipped` rows appear in both branches.
- **What prints:** `UNION` with 3, then `UNION ALL` with 3,490.
- **Where 3,490 comes from:** the first branch has 872 paid plus 873 shipped rows and the second 873 shipped plus 872 delivered, 1,745 each. The 873 shipped orders are counted twice.
- **Why only 3:** `UNION` compares the single `status` column, so 3,490 rows collapse to the values `delivered`, `paid` and `shipped`. Projecting `order_id` as well would give 2,617 distinct rows, one per order with one of those statuses.
- **The outer `UNION ALL`:** the two count rows carry different labels, so `UNION` would print the same two rows; `ALL` just skips a pointless de-duplication step.

## Exercise 5: Debugging

**Prompt:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.

**Reasoning:** Each branch below returns one text label and one numeric amount at the same report grain.

**Clause-by-clause reading:**

- `'order_revenue'::text AS measure, SUM(o.total_amount)::numeric AS amount`: the first branch sets both column names and their types.
- `'expense'::text AS measure, SUM(e.amount)::numeric AS amount`: the second branch lists the same two columns in the same order. Its aliases are optional, since the first branch's names win, but they make the pairing easy to check.
- `UNION ALL`: stacks the two one-row results.
- `ORDER BY measure`: alphabetical, so `expense` prints first.

```sql
SELECT
  'order_revenue'::text AS measure,
  SUM(o.total_amount)::numeric AS amount
FROM
  orders AS o
UNION ALL
SELECT
  'expense'::text AS measure,
  SUM(e.amount)::numeric AS amount
FROM
  expenses AS e
ORDER BY
  measure;
```

**Expected shape:** Rows identify revenue and expense measures with compatible types.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 5, stack one row labeled `order_revenue` holding `SUM(total_amount)` from `orders` and one row labeled `expense` holding `SUM(amount)` from `expenses` with `UNION ALL`, using a text label column followed by a numeric amount column.
- **Expected result/shape:** For sql-06 Exercise 5, return two rows: `expense` with 50483850.00 and `order_revenue` with 2355646.89, both typed as `numeric` under one shared `amount` column. The final columns are `measure`, and `amount`. The final order is `measure`.
- **Independent verification:** For sql-06 Exercise 5, confirm exactly two rows, `expense` = 50483850.00 and `order_revenue` = 2355646.89, each equal to its own standalone `SUM`; both branches must list the label first and the amount second, because swapping them in one branch raises `UNION types text and numeric cannot be matched`.
- **What prints:** two rows, `expense` 50,483,850.00 and `order_revenue` 2,355,646.89.
- **Where the numbers come from:** the expense row adds 10,000 rows of `expenses` ranging from 100.51 to 9,998.28; the revenue row adds the 4,362 order totals.
- **The bug being fixed:** with the label first in one branch and the amount first in the other, PostgreSQL raises `UNION types text and numeric cannot be matched`. Both branches must say label, then amount.
- **The explicit casts:** without `::text`, a string literal starts as type `unknown`; PostgreSQL resolves it to `text` here, but the cast states the intended type for the next reader.
- **Not a profit figure:** the two values share a column but cover different spans; in our check the expenses run about two years and the orders nearly four. Check the dates before subtracting one from the other.

## Exercise 6: Extension

**Prompt:** Return the symmetric difference between customers with orders and customers with support events.

**Reasoning:** Subtract each set from the other, then union the two differences.

**Clause-by-clause reading:**

- `ordering_customers` and `support_customers`: the two distinct ID sets, 438 and 500 rows.
- `only_orders`: `ordering_customers EXCEPT support_customers`, customers who ordered but never contacted support.
- `only_support`: the reverse `EXCEPT`, customers who contacted support but never ordered.
- Final `UNION ALL`: stacks the two lists with a `source` label. An ID cannot be in both lists, so `ALL` loses nothing.
- `ORDER BY customer_id, source`: by ID, with the label as a second key.

```sql
WITH ordering_customers AS (
  SELECT DISTINCT
    o.customer_id
  FROM
    orders AS o
),
support_customers AS (
  SELECT DISTINCT
    e.customer_id
  FROM
    events AS e
  WHERE
    e.event_type = 'support'
),
only_orders AS (
  SELECT
    customer_id
  FROM
    ordering_customers
  EXCEPT
  SELECT
    customer_id
  FROM
    support_customers
),
only_support AS (
  SELECT
    customer_id
  FROM
    support_customers
  EXCEPT
  SELECT
    customer_id
  FROM
    ordering_customers
)
SELECT
  customer_id,
  'orders_only' AS source
FROM
  only_orders
UNION ALL
SELECT
  customer_id,
  'support_only' AS source
FROM
  only_support
ORDER BY
  customer_id,
  source;
```

**Expected shape:** Customers present in exactly one of the two source sets.

### Reasoning and verification

- **Inputs/evidence:** For sql-06 Exercise 6, compute the distinct ordering customers (438) and the distinct support-event customers (500), apply `EXCEPT` in both directions, and label each side with `source` before stacking them with `UNION ALL`.
- **Expected result/shape:** For sql-06 Exercise 6, return 62 rows, all labeled `support_only`, from customer 8 to customer 496; no row is `orders_only` because every buyer also has support events. The final columns are `customer_id`, and `source`. The final order is `customer_id, source`.
- **Independent verification:** For sql-06 Exercise 6, confirm 62 distinct `customer_id` values that equal the Exercise 3 result, and 0 `orders_only` rows. Inside a rolled-back transaction, delete customer 1's support events; the result must grow to 63 rows with one new `(1, 'orders_only')` row.
- **What prints:** 62 rows, IDs 8 to 496 in steps of 8, every one labelled `support_only`.
- **Why no `orders_only` rows:** every customer has support events, so `only_orders` is empty. The query is still right; on other data it would return both kinds.
- **Check by arithmetic:** the union of the two sets has 500 IDs and the intersection 438 (Exercises 1 and 2), and 500 minus 438 is 62.
- **Another way:** `(A UNION B) EXCEPT (A INTERSECT B)` returns the same 62 IDs but cannot say which side each came from. A `FULL JOIN` of the two CTEs on `customer_id`, keeping rows where one side is `NULL`, can.

## Final self-check

- Why do Exercises 1 and 2 return 500 and 438 rows, and what does that say about support events in this fixture?
- Which customers do Example 2, Exercise 3 and Exercise 6 all return, and why the same ones?
- How does the walkthrough's `EXCEPT` grow from 873 to 1,402 rows?
- What would `UNION` instead of `UNION ALL` print for the third learner query?
- Why does `NOT IN` stop working when its subquery contains a `NULL`, while `EXCEPT` does not?
