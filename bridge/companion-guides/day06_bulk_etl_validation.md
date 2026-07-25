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

1. Implement `parse_sale()` for `source_id`, positive integer `customer_id`,
   finite positive `amount`, and ISO `occurred_on`. Do not mutate the input.
2. Quantize money to two decimal places and document the rounding rule your
   domain expects.
3. Implement `partition_rows()`. Retain accepted `Sale` objects and rejected
   source IDs with safe reasons. Do not place the entire raw mapping in errors.
4. Implement `batches()`. Reject sizes below one and test empty, exact, and
   remainder cases.
5. Implement a parameterized `executemany()` upsert into
   `pg_temp.bridge_sales`. Keep values out of SQL text.
6. Record accepted, rejected, submitted, inserted, and updated counts
   separately; explain which counts `executemany()` can and cannot provide
   cheaply.
7. Stretch: implement the same adapter with Psycopg `cursor.copy()`. Feed typed
   rows through `write_row()` rather than hand-building tab-separated text.

### Progressive hints

1. Catch only the conversion errors you can turn into a useful row-level
   rejection.
2. `date.fromisoformat()` handles the required date shape.
3. A stable `source_id` supports an upsert and restart.
4. Validate everything before opening a transaction when practical.
5. COPY is fastest for many rows, but merge/upsert commonly needs a staging
   table followed by set-based SQL.

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
