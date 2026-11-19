// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Complete one valid job lifecycle: change one input
// Copy Example A into a scratch `main.mts` and change `const completed = transition(started,
// { type: 'complete', value: 7 });` to `const completed = transition(started, { type:
// 'complete', value: 8 });`. Before running it, predict which check fails and which value it
// now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.deepEqual(completed, { id: 'A', attempt: 1, kind: 'succeeded', value: 7 })`.
// Restoring the original line brings back the worked observation: succeeded with attempt 1
// and value 7.

// Exercise 2: Reject a result arriving before start: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `assert.deepEqual(queued, {
// id: 'A', attempt: 1, kind: 'queued' });`. Run Example B with that line, explain why the
// edited check now fails for the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' })`; after it the line
// reads `assert.deepEqual(queued, { id: 'A', attempt: 0, kind: 'queued' });` again and
// invalid transition error; original remains queued.

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
