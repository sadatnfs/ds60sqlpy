# c-008: explained solutions

`c-008_solution.c` assembles the "change a caller-owned value" case through the "transfer a swap contract" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A pointer identifies an object or function, or holds a null value. Dereferencing a pointer requires a live target with appropriate type, alignment and access permissions. C does not keep an object alive merely because a pointer still refers to it. A pointer to an automatic local object becomes invalid when that object lifetime ends. Passing a pointer copies the pointer value, while mutation through it can affect the caller-owned target. Prefer an explicit pointer contract over hidden global state. A null check is necessary for optional pointers, but it cannot prove that a non-null pointer still refers to valid storage.

&object obtains an address and *pointer accesses its target. int *p declares a pointer to int. Parentheses matter: *p += 1 changes the target, while p += 1 changes the pointer position. NULL is a null pointer constant. A function can return a pointer to caller-owned or static storage if its lifetime is documented, but must not return a pointer to an expired automatic local.

## Exercise 1: Change a caller-owned value: change one input

In worked example 1, change `int n = 4;` to `int n = 5;`. Predict which value the CHECK on `n == 5` sees, then run and restore.

The unchanged code is worked example 1:

```c
int n = 4;
increment(&n);
CHECK(n == 5);
```

**Expected:** `Check failed` at `n == 5`; restoring `int n = 4;` passes again.

The helper receives a pointer copy, but that copy still designates the original integer.

**Approach.** Trace the edited input: `n` starts at 5, `increment(&n)` adds 1 through the pointer, so `n` becomes 6 and the CHECK on 5 fails.

**Why it holds here.** The helper receives a copy of the address, and that copy designates the caller's `n`, so `*p += 1` changes the caller's object.

**A plausible wrong approach.** Predicting that the CHECK still passes because C passes arguments by value, so `n` would stay 5. The value that is copied is the pointer, not the integer it points to.

**Verify.** Print `n` after the call and see 6; restore 4 and see 5.

## Exercise 2: Read a target copy: debug a regression

In worked example 2, `int n = 3;` now reads `int n = 4;`. Repair it so that the copied value stays 3 and the target becomes 9 again.

The unchanged code is worked example 2:

```c
int n = 3;
int *p = &n;
int copy = *p;
*p = 9;
CHECK(copy == 3 && n == 9);
```

**Expected:** `Check failed` at `copy == 3 && n == 9` until the line reads `int n = 3;` again.

Dereferencing to obtain an int copies that scalar value. Retaining the pointer would retain access to future target changes.

**Approach.** Trace the regressed line: `copy` is initialized from `*p` while `n` is 4, so `copy` is 4; then `*p = 9` changes only `n`.

**Why it holds here.** `copy` is a separate `int` holding the value read at that moment. The CHECK needs `copy == 3`, which fails because the starting value is wrong, not because the later write reached `copy`.

**A plausible wrong approach.** Suspecting that `*p = 9` also changed `copy` and rewriting the write. `copy` holds no pointer to `n`, so no later store through `p` can change it; the defect is the initializer 4.

**Verify.** Print `copy` and `n` and see `4 9` with the regression and `3 9` after restoring `int n = 3;`.

## Exercise 3: Reject an absent target

Pass NULL to an optional update helper.

```c
CHECK(!set_if_present(NULL, 8));
```

**Expected:** The helper returns false without an access.

Null is a valid absence representation under this helper contract. Other invalid pointers cannot be repaired by this check.

**Approach.** Call `set_if_present(NULL, 8)` and expect false, because the helper tests for null before it writes.

**Why it holds here.** `p == NULL` is true, so the function returns false and the store `*p = value` is never reached.

**A plausible wrong approach.** Writing the helper as `*p = value; return p != NULL;`, testing after the store. Storing through a null pointer is undefined behavior, typically a crash, so the order of the test matters; describe it instead of running it.

**Verify.** Build with `-fsanitize=address,undefined` and run: the CHECK passes with no report.

## Exercise 4: Update a present target

Pass an integer address to the same helper.

```c
int n = 1;
CHECK(set_if_present(&n, 8) && n == 8);
```

**Expected:** The helper returns true and stores 8.

The caller owns the object and keeps it alive throughout the call.

**Approach.** Call `set_if_present(&n, 8)` first and read `n` only after it returns, which is the order `&&` guarantees.

**Why it holds here.** `&&` evaluates its left operand completely, including the store, before the right operand, so `n == 8` sees the new value.

**A plausible wrong approach.** Writing the CHECK as `n == 8 && set_if_present(&n, 8)`. `n` is still 1 when the left operand is evaluated, so `&&` short-circuits, the helper never runs and the CHECK fails with `n` still 1.

**Verify.** Evaluate the reordered expression into a `bool`, print it and `n`, and see `0 1`.

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

**Approach.** Reassign `p` from `&a` to `&b` and check that both integers keep their values while `*p` now reads 7.

**Why it holds here.** Assigning to `p` changes which object it designates. Nothing is stored into `a` or `b`, so they remain 2 and 7.

**A plausible wrong approach.** Writing `*p = b;` instead of `p = &b;`. That stores 7 into `a` through the old pointer, so `a == 2` fails even though `*p` is 7.

**Verify.** Print `a`, `b` and `*p` and see `2 7 7`; the `*p = b` version prints `7 7 7`.

## Exercise 6: Transfer a swap contract

Swap two caller-owned integers through pointers.

```c
int a = 2, b = 7;
swap_ints(&a, &b);
CHECK(a == 7 && b == 2);
```

**Expected:** The values exchange positions.

A temporary preserves the first value before overwriting it. The API requires two valid writable int objects.

**Approach.** Save `*a` in a temporary, copy `*b` into `*a`, then store the saved value into `*b`.

**Why it holds here.** The temporary keeps the original 2 after `*a` is overwritten with 7, so `*b` receives 2 and the CHECK on `7 2` holds. Calling `swap_ints(&a, &a)` also leaves `a` unchanged.

**A plausible wrong approach.** Swapping without a temporary, `*a = *b; *b = *a;`. The first store destroys 2, so both integers end as 7 and `b == 2` fails.

**Verify.** Print `a` and `b` and see `7 2`; the version without the temporary prints `7 7`.

## After comparison

Write `bool min_max(const int *values, size_t count, int *lo, int *hi)` that rejects null pointers and a count of 0, leaves both outputs unchanged on rejection, and starts both running values at `values[0]`. Check that `{4, -2, 9}` gives -2 and 9, a single element `{5}` gives 5 for both, count 0 is rejected and a null `hi` is rejected. Explain which result a version that starts the running minimum at 0 gets wrong for `{4, 9}`.
