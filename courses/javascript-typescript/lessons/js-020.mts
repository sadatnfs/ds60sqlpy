// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Handle a result union
// Format both successful value 7 and a failure message.
// Expected: value:7 and error:offline.

// Exercise 2: Preserve an empty string during narrowing
// Handle string or undefined using an explicit undefined comparison.
// Expected: empty string has length 0; absent value returns missing.

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
