# js-007: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

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

Task: In a scratch copy of Example A, change `[second, 'b'],` to `[second, 'b!'],`. Which check fails, and what value does it see?

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

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(map.get(second), 'b')`. Restoring `[second, 'b'],` brings back: size 2 and separate values.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `[second, 'b'],`.

## Exercise 2: Inspect Set equality: diagnose an edited check

Task: Example B's check was edited to read `assert.equal(values.has(-1), true);`. Run it, explain the failure and restore the original.

The collection equality contract differs from strict NaN comparison and Object.is signed zero behavior. Know the actual relation used by the container.

The unchanged code is the exercise block of Example B:

```javascript
const values = new Set([NaN, NaN, 0, -0]);
assert.equal(values.size, 2);
assert.equal(values.has(NaN), true);
assert.equal(values.has(-0), true);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(values.has(-1), true);`. Restoring `assert.equal(values.has(-0), true);` brings back: size 2: one NaN and one zero.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

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

**Verify:** Keep `assert.deepEqual([...counts], [['red', 2], ['blue', 1]])`. Control: changing `for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) + 1);` to `for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) - 1);` must make that check fail; then restore it.

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

**Verify:** Keep `assert.equal(map.get('a'), 0)`. Control: changing `const map = new Map([['a', 0]]);` to `const map = new Map([['a', 1]]);` must make that check fail; then restore it.

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

**Verify:** Keep `assert.deepEqual([...map.keys()], ['b', 'a'])`. Control: changing `map.delete('a'); map.set('a', 4);` to `map.delete('a!'); map.set('a', 4);` must make that check fail; then restore it.

## Exercise 6: Deduplicate while preserving first occurrence

Task: Use Set over b, a, b, c, a and compare the ordered unique values.

This operation intentionally loses repeat counts while preserving first appearance order. State that contract before using it in a data pipeline.

```javascript
const unique = [...new Set(['b', 'a', 'b', 'c', 'a'])];
assert.deepEqual(unique, ['b', 'a', 'c']);
```

**Expected:** b, a, c.

**Verify:** Keep `assert.deepEqual(unique, ['b', 'a', 'c'])`. Control: changing `const unique = [...new Set(['b', 'a', 'b', 'c', 'a'])];` to `const unique = [...new Set(['b!', 'a', 'b', 'c', 'a'])];` must make that check fail; then restore it.

## After comparison

Fresh case: count the words in `['to', 'be', 'or', 'not', 'to', 'be']` and list them by first occurrence with their counts. Then add the word `'constructor'`: a plain object counter breaks on it, while a `Map` needs no special case. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
