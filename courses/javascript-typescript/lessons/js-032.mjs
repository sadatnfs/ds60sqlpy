// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Run an actual transform pipeline: change one input
// In a scratch copy of Example A, change `await pipeline(Readable.from(['ab', 'cd']), upper,
// sink);` to `await pipeline(Readable.from(['ab!', 'cd']), upper, sink);`. Which check
// fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(output.join(''),
// 'ABCD')`. Restoring `await pipeline(Readable.from(['ab', 'cd']), upper, sink);` brings
// back: ABCD after successful pipeline completion.

// Exercise 2: Observe false write and drain without guessing timing: debug a regression
// A regression made one Example B line read `highWaterMark: 3,`. Locate and repair it
// without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(sink.write(Buffer.from('ab')), false)`. Restoring `highWaterMark: 2,` brings
// back: write returns false; drain follows release; stream finishes.

// Exercise 3: Propagate a producer failure and destroy the sink
// Use an async source that yields once then throws.
// Expected: pipeline rejects with source failed; sink is destroyed.

// Exercise 4: Reject an invalid object in a transform
// Process numeric objects but reject a negative value through the callback.
// Expected: pipeline rejects with RangeError.

// Exercise 5: Measure an object-mode threshold in objects
// Write one large-payload object to a writable with object-mode highWaterMark 1.
// Expected: write false and writableLength 1, irrespective of payload string length.

// Exercise 6: Abort a generator and its awaited timer
// Start a source, await its readiness signal, then abort the shared signal.
// Expected: pipeline rejects with AbortError; generator finally runs.

console.log("Implement the six exercises in your saved copy.");
