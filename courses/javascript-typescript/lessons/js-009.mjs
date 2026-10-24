// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Accept a valid order
// Validate id A, quantity 2, price 125 and calculate integer cents.
// Expected: total 250; fresh accepted object.

// Exercise 2: Reject syntactically valid but wrong-shaped JSON
// Parse null, an array and an object with an extra field, then validate.
// Expected: TypeError for each shape violation.

// Exercise 3: Reject invalid numeric domain values
// Try quantity 0, quantity 1.5 and negative price.
// Expected: RangeError for each.

// Exercise 4: Prevent unsafe integer multiplication
// Use a valid safe unit price with quantity 2 whose product exceeds the safe integer range.
// Expected: RangeError from total.

// Exercise 5: Preserve a translated cause
// Wrap a SyntaxError with a contextual Error using cause.
// Expected: cause identity retained.

// Exercise 6: Prove rejected input caused no mutation
// Validate a bad quantity and compare the original object after failure.
// Expected: input unchanged.

console.log("Implement the six exercises in your saved copy.");
