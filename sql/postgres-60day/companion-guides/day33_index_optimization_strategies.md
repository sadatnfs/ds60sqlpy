# Day 33 — Composite, Covering, and Partial Indexes

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 32 — index fundamentals](day32_index_fundamentals.md)
- **Artifacts:** [learner SQL](../day33_index_optimization_strategies.sql) ·
  [solution reasoning](../solutions/day33_solutions.md) ·
  [executable solution](../solutions/day33_solutions.sql)

## Learning objectives

- Order composite search keys from real predicate and ordering requirements.
- Separate search keys, included payload columns, and a partial-index predicate.

## Vocabulary and concepts

- **Leftmost prefix:** the leading composite-index keys usable by a query.
- **Included column:** payload stored with an index but not part of its search
  ordering.
- **Partial index:** an index containing only rows satisfying a fixed predicate.

## Worked example / walkthrough

For a query filtering `customer_id` and a date range, compare
`(customer_id, order_date)` with the reversed key order. Then check whether the
query predicate logically implies a partial-index predicate; mere overlap is
not enough for PostgreSQL to use that index safely.

## Exercises

Complete the prompts in the [learner SQL](../day33_index_optimization_strategies.sql).
For each candidate, write the exact query shape and expected maintenance tradeoff
before creating it.

## Self-check

- Can you identify search, order, and return-only columns separately?
- Is every partial predicate immutable and logically implied by its target
  query?

## Next step

Continue to [Day 34 — query optimization](day34_query_optimization.md).

## Deep dive and reference

## What you will learn

- Match composite-index order to filters and ordering.
- Use `INCLUDE` for covering columns that are not search keys.
- Use a partial index for a stable, explicitly defined subset.

## How the learner script uses the current schema

The script creates:

- `(customer_id, order_date)` on `orders`;
- `(order_id, product_id) INCLUDE (quantity, unit_price, discount)` on
  `order_items`; and
- a partial `orders(order_date)` index for statuses `placed` and `paid`.

The partial predicate is deliberately status-based. PostgreSQL index predicates
must be immutable, so a moving boundary such as `now() - interval '90 days'`
cannot appear in a partial-index definition.

## Design reasoning

- A composite B-tree is most useful from its leftmost key onward.
- `INCLUDE` columns can support index-only reads but do not participate in
  search ordering.
- A partial index is used only when the query predicate logically implies its
  stored predicate.
- Index-only scans are possible, not guaranteed; visibility and cost still
  matter.

## Practice — match the learner prompts exactly

1. Add a composite index on `products(category, created_at)` and test a query
   that filters category and a created-at range.
2. Add a partial index for `orders.total_amount > 1000` and test a query whose
   predicate implies that exact high-value subset.

For each exercise, compare the same query before and after the index and record
plan, row estimate, timing, and index size if useful.

## Pitfalls and validation

- `products` has no `active` column. Do not import an “active products” example
  from another schema.
- A query for `total_amount > 500` cannot generally use an index containing
  only rows greater than 1000.
- The compact seed may prefer a sequential scan; correctness and measured cost
  come before forcing a plan.
- All exercise indexes roll back with the learner transaction.
