# c-032: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

C can write generic storage algorithms using void pointers and explicit element sizes. That flexibility moves type information into the API contract. A wrong element size can copy partial objects, overrun storage or produce misaligned access. void pointer arithmetic is not standard C, so byte traversal uses unsigned char pointers. A generic operation should state overlap, alignment, lifetime and ownership rules rather than claiming that void means any operation is safe. Keep type-specific interpretation at a reviewed boundary and prefer typed wrappers for common callers.

void * can hold object pointers and convert back to an appropriate object pointer. unsigned char * supports bytewise stepping. A swap helper can exchange representations one byte at a time without allocating, provided its two regions are valid, equally sized and nonoverlapping. qsort receives element size explicitly; the comparator must cast each supplied pointer to the actual element type. Generic code still needs bounded size arithmetic.

## Exercise 1: Swap integer objects

Exchange two ints using their exact object size.

```c
int a = 2, b = 7;
swap_bytes(&a, &b, sizeof a);
CHECK(a == 7 && b == 2);
```

**Expected:** The values become 7 and 2.

The size comes from the actual object rather than a guessed platform width.

## Exercise 2: Swap fixed byte arrays

Exchange two three-byte arrays.

```c
unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};
swap_bytes(a, b, sizeof a);
CHECK(a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3);
```

**Expected:** Their byte contents exchange exactly.

The operation changes representation bytes without interpreting them as another type.

## Exercise 3: Use a zero-length operation

Invoke the helper with size zero and valid object pointers.

```c
int a = 2, b = 7;
swap_bytes(&a, &b, 0);
CHECK(a == 2 && b == 7);
```

**Expected:** Both objects remain unchanged.

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

This property complements the exact one-swap result; by itself it would also accept a no-op implementation.

## Exercise 5: Read bytes through a generic input

Count three nonzero bytes in a four-byte buffer.

```c
unsigned char data[] = {1, 0, 2, 3};
CHECK(count_nonzero(data, sizeof data) == 3);
```

**Expected:** The count is 3.

The semantic unit is explicitly a byte, so no typed alignment assumption is needed.

## Exercise 6: Transfer a typed structure copy

Copy a Pair into another Pair using its exact size.

```c
struct Pair a = {2, 3}, b = {0, 0};
memcpy(&b, &a, sizeof b);
CHECK(b.x == 2 && b.y == 3);
```

**Expected:** Both semantic fields match.

The destination is a real object of the same type. Semantic verification checks fields rather than unspecified padding bytes.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
