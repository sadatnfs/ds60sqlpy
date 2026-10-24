# c-028: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A multi-file C project separates declarations in headers from definitions in source files. Each source file is compiled independently, so a header is the shared contract the compiler uses at every call site. The linker later resolves external definitions. Defining a non-static global function in a header included by several files can create duplicate definitions. Omitting a required source object can create an unresolved symbol. Include guards prevent repeated declarations inside one translation unit, but do not fix incorrect cross-file ownership. A reproducible build records compiler mode, warnings, source dependencies and link libraries explicitly.

A header declares a function prototype under an include guard. One .c file defines that function, and a caller includes the header. Compile each source with -c to produce an object, then link the objects into one executable. Put libraries after the objects that reference them when the linker requires left-to-right resolution. The browser pad remains one main.c; the separate fixture demonstrates actual headers, source files, tests and a Makefile.

## Exercise 1: Call a declared API

Use the stats_sum prototype before its definition.

```c
int values[] = {2, 4, 6};
CHECK(stats_sum(values, 3) == 12);
```

**Expected:** Summing 2, 4, 6 returns 12.

A compatible declaration lets the compiler validate the call independently of where the definition appears.

## Exercise 2: Use an empty API contract

Sum a zero-length view.

```c
CHECK(stats_sum(NULL, 0) == 0);
```

**Expected:** The result is zero.

The interface explicitly permits this empty case and the implementation makes no pointer access.

## Exercise 3: Compare two callers

Call the same helper with two separate arrays.

```c
int a[] = {1, 2}, b[] = {3, 4};
CHECK(stats_sum(a, 2) == 3 && stats_sum(b, 2) == 7);
```

**Expected:** The results are 3 and 7.

Reusable code should not depend on one caller-owned array or hidden previous state.

## Exercise 4: Retain caller data

Sum an array and inspect its elements afterward.

```c
int values[] = {2, 4};
(void)stats_sum(values, 2);
CHECK(values[0] == 2 && values[1] == 4);
```

**Expected:** The input remains unchanged.

The const-qualified input contract communicates read-only access through the API.

## Exercise 5: Check a one-element boundary

Sum one negative value.

```c
int values[] = {-3};
CHECK(stats_sum(values, 1) == -3);
```

**Expected:** The result is -3.

The API handles its stated signed data range; this small fixture avoids overflow.

## Exercise 6: Transfer repeatable builds to repeatable behavior

Call the pure helper twice on the same input.

```c
int values[] = {1, 2, 3};
int first = stats_sum(values, 3), second = stats_sum(values, 3);
CHECK(first == 6 && second == 6);
```

**Expected:** Both results equal 6.

Stable input and a pure function produce stable behavior. Reproducible binary bytes additionally depend on compiler and build-environment controls.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
