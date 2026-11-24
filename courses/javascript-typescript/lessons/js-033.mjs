// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Perform bounded CPU work in a real worker: change one input
// Copy Example A into a scratch `main.mjs` and change `10000,` to `10001,`. Before running
// it, predict which check fails and which value it now sees; then run it and restore the
// original line.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(result.sum,
// 50005000)`. Restoring `10000,` brings back: sum 50005000; worker thread id positive.

// Exercise 2: Transfer a buffer and observe detachment: debug a regression
// A regression changed one token in Example B, so one line now reads `const buffer =
// Uint8Array.from([1, 3, 3]).buffer;`. Run Example B with that line, use the failing check
// to locate the defect and repair it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.deepEqual(result, [9, 2, 3])`. Restoring `const buffer = Uint8Array.from([1, 2,
// 3]).buffer;` brings back: parent byteLength 0; returned bytes 9,2,3.

// Exercise 3: Distinguish cloning from shared mutation
// Send an object, mutate the worker copy and compare the original.
// Expected: worker returns 9; parent remains 1.

// Exercise 4: Propagate an actual worker exception
// Run an authored worker that throws a fixture error.
// Expected: parent Promise rejects with worker fixture failed.

// Exercise 5: Terminate an owned worker that remains alive
// Start a worker that reports ready and keeps an interval open, then terminate it.
// Expected: ready observed; terminate resolves with an exit code.

// Exercise 6: Reject data that cannot be cloned
// Try to pass a function through workerData.
// Expected: DataCloneError before useful worker execution.

console.log("Implement the six exercises in your saved copy.");
