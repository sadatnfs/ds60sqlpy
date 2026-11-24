# c-028: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-028_solution.c`, implements all six cases, from the "call a declared API" case to the "transfer repeatable builds to repeatable behavior" case, in one `main.c`.

## Mechanism and assumptions

A multi-file C project separates declarations in headers from definitions in source files. Each source file is compiled independently, so a header is the shared contract the compiler uses at every call site. The linker later resolves external definitions. Defining a non-static global function in a header included by several files can create duplicate definitions. Omitting a required source object can create an unresolved symbol. Include guards prevent repeated declarations inside one translation unit, but do not fix incorrect cross-file ownership. A reproducible build records compiler mode, warnings, source dependencies and link libraries explicitly.

A header declares a function prototype under an include guard. One .c file defines that function, and a caller includes the header. Compile each source with -c to produce an object, then link the objects into one executable. Put libraries after the objects that reference them when the linker requires left-to-right resolution. The browser pad remains one main.c; the separate fixture demonstrates actual headers, source files, tests and a Makefile.

## Exercise 1: Call a declared API: change one input

Copy worked example 1, the "call a declared API" case, into a scratch pad and change `int values[] = {2, 4, 6};` to `int values[] = {3, 4, 6};`. Before running, predict which CHECK fails and which value it sees in place of the worked result (summing 2, 4, 6 returns 12); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int values[] = {2, 4, 6};
CHECK(stats_sum(values, 3) == 12);
```

**Expected:** With `int values[] = {3, 4, 6};` the run stops with `Check failed` at the CHECK on `stats_sum(values, 3) == 12`, because the "call a declared API" case no longer shows that summing 2, 4, 6 returns 12. Restoring `int values[] = {2, 4, 6};` brings that observation back.

A compatible declaration lets the compiler validate the call independently of where the definition appears.

**Approach.** Add the edited elements: 3 + 4 + 6 is 13, so the CHECK on 12 fails.

**Why it holds here.** The prototype makes the compiler check the argument types and count, but values are a run-time matter; the call is still valid and simply returns 13.

**A plausible wrong approach.** Assuming a prototype in a header keeps every caller and the definition in agreement. If `stats.h` declares `int stats_sum(const int *values, int length);` and `stats.c` does not include it, each file compiles alone and the mismatch with the `size_t` definition is undefined at link time. Including the header in `stats.c` makes Clang report `conflicting types for 'stats_sum'`.

**Verify.** Print `stats_sum(values, 3)` and see 13 with the edit and 12 after restoring `{2, 4, 6}`.

## Exercise 2: Use an empty API contract: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "use an empty API contract" case, so that it reads `CHECK(stats_sum(NULL, 0) != 0);`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means the result is zero, and restore it.

The unchanged code is worked example 2:

```c
CHECK(stats_sum(NULL, 0) == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `stats_sum(NULL, 0) == 0`. Once the line reads `CHECK(stats_sum(NULL, 0) == 0);` again, the "use an empty API contract" case again shows that the result is zero.

The interface explicitly permits this empty case and the implementation makes no pointer access.

**Approach.** Evaluate the empty call: with `length` 0 the loop never runs, so the sum stays at its initial 0 and `!= 0` is false.

**Why it holds here.** The contract permits `NULL` when the length is 0, and the implementation reads only inside `i < length`, so no pointer is dereferenced.

**A plausible wrong approach.** Changing the implementation to `if (values == NULL) return -1;` as an error signal. That breaks the documented empty case, and -1 is also a legitimate sum such as `{-1}`, so callers cannot tell an error from data.

**Verify.** Print `stats_sum(NULL, 0)` and see 0.

## Exercise 3: Compare two callers

Call the same helper with two separate arrays.

```c
int a[] = {1, 2}, b[] = {3, 4};
CHECK(stats_sum(a, 2) == 3 && stats_sum(b, 2) == 7);
```

**Expected:** The results are 3 and 7.

Reusable code should not depend on one caller-owned array or hidden previous state.

**Approach.** Call the helper on `a` and then on `b`; each call starts a fresh local `sum` at 0.

**Why it holds here.** The result depends only on the pointer and length passed, so the calls give 1 + 2 = 3 and 3 + 4 = 7 independently.

**A plausible wrong approach.** Keeping the accumulator as `static int sum = 0;` to avoid re-initializing it. The second call then starts from 3 and returns 10, so the result depends on call history rather than on the input.

**Verify.** Call the two arrays in separate statements and print 3 and 7; the static variant prints 3 and 10.

## Exercise 4: Retain caller data

Sum an array and inspect its elements afterward.

```c
int values[] = {2, 4};
(void)stats_sum(values, 2);
CHECK(values[0] == 2 && values[1] == 4);
```

**Expected:** The input remains unchanged.

The const-qualified input contract communicates read-only access through the API.

**Approach.** Pass the array through the `const int *` parameter and read it back afterward.

**Why it holds here.** The function can only read through `values`, so `values[0]` and `values[1]` are still 2 and 4 after the call.

**A plausible wrong approach.** Reusing the input as scratch space, for example a running prefix sum with `values[i] += values[i - 1];`. The `const` parameter rejects that with `read-only variable is not assignable`, which is the point of putting it in the API.

**Verify.** Print both elements after the call and see `2 4`.

## Exercise 5: Check a one-element boundary

Sum one negative value.

```c
int values[] = {-3};
CHECK(stats_sum(values, 1) == -3);
```

**Expected:** The result is -3.

The API handles its stated signed data range; this small fixture avoids overflow.

**Approach.** Run the loop once for `length` 1, adding -3 to 0.

**Why it holds here.** `i < length` admits exactly index 0, so the sum is -3; a signed `int` accumulator holds the negative value without conversion.

**A plausible wrong approach.** Stopping at `i < length - 1`, an off-by-one that skips the last element. For one element the loop never runs and the result is 0, and for `length` 0 the subtraction wraps to `SIZE_MAX` and the loop reads out of bounds.

**Verify.** Print `stats_sum(values, 1)` and see -3; the off-by-one variant prints 0.

## Exercise 6: Transfer repeatable builds to repeatable behavior

Call the pure helper twice on the same input.

```c
int values[] = {1, 2, 3};
int first = stats_sum(values, 3), second = stats_sum(values, 3);
CHECK(first == 6 && second == 6);
```

**Expected:** Both results equal 6.

Stable input and a pure function produce stable behavior. Reproducible binary bytes additionally depend on compiler and build-environment controls.

**Approach.** Call the pure helper twice on the same unchanged array and compare both results with 6.

**Why it holds here.** The function reads only its parameters and writes no shared state, so both calls compute 1 + 2 + 3 = 6.

**A plausible wrong approach.** Taking identical output as proof that builds are reproducible. A file that prints `__TIME__` behaves the same way each run, yet two builds a second apart produce different binaries, because the build time is embedded.

**Verify.** Build the same source twice to the same output name and compare with `cmp`; then repeat with a `__TIME__` line and see `cmp` report a difference.

## After comparison

Split `stats_sum` into `stats.h` and `stats.c`, add `int stats_max(const int *values, size_t length, int *out)` that returns 0 for an empty view and 1 otherwise, and include the header in both `stats.c` and `main.c`. Check `{2, 4, 6}`, `{-3}` and `NULL` with length 0. Then change the header's length type to `int`, rebuild and read the diagnostic, and explain why it only appears because `stats.c` includes its own header.
