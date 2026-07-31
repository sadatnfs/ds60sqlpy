# Day 34 — Solutions: Query Optimization Techniques


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day34_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day34_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Baseline, Predicate pushdown, Semantic equivalence. Its worked-model focus is:
Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

Optimization must preserve meaning. Compare plans only after confirming that
the original and rewritten queries return the same rows at the same grain.

## Exercise 1 — Replace a subquery with a join

The first query uses `EXISTS`; the second uses joins. `DISTINCT` is necessary in
the join form because one order can contain multiple Electronics lines.

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id,
       o.order_date
FROM orders o
WHERE EXISTS (
  SELECT 1
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  WHERE oi.order_id = o.order_id
    AND p.category = 'Electronics'
);

EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT o.order_id,
       o.order_date
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE p.category = 'Electronics';
```

PostgreSQL may already transform `EXISTS` into a semi-join, so the explicit join
is not automatically faster. Compare final row counts as well as cost and time.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 1, run the underlying read-only query over `orders`, `order_items`, and `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-34 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `order_date`.
- **Independent verification:** For sql-34 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-34 Exercise 1, start with the first relation in `orders`, `order_items`, and `products`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-34 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `order_id`, and finish with `order_id`, and `order_date`.
- **Alternative/trade-off:** For sql-34 Exercise 1, the chosen form is justified by this lesson-specific rationale: The first query uses `EXISTS`; the second uses joins. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 2 — Limit rows before enrichment

Both forms request the latest 100 orders with customer country. The second form
makes the bounded order set explicit before the dimension join.

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id,
       o.order_date,
       c.country
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 100;

EXPLAIN (ANALYZE, BUFFERS)
WITH top_orders AS MATERIALIZED (
  SELECT order_id,
         customer_id,
         order_date
  FROM orders
  ORDER BY order_date DESC, order_id DESC
  LIMIT 100
)
SELECT t.order_id,
       t.order_date,
       c.country
FROM top_orders t
JOIN customers c ON c.customer_id = t.customer_id
ORDER BY t.order_date DESC, t.order_id DESC;
```

Expected shape for either actual query: 100 rows when at least 100 orders exist.
`MATERIALIZED` is used here to make the learning contrast visible; in ordinary
code, allow PostgreSQL to inline a CTE unless an optimization fence is needed.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `top_orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-34 Exercise 2, expected output: at most 100 rows keyed by `order_id`. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
- **Independent verification:** For sql-34 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-34 Exercise 2, start with the first relation in `orders`, `customers`, and `top_orders`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-34 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, `customers`, and `top_orders`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, and `country` ordered by `t.order_date DESC, t.order_id DESC`.
- **Alternative/trade-off:** For sql-34 Exercise 2, the chosen form is justified by this lesson-specific rationale: Both forms request the latest 100 orders with customer country. Evaluate another form against the concrete expected result (at most 100 rows keyed by `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- A join can multiply rows. Never remove `EXISTS` without checking the
  relationship cardinality.
- “Filter early” is not a rule to duplicate everywhere; PostgreSQL can push
  many predicates itself.
- An early `LIMIT` is valid only when it selects the same ordered set the final
  query requires.
- Faster on one tiny seeded database is not sufficient evidence for a
  production rewrite.

## Exercise 3 — Compare CTE planner boundaries

`MATERIALIZED` computes/stores the CTE as a boundary. `NOT MATERIALIZED` permits
folding into the parent query. Compare plans; neither spelling is universally
faster.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 3, run the underlying read-only query over `orders`, `recent`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-34 Exercise 3, expected output: one row per `order_id`. The final columns are `materialized`.
- **Independent verification:** For sql-34 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-34 Exercise 3, start with the first relation in `orders`, `recent`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-34 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, `recent`, and `customers`, preserve one row per `order_id`, and finish with `materialized`.
- **Alternative/trade-off:** For sql-34 Exercise 3, the chosen form is justified by this lesson-specific rationale: `MATERIALIZED` computes/stores the CTE as a boundary. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Pre-aggregate to order grain

`item_totals` emits one row per order before customer/country joins. This
reduces fanout while preserving the unit total.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 4, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `units`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-34 Exercise 4, expected output: one row per order before customer/country joins. The final columns are `country`, and `units`. The final order is `c.country`.
- **Independent verification:** For sql-34 Exercise 4, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `units` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units` for the existing `country` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-34 Exercise 4, run `item_totals` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
- **Clause check:** For sql-34 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, `orders`, and `customers`, preserve one row per `country`, and finish with `country`, and `units` ordered by `c.country`.
- **Alternative/trade-off:** For sql-34 Exercise 4, the chosen form is justified by this lesson-specific rationale: `item_totals` emits one row per order before customer/country joins. Evaluate another form against the concrete expected result (one row per order before customer/country joins) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `units` for the existing `country` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Repair two-many-side fanout

Payments and items are independently many-to-one with orders. Each is grouped
by `order_id` before their results are joined, so amounts are never multiplied.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid_amount`, and `line_revenue`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-34 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
- **Independent verification:** For sql-34 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid_amount`, and `line_revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
- **Intermediate relation check:** For sql-34 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-34 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `payments`, `order_items`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `paid_amount`, and `line_revenue` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-34 Exercise 5, the chosen form is justified by this lesson-specific rationale: Payments and items are independently many-to-one with orders. Evaluate another form against the concrete expected result (at most 20 rows keyed by `order_id`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.

## Exercise 6 — Write a NULL-safe anti-join

`NOT EXISTS` asks whether a matching order exists for the current customer.
Unlike nullable `NOT IN`, one NULL produced by the inner relation cannot turn
every comparison into UNKNOWN.

### Reasoning and verification

- **Inputs/evidence:** For sql-34 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-34 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`. The final order is `c.customer_id`.
- **Independent verification:** For sql-34 Exercise 6, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `customers`, and `orders`. Repeat with `NULL` in `customer_id` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-34 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-34 Exercise 6, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `customer_id`, and finish with `customer_id` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-34 Exercise 6, the chosen form is justified by this lesson-specific rationale: `NOT EXISTS` asks whether a matching order exists for the current customer. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `customer_id` and state whether the row is kept, rejected, or classified.
