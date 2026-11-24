// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Cancel a pending timer: predict an edited check
// Copy Example A into a scratch `main.mjs` and change `await assert.rejects(pending, error
// => error.name === 'AbortError' && error.cause === reason);` to `await
// assert.rejects(pending, error => error.name === 'AbortError!' && error.cause === reason);`
// inside its check. Before running it, predict whether the check still passes and explain
// why; then restore it.
// Expected: The changed run fails with an `AssertionError` at `await assert.rejects(pending,
// error => error.name === 'AbortError!' && error.cause === reason);`. Restoring `await
// assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);`
// brings back: abortError with the original reason as cause.

// Exercise 2: Reject an already aborted request before work: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `await
// assert.rejects(cancellableValue(7, controller.signal, trace), error => error !==
// reason);`. Run Example B with that line, explain why the edited check now fails for the
// same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at `await
// assert.rejects(cancellableValue(7, controller.signal, trace), error => error !==
// reason);`. Restoring `await assert.rejects(cancellableValue(7, controller.signal, trace),
// error => error === reason);` brings back: the exact reason is rejected; no timer starts.

// Exercise 3: Complete normally and clean up once
// Run the custom operation without aborting, then abort its signal after completion.
// Expected: value 7; trace `started`, `completed`, `cleaned`, with cleanup exactly once.

// Exercise 4: Cancel custom work and release its timer
// Start the custom operation and immediately abort.
// Expected: rejected reason; trace `started`, `aborted`, `cleaned`.

// Exercise 5: Keep the first abort reason
// Abort a controller twice and call throwIfAborted.
// Expected: the first reason remains authoritative.

// Exercise 6: Combine caller and deadline signals
// Combine a caller signal with a disposable one-second deadline, abort the caller first,
// then leave the block that owns the deadline.
// Expected: combined signal carries the caller reason; the deadline stays unaborted and its
// timer is cleared once when the block ends.

console.log("Implement the six exercises in your saved copy.");
