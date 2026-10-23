"""python-algo-01: Algorithmic Cost, Hash Indexes, and Duplicate-Aware Matching.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

from collections import Counter

def pair_comparisons(size: int) -> int:
    """Count unordered distinct index pairs with explicit nested loops, requiring a nonnegative non-Boolean integer size. Return the number of pair visits. Compare the result with n*(n-1)//2; do not use the formula as the implementation."""
    raise NotImplementedError("Implement pair_comparisons")

def first_duplicate(values: list[int]) -> int | None:
    """Scan integer values left to right and return the value whose repeated occurrence is encountered first. Return None when all values are distinct. Preserve input and distinguish a duplicate zero from no duplicate."""
    raise NotImplementedError("Implement first_duplicate")

def frequencies(values: list[str]) -> dict[str, int]:
    """Return a dictionary of occurrence counts for string values in first-appearance order. Do not remove repeated values or sort the input. Empty input returns an empty dictionary."""
    raise NotImplementedError("Implement frequencies")

def bag_difference(left: list[str], right: list[str]) -> dict[str, int]:
    """Return sorted string keys whose left count minus right count is nonzero. Preserve negative differences as well as positive ones. Do not mutate either list."""
    raise NotImplementedError("Implement bag_difference")

def position_index(values: list[str]) -> dict[str, list[int]]:
    """Build a key-to-list-of-positions index for string values. Preserve positions in ascending encounter order and keys in first-appearance order. Empty input returns{}."""
    raise NotImplementedError("Implement position_index")

def indexed_pairs(left: list[str], right: list[str]) -> list[tuple[int, int]]:
    """Return every matching(left_position, right_position) pair using a hash index of right. Order results by left encounter position, then right encounter position. Preserve duplicate matches and inputs; do not compare every unrelated pair."""
    raise NotImplementedError("Implement indexed_pairs")

def worked_examples():
    for n in [4,8]:
        comparisons=sum(1 for i in range(n) for j in range(i+1,n))
        assert comparisons==n*(n-1)//2
        print("Distinct pairs:",n,comparisons)

    left=Counter(["a","a","b"]);right=Counter(["a","b","b"])
    difference={key:left[key]-right[key] for key in sorted(left.keys()|right.keys()) if left[key]!=right[key]}
    assert difference=={"a":1,"b":-1}
    assert set(left)==set(right)
    print("Bag difference:",difference)

if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Count work rather than guessing from timing
# Prompt: Count unordered distinct index pairs with explicit nested loops, requiring a nonnegative non-Boolean integer size. Return the number of pair visits. Compare the result with n*(n-1)//2; do not use the formula as the implementation.
# Expected: Sizes 0,1,4,8 return 0,0,6,28. Negative size, True and 2.5 raise ValueError.

# Exercise 2: Return the first repeated occurrence
# Prompt: Scan integer values left to right and return the value whose repeated occurrence is encountered first. Return None when all values are distinct. Preserve input and distinguish a duplicate zero from no duplicate.
# Expected: [4,1,4,1] returns 4, [1,2,2,1] returns 2, [0,0] returns 0 and [] returns None.

# Exercise 3: Build counts while preserving first appearance
# Prompt: Return a dictionary of occurrence counts for string values in first-appearance order. Do not remove repeated values or sort the input. Empty input returns an empty dictionary.
# Expected: [b, a, b, c, a, b] yields insertion order[b, a, c] and counts 3,2,1. The sum of counts equals input length for every fixture.

# Exercise 4: Reconcile occurrences in both directions
# Prompt: Return sorted string keys whose left count minus right count is nonzero. Preserve negative differences as well as positive ones. Do not mutate either list.
# Expected: [a, a, b] versus[a, b, b] returns{a:1, b:-1}; identical bags with different order return{}; an empty left versus[x, x] gives{x:-2}.

# Exercise 5: Index every occurrence instead of overwriting
# Prompt: Build a key-to-list-of-positions index for string values. Preserve positions in ascending encounter order and keys in first-appearance order. Empty input returns{}.
# Expected: [a, b, a] yields{a:[0,2], b:[1]}. Every input position occurs exactly once among index lists, including repeated keys.

# Exercise 6: Produce an output-sensitive equality join
# Prompt: Return every matching(left_position, right_position) pair using a hash index of right. Order results by left encounter position, then right encounter position. Preserve duplicate matches and inputs; do not compare every unrelated pair.
# Expected: Left[a, a, b], right[a, b, a] yields [(0,0),(0,2),(1,0),(1,2),(2,1)]. No common keys gives []; two repeated left and right a values produce four pairs.
