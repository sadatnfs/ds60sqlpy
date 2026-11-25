# Day 09 solutions: Correlated Subqueries and EXISTS

<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers are filters: none of them adds a column from the inner query, so each result is a subset of `customers`, `products` or `orders`. Try them yourself, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day09_solutions.sql
```

The script sets `search_path` inside `BEGIN`/`ROLLBACK` and prints six results: 431 customers, 25 products, 2,249 orders, 62 customers, 438 orders and 7 customers. The snippets below leave out that setup line. Exercise prompts follow [the learner file](../day09_correlated_subqueries.sql) one for one, and the study guide's [notes on reading a solution](../../STUDY-GUIDE.md#read-a-solution) suggest how to compare your attempt.

## Reading contract

- **Focus:** Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
- **Assumptions:** `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
- **Primary pitfall:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
- **Safety:** six `SELECT` statements and nothing else; the `BEGIN`/`ROLLBACK` pair is there only for consistency with the rest of the course.

## Exercise 1: Query writing

**Prompt:** Return customers who have at least one delivered order.

**Reasoning:** `EXISTS` expresses the yes/no question without multiplying customer rows.

**Clause-by-clause reading:**

- `FROM customers AS c`: the candidates, all 500 customers.
- `WHERE EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered')`: true when this customer has at least one delivered order; `o.customer_id = c.customer_id` is the correlation.
- `SELECT c.customer_id, c.full_name ... ORDER BY c.customer_id`: one row per kept customer, in ID order.

```sql
SELECT
  c.customer_id,
  c.full_name
FROM
  customers AS c
WHERE
  EXISTS (
    SELECT
      1
    FROM
      orders AS o
    WHERE
      o.customer_id = c.customer_id
      AND o.status = 'delivered')
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per qualifying customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 1, keep each of the 500 `customers` rows for which a correlated `EXISTS` finds at least one `orders` row with `status = 'delivered'`; 872 orders are delivered.
- **Expected result/shape:** For sql-09 Exercise 1, return 431 rows, one per customer with a delivered order, from customer 1 to customer 500; the 62 customers without orders and 7 buyers with no delivered order (39, 169, 234, 299, 364, 429, 494) are missing. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 1, confirm 431 equals `SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'delivered'`; a plain `JOIN` on the same condition returns 872 rows because it repeats customers. Inside a rolled-back transaction, set customer 38's 4 delivered orders to `shipped`; the result must drop to 430 rows.
- **What prints:** 431 customers, starting 1, 2, 3, 4, 5, 6.
- **Who is missing:** 69 customers. 62 are the Brazilian customers with no orders; the other 7 (39, 169, 234, 299, 364, 429 and 494) each placed four orders and none of them was delivered.
- **Join comparison:** `customers JOIN orders` with the same status filter returns 872 rows, one per delivered order, covering the same 431 customers. `EXISTS` reaches 431 directly, with no `DISTINCT` needed.
- **Count to compare:** `SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'delivered'` also returns 431.

## Exercise 2: Query writing

**Prompt:** Return products that have never been sold.

**Reasoning:** `NOT EXISTS` correlates on product ID and is not confused by NULL membership.

**Clause-by-clause reading:**

- `FROM products AS p`: all 300 products.
- `WHERE NOT EXISTS (SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id)`: keeps a product only when no line item mentions it.
- `ORDER BY p.product_id`: unsold products in ID order.

```sql
SELECT
  p.product_id,
  p.name,
  p.category
FROM
  products AS p
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      order_items AS oi
    WHERE
      oi.product_id = p.product_id)
ORDER BY
  p.product_id;
```

**Expected shape:** One row per unsold product.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 2, keep each of the 300 `products` rows for which `NOT EXISTS` finds no `order_items` row with the same `product_id`.
- **Expected result/shape:** For sql-09 Exercise 2, return 25 rows, one per never-sold product, products 276 through 300, from Product 276 (Books) to Product 300 (Books). The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
- **Independent verification:** For sql-09 Exercise 2, confirm `NOT IN (SELECT product_id FROM order_items)` and a `LEFT JOIN ... WHERE oi.product_id IS NULL` both return the same 25 products, which is safe here because `order_items.product_id` is `NOT NULL`. Inside a rolled-back transaction, insert one `order_items` row for product 276; the result must drop to 24 rows.
- **What prints:** 25 products, IDs 276 to 300: five in Books and four in each other category. The first three are 276 (Books), 277 (Apparel) and 278 (Electronics).
- **Same answer, other route:** Day 04 found these 25 with `LEFT JOIN ... WHERE oi.order_item_id IS NULL`. Both are anti-joins; `NOT EXISTS` says it without first building the `NULL`-extended rows.
- **`NOT IN` here:** `p.product_id NOT IN (SELECT product_id FROM order_items)` also returns 25, because `order_items.product_id` is `NOT NULL`. The constraint, not the query, is what keeps that version safe.
- **Opposite count:** switching to `EXISTS` returns 275 products, and 275 + 25 = 300.

## Exercise 3: Query writing

**Prompt:** Return each customer's orders that are above that customer's average order total.

**Reasoning:** Correlate the average to the current order's customer, not to the current order ID.

**Clause-by-clause reading:**

- `FROM orders AS o`: every order is a candidate.
- `(SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id)`: a scalar subquery giving this customer's average order, recomputed for each outer order.
- `o.total_amount > (...)`: strict, so an order exactly equal to the average is left out.
- `ORDER BY o.customer_id, o.total_amount DESC, o.order_id`: customers in turn, largest order first.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount
FROM
  orders AS o
WHERE
  o.total_amount > (
    SELECT
      AVG(peer.total_amount)
    FROM
      orders AS peer
    WHERE
      peer.customer_id = o.customer_id)
ORDER BY
  o.customer_id,
  o.total_amount DESC,
  o.order_id;
```

