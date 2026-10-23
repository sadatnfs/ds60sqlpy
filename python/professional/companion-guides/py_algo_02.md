# Stable Ordering, Binary-Search Boundaries, and Merge Algorithms

**Stable ID:** `python-algo-02`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-algo-01`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

Open the [learner script](../lessons/py_algo_02.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_algo_02.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_algo_02.py
```

Dependencies: Python standard library. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_algo_02_solutions.md) and [runnable reference](../solutions/py_algo_02_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Stable ordering:** An ordering that preserves the original relative positions of records whose comparison keys are equal.

- **Lower bound:** The first position where a sorted sequence value is not less than the target, or the sequence length if all are smaller.

- **Upper bound:** The first position where a sorted sequence value is greater than the target, identifying the far edge of an equal-value run.

- **Loop invariant:** A statement that remains true before and after each loop iteration and explains why the final result is correct.

Sorting and searching are contracts about order, equality and identity. Sorting full tuples can add an unintended tie break from later fields. If the requirement is ascending score while preserving the arrival order of equal scores, use only score as the key and a stable algorithm. A deterministic order is not necessarily the desired stable order; alphabetically breaking ties changes the policy.

Binary search relies on sorted input. The lesson's search functions assume the caller already established that precondition. Checking sortedness on every call would take linear work and erase the benefit of repeated logarithmic searches. A production boundary can validate once, store an immutable sorted sequence, then perform many queries. If the data changes, the ordering guarantee must be renewed.

For a lower-bound search, maintain a half-open candidate interval[lo, hi). Everything before lo is less than the target, and everything at or after hi is not less. At the midpoint, a value smaller than target moves lo to mid+1; otherwise hi moves to mid. Each step shrinks the interval, and when lo equals hi that position is the first valid insertion point. The result can be zero or len(values), so indexing it without checking bounds is unsafe.

Upper bound changes the comparison to move past values equal to the target. Together the two boundaries count duplicates or values inside a closed numeric interval without scanning every match. Equality handling is not a cosmetic operator choice; it determines which side owns an endpoint.

Merge algorithms combine two sorted runs by repeatedly taking the smaller front item. On equal keys, choosing from the left run first preserves stability if each run was already stable. Each item is consumed once, so merging costs linear work in total run length. Repeatedly merging runs doubles their size each round and gives merge sort its O(n log n) time bound.

The exercises use records(score, label) to keep identity visible when scores tie. Search fixtures include empty arrays, all-equal runs and targets outside the range. Reference checks compare manual binary-search results with standard-library bisect on deterministic cases, and compare the handwritten merge sort with Python's stable sorted result. Correctness is established by values, identity order and preserved inputs, not one happy-path printout.

## Worked examples and syntax anatomy

### Example 1

```python
records = [(2, "z"), (1, "b"), (2, "a")]
ordered = sorted(records, key=lambda record: record[0])
assert ordered == [(1, "b"), (2, "z"), (2, "a")]
assert sorted(records) != ordered
print("Stable score order:", ordered)
```

Sorting by the whole tuple uses label as a second key and puts a before z. Sorting only by score preserves z before a because that was their input order. The tuple labels make a stability requirement observable even when tied score values are identical.

### Example 2

```python
values = [1, 2, 2, 2, 5]
start = bisect_left(values, 2)
stop = bisect_right(values, 2)
assert (start, stop) == (1, 4) and stop - start == 3
assert bisect_left(values, 9) == len(values)
print("Equal-value half-open range:", start, stop)
```

The equal run occupies positions 1,2,3, represented by the half-open interval[1,4). An insertion point at the end is valid even though it cannot be indexed as an existing element. This distinction prevents common off-by-one and IndexError failures.

## Exercises

1. **Keep identities stable on ties.** Return a new list ordered by integer score ascending while preserving input order among equal scores. Do not use the label as a secondary key and do not mutate records.

**Expected:** [(2, z),(1, b),(2, a)] becomes[(1, b),(2, z),(2, a)], not alphabetical tie order. Empty input returns a new empty list.

2. **Find the first not-less boundary.** Implement a manual logarithmic lower-bound search on an already sorted integer list. Return the first index with value>=target, or len(values). Do not linearly scan or call bisect inside the implementation. Sortedness is an explicit caller precondition.

**Expected:** [1,2,2,5] at target 2 returns 1; target 0 returns 0; target 9 returns 4. Empty input returns 0. Compare every target 0..6 against bisect_left.

3. **Move past all equal values.** Implement a manual logarithmic upper-bound search on an already sorted integer list. Return the first index with value>target, or len(values). Preserve input and avoid a linear duplicate scan.

**Expected:** [1,2,2,5] at target 2 returns 3; an all-two list of length 3 returns 3; empty returns 0. Results match bisect_right across several targets.

4. **Count an inclusive interval using boundaries.** Count values in the closed numeric interval[lower, upper] using the manual lower_bound and upper_bound functions. Assume sorted integer input and reject lower>upper with ValueError. Do not scan the full list.

**Expected:** [1,2,2,5,7] over [2,5] returns 3; [3,4] returns 0; [2,2] returns 2. Empty input returns 0 and reversed bounds fail.

5. **Merge sorted runs stably.** Merge two score-sorted record lists in linear work, selecting the left record first on equal scores. Preserve input lists and reject a run whose scores decrease with ValueError. Empty runs are valid.

**Expected:** Left[(1, L1),(2, L2)] and right[(1, R1),(3, R3)] yield [(1, L1),(1, R1),(2, L2),(3, R3)]. A reversed-score run fails.

6. **Build stable sorting from repeated merges.** Implement bottom-up merge sort by starting with singleton runs and repeatedly merging adjacent pairs using merge_runs. Do not call sorted or list.sort in this function. Preserve input, stability and an odd final run at each level.

**Expected:** [(3, a),(1, b),(2, c),(1, d),(0, e)] becomes[(0, e),(1, b),(1, d),(2, c),(3, a)]. Empty and singleton inputs work; results match stable_score_order.

## Common mistakes and diagnosis

If binary search loops forever, inspect whether every branch strictly shrinks[lo, hi). If the result points past the end, treat it as an insertion boundary rather than indexing immediately. If duplicate counts are off by one, compare lower and upper equality rules. If sorted output reverses equal-key labels, inspect a secondary tuple key or the merge tie condition. If odd-length merge sort loses a record, trace the final unpaired run. Validate sortedness once at the data boundary for repeated searches rather than hiding an O(n) scan inside a supposedly O(log n) query.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [Python sorting stability](https://docs.python.org/3/howto/sorting.html).

- [Python bisect boundary semantics](https://docs.python.org/3/library/bisect.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-02: Stable Ordering, Binary-Search Boundaries, and Merge Algorithms.
Read python/professional/companion-guides/py_algo_02.md and python/professional/lessons/py_algo_02.py. Direct prerequisites: python-algo-01.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
