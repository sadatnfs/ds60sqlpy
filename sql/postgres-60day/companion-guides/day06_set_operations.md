# Day 06: Set Operations: UNION, INTERSECT, EXCEPT (Companion Guide)

## How to run this lesson

Run `./classroom` from the repository root, pick PostgreSQL, open **sql-06** and choose **Whole SQL lesson (psql)**. The script runs in `advanced_sql_training` with `search_path` set to `training`, wraps everything in a transaction that ends in `ROLLBACK`, and prints three results: customers who both ordered and contacted support (`INTERSECT`), customers who viewed pages but never ordered (`EXCEPT`), and a stacked list of US, CA and GB country codes (`UNION ALL`).

Edit your copy at
`.learning/sql/sql-06/lesson/workspace/sql/postgres-60day/day06_set_operations.sql`.
A quick experiment: change the third query's `UNION ALL` to `UNION` and watch 252 rows shrink to 3.

If the launcher or the `psql` connection misbehaves, the study guide's [how-to for running lessons](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) lists the fixes. Contributors who work in JupyterLab can follow the [contributor notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route) instead.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 05; cross and self joins](day05_cross_self_joins.md)
- **Artifacts:** [learner SQL](../day06_set_operations.sql) ·
  [solution reasoning](../solutions/day06_solutions.md) ·
  [executable solution](../solutions/day06_solutions.sql)

## A beginner's mental model for this lesson

Joins put columns side by side; set operations stack or compare whole rows. Each branch is a complete `SELECT`, and a **set operation** combines their outputs: `UNION` keeps any row found in either branch, `INTERSECT` keeps rows found in both, and `EXCEPT` keeps rows of the left branch that the right branch lacks. A row counts as "the same" only when every projected column matches, so the columns you choose decide what is being compared.

The branches must be **union compatible**: the same number of columns, with types that line up position by position. Names do not have to match. PostgreSQL pairs columns by position and labels the result with the first branch's names, so a misplaced column fails only when the types clash.

**Duplicate semantics** are the last decision. `UNION`, `INTERSECT` and `EXCEPT` return distinct rows; adding `ALL` keeps multiplicity. In this fixture each of the 500 customers has 8 support events and 438 customers have between 4 and 16 orders, so `UNION ALL` of order customers and support customers gives 8,362 rows while `UNION` gives 500. Unlike `=`, set operations treat two `NULL`s as equal, which is why `EXCEPT` is safer than `NOT IN` when a column can be empty.

## Two worked SQL examples

### Example 1

```sql
WITH purchasers AS (
  SELECT DISTINCT
    o.customer_id
  FROM
    orders o
),
supporters AS (
  SELECT DISTINCT
    e.customer_id
  FROM
    events e
  WHERE
    e.event_type = 'support'
)
SELECT
  *
FROM
  purchasers
INTERSECT
SELECT
  *
FROM
  supporters
ORDER BY
  customer_id;
```

**How to read it:** Two CTEs turn the fixture into sets of customer IDs. `purchasers` takes the distinct `customer_id` values from `orders`; `supporters` takes the distinct ones from support events. `INTERSECT` keeps IDs present in both, and the single `ORDER BY` at the end sorts the combined result, not either branch.

**Expected result/shape:** 438 rows, customer 1 first and customer 500 last. That is exactly the set of customers with orders, because every one of the 500 customers has eight support events, so the support side filters nothing out. The 62 Brazilian customers (IDs 8, 16, 24 and so on up to 496) are missing because they have no orders.

### Example 2

```sql
WITH browsers AS (
  SELECT DISTINCT
    e.customer_id
  FROM
    events e
  WHERE
    e.event_type = 'page_view'
),
purchasers AS (
  SELECT DISTINCT
    o.customer_id
  FROM
    orders o
)
SELECT
  *
FROM
  browsers
EXCEPT
SELECT
  *
FROM
  purchasers
ORDER BY
  customer_id;
```

