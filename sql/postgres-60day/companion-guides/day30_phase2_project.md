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

## Exercises

Implement the project in the [learner SQL](../day30_phase2_project.sql). Add a
cohort/offset spine and compare absent rows with explicit zero-activity rows.

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

Deliverable from the learner script
1) Define cohort size from customer creation month.
2) Count active customers and revenue for each cohort/order month.
3) Compute retention as active customers divided by original cohort size.
4) Project CLV with a moving average, documenting the model and its limits.

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
