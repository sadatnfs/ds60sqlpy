# c-032: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-032_solution.c`, implements all six cases, from the "swap integer objects" case to the "transfer a typed structure copy" case, in one `main.c`.

## Mechanism and assumptions

C can write generic storage algorithms using void pointers and explicit element sizes. That flexibility moves type information into the API contract. A wrong element size can copy partial objects, overrun storage or produce misaligned access. void pointer arithmetic is not standard C, so byte traversal uses unsigned char pointers. A generic operation should state overlap, alignment, lifetime and ownership rules rather than claiming that void means any operation is safe. Keep type-specific interpretation at a reviewed boundary and prefer typed wrappers for common callers.

void * can hold object pointers and convert back to an appropriate object pointer. unsigned char * supports bytewise stepping. A swap helper can exchange representations one byte at a time without allocating, provided its two regions are valid, equally sized and nonoverlapping. qsort receives element size explicitly; the comparator must cast each supplied pointer to the actual element type. Generic code still needs bounded size arithmetic.

## Exercise 1: Swap integer objects: change one input

Copy worked example 1, the "swap integer objects" case, into a scratch pad and change `int a = 2, b = 7;` to `int a = 3, b = 7;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the values become 7 and 2); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int a = 2, b = 7;
swap_bytes(&a, &b, sizeof a);
CHECK(a == 7 && b == 2);
```

**Expected:** With `int a = 3, b = 7;` the run stops with `Check failed` at the CHECK on `a == 7 && b == 2`, because the "swap integer objects" case no longer shows that the values become 7 and 2. Restoring `int a = 2, b = 7;` brings that observation back.

The size comes from the actual object rather than a guessed platform width.

## Exercise 2: Swap fixed byte arrays: debug a regression

A regression changed one token in worked example 2, the "swap fixed byte arrays" case, so one line now reads `unsigned char a[] = {2, 2, 3}, b[] = {4, 5, 6};`. Run the example with that line, use the failing CHECK to find why their byte contents exchange exactly no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};
swap_bytes(a, b, sizeof a);
CHECK(a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3`. Once the line reads `unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};` again, the "swap fixed byte arrays" case again shows that their byte contents exchange exactly.

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

Add a fresh distinguishing input for the "transfer a typed structure copy" case to your own c-032 source. Explain why every access in `swap_bytes` or `count_nonzero` stays within a live object and each owned resource is released. An expected type erasure failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "swap fixed byte arrays" case apart from ordinary output: the fixture proves its stated type erasure, element size and typed wrapper assumptions, not universal safety.
