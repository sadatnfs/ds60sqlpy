# c-024: explained solutions

`c-024_solution.c` assembles the "find an interior boundary" case through the "transfer an exact membership check" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

An algorithm contract includes input assumptions and output meaning. Binary search requires sorted data and a comparison relation consistent with that ordering. A lower-bound search returns the first position whose value is at least a target, including an insertion position when no element matches. Using a half-open interval makes empty input and one-past results natural. Midpoint arithmetic should avoid overflowing low+high. Complexity explains growth in operations, while runtime performance depends on constants, memory access and input distribution. Preserve exact boundary tests when optimizing rather than trusting a faster-looking implementation.

Maintain an interval [low, high) containing the answer. Compute middle as low+(high-low)/2. If values[middle] is below the target, advance low to middle+1; otherwise set high to middle. The interval strictly shrinks until both bounds meet. Never dereference the returned index before checking it is below length. Sorting and deduplication are different operations.

## Exercise 1: Find an interior boundary: change one input

In worked example 1, change `int values[] = {2, 4, 6, 8};` to `int values[] = {2, 5, 6, 8};`. Predict which value the CHECK on `lower_bound(values, 4, 5) == 2` sees, then run and restore.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6, 8};
CHECK(lower_bound(values, 4, 5) == 2);
```

**Expected:** `Check failed` at `lower_bound(values, 4, 5) == 2`; restoring `int values[] = {2, 4, 6, 8};` passes again.

The result is an insertion position, not a claim that 5 exists.

**Approach.** Find the first element that is not less than 5: in `{2, 5, 6, 8}` that is the 5 at index 1.

**Why it holds here.** Lower bound returns the first position whose value is `>=` the target, so a matching element is found at its own index, and 1 is not 2.

**A plausible wrong approach.** Predicting 2 because 5 "goes after 4". That is the upper-bound answer, the position after all elements `<=` the target; lower bound stops at the first equal element.

**Verify.** Print `lower_bound(values, 4, 5)` and see 1 with the edit and 2 after restoring `{2, 4, 6, 8}`.

## Exercise 2: Find the first duplicate: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(lower_bound(values, 4, 4) == 1);`. Explain why it fails although the index is the first 3 at position 1, then restore it.

The unchanged code is worked example 2:

```c
int values[] = {1, 3, 3, 5};
CHECK(lower_bound(values, 4, 3) == 1);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(lower_bound(values, 4, 3) == 1);` again, though the index is the first 3 at position 1.

The high=middle branch keeps earlier equal values in the candidate interval.

**Approach.** Search for 4 in `{1, 3, 3, 5}`: no element equals 4, and the first element `>= 4` is the 5 at index 3.

**Why it holds here.** The array is unchanged; only the target changed, so the edited CHECK compares 3 with 1 and fails. With target 3, the `high = middle` branch keeps the earlier 3 and returns 1.

**A plausible wrong approach.** Using `<=` in the comparison, `if (values[middle] <= target)`. That computes the upper bound and returns 3 for target 3, past both duplicates, so the original CHECK fails too.

**Verify.** Print `lower_bound(values, 4, 4)` and see 3; the `<=` variant prints 3 for target 3.

## Exercise 3: Handle no larger value

Search 2, 4, 6 for target 9.

```c
int values[] = {2, 4, 6};
CHECK(lower_bound(values, 3, 9) == 3);
```

**Expected:** The result is length 3.

The returned one-past index must not be dereferenced.

**Approach.** Return `n` when every element is smaller than the target, here 3 for `{2, 4, 6}` and 9.

**Why it holds here.** Each probe finds a value below 9 and moves `low` past it until `low` reaches `high`, which started at `n`, so the result is one past the end.

**A plausible wrong approach.** Reading `values[i]` right after the call to see what was found. With `i` 3 that reads past the 3-element array, which is undefined; every caller must test `i < n` first.

**Verify.** Print the result and see 3, and confirm it equals `sizeof values / sizeof values[0]`.

## Exercise 4: Handle empty input

Search an empty logical view.

```c
CHECK(lower_bound(NULL, 0, 7) == 0);
```

**Expected:** The insertion index is zero.

The loop performs no access because low already equals high.

**Approach.** Start with `low` 0 and `high` equal to `n`, so an empty range never enters the loop.

**Why it holds here.** With `n` 0, `low < high` is false at once, no element is read, and the insertion index 0 is returned without touching the null pointer.

**A plausible wrong approach.** Adding a fast path such as `if (target <= values[0]) return 0;` before the loop. It reads the first element through `NULL` when the view is empty, which is undefined and usually crashes.

**Verify.** Run the CHECK and see the success line; the fast-path variant should only be compiled, never run, with `NULL`.

## Exercise 5: Check the first boundary

Search 2, 4, 6 for target 1.

```c
int values[] = {2, 4, 6};
CHECK(lower_bound(values, 3, 1) == 0);
```

**Expected:** The index is zero.

The answer can be before the first stored value without requiring a negative index.

**Approach.** Use the half-open interval `[low, high)` so the answer 0 is reached by shrinking `high`, never by subtracting below 0.

**Why it holds here.** Every element is at least 1, so each probe sets `high = middle` until `high` reaches 0, and `low` 0 is returned.

**A plausible wrong approach.** Using a closed interval with `size_t` and `high = middle - 1`. When `middle` is 0 that wraps to 18446744073709551615, `low <= high` stays true and the next probe reads far out of bounds.

**Verify.** Print `(size_t)0 - 1` and see 18446744073709551615, then print `lower_bound(values, 3, 1)` and see 0.

## Exercise 6: Transfer an exact membership check

Use lower bound and then equality to test whether 4 is present.

```c
int values[] = {2, 4, 6};
size_t i = lower_bound(values, 3, 4);
CHECK(i < 3 && values[i] == 4);
```

**Expected:** The guarded membership test succeeds.

Membership requires both an in-range result and equality. A lower-bound index by itself is not proof of presence.

**Approach.** Combine both tests: `i < 3` proves the index is in range, and `values[i] == 4` proves the element matches.

**Why it holds here.** 4 is present at index 1, the lower bound returns 1, and both operands are true; `&&` evaluates the bounds test first, so the read is always safe.

**A plausible wrong approach.** Testing only `i < 3`. For a missing target such as 5 the lower bound is 2, which is in range, so the code would report 5 present even though `values[2]` is 6.

**Verify.** Print `lower_bound(values, 3, 5)` and see 2, then confirm that `values[2] == 5` is false.

## After comparison

Write `bool count_equal(const int *values, size_t n, int target, size_t *count)` that uses `lower_bound` and an upper bound with `<=` to count matching elements in a sorted array. Check `{1, 3, 3, 5}` for 3 (2), 4 (0) and 5 (1), and an empty `NULL` view (0). Explain why the count is the difference of the two bounds, and why that takes about 2 log2 n comparisons instead of one pass over every element.
