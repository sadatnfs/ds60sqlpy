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


<!-- BEGIN BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->
## Small executable check

Validation and batching can be verified entirely offline:

```python
from decimal import Decimal

from bridge.solutions.day06_solution import batches, parse_sale

sale = parse_sale(
    {
        "source_id": "sale-1",
        "customer_id": "7",
        "amount": "12.30",
        "occurred_on": "2026-07-30",
    }
)
assert sale.amount == Decimal("12.30")
assert batches([1, 2, 3], 2) == [(1, 2), (3,)]
```
<!-- END BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->

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

**Verification evidence:** Parse one valid mapping and compare exact typed fields; assert blank source ID, non-positive/non-integer customer ID, non-finite/non-positive amount, and bad ISO date raise `RowValidationError`, and the input mapping is unchanged.

### Exercise 2 — Money

**Prompt:** Quantize accepted amounts to two decimals and document the chosen rounding rule.

**Approach:** Use `Decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)` as the reference
teaching policy and test boundary values. Another policy is valid only when explicitly required
and tested.

**Why this boundary matters:** Quantization is a domain decision, not merely display formatting.

**Verification evidence:** Check amounts with more than two places and a halfway value; assert the exact two-place `Decimal` results under the documented rounding mode, not merely formatted strings.

### Exercise 3 — Partitioning

**Prompt:** Implement `partition_rows()` so accepted sales and rejected source IDs/reasons
retain input order without storing full raw rows.

**Approach:** Iterate once, append parsed sales on success, and append
`RejectedRow(safe_source_id, reason)` on expected validation failure. Do not include the
original mapping or unrelated exceptions.

**Why this boundary matters:** Catch only `RowValidationError` from the conversion boundary.

**Verification evidence:** Feed valid-invalid-valid rows; assert accepted sales and rejection `(source_id, reason)` records preserve input order and no rejected object stores the complete raw mapping.

### Exercise 4 — Batching

**Prompt:** Implement `batches()` with positive-size validation and tests for empty, exact, and
remainder cases.

**Approach:** Raise for `size < 1`; step over indexes by `size`; convert each non-empty slice to
a tuple. Empty input returns an empty list and input order is unchanged.

**Why this boundary matters:** Slice deterministic tuples from the original sequence.

**Verification evidence:** Assert `batches([], 2) == []`, exact division has no empty tail, a remainder becomes the last tuple, and sizes `0`/negative raise `ValueError`.

### Exercise 5 — Bulk SQL

**Prompt:** Implement a parameterized `executemany()` upsert into `pg_temp.bridge_sales` with no
values in SQL text.

**Approach:** Use a static `INSERT ... VALUES (%s, ...) ON CONFLICT (source_id) DO UPDATE` and
pass an iterable of `(source_id, customer_id, amount, occurred_on)` tuples to `executemany`.

**Why this boundary matters:** Convert typed sales to one parameter tuple per row.

**Verification evidence:** Inspect one `executemany` call: SQL contains placeholders and the upsert clause, every sale value exists only in parameter rows, and empty input makes no driver call.

### Exercise 6 — Accounting

**Prompt:** Track accepted, rejected, submitted, inserted, and updated counts separately and
state what `executemany()` cannot cheaply distinguish.

**Approach:** Validation provides accepted/rejected/submitted counts. Ordinary `executemany`
does not cheaply classify each upsert as insert versus update; use staging plus set-based
comparison/`RETURNING` if that distinction is required.

**Why this boundary matters:** Do not infer business outcomes from submitted row count.

**Verification evidence:** For a mixed fixture, report separate accepted, rejected, and submitted counts; label inserted/updated as unknown unless returned/reconciled database evidence distinguishes them.

### Exercise 7 — Extension

**Prompt:** Design the Psycopg COPY variant using typed `write_row()` calls and a staging table
instead of hand-built delimited text.

**Approach:** Open a COPY context for typed columns, call `write_row` per validated `Sale`, then
merge staging rows into the target in the same transaction. Never concatenate
tab/newline-delimited source strings.

**Why this boundary matters:** COPY handles transport; a later set-based statement owns merge
semantics.

