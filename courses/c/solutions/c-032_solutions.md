# c-032: explained solutions

`c-032_solution.c` assembles the "swap integer objects" case through the "transfer a typed structure copy" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

C can write generic storage algorithms using void pointers and explicit element sizes. That flexibility moves type information into the API contract. A wrong element size can copy partial objects, overrun storage or produce misaligned access. void pointer arithmetic is not standard C, so byte traversal uses unsigned char pointers. A generic operation should state overlap, alignment, lifetime and ownership rules rather than claiming that void means any operation is safe. Keep type-specific interpretation at a reviewed boundary and prefer typed wrappers for common callers.

void * can hold object pointers and convert back to an appropriate object pointer. unsigned char * supports bytewise stepping. A swap helper can exchange representations one byte at a time without allocating, provided its two regions are valid, equally sized and nonoverlapping. qsort receives element size explicitly; the comparator must cast each supplied pointer to the actual element type. Generic code still needs bounded size arithmetic.

## Exercise 1: Swap integer objects: change one input

In worked example 1, change `int a = 2, b = 7;` to `int a = 3, b = 7;`. Predict which value the CHECK on `a == 7 && b == 2` sees, then run and restore.

The unchanged code is worked example 1:

```c
int a = 2, b = 7;
swap_bytes(&a, &b, sizeof a);
CHECK(a == 7 && b == 2);
```

**Expected:** `Check failed` at `a == 7 && b == 2`; restoring `int a = 2, b = 7;` passes again.

**Verify:** Name the value that made `a == 7 && b == 2` false, where worked example 1 showed that the values become 7 and 2.

The size comes from the actual object rather than a guessed platform width.

## Exercise 2: Swap fixed byte arrays: debug a regression

Worked example 2 now has a line reading `unsigned char a[] = {2, 2, 3}, b[] = {4, 5, 6};`. Repair it so that their byte contents exchange exactly again.

The unchanged code is worked example 2:

```c
unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};
swap_bytes(a, b, sizeof a);
CHECK(a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3);
```

**Expected:** `Check failed` at `a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3` until the line reads `unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};` again.

**Verify:** Explain how `unsigned char a[] = {2, 2, 3}, b[] = {4, 5, 6};` changes the value `a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3` tests, using your failing and repaired runs.

The operation changes representation bytes without interpreting them as another type.

## Exercise 3: Use a zero-length operation

Invoke the helper with size zero and valid object pointers.

```c
int a = 2, b = 7;
swap_bytes(&a, &b, 0);
CHECK(a == 2 && b == 7);
```

**Expected:** Both objects remain unchanged.

**Verify:** Keep a CHECK equivalent to `a == 2 && b == 7`. Control edit: changing `int a = 2, b = 7;` to `int a = 3, b = 7;` must fail it; then restore it.

The loop performs no accesses. This fixture uses valid pointers rather than assuming every generic API accepts NULL for zero length.

## Exercise 4: Round-trip a swap

Swap two ints twice.

```c
int a = 2, b = 7;
swap_bytes(&a, &b, sizeof a);
swap_bytes(&a, &b, sizeof a);
CHECK(a == 2 && b == 7);
```

**Expected:** The original values return.

**Verify:** Keep a CHECK equivalent to `a == 2 && b == 7`. Control edit: changing `int a = 2, b = 7;` to `int a = 3, b = 7;` must fail it; then restore it.

This property complements the exact one-swap result; by itself it would also accept a no-op implementation.

## Exercise 5: Read bytes through a generic input

Count three nonzero bytes in a four-byte buffer.

```c
unsigned char data[] = {1, 0, 2, 3};
CHECK(count_nonzero(data, sizeof data) == 3);
```

**Expected:** The count is 3.

**Verify:** Keep a CHECK equivalent to `count_nonzero(data, sizeof data) == 3`. Control edit: changing `unsigned char data[] = {1, 0, 2, 3};` to `unsigned char data[] = {1, 1, 2, 3};` must fail it; then restore it.

The semantic unit is explicitly a byte, so no typed alignment assumption is needed.

## Exercise 6: Transfer a typed structure copy

Copy a Pair into another Pair using its exact size.

```c
struct Pair a = {2, 3}, b = {0, 0};
memcpy(&b, &a, sizeof b);
CHECK(b.x == 2 && b.y == 3);
```

**Expected:** Both semantic fields match.

**Verify:** Keep a CHECK equivalent to `b.x == 2 && b.y == 3`. Control edit: changing `struct Pair a = {2, 3}, b = {0, 0};` to `struct Pair a = {3, 3}, b = {0, 0};` must fail it; then restore it.

The destination is a real object of the same type. Semantic verification checks fields rather than unspecified padding bytes.

## After comparison

Swap two `double` values with `swap_bytes(&a, &b, sizeof a)` and CHECK both results. Then explain why passing `sizeof(int)` for the same call would exchange only the first bytes of each object and leave two mixed values that the compiler cannot flag. Finally sketch `swap_double(double *a, double *b)` and explain how a typed wrapper removes the size choice from the caller.
