# Day 42 — Data Quality and Validation

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 41 — complex aggregations](day41_complex_aggregations.md)
- **Artifacts:** [learner SQL](../day42_data_quality_validation.sql) ·
  [solution reasoning](../solutions/day42_solutions.md) ·
  [executable solution](../solutions/day42_solutions.sql)

## Learning objectives

- Encode repeatable quality rules with stable names, grains, and failure counts.
- Separate observed failures from remediation policy.

## Vocabulary and concepts

- **Invariant:** a condition expected to remain true for valid data.
- **Orphan:** a foreign-key-like value with no matching parent.
- **DQ result grain:** whether a check counts failing rows, keys, or duplicate
  groups.

## Worked example / walkthrough

Normalize email with `lower(trim(email))`, group it, and return groups with
`COUNT(*) > 1`. Keep the raw emails in a separate detail query: the summary
counts duplicate groups, while remediation needs the member records.

## Exercises

Complete these in the [learner SQL](../day42_data_quality_validation.sql):

1. Build a named core-table validation report.
2. Detect invalid/null customer emails.
3. Explain CHECK behavior for NULL without `NOT NULL`.
4. Reconcile order totals with calculated line revenue.
5. Retain raw case variants in a normalized-email duplicate report.
6. Detect overlapping inclusive promotion ranges.

For one rule, return both a summary and failing-record detail.

## Self-check

- Does every check expose its name, result grain, expected result, and observed
  failure count?
- Can a zero result be rerun on future data without implying a permanent
  guarantee?

## Next step

Continue to [Day 43 — logical backup and recovery](day43_backup_recovery.md).

## Deep dive and reference

## What you will learn

- Profile nulls and normalized duplicates.
- Check referential, range, quantity, and discount invariants.
- Return repeatable validation results with named checks and failure counts.

## How the learner script uses the current schema

The starter profiles `customers.email` and `customers.country`, searches for
duplicate emails, checks `order_items` and `payments` for orphan orders, and
looks for negative order/payment amounts. Foreign keys and checks should keep
many failures at zero, but the queries protect future imports and schema
changes.

## Validation design

- Give each rule a stable `check_name` and `failing_rows`.
- Normalize email with `lower(trim(email))` before duplicate grouping.
- Use anti-joins to test relationships even when foreign keys exist.
- Keep observed failures separate from remediation policy.
- Report the grain: duplicate groups, failing records, and orphan keys are
  different counts.

## Practice — match the learner prompts exactly

1. Build one validation report for core tables that summarizes null emails,
   normalized duplicate emails, negative totals, orphan references, invalid
   quantities, and discounts outside 0–1.
2. Return `customer_id` and `email` for null or regex-invalid email values.

## Pitfalls and validation

- The course email regex is a pragmatic check, not the full email RFC.
- A zero count means the checked rule passed on this snapshot, not that future
  loads are guaranteed clean.
- Do not auto-delete failed rows from a validation query.
- The deterministic seed should return zero for every core failure check and no
  invalid emails.

## Expanded practice lab

Prompts 3–6 progress from constraint semantics to reconciliations and diagnostic
evidence. SQL CHECK constraints pass both TRUE and UNKNOWN, so nullable fields
need a separate `NOT NULL` rule when NULL is invalid.

Reconcile stored totals to line revenue at order grain and use a one-cent
tolerance deliberately. A duplicate report should retain raw email variants.
For inclusive promotion dates, ranges overlap when each start is less than or
equal to the other range's end; compare each pair only once.
