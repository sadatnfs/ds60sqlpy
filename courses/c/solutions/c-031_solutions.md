# c-031: explained solutions

`c-031_solution.c` assembles the "add ordinary values" case through the "transfer the zero product" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Integer overflow is often a memory-safety defect in disguise. A wrapped allocation size can reserve less storage than later code assumes, and signed overflow cannot safely be used as the condition that detects itself. Validate before the operation using inequalities whose own arithmetic is defined. Keep signed value arithmetic separate from size_t storage arithmetic, and validate conversions at their boundary. The chosen failure policy should preserve outputs and let callers distinguish overflow from a legitimate zero. Compiler overflow builtins can be useful, but portable C17 logic remains worth understanding before depending on a toolchain extension.

For a positive addend b, a+b fits int only when a<=INT_MAX-b. For a negative b, require a>=INT_MIN-b. For size_t multiplication, if b is nonzero require a<=SIZE_MAX/b. Check output pointers before writing. These preconditions avoid evaluating the dangerous expression until its validity is established. A zero multiplier is a valid mathematical case, even when an allocator wrapper later rejects zero-sized storage by policy.

## Exercise 1: Add ordinary values: predict an edited check

In worked example 1, change `CHECK(add_checked(7, 5, &out) && out == 12);` to `CHECK(add_checked(8, 5, &out) && out == 12);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
int out = 0;
CHECK(add_checked(7, 5, &out) && out == 12);
```

**Expected:** `Check failed`: `CHECK(add_checked(8, 5, &out) && out == 12);` is false, although the result is 12.

The normal case uses the same guarded path as boundary cases.

**Approach.** Evaluate both operands: `add_checked(8, 5, &out)` passes both guards and stores 13, then `out == 12` is false.

**Why it holds here.** 8 + 5 is far from either limit, so the function takes the normal path and returns true; the CHECK fails on the comparison, not on overflow.

**A plausible wrong approach.** Inspecting the call with `printf("%d %d", add_checked(8, 5, &out), out);`. The order in which arguments are evaluated is unspecified, so `out` may be read before the call stores 13 and print the old 0.

**Verify.** Print the return value and `out` in separate statements and see 1 and then 13.

## Exercise 2: Reject positive overflow: debug a regression

Worked example 2 now has a line reading `int out = 10;`. Repair it so that the operation fails and preserves output again.

The unchanged code is worked example 2:

```c
int out = 9;
CHECK(!add_checked(INT_MAX, 1, &out) && out == 9);
```

**Expected:** `Check failed` at `!add_checked(INT_MAX, 1, &out) && out == 9` until the line reads `int out = 9;` again.

The addition itself is never evaluated after the precondition fails.

**Approach.** Read the guard: for `b` 1, `a > INT_MAX - b` is `INT_MAX > INT_MAX - 1`, which is true, so the function returns false before any addition and leaves `out` alone.

**Why it holds here.** The function is correct; the regression changed the initial value to 10, so `out == 9` fails until the initializer is 9 again.

**A plausible wrong approach.** Checking after the fact: `int sum = a + b; if (b > 0 && sum < a) return false;`. The addition has already overflowed, which is undefined, so the compiler may assume it did not; Clang at `-O2` compiles that function to an unconditional store and `return true`.

**Verify.** Compile that variant with `-O2 -S` and see that the comparison is gone; run the lesson's version and print `out` as 9.

## Exercise 3: Reject negative overflow

Add negative one to INT_MIN.

```c
int out = 9;
CHECK(!add_checked(INT_MIN, -1, &out) && out == 9);
```

**Expected:** The operation fails without evaluating the overflow.

Checking the negative boundary requires a separate inequality from the positive case.

**Approach.** Use the negative branch: for `b` -1, reject when `a < INT_MIN - b`, which is `INT_MIN < INT_MIN + 1`.

**Why it holds here.** `INT_MIN - b` is `INT_MIN + 1`, which is representable, so the guard itself cannot overflow and the call returns false with `out` still 9.

**A plausible wrong approach.** Reusing the positive test for every `b`, `if (a > INT_MAX - b)`. With `b` -1 the expression `INT_MAX - (-1)` overflows during the check itself, which is undefined, so the guard is not a guard.

**Verify.** Print `add_checked(INT_MIN, -1, &out)` and see 0, then print `out` and see 9.

## Exercise 4: Accept exact boundaries

Add zero to both int extremes.

```c
int out = 0;
CHECK(add_checked(INT_MAX, 0, &out) && out == INT_MAX);
CHECK(add_checked(INT_MIN, 0, &out) && out == INT_MIN);
```

**Expected:** Both exact boundary values are accepted.

An overconservative check that rejects every extreme would violate the valid-domain contract.

**Approach.** Let `b` 0 skip both inequalities, because adding 0 can never overflow.

**Why it holds here.** `b > 0` and `b < 0` are both false, so the function stores `INT_MAX` and then `INT_MIN` and returns true each time.

**A plausible wrong approach.** Writing the positive test with `>=`, `a >= INT_MAX - b`. For `INT_MAX` plus 0 that is `INT_MAX >= INT_MAX`, so a valid sum at the exact boundary is rejected.

**Verify.** Print `add_checked(INT_MAX, 0, &out)` and see 1, then confirm `out == INT_MAX`.

## Exercise 5: Reject a size product

Multiply SIZE_MAX by two through a size helper.

```c
size_t out = 7;
CHECK(!size_product(SIZE_MAX, 2, &out) && out == 7);
```

**Expected:** The helper rejects it and preserves output.

The division comparison avoids wrapping before allocation-size validation.

**Approach.** Compare `a` with `SIZE_MAX / b` before multiplying: `SIZE_MAX` is greater than `SIZE_MAX / 2`, so the product would not fit.

**Why it holds here.** Division cannot overflow, and the inequality is exact for unsigned values, so the helper returns false before computing `a * b` and leaves `out` at 7.

**A plausible wrong approach.** Multiplying first and testing `product < a`. Unsigned multiplication wraps without undefined behavior, but the test misses many wraps: `3 * 2^63` wraps to 9223372036854775808, which is not less than 3. A wrapped size passed to `malloc` allocates far too little.

**Verify.** Print `(size_t)3 * ((size_t)1 << 63)` and see 9223372036854775808, then confirm `size_product(SIZE_MAX, 2, &out)` returns 0.

## Exercise 6: Transfer the zero product

Multiply SIZE_MAX by zero.

```c
size_t out = 7;
CHECK(size_product(SIZE_MAX, 0, &out) && out == 0);
```

**Expected:** The checked mathematical result is zero.

Arithmetic validity and whether a zero-sized allocation is useful are separate policies.

**Approach.** Test `b != 0` before dividing, so a zero factor skips the division and the product 0 is stored.

**Why it holds here.** Any count times 0 is 0, which fits, so the helper returns true with `out` 0.

**A plausible wrong approach.** Dropping the `b != 0` guard, `if (a > SIZE_MAX / b)`. With `b` 0 that divides by zero, which is undefined; on x86-64 it traps with a floating-point exception signal, while on ARM64 it silently yields 0.

**Verify.** Print `size_product(SIZE_MAX, 0, &out)` and `out` in separate statements and see 1 and 0.

## After comparison

Write `void *checked_array_alloc(size_t count, size_t size)` that uses `size_product` and returns `NULL` when it fails or when the product is 0, otherwise `malloc(product)`. Check `count` 4 with `sizeof(int)`, `count` `SIZE_MAX` with size 2, and `count` 0, freeing every non-null pointer. Explain why calling `malloc(count * size)` directly with the second input could return a small block that later writes overrun.
