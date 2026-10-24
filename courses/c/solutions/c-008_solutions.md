# c-008: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A pointer identifies an object or function, or holds a null value. Dereferencing a pointer requires a live target with appropriate type, alignment and access permissions. C does not keep an object alive merely because a pointer still refers to it. A pointer to an automatic local object becomes invalid when that object lifetime ends. Passing a pointer copies the pointer value, while mutation through it can affect the caller-owned target. Prefer an explicit pointer contract over hidden global state. A null check is necessary for optional pointers, but it cannot prove that a non-null pointer still refers to valid storage.

&object obtains an address and *pointer accesses its target. int *p declares a pointer to int. Parentheses matter: *p += 1 changes the target, while p += 1 changes the pointer position. NULL is a null pointer constant. A function can return a pointer to caller-owned or static storage if its lifetime is documented, but must not return a pointer to an expired automatic local.

## Exercise 1: Change a caller-owned value

Increment integer 4 through its address.

```c
int n = 4;
increment(&n);
CHECK(n == 5);
```

**Expected:** The caller value becomes 5.

The helper receives a pointer copy, but that copy still designates the original integer.

## Exercise 2: Read a target copy

Copy the integer behind a pointer, then change the target.

```c
int n = 3;
int *p = &n;
int copy = *p;
*p = 9;
CHECK(copy == 3 && n == 9);
```

**Expected:** The copied value stays 3 and the target becomes 9.

Dereferencing to obtain an int copies that scalar value. Retaining the pointer would retain access to future target changes.

## Exercise 3: Reject an absent target

Pass NULL to an optional update helper.

```c
CHECK(!set_if_present(NULL, 8));
```

**Expected:** The helper returns false without an access.

Null is a valid absence representation under this helper contract. Other invalid pointers cannot be repaired by this check.

## Exercise 4: Update a present target

Pass an integer address to the same helper.

```c
int n = 1;
CHECK(set_if_present(&n, 8) && n == 8);
```

**Expected:** The helper returns true and stores 8.

The caller owns the object and keeps it alive throughout the call.

## Exercise 5: Distinguish pointer and target change

Point p at a, then reassign p to b.

```c
int a = 2, b = 7;
int *p = &a;
p = &b;
CHECK(a == 2 && b == 7 && *p == 7);
```

**Expected:** Neither integer changes merely because p changes.

Pointer assignment changes which object is designated. It is not a write to either prior or new target.

## Exercise 6: Transfer a swap contract

Swap two caller-owned integers through pointers.

```c
int a = 2, b = 7;
swap_ints(&a, &b);
CHECK(a == 7 && b == 2);
```

**Expected:** The values exchange positions.

A temporary preserves the first value before overwriting it. The API requires two valid writable int objects.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
