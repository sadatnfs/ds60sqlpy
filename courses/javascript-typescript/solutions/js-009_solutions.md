# js-009: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

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

Task: Copy Example A into a scratch `main.mjs` and change `const raw = { id: 'A', quantity: 2, priceCents: 125 };` to `const raw = { id: 'A', quantity: 3, priceCents: 125 };`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The accepted record is a copy with a known schema. It does not expose a reference that an external caller can later edit to invalidate the already checked value.

The unchanged code is the exercise block of Example A:

```javascript
const raw = { id: 'A', quantity: 2, priceCents: 125 };
const order = validateOrder(raw);
assert.equal(total(order), 250);
assert.notEqual(order, raw);
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal(total(order), 250)`. Restoring the original line brings back the worked observation: total 250; fresh accepted object.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(total(order), 250)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Reject syntactically valid but wrong-shaped JSON: debug a regression

Task: A regression changed one token in Example B, so one line now reads `for (const text of ['null!', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

JSON.parse proves only syntax. It does not know the domain fields or reject a valid JSON value of the wrong kind.

The unchanged code is the exercise block of Example B:

```javascript
for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {
  assert.throws(() => validateOrder(JSON.parse(text)), TypeError);
}
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.throws(() => validateOrder(JSON.parse(text)), TypeError)`; after it the line reads `for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {` again and typeError for each shape violation.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.throws(() => validateOrder(JSON.parse(text)), TypeError)` for this input.

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

**Verify:** Keep a check equivalent to `assert.throws(() => validateOrder(raw), RangeError)`. As a control, change `{ id: 'A', quantity: 0, priceCents: 2 },` to `{ id: 'A', quantity: 1, priceCents: 2 },`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Prevent unsafe integer multiplication

Task: Use a valid safe unit price with quantity 2 whose product exceeds the safe integer range.

Inputs can each be valid while their combination exceeds the output representation. Validate the computed result as well as individual fields.

```javascript
const order = validateOrder({ id: 'A', quantity: 2, priceCents: Number.MAX_SAFE_INTEGER });
assert.throws(() => total(order), RangeError);
```

**Expected:** RangeError from total.

**Verify:** Keep a check equivalent to `assert.throws(() => total(order), RangeError)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

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

**Verify:** Keep a check equivalent to `assert.match(contextual.message, /order fixture/u)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

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

**Verify:** Keep a check equivalent to `assert.deepEqual(raw, before)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
