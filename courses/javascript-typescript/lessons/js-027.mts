// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Await and narrow a result
// Look up a known id and an absent id.
// Expected: known value 7; absent error not_found.

// Exercise 2: Show a failure result does not invoke catch
// Attach catch to a lookup returning a not_found value.
// Expected: catch count 0; result still not_found.

// Exercise 3: Translate recognized cancellation
// Abort a real timer-backed operation.
// Expected: failure result cancelled.

// Exercise 4: Inspect an unknown rejection reason
// Reject with a string and normalize it at a reporting boundary.
// Expected: diagnostic unclassified failure.

// Exercise 5: Preserve every batch outcome
// Summarize one fulfilled value and one rejected task.
// Expected: value:2 and error:offline.

// Exercise 6: Reject unresolved and unnarrowed access
// Demonstrate both errors in an uncalled compile-time check.
// Expected: expected diagnostics for value before await or before narrowing.

console.log("Implement the six exercises in your saved copy.");
