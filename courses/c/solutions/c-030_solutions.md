# c-030: explained solutions

`c-030_solution.c` assembles the "guard a formerly unsafe index" case through the "transfer a newly discovered boundary" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Compiler warnings, static analysis, sanitizers and debugger traces reveal different classes of evidence. AddressSanitizer instruments many invalid memory accesses; UndefinedBehaviorSanitizer checks selected undefined operations. Neither establishes that every possible path is correct, and neither replaces ownership reasoning. A sanitizer failure should become a small regression case after the defect is repaired. Do not ship a reference that intentionally executes undefined behavior merely to print a diagnostic. This lesson runs safe regression cases and gives the separate instrumented build workflow. A debugger is most useful when you can name the first invariant that became false rather than merely stop at the final crash.

A prepared contributor build can add `-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer` to compilation and linking. Execute the same checked source under that build. The ordinary pad uses its fixed reviewed flags and does not claim sanitizer execution. Keep source, compiler command, exit status and diagnostic together. Disable neither an assertion nor a sanitizer report without explaining the actual correction.

## Exercise 1: Guard a formerly unsafe index: change one input

In worked example 1, change `int values[] = {2, 4, 6}, out = 0;` to `int values[] = {2, 4, 7}, out = 0;`. Predict which value the CHECK on `at_index(values, 3, 2, &out) && out == 6` sees, then run and restore.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6}, out = 0;
CHECK(at_index(values, 3, 2, &out) && out == 6);
```

**Expected:** `Check failed` at `at_index(values, 3, 2, &out) && out == 6`; restoring `int values[] = {2, 4, 6}, out = 0;` passes again.

**Verify:** Name the value that made `at_index(values, 3, 2, &out) && out == 6` false, where worked example 1 showed that the value 6 is returned.

The accessor proves the index is below length before reading.

## Exercise 2: Reject the one-past index: debug a regression

Worked example 2 now has a line reading `int values[] = {2, 4, 6}, out = 10;`. Repair it so that the operation fails and output remains 9 again.

The unchanged code is worked example 2:

```c
int values[] = {2, 4, 6}, out = 9;
CHECK(!at_index(values, 3, 3, &out) && out == 9);
```

**Expected:** `Check failed` at `!at_index(values, 3, 3, &out) && out == 9` until the line reads `int values[] = {2, 4, 6}, out = 9;` again.

**Verify:** Explain how `int values[] = {2, 4, 6}, out = 10;` changes the value `!at_index(values, 3, 3, &out) && out == 9` tests, using your failing and repaired runs.

The regression preserves the boundary that an unchecked implementation would access illegally.

## Exercise 3: Reject an empty view

Request index zero from an empty logical view.

```c
int out = 9;
CHECK(!at_index(NULL, 0, 0, &out) && out == 9);
```

**Expected:** No access occurs.

**Verify:** Keep a CHECK equivalent to `!at_index(NULL, 0, 0, &out) && out == 9`. Control edit: changing `int out = 9;` to `int out = 10;` must fail it; then restore it.

The function checks the pointer and bound instead of relying on a sanitizer to stop a bad access.

## Exercise 4: Verify a valid allocation lifetime

Allocate, initialize, inspect and free one integer.

```c
int *p = malloc(sizeof *p);
CHECK(p != NULL);
*p = 7;
CHECK(*p == 7);
free(p);
p = NULL;
CHECK(p == NULL);
```

**Expected:** The value is checked before release.

**Verify:** Keep a CHECK equivalent to `*p == 7`. Control edit: changing `*p = 7;` to `*p = 8;` must fail it; then restore it.

There is no post-free dereference in a production reference. A historical failing source belongs only in a clearly isolated diagnostic exercise.

## Exercise 5: Retain output capacity checks

Format a short message into sufficient storage.

```c
char out[8];
int n = snprintf(out, sizeof out, "%s", "ready");
CHECK(n >= 0 && (size_t)n < sizeof out && strcmp(out, "ready") == 0);
```

**Expected:** The write fits completely.

**Verify:** Keep a CHECK equivalent to `n >= 0 && (size_t)n < sizeof out && strcmp(out, "ready") == 0`. Control edit: changing `int n = snprintf(out, sizeof out, "%s", "ready");` to `int n = snprintf(out, sizeof out, "%s!", "ready");` must fail it; then restore it.

The explicit return-value check remains useful even when instrumentation is enabled.

## Exercise 6: Transfer a newly discovered boundary

Test a singleton at indices zero and one.

```c
int values[] = {5}, out = 0;
CHECK(at_index(values, 1, 0, &out) && out == 5);
CHECK(!at_index(values, 1, 1, &out));
```

**Expected:** Only zero is valid.

**Verify:** Keep a CHECK equivalent to `at_index(values, 1, 0, &out) && out == 5`. Control edit: changing `int values[] = {5}, out = 0;` to `int values[] = {6}, out = 0;` must fail it; then restore it.

A tiny case is easier to reason about and keep as a permanent regression than a large nondeterministic crash workload.

## After comparison

Add a regression for an index that no small test reaches: `at_index(values, 3, SIZE_MAX, &out)` must fail with `out` unchanged; CHECK it. Then explain why the equivalent-looking guard `i + 1 <= n` passes Exercises 1 and 2 but accepts this call, because `SIZE_MAX + 1` wraps to 0, and why a negative `int` index converted to `size_t` arrives as exactly this kind of huge value.
