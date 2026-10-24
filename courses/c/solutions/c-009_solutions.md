# c-009: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Pointer arithmetic is defined relative to an array object. A pointer may move among its elements and to the one-past position; the one-past pointer can be compared or used as an end marker but not dereferenced. Subtracting two pointers is defined only under the appropriate same-array relationship and when the result fits ptrdiff_t. Unrelated addresses are not a portable ordering mechanism. A pointer-and-length view makes the valid range explicit without owning the storage. Its lifetime remains limited by the underlying array. Treat an end pointer as a boundary, not as an extra element.

values+i points to element i and *(values+i) is equivalent to values[i] within valid bounds. end-begin produces an element count, not a byte count. A traversal can use p!=end before dereference. const int * restricts mutation through that view. Zero-length views need a documented representation; avoid performing pointer arithmetic on NULL merely because the intended length is zero.

## Exercise 1: Relate indexing and arithmetic

Read the second element through both forms.

```c
int values[] = {2, 4, 6};
CHECK(values[1] == *(values + 1) && *(values + 1) == 4);
```

**Expected:** Both yield 4.

The equivalence applies because the computed pointer remains within the live array.

## Exercise 2: Measure an array interval

Subtract begin from one-past end.

```c
int values[] = {2, 4, 6};
int *begin = values;
int *end = values + 3;
ptrdiff_t n = end - begin;
CHECK(n == 3);
```

**Expected:** The difference is 3 elements.

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

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
