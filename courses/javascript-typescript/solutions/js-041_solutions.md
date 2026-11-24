# js-041: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

An analytics pipeline combines framing, parsing, validation and aggregation. Each layer has a different failure mode. Bytes can split UTF-8 characters, chunks can split lines, JSON can be malformed, and syntax-valid rows can violate a domain schema. Treating every line as a trusted typed record skips several independent boundaries. A useful diagnostic identifies the physical line and category without copying sensitive raw data into logs.

This fixture accepts newline-delimited JSON rows containing a group and a bounded integer value. A StringDecoder retains incomplete UTF-8 sequences across byte chunks. A line buffer retains incomplete records. The parser validates exact fields and returns a typed record or a compact diagnostic. Aggregation stores a count and sum per group. Invalid rows are quarantined as diagnostics; their values do not contribute to accepted totals.

The quarantine policy is a deliberate choice. A financial reconciliation or release gate might instead reject the entire input on any invalid row. This example returns accepted and rejected counts so a partial aggregate cannot be confused with a complete clean dataset. It does not infer that rejected data is statistically ignorable: missingness can bias the aggregate, so the downstream interpretation must consider why rows failed.

Streaming does not automatically mean bounded memory. The fixture caps total input bytes, line bytes and record lengths, and its tiny group set is controlled by the authored input. A production pipeline with unbounded unique groups needs a cardinality limit, spill strategy or external aggregation. The code demonstrates actual incremental decoding and validation, not a claim of constant memory for arbitrary datasets.

**Framing:** Separating a byte/text stream into logical records.

**Quarantine:** Retaining failure diagnostics while excluding invalid rows from accepted aggregates.

**Aggregation state:** The per-group statistics retained while scanning records.

**Resource budget:** An explicit bound on input, records or retained state.

## Reading the implementation

The byte source is an AsyncIterable<Uint8Array>. StringDecoder.write handles split characters, while end flushes remaining decoder state. A pending text buffer is split at newline characters and strips an optional preceding carriage return. Each physical line receives a one-based number. JSON.parse returns unknown at the boundary, and the validator checks its shape before constructing a fresh Row. Map aggregation updates only accepted rows and returns a separate diagnostics list.

## Exercise 1: Aggregate valid split-byte input: change one input

Task: Copy Example A into a scratch `main.mts` and change `{ group: 'A', value: 2 },` to `{ group: 'A', value: 3 },`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

Chunk boundaries are independent of JSON record boundaries. The pipeline carries partial decoder and line state instead of parsing each chunk as a complete row.

The unchanged code is the exercise block of Example A:

```typescript
const text = [
  { group: 'A', value: 2 },
  { group: 'B', value: 4 },
  { group: 'A', value: 3 },
]
  .map((row) => JSON.stringify(row))
  .join('\n');
const result = await analyze(chunks(text, 3));
assert.deepEqual(
  [...result.groups],
  [
    ['A', { count: 2, sum: 5 }],
    ['B', { count: 1, sum: 4 }],
  ],
);
assert.equal(result.accepted, 3);
assert.deepEqual(result.rejected, []);
```

**Expected:** The changed run fails with an `AssertionError` at `assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum: 4 }]])`. Restoring `{ group: 'A', value: 2 },` brings back: A count 2 sum 5; B count 1 sum 4; zero rejected.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum: 4 }]])` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Quarantine syntax and domain failures with physical line numbers: debug a regression

Task: A regression changed one token in Example B, so one line now reads `"value":3`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

Rejected values never enter the aggregate. The diagnostic identifies where and why the row failed without reproducing the entire source payload.

The unchanged code is the exercise block of Example B:

```typescript
const text = '{"group":"A","value":2}\n{broken\n{"group":"A","value":"wrong"}\n';
const result = await analyze(chunks(text, 2));
assert.equal(result.accepted, 1);
assert.deepEqual(result.rejected, [
  { line: 2, code: 'json' },
  { line: 3, code: 'schema' },
]);
assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 });
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 })`. Restoring `"value":2` brings back: one accepted row; diagnostics at lines 2 and 3 with json/schema categories.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 })` for this input.

## Exercise 3: Preserve a multi-byte group name across single-byte chunks

Task: Use an emoji group and split every UTF-8 byte.

A raw chunk.toString call per byte would introduce replacement characters. The decoder retains incomplete sequences until enough bytes arrive.

```typescript
const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));
assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 });
assert.equal(result.rejected.length, 0);
```

**Expected:** group name remains intact with sum 7.

**Verify:** Keep a check equivalent to `assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 })`. As a control, change `const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));` to `const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 8 }), 1));`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Handle blank lines and a final line without newline

Task: Supply blank lines, CRLF and one final valid row.

Blank lines are ignored under this declared format policy, while physical line numbering still advances. The final buffered record is processed even without a trailing newline.

```typescript
const text = '\n{"group":"A","value":1}\r\n\n{"group":"A","value":2}';
const result = await analyze(chunks(text, 4));
assert.equal(result.accepted, 2);
assert.deepEqual(result.groups.get('A'), { count: 2, sum: 3 });
assert.deepEqual(result.rejected, []);
```

**Expected:** two accepted rows; no fabricated empty records.

**Verify:** Keep a check equivalent to `assert.deepEqual(result.groups.get('A'), { count: 2, sum: 3 })`. As a control, change `"value":1` to `"value":2`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Enforce input and record budgets

Task: Reject a line exceeding 1024 bytes and an input exceeding 16384 bytes.

A budget violation aborts the stream rather than becoming a harmless row diagnostic. Continuing could retain or process more data than the application agreed to accept.

```typescript
await assert.rejects(analyze(chunks('x'.repeat(1025), 10)), RangeError);
await assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError);
```

**Expected:** RangeError for each resource-limit violation.

**Verify:** Keep a check equivalent to `assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## Exercise 6: Expose incomplete-data counts and empty input

Task: Analyze one invalid row and no valid rows, then analyze an empty stream.

An empty aggregate can arise from no data or from entirely rejected data. Reporting accepted and rejected counts preserves that crucial interpretation difference.

```typescript
const invalid = await analyze(chunks('{"group":"A","value":null}', 5));
const empty = await analyze(chunks('', 5));
assert.equal(invalid.accepted, 0);
assert.equal(invalid.rejected.length, 1);
assert.equal(empty.accepted, 0);
assert.equal(empty.rejected.length, 0);
assert.equal(empty.groups.size, 0);
```

**Expected:** zero accepted with one rejected versus zero accepted with zero rejected.

**Verify:** Keep a check equivalent to `assert.equal(empty.groups.size, 0)`. As a control, change `assert.equal(empty.groups.size, 0);` to `assert.equal(empty.groups.size, 1);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
