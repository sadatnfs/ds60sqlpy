# c-040: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

An application binary interface describes how compiled components exchange calls, values and symbols. A C function name alone does not define the entire contract: integer widths, struct layout, calling convention, ownership, error reporting and callback lifetime also matter. C interfaces are often used from C++, Rust or managed languages, but each side must agree on representation and who releases returned storage. Prefer explicit lengths and fixed-width types for data crossing the boundary. Do not return pointers to automatic locals or require another language to guess which allocator should free an allocation.

extern declares a function or object defined elsewhere; C++ callers use an extern "C" declaration wrapper to request C linkage. A stable buffer API can accept caller-owned output plus capacity and return a status and required length. Keep structs simple and versioned when they form a public ABI. A foreign pointer must satisfy the same C lifetime, alignment and bounds rules as a native pointer.

## Exercise 1: Use caller-owned output

Copy hello into sufficient caller storage through a status API.

```c
char out[8];
size_t required = 0;
CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);
CHECK(required == 5 && strcmp(out, "hello") == 0);
```

**Expected:** The output is complete and required length is 5.

Caller-owned storage avoids requiring the foreign runtime to guess a deallocator.

## Exercise 2: Report insufficient capacity

Request the same copy into four bytes.

```c
char out[4] = "old";
size_t required = 0;
CHECK(copy_api("hello", out, sizeof out, &required) == API_TOO_SMALL);
CHECK(required == 5 && strcmp(out, "old") == 0);
```

**Expected:** The status is too-small and required length is 5.

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

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
