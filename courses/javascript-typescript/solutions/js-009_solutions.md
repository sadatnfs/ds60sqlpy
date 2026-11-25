# js-009: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

Errors should distinguish an invalid request from an expected missing result and an operational failure. JavaScript can throw any value, but throwing Error objects preserves a useful message, stack and cause chain. Validation belongs at an external boundary before state changes or resource work. A catch that returns a plausible default for every failure can turn corrupted input into misleading success.

This lesson parses a bounded order record with an identifier, positive quantity and integer-cent price. JSON syntax validity is only the first gate; the parsed value can still be null, an array, missing fields or semantically invalid. The validator returns a fresh accepted record and leaves the input untouched. A domain calculation checks integer overflow with Number.isSafeInteger. Error translation adds context while preserving the original cause.

**Validation boundary:** The point where untrusted values are checked before use.

**Error cause:** The original failure retained when adding higher-level context.

**Domain invariant:** A rule every accepted record must satisfy.

**Failure category:** A named distinction guiding diagnosis or recovery.

## Reading the implementation

Use try/catch around the operation whose failure you intend to handle. Check object shape, own keys, primitive types and value bounds explicitly. Number.isInteger and Number.isSafeInteger express different numeric contracts. Throw TypeError for a schema/type violation and RangeError for an out-of-range numeric value under this fixture. Error options can retain cause when translating an operational failure.

## Exercise 1: Accept a valid order: change one input

Task: In a scratch copy of Example A, change `const raw = { id: 'A', quantity: 2, priceCents: 125 };` to `const raw = { id: 'A', quantity: 3, priceCents: 125 };`. Which check fails, and what value does it see?

The accepted record is a copy with a known schema. It does not expose a reference that an external caller can later edit to invalidate the already checked value.

The unchanged code is the exercise block of Example A:

```javascript
const raw = { id: 'A', quantity: 2, priceCents: 125 };
const order = validateOrder(raw);
assert.equal(total(order), 250);
assert.notEqual(order, raw);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(total(order), 250)`. Restoring `const raw = { id: 'A', quantity: 2, priceCents: 125 };` brings back: total 250; fresh accepted object.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const raw = { id: 'A', quantity: 2, priceCents: 125 };`.

## Exercise 2: Reject syntactically valid but wrong-shaped JSON: debug a regression

Task: A regression made one Example B line read `for (const text of ['null!', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {`. Locate and repair it without editing the check.

JSON.parse proves only syntax. It does not know the domain fields or reject a valid JSON value of the wrong kind.

The unchanged code is the exercise block of Example B:

```javascript
for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {
  assert.throws(() => validateOrder(JSON.parse(text)), TypeError);
}
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.throws(() => validateOrder(JSON.parse(text)), TypeError)`. Restoring `for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {` brings back: typeError for each shape violation.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Reject invalid numeric domain values

Task: Try quantity 0, quantity 1.5 and negative price.

A numeric runtime type does not establish a positive integer or nonnegative cent amount. The validator makes those domain rules explicit.

```javascript
for (const raw of [
  { id: 'A', quantity: 0, priceCents: 2 },
  { id: 'A', quantity: 1.5, priceCents: 2 },
  { id: 'A', quantity: 1, priceCents: -1 },
]) {
  assert.throws(() => validateOrder(raw), RangeError);
}
```

**Expected:** RangeError for each.

**Verify:** Keep `assert.throws(() => validateOrder(raw), RangeError)`. Control: changing `{ id: 'A', quantity: 0, priceCents: 2 },` to `{ id: 'A', quantity: 1, priceCents: 2 },` must make that check fail; then restore it.

## Exercise 4: Prevent unsafe integer multiplication

Task: Use a valid safe unit price with quantity 2 whose product exceeds the safe integer range.

Inputs can each be valid while their combination exceeds the output representation. Validate the computed result as well as individual fields.

```javascript
const order = validateOrder({ id: 'A', quantity: 2, priceCents: Number.MAX_SAFE_INTEGER });
assert.throws(() => total(order), RangeError);
```

**Expected:** RangeError from total.

**Verify:** Keep the check `assert.throws(() => total(order), RangeError)`; name an input that would make it fail and the value that changes.

## Exercise 5: Preserve a translated cause

Task: Wrap a SyntaxError with a contextual Error using cause.

The added context should not erase the underlying failure type or stack. Callers can inspect the cause when deciding whether recovery is appropriate.

```javascript
const original = new SyntaxError('invalid fixture JSON');
const contextual = new Error('Cannot read order fixture', { cause: original });
assert.equal(contextual.cause, original);
assert.match(contextual.message, /order fixture/u);
```

**Expected:** cause identity retained.

**Verify:** Keep the check `assert.match(contextual.message, /order fixture/u)`; name an input that would make it fail and the value that changes.

## Exercise 6: Prove rejected input caused no mutation

Task: Validate a bad quantity and compare the original object after failure.

Validation should not partially repair or mutate untrusted input before throwing unless that behavior is explicitly part of the API. A pure boundary is easier to audit.

```javascript
const raw = { id: 'A', quantity: -1, priceCents: 5 };
const before = structuredClone(raw);
assert.throws(() => validateOrder(raw), RangeError);
assert.deepEqual(raw, before);
```

**Expected:** input unchanged.

**Verify:** Keep the check `assert.deepEqual(raw, before)`; name an input that would make it fail and the value that changes.

## After comparison

Fresh case: add a `discount` field that must be an integer from 0 up to the price. Predict the error class for `-1`, for `'5'` and for a discount larger than the price, and confirm that a rejected order leaves the input untouched. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
