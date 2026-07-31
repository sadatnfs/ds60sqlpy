# Bridge Day 6 — Bulk ETL and data validation

**Level:** Advanced  
**Prerequisite:** [Bridge Day 5](day05_db_testing_fixtures_doubles.md)

## Why this matters

Extract-transform-load (ETL) code crosses a trust boundary. Source strings may
be malformed, duplicated, too large, or semantically invalid. A sound pipeline
converts raw rows into a typed record before loading, keeps rejection
diagnostics minimal, and writes batches with parameter binding. Performance
comes after the data contract is explicit.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day06_bulk_etl_validation.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day06_bulk_etl_validation.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day06_bulk_etl_validation.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- validate an external mapping into an immutable typed record;
- preserve exact decimal money and parse ISO dates;
- separate accepted and rejected rows without exposing whole records;
- create deterministic batches with tested boundary cases;
- compare `executemany()` and Psycopg `COPY` tradeoffs;
- use a source ID and `ON CONFLICT` for restart-safe loading.

## Vocabulary

| Term | Meaning |
|---|---|
| ETL | Extract data, transform it to a contract, then load it |
| schema | The expected fields, types, and constraints of a record or table |
| quarantine | A controlled destination for rejected records or diagnostics |
| batch | A bounded group handled as one loading unit |
| upsert | Insert a new row or update the conflicting existing row |
| COPY | PostgreSQL's high-throughput bulk transfer protocol |
| data lineage | Information about where a record came from and how it changed |


## Worked example: conversion is part of validation

```python
raw_amount = "12.345"
amount = Decimal(raw_amount)
if not amount.is_finite() or amount <= 0:
    raise RowValidationError("amount must be finite and positive")
normalized = amount.quantize(Decimal("0.01"))
```

This creates a declared rounding policy and rejects `NaN` or infinity. Binary
`float` is a poor money boundary because values such as `0.1` are not exact.

Decide separately:

- **record validity:** can one row become a `Sale`?
- **batch policy:** how many validated rows are submitted together?
- **load semantics:** insert-only, upsert, or reject duplicates?
- **transaction policy:** all rows, one batch, or another recovery unit?


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: validate, partition, batch, load, reconcile

Bulk work is easier to reason about as a pipeline with named boundaries.
Validation converts one external mapping into an immutable typed `Sale`.
Partitioning separates accepted records from small safe rejection facts.
Batching bounds memory and parameter volume. Loading sends values separately
from SQL structure. Reconciliation compares what was accepted, submitted, and
stored. Skipping any boundary makes a fast loader hard to trust.

Conversion is part of validation. `"12.30"` should become `Decimal("12.30")`,
an ISO date should become `date`, and `NaN` or infinity should fail before the
driver sees them. Never mutate the source mapping while cleaning it; returning
a new value keeps raw evidence and accepted state distinct.

A batch helper has a simple, testable contract:

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def chunks(values: Sequence[T], size: int) -> list[tuple[T, ...]]:
    if size < 1:
        raise ValueError("size must be positive")
    return [tuple(values[i : i + size]) for i in range(0, len(values), size)]