**Verification evidence:** Provide a COPY design that calls typed `write_row` into a staging table, validates staging rows, and performs one set-based merge without constructing delimited text.

### Exercise 8 — Edge cases

**Prompt:** Test NaN, infinities, zero, negatives, whitespace IDs, leading-zero customer IDs,
and invalid dates.

**Approach:** Reject non-finite or non-positive Decimal values and blank IDs; define whether
`'007'` is a valid integer representation; reject invalid calendar dates. None of the full raw
inputs should appear in reasons.

**Why this boundary matters:** Classify each rejection at the field boundary and keep its reason
safe.

**Verification evidence:** Parameterize `NaN`, both infinities, zero, negative amount, blank ID, leading-zero customer ID, and invalid dates; compare exact acceptance or `RowValidationError` outcome.

### Exercise 9 — Idempotency

**Prompt:** Choose a policy for duplicate `source_id` values within one input batch and test it
before database submission.

**Approach:** The safer teaching policy rejects duplicate source IDs during planning, because
last-write-wins would depend on input order. Track seen IDs and reject before opening the
transaction.

**Why this boundary matters:** Database upsert resolves persisted conflicts but may hide
contradictory source rows.

**Verification evidence:** Choose reject-first, reject-all, or deterministic-last-wins for duplicate `source_id`; assert the chosen result is decided before `executemany` and documented in counts.

### Exercise 10 — Scale design

**Prompt:** Compare materializing all accepted rows with a streaming validator and identify
where bounded memory changes APIs.

**Approach:** For large inputs, yield accepted/rejected events or bounded batches from an
iterator and aggregate counters incrementally. Preserve source order and avoid keeping raw rows
after validation.

**Why this boundary matters:** A tuple return is convenient for lessons but not for unlimited
sources.

**Verification evidence:** Compare peak retained rows for materialized and streaming designs; the streaming API must emit bounded batches/rejections without requiring the entire input sequence.

### Exercise 11 — Capacity

**Prompt:** Select batch size from parameter count, row width, memory, and transaction duration
rather than a universal constant.

**Approach:** Bound rows so parameters and memory remain reasonable, then benchmark
throughput/latency. Validate a positive configured size and expose submitted batch counts for
tuning.

**Why this boundary matters:** Measure the real adapter and keep a safe configurable default.

**Verification evidence:** Show a batch-size calculation using parameter count, row width, memory budget, and transaction-duration target; assert the selected size stays below every stated limit.

### Exercise 12 — Transaction failure

**Prompt:** Specify behavior when `executemany()` fails halfway and identify which layer owns
rollback and retry.

**Approach:** Let the caller's transaction boundary roll back the entire batch and classify the
exception there. Retry the same stable source IDs in a fresh transaction; never report partial
rows as committed without database evidence.

**Why this boundary matters:** Submission count is not committed count.

**Verification evidence:** Inject a mid-load driver failure; assert the transaction owner rolls back the complete unit, the loader does not claim partial success, and retry starts from a defined boundary.

### Exercise 13 — Observability

**Prompt:** Create a bounded rejection taxonomy and metrics that do not use source IDs or raw
reasons as tags.

**Approach:** Map failures to codes such as `missing_source_id`, `invalid_customer_id`,
`invalid_amount`, and `invalid_date`; count by code while retaining minimal per-row diagnostics
in a protected bounded sink.

**Why this boundary matters:** Metric labels must come from a fixed vocabulary.

**Verification evidence:** Inspect metrics for a fixed rejection-reason enum and bounded outcome tags; assert no source ID, raw reason text, or complete rejected row appears as a tag.

### Exercise 14 — Reconciliation

**Prompt:** Design a replay test that loads the same accepted sales twice and reconciles source
IDs and total amount.

**Approach:** After two upserts, query one row per source ID and compare exact counts/sums with
the deduplicated accepted plan. The second run may update but must not duplicate logical rows.

**Why this boundary matters:** Idempotency is proven by stable final state, not by absence of
exceptions.

**Verification evidence:** Load the accepted fixture twice under the declared upsert policy; reconcile the same source-ID set and exact total amount after both runs with no duplicate logical sale.
