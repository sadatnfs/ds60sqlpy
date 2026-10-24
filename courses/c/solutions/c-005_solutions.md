# c-005: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A function contract names inputs, outputs, side effects and failure behavior. A prototype lets the compiler check calls before seeing the implementation. C passes arguments by value, so changing a scalar parameter does not change its caller. A pointer parameter can permit a function to modify a caller-owned object, but the function must state whether null is accepted and what object size is required. Returning a status plus writing through an output pointer is a common C API pattern. On failure, define whether the output remains unchanged rather than leaving callers to guess.

static limits a file-scope function to its translation unit. A prototype such as int twice(int x) declares parameter and result types. void in an empty parameter list means no parameters in C17. bool try_area(int w,int h,int *out) can report success and provide an output separately. Validate preconditions before writing through out. Returning a pointer to an automatic local object creates a dangling pointer and must not be used.

## Exercise 1: Call a pure calculation

Evaluate twice for 7 and 0.

```c
CHECK(twice(7) == 14);
CHECK(twice(0) == 0);
```

**Expected:** The results are 14 and 0.

The helper has no external state and its tiny input range avoids overflow. A general API would need a stated range.

## Exercise 2: Return an output on success

Calculate area for width 3 and height 4.

```c
int out = -1;
CHECK(try_area(3, 4, &out));
CHECK(out == 12);
```

**Expected:** Success is true and output becomes 12.

The status and result are distinct. The caller checks status before using the new output.

## Exercise 3: Preserve output on rejection

Request area with width zero.

```c
int out = -1;
CHECK(!try_area(0, 4, &out));
CHECK(out == -1);
```

**Expected:** The call fails and output remains -1.

The helper validates before writing. This makes failure behavior predictable and supports retries or alternative handling.

## Exercise 4: Trace copied scalar state

Pass 5 to a helper that reassigns its parameter.

```c
int value = 5;
reassign(value);
CHECK(value == 5);
```

**Expected:** The caller remains 5.

The function receives a scalar copy. Pointer-based mutation is a different explicit interface.

## Exercise 5: Reject a missing output target

Call try_area with a null output pointer.

```c
CHECK(!try_area(3, 4, NULL));
```

**Expected:** The call fails without dereferencing it.

This API deliberately accepts null as a rejected input. Other APIs may require non-null, but that precondition must be documented.

## Exercise 6: Transfer overflow prevention

Request INT_MAX times 2.

```c
int out = 9;
CHECK(!try_area(INT_MAX, 2, &out));
CHECK(out == 9);
```

**Expected:** The operation rejects it and preserves output.

Checking w > INT_MAX/h before multiplication avoids executing signed overflow while deciding whether overflow would occur.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
