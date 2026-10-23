# python-algo-02: Explained reference solutions

These answers implement the contracts in [Stable Ordering, Binary-Search Boundaries, and Merge Algorithms](../companion-guides/py_algo_02.md). Compare after an attempt. The [executable reference](py_algo_02_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Keep identities stable on ties

Return a new list ordered by integer score ascending while preserving input order among equal scores. Do not use the label as a secondary key and do not mutate records.

**Expected:** [(2, z),(1, b),(2, a)] becomes[(1, b),(2, z),(2, a)], not alphabetical tie order. Empty input returns a new empty list.

```python
def stable_score_order(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return sorted(records,key=lambda record:record[0])
```

The key function exposes only the intended comparison field. Python's stable sort then preserves equal-key encounter order without inventing a label-based policy. sorted constructs a new list, so callers retain their original ordering. The test checks both tie identities and source preservation, since comparing only the sequence of scores would miss an unstable but numerically sorted output.

```python
records=[(2,"z"),(1,"b"),(2,"a")];original=records.copy()
assert stable_score_order(records)==[(1,"b"),(2,"z"),(2,"a")] and records==original
empty=[]
assert stable_score_order(empty)==[] and stable_score_order(empty) is not empty
```

### Exercise 2: Find the first not-less boundary

Implement a manual logarithmic lower-bound search on an already sorted integer list. Return the first index with value>=target, or len(values). Do not linearly scan or call bisect inside the implementation. Sortedness is an explicit caller precondition.

**Expected:** [1,2,2,5] at target 2 returns 1; target 0 returns 0; target 9 returns 4. Empty input returns 0. Compare every target 0..6 against bisect_left.

```python
def lower_bound(values: list[int], target: int) -> int:
    lo,hi=0,len(values)
    while lo<hi:
        mid=(lo+hi)//2
        if values[mid]<target:
            lo=mid+1
        else:
            hi=mid
    return lo
```

The half-open interval never requires reading position len(values). Moving lo past a smaller midpoint proves that every removed position is too small; moving hi to the midpoint retains a possible first qualifying position. Equal values therefore move the upper boundary left, finding the first duplicate. The standard-library comparison is an independent oracle across below-range, inside-range and above-range targets.

```python
values=[1,2,2,5]
assert lower_bound(values,2)==1 and lower_bound(values,0)==0 and lower_bound(values,9)==4
assert lower_bound([],2)==0
for target in range(7):
    assert lower_bound(values,target)==bisect_left(values,target)
```

### Exercise 3: Move past all equal values

Implement a manual logarithmic upper-bound search on an already sorted integer list. Return the first index with value>target, or len(values). Preserve input and avoid a linear duplicate scan.

**Expected:** [1,2,2,5] at target 2 returns 3; an all-two list of length 3 returns 3; empty returns 0. Results match bisect_right across several targets.

```python
def upper_bound(values: list[int], target: int) -> int:
    lo,hi=0,len(values)
    while lo<hi:
        mid=(lo+hi)//2
        if values[mid]<=target:
            lo=mid+1
        else:
            hi=mid
    return lo
```

The only changed comparison is equality ownership. Values equal to target now belong before lo, so the search advances beyond the entire equal run. A separate scan after finding one duplicate could degrade to linear time for an all-equal list; binary upper bound retains logarithmic search work. The empty-list result follows the same invariant without a special indexing branch.

```python
values=[1,2,2,5]
assert upper_bound(values,2)==3 and upper_bound([2,2,2],2)==3 and upper_bound([],2)==0
for target in range(7):
    assert upper_bound(values,target)==bisect_right(values,target)
```

### Exercise 4: Count an inclusive interval using boundaries

Count values in the closed numeric interval[lower, upper] using the manual lower_bound and upper_bound functions. Assume sorted integer input and reject lower>upper with ValueError. Do not scan the full list.

**Expected:** [1,2,2,5,7] over [2,5] returns 3; [3,4] returns 0; [2,2] returns 2. Empty input returns 0 and reversed bounds fail.

```python
def count_closed_range(values: list[int], lower: int, upper: int) -> int:
    if lower>upper:
        raise ValueError("Range lower bound must not exceed upper bound")
    return upper_bound(values,upper)-lower_bound(values,lower)
```

The first boundary excludes everything below lower, while the second includes all values equal to upper before stopping. Their difference counts the interval without examining each matching element. Using lower_bound for both endpoints would incorrectly exclude the upper endpoint. The equal-endpoint case is therefore an important independent check, especially when many duplicate values lie on that boundary.

```python
values=[1,2,2,5,7]
assert count_closed_range(values,2,5)==3 and count_closed_range(values,3,4)==0
assert count_closed_range(values,2,2)==2 and count_closed_range([],0,9)==0
expect_value_error(lambda:count_closed_range(values,5,2))
```

### Exercise 5: Merge sorted runs stably

Merge two score-sorted record lists in linear work, selecting the left record first on equal scores. Preserve input lists and reject a run whose scores decrease with ValueError. Empty runs are valid.

**Expected:** Left[(1, L1),(2, L2)] and right[(1, R1),(3, R3)] yield [(1, L1),(1, R1),(2, L2),(3, R3)]. A reversed-score run fails.

```python
def merge_runs(left: list[tuple[int, str]], right: list[tuple[int, str]]) -> list[tuple[int, str]]:
    for run in [left,right]:
        if any(run[index][0]>run[index+1][0] for index in range(len(run)-1)):
            raise ValueError("Each input run must be sorted by score")
    i=j=0;result=[]
    while i<len(left) and j<len(right):
        if left[i][0]<=right[j][0]:
            result.append(left[i]);i+=1
        else:
            result.append(right[j]);j+=1
    result.extend(left[i:]);result.extend(right[j:])
    return result
```

Each comparison advances exactly one cursor, so no item is repeatedly searched. The <= tie rule takes left-run records before equal right-run records and preserves their earlier global order when the runs came from adjacent input slices. Extending the remaining suffix is safe because it is already sorted. Checking each run adds only linear work and catches a broken precondition before producing a misleading combined order.

```python
left=[(1,"L1"),(2,"L2")];right=[(1,"R1"),(3,"R3")]
assert merge_runs(left,right)==[(1,"L1"),(1,"R1"),(2,"L2"),(3,"R3")]
assert left==[(1,"L1"),(2,"L2")] and merge_runs([],right)==right
expect_value_error(lambda:merge_runs([(2,"a"),(1,"b")],[]))
```

### Exercise 6: Build stable sorting from repeated merges

Implement bottom-up merge sort by starting with singleton runs and repeatedly merging adjacent pairs using merge_runs. Do not call sorted or list.sort in this function. Preserve input, stability and an odd final run at each level.

**Expected:** [(3, a),(1, b),(2, c),(1, d),(0, e)] becomes[(0, e),(1, b),(1, d),(2, c),(3, a)]. Empty and singleton inputs work; results match stable_score_order.

```python
def merge_sort(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    runs=[[record] for record in records]
    if not runs:
        return []
    while len(runs)>1:
        next_runs=[]
        for index in range(0,len(runs),2):
            next_runs.append(merge_runs(runs[index],runs[index+1]) if index+1<len(runs) else runs[index])
        runs=next_runs
    return runs[0]
```

Singleton runs are sorted by definition. Each merge preserves sortedness and stability, so induction over the rounds establishes the final result. Runs approximately double in length per round, producing logarithmically many rounds with linear total work per round. Carrying an unpaired final run prevents odd-length inputs from losing records. The generated deterministic fixtures vary both length and repeated-key structure, exposing mistakes that a single already-sorted list would hide.

```python
records=[(3,"a"),(1,"b"),(2,"c"),(1,"d"),(0,"e")]
assert merge_sort(records)==[(0,"e"),(1,"b"),(1,"d"),(2,"c"),(3,"a")]
assert merge_sort(records)==stable_score_order(records) and records[0]==(3,"a")
assert merge_sort([])==[] and merge_sort([(1,"x")])==[(1,"x")]
for size in range(12):
    sample=[(index%3,str(index)) for index in range(size-1,-1,-1)]
    assert merge_sort(sample)==stable_score_order(sample)
```

## Verification and interpretation

Run `python python/professional/solutions/py_algo_02_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
