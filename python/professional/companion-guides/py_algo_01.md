# Algorithmic Cost, Hash Indexes, and Duplicate-Aware Matching

**Stable ID:** `python-algo-01`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-06`, `python-10`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Open the [learner script](../lessons/py_algo_01.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_algo_01.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_algo_01.py
```

Dependencies: Python standard library. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_algo_01_solutions.md) and [runnable reference](../solutions/py_algo_01_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Time complexity:** How an operation count grows with input size under a stated cost model, rather than one elapsed-time measurement.

- **Hash table:** A structure using hash values to locate keys efficiently on average, while still comparing keys for equality.

- **Bag or multiset:** A collection in which repeated occurrences matter, unlike a set that records only membership.

- **Output-sensitive cost:** A complexity bound that includes the number of result records that must actually be produced.

Algorithm analysis starts with the operation that dominates work. A loop comparing every distinct pair of n items performs n*(n-1)/2 comparisons, so doubling n roughly quadruples work. A single pass that updates a dictionary usually performs work proportional to n under ordinary average-case hash assumptions. Timing a five-row example is too noisy to establish that difference; counting operations makes the mechanism visible.

Big-O notation describes an upper growth rate, not an exact number of seconds. Constant factors, memory layout, Python overhead and input distributions still matter. Expected constant-time hash lookup is not a guarantee against every collision pattern or arbitrary key implementation. Hashability also does not imply a key is the correct business identity. A rounded measurement is a poor identifier even if Python accepts it as a dictionary key.

Duplicate-aware matching connects algorithms to data engineering. Building a dictionary from key to one row silently overwrites previous rows for that key. If repetitions are legitimate, build key-to-list-of-positions instead. A join then returns every left-right occurrence pair. Two left rows and three right rows for one key produce six pairs. A hash index avoids unnecessary comparisons but cannot eliminate output that the relationship actually requires.

Sets and bags answer different reconciliation questions. If one extract contains [a, a, b] and another[a, b, b], their sets are equal but their occurrence counts differ. A signed count difference reports a:+1, b:-1. This is the algorithmic counterpart of SQL EXCEPT ALL and explains why deduplicating before comparison can hide data loss or repeated ingestion.

Ordering is a separate contract. Python dictionaries preserve insertion order in the supported versions, so a frequency table can preserve first appearance. A diagnostic report may instead sort keys for reproducibility. State that choice rather than allowing a set's iteration order to determine learner-visible output.

The exercises move from explicit comparison counting to hash counting, duplicate detection, bag reconciliation and an indexed join. They keep inputs unchanged and use small counterexamples where a tempting faster-looking implementation loses information. The goal is choosing a data structure that preserves semantics before optimizing a loop.

## Worked examples and syntax anatomy

### Example 1

```python
for n in [4, 8]:
    comparisons = sum(1 for i in range(n) for j in range(i + 1, n))
    assert comparisons == n * (n - 1) // 2
    print("Distinct pairs:", n, comparisons)
```

The inner range starts after i, so each unordered pair is counted once and self-pairs are excluded. Four items produce six comparisons; eight produce 28. The count demonstrates quadratic growth without depending on processor speed or timing noise.

### Example 2

```python
left = Counter(["a", "a", "b"])
right = Counter(["a", "b", "b"])
difference = {
    key: left[key] - right[key]
    for key in sorted(left.keys() | right.keys())
    if left[key] != right[key]
}
assert difference == {"a": 1, "b": -1}
assert set(left) == set(right)
print("Bag difference:", difference)
```

Equal membership sets conceal changed multiplicity. Counter stores counts, and the signed difference preserves which side has an extra occurrence. Ordinary Counter subtraction drops nonpositive results, so explicitly subtracting per key is necessary for a two-direction diagnostic.

## Exercises

1. **Count work rather than guessing from timing.** Count unordered distinct index pairs with explicit nested loops, requiring a nonnegative non-Boolean integer size. Return the number of pair visits. Compare the result with n*(n-1)//2; do not use the formula as the implementation.

**Expected:** Sizes 0,1,4,8 return 0,0,6,28. Negative size, True and 2.5 raise ValueError.

2. **Return the first repeated occurrence.** Scan integer values left to right and return the value whose repeated occurrence is encountered first. Return None when all values are distinct. Preserve input and distinguish a duplicate zero from no duplicate.

**Expected:** [4,1,4,1] returns 4, [1,2,2,1] returns 2, [0,0] returns 0 and [] returns None.

3. **Build counts while preserving first appearance.** Return a dictionary of occurrence counts for string values in first-appearance order. Do not remove repeated values or sort the input. Empty input returns an empty dictionary.

**Expected:** [b, a, b, c, a, b] yields insertion order[b, a, c] and counts 3,2,1. The sum of counts equals input length for every fixture.

4. **Reconcile occurrences in both directions.** Return sorted string keys whose left count minus right count is nonzero. Preserve negative differences as well as positive ones. Do not mutate either list.

**Expected:** [a, a, b] versus[a, b, b] returns{a:1, b:-1}; identical bags with different order return{}; an empty left versus[x, x] gives{x:-2}.

5. **Index every occurrence instead of overwriting.** Build a key-to-list-of-positions index for string values. Preserve positions in ascending encounter order and keys in first-appearance order. Empty input returns{}.

**Expected:** [a, b, a] yields{a:[0,2], b:[1]}. Every input position occurs exactly once among index lists, including repeated keys.

6. **Produce an output-sensitive equality join.** Return every matching(left_position, right_position) pair using a hash index of right. Order results by left encounter position, then right encounter position. Preserve duplicate matches and inputs; do not compare every unrelated pair.

**Expected:** Left[a, a, b], right[a, b, a] yields [(0,0),(0,2),(1,0),(1,2),(2,1)]. No common keys gives []; two repeated left and right a values produce four pairs.

## Common mistakes and diagnosis

If a reconciliation says equal while counts differ, inspect whether a set replaced a multiset. If an index loses earlier rows, check for assigning one row per key instead of appending occurrences. If a supposedly linear join produces huge output, calculate per-key left_count*right_count before blaming the hash table. If duplicate zero is reported as absent, inspect truthiness checks and use an explicit None sentinel. If a benchmark contradicts asymptotic reasoning on tiny inputs, measure larger controlled inputs and operation counts before drawing a general conclusion.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [Python mapping types and dictionary behavior](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict).

- [Python Counter](https://docs.python.org/3/library/collections.html#collections.Counter).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-01: Algorithmic Cost, Hash Indexes, and Duplicate-Aware Matching.
Read python/professional/companion-guides/py_algo_01.md and python/professional/lessons/py_algo_01.py. Direct prerequisites: python-06, python-10.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
