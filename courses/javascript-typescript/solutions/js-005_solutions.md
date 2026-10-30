# js-005: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Array operations differ in whether they mutate the container, return a new container or reuse referenced objects. map transforms values, filter selects them, and reduce combines them under an explicit accumulator contract. A new array does not necessarily contain new objects: shallow copies preserve nested references. sort mutates its array and uses string ordering by default, which can misorder numbers. toSorted returns a sorted copy in the prepared Node 24 runtime.

An immutable transformation means preserving the prior value needed by the application, not merely using const. const prevents rebinding the variable but does not freeze its array. Choose mutation or copying based on ownership and history requirements. Test both returned results and the original input when preservation is part of the contract.

**Transformation:** A rule producing new values from existing elements.

**Reduction:** Combining elements into one accumulator result.

**Shallow copy:** A new container retaining references to nested objects.

**Mutation:** Changing the state of an existing object.

## Reading the implementation

map receives value, index and array; avoid passing a callback that unintentionally interprets the extra arguments. filter keeps elements whose predicate is truthy. reduce needs an identity for an empty input unless absence is handled separately. Use (a, b)=>a-b for numeric ordering. Spread or slice copies the outer array only; copy nested records deliberately when they will be edited.

## Exercise 1: Map and filter without changing input

Task: Double 1, 2, 3, 4 and keep results above 4.

The pipeline returns new arrays while retaining the original numeric fixture. Object-valued elements would need an additional ownership analysis.

```javascript
const original = [1, 2, 3, 4];
const result = original.map((value) => value * 2).filter((value) => value > 4);
assert.deepEqual(result, [6, 8]);
assert.deepEqual(original, [1, 2, 3, 4]);
```

**Expected:** 6, 8; original array unchanged.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Supply a reduction identity

Task: Sum an empty array and 1, 2, 3 using initial 0.

The identity defines the empty case. Omitting it would make an empty array throw and change the callback's initial state.

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

**Expected:** 0 and 6.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
