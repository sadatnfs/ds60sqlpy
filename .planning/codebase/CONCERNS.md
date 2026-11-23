---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
# Codebase Concerns

<!-- refreshed: 2026-11-23 -->
**Analysis Date:** 2026-11-23

## Tech Debt

**New Python/SQL step-through implementation has unverified edge cases (observed; suspected correctness risk):**
- Issue: The current branch adds a 1,972-line implementation combining Python tracing, SQL tokenization/planning, and response construction. No test file references `step_through`, `plan_sql`, `python_response`, or `sql_response`; the source docstring says the planner and response builders are intended to be testable without subprocesses or a database.
- Files: `src/ds60sqlpy/step_through.py`, `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/lab.py`, `tests/`
- Impact: SQL dialect edge cases or tracing/serialization regressions could produce misleading walkthroughs or fail to explain valid learner code. No specific failure was confirmed in this static review.
- Fix approach: Add table-driven unit tests for quoting, comments, nested expressions, CTEs, set operations, unsupported statements, and cursor positions. Add disposable PostgreSQL tests proving read-only behavior, timeout/cancellation handling, and bounded result files; cover the UI request/response path separately.

**Large multi-responsibility modules (observed; maintenance risk):**
- Issue: Several core modules exceed 2,000 lines: `src/ds60sqlpy/run_explain.py` (2,664), `src/ds60sqlpy/kubernetes_module.py` (2,321), `src/ds60sqlpy/lesson_reader.py` (2,106), and `src/ds60sqlpy/step_through.py` (1,972).
- Impact: Changes to parsers, rendering, and runtime behavior are harder to review in isolation and can make regressions less apparent.
- Fix approach: Split along stable responsibilities when those areas are next changed, keeping public contracts and focused tests in place. Avoid broad restructuring without behavior-specific regression coverage.

## Known Bugs

- No confirmed production bug was established from the inspected source. This is a static audit; the test suite was not run.

## Security Considerations

**Local pad execution is not a security sandbox (observed; high impact if deployment assumptions change):**
- Risk: `PadRunner` runs submitted Python/SQL code in child processes with the application environment and repository-root working directory. Timeouts, process-group cleanup, and output limits bound some failure modes, but do not by themselves prevent code from accessing files or network resources available to that process.
- Files: `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/notebook_execution.py`
- Current mitigation: `src/ds60sqlpy/execution.py` explicitly documents the trusted-local-code boundary and applies execution time/output limits. The separate optional worker path has authenticated requests, fixed profile commands, a dropped job identity, scratch/output bounds, and process cleanup in `src/ds60sqlpy/module_worker.py` and `src/ds60sqlpy/worker_operations.py`.
- Recommendations: Keep the local pad limited to trusted users and the documented local classroom model. Do not expose it as a shared or remote service for untrusted code. Any such expansion needs independently validated filesystem, network, identity, and resource isolation for every execution path, including step-through.

## Performance Bottlenecks

**Module execution is serialized across the classroom (observed; deliberate local-product limit):**
- Problem: `src/ds60sqlpy/module_jobs.py` rejects a new run while a job is active or unresolved; each worker in `src/ds60sqlpy/module_worker.py` also accepts one active operation.
- Cause: A single active application job and a single active job per worker are enforced in the job state and worker state.
- Improvement path: This matches the documented single-classroom workflow. If concurrent or multi-user serving becomes a requirement, add explicit queueing, per-user fairness, and resource isolation before increasing concurrency.

- No measured hot path or benchmark-confirmed performance regression was detected. Static inspection does not establish runtime throughput.

## Fragile Areas

**Step-through SQL planner and trace output:**
- Files: `src/ds60sqlpy/step_through.py`, `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/lab.py`
- Why fragile: A custom tokenizer/planner and trace serializer interact with PostgreSQL execution and UI payloads; the implementation is large and no tests in `tests/` currently exercise its public functions.
- Safe modification: Add focused parser and response tests first, then integration-test execution against disposable state. Preserve the existing read-only SQL transaction and time/output bounds.
- Test coverage: No matching tests were found; see **Test Coverage Gaps**.

## Scaling Limits

**Single active module run:**
- Current capacity: One active or unresolved module job per classroom, with one active operation per optional worker; source, duration, output, scratch-file, and scratch-size limits are enforced in `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`, and `src/ds60sqlpy/worker_operations.py`.
- Limit: Concurrent learners or simultaneous heavy runtimes queue by rejection rather than parallel execution.
- Scaling path: Retain the current boundary for the local single-learner product. A shared deployment would need an explicit queue and tenant isolation rather than simply removing the active-job checks.

## Dependencies at Risk

- No specific dependency risk was established from repository inspection. No external vulnerability or software-composition audit was run; dependency safety remains unverified by this mapping.

## Missing Critical Features

- Not detected from the requested static concerns review.

## Test Coverage Gaps

**Python/SQL step-through behavior:**
- What's not tested: The new line tracer, SQL planner, response builders, timeout/cancellation flow, and read-only database walkthrough have no matching automated test references in `tests/`.
- Files: `src/ds60sqlpy/step_through.py`, `src/ds60sqlpy/execution.py`, `tests/`
- Risk: Parser edge cases and learner-visible execution results can regress without the CI test suite detecting them.
- Priority: High.

**Coverage enforcement:**
- What's not tested: Coverage reporting is configured in `pyproject.toml`, but no minimum coverage threshold is configured, and the CI unit-test command in `.github/workflows/ci.yml` does not request coverage output.
- Files: `pyproject.toml`, `.github/workflows/ci.yml`
- Risk: Untested additions can pass CI as long as existing tests pass; the step-through gap above is a concrete example.
- Priority: Medium.

## Evidence

- `src/ds60sqlpy/step_through.py`
- `src/ds60sqlpy/execution.py`
- `src/ds60sqlpy/lab.py`
- `src/ds60sqlpy/module_jobs.py`
- `src/ds60sqlpy/module_worker.py`
- `src/ds60sqlpy/worker_operations.py`
- `tests/`
- `pyproject.toml`
- `.github/workflows/ci.yml`

---

*Concerns audit: 2026-11-23*
