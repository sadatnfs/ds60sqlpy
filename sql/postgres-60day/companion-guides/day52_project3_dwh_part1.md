# Day 52 — Data Warehouse Project, Part 1: Star Schema

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 51 — cash flow](day51_project2_finance_part3.md).
  Use only the course-owned disposable `dwh` schema; Day 52 resets and commits
  it for Days 53–54.
- **Artifacts:** [learner SQL](../day52_project3_dwh_part1.sql) ·
  [solution reasoning](../solutions/day52_solutions.md) ·
  [executable solution](../solutions/day52_solutions.sql)

## Learning objectives

- Declare fact and dimension grains before creating a star schema.
- Load surrogate keys and validate every fact-to-dimension relationship.

## Vocabulary and concepts

- **Fact table:** measurements/events at a declared business grain.
- **Dimension:** descriptive attributes joined to facts through keys.
- **Surrogate key:** warehouse-owned identifier for a dimension row or version.

## Worked example / walkthrough

Write the grain beside every table before loading it. Load `dim_date` and the
customer/product dimensions, then map each source order item to exactly one date,
customer, and product key in `fact_sales`. Compare fact row count with source
`order_items` and check every key resolves once before committing Day 52.

## Exercises

Complete these in the [learner SQL](../day52_project3_dwh_part1.sql):

1. Add `dim_country` and connect it to customers.
2. Build `fact_payments` at payment grain.
3. State/prove the `fact_sales` grain.
4. Add and test unknown dimension members.
5. Reconcile fact rows and amount to source.
6. Define a late-arriving date policy.

Run from a reset and save checks for Days 53–54.

## Self-check

- Does every fact table have a documented, enforced source grain?
- Did the script complete with `COMMIT`, and do all source/fact counts and key
  resolution checks pass?

## Next step

Continue in the same database to
[Day 53 — slowly changing dimensions](day53_project3_dwh_part2_scd.md).

## Deep dive and reference

## Project focus

- Define fact and dimension grain with surrogate keys.
- Load date, customer, product, and sales facts from `training`.
- Add a conformed country dimension and a payment fact.

## Stateful behavior

Day 52 is intentionally different from most lessons. It drops and recreates
only the course-owned `dwh` schema, builds its base warehouse, and commits it for
Days 53 and 54. Do not run it against a `dwh` schema containing unrelated work.

The base grains are:

- `dim_date`: one row per calendar date;
- `dim_customer`: Type-2-ready versions keyed by `customer_sk`;
- `dim_product`: Type-2-ready versions keyed by `product_sk`; and
- `fact_sales`: one row per source `order_item_id`.

## Practice — match the learner prompts exactly

1. Create `dim_country`, load one row per customer country code, add
   `country_sk` to `dim_customer`, backfill it, and enforce the relationship.
2. Create `fact_payments` at one row per source payment, linked to payment-day
   `dim_date` and the customer version valid on that date.

## Required Days 52–54 sequence

1. Run Day 52 once; it commits the base warehouse.
2. Run Day 53 in the same database; its exercise changes roll back.
3. Run Day 54 in the same database; its aggregate/procedure changes roll back.

Day 54 depends on committed Day 52 state, not on Day 53 changes persisting.

## Validation and limits

- `fact_sales` rows must equal source `order_items` rows.
- `fact_payments` rows must equal source `payments` rows.
- Every fact date and dimension key must resolve exactly once.
- Use `psql -v ON_ERROR_STOP=1`; a partial warehouse is not a passing load.