**Expected shape:** Order rows above their own customer average.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 3, compare each of the 4,362 `orders` rows with a correlated subquery that averages `total_amount` over the same customer's orders.
- **Expected result/shape:** For sql-09 Exercise 3, return 2,249 rows, one per order above its own customer's average, covering all 438 buyers; customer 1 contributes orders 4 (1155.92) and 3 (601.73). The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
- **Independent verification:** For sql-09 Exercise 3, confirm 2,249 distinct `order_id` values and that filtering on `total_amount > AVG(total_amount) OVER (PARTITION BY customer_id)` returns the same 2,249 orders. Comparing with the global average instead, as in sql-08, returns 2,269 rows, so a correlation mistake changes the count.
- **What prints:** 2,249 of the 4,362 orders. Customer 1 averages 504.33, so only orders 4 (1,155.92) and 3 (601.73) qualify; customer 2 averages 602.72 and starts with order 8 at 917.69.
- **Every customer appears:** each of the 438 customers with orders keeps between 1 and 9 orders. Unless all of a customer's amounts are equal, at least one must sit above their mean.
- **Global average instead:** comparing with the overall mean, 540.04, returns 2,269 orders, a similar count but a different set. Order 37 (customer 6, 583.61) passes the global test but not its own customer's 620.26, while order 18 (customer 3, 490.39) passes only its customer's 479.32.
- **Wrong correlation:** `peer.order_id = o.order_id` returns 0 rows, since each order would be measured against an average of itself.

## Exercise 4: Prediction

**Prompt:** Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.

**Reasoning:** Correlate on the customer key; a matching row alone determines exclusion.

**Clause-by-clause reading:**

- `FROM customers AS c`: all 500 customers.
- `WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id)`: keep the customer only if no order points at them.
- `ORDER BY c.customer_id`: customers without orders in ID order.

```sql
SELECT
  c.customer_id,
  c.full_name
FROM
  customers AS c
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      orders AS o
    WHERE
      o.customer_id = c.customer_id)
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with no order.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 4, keep each of the 500 `customers` rows for which `NOT EXISTS` finds no matching `orders` row.
- **Expected result/shape:** For sql-09 Exercise 4, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 4, confirm the same 62 customers as the sql-06 `EXCEPT` result. Rewrite the filter as `customer_id NOT IN (SELECT customer_id FROM orders UNION ALL SELECT NULL)` and it must return 0 rows, which is why `NOT EXISTS` is used instead of `NOT IN` against a column that can contain `NULL`.
- **What prints:** 62 customers, 8, 16, 24 and so on up to 496, every one of them in Brazil.
- **The `NOT IN` trap, shown:** `WHERE c.customer_id NOT IN (SELECT customer_id FROM orders UNION ALL SELECT NULL)` returns 0 rows. For customer 8 the test reads "8 is not 1, and not 2, ..., and not `NULL`", and that last part is unknown, so the whole condition is unknown and the row is dropped.
- **Why the plain version works today:** `orders.customer_id` is `NOT NULL`, so `NOT IN` without the added `NULL` also gives 62. Relying on that ties the answer to a constraint someone could later drop.
- **Cross-check:** 438 customers have orders, and 438 + 62 = 500.

## Exercise 5: Debugging

**Prompt:** Return only each customer's most recent order without an arbitrary `LIMIT 1`.

**Reasoning:** Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.

**Clause-by-clause reading:**

- `FROM orders AS o`: every order is a candidate.
- Inner `SELECT candidate.order_id ... WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1`: the single latest order ID for this customer, with the ID breaking any timestamp tie.
- `o.order_id = (...)`: keep the outer order only if it is that one.
- `ORDER BY o.customer_id`: one row per customer in ID order.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date
FROM
  orders AS o
WHERE
  o.order_id = (
    SELECT
      candidate.order_id
    FROM
      orders AS candidate
    WHERE
      candidate.customer_id = o.customer_id
    ORDER BY
      candidate.order_date DESC,
      candidate.order_id DESC
    LIMIT 1)
ORDER BY
  o.customer_id;
```

