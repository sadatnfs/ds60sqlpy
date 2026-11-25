# c-027: explained solutions

`c-027_solution.c` assembles the "exercise successful allocation" case through the "transfer a distinguishing content check" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Reliable tests target plausible defects rather than mirror the implementation line for line. A normal result, an exact boundary, malformed input and resource failure often exercise different contracts. Allocation failure is difficult to reproduce by exhausting real machine memory and should not be forced on a shared system. Inject a controlled allocator interface instead. The fake can fail on a selected call while recording ownership counts, making cleanup behavior deterministic. Such a fake proves local error-path logic, not the operating system allocator or every interleaving. Keep sanitizer and real integration evidence separate.

A function pointer supplies allocation behavior. The fixture allocator either delegates to malloc or returns NULL according to an explicit flag. The component validates and allocates before modifying the caller output pointer. Tests retain the previous output on failure. A useful oracle checks both the returned status and absence of unintended state changes; a nonzero exit alone cannot explain which invariant was violated.

## Exercise 1: Exercise successful allocation: predict an edited check

In worked example 1, change `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` to `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
char *out = NULL;
fail_allocation = false;
CHECK(copy_with_allocator("abc", &out, controlled_alloc));
CHECK(strcmp(out, "abc") == 0);
free(out);
```

**Expected:** `Check failed`: `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` is false, although the output owns an equal string.

**Verify:** Explain which claim `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` makes that the state fails; restoring `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` passes again.

The test checks content and then releases the owned result.

## Exercise 2: Inject allocation failure: debug a regression

In worked example 2, `fail_allocation = true;` now reads `fail_allocation = false;`. Repair it so that the copy fails and output remains NULL again.

The unchanged code is worked example 2:

```c
char *out = NULL;
fail_allocation = true;
CHECK(!copy_with_allocator("abc", &out, controlled_alloc));
CHECK(out == NULL);
fail_allocation = false;
```

**Expected:** `Check failed` at `!copy_with_allocator("abc", &out, controlled_alloc)` until the line reads `fail_allocation = true;` again.

**Verify:** Explain how `fail_allocation = false;` changes the value `!copy_with_allocator("abc", &out, controlled_alloc)` tests, using your failing and repaired runs.

No real memory pressure is required. The failure is reproducible and isolated to this operation.

## Exercise 3: Preserve an existing output pointer

Fail allocation while output points to a separate valid buffer.

```c
char existing[] = "old";
char *out = existing;
fail_allocation = true;
CHECK(!copy_with_allocator("new", &out, controlled_alloc));
CHECK(out == existing && strcmp(out, "old") == 0);
fail_allocation = false;
```

**Expected:** The output pointer remains unchanged.

**Verify:** Keep a CHECK equivalent to `out == existing && strcmp(out, "old") == 0`. Control edit: changing `char existing[] = "old";` to `char existing[] = "old!";` must fail it; then restore it.

The component does not erase caller state before it knows it can return a successful replacement.

## Exercise 4: Test an empty valid input

Copy empty text through the working allocator.

```c
char *out = NULL;
CHECK(copy_with_allocator("", &out, controlled_alloc));
CHECK(out != NULL && out[0] == '\0');
free(out);
```

**Expected:** A valid empty owned string is returned.

**Verify:** Keep a CHECK equivalent to `out != NULL && out[0] == '\0'`. Control edit: `CHECK(out == NULL && out[0] == '\0');` must fail; then restore it.

The allocation includes the terminator even when payload length is zero.

## Exercise 5: Retain a normal case after failure

Run one failing call followed by a successful call.

```c
char *out = NULL;
fail_allocation = true;
CHECK(!copy_with_allocator("x", &out, controlled_alloc));
fail_allocation = false;
CHECK(copy_with_allocator("x", &out, controlled_alloc));
CHECK(strcmp(out, "x") == 0);
free(out);
```

**Expected:** The later call succeeds independently.

**Verify:** Keep a CHECK equivalent to `strcmp(out, "x") == 0`. Control edit: `CHECK(copy_with_allocator("x!", &out, controlled_alloc));` must fail; then restore it.

Failure must not leave hidden component state that poisons the next invocation.

## Exercise 6: Transfer a distinguishing content check

Copy case-sensitive text and compare exact content.

```c
char *out = NULL;
CHECK(copy_with_allocator("Red", &out, controlled_alloc));
CHECK(strcmp(out, "Red") == 0 && strcmp(out, "red") != 0);
free(out);
```

**Expected:** Red remains different from red.

**Verify:** Keep a CHECK equivalent to `strcmp(out, "Red") == 0 && strcmp(out, "red") != 0`. Control edit: `CHECK(copy_with_allocator("Red!", &out, controlled_alloc));` must fail; then restore it.

A weak length-only check would accept the wrong letters. Choose an oracle strong enough to reject the relevant defect.

## After comparison

Replace `controlled_alloc` with a counting allocator that increments a counter on every successful call. CHECK that one successful copy makes exactly one allocation and that an injected failure makes none. Then explain why this oracle rejects a helper that allocates twice per copy and leaks the first block, a defect that content checks with `strcmp` cannot see.
