# c-031: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Integer overflow is often a memory-safety defect in disguise. A wrapped allocation size can reserve less storage than later code assumes, and signed overflow cannot safely be used as the condition that detects itself. Validate before the operation using inequalities whose own arithmetic is defined. Keep signed value arithmetic separate from size_t storage arithmetic, and validate conversions at their boundary. The chosen failure policy should preserve outputs and let callers distinguish overflow from a legitimate zero. Compiler overflow builtins can be useful, but portable C17 logic remains worth understanding before depending on a toolchain extension.

For a positive addend b, a+b fits int only when a<=INT_MAX-b. For a negative b, require a>=INT_MIN-b. For size_t multiplication, if b is nonzero require a<=SIZE_MAX/b. Check output pointers before writing. These preconditions avoid evaluating the dangerous expression until its validity is established. A zero multiplier is a valid mathematical case, even when an allocator wrapper later rejects zero-sized storage by policy.

## Exercise 1: Add ordinary values

Add 7 and 5 through the checked helper.

```c
int out = 0;
CHECK(add_checked(7, 5, &out) && out == 12);
```

**Expected:** The result is 12.

The normal case uses the same guarded path as boundary cases.

## Exercise 2: Reject positive overflow

Add one to INT_MAX.

```c
int out = 9;
CHECK(!add_checked(INT_MAX, 1, &out) && out == 9);
```

**Expected:** The operation fails and preserves output.

The addition itself is never evaluated after the precondition fails.

## Exercise 3: Reject negative overflow

Add negative one to INT_MIN.

```c
int out = 9;
CHECK(!add_checked(INT_MIN, -1, &out) && out == 9);
```

**Expected:** The operation fails without evaluating the overflow.

Checking the negative boundary requires a separate inequality from the positive case.

## Exercise 4: Accept exact boundaries

Add zero to both int extremes.

```c
int out = 0;
CHECK(add_checked(INT_MAX, 0, &out) && out == INT_MAX);
CHECK(add_checked(INT_MIN, 0, &out) && out == INT_MIN);
```

**Expected:** Both exact boundary values are accepted.

An overconservative check that rejects every extreme would violate the valid-domain contract.

## Exercise 5: Reject a size product

Multiply SIZE_MAX by two through a size helper.

```c
size_t out = 7;
CHECK(!size_product(SIZE_MAX, 2, &out) && out == 7);
```

**Expected:** The helper rejects it and preserves output.

The division comparison avoids wrapping before allocation-size validation.

## Exercise 6: Transfer the zero product

Multiply SIZE_MAX by zero.

```c
size_t out = 7;
CHECK(size_product(SIZE_MAX, 0, &out) && out == 0);
```

**Expected:** The checked mathematical result is zero.

Arithmetic validity and whether a zero-sized allocation is useful are separate policies.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
