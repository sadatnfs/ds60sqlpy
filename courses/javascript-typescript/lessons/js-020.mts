// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Handle a result union: predict an edited check
// Copy Example A into a scratch `main.mts` and change `assert.equal(formatResult({ kind:
// 'failure', message: 'offline' }), 'error:offline');` to `assert.equal(formatResult({ kind:
// 'failure', message: 'offline!' }), 'error:offline');` inside its check. Before running it,
// predict whether the check still passes and explain why; then restore it.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(formatResult({
// kind: 'failure', message: 'offline!' }), 'error:offline');`. Restoring
// `assert.equal(formatResult({ kind: 'failure', message: 'offline' }), 'error:offline');`
// brings back: `value:7` and `error:offline`.

// Exercise 2: Preserve an empty string during narrowing: diagnose an edited check
// A careless edit changed a check in Example B so that it reads
// `assert.equal(describe(undefined), 'missing!');`. Run Example B with that line, explain
// why the edited check now fails for the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(describe(undefined), 'missing!');`. Restoring
// `assert.equal(describe(undefined), 'missing');` brings back: empty string has length 0;
// absent value returns missing.

// Exercise 3: Reject access to another variant payload
// Demonstrate that a failure branch cannot read value.
// Expected: expected compiler error on value; valid failure formatting remains unchanged.

// Exercise 4: Catch an unhandled new variant at compile time
// Add a pending variant and intentionally omit it from a switch in an uncalled function.
// Expected: expected compiler error at assertNever for pending.

// Exercise 5: Use an honest unknown-value predicate
// Check for a record with a finite numeric value before consuming it.
// Expected: valid record accepted; null, arrays and string-valued records rejected.

// Exercise 6: Expose the runtime limit of an asserted union
// Force a malformed external value into Result for demonstration and call the handler.
// Expected: runtime fallback throws rather than fabricating success.

console.log("Implement the six exercises in your saved copy.");
