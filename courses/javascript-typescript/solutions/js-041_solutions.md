# js-041: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

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

Task: In a scratch copy of Example A, change `{ group: 'A', value: 2 },` to `{ group: 'A', value: 3 },`. Which check fails, and what value does it see?

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

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum: 4 }]])`. Restoring `{ group: 'A', value: 2 },` brings back: A count 2 sum 5; B count 1 sum 4; zero rejected.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `{ group: 'A', value: 2 },`.

## Exercise 2: Quarantine syntax and domain failures with physical line numbers: debug a regression

Task: A regression made one Example B line read `"value":3`. Locate and repair it without editing the check.

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

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Preserve a multi-byte group name across single-byte chunks

Task: Use an emoji group and split every UTF-8 byte.

A raw chunk.toString call per byte would introduce replacement characters. The decoder retains incomplete sequences until enough bytes arrive.

```typescript
const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));
assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 });
assert.equal(result.rejected.length, 0);
```

**Expected:** group name remains intact with sum 7.

**Verify:** Keep `assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 })`. Control: changing `const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));` to `const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 8 }), 1));` must make that check fail; then restore it.

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

**Verify:** Keep `assert.deepEqual(result.groups.get('A'), { count: 2, sum: 3 })`. Control: changing `"value":1` to `"value":2` must make that check fail; then restore it.

## Exercise 5: Enforce input and record budgets

Task: Reject a line exceeding 1024 bytes and an input exceeding 16384 bytes.

A budget violation aborts the stream rather than becoming a harmless row diagnostic. Continuing could retain or process more data than the application agreed to accept.

```typescript
await assert.rejects(analyze(chunks('x'.repeat(1025), 10)), RangeError);
await assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError);
```

**Expected:** RangeError for each resource-limit violation.

**Verify:** Keep the check `assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError)`; name an input that would make it fail and the value that changes.

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

**Verify:** Keep `assert.equal(empty.groups.size, 0)`. Control: editing it to `assert.equal(empty.groups.size, 1);` must make the check fail; then restore it.

## After comparison

Fresh case: add a per-group minimum and maximum. Predict the output for one group with values 3, -1 and 8, a second group with a single row, and an input in which every row is rejected. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
