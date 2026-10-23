// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Validate and copy a complete order
// Parse an order with two line items and inspect the typed success.
// Expected: success with total quantity 5; independent copied item records.

// Exercise 2: Report a nested domain failure precisely
// Validate a second item with quantity zero.
// Expected: failure code schema and path items[1].quantity.

// Exercise 3: Separate JSON syntax failure from schema failure
// Parse malformed JSON and valid JSON null.
// Expected: codes json and schema respectively.

// Exercise 4: Reject unknown fields and excessive item counts
// Add an extra top-level field, then exceed the twenty-item limit.
// Expected: paths $ and items respectively.

// Exercise 5: Preserve the validated value after input mutation
// Validate a mutable source and edit its first item afterward.
// Expected: validated quantity stays 2 while input becomes 9.

// Exercise 6: Exercise numeric and string boundaries
// Reject NaN, fractional quantities, empty SKU and oversized identifiers.
// Expected: every malformed fixture is rejected; an empty items array remains valid.

console.log("Implement the six exercises in your saved copy.");
