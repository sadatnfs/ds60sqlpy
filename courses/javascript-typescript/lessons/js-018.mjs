// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Aggregate valid rows through a real child process: change one input
// In a scratch copy of Example A, change `{ id: 'A', quantity: 2, priceCents: 125 },` to `{
// id: 'A', quantity: 3, priceCents: 125 },`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at
// `assert.deepEqual(JSON.parse(result.stdout), { rows: 2, totalCents: 550 })`. Restoring `{
// id: 'A', quantity: 2, priceCents: 125 },` brings back: exit 0; stdout is exactly one JSON
// result with 2 rows and 550 cents; stderr empty.

// Exercise 2: Reject unknown arguments before consuming data: diagnose an edited check
// Example B's check was edited to read `assert.equal(result.status, 3);`. Run it, explain
// the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(result.status, 3);`. Restoring `assert.equal(result.status, 2);` brings
// back: exit 2; stdout empty; stderr includes usage.

// Exercise 3: Report the first invalid row without a partial result
// Send a valid first row and malformed JSON on line 2.
// Expected: exit 2; stdout empty; stderr identifies line 2.

// Exercise 4: Reject duplicate business identifiers
// Send two valid rows with the same id.
// Expected: exit 2 with duplicate id diagnostic.

// Exercise 5: Define empty input deliberately
// Send whitespace and empty lines only.
// Expected: exit 0 with rows 0 and totalCents 0.

// Exercise 6: Enforce an input budget before retaining all data
// Send 4097 bytes to a CLI whose cap is 4096.
// Expected: exit 2 with input limit diagnostic; stdout empty.

console.log("Implement the six exercises in your saved copy.");
