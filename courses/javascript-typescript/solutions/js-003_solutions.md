# js-003: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Control flow decides which expressions execute and how many times. JavaScript conditions use truthiness, so false, 0, empty string, null, undefined and NaN act differently from empty arrays and objects, which are truthy. Short-circuit operators can return an operand rather than a Boolean. The nullish-coalescing operator provides a fallback only for null or undefined, which is often different from treating zero or empty text as missing.

Loops need an initial state, an invariant and a termination condition. A prefix sum invariant says the accumulator equals the sum of elements already visited. Half-open index bounds align with zero-based arrays. Boundary tests on empty and single-element inputs expose off-by-one errors more clearly than a large happy-path example. A loop that mutates its own collection also needs an explicit policy about which elements are visited.

**Truthiness:** The Boolean interpretation used by conditions.

**Short circuit:** Skipping an operand after the result can be determined.

**Loop invariant:** A property preserved as each iteration advances.

**Nullish fallback:** A fallback applied only to null or undefined.

## Reading the implementation

Use if for a branch, for...of for values, and indexed for when positions matter. The expression left&&right evaluates right only when left is truthy; left||right uses right only when left is falsy. Neither necessarily returns a Boolean. The expression value??fallback preserves 0, false and empty string. A loop condition i<array.length excludes the invalid index length.

## Exercise 1: Compare false and truthy containers: predict an edited check

Task: Copy Example A into a scratch `main.mjs` and change `assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);` to `assert.deepEqual([Boolean(1), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);` inside its check. Before running it, predict whether the check still passes and explain why; then restore it.

An empty collection is still an object. Testing if(array) does not establish that it contains any elements.

The unchanged code is the exercise block of Example A:

```javascript
assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true])`. Restoring the original line brings back the worked observation: false, false, true, true.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and explain why the edited check rejects the values that `assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true])` accepts. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Preserve a valid zero with nullish fallback: diagnose an edited check

Task: A careless edit changed a check in Example B so that it reads `assert.equal(null ?? 11, 10);`. Run Example B with that line, explain why the edited check now fails for the same program state, and restore it.

The operators encode different absence policies. A valid zero count should not silently become a default because it is falsy.

The unchanged code is the exercise block of Example B:

```javascript
assert.equal(0 || 10, 10);
assert.equal(0 ?? 10, 0);
assert.equal(null ?? 10, 10);
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.equal(null ?? 10, 10)`; after it the line reads `assert.equal(null ?? 10, 10);` again and 10, 0, 10.

**Verify:** Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that `assert.equal(null ?? 10, 10)` accepts.

## Exercise 3: Trace a prefix sum

Task: Sum 2, 4, 6 and record the accumulator after each iteration.

Each element contributes exactly once. The recorded states make the invariant inspectable rather than only checking a final total.

```javascript
let sum = 0;
const prefixes = [];
for (const value of [2, 4, 6]) {
  sum += value;
  prefixes.push(sum);
}
assert.deepEqual(prefixes, [2, 6, 12]);
```

**Expected:** prefixes 2, 6, 12.

**Verify:** Keep a check equivalent to `assert.deepEqual(prefixes, [2, 6, 12])`. As a control, change `sum += value;` to `sum -= value;`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Handle an empty collection

Task: Run the same accumulation pattern on an empty array.

The additive identity already represents the empty result. No fabricated element is needed.

```javascript
let sum = 0;
let iterations = 0;
for (const value of []) {
  sum += value;
  iterations += 1;
}
assert.equal(sum, 0);
assert.equal(iterations, 0);
```

**Expected:** sum 0 and iterations 0.

**Verify:** Keep a check equivalent to `assert.equal(iterations, 0)`. As a control, change `let iterations = 0;` to `let iterations = 1;`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Stop at the first match

Task: Find the first 8 in 3, 8, 8 using an indexed loop and break.

Without break, a later match could overwrite the first index. The sentinel -1 distinguishes absence from index 0.

```javascript
const values = [3, 8, 8];
let found = -1;
for (let index = 0; index < values.length; index += 1) {
  if (values[index] === 8) {
    found = index;
    break;
  }
}
assert.equal(found, 1);
```

**Expected:** index 1.

**Verify:** Keep a check equivalent to `assert.equal(found, 1)`. As a control, change `if (values[index] === 8) {` to `if (values[index] !== 8) {`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 6: Make a wrong boundary observable

Task: Iterate with index<=length over a one-element array and record the values.

JavaScript array out-of-range reads return undefined rather than throwing by default. A loop bug can therefore travel into later arithmetic as NaN unless the contract is checked.

```javascript
const values = [7];
const observed = [];
for (let index = 0; index <= values.length; index += 1) observed.push(values[index]);
assert.deepEqual(observed, [7, undefined]);
```

**Expected:** extra undefined element exposes the off-by-one.

**Verify:** Keep a check equivalent to `assert.deepEqual(observed, [7, undefined])`. As a control, change `for (let index = 0; index <= values.length; index += 1) observed.push(values[index]);` to `for (let index = 0; index < values.length; index += 1) observed.push(values[index]);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
