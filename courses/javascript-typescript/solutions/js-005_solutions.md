# js-005: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

Array operations differ in whether they mutate the container, return a new container or reuse referenced objects. map transforms values, filter selects them, and reduce combines them under an explicit accumulator contract. A new array does not necessarily contain new objects: shallow copies preserve nested references. sort mutates its array and uses string ordering by default, which can misorder numbers. toSorted returns a sorted copy in the prepared Node 24 runtime.

An immutable transformation means preserving the prior value needed by the application, not merely using const. const prevents rebinding the variable but does not freeze its array. Choose mutation or copying based on ownership and history requirements. Test both returned results and the original input when preservation is part of the contract.

**Transformation:** A rule producing new values from existing elements.

**Reduction:** Combining elements into one accumulator result.

**Shallow copy:** A new container retaining references to nested objects.

**Mutation:** Changing the state of an existing object.

## Reading the implementation

map receives value, index and array; avoid passing a callback that unintentionally interprets the extra arguments. filter keeps elements whose predicate is truthy. reduce needs an identity for an empty input unless absence is handled separately. Use (a, b)=>a-b for numeric ordering. Spread or slice copies the outer array only; copy nested records deliberately when they will be edited.

## Exercise 1: Map and filter without changing input: change one input

Task: In a scratch copy of Example A, change `const original = [1, 2, 3, 4];` to `const original = [2, 2, 3, 4];`. Which check fails, and what value does it see?

The pipeline returns new arrays while retaining the original numeric fixture. Object-valued elements would need an additional ownership analysis.

The unchanged code is the exercise block of Example A:

```javascript
const original = [1, 2, 3, 4];
const result = original.map((value) => value * 2).filter((value) => value > 4);
assert.deepEqual(result, [6, 8]);
assert.deepEqual(original, [1, 2, 3, 4]);
```

**Expected:** The edited run fails with an `AssertionError` at `assert.deepEqual(original, [1, 2, 3, 4])`. Restoring `const original = [1, 2, 3, 4];` brings back: 6, 8; original array unchanged.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const original = [1, 2, 3, 4];`.

## Exercise 2: Supply a reduction identity: diagnose an edited check

Task: Example B's check was edited to read `assert.equal([1, 2, 3].reduce((sum, value) => sum - value, 0), 6);`. Run it, explain the failure and restore the original.

The identity defines the empty case. Omitting it would make an empty array throw and change the callback's initial state.

The unchanged code is the exercise block of Example B:

```javascript
assert.equal(
  [].reduce((sum, value) => sum + value, 0),
  0,
);
assert.equal(
  [1, 2, 3].reduce((sum, value) => sum + value, 0),
  6,
);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal([1, 2, 3].reduce((sum, value) => sum - value, 0), 6);`. Restoring `assert.equal([1, 2, 3].reduce((sum, value) => sum + value, 0), 6);` brings back: 0 and 6.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Expose default sort coercion

Task: Sort 10, 2, 1 with default and numeric comparators.

Default sort compares string representations. A valid array of numbers does not automatically select numeric order.

```javascript
assert.deepEqual([10, 2, 1].sort(), [1, 10, 2]);
assert.deepEqual(
  [10, 2, 1].sort((a, b) => a - b),
  [1, 2, 10],
);
```

**Expected:** default 1, 10, 2; numeric 1, 2, 10.

**Verify:** Keep `assert.deepEqual([10, 2, 1].sort((a, b) => a - b), [1, 2, 10])`. Control: editing it to `[10, 2, 1].sort((a, b) => a + b),` must make the check fail; then restore it.

## Exercise 4: Preserve an array while sorting

Task: Use toSorted on 3, 1, 2 and inspect both arrays.

The prepared Node 24 runtime supplies toSorted. The contract is copying rather than mutating; this distinction matters when another component retains the old array.

```javascript
const original = [3, 1, 2];
const sorted = original.toSorted((a, b) => a - b);
assert.deepEqual(sorted, [1, 2, 3]);
assert.deepEqual(original, [3, 1, 2]);
```

**Expected:** sorted 1, 2, 3; original 3, 1, 2.

**Verify:** Keep `assert.deepEqual(sorted, [1, 2, 3])`. Control: changing `const sorted = original.toSorted((a, b) => a - b);` to `const sorted = original.toSorted((a, b) => a + b);` must make that check fail; then restore it.

## Exercise 5: Expose a shallow copy alias

Task: Spread an array containing one object and mutate that object through the copy.

The containers differ but their first elements share identity. A shallow copy cannot preserve historical nested state by itself.

```javascript
const original = [{ value: 1 }];
const copy = [...original];
copy[0].value = 9;
assert.equal(original[0].value, 9);
assert.notEqual(copy, original);
```

**Expected:** original nested value also changes.

**Verify:** Keep `assert.equal(original[0].value, 9)`. Control: changing `copy[0].value = 9;` to `copy[0].value = 10;` must make that check fail; then restore it.

## Exercise 6: Copy records for a specific edit

Task: Map records to new objects before changing one field.

This copy is sufficient for the fixture's flat record. Deeper mutable fields would need their own policy rather than a claim that spread is a universal deep clone.

```javascript
const original = [{ value: 1 }];
const copy = original.map((row) => ({ ...row }));
copy[0].value = 9;
assert.equal(original[0].value, 1);
assert.equal(copy[0].value, 9);
```

**Expected:** edited record changes; original record stays 1.

**Verify:** Keep `assert.equal(copy[0].value, 9)`. Control: changing `copy[0].value = 9;` to `copy[0].value = 10;` must make that check fail; then restore it.

## After comparison

Fresh case: sort `{ name, score }` records by score descending and then by name, without changing the input. Include two equal scores and an empty array, and predict the order before running. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
