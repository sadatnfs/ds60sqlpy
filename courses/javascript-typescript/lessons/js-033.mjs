// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Perform bounded CPU work in a real worker: change one input
// In a scratch copy of Example A, change `10000,` to `10001,`. Which check fails, and what
// value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(result.sum,
// 50005000)`. Restoring `10000,` brings back: sum 50005000; worker thread id positive.

// Exercise 2: Transfer a buffer and observe detachment: debug a regression
// A regression made one Example B line read `const buffer = Uint8Array.from([1, 3,
// 3]).buffer;`. Locate and repair it without editing the check.
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