**Expected shape:** At most one deterministic order per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 5, keep each `orders` row whose `order_id` equals a correlated subquery that picks the same customer's order by `order_date DESC, order_id DESC` with `LIMIT 1`.
- **Expected result/shape:** For sql-09 Exercise 5, return 438 rows, one latest order per buyer, starting with order 5 for customer 1 and ending with order 4362 for customer 500. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
- **Independent verification:** For sql-09 Exercise 5, confirm 438 distinct `customer_id` values and that `DISTINCT ON (customer_id)` with the same ordering returns the same 438 orders. Inside a rolled-back transaction, insert a new order for customer 1 with the default `order_date` of `now()`; customer 1's row must switch from order 5 to the new order.
- **What prints:** 438 rows, one per customer with orders. In our check customer 1's latest is order 5 on 2026-11-17, customer 2's is order 11 and customer 3's is order 18.
- **Is the tie-breaker used?** Not on this data: no customer has two orders with the same timestamp. It still belongs there, because with a tie `LIMIT 1` could return either row.
- **A shortcut that only looks right:** `MAX(order_id)` per customer picks the same 438 orders here, because the generator assigned IDs in date order. Nothing in the schema promises that, so the date has to drive the choice.
- **Cost:** the inner query runs once per outer order, 4,362 times in principle. Day 17's `ROW_NUMBER()` or `DISTINCT ON (customer_id)` does the same job in a single pass.

## Exercise 6: Extension

**Prompt:** Return customers for whom every order has at least one payment, excluding customers with no orders.

**Reasoning:** Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.

**Clause-by-clause reading:**

- `EXISTS (SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id)`: the customer must have at least one order.
- Outer `NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS (...))`: there must be no order of theirs that ...
- Inner `NOT EXISTS (SELECT 1 FROM payments AS p WHERE p.order_id = o.order_id)`: ... has no payment.
- `ORDER BY c.customer_id`: qualifying customers in ID order.

```sql
SELECT
  c.customer_id,
  c.full_name
FROM
  customers AS c
WHERE
  EXISTS (
    SELECT
      1
    FROM
      orders AS any_order
    WHERE
      any_order.customer_id = c.customer_id)
  AND NOT EXISTS (
    SELECT
      1
    FROM
      orders AS o
    WHERE
      o.customer_id = c.customer_id
      AND NOT EXISTS (
        SELECT
          1
        FROM
          payments AS p
        WHERE
          p.order_id = o.order_id))
  ORDER BY
    c.customer_id;
```

**Expected shape:** One row per customer satisfying the universal condition.

### Reasoning and verification

- **Inputs/evidence:** For sql-09 Exercise 6, keep each `customers` row that has at least one order and no order lacking a `payments` row, using `EXISTS` plus a doubly nested `NOT EXISTS`; 873 of the 4,362 orders have no payment.
- **Expected result/shape:** For sql-09 Exercise 6, return 7 rows, one per customer whose every order is paid: customers 26, 91, 156, 221, 286, 351, and 481, each with 4 orders. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-09 Exercise 6, confirm each of the 7 customers has 0 orders without a payment. Dropping the `EXISTS` guard must return 69 rows, because the 62 customers with no orders satisfy the universal condition vacuously. Inside a rolled-back transaction, delete the payments for order 223; customer 26 must leave the result, leaving 6 rows.
- **What prints:** 7 customers: 26, 91, 156, 221, 286, 351 and 481. Each has exactly four orders with the statuses paid, shipped, delivered and returned, and every one of those orders has a payment.
- **Why so few:** all 873 placed orders lack a payment, and 431 of the 438 customers with orders have at least one of them. A single placed order disqualifies a customer.
- **Without the first `EXISTS`:** 69 rows. The extra 62 are the Brazilian customers, who have no orders, so there is no unpaid order to find.
- **Reading the double negative:** "no order exists without a payment" is how SQL says "every order has a payment". Read the inner pair first: an order with no payment is a counterexample, and the outer `NOT EXISTS` demands zero counterexamples.

## Final self-check

- Why does customer 12 appear once in Example 1 despite eight Electronics line items?
- Which six customers with orders are missing from Example 1, and why?
- What does `NOT IN` return in Exercise 4 if its list contains one `NULL`?
- Which two of customer 1's orders beat their own average in Exercise 3?
- Why does Exercise 6 need its first `EXISTS`?
