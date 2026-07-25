# Day 60 — Final Capstone, Part 3: End-to-End Sign-off

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 59 — stakeholder analytics](day59_final_capstone_part2.md)
  and completed evidence from the full SQL track
- **Artifacts:** [learner SQL](../day60_final_capstone_part3.sql) ·
  [solution reasoning](../solutions/day60_solutions.md) ·
  [executable solution](../solutions/day60_solutions.sql)

## Learning objectives

- Apply explicit acceptance criteria to data quality, business metrics,
  performance evidence, and documentation.
- Produce a handoff that separates verified results, limitations, and future
  production work.

## Vocabulary and concepts

- **Acceptance criterion:** an observable condition required for sign-off.
- **Evidence bundle:** reproducible query, environment, output, reconciliation,
  and interpretation.
- **Handoff:** documentation that lets another person operate, verify, and
  extend the work safely.

## Worked example / walkthrough

Take customer LTV through the final evidence loop: state one-customer grain and
revenue scope, run the view query, reconcile summed LTV with
`SUM(orders.total_amount)`, capture the result and environment, and record any
exception with owner and next action. Apply the same loop to each deliverable.

## Exercises

Complete every acceptance item in the [learner SQL](../day60_final_capstone_part3.sql).
Produce a final checklist that links each claim to its query and evidence rather
than marking work complete from prose alone.

## Self-check

- Does every sign-off claim have reproducible evidence and a named limitation
  or owner where applicable?
- Are tutorial views and indexes still rollback-only unless a separate reviewed
  migration explicitly persists them?

## Next step

Review any weak SQL areas, then combine both languages in the
[Python and PostgreSQL engineering bridge](../../../bridge/README.md). The
bridge expects at least Python Day 15 and SQL Day 15.

## Deep dive and reference

Day 60 defines acceptance criteria rather than discrete exercises. The final
submission connects reusable DQ checks, business views, stakeholder outputs,
performance evidence, and a written handoff.

## Deliverable 1 — Data quality

- `v_dq_customers`: total rows plus invalid email, country, and name counts.
- `v_dq_orders`: total rows plus negative totals and missing customers.
- Document every nonzero result with remediation, owner, and severity.

## Deliverable 2 — Core business views

- Customer LTV at one row per customer, retaining zero-order customers.
- Monthly order revenue with previous month and safely divided month-over-month
  growth.
- Reconcile summed customer LTV to summed `orders.total_amount`; expected
  difference on the seed is zero.

## Deliverable 3 — Stakeholder outputs

- Finance: current-year budget versus actual by month/category.
- Marketing: active customers by signup cohort and lifecycle month 0–6. A true
  retention rate also needs the cohort-size denominator from Day 47.
- Operations: an actual plan for recent units by product category.

## Deliverable 4 — Performance sign-off

Capture before/after `EXPLAIN (ANALYZE, BUFFERS)` for critical queries and record
dataset size, PostgreSQL version, indexes, timing, buffers, correctness check,
and decision. The requested under-10-second goal applies to the measured learner
machine/dataset; the compact seed does not prove production-scale performance.

## Deliverable 5 — Written handoff

Document DQ exceptions, model grain, join rationale, KPI definitions,
reconciliation, freshness-versus-speed tradeoffs, known limitations, and next
steps. Evidence must support every sign-off claim.

## State and safety

The learner file ends with `ROLLBACK`; its views and indexes do not persist.
Replace it with `COMMIT` only as a deliberate reviewed migration. Days 59–60 are
capstone criteria/checkpoints, so measured evidence and documentation are part
of the deliverable, not optional stretch work.
