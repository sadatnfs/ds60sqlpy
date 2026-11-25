# c-026: explained solutions

`c-026_solution.c` assembles the "append two fragments" case through the "transfer a delimiter protocol" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Building text incrementally requires an invariant connecting length, capacity and termination. A valid builder keeps length below capacity and stores a null character at data[length]. An append must prove enough remaining space for both payload and terminator before copying. Failure should preserve the existing valid string rather than leave a half-written result that looks complete. Avoid repeated strcat scans when the current length is already known. This fixed-capacity builder makes the resource budget visible and rejects overflow; a dynamic builder would additionally need allocation failure and pointer-invalidation policies.

The builder owns a fixed character array and a length. append_text obtains the source length, checks it against capacity-1-length, then copies payload plus terminator with memcpy. The subtraction form avoids overflowing length+incoming+1. Source and destination must not overlap for this helper. Initial zero state is a valid empty string, which makes construction and cleanup simple.

## Exercise 1: Append two fragments: predict an edited check

In worked example 1, change `CHECK(append_text(&b, "red") && append_text(&b, " sky"));` to `CHECK(append_text(&b, "red!") && append_text(&b, " sky"));`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
struct Builder b = {0};
CHECK(append_text(&b, "red") && append_text(&b, " sky"));
CHECK(b.len == 7 && strcmp(b.data, "red sky") == 0);
```

**Expected:** `Check failed`: `CHECK(append_text(&b, "red!") && append_text(&b, " sky"));` is false, although the result is red sky with length 7.

**Verify:** Explain which claim `CHECK(append_text(&b, "red!") && append_text(&b, " sky"));` makes that the state fails; restoring `CHECK(append_text(&b, "red") && append_text(&b, " sky"));` passes again.

The stored length avoids rescanning previous content before every append.

## Exercise 2: Append empty text: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(append_text(&b, "abc!") && append_text(&b, ""));`. Explain why it fails although length and content remain unchanged, then restore it.

The unchanged code is worked example 2:

```c
struct Builder b = {0};
CHECK(append_text(&b, "abc") && append_text(&b, ""));
CHECK(b.len == 3 && strcmp(b.data, "abc") == 0);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(append_text(&b, "abc") && append_text(&b, ""));` again, though length and content remain unchanged.

**Verify:** Explain why `CHECK(append_text(&b, "abc!") && append_text(&b, ""));` rejects a state that `b.len == 3 && strcmp(b.data, "abc") == 0` accepts, using your failing and repaired runs.

The empty append is a successful no-op, not an error or a new terminator-free state.

## Exercise 3: Fill to exact payload capacity

Append fifteen characters to capacity sixteen.

```c
struct Builder b = {0};
CHECK(append_text(&b, "123456789012345"));
CHECK(b.len == 15 && b.data[15] == '\0');
```

**Expected:** The complete payload fits and remains terminated.

**Verify:** Keep a CHECK equivalent to `append_text(&b, "123456789012345")`. Control edit: `CHECK(append_text(&b, "123456789012345!"));` must fail; then restore it.

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

**Verify:** Keep a CHECK equivalent to `b.len == 15 && strcmp(b.data, "123456789012345") == 0`. Control edit: `CHECK(append_text(&b, "123456789012346"));` must fail; then restore it.

The bound is checked before copying, preserving a valid complete previous result.

## Exercise 5: Reject an oversized first fragment

Try a fragment longer than payload capacity.

```c
struct Builder b = {0};
CHECK(!append_text(&b, "1234567890123456"));
CHECK(b.len == 0 && b.data[0] == '\0');
```

**Expected:** The builder remains an empty valid string.

**Verify:** Keep a CHECK equivalent to `b.len == 0 && b.data[0] == '\0'`. Control edit: changing `struct Builder b = {0};` to `struct Builder b = {1};` must fail it; then restore it.

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

**Verify:** Keep a CHECK equivalent to `strcmp(b.data, "a,b,c") == 0`. Control edit: `CHECK(append_text(&b, "a!") && append_text(&b, ",") && append_text(&b, "b") &&` must fail; then restore it.

This is a fixed synthetic delimiter example. General CSV output needs quoting rules, not simple separator insertion.

## After comparison

Append the ten characters `abcdefghij`, then try to append `klmnop`. The builder holds 15 payload characters, so the six-character append must fail and leave exactly `abcdefghij` with its terminator; CHECK both. Then append `klmno` and CHECK that the exact-capacity result is accepted. Explain why copying `klmno` before discovering that `p` does not fit would break failure atomicity.
