# c-001: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-001_solution.c`, implements all six cases, from the "check a first value" case to the "transfer a receipt calculation" case, in one `main.c`.

## Mechanism and assumptions

C source is text describing declarations and operations. The preprocessor handles directives, the compiler translates a translation unit, and the linker combines machine-code objects with required libraries. The executable is a separate artifact from main.c. A syntax error prevents compilation; an unresolved symbol prevents linking; an assertion can fail only after execution begins. These stages require different diagnoses. C does not automatically validate every runtime memory operation, so successful compilation is a starting point rather than a safety proof. Begin with independently checked scalar results before learning pointers and resource ownership.

#include makes header declarations available. int main(void) is an entrypoint with no parameters; returning zero signals successful termination. Braces form a block and semicolons finish most statements. printf formats values, while puts writes a string plus a newline. assert from assert.h checks a condition when NDEBUG is not defined. %d expects an int, and a mismatched format argument can be undefined behavior.

## Exercise 1: Check a first value: change one input

Copy worked example 1, the "check a first value" case, into a scratch pad and change `int total = 2 + 3;` to `int total = 3 + 3;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the stored value is 5); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int total = 2 + 3;
CHECK(total == 5);
```

**Expected:** With `int total = 3 + 3;` the run stops with `Check failed` at the CHECK on `total == 5`, because the "check a first value" case no longer shows that the stored value is 5. Restoring `int total = 2 + 3;` brings that observation back.

The expectation is known independently of the program. A print statement alone would not reject a wrong calculation.

**Approach.** Evaluate the edited initializer before reading the CHECK: `3 + 3` stores 6 in `total`, and the CHECK still compares with 5.

**Why it holds here.** The expected 5 was fixed before the program ran, so 6 makes `total == 5` false. `lesson_check` writes `Check failed at main.c:` plus the line number to stderr and calls `abort()`, so the success line never prints.

**A plausible wrong approach.** Predicting that the run still succeeds because CHECK behaves like `assert`, which a release build can remove with `NDEBUG`. This CHECK is always compiled in, so the wrong total always reaches the comparison.

**Verify.** Run the edited pad and see the `Check failed` line with a nonzero exit status (134 in a shell after `abort`); restore `2 + 3` and see `Worked example checks passed.`

## Exercise 2: Format a checked result: debug a regression

