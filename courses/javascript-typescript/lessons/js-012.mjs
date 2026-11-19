// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Trace executor and reaction ordering: change one input
// Copy Example A into a scratch `main.mjs` and change `const observed = pending.then(value
// => { trace.push('reaction'); return value; });` to `const observed = pending.then(value =>
// { trace.push('reaction!'); return value; });`. Before running it, predict which check
// fails and which value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual(trace, ['executor', 'sync', 'reaction'])`. Restoring the original line
// brings back the worked observation: executor, sync, reaction.

// Exercise 2: Compose values and rejection recovery: debug a regression
// A regression changed one token in Example B, so one line now reads `.then(value => value +
// 2)`. Run Example B with that line, use the failing check to locate the defect and repair
// it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(result, 'bad value 8')`; after it the line reads `.then(value => value * 2)`
// again and recovered message is bad value 8.

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
