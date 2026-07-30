# Day 23 — Common Table Expressions (CTEs) Introduction (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 22 — advanced windows](day22_advanced_windows.md)
- **Artifacts:** [learner SQL](../day23_ctes_intro.sql) ·
  [solution reasoning](../solutions/day23_solutions.md) ·
  [executable solution](../solutions/day23_solutions.sql)

## Learning objectives

- Decompose a query into named stages with an explicit grain at each stage.
- Explain when PostgreSQL may inline or materialize a non-recursive CTE.

## Vocabulary and concepts

- **CTE:** a statement-local named query introduced by `WITH`.
- **Inlining:** planner substitution of a CTE into the surrounding query.
- **Materialization:** evaluating and storing an intermediate relation before
  later use.

## Worked example / walkthrough

Trace `order_lines` at one row per order, then `top_customers` at one row per
customer, then the final top-N presentation. Run each CTE body independently
while developing and verify its key uniqueness before adding the next stage.

## Practice assumptions and review method

- **Focus:** Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
- **Assumptions:** Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
- **Failure to watch for:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build order-level net value in one CTE and summarize it by customer in the outer query.
   **Progressive hint:** Name the one-row-per-order grain before changing to customer grain.
   **Expected shape:** One row per ordering customer.
2. **Query writing:** Use one category-revenue CTE twice to return the highest category and total revenue.
   **Progressive hint:** A named aggregate can support multiple scalar reads without repeating the business formula.
   **Expected shape:** One summary row.
3. **Query writing:** Create staged payment reconciliation CTEs at order grain.
   **Progressive hint:** Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
   **Expected shape:** One row per order.
4. **Prediction:** Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
   **Progressive hint:** Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
   **Expected shape:** Two count rows with equal values.
5. **Debugging:** Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
   **Progressive hint:** Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
   **Expected shape:** One row per country.
6. **Extension:** Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
   **Progressive hint:** The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
   **Expected shape:** One summary row for a bounded three-product update.

## Self-check

- Can later stages reference only columns deliberately exposed by earlier ones?
- Is `MATERIALIZED` or `NOT MATERIALIZED` used only for a measured reason?

## Next step

Continue to [Day 24 — recursive CTEs](day24_recursive_ctes.md).

## Deep dive and reference

Learning objectives
- Rewrite subqueries as CTEs (WITH ...) to improve readability and reuse
- Understand evaluation order and CTE inlining/materialization in Postgres
- Structure multi-step analytical pipelines with clean, named stages

Why this matters
CTEs make complex queries understandable. By naming intermediate results, you reduce cognitive load and avoid repeating logic. Postgres can inline non-recursive CTEs (since v12), so you often get both clarity and performance.

Core concepts and deep dive
- Syntax: WITH name AS (subquery) SELECT ... FROM name ...; Multiple CTEs are comma-separated.
- Visibility: CTEs are visible only to the main query and to subsequent CTEs defined after them.
- Evaluation (Postgres specifics):
  - Pre-v12: non-recursive CTEs were optimization fences (always materialized). v12+ can inline them; the planner may treat them as simple subqueries.
  - Use MATERIALIZED/NOT MATERIALIZED hints (v12+) to force/forbid materialization if needed.
- Reuse: you can reference a CTE multiple times to avoid recomputing complex expressions. Be mindful: if inlined, the planner may duplicate work; consider MATERIALIZED.

Walkthrough of the day’s script
- order_lines CTE aggregates order-level revenue by joining orders and order_items, producing one row per order_id and customer_id.
- top_customers CTE rolls order_lines up to lifetime_revenue per customer.
- The final SELECT orders customers by lifetime revenue and returns the top 20. This expresses a clear two-stage pipeline: lines → customers.

Design patterns
- “Stage and refine”: build granular CTEs (lines), then roll-ups (customers), then selections (top-N).
- “Filter early”: push selective WHERE predicates into earlier CTEs to reduce data volume in later stages.
- Parameterization with psql variables: WHERE order_date >= :'since'.

Pitfalls
- Overusing CTEs for tiny subqueries can hurt readability and prevent predicate pushdown if forced materialization.
- Reusing a heavy CTE many times without MATERIALIZED can multiply work if the planner inlines it.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
- MATERIALIZED/NOT MATERIALIZED: https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-MATERIALIZED
