# c-006: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-006_solution.c`, implements all six cases, from the "derive a local element count" case to the "transfer independent array storage" case, in one `main.c`.

## Mechanism and assumptions

An array owns a fixed number of elements of one type. Its valid indices run from zero through length minus one. C does not attach a runtime bounds check to each subscript. In many expressions an array converts to a pointer to its first element, which loses the length information. A function receiving an array-like parameter therefore normally needs a separate element count. sizeof applied to an actual array measures the whole array, but sizeof applied to a pointer measures the pointer object. Confusing these contexts is a common source of incomplete loops and out-of-bounds access.

`int values[3]` allocates three integers. A partial initializer fills remaining elements with zero. `sizeof values / sizeof values[0]` derives an element count only where `values` is still an array. A parameter written `int values[]` is adjusted to a pointer parameter. Pass the logical length explicitly and document whether a null pointer is permitted for length zero. Never dereference the one-past position.

## Exercise 1: Derive a local element count: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(n == 3);` to `CHECK(n == 4);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6};
size_t n = sizeof values / sizeof values[0];
CHECK(n == 3);
```

**Expected:** With `CHECK(n == 4);` the run stops with `Check failed` at the CHECK on `n == 3`, because the "derive a local element count" case no longer shows that the count is 3. Restoring `CHECK(n == 3);` brings that observation back.

The expression works because values is an array in this scope. Moving it unchanged into a pointer-taking helper would change its meaning.

## Exercise 2: Pass an explicit length: debug a regression

A regression changed one token in worked example 2, the "pass an explicit length" case, so one line now reads `int values[] = {3, 4, 6};`. Run the example with that line, use the failing CHECK to find why the result is 12 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int values[] = {2, 4, 6};
CHECK(sum_items(values, 3) == 12);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `sum_items(values, 3) == 12`. Once the line reads `int values[] = {2, 4, 6};` again, the "pass an explicit length" case again shows that the result is 12.

The API relies on the caller providing at least three live elements. The pointer alone cannot prove that extent.

## Exercise 3: Inspect partial initialization

Initialize only the first element of a three-element array.

```c
int values[3] = {7};
CHECK(values[0] == 7 && values[1] == 0 && values[2] == 0);
```

**Expected:** The remaining two elements are zero.

This initialization rule differs from an uninitialized automatic array, whose elements must not be read before assignment.

## Exercise 4: Use a logical prefix

Sum only the first two elements of a three-element array.

```c
int values[] = {2, 4, 99};
CHECK(sum_items(values, 2) == 6);
```

**Expected:** The result is 6.

Physical capacity and logical length are separate. The third stored value is intentionally outside this operation.

## Exercise 5: Handle an empty logical view

Call the sum contract with null and length zero.

```c
CHECK(sum_items(NULL, 0) == 0);
```

**Expected:** The sum is zero and no access occurs.

This particular helper accepts an empty null view because its loop performs no access. Do not assume every library function accepts null with a zero size.

## Exercise 6: Transfer independent array storage

Copy elements into a distinct array and mutate the copy.

```c
int a[] = {1, 2};
int b[2];
for (size_t i = 0; i < 2; i++)
  b[i] = a[i];
b[0] = 9;
CHECK(a[0] == 1 && b[0] == 9);
```

**Expected:** The original first element remains 1.

C arrays cannot be assigned as whole arrays with =. Explicit element copy or a correctly sized memcpy creates separate element storage.

## After comparison

Add a fresh distinguishing input for the "transfer independent array storage" case to your own c-006 source. Explain why every access in `sum_items` stays within a live object and each owned resource is released. An expected array extent failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "pass an explicit length" case apart from ordinary output: the fixture proves its stated array extent, array-to-pointer conversion and logical length assumptions, not universal safety.
