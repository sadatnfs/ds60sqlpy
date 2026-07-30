# Day 03 — INNER JOINs: Relational Linking and Predicate Placement (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 02 — aggregations and grouping](day02_aggregates_groupby_having.md)
- **Artifacts:** [learner SQL](../day03_inner_joins.sql) ·
  [solution reasoning](../solutions/day03_solutions.md) ·
  [executable solution](../solutions/day03_solutions.sql)

## Learning objectives

- Join related tables with explicit keys and qualified column names.
- Predict one-to-many fanout and validate the intended output grain.

## Vocabulary and concepts

- **Join key:** columns that define how rows from two relations correspond.
- **Cardinality:** whether a relationship is one-to-one, one-to-many, or
  many-to-many.
- **Fanout:** row multiplication caused by matching one row to several rows.

## Worked example / walkthrough

Follow one `orders` row through the `order_items` join. It becomes one row per
line item, so summing `orders.total_amount` at that point repeats the order
total. The learner query instead calculates value from each line and aggregates
at the requested customer or category grain.

## Practice assumptions and review method

- **Focus:** Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
- **Assumptions:** Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
- **Failure to watch for:** A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List orders with customer names and countries.
   **Progressive hint:** Join the order foreign key to the customer primary key and qualify every selected column.
   **Expected shape:** One row per order.
2. **Query writing:** Calculate each order item's net line revenue with the product name and category.
   **Progressive hint:** Remain at one row per order item; do not aggregate until the desired grain changes.
   **Expected shape:** One row per order item.
3. **Query writing:** List payments with order status and customer name.
   **Progressive hint:** Follow payments → orders → customers using each declared foreign key.
   **Expected shape:** One row per payment.
4. **Prediction:** Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
   **Progressive hint:** Aggregate items and payments separately to one row per order before joining those aggregates.
   **Expected shape:** One row per order; no six-row multiplication.
5. **Debugging:** Repair a customer/order join whose `ON` clause compares unrelated IDs.
   **Progressive hint:** Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
   **Expected shape:** Exactly one customer match per order.
6. **Extension:** Calculate net line revenue by customer country without double-counting order totals.
   **Progressive hint:** Start from line items, join through orders and customers, then aggregate at country grain.
   **Expected shape:** One row per country represented by an order.

## Self-check

- Can you diagram every join as one-to-one or one-to-many before running it?
- Does each relationship predicate live in `ON`, with business filters placed
  deliberately?

## Next step

Continue to [Day 04 — outer joins](day04_outer_joins.md).

## Deep dive and reference

Learning objectives
- Join multiple tables with explicit INNER JOIN ... ON syntax
- Place join predicates vs row filters correctly (ON vs WHERE)
- Avoid fanout and duplicate rows; validate cardinalities
- Use table aliases and qualified names for clarity

Why this matters
Most analytical questions span multiple entities. Correct join logic preserves row counts, avoids duplicate multiplication, and keeps queries maintainable.

Core concepts and deep dive
- INNER JOIN returns rows where the join condition matches in both tables. Rows without matches are dropped.
- Predicate placement:
  - ON defines how rows from left and right relate. Keep relationship conditions here (keys, equality).
  - WHERE filters the result after joins. Put row-level filters here (time windows, status).
- Cardinality awareness: 1:1, 1:N, N:M. Validate with COUNT(*) vs COUNT(DISTINCT key) to detect accidental fanout.
- Joining chains: Join dimension tables (customers, products) to fact tables (orders, order_items) along keys. Prefer explicit column lists to avoid ambiguous names.

Walkthrough mapping to your schema
- orders o JOIN customers c ON c.customer_id=o.customer_id — adds customer context to orders.
- `order_items oi JOIN products p ON p.product_id=oi.product_id` brings product
  name, category, catalog price, and cost to lines.
- Multi-join: orders→order_items→products to compute revenue: SUM(oi.quantity*oi.unit_price*(1-oi.discount)).

Validation patterns
- Compare: SELECT COUNT(*) FROM orders vs SELECT COUNT(DISTINCT order_id) after joining order_items; counts should match if grouping by order_id.
- Check join selectivity: how many rows drop when adding additional ON predicates.

Anti-patterns and pitfalls
- Old-style comma joins with predicates in WHERE — easy to miss a condition and create cross joins; use explicit JOIN ... ON.
- Using LIKE to join keys; always use exact key equality unless justified.
- Ambiguity in column names after join; qualify columns to avoid surprises.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS
