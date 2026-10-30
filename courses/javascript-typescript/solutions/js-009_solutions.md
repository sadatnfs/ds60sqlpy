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

## Exercise 1: Accept a valid order

Task: Validate id A, quantity 2, price 125 and calculate integer cents.

The accepted record is a copy with a known schema. It does not expose a reference that an external caller can later edit to invalidate the already checked value.

```javascript
const raw = { id: 'A', quantity: 2, priceCents: 125 };
const order = validateOrder(raw);
assert.equal(total(order), 250);
assert.notEqual(order, raw);
```

**Expected:** total 250; fresh accepted object.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject syntactically valid but wrong-shaped JSON

Task: Parse null, an array and an object with an extra field, then validate.

JSON.parse proves only syntax. It does not know the domain fields or reject a valid JSON value of the wrong kind.

```javascript
for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {
  assert.throws(() => validateOrder(JSON.parse(text)), TypeError);
}
```

**Expected:** TypeError for each shape violation.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Prevent unsafe integer multiplication

Task: Use a valid safe unit price with quantity 2 whose product exceeds the safe integer range.

Inputs can each be valid while their combination exceeds the output representation. Validate the computed result as well as individual fields.

```javascript
const order = validateOrder({ id: 'A', quantity: 2, priceCents: Number.MAX_SAFE_INTEGER });
assert.throws(() => total(order), RangeError);
```

**Expected:** RangeError from total.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
