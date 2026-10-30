# js-014: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

An algorithm is a rule for transforming an input into a result; complexity describes how its required work grows with input size. Counting comparisons on controlled inputs explains a growth claim better than a single timing measurement. Linear search may inspect every item. Binary search discards approximately half of a sorted interval at each step, requiring logarithmically many comparisons. Sorting or building an index also has a cost, so binary search is not automatically the best choice for one lookup in unsorted data.

This lesson implements lower_bound: the first position at which a target could be inserted without breaking sorted order. The half-open interval [low, high) always contains the answer. If values[mid] is less than the target, all positions through mid are too early, so low becomes mid+1. Otherwise high becomes mid. The interval shrinks on every iteration, preventing a duplicate value from trapping the loop.

A Map can index records by key when repeated lookups justify an extra structure. Duplicate-key policy must be explicit because silently overwriting records loses information. A binary min-heap supports repeated access to the smallest item without fully sorting every update. Its shape is an array-backed complete tree; the parent of index i is floor((i-1)/2), and children are 2i+1 and 2i+2. Restoring the parent-before-child invariant takes logarithmic height. Map performance guarantees are implementation dependent, so this lesson does not promise worst-case constant time for every lookup.

**Complexity:** How operation count or storage grows with input size.

**Search invariant:** A property keeping the possible answer inside a shrinking interval.

**Index:** A structure trading construction and storage for later lookup convenience.

**Heap invariant:** Every parent is no larger than either child in a min-heap.

## Reading the implementation

lowerBound returns an insertion position from 0 through length, including length when the target exceeds all values. Finding equality requires a separate comparison at that position. Heap push bubbles a new value toward its parent; pop moves the last value to the root and sinks it toward the smaller child. An empty heap returns undefined under this API. The algorithms assume finite numeric values and sorted search input; accepting NaN would break the ordering relation.

## Exercise 1: Trace lower bound with duplicates

Task: Find the first insertion position for 4 in 1,4,4,8 and inspect the visited intervals.

The equality branch moves high leftward rather than returning an arbitrary match. That is why lower bound finds the first duplicate and remains useful for insertion and range queries.

```javascript
const trace = [];
assert.equal(lowerBound([1, 4, 4, 8], 4, trace), 1);
assert.deepEqual(trace, [
  [0, 4, 2],
  [0, 2, 1],
  [0, 1, 0],
]);
```

**Expected:** index 1; intervals shrink to the first duplicate.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Use a heap for repeated minimum extraction

Task: Insert 5,1,3,1 and remove all values.

The heap maintains only the order needed at its root, not a fully sorted array. Equal priorities remain valid, but this numeric heap does not promise stable ordering among associated records.

```javascript
const heap = new MinHeap();
for (const value of [5, 1, 3, 1]) heap.push(value);
assert.deepEqual([heap.pop(), heap.pop(), heap.pop(), heap.pop()], [1, 1, 3, 5]);
assert.equal(heap.pop(), undefined);
```

**Expected:** pops 1,1,3,5, then undefined.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Cover empty and outside search boundaries

Task: Search empty input, then targets below and above a sorted input.

Returning length is a valid insertion answer, not a valid array element. A caller must check position < length before testing equality.

```javascript
assert.equal(lowerBound([], 4), 0);
assert.equal(lowerBound([2, 4, 6], 1), 0);
assert.equal(lowerBound([2, 4, 6], 9), 3);
```

**Expected:** positions 0,0,3.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Measure comparisons without a timing claim

Task: Search 1024 even integers for a missing value between two entries.

An operation count exposes logarithmic interval reduction independent of machine speed. It does not account for the cost of first sorting or materializing the input.

```javascript
const values = Array.from({ length: 1024 }, (_, index) => index * 2);
const trace = [];
assert.equal(lowerBound(values, 1001, trace), 501);
assert.ok(trace.length <= 11);
assert.equal(values.includes(1001), false);
```

**Expected:** insertion position 501 with no more than 11 comparisons.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Reject duplicate index keys

Task: Build a Map keyed by id and reject repeated ids rather than silently replacing a row.

Index construction is a data-quality boundary. An overwritten record could make later lookup appear correct while silently dropping an input row.

```javascript
const index = uniqueIndex([
  { id: 'A', value: 7 },
  { id: 'B', value: 9 },
]);
assert.equal(index.get('A').value, 7);
assert.throws(() => uniqueIndex([{ id: 'A' }, { id: 'A' }]), /duplicate/u);
```

**Expected:** valid lookup returns 7; duplicate id throws.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Check the heap invariant after every update

Task: Push descending values and check each parent/child relation; reject NaN.

Inspecting the invariant catches a broken bubble-up implementation before it happens to return a wrong minimum. NaN lacks the total ordering this implementation requires.

```javascript
const heap = new MinHeap();
for (const value of [6, 5, 4, 3, 2, 1]) {
  heap.push(value);
  for (let index = 1; index < heap.values.length; index += 1) {
    assert.ok(heap.values[Math.floor((index - 1) / 2)] <= heap.values[index]);
  }
}
assert.throws(() => heap.push(NaN), TypeError);
```

**Expected:** all invariants hold; invalid value throws.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