assert chunks([1, 2, 3, 4, 5], 2) == [(1, 2), (3, 4), (5,)]
assert chunks([], 2) == []
```

Accounting words must not blur together. *Accepted* rows passed validation.
*Rejected* rows did not. *Submitted* rows were handed to the driver.
*Inserted* and *updated* describe database outcomes and may require returned
data or reconciliation to distinguish. `executemany()` returning normally does
not by itself prove every intended semantic outcome.

For larger inputs, a streaming validator and bounded flushes prevent
materializing the whole file. COPY can improve throughput, but safe values,
staging-table validation, transaction ownership, and set-based merge rules
still matter. Design replay behavior before optimizing: a stable `source_id`
can make upsert converge, while an append-only audit domain may need to reject
duplicates instead. Rejection metrics should use a bounded reason taxonomy,
never source IDs or entire invalid records as labels.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Validate untrusted rows before I/O, retain minimal rejection evidence, batch deterministically, and submit typed parameters through an idempotent bulk boundary.
- **Assumptions:** Money is finite, positive, and quantized to two decimals; source IDs are stable replay keys; raw records may contain sensitive fields.
- **Primary failure mode:** Bulk speed does not excuse weak validation, unbounded materialization, or diagnostics that copy entire rejected records.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Validation:** Implement `parse_sale()` for non-blank source ID, positive integer customer
   ID, finite positive amount, and ISO date without mutating input.
   - **Progressive hint:** Convert each field explicitly and translate only expected conversion
     failures.
   - **Verify:** Parse one valid mapping and compare exact typed fields; assert blank source ID, non-positive/non-integer customer ID, non-finite/non-positive amount, and bad ISO date raise `RowValidationError`, and the input mapping is unchanged.
2. **Money:** Quantize accepted amounts to two decimals and document the chosen rounding rule.
   - **Progressive hint:** Quantization is a domain decision, not merely display formatting.
   - **Verify:** Check amounts with more than two places and a halfway value; assert the exact two-place `Decimal` results under the documented rounding mode, not merely formatted strings.
3. **Partitioning:** Implement `partition_rows()` so accepted sales and rejected source
   IDs/reasons retain input order without storing full raw rows.
   - **Progressive hint:** Catch only `RowValidationError` from the conversion boundary.
   - **Verify:** Feed valid-invalid-valid rows; assert accepted sales and rejection `(source_id, reason)` records preserve input order and no rejected object stores the complete raw mapping.
4. **Batching:** Implement `batches()` with positive-size validation and tests for empty, exact,
   and remainder cases.
   - **Progressive hint:** Slice deterministic tuples from the original sequence.
   - **Verify:** Assert `batches([], 2) == []`, exact division has no empty tail, a remainder becomes the last tuple, and sizes `0`/negative raise `ValueError`.
5. **Bulk SQL:** Implement a parameterized `executemany()` upsert into `pg_temp.bridge_sales`
   with no values in SQL text.
   - **Progressive hint:** Convert typed sales to one parameter tuple per row.
   - **Verify:** Inspect one `executemany` call: SQL contains placeholders and the upsert clause, every sale value exists only in parameter rows, and empty input makes no driver call.
6. **Accounting:** Track accepted, rejected, submitted, inserted, and updated counts separately
   and state what `executemany()` cannot cheaply distinguish.
   - **Progressive hint:** Do not infer business outcomes from submitted row count.
   - **Verify:** For a mixed fixture, report separate accepted, rejected, and submitted counts; label inserted/updated as unknown unless returned/reconciled database evidence distinguishes them.
7. **Extension:** Design the Psycopg COPY variant using typed `write_row()` calls and a staging
   table instead of hand-built delimited text.
   - **Progressive hint:** COPY handles transport; a later set-based statement owns merge
     semantics.
   - **Verify:** Provide a COPY design that calls typed `write_row` into a staging table, validates staging rows, and performs one set-based merge without constructing delimited text.
8. **Edge cases:** Test NaN, infinities, zero, negatives, whitespace IDs, leading-zero customer
   IDs, and invalid dates.
   - **Progressive hint:** Classify each rejection at the field boundary and keep its reason
     safe.
   - **Verify:** Parameterize `NaN`, both infinities, zero, negative amount, blank ID, leading-zero customer ID, and invalid dates; compare exact acceptance or `RowValidationError` outcome.
9. **Idempotency:** Choose a policy for duplicate `source_id` values within one input batch and
   test it before database submission.
   - **Progressive hint:** Database upsert resolves persisted conflicts but may hide
     contradictory source rows.
   - **Verify:** Choose reject-first, reject-all, or deterministic-last-wins for duplicate `source_id`; assert the chosen result is decided before `executemany` and documented in counts.
10. **Scale design:** Compare materializing all accepted rows with a streaming validator and
   identify where bounded memory changes APIs.
   - **Progressive hint:** A tuple return is convenient for lessons but not for unlimited
     sources.
   - **Verify:** Compare peak retained rows for materialized and streaming designs; the streaming API must emit bounded batches/rejections without requiring the entire input sequence.
11. **Capacity:** Select batch size from parameter count, row width, memory, and transaction
   duration rather than a universal constant.
   - **Progressive hint:** Measure the real adapter and keep a safe configurable default.
   - **Verify:** Show a batch-size calculation using parameter count, row width, memory budget, and transaction-duration target; assert the selected size stays below every stated limit.
12. **Transaction failure:** Specify behavior when `executemany()` fails halfway and identify
   which layer owns rollback and retry.
   - **Progressive hint:** Submission count is not committed count.
   - **Verify:** Inject a mid-load driver failure; assert the transaction owner rolls back the complete unit, the loader does not claim partial success, and retry starts from a defined boundary.
13. **Observability:** Create a bounded rejection taxonomy and metrics that do not use source
   IDs or raw reasons as tags.
   - **Progressive hint:** Metric labels must come from a fixed vocabulary.
   - **Verify:** Inspect metrics for a fixed rejection-reason enum and bounded outcome tags; assert no source ID, raw reason text, or complete rejected row appears as a tag.
14. **Reconciliation:** Design a replay test that loads the same accepted sales twice and
   reconciles source IDs and total amount.
   - **Progressive hint:** Idempotency is proven by stable final state, not by absence of
     exceptions.
   - **Verify:** Load the accepted fixture twice under the declared upsert policy; reconcile the same source-ID set and exact total amount after both runs with no duplicate logical sale.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Optional live-DB step

Within one disposable connection, create a temporary target:

```sql
CREATE TEMP TABLE bridge_sales (
    source_id text PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES training.customers(customer_id),
    amount numeric(12,2) NOT NULL CHECK (amount > 0),
    occurred_on date NOT NULL
) ON COMMIT DROP;
```

Load a tiny valid batch twice, verify the stable final row count, and explicitly
roll back. The reference SQL uses `pg_temp.bridge_sales`, which cannot resolve
to a persistent production table.

```powershell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

```bash
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

## Self-check

- Does malformed input become a rejection rather than a partial `Sale`?
- Are `NaN`, infinity, zero, negative money, and invalid dates rejected?
- Does every batch preserve input order and stay within the size?
- Are values sent separately from the upsert text?
- Can a rerun produce the same logical target state?

## Common pitfalls

- **Loading before validating:** one bad row can abort a large transaction late.
- **Catching every exception as “bad data”:** database outages and programming
  bugs must not become quarantine rows.
- **Logging raw rejected records:** they may contain personal or secret fields.
- **Reporting submitted rows as inserted rows:** upserts and conflicts make
  those different metrics.
- **One enormous transaction:** it increases lock time, rollback cost, and
  recovery work.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-05`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-06: Bulk ETL Validation.
Direct catalog prerequisites: bridge-05. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day06_bulk_etl_validation.md
Learner artifact: bridge/lessons/day06_bulk_etl_validation.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

[Day 7](day07_async_bounded_concurrency.md) introduces async database I/O while
keeping concurrency bounded. Review
[the Day 6 solution notes](../solutions/day06_solutions.md) after your attempt.
