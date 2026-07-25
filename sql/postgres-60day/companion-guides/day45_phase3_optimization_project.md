# Day 45 — Phase 3 Optimization Project

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 44 — monitoring and diagnostics](day44_monitoring_diagnostics.md)
  and the complete performance sequence from Days 31–44
- **Artifacts:** [learner SQL](../day45_phase3_optimization_project.sql) ·
  [solution reasoning](../solutions/day45_solutions.md) ·
  [executable solution](../solutions/day45_solutions.sql)

## Learning objectives

- Run a controlled optimization experiment with comparable plans and outputs.
- Report measured improvement honestly, including a result below the target.

## Vocabulary and concepts

- **Experimental control:** fixed query semantics, data, parameters, and
  environment for a comparison.
- **Buffer evidence:** shared/local block hits, reads, dirties, and writes
  reported by `BUFFERS`.
- **Regression check:** proof that a rewrite preserves the defined output.

## Worked example / walkthrough

Capture the function-wrapped date baseline, rewrite it as a raw half-open range,
and add one candidate index inside the rollback transaction. Run both forms
several times, reconcile country/unit results, and calculate percentage change
from comparable observations without promising 70%.

## Exercises

Complete the project in the [learner SQL](../day45_phase3_optimization_project.sql).
Produce a short decision record covering plan, buffers, timing, correctness,
index cost, and whether the candidate should proceed.

## Self-check

- Are result keys and totals identical before performance is discussed?
- Does the recommendation distinguish the compact seed from representative
  production-scale evidence?

## Next step

Continue to [Day 46 — e-commerce LTV and cohorts](day46_project1_ecommerce_part1.md).

## Deep dive and reference

## Project goal

Measure a recent country-units query, make its predicate and aggregation more
efficient, and attempt to reduce runtime by more than 70% without changing the
result.

## What the learner script compares

1. A baseline whose date filter wraps `orders.order_date` in `date_trunc`.
2. A sargable raw-column date range after adding an `orders(order_date)` index.
3. A rewrite that pre-aggregates `order_items.quantity` by `order_id` before the
   country rollup.

All DDL and plans are inside a transaction and roll back.

## Evidence to collect

- exact SQL and seed/setup version;
- row counts and country-to-units totals for correctness;
- `EXPLAIN (ANALYZE, BUFFERS)` before and after;
- execution time, shared buffer hits/reads, rows, loops, and scan/join types;
- candidate index size and expected write cost; and
- percentage improvement calculated from comparable timings.

## Optimization reasoning

- A raw `order_date >= boundary` predicate can use a normal B-tree range.
- Set-based pre-aggregation avoids repeated line-level work.
- A covering order-item index may help but remains a measured candidate.
- Small tables can legitimately use sequential scans.

## The 70% target is not guaranteed

The target is an experiment goal, not a promised result on the compact
deterministic seed. Planning overhead, cache state, and small table size can
dominate. Report the observed percentage honestly, reconcile outputs, and use a
representative-scale dataset before recommending production changes.

Production index creation requires a separate reviewed migration and may need
`CREATE INDEX CONCURRENTLY`; the tutorial transaction intentionally persists
nothing.