**How to read it:** `browsers` collects every customer with a `page_view` event and `purchasers` every customer with an order. `EXCEPT` removes the second set from the first, leaving people who browsed but never bought. Order matters here: swapping the two CTEs would ask for buyers who never browsed.

**Expected result/shape:** 62 rows: 8, 16, 24 and so on up to 496. All 500 customers have page views and 438 have orders, so the leftovers are the 62 Brazilian customers, the same IDs Exercise 3 finds and the same list Exercise 6 labels `support_only`. Swapping the branches returns zero rows.

## Learning objectives

- Combine compatible result sets and choose deliberately between duplicate
  preservation and removal.
- Express set overlap and difference at the correct projected grain.

## Vocabulary and concepts

- **Set operation:** an operator that combines or compares complete result rows.
- **Union compatibility:** equal column counts with compatible data types.
- **Duplicate semantics:** `UNION ALL` preserves duplicates; `UNION`,
  `INTERSECT`, and `EXCEPT` use set-style duplicate handling.

## Worked example / walkthrough

To list unpaid orders, compare order IDs only: `SELECT order_id FROM orders EXCEPT SELECT order_id FROM payments` returns 873 orders, starting with 5, 9 and 14. Now add the money, `SELECT order_id, total_amount FROM orders EXCEPT SELECT order_id, amount FROM payments`, and the result grows to 1,402. The extra 529 are paid orders with no payment row equal to the full total: 347 were paid in two parts, and 182 have a single payment of a different amount, such as order 17 (total 344.31, one payment of 172.16). The second query answers a different question, "which orders lack a payment of exactly their total", because `EXCEPT` compares whole rows.

## Practice assumptions and review method

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Failure to watch for:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Review loop:** before running, write how many rows each branch returns on its own and what the combined count must be under `ALL` and without it; after running, rerun one branch alone to check the arithmetic.

## Exercises

Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.

For each exercise, write both branches as separate queries first and run them alone. Note each branch's row count and whether it can repeat a `customer_id`; only then join them with the set operator and predict the combined count.

1. **Query writing:** Return customer IDs that have either an order or a support event.
   **Gut check:** `orders` has 4,362 rows and support events number 4,000. Roughly how many customer IDs will `UNION` return?
   **Progressive hint:** `UNION` expresses set membership and removes duplicates across both sources.
   **Inputs/evidence:** For sql-06 Exercise 1, combine `customer_id` from all 4,362 `orders` rows with `customer_id` from the 4,000 `events` rows whose `event_type` is `support`; every one of the 500 customers has support events, while only 438 have orders.
   **Expected result/shape:** For sql-06 Exercise 1, return 500 rows, one per distinct customer, customer 1 through customer 500, because `UNION` removes the duplicates from the 8,362 combined input rows. The final columns are `customer_id`. The final order is `customer_id`.
   **Verify:** For sql-06 Exercise 1, confirm 500 distinct values and that `UNION ALL` over the same two branches returns 8,362 rows. Inside a rolled-back transaction, delete customer 8's support events; customer 8 has no orders, so the result must drop to 499 rows.
2. **Query writing:** Return customer IDs that have both an order and a support event.
   **Gut check:** can the answer be larger than the 438 customers who have ordered?
   **Progressive hint:** `INTERSECT` keeps keys present in both compatible sets.
   **Inputs/evidence:** For sql-06 Exercise 2, intersect the distinct `customer_id` values from `orders` (438 buyers) with those from `events` filtered to `event_type = 'support'` (all 500 customers).
   **Expected result/shape:** For sql-06 Exercise 2, return 438 rows, one per customer found in both sets; customer 8 and the other 61 customers without orders are missing. The final columns are `customer_id`. The final order is `customer_id`.
   **Verify:** For sql-06 Exercise 2, confirm the 438 rows match `SELECT DISTINCT customer_id FROM orders` exactly, since every buyer also has support events. Inside a rolled-back transaction, delete customer 1's support events; the result must drop to 437 rows without customer 1.
