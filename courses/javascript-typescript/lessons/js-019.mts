// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Annotate a numeric function: change one input
// In a scratch copy of Example A, change `const result = add(2, 3);` to `const result =
// add(3, 3);`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(result, 5)`.
// Restoring `const result = add(2, 3);` brings back: sum 5 with runtime typeof number.

// Exercise 2: Show that an assertion does not convert data: debug a regression
// A regression made one Example B line read `const external: unknown = 'wrong!';`. Locate
// and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(String(claimed), 'wrong')`. Restoring `const external: unknown = 'wrong';`
// brings back: the runtime value remains the string wrong.

// Exercise 3: Compare literal preservation and widening
// Use const for a fixed tag and let for a changing text value.
// Expected: fixed tag remains ready; mutable text can change to done.

// Exercise 4: Handle null explicitly under strict checking
// Write a length function accepting string or null.
// Expected: length 3 for abc and 0 for null.

// Exercise 5: Observe type erasure through object keys
// Declare a record type and create a compatible object.
// Expected: runtime keys contain only id and count, with no type alias metadata.

// Exercise 6: Narrow unknown before numeric use
// Accept only a finite number from an unknown value.
// Expected: 12 doubles to 24; string 12 and Infinity reject.

console.log("Implement the six exercises in your saved copy.");
