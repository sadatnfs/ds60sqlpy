# c-002: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-002_solution.c`, implements all six cases, from the "compare integer and floating division" case to the "transfer negative division" case, in one `main.c`.

## Mechanism and assumptions

An integer type has a finite range. C guarantees minimum ranges for fundamental integer types, not that int has one universal size. Fixed-width types from stdint.h exist when the implementation supports exactly those widths. Unsigned arithmetic is defined modulo one more than its maximum value; signed overflow is undefined behavior. That difference is a semantic rule, not an invitation to guess CPU wraparound. Floating-point types approximate many real numbers and need deliberate comparison policies. Conversion can lose information even when the source program compiles without an error.

sizeof reports a size in char units, and sizeof(char) is always one; CHAR_BIT gives bits per char. INT_MAX and UINT_MAX expose implementation limits. A U suffix creates an unsigned integer constant. Integer division truncates toward zero. Convert an operand before division when a fractional result is required. fabs computes an absolute floating difference; a tolerance is specific to the numerical problem.

## Exercise 1: Compare integer and floating division: change one input

Copy worked example 1, the "compare integer and floating division" case, into a scratch pad and change `int whole = 7 / 2;` to `int whole = 8 / 2;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the results are 3 and 3.5); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int whole = 7 / 2;
double fraction = 7 / 2.0;
CHECK(whole == 3 && fraction == 3.5);
```

**Expected:** With `int whole = 8 / 2;` the run stops with `Check failed` at the CHECK on `whole == 3 && fraction == 3.5`, because the "compare integer and floating division" case no longer shows that the results are 3 and 3.5. Restoring `int whole = 7 / 2;` brings that observation back.

Converting the already truncated integer result afterward cannot restore the missing fraction.

**Approach.** Evaluate the edited line with integer operands: `8 / 2` is exact and stores 4 in `whole`, while `fraction` is still `7 / 2.0`, which is 3.5.

**Why it holds here.** The CHECK needs `whole == 3`, so the first operand of `&&` is false and the run stops even though `fraction` is unchanged.

**A plausible wrong approach.** Assuming the original `7 / 2` rounds to 4, so that the edit looks harmless. Integer division in C truncates toward zero, so 7 / 2 is 3 and the edit really changes the value from 3 to 4.

**Verify.** Print `whole` and `fraction` with `%d %.1f` and see `4 3.5` for the edit and `3 3.5` for the original.

## Exercise 2: Observe defined unsigned wrap: debug a regression

A regression changed one token in worked example 2, the "observe defined unsigned wrap" case, so one line now reads `n -= 1U;`. Run the example with that line, use the failing CHECK to find why the result is zero no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
unsigned int n = UINT_MAX;
n += 1U;
CHECK(n == 0U);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `n == 0U`. Once the line reads `n += 1U;` again, the "observe defined unsigned wrap" case again shows that the result is zero.

This result is guaranteed for unsigned arithmetic. Repeating the experiment with INT_MAX would invoke undefined behavior and is not an acceptable runnable example.

**Approach.** Trace the regressed line from `UINT_MAX`: subtracting 1 gives `UINT_MAX - 1`, which on the worker's 32-bit `unsigned int` is 4294967294.

**Why it holds here.** Unsigned arithmetic is defined modulo 2 to the number of value bits, so only `n += 1U` wraps `UINT_MAX` to 0. With `-=` nothing wraps and `n == 0U` fails; restoring `+=` repairs it.

**A plausible wrong approach.** Deciding that unsigned wraparound is unreliable and rewriting the experiment with `int n = INT_MAX; n += 1;`. That is signed overflow, which is undefined behavior, so it trades a defined result for one that must never be executed.

**Verify.** Print `n` with `%u` and see 4294967294 for the regression and 0 after the repair.

## Exercise 3: Inspect representation facts

Check sizeof(char) and minimum CHAR_BIT.

```c
CHECK(sizeof(char) == 1);
CHECK(CHAR_BIT >= 8);
```

**Expected:** A char occupies one char unit and has at least eight bits.

A C byte is defined in char units. Do not silently assume every historical or embedded target has eight-bit bytes.

**Approach.** Check only facts the standard guarantees: `sizeof(char)` is 1 by definition and `CHAR_BIT` is at least 8.

