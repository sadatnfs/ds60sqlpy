// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Cancel a pending timer
// Start a timer with a signal, abort it, and inspect the rejection.
// Expected: AbortError with the original reason as cause.

// Exercise 2: Reject an already aborted request before work
// Abort before calling the custom operation.
// Expected: the exact reason is rejected; no timer starts.

// Exercise 3: Complete normally and clean up once
// Run the custom operation without aborting, then abort its signal after completion.
// Expected: value 7; started,completed,cleaned exactly once.

// Exercise 4: Cancel custom work and release its timer
// Start the custom operation and immediately abort.
// Expected: rejected reason; started,aborted,cleaned.

// Exercise 5: Keep the first abort reason
// Abort a controller twice and call throwIfAborted.
// Expected: the first reason remains authoritative.

// Exercise 6: Combine caller and deadline signals
// Combine two controllers and abort the deadline controller.
// Expected: combined signal is aborted with deadline reason.

console.log("Implement the six exercises in your saved copy.");
