// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Validate and copy a complete order: change one input
// In a scratch copy of Example A, change `{ sku: 'X', quantity: 2 },` to `{ sku: 'X',
// quantity: 3 },`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at
// `assert.equal(result.value.items.reduce((sum, item) => sum + item.quantity, 0), 5)`.
// Restoring `{ sku: 'X', quantity: 2 },` brings back: success with total quantity 5;
// independent copied item records.

// Exercise 2: Report a nested domain failure precisely: debug a regression
// A regression made one Example B line read `{ sku: 'Y', quantity: 1 },`. Locate and repair
// it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(result.ok, false)`. Restoring `{ sku: 'Y', quantity: 0 },` brings back:
// failure code schema and path `items[1].quantity`.

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
