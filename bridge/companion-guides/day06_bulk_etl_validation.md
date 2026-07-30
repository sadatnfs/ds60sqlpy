# Bridge Day 6 — Bulk ETL and data validation

**Level:** Advanced  
**Prerequisite:** [Bridge Day 5](day05_db_testing_fixtures_doubles.md)

## Why this matters

Extract-transform-load (ETL) code crosses a trust boundary. Source strings may
be malformed, duplicated, too large, or semantically invalid. A sound pipeline
converts raw rows into a typed record before loading, keeps rejection
diagnostics minimal, and writes batches with parameter binding. Performance
comes after the data contract is explicit.

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

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day06_bulk_etl_validation.py
```

```bash
.venv/bin/python bridge/lessons/day06_bulk_etl_validation.py
```

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
2. **Money:** Quantize accepted amounts to two decimals and document the chosen rounding rule.
   - **Progressive hint:** Quantization is a domain decision, not merely display formatting.
3. **Partitioning:** Implement `partition_rows()` so accepted sales and rejected source
   IDs/reasons retain input order without storing full raw rows.
   - **Progressive hint:** Catch only `RowValidationError` from the conversion boundary.
4. **Batching:** Implement `batches()` with positive-size validation and tests for empty, exact,
   and remainder cases.
   - **Progressive hint:** Slice deterministic tuples from the original sequence.
5. **Bulk SQL:** Implement a parameterized `executemany()` upsert into `pg_temp.bridge_sales`
   with no values in SQL text.
   - **Progressive hint:** Convert typed sales to one parameter tuple per row.
6. **Accounting:** Track accepted, rejected, submitted, inserted, and updated counts separately
   and state what `executemany()` cannot cheaply distinguish.
   - **Progressive hint:** Do not infer business outcomes from submitted row count.
7. **Extension:** Design the Psycopg COPY variant using typed `write_row()` calls and a staging
   table instead of hand-built delimited text.
   - **Progressive hint:** COPY handles transport; a later set-based statement owns merge
     semantics.
8. **Edge cases:** Test NaN, infinities, zero, negatives, whitespace IDs, leading-zero customer
   IDs, and invalid dates.
   - **Progressive hint:** Classify each rejection at the field boundary and keep its reason
     safe.
9. **Idempotency:** Choose a policy for duplicate `source_id` values within one input batch and
   test it before database submission.
   - **Progressive hint:** Database upsert resolves persisted conflicts but may hide
     contradictory source rows.
10. **Scale design:** Compare materializing all accepted rows with a streaming validator and
   identify where bounded memory changes APIs.
   - **Progressive hint:** A tuple return is convenient for lessons but not for unlimited
     sources.
11. **Capacity:** Select batch size from parameter count, row width, memory, and transaction
   duration rather than a universal constant.
   - **Progressive hint:** Measure the real adapter and keep a safe configurable default.
12. **Transaction failure:** Specify behavior when `executemany()` fails halfway and identify
   which layer owns rollback and retry.
   - **Progressive hint:** Submission count is not committed count.
13. **Observability:** Create a bounded rejection taxonomy and metrics that do not use source
   IDs or raw reasons as tags.
   - **Progressive hint:** Metric labels must come from a fixed vocabulary.
14. **Reconciliation:** Design a replay test that loads the same accepted sales twice and
   reconciles source IDs and total amount.
   - **Progressive hint:** Idempotency is proven by stable final state, not by absence of
     exceptions.

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

## Next step

[Day 7](day07_async_bounded_concurrency.md) introduces async database I/O while
keeping concurrency bounded. Review
[the Day 6 solution notes](../solutions/day06_solutions.md) after your attempt.
