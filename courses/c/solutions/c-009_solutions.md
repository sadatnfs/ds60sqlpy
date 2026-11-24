# c-009: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-009_solution.c`, implements all six cases, from the "relate indexing and arithmetic" case to the "transfer mutation through a subview" case, in one `main.c`.

## Mechanism and assumptions

Pointer arithmetic is defined relative to an array object. A pointer may move among its elements and to the one-past position; the one-past pointer can be compared or used as an end marker but not dereferenced. Subtracting two pointers is defined only under the appropriate same-array relationship and when the result fits ptrdiff_t. Unrelated addresses are not a portable ordering mechanism. A pointer-and-length view makes the valid range explicit without owning the storage. Its lifetime remains limited by the underlying array. Treat an end pointer as a boundary, not as an extra element.

values+i points to element i and *(values+i) is equivalent to values[i] within valid bounds. end-begin produces an element count, not a byte count. A traversal can use p!=end before dereference. const int * restricts mutation through that view. Zero-length views need a documented representation; avoid performing pointer arithmetic on NULL merely because the intended length is zero.

## Exercise 1: Relate indexing and arithmetic: change one input

Copy worked example 1, the "relate indexing and arithmetic" case, into a scratch pad and change `int values[] = {2, 4, 6};` to `int values[] = {2, 5, 6};`. Before running, predict which CHECK fails and which value it sees in place of the worked result (both yield 4); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6};
CHECK(values[1] == *(values + 1) && *(values + 1) == 4);
```

**Expected:** With `int values[] = {2, 5, 6};` the run stops with `Check failed` at the CHECK on `values[1] == *(values + 1) && *(values + 1) == 4`, because the "relate indexing and arithmetic" case no longer shows that both yield 4. Restoring `int values[] = {2, 4, 6};` brings that observation back.

The equivalence applies because the computed pointer remains within the live array.

## Exercise 2: Measure an array interval: debug a regression

A regression changed one token in worked example 2, the "measure an array interval" case, so one line now reads `int *end = values - 3;`. Run the example with that line, use the failing CHECK to find why the difference is 3 elements no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int values[] = {2, 4, 6};
int *begin = values;
int *end = values + 3;
ptrdiff_t n = end - begin;
CHECK(n == 3);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `n == 3`. Once the line reads `int *end = values + 3;` again, the "measure an array interval" case again shows that the difference is 3 elements.

The result counts int elements. Multiplying by sizeof(int) would be a separate byte-size calculation.

## Exercise 3: Traverse before the boundary

Sum through a begin/end pointer loop.

```c
int values[] = {2, 4, 6};
int sum = 0;
for (const int *p = values; p != values + 3; p++) {
  sum += *p;
}
CHECK(sum == 12);
```

**Expected:** The result is 12.

The condition proves p is not one-past before dereference. Incrementing the final valid pointer reaches the end marker safely.

## Exercise 4: Construct a subview

View two elements starting at the second element.

```c
int values[] = {2, 4, 6};
const int *view = values + 1;
size_t n = 2;
CHECK(n == 2 && view[0] == 4 && view[1] == 6);
```

**Expected:** The subview contains 4 and 6.

The subview borrows the original array. It must not outlive that array or expand beyond its remaining extent.

## Exercise 5: Keep an empty boundary non-dereferenced

Use equal begin and end pointers inside one array.

```c
int values[1] = {9};
const int *begin = values, *end = values;
size_t visits = 0;
for (const int *p = begin; p != end; p++) {
  visits++;
}
CHECK(visits == 0);
```

**Expected:** The traversal performs zero accesses.

This empty interval uses valid pointers into a real object. It avoids inventing a zero-sized array or arithmetic on NULL.

## Exercise 6: Transfer mutation through a subview

Change the first element of a borrowed suffix.

```c
int values[] = {1, 2, 3};
int *suffix = values + 1;
suffix[0] = 8;
CHECK(values[1] == 8 && values[0] == 1);
```

**Expected:** The corresponding original element changes.

A view does not copy storage. The shared mutation must be part of the API contract.

## After comparison

Add a fresh distinguishing input for the "transfer mutation through a subview" case to your own c-009 source. Explain why every access in the case code inside `main` stays within a live object and each owned resource is released. An expected one-past pointer failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "measure an array interval" case apart from ordinary output: the fixture proves its stated one-past pointer, pointer difference and borrowed view assumptions, not universal safety.
