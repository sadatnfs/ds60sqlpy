# c-027: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-027_solution.c`, implements all six cases, from the "exercise successful allocation" case to the "transfer a distinguishing content check" case, in one `main.c`.

## Mechanism and assumptions

Reliable tests target plausible defects rather than mirror the implementation line for line. A normal result, an exact boundary, malformed input and resource failure often exercise different contracts. Allocation failure is difficult to reproduce by exhausting real machine memory and should not be forced on a shared system. Inject a controlled allocator interface instead. The fake can fail on a selected call while recording ownership counts, making cleanup behavior deterministic. Such a fake proves local error-path logic, not the operating system allocator or every interleaving. Keep sanitizer and real integration evidence separate.

A function pointer supplies allocation behavior. The fixture allocator either delegates to malloc or returns NULL according to an explicit flag. The component validates and allocates before modifying the caller output pointer. Tests retain the previous output on failure. A useful oracle checks both the returned status and absence of unintended state changes; a nonzero exit alone cannot explain which invariant was violated.

## Exercise 1: Exercise successful allocation: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` to `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
char *out = NULL;
fail_allocation = false;
CHECK(copy_with_allocator("abc", &out, controlled_alloc));
CHECK(strcmp(out, "abc") == 0);
free(out);
```

**Expected:** With `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` the run stops with `Check failed` at the CHECK on `strcmp(out, "abc") == 0`, because the "exercise successful allocation" case no longer shows that the output owns an equal string. Restoring `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` brings that observation back.

The test checks content and then releases the owned result.

## Exercise 2: Inject allocation failure: debug a regression

A regression changed `fail_allocation = true;` to `fail_allocation = false;` in worked example 2, the "inject allocation failure" case. Run the example with that change, use the failing CHECK to explain why the copy fails and output remains NULL no longer holds and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
char *out = NULL;
fail_allocation = true;
CHECK(!copy_with_allocator("abc", &out, controlled_alloc));
CHECK(out == NULL);
fail_allocation = false;
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!copy_with_allocator("abc", &out, controlled_alloc)`. Once the line reads `fail_allocation = true;` again, the "inject allocation failure" case again shows that the copy fails and output remains NULL.

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

A weak length-only check would accept the wrong letters. Choose an oracle strong enough to reject the relevant defect.

## After comparison

Add a fresh distinguishing input for the "transfer a distinguishing content check" case to your own c-027 source. Explain why every access in `controlled_alloc` or `copy_with_allocator` stays within a live object and each owned resource is released. An expected fault injection failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "inject allocation failure" case apart from ordinary output: the fixture proves its stated fault injection, test oracle and failure-path coverage assumptions, not universal safety.
