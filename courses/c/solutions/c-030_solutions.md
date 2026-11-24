# c-030: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-030_solution.c`, implements all six cases, from the "guard a formerly unsafe index" case to the "transfer a newly discovered boundary" case, in one `main.c`.

## Mechanism and assumptions

Compiler warnings, static analysis, sanitizers and debugger traces reveal different classes of evidence. AddressSanitizer instruments many invalid memory accesses; UndefinedBehaviorSanitizer checks selected undefined operations. Neither establishes that every possible path is correct, and neither replaces ownership reasoning. A sanitizer failure should become a small regression case after the defect is repaired. Do not ship a reference that intentionally executes undefined behavior merely to print a diagnostic. This lesson runs safe regression cases and gives the separate instrumented build workflow. A debugger is most useful when you can name the first invariant that became false rather than merely stop at the final crash.

A prepared contributor build can add `-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer` to compilation and linking. Execute the same checked source under that build. The ordinary pad uses its fixed reviewed flags and does not claim sanitizer execution. Keep source, compiler command, exit status and diagnostic together. Disable neither an assertion nor a sanitizer report without explaining the actual correction.

## Exercise 1: Guard a formerly unsafe index: change one input

Copy worked example 1, the "guard a formerly unsafe index" case, into a scratch pad and change `int values[] = {2, 4, 6}, out = 0;` to `int values[] = {2, 4, 7}, out = 0;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the value 6 is returned); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6}, out = 0;
CHECK(at_index(values, 3, 2, &out) && out == 6);
```

**Expected:** With `int values[] = {2, 4, 7}, out = 0;` the run stops with `Check failed` at the CHECK on `at_index(values, 3, 2, &out) && out == 6`, because the "guard a formerly unsafe index" case no longer shows that the value 6 is returned. Restoring `int values[] = {2, 4, 6}, out = 0;` brings that observation back.

The accessor proves the index is below length before reading.

## Exercise 2: Reject the one-past index: debug a regression

A regression changed one token in worked example 2, the "reject the one-past index" case, so one line now reads `int values[] = {2, 4, 6}, out = 10;`. Run the example with that line, use the failing CHECK to find why the operation fails and output remains 9 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int values[] = {2, 4, 6}, out = 9;
CHECK(!at_index(values, 3, 3, &out) && out == 9);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!at_index(values, 3, 3, &out) && out == 9`. Once the line reads `int values[] = {2, 4, 6}, out = 9;` again, the "reject the one-past index" case again shows that the operation fails and output remains 9.

The regression preserves the boundary that an unchecked implementation would access illegally.

## Exercise 3: Reject an empty view

Request index zero from an empty logical view.

```c
int out = 9;
CHECK(!at_index(NULL, 0, 0, &out) && out == 9);
```

**Expected:** No access occurs.

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

There is no post-free dereference in a production reference. A historical failing source belongs only in a clearly isolated diagnostic exercise.

## Exercise 5: Retain output capacity checks

Format a short message into sufficient storage.

```c
char out[8];
int n = snprintf(out, sizeof out, "%s", "ready");
CHECK(n >= 0 && (size_t)n < sizeof out && strcmp(out, "ready") == 0);
```

**Expected:** The write fits completely.

The explicit return-value check remains useful even when instrumentation is enabled.

## Exercise 6: Transfer a newly discovered boundary

Test a singleton at indices zero and one.

```c
int values[] = {5}, out = 0;
CHECK(at_index(values, 1, 0, &out) && out == 5);
CHECK(!at_index(values, 1, 1, &out));
```

**Expected:** Only zero is valid.

A tiny case is easier to reason about and keep as a permanent regression than a large nondeterministic crash workload.

## After comparison

Add a fresh distinguishing input for the "transfer a newly discovered boundary" case to your own c-030 source. Explain why every access in `at_index` stays within a live object and each owned resource is released. An expected instrumentation failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "reject the one-past index" case apart from ordinary output: the fixture proves its stated instrumentation, regression fixture and diagnostic evidence assumptions, not universal safety.
