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

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day06_solution.py`; use it only after an honest attempt.

**Shared failure rule:** Bulk speed does not excuse weak validation, unbounded materialization, or diagnostics that copy entire rejected records.

### Exercise 1 — Validation

**Prompt:** Implement `parse_sale()` for non-blank source ID, positive integer customer ID,
finite positive amount, and ISO date without mutating input.

**Approach:** Read values into locals, validate every invariant, parse with `Decimal` and
`date.fromisoformat`, and return a new frozen `Sale`. Raise `RowValidationError` with a safe
field-level reason.

**Why this boundary matters:** Convert each field explicitly and translate only expected
conversion failures.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Money

**Prompt:** Quantize accepted amounts to two decimals and document the chosen rounding rule.

**Approach:** Use `Decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)` as the reference
teaching policy and test boundary values. Another policy is valid only when explicitly required
and tested.

**Why this boundary matters:** Quantization is a domain decision, not merely display formatting.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Partitioning

**Prompt:** Implement `partition_rows()` so accepted sales and rejected source IDs/reasons
retain input order without storing full raw rows.

**Approach:** Iterate once, append parsed sales on success, and append
`RejectedRow(safe_source_id, reason)` on expected validation failure. Do not include the
original mapping or unrelated exceptions.

**Why this boundary matters:** Catch only `RowValidationError` from the conversion boundary.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Batching

**Prompt:** Implement `batches()` with positive-size validation and tests for empty, exact, and
remainder cases.

**Approach:** Raise for `size < 1`; step over indexes by `size`; convert each non-empty slice to
a tuple. Empty input returns an empty list and input order is unchanged.

**Why this boundary matters:** Slice deterministic tuples from the original sequence.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Bulk SQL

**Prompt:** Implement a parameterized `executemany()` upsert into `pg_temp.bridge_sales` with no
values in SQL text.

**Approach:** Use a static `INSERT ... VALUES (%s, ...) ON CONFLICT (source_id) DO UPDATE` and
pass an iterable of `(source_id, customer_id, amount, occurred_on)` tuples to `executemany`.

**Why this boundary matters:** Convert typed sales to one parameter tuple per row.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Accounting

**Prompt:** Track accepted, rejected, submitted, inserted, and updated counts separately and
state what `executemany()` cannot cheaply distinguish.

**Approach:** Validation provides accepted/rejected/submitted counts. Ordinary `executemany`
does not cheaply classify each upsert as insert versus update; use staging plus set-based
comparison/`RETURNING` if that distinction is required.

**Why this boundary matters:** Do not infer business outcomes from submitted row count.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Extension

**Prompt:** Design the Psycopg COPY variant using typed `write_row()` calls and a staging table
instead of hand-built delimited text.

**Approach:** Open a COPY context for typed columns, call `write_row` per validated `Sale`, then
merge staging rows into the target in the same transaction. Never concatenate
tab/newline-delimited source strings.

**Why this boundary matters:** COPY handles transport; a later set-based statement owns merge
semantics.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Edge cases

**Prompt:** Test NaN, infinities, zero, negatives, whitespace IDs, leading-zero customer IDs,
and invalid dates.

**Approach:** Reject non-finite or non-positive Decimal values and blank IDs; define whether
`'007'` is a valid integer representation; reject invalid calendar dates. None of the full raw
inputs should appear in reasons.

**Why this boundary matters:** Classify each rejection at the field boundary and keep its reason
safe.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — Idempotency

**Prompt:** Choose a policy for duplicate `source_id` values within one input batch and test it
before database submission.

**Approach:** The safer teaching policy rejects duplicate source IDs during planning, because
last-write-wins would depend on input order. Track seen IDs and reject before opening the
transaction.

**Why this boundary matters:** Database upsert resolves persisted conflicts but may hide
contradictory source rows.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Scale design

**Prompt:** Compare materializing all accepted rows with a streaming validator and identify
where bounded memory changes APIs.

**Approach:** For large inputs, yield accepted/rejected events or bounded batches from an
iterator and aggregate counters incrementally. Preserve source order and avoid keeping raw rows
after validation.

**Why this boundary matters:** A tuple return is convenient for lessons but not for unlimited
sources.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 11 — Capacity

**Prompt:** Select batch size from parameter count, row width, memory, and transaction duration
rather than a universal constant.

**Approach:** Bound rows so parameters and memory remain reasonable, then benchmark
throughput/latency. Validate a positive configured size and expose submitted batch counts for
tuning.

**Why this boundary matters:** Measure the real adapter and keep a safe configurable default.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 12 — Transaction failure

**Prompt:** Specify behavior when `executemany()` fails halfway and identify which layer owns
rollback and retry.

**Approach:** Let the caller's transaction boundary roll back the entire batch and classify the
exception there. Retry the same stable source IDs in a fresh transaction; never report partial
rows as committed without database evidence.

**Why this boundary matters:** Submission count is not committed count.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 13 — Observability

**Prompt:** Create a bounded rejection taxonomy and metrics that do not use source IDs or raw
reasons as tags.

**Approach:** Map failures to codes such as `missing_source_id`, `invalid_customer_id`,
`invalid_amount`, and `invalid_date`; count by code while retaining minimal per-row diagnostics
in a protected bounded sink.

**Why this boundary matters:** Metric labels must come from a fixed vocabulary.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 14 — Reconciliation

**Prompt:** Design a replay test that loads the same accepted sales twice and reconciles source
IDs and total amount.

**Approach:** After two upserts, query one row per source ID and compare exact counts/sums with
the deduplicated accepted plan. The second run may update but must not duplicate logical rows.

**Why this boundary matters:** Idempotency is proven by stable final state, not by absence of
exceptions.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
