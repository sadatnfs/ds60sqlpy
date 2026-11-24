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

**Approach.** Evaluate the predicate `items[i] >= 5` over the edited sorted slice `2, 5, 6, 8`: it is false at index 0 and true from index 1, so `sort.Search` returns 1.

**Why it holds here.** `sort.Search` returns the smallest index where a monotone predicate becomes true. The new 5 itself satisfies `>= 5`, so the boundary moves left and `i == 2` panics with `boundary`.

**A plausible wrong approach.** Reading the predicate as "greater than 5" and predicting 2 again. With `>=` the element equal to the target counts, which is exactly what makes this a lower bound.

**Verify.** Print `i` and see 1 before the panic; the restored input prints 2.

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

**Approach.** Search the regressed slice `2, 4, 6, 9` for the first value at least 9. The predicate is true at index 3, so the result is 3, not the not-found position 4.

**Why it holds here.** The check encodes that 9 is absent from the original data, so the expected answer is `len(items)`. The regression placed a 9 in the slice, and restoring 8 makes the predicate false everywhere and returns 4.

**A plausible wrong approach.** Using the result as an element index without checking it, as in `found := items[i] == 9`. With the repaired data `i` is 4 and that line panics with `index out of range [4] with length 4`.

**Verify.** Print `i, len(items)` and see `3 4` for the regression and `4 4` after the repair.

## 3. Separate length and capacity

Reserve capacity four, then append one value.

```go
items := make([]int, 0, 4)
items = append(items, 7)
check(len(items) == 1 && cap(items) == 4 && items[0] == 7, "capacity")
```

**Expected:** Length is 1, capacity is 4.

Starting with length four would create four logical zeros before the appended value.

**Approach.** Allocate with `make([]int, 0, 4)` so the slice starts empty with room for four, then append 7 into the first slot.

**Why it holds here.** Append writes into existing capacity without reallocating, so length becomes 1, capacity stays 4 and `items[0]` is 7.

**A plausible wrong approach.** Writing `make([]int, 4)` and then appending. The slice already holds four zeros, so the append produces `[0 0 0 0 7]` with length 5 and a reallocated capacity of 8, and the check panics with `capacity`.

**Verify.** Print `len(items), cap(items), items` and see `1 4 [7]`; the wrong version prints `5 8 [0 0 0 0 7]`.

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

**Approach.** Count one visit per element while summing, so the work count is measured, not assumed.

**Why it holds here.** The loop body runs once for each of the five values, giving 5 visits and a sum of 1 through 5, which is 15.

**A plausible wrong approach.** Recording work as the last index, `for i, v := range ... { visits = i }`. Indexes run 0 through 4, so `visits` ends at 4, an off-by-one that makes the `work` check panic.

**Verify.** Print `visits, sum` and see `5 15`. For timing, put the loop in a `BenchmarkSum` in a `_test.go` file and run `go test -bench=. -benchmem` rather than asserting a clock threshold.

## 5. Handle empty search

Search a zero-length interval.

```go
calls := 0
i := sort.Search(0, func(i int) bool { calls++; return true })
check(i == 0 && calls == 0, "empty")
```

**Expected:** Index is 0 and the predicate is never called.

The empty interval has a valid insertion position without accessing any element.

**Approach.** Call `sort.Search(0, f)` and count how often `f` runs.

**Why it holds here.** With an empty interval the search range is already closed, so `Search` returns 0 without calling the predicate, and `calls` stays 0.

**A plausible wrong approach.** Adding a fast path that inspects `items[0]` before searching. On an empty slice that read panics with `index out of range [0] with length 0`, while `sort.Search` handles the empty case without touching any element.

**Verify.** Print `i, calls` and see `0 0`.

## 6. Transfer duplicate boundaries

Find the first value at least 3 in 1, 3, 3, 5.

```go
items := []int{1, 3, 3, 5}
i := sort.Search(len(items), func(i int) bool { return items[i] >= 3 })
check(i == 1, "duplicates")
```

**Expected:** The first duplicate has index 1.

A lower bound is more precise than any matching index. That contract supports insertion and range queries.

**Approach.** Search `1, 3, 3, 5` with `items[i] >= 3`, which is false only at index 0, so the lower bound is 1.

**Why it holds here.** `sort.Search` always returns the first index where the predicate turns true, so with duplicates it lands on the leftmost 3.

**A plausible wrong approach.** A classic binary search that returns as soon as `items[mid] == 3`. Starting from `lo = 0` and `hi = 4`, its first probe is index 2, which holds a 3, so it returns 2 and the check panics with `duplicates`.

**Verify.** Print `i` and see 1. Searching with `> 3` returns 3, and 3 minus 1 gives the two copies of 3.

## Transfer after comparison

Write `countInRange(items []int, lo, hi int) int` for a sorted slice as the difference of two `sort.Search` lower bounds. For `1, 3, 3, 5, 8` check that [3, 4) gives 2, [6, 8) gives 0 and [0, 9) gives 5, and that an empty slice gives 0. Explain which answer an any-match binary search or a `>` predicate would get wrong.
