// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Distinguish own and inherited properties
// Create a child inheriting kind and owning name.
// Expected: kind found by in but not hasOwn; name is own.

// Exercise 2: Copy only own enumerable fields
// Spread the child into a plain record and inspect keys.
// Expected: only name copied.

// Exercise 3: Use destructuring defaults carefully
// Read missing count and explicit null count with default 0.
// Expected: missing becomes 0; null remains null.

// Exercise 4: Use a null-prototype dictionary for arbitrary keys
// Store __proto__ as data in Object.create(null).
// Expected: own value preserved; prototype remains null.

// Exercise 5: Expose shallow freeze
// Freeze an outer object and mutate its nested record.
// Expected: outer reassignment throws; inner value can change.

// Exercise 6: Observe a getter side effect
// Read a controlled getter twice and count calls.
// Expected: values 1 then 2; getter executed twice.

console.log("Implement the six exercises in your saved copy.");
