# js-007: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Map and Set provide collection contracts different from plain object records. Map can use objects as keys without converting them to string. Object keys are compared by identity, so two separately created objects with same fields remain distinct keys. Set removes repeated values under SameValueZero equality, which treats NaN as equal to itself and +0/-0 as the same key. Iteration follows insertion order, but insertion order is not a semantic numeric or business sort unless the application defines it that way.

Choosing a collection determines which information is retained. A Set loses multiplicity; a Map keeps one current value per key. Use a frequency Map when repeated events matter. Avoid checking a lookup result for truthiness when zero, false or undefined can be legitimate stored values; has distinguishes key presence from the value returned by get.

**Reference identity:** Sameness of the actual object rather than its field contents.

**SameValueZero:** The Map/Set primitive equality rule including NaN equality and merged signed zeros.

**Multiplicity:** How many times a value appears in the input.

**Membership:** Whether a key or value is present, independent of its stored value.

## Reading the implementation

Map.set inserts or replaces a key, value pair; get returns the value or undefined; has checks membership. Map.size counts keys. Set.add returns the set itself, while has reports membership. Iterating map entries yields [key, value] pairs in insertion order. Updating an existing key does not move it to the end; deleting and reinserting does.

## Exercise 1: Keep equal-looking object keys distinct: change one input

Task: Copy Example A into a scratch `main.mjs` and change `[second, 'b'],` to `[second, 'b!'],`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

Field equality does not establish object identity. A domain needing value-based keys should choose a stable canonical identifier explicitly.

The unchanged code is the exercise block of Example A:

```javascript
const first = { id: 1 };
const second = { id: 1 };
const map = new Map([
  [first, 'a'],
  [second, 'b'],
]);
assert.equal(map.size, 2);
assert.equal(map.get(first), 'a');
assert.equal(map.get(second), 'b');
```

**Expected:** The changed run fails with an `AssertionError` at `assert.equal(map.get(second), 'b')`. Restoring `[second, 'b'],` brings back: size 2 and separate values.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal(map.get(second), 'b')` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Inspect Set equality: diagnose an edited check

Task: A careless edit changed a check in Example B so that it reads `assert.equal(values.has(-1), true);`. Run Example B with that line, explain why the edited check now fails for the same program state, and restore it.

The collection equality contract differs from strict NaN comparison and Object.is signed zero behavior. Know the actual relation used by the container.

The unchanged code is the exercise block of Example B:

```javascript
const values = new Set([NaN, NaN, 0, -0]);
assert.equal(values.size, 2);
assert.equal(values.has(NaN), true);
assert.equal(values.has(-0), true);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(values.has(-1), true);`. Restoring `assert.equal(values.has(-0), true);` brings back: size 2: one NaN and one zero.

**Verify:** Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that `assert.equal(values.has(-0), true)` accepts.

## Exercise 3: Count repeated events

Task: Build a frequency Map for red, blue, red.

A Set would retain only membership and lose the two red observations. The accumulator uses an explicit zero for an absent count.

```javascript
const counts = new Map();
for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) + 1);
assert.deepEqual(
  [...counts],
  [
    ['red', 2],
    ['blue', 1],
  ],
);
```

**Expected:** red 2, blue 1.

**Verify:** Keep a check equivalent to `assert.deepEqual([...counts], [['red', 2], ['blue', 1]])`. As a control, change `for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) + 1);` to `for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) - 1);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Distinguish a stored zero from absence

Task: Store key a with 0 and compare has/get for a and b.

Truthiness would misclassify the valid zero as missing. Presence and value are separate questions.

```javascript
const map = new Map([['a', 0]]);
assert.equal(map.has('a'), true);
assert.equal(map.get('a'), 0);
assert.equal(map.has('b'), false);
assert.equal(map.get('b'), undefined);
```

**Expected:** a present with 0; b absent with undefined.

**Verify:** Keep a check equivalent to `assert.equal(map.get('a'), 0)`. As a control, change `const map = new Map([['a', 0]]);` to `const map = new Map([['a', 1]]);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 5: Trace insertion order updates

Task: Insert a, b, update a, then delete and reinsert a.

The order reflects insertion history. If a report requires sorted keys, sort them rather than depending on this history accidentally.

```javascript
const map = new Map([
  ['a', 1],
  ['b', 2],
]);
map.set('a', 3);
assert.deepEqual([...map.keys()], ['a', 'b']);
map.delete('a');
map.set('a', 4);
assert.deepEqual([...map.keys()], ['b', 'a']);
```

**Expected:** update order a, b; reinsertion order b, a.

**Verify:** Keep a check equivalent to `assert.deepEqual([...map.keys()], ['b', 'a'])`. As a control, change `map.delete('a'); map.set('a', 4);` to `map.delete('a!'); map.set('a', 4);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 6: Deduplicate while preserving first occurrence

Task: Use Set over b, a, b, c, a and compare the ordered unique values.

This operation intentionally loses repeat counts while preserving first appearance order. State that contract before using it in a data pipeline.

```javascript
const unique = [...new Set(['b', 'a', 'b', 'c', 'a'])];
assert.deepEqual(unique, ['b', 'a', 'c']);
```

**Expected:** b, a, c.

**Verify:** Keep a check equivalent to `assert.deepEqual(unique, ['b', 'a', 'c'])`. As a control, change `const unique = [...new Set(['b', 'a', 'b', 'c', 'a'])];` to `const unique = [...new Set(['b!', 'a', 'b', 'c', 'a'])];`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
