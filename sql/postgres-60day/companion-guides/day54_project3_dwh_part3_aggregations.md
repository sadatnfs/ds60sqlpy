# Day 54 — Data Warehouse Project, Part 3: Aggregates

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Review [Day 53 — slowly changing dimensions](day53_project3_dwh_part2_scd.md)
  and retain the committed Day 52 warehouse in the same database. Day 54 does
  not depend on Day 53's rolled-back changes.
- **Artifacts:** [learner SQL](../day54_project3_dwh_part3_aggregations.sql) ·
  [solution reasoning](../solutions/day54_solutions.md) ·
  [executable solution](../solutions/day54_solutions.sql)

## Learning objectives

- Build aggregate tables with an enforced monthly grain.
- Refresh one period idempotently and reconcile it with warehouse facts.

## Vocabulary and concepts

- **Aggregate table:** persisted summaries at a coarser fact grain.
- **Idempotent refresh:** a rebuild whose repeated execution yields the same
  target-period rows.
- **Late-arriving fact:** a fact received after its reporting period was first
  built.

## Worked example / walkthrough

For one target year/month, delete category, customer, and product aggregate
rows, rebuild each independently from facts, and commit or roll back the whole
unit together. Reconcile each table's period revenue with a fact-only control
before considering the refresh successful.

## Exercises

Complete these in the
[learner SQL](../day54_project3_dwh_part3_aggregations.sql):

1. Add and validate `agg_sales_product_month`.
2. Refresh all aggregates for a supplied year/month.
3. Explain late-fact effects on closed months.
4. Implement transactional delete/insert for one month.
5. Make missing-side reconciliation NULL-safe.
6. Prove the refresh is idempotent.

Refresh twice and compare row counts and totals.

## Self-check

- Does each primary key exactly match the documented aggregate grain?
- Can a late fact be incorporated through a deliberate period backfill?

## Next step

Continue to [Day 55 — BI drill-downs](day55_project4_bi_part1.md).

## Deep dive and reference

## Project focus

- Build monthly category and customer aggregate tables.
- Add a monthly product aggregate with a declared primary-key grain.
- Refresh one period idempotently and reconcile it to facts.

## Preconditions and state

Run Day 52 first in the same database. The learner creates its aggregate tables,
loads them, performs data-quality checks, and rolls the entire Day 54 transaction
back.

The starter grains are `(year, month, category)` and
`(year, month, customer_sk)`. Revenue is summed from `fact_sales.amount`; date
attributes come from `dim_date`.

## Practice — match the learner prompts exactly

1. Create `agg_sales_product_month` at
   `(year, month, product_sk)` grain with revenue, units, and distinct orders,
   then validate it against `fact_sales`.
2. Create a stored procedure accepting year and month that deletes and rebuilds
   category, customer, and product aggregates for that target period.

## Refresh design

- Delete and insert all related aggregates in one transaction.
- A period rebuild is idempotent when the primary-key grain is correct.
- Filter facts through `dim_date.year` and `dim_date.month`.
- Aggregate each side independently before reconciliation to prevent fanout.

## Validation and limits

- Every refreshed month's aggregate revenue must equal fact revenue.
- Orphan surrogate keys must be zero.
- Late facts require rerunning affected periods or a deliberate backfill window.
- The compact seed does not need aggregates for speed; this is a warehouse
  serving-pattern exercise.
- Day 54 does not require rolled-back Day 53 audit/SCD changes.
