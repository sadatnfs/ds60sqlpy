// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Complete one valid job lifecycle: change one input
// In a scratch copy of Example A, change `const completed = transition(started, { type:
// 'complete', value: 7 });` to `const completed = transition(started, { type: 'complete',
// value: 8 });`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.deepEqual(completed, {
// id: 'A', attempt: 1, kind: 'succeeded', value: 7 })`. Restoring `const completed =
// transition(started, { type: 'complete', value: 7 });` brings back: succeeded with attempt
// 1 and value 7.

// Exercise 2: Reject a result arriving before start: diagnose an edited check
// Example B's check was edited to read `assert.deepEqual(queued, { id: 'A', attempt: 1,
// kind: 'queued' });`. Run it, explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.deepEqual(queued, { id: 'A', attempt: 1, kind: 'queued' });`. Restoring
// `assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });` brings back: invalid
// transition error; original remains queued.

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
