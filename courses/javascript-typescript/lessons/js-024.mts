// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Validate and copy a complete order: change one input
// Copy Example A into a scratch `main.mts` and change `{ sku: 'X', quantity: 2 },` to `{
// sku: 'X', quantity: 3 },`. Before running it, predict which check fails and which value it
// now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(result.value.items.reduce((sum, item) => sum + item.quantity, 0), 5)`.
// Restoring the original line brings back the worked observation: success with total
// quantity 5; independent copied item records.

// Exercise 2: Report a nested domain failure precisely: debug a regression
// A regression changed one token in Example B, so one line now reads `{ sku: 'Y', quantity:
// 1 },`. Run Example B with that line, use the failing check to locate the defect and repair
// it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(result.ok, false)`; after it the line reads `{ sku: 'Y', quantity: 0 },`
// again and failure code schema and path items[1].quantity.

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
