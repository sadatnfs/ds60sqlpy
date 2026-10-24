// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Retry transient failures with deterministic full jitter
// Fail twice transiently, then succeed, using random value 0.5 and a recording wait.
// Expected: three attempts; delays 50 and 100; result ready.

// Exercise 2: Stop on permanent failure and on exhausted attempts
// Use one permanent failure, then an always-transient operation with a three-attempt budget.
// Expected: permanent attempted once; transient attempted three times and still rejects.

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
