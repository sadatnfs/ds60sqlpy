// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Await and narrow a result: predict an edited check
// In a scratch copy of Example A, change `assert.deepEqual(await lookup('missing'), { ok:
// false, error: 'not_found' });` to `assert.deepEqual(await lookup('missing'), { ok: true,
// error: 'not_found' });` inside its check. Does the check still pass?
// Expected: The edited run fails with an `AssertionError` at `assert.deepEqual(await
// lookup('missing'), { ok: true, error: 'not_found' });`. Restoring `assert.deepEqual(await
// lookup('missing'), { ok: false, error: 'not_found' });` brings back: known value 7; absent
// error not_found.

// Exercise 2: Show a failure result does not invoke catch: debug a regression
// A regression made one Example B line read `let caught = 1;`. Locate and repair it without
// editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(caught, 0)`. Restoring `let caught = 0;` brings back: catch count 0; result
// still not_found.

// Exercise 3: Translate recognized cancellation
// Abort a real timer-backed operation.
// Expected: failure result cancelled.

// Exercise 4: Inspect an unknown rejection reason
// Reject with a string and normalize it at a reporting boundary.
// Expected: diagnostic unclassified failure.

// Exercise 5: Preserve every batch outcome
// Summarize one fulfilled value and one rejected task.
// Expected: `value:2` and `error:offline`.

// Exercise 6: Reject unresolved and unnarrowed access
// Demonstrate both errors in an uncalled compile-time check.
// Expected: expected diagnostics for value before await or before narrowing.

console.log("Implement the six exercises in your saved copy.");
