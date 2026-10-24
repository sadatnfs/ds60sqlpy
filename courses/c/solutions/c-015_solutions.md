# c-015: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Allocated storage lets a program choose capacity at runtime. malloc returns uninitialized storage or a null pointer on failure; calloc also initializes its bytes to zero. The caller must establish an owner responsible for exactly one release after the last use. free ends the allocation lifetime, so every pointer into that allocation becomes invalid even if its numeric address still looks familiar. Setting one pointer to NULL does not repair other aliases. Calculate allocation sizes without overflowing size_t before calling an allocator. A successful allocation says storage exists, not that application fields have been initialized meaningfully.

malloc(count * sizeof *items) avoids repeating the element type, but multiplication needs a prior bound check. Check the returned pointer before use. calloc(count,sizeof *items) accepts element count and size separately, while still requiring an application resource budget. free(NULL) is defined and harmless. The helper here returns NULL for a zero count by its own contract and refuses multiplication overflow before allocation.

## Exercise 1: Allocate and initialize

Allocate three ints, assign 2, 4, 6 and sum them.

```c
int *p = allocate_ints(3);
CHECK(p != NULL);
p[0] = 2;
p[1] = 4;
p[2] = 6;
CHECK(p[0] + p[1] + p[2] == 12);
free(p);
```

**Expected:** The sum is 12 before release.

malloc storage must be initialized before reading. The owner releases it after the final valid access.

## Exercise 2: Inspect zero-initialized integers

Allocate three ints with calloc and read them.

```c
int *p = calloc(3, sizeof *p);
CHECK(p != NULL);
CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);
free(p);
```

**Expected:** All three values are zero.

For integer objects, all-bits-zero represents zero. Do not generalize that claim blindly to every possible pointer or floating representation.

## Exercise 3: Define the empty allocation policy

Request zero elements through the helper.

```c
CHECK(allocate_ints(0) == NULL);
```

**Expected:** The helper returns NULL without an allocation.

The wrapper makes zero-size behavior predictable. Raw allocator zero-size behavior should not be treated as a portable nonempty object.

## Exercise 4: Reject multiplication overflow

Request SIZE_MAX elements.

```c
CHECK(allocate_ints(SIZE_MAX) == NULL);
```

**Expected:** The helper returns NULL before multiplication or allocation.

The division bound proves the product will fit. Testing a wrapped product after multiplication would be too late.

## Exercise 5: Release an absent allocation

Call free on NULL.

```c
int *p = NULL;
free(p);
CHECK(p == NULL);
```

**Expected:** The operation is harmless.

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

Clearing the owner reduces accidental reuse through that variable. Any aliases would still need to be retired by the ownership protocol.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
