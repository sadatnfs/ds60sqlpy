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

## Exercises

Complete the prompts in the [learner SQL](../day23_ctes_intro.sql). Annotate each
CTE name with its expected grain and one validation query.

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

Exercises from the learner script
1) Create a monthly-revenue CTE from orders and order items, then select the top
   three months.
2) Create a CTE that filters Electronics order lines, then aggregate their net
   revenue by customer country.

The setup has `orders.total_amount`, not an `order_total` column. The maintained
answer calculates net line revenue explicitly so the same expression is used
throughout the course.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
- MATERIALIZED/NOT MATERIALIZED: https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-MATERIALIZED
