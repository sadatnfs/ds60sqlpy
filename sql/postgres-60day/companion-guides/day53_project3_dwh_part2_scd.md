# Day 53 — Data Warehouse Project, Part 2: SCD Type 2

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Run and verify committed
  [Day 52 — star-schema warehouse](day52_project3_dwh_part1.md) in the same
  database.
- **Artifacts:** [learner SQL](../day53_project3_dwh_part2_scd.sql) ·
  [solution reasoning](../solutions/day53_solutions.md) ·
  [executable solution](../solutions/day53_solutions.sql)

## Learning objectives

- Close one current dimension version and insert its successor atomically.
- Resolve facts to the dimension version valid on their event date.

## Vocabulary and concepts

- **SCD Type 2:** slowly changing dimension design that preserves version
  history as new rows.
- **Business key:** stable source identity shared by all versions.
- **Validity interval:** the dates or timestamps for which one version applies.

## Worked example / walkthrough

For one changed customer, locate exactly one current row, set its `valid_to` to
the day before the new version, and insert the successor at `CURRENT_DATE`.
Then as-of join a fact date using inclusive bounds and verify it resolves to one
surrogate key—not zero and not two.

## Exercises

Complete the prompts in the [learner SQL](../day53_project3_dwh_part2_scd.sql).
Add checks for multiple current versions, validity gaps, and overlapping
intervals.

## Self-check

- Are close and insert operations in one atomic transaction?
- Does temporal fact mapping preserve the source fact count exactly?

## Next step

Continue in the same database to
[Day 54 — warehouse aggregates](day54_project3_dwh_part3_aggregations.md).

## Deep dive and reference

## Project focus

- Detect changed customer and product attributes.
- Close the old current row and insert a new version.
- Map historical facts to the dimension version valid on the fact date.

## Preconditions and state

Run Day 52 first in the same database. Day 53 reads the committed `dwh` schema
but performs its changes inside a transaction and rolls them back.

The learner stages deterministic changes for ten customers and ten products.
For each changed business key, the current row closes at `CURRENT_DATE - 1`,
and the replacement starts at `CURRENT_DATE`.

## Practice — match the learner prompts exactly

1. Rebuild or test fact-key mapping with an as-of join:
   `valid_from <= order_date <= COALESCE(valid_to, infinity)` for both customer
   and product versions.
2. Add `updated_by` and `updated_at` to both changing dimensions, and stamp
   close/insert operations deliberately.

## SCD reasoning

- Close and insert are one atomic transaction.
- `customer_id` and `product_id` are business keys; their surrogate keys identify
  versions.
- Inclusive bounds require the old row to end one day before the new row starts.
- A production dimension should prevent more than one current row per business
  key and overlapping validity ranges.

## Validation and limits

- Temporal fact mapping count must equal source item count.
- A lower count signals a date/version gap; a higher count signals overlapping
  versions.
- Audit defaults cover inserts but do not explain update actors; set them on
  close operations too.
- The course uses date-grain validity. Timestamp-effective changes require a
  different boundary model.
