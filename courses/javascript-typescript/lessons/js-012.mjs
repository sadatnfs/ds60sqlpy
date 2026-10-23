// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace executor and reaction ordering
// Record executor, synchronous continuation and then reaction.
// Expected: executor, sync, reaction.

// Exercise 2: Compose values and rejection recovery
// Double a value, throw an error, then recover through catch.
// Expected: recovered message is bad value 8.

// Exercise 3: Preserve input order in Promise.all
// Resolve the second deferred Promise first, then the first.
// Expected: result remains first,second.

// Exercise 4: Inspect every outcome with allSettled
// Combine fulfillment 2 with rejection offline.
// Expected: statuses fulfilled/rejected with their original value and reason.

// Exercise 5: Demonstrate that race does not cancel losers
// Race an already fulfilled result against a deferred operation, then settle the deferred
// operation.
// Expected: winner fast; deferred operation still completes later.

// Exercise 6: Observe FIFO microtasks before an awaited timer
// Queue one Promise reaction and one queueMicrotask callback, then await a timer.
// Expected: sync,promise,microtask,timer.

console.log("Implement the six exercises in your saved copy.");
