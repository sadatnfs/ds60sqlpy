# c-002: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

An integer type has a finite range. C guarantees minimum ranges for fundamental integer types, not that int has one universal size. Fixed-width types from stdint.h exist when the implementation supports exactly those widths. Unsigned arithmetic is defined modulo one more than its maximum value; signed overflow is undefined behavior. That difference is a semantic rule, not an invitation to guess CPU wraparound. Floating-point types approximate many real numbers and need deliberate comparison policies. Conversion can lose information even when the source program compiles without an error.

sizeof reports a size in char units, and sizeof(char) is always one; CHAR_BIT gives bits per char. INT_MAX and UINT_MAX expose implementation limits. A U suffix creates an unsigned integer constant. Integer division truncates toward zero. Convert an operand before division when a fractional result is required. fabs computes an absolute floating difference; a tolerance is specific to the numerical problem.

## Exercise 1: Compare integer and floating division

Compute 7/2 and 7/2.0.

```c
int whole = 7 / 2;
double fraction = 7 / 2.0;
CHECK(whole == 3 && fraction == 3.5);
```

**Expected:** The results are 3 and 3.5.

Converting the already truncated integer result afterward cannot restore the missing fraction.

## Exercise 2: Observe defined unsigned wrap

Add one to UINT_MAX in unsigned arithmetic.

```c
unsigned int n = UINT_MAX;
n += 1U;
CHECK(n == 0U);
```

**Expected:** The result is zero.

This result is guaranteed for unsigned arithmetic. Repeating the experiment with INT_MAX would invoke undefined behavior and is not an acceptable runnable example.

## Exercise 3: Inspect representation facts

Check sizeof(char) and minimum CHAR_BIT.

```c
CHECK(sizeof(char) == 1);
CHECK(CHAR_BIT >= 8);
```

**Expected:** A char occupies one char unit and has at least eight bits.

A C byte is defined in char units. Do not silently assume every historical or embedded target has eight-bit bytes.

## Exercise 4: Widen before multiplication

Multiply two int64_t values of 50000.

```c
int64_t a = 50000;
int64_t b = 50000;
CHECK(a *b == INT64_C(2500000000));
```

**Expected:** The product is 2500000000.

The operand type determines the arithmetic. Casting an already-overflowed signed product afterward cannot repair undefined behavior.

## Exercise 5: Check a tiny floating calculation

Add 0.1 and 0.2 and compare to 0.3.

```c
double a = 0.1, b = 0.2;
CHECK(fabs((a + b) - 0.3) < 1e-15);
```

**Expected:** The absolute error is below 1e-15.

The tolerance is appropriate only for this tiny example. Large-scale or iterative calculations need error analysis and nonfinite-value handling.

## Exercise 6: Transfer negative division

Divide -7 by 2 and inspect its remainder.

```c
int q = -7 / 2, r = -7 % 2;
CHECK(q == -3 && r == -1 && q * 2 + r == -7);
```

**Expected:** The quotient is -3 and remainder -1.

Truncation toward zero differs from floor division. The reconstruction identity links the quotient and remainder.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
