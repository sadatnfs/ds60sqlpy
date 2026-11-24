# c-026: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-026_solution.c`, implements all six cases, from the "append two fragments" case to the "transfer a delimiter protocol" case, in one `main.c`.

## Mechanism and assumptions

Building text incrementally requires an invariant connecting length, capacity and termination. A valid builder keeps length below capacity and stores a null character at data[length]. An append must prove enough remaining space for both payload and terminator before copying. Failure should preserve the existing valid string rather than leave a half-written result that looks complete. Avoid repeated strcat scans when the current length is already known. This fixed-capacity builder makes the resource budget visible and rejects overflow; a dynamic builder would additionally need allocation failure and pointer-invalidation policies.

The builder owns a fixed character array and a length. append_text obtains the source length, checks it against capacity-1-length, then copies payload plus terminator with memcpy. The subtraction form avoids overflowing length+incoming+1. Source and destination must not overlap for this helper. Initial zero state is a valid empty string, which makes construction and cleanup simple.

## Exercise 1: Append two fragments: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(append_text(&b, "red") && append_text(&b, " sky"));` to `CHECK(append_text(&b, "red!") && append_text(&b, " sky"));` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
struct Builder b = {0};
CHECK(append_text(&b, "red") && append_text(&b, " sky"));
CHECK(b.len == 7 && strcmp(b.data, "red sky") == 0);
```

**Expected:** With `CHECK(append_text(&b, "red!") && append_text(&b, " sky"));` the run stops with `Check failed` at the CHECK on `b.len == 7 && strcmp(b.data, "red sky") == 0`, because the "append two fragments" case no longer shows that the result is red sky with length 7. Restoring `CHECK(append_text(&b, "red") && append_text(&b, " sky"));` brings that observation back.

The stored length avoids rescanning previous content before every append.

## Exercise 2: Append empty text: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "append empty text" case, so that it reads `CHECK(append_text(&b, "abc!") && append_text(&b, ""));`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means length and content remain unchanged, and restore it.

The unchanged code is worked example 2:

```c
struct Builder b = {0};
CHECK(append_text(&b, "abc") && append_text(&b, ""));
CHECK(b.len == 3 && strcmp(b.data, "abc") == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `b.len == 3 && strcmp(b.data, "abc") == 0`. Once the line reads `CHECK(append_text(&b, "abc") && append_text(&b, ""));` again, the "append empty text" case again shows that length and content remain unchanged.

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

Add a fresh distinguishing input for the "transfer a delimiter protocol" case to your own c-026 source. Explain why every access in `append_text` stays within a live object and each owned resource is released. An expected builder invariant failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "append empty text" case apart from ordinary output: the fixture proves its stated builder invariant, failure-atomic append and overlap contract assumptions, not universal safety.
