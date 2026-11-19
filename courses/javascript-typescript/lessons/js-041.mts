// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Aggregate valid split-byte input: change one input
// Copy Example A into a scratch `main.mts` and change `{ group: 'A', value: 2 },` to `{
// group: 'A', value: 3 },`. Before running it, predict which check fails and which value it
// now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum:
// 4 }]])`. Restoring the original line brings back the worked observation: A count 2 sum 5;
// B count 1 sum 4; zero rejected.

// Exercise 2: Quarantine syntax and domain failures with physical line numbers: debug a regression
// A regression changed one token in Example B, so one line now reads `"value":3`. Run
// Example B with that line, use the failing check to locate the defect and repair it without
// changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 })`; after it the line reads
// `"value":2` again and one accepted row; diagnostics at lines 2 and 3 with json/schema
// categories.

// Exercise 3: Preserve a multi-byte group name across single-byte chunks
// Use an emoji group and split every UTF-8 byte.
// Expected: group name remains intact with sum 7.

// Exercise 4: Handle blank lines and a final line without newline
// Supply blank lines, CRLF and one final valid row.
// Expected: two accepted rows; no fabricated empty records.

// Exercise 5: Enforce input and record budgets
// Reject a line exceeding 1024 bytes and an input exceeding 16384 bytes.
// Expected: RangeError for each resource-limit violation.

// Exercise 6: Expose incomplete-data counts and empty input
// Analyze one invalid row and no valid rows, then analyze an empty stream.
// Expected: zero accepted with one rejected versus zero accepted with zero rejected.

console.log("Implement the six exercises in your saved copy.");
