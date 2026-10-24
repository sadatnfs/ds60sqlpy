# c-024: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

An algorithm contract includes input assumptions and output meaning. Binary search requires sorted data and a comparison relation consistent with that ordering. A lower-bound search returns the first position whose value is at least a target, including an insertion position when no element matches. Using a half-open interval makes empty input and one-past results natural. Midpoint arithmetic should avoid overflowing low+high. Complexity explains growth in operations, while runtime performance depends on constants, memory access and input distribution. Preserve exact boundary tests when optimizing rather than trusting a faster-looking implementation.

Maintain an interval [low, high) containing the answer. Compute middle as low+(high-low)/2. If values[middle] is below the target, advance low to middle+1; otherwise set high to middle. The interval strictly shrinks until both bounds meet. Never dereference the returned index before checking it is below length. Sorting and deduplication are different operations.

## Exercise 1: Find an interior boundary

Search 2, 4, 6, 8 for target 5.

```c
int values[] = {2, 4, 6, 8};
CHECK(lower_bound(values, 4, 5) == 2);
```

**Expected:** The lower-bound index is 2.

The result is an insertion position, not a claim that 5 exists.

## Exercise 2: Find the first duplicate

Search 1, 3, 3, 5 for target 3.

```c
int values[] = {1, 3, 3, 5};
CHECK(lower_bound(values, 4, 3) == 1);
```

**Expected:** The index is the first 3 at position 1.

The high=middle branch keeps earlier equal values in the candidate interval.

## Exercise 3: Handle no larger value

Search 2, 4, 6 for target 9.

```c
int values[] = {2, 4, 6};
CHECK(lower_bound(values, 3, 9) == 3);
```

**Expected:** The result is length 3.

The returned one-past index must not be dereferenced.

## Exercise 4: Handle empty input

Search an empty logical view.

```c
CHECK(lower_bound(NULL, 0, 7) == 0);
```

**Expected:** The insertion index is zero.

The loop performs no access because low already equals high.

## Exercise 5: Check the first boundary

Search 2, 4, 6 for target 1.

```c
int values[] = {2, 4, 6};
CHECK(lower_bound(values, 3, 1) == 0);
```

**Expected:** The index is zero.

The answer can be before the first stored value without requiring a negative index.

## Exercise 6: Transfer an exact membership check

Use lower bound and then equality to test whether 4 is present.

```c
int values[] = {2, 4, 6};
size_t i = lower_bound(values, 3, 4);
CHECK(i < 3 && values[i] == 4);
```

**Expected:** The guarded membership test succeeds.

Membership requires both an in-range result and equality. A lower-bound index by itself is not proof of presence.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
