# Bridge Day 6 — Solution notes

Work through the [learner file](../lessons/day06_bulk_etl_validation.py) before
opening [day06_solution.py](day06_solution.py).

## Validation pipeline

`parse_sale()` validates one raw mapping and produces an immutable `Sale`.
Money stays as `Decimal`, non-finite or non-positive values fail, and ISO dates
become `date` objects. The two-decimal quantization is an explicit course
policy, not an accidental database conversion.

`plan_load()` catches only `RowValidationError`. Programmer errors and
infrastructure failures still fail the run. Rejections retain source ID and a
safe reason, not the entire external row.

`batches()` returns deterministic tuples and rejects invalid sizes.
`load_sales()` sends a list of parameter tuples to `executemany()` and targets a
temporary PostgreSQL table for the optional live exercise.

## Tradeoffs

- The reference quantization uses the active decimal rounding context. A
  financial domain should name its rounding mode explicitly and test half-way
  values.
- Collecting all accepted rows is easy to understand but uses memory
  proportional to input. A large pipeline can validate an iterator and flush
  bounded batches.
- `executemany()` is convenient and preserves parameter safety. Psycopg COPY is
  usually faster for large loads but upsert commonly needs a temporary staging
  table plus set-based merge.
- The return value is submitted row count, not inserted row count. Conflicts can
  update existing rows; observability should not label these as inserts.
- Upserting makes restarts converge on a stable state, but overwriting an
  existing amount may be wrong for append-only audit data. Choose semantics
  from the source contract.

Test empty input, invalid batch sizes, invalid numeric forms, `NaN`, dates,
rounding boundaries, remainders, and exact parameter rows.