A regression changed one token in worked example 2, the "format a checked result" case, so one line now reads `int n = snprintf(out, sizeof out, "total=%d", 6);`. Run the example with that line, use the failing CHECK to find why the result length is 7 and text is total=5 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
char out[16];
int n = snprintf(out, sizeof out, "total=%d", 5);
CHECK(n == 7);
CHECK(strcmp(out, "total=5") == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `strcmp(out, "total=5") == 0`. Once the line reads `int n = snprintf(out, sizeof out, "total=%d", 5);` again, the "format a checked result" case again shows that the result length is 7 and text is total=5.

snprintf returns the length that would be required, excluding the terminating null byte. A caller must compare it with capacity before treating output as complete.

**Approach.** Read the two CHECKs separately: `snprintf` still writes seven characters, `total=6`, so `n == 7` passes and the string comparison is the CHECK that stops the run.

**Why it holds here.** The length check cannot tell one digit from another, because `total=5` and `total=6` are both seven characters. Only `strcmp(out, "total=5") == 0` sees the wrong digit, so restoring the argument 5 repairs it.

**A plausible wrong approach.** Concluding from the passing `n == 7` that formatting is fine and enlarging `out` or changing the format string. The buffer has 16 bytes and nothing was truncated; the defect is the value 6 passed to `snprintf`.

**Verify.** Add `printf("%d %s\n", n, out);` before the CHECKs and see `7 total=6` with the regression and `7 total=5` after the repair.

## Exercise 3: Trace statement order

Start at 1, increment, then multiply by 3.

```c
int count = 1;
count += 1;
count *= 3;
CHECK(count == 6);
```

**Expected:** The result is 6.

Changing operation order changes the state trajectory. Separate statements make sequencing explicit.

**Approach.** Apply the statements in source order: `count` starts at 1, `+= 1` makes it 2 and `*= 3` makes it 6.

**Why it holds here.** Each compound assignment reads the value left by the previous statement, so the multiplication sees 2, not the initial 1, and the CHECK on 6 holds.

**A plausible wrong approach.** Collapsing the steps into one expression as `count = count * 3 + 1;`. Multiplying first gives 4 from the starting value 1, so the CHECK on 6 fails; order matters because both operations change the same object.

**Verify.** Print `count` after each statement and see 2 and then 6.

## Exercise 4: Inspect a boolean condition

Compare 4 with 4 and 4 with 5.

```c
bool same = (4 == 4);
bool different = (4 != 5);
CHECK(same &&different);
```

**Expected:** Equality is true and inequality is true.

An equality expression compares values. Assignment uses a different operator and changes state.

**Approach.** Evaluate each comparison to a `bool`: `4 == 4` is true and `4 != 5` is true, so `same && different` is true.

**Why it holds here.** Both relational expressions compare values without changing anything, and `&&` needs both to be true, which they are for these literals.

**A plausible wrong approach.** Writing the equality with `=`, for example `int a = 4; bool same = (a = 4);`. That assigns 4 to `a` and converts 4 to true, so it passes for the wrong reason; `(a = 5)` would also be true and would change `a`. With two literals, `4 = 4` does not even compile because a literal is not assignable.

**Verify.** Print `same`, `different` and `(4 == 5)` with `%d` and see `1 1 0`.

## Exercise 5: Use an explicit return contract

Call a helper returning the value 7.

```c
CHECK(seven() == 7);
```

**Expected:** The caller receives 7.

The declaration gives the compiler a return-type contract. A missing or incompatible declaration should be repaired before execution.

**Approach.** Call the helper `seven()`, which is defined above `main` with the prototype `int seven(void)`, and compare its result with 7.

**Why it holds here.** Because the definition is visible before the call, the compiler checks the call against an `int` return and an empty parameter list, and the call yields 7.

**A plausible wrong approach.** Moving the helper below `main` without a prototype. C99 removed implicit declarations, so current GCC and Clang reject the call to an undeclared function under `-std=c17`; old compilers guessed an `int` return, which happens to match here but would silently break a helper returning `double`.

**Verify.** Temporarily move the helper below `main`, compile with the lesson flags and read the undeclared-function diagnostic; restore it, or add `int seven(void);` above `main`, and the program prints its success line.

## Exercise 6: Transfer a receipt calculation

Multiply 4 items by a unit amount of 6.

```c
int items = 4;
int unit = 6;
int amount = items * unit;
CHECK(amount == 24);
```

**Expected:** The checked amount is 24.

These small values fit int. A reusable arithmetic API later needs a range and overflow policy rather than relying on one benign fixture.

**Approach.** Multiply `items` by `unit` in `int`: 4 times 6 is 24, which is far inside the range of `int`.

**Why it holds here.** No intermediate value comes near `INT_MAX`, so the product is exact and the CHECK on 24 holds.

**A plausible wrong approach.** Reusing the same line for large receipts, such as 100000 items at a unit of 30000. The true product, 3000000000, exceeds `INT_MAX` on the worker, and signed overflow is undefined behavior, so that input must be rejected before multiplying rather than run to see what happens.

**Verify.** Keep the CHECK on 24, then add `CHECK(4 <= INT_MAX / 6);` and `CHECK(100000 > INT_MAX / 30000);`. The quotient `INT_MAX / 30000` is 71582, so the second CHECK proves the large receipt would overflow without performing it.

## After comparison

Write `bool format_total(char *out, size_t cap, int total)` that calls `snprintf` and returns true only when the result is nonnegative and less than `cap`. Check that capacity 16 and total 5 give `total=5`, capacity 8 also succeeds because seven characters plus the null byte fit exactly, capacity 7 is rejected with `out` truncated to `total=`, and capacity 8 with total 123 is rejected. Explain which of these a test written as `n > cap` would wrongly accept.
