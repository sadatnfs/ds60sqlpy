---
phase: 11-post-release-hardening-content-completion
plan: 02
subsystem: test-suite
status: complete
requirements: [HARD-06]
requirements-completed: []
tags: [tests, xdist, flaky, timeouts, determinism]
requires: []
provides:
  - load-tolerant hang guards in the Apache run.sh, JAX and PyTorch authoring tests
  - a deterministic slow-subscriber backpressure test in the LLM serving contract
affects: [11-08]
key-files:
  created:
    - .planning/phases/11-post-release-hardening-content-completion/11-02-SUMMARY.md
  modified:
    - tests/test_apache_data_platforms.py
    - tests/test_apache_hive_preparation.py
    - tests/test_apache_kafka_retention.py
    - tests/test_apache_kafka_startup.py
    - tests/test_apache_orchestration.py
    - tests/test_apache_prepared_routes.py
    - tests/test_jax_lessons.py
    - tests/test_llm_serving_contract.py
    - tests/test_pytorch_lessons.py
decisions:
  - The widened timeouts are hang guards on subprocesses, not performance assertions, so widening them does not hide a bug. Each test still fails if the process never finishes.
  - The slow-subscriber test was fixed at the root (it drained too early and relieved the backpressure under test) instead of getting a longer deadline alone, and it now asserts the producer gave up.
  - No retries, reruns or skips were added.
commits: [0ee8350c]
actuals:
  tasks: 3
  commits: 1
completed: 2026-11-24
---

# Phase 11 Plan 02: make the full local suite pass under pytest -n auto Summary

The tests that failed only under `pytest -n auto` load are fixed at their cause. Commit 0ee8350c
changed 9 test files (27 insertions, 24 deletions). HARD-06 is not marked complete here, because
the commit records neither the plan's two clean full parallel runs nor their counts. Release
verification in 11-08 closes it.

## Root causes and fixes

| Test area | Cause | Fix |
| --- | --- | --- |
| Apache `run.sh` fakes (6 files, 18 call sites) | 5 s subprocess hang guards tripped when xdist workers shared the CPU | Guards allow 60 s |
| `tests/test_jax_lessons.py` (2 sites) | 120 s authoring rebuild guard | 600 s |
| `tests/test_pytorch_lessons.py` (3 sites) | 30 s native-text authoring rebuild guard | 300 s |
| `tests/test_llm_serving_contract.py` slow subscriber | Drained the iterator after a 2 s deadline, which relieved the backpressure under test on a busy host | Waits (bounded at 60 s) for the producer to give up, asserts `one["id"] not in scheduler.work`, then checks the `subscriber_backpressure_timeout` reason and at most 5 tokens |

The Apache files are `test_apache_data_platforms.py` (5), `test_apache_hive_preparation.py` (4),
`test_apache_orchestration.py` (3), `test_apache_prepared_routes.py` (4),
`test_apache_kafka_retention.py` (1) and `test_apache_kafka_startup.py` (1). The `ballista` resume
candidate the plan named is in this group.

## Verification

- Each changed test keeps its original assertions. Only the hang-guard bounds and the
  slow-subscriber ordering changed, as the diff shows.
- The plan requires two consecutive full `-n auto` runs with fresh `--basetemp` directories and
  recorded counts. The commit and this phase's artifacts record no such run, so this summary
  claims none. The full-suite run belongs to the 2.1.0 release verification in plan 11-08.

## Deviations

- **No fix for two named candidates.** The plan listed "JavaScript reference parse" and
  "curriculum extensions" as known candidates. Commit 0ee8350c changes no test or source for
  either. Either they did not reproduce or other Phase 11 content commits fixed them; neither
  is evidenced here.
- **The two recorded full runs are missing** (plan task 3), as described under Verification.

## Self-Check: INCOMPLETE

- Task 1 (reproduce candidates): evidenced for the Apache, JAX, PyTorch and LLM serving
  candidates only.
- Task 2 (fix root causes): done in 0ee8350c.
- Task 3 (two full `-n auto` runs with counts): not recorded. It is deferred to plan 11-08.