**Why it holds here.** `sizeof` counts in units of `char`, so the first CHECK holds on every implementation, and `<limits.h>` must define `CHAR_BIT` as 8 or more.

**A plausible wrong approach.** Adding `CHECK(sizeof(int) == 4)` as another representation fact. It passes on the Linux worker, but C only requires `int` to hold at least 16 bits, so it records a platform assumption rather than a language rule.

**Verify.** Print `sizeof(char)`, `CHAR_BIT` and `sizeof(int)` with `%zu %d %zu` and see `1 8 4` on the worker; only the first two values are guaranteed, and POSIX additionally fixes `CHAR_BIT` at 8.

## Exercise 4: Widen before multiplication

Multiply two int64_t values of 50000.

```c
int64_t a = 50000;
int64_t b = 50000;
CHECK(a *b == INT64_C(2500000000));
```

**Expected:** The product is 2500000000.

The operand type determines the arithmetic. Casting an already-overflowed signed product afterward cannot repair undefined behavior.

**Approach.** Declare both operands as `int64_t` so the multiplication itself happens in a 64-bit type and produces 2500000000.

**Why it holds here.** The usual arithmetic conversions use the operand types, and 2500000000 fits easily in `int64_t`, so the product compares equal to `INT64_C(2500000000)`.

**A plausible wrong approach.** Keeping the operands as `int` and assigning the result to a wider variable, as in `int a = 50000, b = 50000; int64_t p = a * b;`. The product is computed in `int` first and 2500000000 exceeds `INT_MAX`, so the overflow is undefined before the conversion can help; describe it, do not run it.

**Verify.** Print `(long long)(a * b)` with `%lld` and see 2500000000. Then print `INT_MAX / 50000`, which is 42949: since 50000 is larger, the `int` product would overflow.

## Exercise 5: Check a tiny floating calculation

Add 0.1 and 0.2 and compare to 0.3.

```c
double a = 0.1, b = 0.2;
CHECK(fabs((a + b) - 0.3) < 1e-15);
```

**Expected:** The absolute error is below 1e-15.

The tolerance is appropriate only for this tiny example. Large-scale or iterative calculations need error analysis and nonfinite-value handling.

**Approach.** Compare the computed sum with 0.3 through an absolute tolerance, `fabs((a + b) - 0.3) < 1e-15`.

**Why it holds here.** Neither 0.1 nor 0.2 is exactly representable in binary floating point, and their sum is 0.30000000000000004. The error is about 5.55e-17, comfortably below 1e-15.

**A plausible wrong approach.** Writing `CHECK(a + b == 0.3)`. The nearest doubles do not add up to the double nearest 0.3, so the exact comparison is false and the CHECK fails on a correct calculation.

**Verify.** Print `a + b` with `%.17g` and the error with `%.3g`, and see `0.30000000000000004 5.55e-17`; `a + b == 0.3` prints as 0.

## Exercise 6: Transfer negative division

Divide -7 by 2 and inspect its remainder.

```c
int q = -7 / 2, r = -7 % 2;
CHECK(q == -3 && r == -1 && q * 2 + r == -7);
```

**Expected:** The quotient is -3 and remainder -1.

Truncation toward zero differs from floor division. The reconstruction identity links the quotient and remainder.

**Approach.** Use C's truncating division: -7 / 2 is -3, and the remainder is defined so that `q * 2 + r` equals -7, which makes it -1.

**Why it holds here.** Since C99 the quotient truncates toward zero, and the remainder takes the sign of the dividend, so all three conditions in the CHECK hold.

**A plausible wrong approach.** Expecting floor division as in Python, a quotient of -4 and a remainder of 1. Those values also satisfy the reconstruction identity, but they are not what C computes, so the CHECK on -3 and -1 fails.

**Verify.** Print `-7 / 2`, `-7 % 2` and `floor(-7 / 2.0)` and see `-3 -1 -4`.

## After comparison

Write `bool mul_nonneg(int a, int b, int *out)` for nonnegative operands that returns false when `b != 0 && a > INT_MAX / b` and otherwise stores `a * b`. Check that 4 and 6 store 24, 50000 and 50000 is rejected with `*out` unchanged, 0 and `INT_MAX` store 0, and `INT_MAX` and 1 store `INT_MAX`. Explain why testing `a * b < 0` after multiplying is not a valid overflow check in C.
