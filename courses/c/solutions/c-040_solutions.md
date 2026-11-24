# c-040: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-040_solution.c`, implements all six cases, from the "use caller-owned output" case to the "transfer an empty payload" case, in one `main.c`.

## Mechanism and assumptions

An application binary interface describes how compiled components exchange calls, values and symbols. A C function name alone does not define the entire contract: integer widths, struct layout, calling convention, ownership, error reporting and callback lifetime also matter. C interfaces are often used from C++, Rust or managed languages, but each side must agree on representation and who releases returned storage. Prefer explicit lengths and fixed-width types for data crossing the boundary. Do not return pointers to automatic locals or require another language to guess which allocator should free an allocation.

extern declares a function or object defined elsewhere; C++ callers use an extern "C" declaration wrapper to request C linkage. A stable buffer API can accept caller-owned output plus capacity and return a status and required length. Keep structs simple and versioned when they form a public ABI. A foreign pointer must satisfy the same C lifetime, alignment and bounds rules as a native pointer.

## Exercise 1: Use caller-owned output: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);` to `CHECK(copy_api("hello!", out, sizeof out, &required) == API_OK);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
char out[8];
size_t required = 0;
CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);
CHECK(required == 5 && strcmp(out, "hello") == 0);
```

**Expected:** With `CHECK(copy_api("hello!", out, sizeof out, &required) == API_OK);` the run stops with `Check failed` at the CHECK on `required == 5 && strcmp(out, "hello") == 0`, because the "use caller-owned output" case no longer shows that the output is complete and required length is 5. Restoring `CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);` brings that observation back.

Caller-owned storage avoids requiring the foreign runtime to guess a deallocator.

## Exercise 2: Report insufficient capacity: debug a regression

A regression changed one token in worked example 2, the "report insufficient capacity" case, so one line now reads `char out[4] = "old!";`. Run the example with that line, use the failing CHECK to find why the status is too-small and required length is 5 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
char out[4] = "old";
size_t required = 0;
CHECK(copy_api("hello", out, sizeof out, &required) == API_TOO_SMALL);
CHECK(required == 5 && strcmp(out, "old") == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `required == 5 && strcmp(out, "old") == 0`. Once the line reads `char out[4] = "old";` again, the "report insufficient capacity" case again shows that the status is too-small and required length is 5.

The API reports the required payload length and preserves output on failure. The caller must reserve one more byte for termination.

## Exercise 3: Support a size query

Call with no output buffer and capacity zero.

```c
size_t required = 0;
CHECK(copy_api("abc", NULL, 0, &required) == API_TOO_SMALL && required == 3);
```

**Expected:** The required payload length is still reported.

A deliberate size-query mode is useful across language boundaries, but it must be specified rather than inferred from null behavior.

## Exercise 4: Reject a missing required-output pointer

Call without a place to report required length.

```c
char out[4];
CHECK(copy_api("abc", out, sizeof out, NULL) == API_INVALID);
```

**Expected:** The API returns invalid.

Validation precedes dereference. Every pointer parameter has an explicit role and null policy.

## Exercise 5: Keep fixed-width values exact

Pass a uint32_t value through an identity boundary.

```c
uint32_t value = UINT32_C(0x89abcdef);
CHECK(identity_u32(value) == value);
```

**Expected:** All 32 bits remain unchanged.

A foreign declaration must use a compatible unsigned 32-bit representation, not assume that its default integer type matches.

## Exercise 6: Transfer an empty payload

Copy an empty string into one byte.

```c
char out[1];
size_t required = 9;
CHECK(copy_api("", out, sizeof out, &required) == API_OK && required == 0 &&
      out[0] == '\0');
```

**Expected:** The API succeeds and stores a terminator.

The empty payload still requires one writable byte under this null-terminated ABI contract.

## After comparison

Add a fresh distinguishing input for the "transfer an empty payload" case to your own c-040 source. Explain why every access in `copy_api` or `identity_u32` stays within a live object and each owned resource is released. An expected ABI failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "report insufficient capacity" case apart from ordinary output: the fixture proves its stated ABI, calling convention and allocator boundary assumptions, not universal safety.
