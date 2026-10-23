// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Complete one valid job lifecycle
// Start a queued job and complete it with value 7.
// Expected: succeeded with attempt 1 and value 7.

// Exercise 2: Reject a result arriving before start
// Send complete directly to queued.
// Expected: invalid transition error; original remains queued.

// Exercise 3: Enforce the retry budget
// Fail three started attempts and try to retry once more.
// Expected: attempt 3 remains failed; further retry rejects.

// Exercise 4: Keep cancellation terminal
// Cancel a running job, then deliver a late completion.
// Expected: cancelled state remains; late completion rejects.

// Exercise 5: Replay deterministically from the same history
// Replay start, failure, retry, start and completion twice.
// Expected: both runs produce the same succeeded attempt-2 state.

// Exercise 6: Preserve input state and validate success values
// Compare input before and after a transition, then reject NaN as a result.
// Expected: input unchanged; new object returned; NaN rejects.

console.log("Implement the six exercises in your saved copy.");
