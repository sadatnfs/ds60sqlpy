# c-005: explained solutions

`c-005_solution.c` assembles the "call a pure calculation" case through the "transfer overflow prevention" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A function contract names inputs, outputs, side effects and failure behavior. A prototype lets the compiler check calls before seeing the implementation. C passes arguments by value, so changing a scalar parameter does not change its caller. A pointer parameter can permit a function to modify a caller-owned object, but the function must state whether null is accepted and what object size is required. Returning a status plus writing through an output pointer is a common C API pattern. On failure, define whether the output remains unchanged rather than leaving callers to guess.

static limits a file-scope function to its translation unit. A prototype such as int twice(int x) declares parameter and result types. void in an empty parameter list means no parameters in C17. bool try_area(int w,int h,int *out) can report success and provide an output separately. Validate preconditions before writing through out. Returning a pointer to an automatic local object creates a dangling pointer and must not be used.

## Exercise 1: Call a pure calculation: predict an edited check

In worked example 1, change `CHECK(twice(0) == 0);` to `CHECK(twice(1) == 0);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
CHECK(twice(7) == 14);
CHECK(twice(0) == 0);
```

**Expected:** `Check failed`: `CHECK(twice(1) == 0);` is false, although the results are 14 and 0.

The helper has no external state and its tiny input range avoids overflow. A general API would need a stated range.

**Approach.** Evaluate the edited call: `twice(1)` returns 2, and the edited CHECK still expects 0.

**Why it holds here.** `twice` has no hidden state, so its result depends only on the argument. Changing the input from 0 to 1 changes the correct result to 2, and `2 == 0` is false, so the run stops at that CHECK.

**A plausible wrong approach.** Predicting that the CHECK still holds because only the argument changed and the expected value was kept. An expected value belongs to one input; a CHECK whose input changes needs a new expected value, here 2.

**Verify.** Print `twice(1)` and see 2; restore `twice(0)` and the program prints its success line.

## Exercise 2: Return an output on success: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(try_area(4, 4, &out));`. Explain why it fails although success is true and output becomes 12, then restore it.

The unchanged code is worked example 2:

```c
int out = -1;
CHECK(try_area(3, 4, &out));
CHECK(out == 12);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(try_area(3, 4, &out));` again, though success is true and output becomes 12.

The status and result are distinct. The caller checks status before using the new output.

**Approach.** Follow the edited call: `try_area(4, 4, &out)` is a valid request, so it returns true, the edited CHECK passes and `out` becomes 16.

**Why it holds here.** The status CHECK only states that the call succeeded, which it did. The failure appears one statement later, where `out == 12` reads 16, so the reported line number points at the value CHECK, not the edited one.

**A plausible wrong approach.** Expecting the edited CHECK line itself to report the failure. `try_area` accepts every positive pair whose product fits in `int`, so a valid but different request changes the output, not the status.

**Verify.** Print `out` after the edited call and see 16; restore `3, 4` and see 12.

## Exercise 3: Preserve output on rejection

Request area with width zero.

```c
int out = -1;
CHECK(!try_area(0, 4, &out));
CHECK(out == -1);
```

**Expected:** The call fails and output remains -1.

The helper validates before writing. This makes failure behavior predictable and supports retries or alternative handling.

**Approach.** Call `try_area(0, 4, &out)` with `out` preset to -1 and check both the false status and the untouched output.

**Why it holds here.** The helper tests `w <= 0` before it writes, so it returns false and never assigns `*out`, leaving -1 in place.

**A plausible wrong approach.** Computing the product before validating, as in `*out = w * h; return w > 0 && h > 0;`. The status is still false, but `out` now holds 0, so `out == -1` fails and the caller cannot tell a rejected call from a real result.

**Verify.** Print `out` after the call and see -1, and the program reaches its success line.

## Exercise 4: Trace copied scalar state

Pass 5 to a helper that reassigns its parameter.

```c
int value = 5;
reassign(value);
CHECK(value == 5);
```

**Expected:** The caller remains 5.

The function receives a scalar copy. Pointer-based mutation is a different explicit interface.

**Approach.** Pass `value` to `reassign`, which overwrites its own parameter with 99, and check that the caller still sees 5.

**Why it holds here.** C passes a scalar argument by value: `reassign` receives a separate `int` initialized from 5, so assigning 99 to it never touches the caller's object.

**A plausible wrong approach.** Expecting `value` to be 99 after the call, as if the parameter were a reference. A CHECK written as `value == 99` fails; changing the caller requires an `int *` parameter and an explicit `&value` at the call site.

**Verify.** Print `value` after the call and see 5.

## Exercise 5: Reject a missing output target

Call try_area with a null output pointer.

```c
CHECK(!try_area(3, 4, NULL));
```

**Expected:** The call fails without dereferencing it.

This API deliberately accepts null as a rejected input. Other APIs may require non-null, but that precondition must be documented.

**Approach.** Pass `NULL` as the output pointer and expect `try_area` to reject the call before any access.

**Why it holds here.** The first test in the helper is `out == NULL`, and `||` stops at the first true operand, so the function returns false without evaluating anything that dereferences `out`.

**A plausible wrong approach.** Validating only the sizes and then writing `*out = w * h;`. With a null `out` that write is undefined behavior, typically a crash, so it must be described rather than executed; the null test has to come before the first dereference.

**Verify.** Build with `-fsanitize=address,undefined` and run: the CHECK passes with no sanitizer report and the success line prints.

## Exercise 6: Transfer overflow prevention

Request INT_MAX times 2.

```c
int out = 9;
CHECK(!try_area(INT_MAX, 2, &out));
CHECK(out == 9);
```

**Expected:** The operation rejects it and preserves output.

Checking w > INT_MAX/h before multiplication avoids executing signed overflow while deciding whether overflow would occur.

**Approach.** Ask whether `INT_MAX` times 2 fits before multiplying, by comparing `w` with `INT_MAX / h`.

**Why it holds here.** `INT_MAX / 2` is 1073741823 and `w` is `INT_MAX`, so `w > INT_MAX / h` is true, the helper returns false and `out` keeps 9.

**A plausible wrong approach.** Multiplying first and testing the result, for example `int area = w * h; if (area < 0) return false;`. The product overflows, which is undefined behavior, so an optimizer may delete the test entirely; the decision has to be made before the multiplication.

**Verify.** Call `try_area(1073741823, 2, &out)` and see true with `out` equal to 2147483646, the largest accepted product; then call it with 1073741824 and see false with `out` unchanged. Print in separate statements, because argument evaluation order in one `printf` call is unspecified.

## After comparison

Write `bool try_perimeter(int w, int h, int *out)` that rejects a null `out`, nonpositive sides and any pair whose `2 * (w + h)` exceeds `INT_MAX`, testing `w > INT_MAX / 2 - h` before adding, and that leaves `*out` unchanged on rejection. Check 3 and 4 store 14, 0 and 4 is rejected, 1073741822 and 1 store 2147483646, and 1073741823 and 1 are rejected. Explain why computing `w + h` first is unsafe when `w` is `INT_MAX`.
