# python-algo-01: Explained reference solutions

These answers implement the contracts in [Algorithmic Cost, Hash Indexes, and Duplicate-Aware Matching](../companion-guides/py_algo_01.md). Compare after an attempt. The [executable reference](py_algo_01_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Count work rather than guessing from timing

Count unordered distinct index pairs with explicit nested loops, requiring a nonnegative non-Boolean integer size. Return the number of pair visits. Compare the result with n*(n-1)//2; do not use the formula as the implementation.

**Expected:** Sizes 0,1,4,8 return 0,0,6,28. Negative size, True and 2.5 raise ValueError.

```python
def pair_comparisons(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ValueError("Expected a nonnegative integer size")
    count = 0
    for left in range(size):
        for _right in range(left + 1, size):
            count += 1
    return count
```

The loop embodies the work being measured, while the closed-form identity is an independent oracle. Starting the second index at left+1 excludes self-pairs and avoids counting both orientations. Empty and singleton inputs naturally contain no pairs. Rejecting Boolean size avoids treating True as an accidental one-item problem. The implementation is deliberately quadratic because the lesson is about observing that growth, not optimizing this count.

```python
assert [pair_comparisons(n) for n in [0, 1, 4, 8]] == [0, 0, 6, 28]
for n in range(20):
    assert pair_comparisons(n) == n * (n - 1) // 2
expect_value_error(lambda: pair_comparisons(-1))
expect_value_error(lambda: pair_comparisons(True))
expect_value_error(lambda: pair_comparisons(2.5))  # type: ignore[arg-type]  # Invalid-type boundary.
```

### Exercise 2: Return the first repeated occurrence

Scan integer values left to right and return the value whose repeated occurrence is encountered first. Return None when all values are distinct. Preserve input and distinguish a duplicate zero from no duplicate.

**Expected:** [4,1,4,1] returns 4, [1,2,2,1] returns 2, [0,0] returns 0 and [] returns None.

```python
def first_duplicate(values: list[int]) -> int | None:
    seen = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None
```

Membership is checked before inserting the current value, so the function identifies the first repeated occurrence in scan order. Sorting first would answer a different question and mutate or reorder the evidence. None is used as the absence sentinel because zero is a valid data value. Expected time is linear with state proportional to the distinct values seen before the first duplicate.

```python
values_2 = [4, 1, 4, 1]
assert first_duplicate(values_2) == 4 and values_2 == [4, 1, 4, 1]
assert first_duplicate([1, 2, 2, 1]) == 2 and first_duplicate([0, 0]) == 0
assert first_duplicate([]) is None and first_duplicate([1, 2, 3]) is None
```

### Exercise 3: Build counts while preserving first appearance

Return a dictionary of occurrence counts for string values in first-appearance order. Do not remove repeated values or sort the input. Empty input returns an empty dictionary.

**Expected:** [b, a, b, c, a, b] yields insertion order[b, a, c] and counts 3,2,1. The sum of counts equals input length for every fixture.

```python
def frequencies(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

get supplies zero only for a previously unseen key, then every occurrence increments its count. Updating an existing dictionary entry does not move its insertion position in the supported Python versions. The count-sum invariant catches accidental dropping or double-counting, while the explicit key-order assertion checks a different part of the contract. A set would preserve neither multiplicity nor this presentation policy.

```python
values_3 = ["b", "a", "b", "c", "a", "b"]
result_3 = frequencies(values_3)
assert list(result_3) == ["b", "a", "c"] and result_3 == {"b": 3, "a": 2, "c": 1}
assert sum(result_3.values()) == len(values_3) and frequencies([]) == {}
```

### Exercise 4: Reconcile occurrences in both directions

Return sorted string keys whose left count minus right count is nonzero. Preserve negative differences as well as positive ones. Do not mutate either list.

**Expected:** [a, a, b] versus[a, b, b] returns{a:1, b:-1}; identical bags with different order return{}; an empty left versus[x, x] gives{x:-2}.

```python
def bag_difference(left: list[str], right: list[str]) -> dict[str, int]:
    a = Counter(left)
    b = Counter(right)
    return {key: a[key] - b[key] for key in sorted(a.keys() | b.keys()) if a[key] != b[key]}
```

The union of keys includes values present on only one side, and Counter returns zero for absent keys. Explicit signed subtraction is required because Counter's subtraction operator discards zero and negative counts. Sorting keys makes the diagnostic deterministic without changing bag semantics. Equality of total lengths is insufficient: a missing occurrence of one value can be offset by an extra occurrence of another.

```python
assert bag_difference(["a", "a", "b"], ["a", "b", "b"]) == {"a": 1, "b": -1}
assert bag_difference(["b", "a"], ["a", "b"]) == {}
assert bag_difference([], ["x", "x"]) == {"x": -2}
```

### Exercise 5: Index every occurrence instead of overwriting

Build a key-to-list-of-positions index for string values. Preserve positions in ascending encounter order and keys in first-appearance order. Empty input returns{}.

**Expected:** [a, b, a] yields{a:[0,2], b:[1]}. Every input position occurs exactly once among index lists, including repeated keys.

```python
def position_index(values: list[str]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for position, value in enumerate(values):
        index.setdefault(value, []).append(position)
    return index
```

A single-value dictionary assignment would overwrite the earlier position of a, losing a legitimate occurrence. A list at each key retains all matches and therefore supports duplicate-aware joins. The flattened-position invariant verifies that indexing neither loses nor invents rows. Memory is linear in the input size because every position is stored once, even if the number of distinct keys is much smaller.

```python
values_5 = ["a", "b", "a"]
result_5 = position_index(values_5)
assert result_5 == {"a": [0, 2], "b": [1]} and list(result_5) == ["a", "b"]
assert sorted(position for positions in result_5.values() for position in positions) == list(
    range(len(values_5))
)
assert position_index([]) == {}
```

### Exercise 6: Produce an output-sensitive equality join

Return every matching(left_position, right_position) pair using a hash index of right. Order results by left encounter position, then right encounter position. Preserve duplicate matches and inputs; do not compare every unrelated pair.

**Expected:** Left[a, a, b], right[a, b, a] yields [(0,0),(0,2),(1,0),(1,2),(2,1)]. No common keys gives []; two repeated left and right a values produce four pairs.

```python
def indexed_pairs(left: list[str], right: list[str]) -> list[tuple[int, int]]:
    index = position_index(right)
    result = []
    for left_position, value in enumerate(left):
        for right_position in index.get(value, []):
            result.append((left_position, right_position))
    return result
```

Building the right index costs expected linear work, and probing it costs expected linear work in left size plus the number of emitted matches. The output can still be quadratic when every key repeats on both sides, because those pairs are genuinely required. This explains why an efficient hash join does not make an unintended many-to-many relationship harmless. Complexity and row-grain correctness must both be reviewed.

```python
assert indexed_pairs(["a", "a", "b"], ["a", "b", "a"]) == [
    (0, 0),
    (0, 2),
    (1, 0),
    (1, 2),
    (2, 1),
]
assert indexed_pairs(["a"], ["b"]) == []
assert len(indexed_pairs(["a", "a"], ["a", "a"])) == 4
assert indexed_pairs([], []) == []
```

## Verification and interpretation

Run `python python/professional/solutions/py_algo_01_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
