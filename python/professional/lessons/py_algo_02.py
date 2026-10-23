"""python-algo-02: Stable Ordering, Binary-Search Boundaries, and Merge Algorithms.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

from bisect import bisect_left, bisect_right

def stable_score_order(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Return a new list ordered by integer score ascending while preserving input order among equal scores. Do not use the label as a secondary key and do not mutate records."""
    raise NotImplementedError("Implement stable_score_order")

def lower_bound(values: list[int], target: int) -> int:
    """Implement a manual logarithmic lower-bound search on an already sorted integer list. Return the first index with value>=target, or len(values). Do not linearly scan or call bisect inside the implementation. Sortedness is an explicit caller precondition."""
    raise NotImplementedError("Implement lower_bound")

def upper_bound(values: list[int], target: int) -> int:
    """Implement a manual logarithmic upper-bound search on an already sorted integer list. Return the first index with value>target, or len(values). Preserve input and avoid a linear duplicate scan."""
    raise NotImplementedError("Implement upper_bound")

def count_closed_range(values: list[int], lower: int, upper: int) -> int:
    """Count values in the closed numeric interval[lower, upper] using the manual lower_bound and upper_bound functions. Assume sorted integer input and reject lower>upper with ValueError. Do not scan the full list."""
    raise NotImplementedError("Implement count_closed_range")

def merge_runs(left: list[tuple[int, str]], right: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Merge two score-sorted record lists in linear work, selecting the left record first on equal scores. Preserve input lists and reject a run whose scores decrease with ValueError. Empty runs are valid."""
    raise NotImplementedError("Implement merge_runs")

def merge_sort(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Implement bottom-up merge sort by starting with singleton runs and repeatedly merging adjacent pairs using merge_runs. Do not call sorted or list.sort in this function. Preserve input, stability and an odd final run at each level."""
    raise NotImplementedError("Implement merge_sort")

def worked_examples():
    records=[(2,"z"),(1,"b"),(2,"a")]
    ordered=sorted(records,key=lambda record:record[0])
    assert ordered==[(1,"b"),(2,"z"),(2,"a")]
    assert sorted(records)!=ordered
    print("Stable score order:",ordered)

    values=[1,2,2,2,5]
    start=bisect_left(values,2);stop=bisect_right(values,2)
    assert (start,stop)==(1,4) and stop-start==3
    assert bisect_left(values,9)==len(values)
    print("Equal-value half-open range:",start,stop)

if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Keep identities stable on ties
# Prompt: Return a new list ordered by integer score ascending while preserving input order among equal scores. Do not use the label as a secondary key and do not mutate records.
# Expected: [(2, z),(1, b),(2, a)] becomes[(1, b),(2, z),(2, a)], not alphabetical tie order. Empty input returns a new empty list.

# Exercise 2: Find the first not-less boundary
# Prompt: Implement a manual logarithmic lower-bound search on an already sorted integer list. Return the first index with value>=target, or len(values). Do not linearly scan or call bisect inside the implementation. Sortedness is an explicit caller precondition.
# Expected: [1,2,2,5] at target 2 returns 1; target 0 returns 0; target 9 returns 4. Empty input returns 0. Compare every target 0..6 against bisect_left.

# Exercise 3: Move past all equal values
# Prompt: Implement a manual logarithmic upper-bound search on an already sorted integer list. Return the first index with value>target, or len(values). Preserve input and avoid a linear duplicate scan.
# Expected: [1,2,2,5] at target 2 returns 3; an all-two list of length 3 returns 3; empty returns 0. Results match bisect_right across several targets.

# Exercise 4: Count an inclusive interval using boundaries
# Prompt: Count values in the closed numeric interval[lower, upper] using the manual lower_bound and upper_bound functions. Assume sorted integer input and reject lower>upper with ValueError. Do not scan the full list.
# Expected: [1,2,2,5,7] over [2,5] returns 3; [3,4] returns 0; [2,2] returns 2. Empty input returns 0 and reversed bounds fail.

# Exercise 5: Merge sorted runs stably
# Prompt: Merge two score-sorted record lists in linear work, selecting the left record first on equal scores. Preserve input lists and reject a run whose scores decrease with ValueError. Empty runs are valid.
# Expected: Left[(1, L1),(2, L2)] and right[(1, R1),(3, R3)] yield [(1, L1),(1, R1),(2, L2),(3, R3)]. A reversed-score run fails.

# Exercise 6: Build stable sorting from repeated merges
# Prompt: Implement bottom-up merge sort by starting with singleton runs and repeatedly merging adjacent pairs using merge_runs. Do not call sorted or list.sort in this function. Preserve input, stability and an odd final run at each level.
# Expected: [(3, a),(1, b),(2, c),(1, d),(0, e)] becomes[(0, e),(1, b),(1, d),(2, c),(3, a)]. Empty and singleton inputs work; results match stable_score_order.