3. **Query writing:** Return customers who have no orders.
   **Gut check:** 500 customers, 438 with orders. Which country do you think the rest come from?
   **Progressive hint:** `EXCEPT` subtracts the order-customer set from all customers.
   **Inputs/evidence:** For sql-06 Exercise 3, subtract the `customer_id` values in `orders` from the 500 `customers` keys with `EXCEPT`.
   **Expected result/shape:** For sql-06 Exercise 3, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`. The final order is `customer_id`.
   **Verify:** For sql-06 Exercise 3, confirm a `NOT EXISTS` anti-join and a `NOT IN (SELECT customer_id FROM orders)` filter both return the same 62 customers. Inside a rolled-back transaction, insert one order for customer 8; the result must drop to 61 rows.
4. **Prediction:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
   **Gut check:** with 872 paid, 873 shipped and 872 delivered orders, write both counts before you run anything.
   **Progressive hint:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.
   **Inputs/evidence:** For sql-06 Exercise 4, read `status` from `orders` twice, once for `paid` or `shipped` and once for `shipped` or `delivered`, then count the combined rows under `UNION ALL` and under `UNION`.
   **Expected result/shape:** For sql-06 Exercise 4, return two rows: `UNION` with `row_count` 3 and `UNION ALL` with `row_count` 3490. The final columns are `operation`, and `row_count`. The final order is `operation`.
   **Verify:** For sql-06 Exercise 4, confirm that `UNION ALL` returns 3490 rows, the sum of the two branch counts (1745 + 1745), while `UNION` returns 3 because it keeps only the distinct statuses `delivered`, `paid`, and `shipped`; the `shipped` rows appear in both branches.
5. **Debugging:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
   **Gut check:** which branch decides the column names of the result?
   **Progressive hint:** Each branch below returns one text label and one numeric amount at the same report grain.
   **Inputs/evidence:** For sql-06 Exercise 5, stack one row labeled `order_revenue` holding `SUM(total_amount)` from `orders` and one row labeled `expense` holding `SUM(amount)` from `expenses` with `UNION ALL`, using a text label column followed by a numeric amount column.
   **Expected result/shape:** For sql-06 Exercise 5, return two rows: `expense` with 50483850.00 and `order_revenue` with 2355646.89, both typed as `numeric` under one shared `amount` column. The final columns are `measure`, and `amount`. The final order is `measure`.
   **Verify:** For sql-06 Exercise 5, confirm exactly two rows, `expense` = 50483850.00 and `order_revenue` = 2355646.89, each equal to its own standalone `SUM`; both branches must list the label first and the amount second, because swapping them in one branch raises `UNION types text and numeric cannot be matched`.
6. **Extension:** Return the symmetric difference between customers with orders and customers with support events.
   **Gut check:** after Exercises 2 and 3, how many rows will carry `orders_only`?
   **Progressive hint:** Subtract each set from the other, then union the two differences.
   **Inputs/evidence:** For sql-06 Exercise 6, compute the distinct ordering customers (438) and the distinct support-event customers (500), apply `EXCEPT` in both directions, and label each side with `source` before stacking them with `UNION ALL`.
   **Expected result/shape:** For sql-06 Exercise 6, return 62 rows, all labeled `support_only`, from customer 8 to customer 496; no row is `orders_only` because every buyer also has support events. The final columns are `customer_id`, and `source`. The final order is `customer_id, source`.
   **Verify:** For sql-06 Exercise 6, confirm 62 distinct `customer_id` values that equal the Exercise 3 result, and 0 `orders_only` rows. Inside a rolled-back transaction, delete customer 1's support events; the result must grow to 63 rows with one new `(1, 'orders_only')` row.

## Common mistakes and how to recover

- **Branches with different widths:** `SELECT customer_id FROM orders UNION SELECT customer_id, event_type FROM events` fails with `each UNION query must have the same number of columns`. Every branch must project the same list.
- **Columns in a different order:** in Exercise 5, putting the amount first in one branch raises `UNION types text and numeric cannot be matched`. Two numeric columns swapped would not raise anything; the values would simply land under the wrong heading, so read the branches side by side.
- **Qualified names in `ORDER BY`:** `... UNION ... ORDER BY o.customer_id` fails with `missing FROM-clause entry for table "o"`. The final `ORDER BY` sees only the result's columns, so write `ORDER BY customer_id`.
- **`UNION` where counts matter:** the third learner query stacks US and CA with CA and GB. `UNION ALL` gives 252 rows with CA listed 126 times; `UNION` would leave three rows and destroy any count you meant to take.
- **`NOT IN` with a `NULL`:** `customer_id NOT IN (SELECT customer_id FROM orders)` returns 62 rows today, but add one `NULL` to the subquery and it returns 0. `EXCEPT` and `NOT EXISTS` keep returning 62.
- **Extra columns in `EXCEPT`:** as the walkthrough shows, adding `total_amount` turns 873 unpaid orders into 1,402 mismatched rows.

If one of these errors stops the script partway, see the study guide's [fixes for a stalled run](../../STUDY-GUIDE.md#recover-from-common-failures) before rerunning the whole file.

## Self-check

- Do both branches return columns in the same semantic order, not merely
  compatible types?
- Can you state whether duplicates should survive for the business question?

## Next step

Continue to [Day 07; Week 1 project](day07_week1_project.md).

## Deep dive and reference

Learning objectives
- Combine result sets with UNION/UNION ALL
- Compute set intersection and differences with INTERSECT/EXCEPT
- Understand duplicate handling and column alignment rules

Why this matters
Merging and comparing result sets is common in data reconciliation, feature flags, and A/B test cohorts.

Core concepts and deep dive
- UNION ALL concatenates rows and keeps duplicates; UNION removes duplicates (implies sort/unique).
- INTERSECT returns rows present in both queries; EXCEPT returns rows in left not in right.
- Column rules: Both queries must have same number of columns and compatible types; column names come from the first query.
- Performance: DISTINCT/UNION can be expensive; prefer UNION ALL followed by targeted dedup when appropriate.

Examples in your schema
- Customers from the `gold` and `platinum` segments can be combined by
  selecting `customer_id` from each set.
- Orders with no payment can be found with `SELECT order_id FROM orders EXCEPT
  SELECT order_id FROM payments`.
- Common high-value customers across two periods can be found by intersecting
  compatible `customer_id` result sets.

Further reading
- Set operations: https://www.postgresql.org/docs/17/queries-union.html

## Ask an AI tutor about this lesson

No tutor is required. One useful way to use one: ask it to predict the row counts of `UNION`, `UNION ALL`, `INTERSECT ALL` and `EXCEPT ALL` between order customers and support customers, given that each customer has 8 support events and between 4 and 16 orders, then check its answers in `psql` (`INTERSECT ALL` gives 3,164 and `orders EXCEPT ALL support` gives 1,198). The study guide's [tutoring advice](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) explains how to keep the conversation on your reasoning.

```text
Tutor me through sql-06: Set Operations: UNION, INTERSECT, and EXCEPT.

I have completed the direct catalog prerequisite: `sql-05`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day06_set_operations.md
- Answer-free learner SQL: sql/postgres-60day/day06_set_operations.sql

Key terms to teach in context: Set operation, Union compatibility, Duplicate semantics. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Project only `order_id` from orders and payments before applying `EXCEPT`. Because set operations compare every projected column, adding an unrelated amount or timestamp would change the meaning from “missing order IDs” to “missing complete tuples.”

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-06/ working copy. Never point setup, reset, DDL, or DML
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
