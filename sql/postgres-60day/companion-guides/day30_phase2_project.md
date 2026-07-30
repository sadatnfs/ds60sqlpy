# Day 30 — Phase 2 Project: Cohort Retention and CLV (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 29 — pattern matching](day29_pattern_matching.md) and
  the complete window/CTE sequence from Days 16–29
- **Artifacts:** [learner SQL](../day30_phase2_project.sql) ·
  [solution reasoning](../solutions/day30_solutions.md) ·
  [executable solution](../solutions/day30_solutions.sql)

## Learning objectives

- Build cohort-size, activity, retention, and revenue measures at compatible
  grains.
- Present an illustrative projection with explicit model limitations.

## Vocabulary and concepts

- **Cohort:** entities grouped by a shared starting period or event.
- **Retention denominator:** the original eligible population for a cohort.
- **Calendar spine:** explicit cohort/period combinations, including periods
  with no observed activity.

## Worked example / walkthrough

Calculate cohort size directly from customers at one row per signup cohort.
Separately deduplicate activity to one row per customer/order month, derive
month offset, and count active customers. Join numerator to denominator only
after both relations are stable, then guard and range-check the retention rate.

## Practice assumptions and review method

- **Focus:** Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
- **Assumptions:** Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
- **Failure to watch for:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate original customer count for each UTC signup cohort month.
   **Progressive hint:** Build the denominator from customers, including customers who never order.
   **Expected shape:** One row per cohort month.
2. **Query writing:** Calculate active customers and net line revenue for each cohort/order month.
   **Progressive hint:** Aggregate line items to order grain before cohort joins, then count distinct active customers.
   **Expected shape:** One row per observed cohort/order month.
3. **Query writing:** Calculate cohort month offset and retention using original cohort size.
   **Progressive hint:** Use year-plus-month age components and guard the denominator.
   **Expected shape:** Observed cohort/offset rows with retention from 0 to 1.
4. **Prediction:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
   **Progressive hint:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
   **Expected shape:** Thirteen rows per cohort.
5. **Debugging:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
   **Progressive hint:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
   **Expected shape:** One row per observed cohort/month with nullable guarded measures.
6. **Extension:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
   **Progressive hint:** Calculate violations and compare totals at the same scoped population.
   **Expected shape:** One row with zero retention violations and zero revenue difference.

## Self-check

- Is `active_customers <= cohort_size` for every row and is retention in
  `[0, 1]`?
- Does the projection exclude current-period leakage and disclose sparse-month,
  margin, churn, and uncertainty limits?

## Next step

Continue to [Day 31 — EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md).

## Deep dive and reference

Goal
- Extend the starter customer-cohort analysis with retention rates and an
  illustrative customer-lifetime-value projection.

Current practice map
- The six maintained prompts above are the complete deliverable: denominator,
  activity and revenue, retention, a dense offset spine, a limited teaching
  projection, and a reconciliation/constraint audit.

Guidance
1) Aggregate net order-line value to one row per order before cohort joins.
2) Calculate month offsets with year and month components from `age`; extracting
   only the month component wraps after 12 months.
3) Use the original cohort size as the retention denominator, including
   customers who never order.
4) Apply the moving window after revenue per active customer is computed.
5) Reconcile order-value totals to the underlying line-item formula.

Explicit limitations
- The maintained projection annualizes a trailing three-observation average of
  revenue per active customer. It is a teaching heuristic, not a production CLV
  model.
- Observed order months are not a dense calendar. A three-row frame may span
  missing month offsets unless you add a cohort calendar.
- The model does not incorporate margin, churn probability, discount rate,
  acquisition cost, or uncertainty.

Quality checklist
- `active_customers <= cohort_size` and retention remains between 0 and 1.
- Revenue is not multiplied by line or cohort joins.
- Cohort definition, active-customer rule, missing-month treatment, and
  projection horizon are stated beside the query.
