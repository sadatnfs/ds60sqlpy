// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Accept a valid order: change one input
// In a scratch copy of Example A, change `const raw = { id: 'A', quantity: 2, priceCents:
// 125 };` to `const raw = { id: 'A', quantity: 3, priceCents: 125 };`. Which check fails,
// and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(total(order),
// 250)`. Restoring `const raw = { id: 'A', quantity: 2, priceCents: 125 };` brings back:
// total 250; fresh accepted object.

// Exercise 2: Reject syntactically valid but wrong-shaped JSON: debug a regression
// A regression made one Example B line read `for (const text of ['null!', '[]',
// '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {`. Locate and repair it without
// editing the check.
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
