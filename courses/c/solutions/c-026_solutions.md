# c-026: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Building text incrementally requires an invariant connecting length, capacity and termination. A valid builder keeps length below capacity and stores a null character at data[length]. An append must prove enough remaining space for both payload and terminator before copying. Failure should preserve the existing valid string rather than leave a half-written result that looks complete. Avoid repeated strcat scans when the current length is already known. This fixed-capacity builder makes the resource budget visible and rejects overflow; a dynamic builder would additionally need allocation failure and pointer-invalidation policies.

The builder owns a fixed character array and a length. append_text obtains the source length, checks it against capacity-1-length, then copies payload plus terminator with memcpy. The subtraction form avoids overflowing length+incoming+1. Source and destination must not overlap for this helper. Initial zero state is a valid empty string, which makes construction and cleanup simple.

## Exercise 1: Append two fragments

Append red then space sky.

```c
struct Builder b = {0};
CHECK(append_text(&b, "red") && append_text(&b, " sky"));
CHECK(b.len == 7 && strcmp(b.data, "red sky") == 0);
```

**Expected:** The result is red sky with length 7.

The stored length avoids rescanning previous content before every append.

## Exercise 2: Append empty text

Append an empty fragment to abc.

```c
struct Builder b = {0};
CHECK(append_text(&b, "abc") && append_text(&b, ""));
CHECK(b.len == 3 && strcmp(b.data, "abc") == 0);
```

**Expected:** Length and content remain unchanged.

The empty append is a successful no-op, not an error or a new terminator-free state.

## Exercise 3: Fill to exact payload capacity

Append fifteen characters to capacity sixteen.

```c
struct Builder b = {0};
CHECK(append_text(&b, "123456789012345"));
CHECK(b.len == 15 && b.data[15] == '\0');
```

**Expected:** The complete payload fits and remains terminated.

The final storage byte belongs to the terminator. Payload capacity is one less than total capacity.

## Exercise 4: Reject one extra character

Fill the builder then append x.

```c
struct Builder b = {0};
CHECK(append_text(&b, "123456789012345"));
CHECK(!append_text(&b, "x"));
CHECK(b.len == 15 && strcmp(b.data, "123456789012345") == 0);
```

**Expected:** The append fails without changing prior content.

The bound is checked before copying, preserving a valid complete previous result.

## Exercise 5: Reject an oversized first fragment

Try a fragment longer than payload capacity.

```c
struct Builder b = {0};
CHECK(!append_text(&b, "1234567890123456"));
CHECK(b.len == 0 && b.data[0] == '\0');
```

**Expected:** The builder remains an empty valid string.

A failed first append should not leave a misleading truncated result.

## Exercise 6: Transfer a delimiter protocol

Build a,b,c with explicit separators.

```c
struct Builder b = {0};
CHECK(append_text(&b, "a") && append_text(&b, ",") && append_text(&b, "b") &&
      append_text(&b, ",") && append_text(&b, "c"));
CHECK(strcmp(b.data, "a,b,c") == 0);
```

**Expected:** The exact result is a,b,c.

This is a fixed synthetic delimiter example. General CSV output needs quoting rules, not simple separator insertion.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
