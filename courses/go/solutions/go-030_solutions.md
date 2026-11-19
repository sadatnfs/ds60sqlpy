# go-030: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Performance work starts with a behavioral contract and representative input. Complexity predicts growth in work, while a benchmark measures a particular implementation and environment. A linear scan visits each item; binary search repeatedly narrows a sorted interval. Faster execution is useful only if it preserves the result and failure policy. Preallocating slice capacity can avoid growth allocations, but preallocating length creates real zero elements. Tiny timings are noisy. Separate setup from measurement, repeat a representative workload, record environment and check results outside the timing loop. A profile should answer a hypothesis about where time or allocations are spent.

sort.Search finds the first index where a monotone predicate becomes true, or n when none does. It does not sort or validate input. make([]int,0,n) reserves capacity with zero length; make([]int,n) creates n elements. Prepared project benchmarks use testing.B in _test.go files; pprof investigates CPU or allocation evidence rather than establishing a universal speed ranking.

## 1. Find a lower boundary: change one input

Copy worked example 1 into a scratch pad and change `items := []int{2, 4, 6, 8}` to `items := []int{2, 5, 6, 8}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
items := []int{2, 4, 6, 8}
i := sort.Search(len(items), func(i int) bool { return items[i] >= 5 })
check(i == 2, "boundary")
```

**Expected:** The changed run panics with `boundary` because `i == 2` no longer holds. Restoring the original line brings back the worked observation: the index is 2.

Sorting makes the predicate monotone. The same expression over unsorted input violates the algorithm precondition.

## 2. Represent no match: debug a regression

A regression changed one token in worked example 2, so one line now reads `items := []int{2, 4, 6, 9}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
items := []int{2, 4, 6, 8}
i := sort.Search(len(items), func(i int) bool { return items[i] >= 9 })
check(i == len(items), "not found")
```

**Expected:** Before the repair the program panics with `not found`; after it the line reads `items := []int{2, 4, 6, 8}` again and the index equals the collection length.

The sentinel is not a valid element index. Check it before indexing.

## 3. Separate length and capacity

Reserve capacity four, then append one value.

```go
items := make([]int, 0, 4)
items = append(items, 7)
check(len(items) == 1 && cap(items) == 4 && items[0] == 7, "capacity")
```

**Expected:** Length is 1, capacity is 4.

Starting with length four would create four logical zeros before the appended value.

## 4. Count linear work

Sum five values and count visits.

```go
visits, sum := 0, 0
for _, v := range []int{1, 2, 3, 4, 5} {
	visits++
	sum += v
}
check(visits == 5 && sum == 15, "work")
```

**Expected:** There are five visits and the sum is 15.

Operation counting supplies structural evidence without inventing a universal wall-clock threshold.

## 5. Handle empty search

Search a zero-length interval.

```go
calls := 0
i := sort.Search(0, func(i int) bool { calls++; return true })
check(i == 0 && calls == 0, "empty")
```

**Expected:** Index is 0 and the predicate is never called.

The empty interval has a valid insertion position without accessing any element.

## 6. Transfer duplicate boundaries

Find the first value at least 3 in 1, 3, 3, 5.

```go
items := []int{1, 3, 3, 5}
i := sort.Search(len(items), func(i int) bool { return items[i] >= 3 })
check(i == 1, "duplicates")
```

**Expected:** The first duplicate has index 1.

A lower bound is more precise than any matching index. That contract supports insertion and range queries.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
