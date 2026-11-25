# js-002: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

JavaScript values have runtime types, and operators can perform implicit conversion. The plus operator adds numbers but concatenates when string conversion applies. Strict equality avoids the broad coercion of loose equality, but it still has specific semantics for NaN and signed zero. Object.is provides another comparison contract. Choose the relation required by the domain rather than assuming one operator means every notion of same.

Numbers use binary floating-point arithmetic and have a finite safe-integer range. Exact decimal fractions such as 0.1 are generally approximate. BigInt represents arbitrary-size integers but cannot be mixed with Number arithmetic without an explicit conversion policy. null and undefined are distinct values commonly used for absence; neither should be silently converted to a domain count. Validate external numeric text before calculation instead of relying on a convenient coercion.

**Coercion:** An implicit conversion performed by an operator or API.

**Strict equality:** A comparison that does not broadly convert different primitive types.

**Safe integer:** An integer exactly distinguishable within the Number representation.

**BigInt:** An arbitrary-size integer type with separate arithmetic rules.

## Reading the implementation

typeof reports primitive categories but typeof null is the historical string object. Number.isNaN tests NaN without coercing its argument. Number.isFinite rejects non-number values and infinities. Object.is distinguishes +0 and -0 while treating NaN as equal to itself. BigInt literals end in n. JSON does not serialize BigInt by default, so an explicit wire-format policy is needed.

## Exercise 1: Trace plus versus numeric conversion: predict an edited check

Task: In a scratch copy of Example A, change `assert.equal(Number('3') + 2, 5);` to `assert.equal(Number('3') + 3, 5);` inside its check. Does the check still pass?

The same symbol has different behavior when a string participates. Explicit conversion makes the intended numeric operation visible.

The unchanged code is the exercise block of Example A:

```javascript
assert.equal(2 + 3, 5);
assert.equal(2 + '3', '23');
assert.equal(Number('3') + 2, 5);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(Number('3') + 3, 5);`. Restoring `assert.equal(Number('3') + 2, 5);` brings back: 5, string 23, and 5.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `assert.equal(Number('3') + 2, 5);`.

## Exercise 2: Inspect absence and NaN: diagnose an edited check

Task: Example B's check was edited to read `assert.equal(Number.isNaN('not a number'), true);`. Run it, explain the failure and restore the original.

The typeof null result is a language legacy, not evidence that null has usable object properties. Number.isNaN avoids converting arbitrary text.

The unchanged code is the exercise block of Example B:

```javascript
assert.equal(typeof null, 'object');
assert.equal(typeof undefined, 'undefined');
assert.equal(Number.isNaN(NaN), true);
assert.equal(Number.isNaN('not a number'), false);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(Number.isNaN('not a number'), true);`. Restoring `assert.equal(Number.isNaN('not a number'), false);` brings back: null reports object; undefined reports undefined; only numeric NaN passes isNaN.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Compare equality contracts

Task: Use NaN, +0 and -0 with strict equality and Object.is.

Different APIs use different equality relations. A collection key policy may differ from Object.is, which is examined in the Map/Set lesson.

```javascript
assert.equal(NaN === NaN, false);
assert.equal(Object.is(NaN, NaN), true);
assert.equal(0 === -0, true);
assert.equal(Object.is(0, -0), false);
```

**Expected:** NaN!==NaN; Object.is(NaN, NaN) is true; +0===-0; Object.is distinguishes zeros.

**Verify:** Keep `assert.equal(NaN === NaN, false)`. Control: editing it to `assert.equal(NaN !== NaN, false);` must make the check fail; then restore it.

## Exercise 4: Expose floating-point approximation

Task: Add 0.1 and 0.2 and compare with 0.3 under an explicit tolerance.

A tolerance is appropriate only when the domain permits approximate arithmetic. Currency or identity calculations may require integer units or another representation.

```javascript
const value = 0.1 + 0.2;
assert.notEqual(value, 0.3);
assert.ok(Math.abs(value - 0.3) < 1e-15);
```

**Expected:** strict equality false; absolute error below 1e-15.

**Verify:** Keep `assert.ok(Math.abs(value - 0.3) < 1e-15)`. Control: changing `const value = 0.1 + 0.2;` to `const value = 0.1 - 0.2;` must make that check fail; then restore it.

## Exercise 5: Protect integer identity

Task: Compare the two integers just beyond Number.MAX_SAFE_INTEGER and then use BigInt.

Losing a unit difference is unacceptable for an identifier or counter requiring exactness. Converting after rounding cannot recover the original integer.

```javascript
const max = Number.MAX_SAFE_INTEGER;
assert.equal(max + 1, max + 2);
const exact = BigInt(max);
assert.notEqual(exact + 1n, exact + 2n);
```

**Expected:** Number collapses a difference; BigInt preserves it.

**Verify:** Keep `assert.equal(max + 1, max + 2)`. Control: editing it to `assert.equal(max - 1, max + 2);` must make the check fail; then restore it.

## Exercise 6: Reject ambiguous numeric input

Task: Validate finite nonblank numeric text and reject blank, Infinity and mixed BigInt arithmetic.

The parser states its accepted text domain instead of accepting every Number coercion. BigInt and Number mixing needs an explicit precision policy.

```javascript
assert.equal(parseFinite('12'), 12);
assert.throws(() => parseFinite(' '), TypeError);
assert.throws(() => parseFinite('Infinity'), TypeError);
assert.throws(() => 1n + 1, TypeError);
```

**Expected:** valid 12 accepted; invalid cases throw.

**Verify:** Keep `assert.equal(parseFinite('12'), 12)`. Control: editing it to `assert.equal(parseFinite('13'), 12);` must make the check fail; then restore it.

## After comparison

Fresh case: run your numeric validator on `'1e3'` and `'0x10'`. `Number` accepts them as 1000 and 16, so decide whether your contract should accept exponent and hexadecimal spellings, and write the check that enforces that decision. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
