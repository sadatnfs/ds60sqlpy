# c-015: explained solutions

`c-015_solution.c` assembles the "allocate and initialize" case through the "transfer ownership cleanup" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Allocated storage lets a program choose capacity at runtime. malloc returns uninitialized storage or a null pointer on failure; calloc also initializes its bytes to zero. The caller must establish an owner responsible for exactly one release after the last use. free ends the allocation lifetime, so every pointer into that allocation becomes invalid even if its numeric address still looks familiar. Setting one pointer to NULL does not repair other aliases. Calculate allocation sizes without overflowing size_t before calling an allocator. A successful allocation says storage exists, not that application fields have been initialized meaningfully.

`malloc(count * sizeof *items)` avoids repeating the element type, but multiplication needs a prior bound check. Check the returned pointer before use. `calloc(count, sizeof *items)` accepts element count and size separately, while still requiring an application resource budget. `free(NULL)` is defined and harmless. The helper here returns NULL for a zero count by its own contract and refuses multiplication overflow before allocation.

## Exercise 1: Allocate and initialize: change one input

In worked example 1, change `p[0] = 2;` to `p[1] = 2;`. Predict which value the CHECK on `p[0] + p[1] + p[2] == 12` sees, then run and restore.

The unchanged code is worked example 1:

```c
int *p = allocate_ints(3);
CHECK(p != NULL);
p[0] = 2;
p[1] = 4;
p[2] = 6;
CHECK(p[0] + p[1] + p[2] == 12);
free(p);
```

**Expected:** `Check failed` at `p[0] + p[1] + p[2] == 12`; restoring `p[0] = 2;` passes again.

**Verify:** Name the value that made `p[0] + p[1] + p[2] == 12` false, where worked example 1 showed that the sum is 12 before release.

malloc storage must be initialized before reading. The owner releases it after the final valid access.

## Exercise 2: Inspect zero-initialized integers: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(p[0] != 0 && p[1] == 0 && p[2] == 0);`. Explain why it fails although all three values are zero, then restore it.

The unchanged code is worked example 2:

```c
int *p = calloc(3, sizeof *p);
CHECK(p != NULL);
CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);
free(p);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);` again, though all three values are zero.

**Verify:** Explain why `CHECK(p[0] != 0 && p[1] == 0 && p[2] == 0);` rejects a state that `p[0] == 0 && p[1] == 0 && p[2] == 0` accepts, using your failing and repaired runs.

For integer objects, all-bits-zero represents zero. Do not generalize that claim blindly to every possible pointer or floating representation.

## Exercise 3: Define the empty allocation policy

Request zero elements through the helper.

```c
CHECK(allocate_ints(0) == NULL);
```

**Expected:** The helper returns NULL without an allocation.

**Verify:** Keep a CHECK equivalent to `allocate_ints(0) == NULL`. Control edit: `CHECK(allocate_ints(1) == NULL);` must fail; then restore it.

The wrapper makes zero-size behavior predictable. Raw allocator zero-size behavior should not be treated as a portable nonempty object.

## Exercise 4: Reject multiplication overflow

Request SIZE_MAX elements.

```c
CHECK(allocate_ints(SIZE_MAX) == NULL);
```

**Expected:** The helper returns NULL before multiplication or allocation.

**Verify:** Keep a CHECK equivalent to `allocate_ints(SIZE_MAX) == NULL`. Control edit: `CHECK(allocate_ints(SIZE_MAX) != NULL);` must fail; then restore it.

The division bound proves the product will fit. Testing a wrapped product after multiplication would be too late.

## Exercise 5: Release an absent allocation

Call free on NULL.

```c
int *p = NULL;
free(p);
CHECK(p == NULL);
```

**Expected:** The operation is harmless.

**Verify:** Keep a CHECK equivalent to `p == NULL`. Control edit: `CHECK(p != NULL);` must fail; then restore it.

This defined behavior simplifies cleanup paths. It does not make double-free of a non-null stale pointer valid.

## Exercise 6: Transfer ownership cleanup

Allocate one value, release it and clear the owning pointer.

```c
int *p = allocate_ints(1);
CHECK(p != NULL);
*p = 9;
CHECK(*p == 9);
free(p);
p = NULL;
CHECK(p == NULL);
```

**Expected:** The owner records absence afterward.

**Verify:** Keep a CHECK equivalent to `*p == 9`. Control edit: changing `*p = 9;` to `*p = 10;` must fail it; then restore it.

Clearing the owner reduces accidental reuse through that variable. Any aliases would still need to be retired by the ownership protocol.

## After comparison

Write `int *copy_with_zero(const int *source, size_t count)` that allocates `count + 1` ints, copies `count` values and appends 0. Call it with three values, CHECK the copy and the trailing 0, then free it exactly once. Reject `count > SIZE_MAX / sizeof(int) - 1` before computing `(count + 1) * sizeof(int)`: that single test covers both the addition and the multiplication, and the empty-allocation policy must not hide either overflow.
