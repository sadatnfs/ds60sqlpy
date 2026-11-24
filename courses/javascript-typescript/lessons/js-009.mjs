// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Accept a valid order: change one input
// Copy Example A into a scratch `main.mjs` and change `const raw = { id: 'A', quantity: 2,
// priceCents: 125 };` to `const raw = { id: 'A', quantity: 3, priceCents: 125 };`. Before
// running it, predict which check fails and which value it now sees; then run it and restore
// the original line.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(total(order),
// 250)`. Restoring `const raw = { id: 'A', quantity: 2, priceCents: 125 };` brings back:
// total 250; fresh accepted object.

// Exercise 2: Reject syntactically valid but wrong-shaped JSON: debug a regression
// A regression changed one token in Example B, so one line now reads `for (const text of
// ['null!', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {`. Run Example B
// with that line, use the failing check to locate the defect and repair it without changing
// the check.
// Expected: Before the repair the run fails with an `AssertionError` at `assert.throws(() =>
// validateOrder(JSON.parse(text)), TypeError)`. Restoring `for (const text of ['null', '[]',
// '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {` brings back: typeError for each
// shape violation.

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
