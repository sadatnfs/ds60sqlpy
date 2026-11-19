// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Retry transient failures with deterministic full jitter: change one input
// Copy Example A into a scratch `main.mjs` and change `let attempts = 0;` to `let attempts =
// 1;`. Before running it, predict which check fails and which value it now sees; then run it
// and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual(waits, [50, 100])`. Restoring the original line brings back the worked
// observation: three attempts; delays 50 and 100; result ready.

// Exercise 2: Stop on permanent failure and on exhausted attempts: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `async () => { transient -=
// 1`. Run Example B with that line, explain why the edited check now fails for the same
// program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(transient, 3)`; after it the line reads `async () => { transient += 1` again
// and permanent attempted once; transient attempted three times and still rejects.

// Exercise 3: Reuse a completed idempotent result
// Submit the same key and payload twice to the local store.
// Expected: one side effect; identical returned receipt.

// Exercise 4: Reject conflicting reuse of an idempotency key
// Reuse one key for amounts 5 and 7.
// Expected: conflict error; effects remains 1.

// Exercise 5: Bound active work while preserving input order
// Map four values with concurrency 2 and observe active-operation counts.
// Expected: results 2,4,6,8; peak active at most 2; active returns to 0.

// Exercise 6: Honor cancellation before the first attempt
// Abort a signal before calling retry and track attempted work.
// Expected: original reason rejects; attempts remain 0.

console.log("Implement the six exercises in your saved copy.");
