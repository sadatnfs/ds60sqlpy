# c-010: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A struct groups named fields into one object. An enum gives meaningful names to integer constants, but it does not automatically prevent every other integer value from appearing in the representation. A tagged union pairs a discriminator with a union whose active interpretation depends on that tag. This can model alternatives without allocating a class hierarchy, but every reader must check the tag before interpreting the stored payload. Struct assignment copies fields, including pointer values rather than their targets. Struct padding and representation are implementation details, so bytewise comparison or raw struct serialization is not a general semantic equality policy.

struct Point names a type unless a typedef adds a shorter alias. A designated initializer uses .field=value. The dot operator accesses a struct value; -> accesses through a struct pointer. A union shares storage among alternatives. Switch on an enum tag and handle unexpected values explicitly. Compare meaningful fields rather than relying on memcmp over padding bytes.

## Exercise 1: Use named fields: change one input

Copy worked example 1 into a scratch pad and change `struct Point p = {.x = 2, .y = 3};` to `struct Point p = {.x = 3, .y = 3};`. Before running, predict which CHECK fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```c
struct Point p = {.x = 2, .y = 3};
CHECK(p.x + p.y == 5);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `p.x + p.y == 5`. Restoring the original line brings back the worked observation: the field sum is 5.

Designated initialization preserves field meaning even if declaration order changes.

## Exercise 2: Copy scalar fields: debug a regression

A regression changed one token in worked example 2, so one line now reads `struct Point a = {3, 3};`. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
struct Point a = {2, 3};
struct Point b = a;
b.x = 9;
CHECK(a.x == 2 && b.x == 9);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `a.x == 2 && b.x == 9`; after it the line reads `struct Point a = {2, 3};` again and the original x stays 2.

Scalar fields are copied into independent struct storage. Pointer fields would still designate their original targets.

## Exercise 3: Interpret an integer alternative

Create a tagged number with an integer payload.

```c
struct Value v = {.tag = VALUE_INT, .data.integer = 7};
CHECK(v.tag == VALUE_INT && v.data.integer == 7);
```

**Expected:** The checked payload is 7.

The tag establishes which union member this design permits the reader to interpret.

## Exercise 4: Interpret a text alternative

Create a tagged value containing a borrowed string.

```c
struct Value v = {.tag = VALUE_TEXT, .data.text = "ready"};
CHECK(v.tag == VALUE_TEXT && strcmp(v.data.text, "ready") == 0);
```

**Expected:** The text is ready.

The text pointer borrows static string-literal storage. A general API would document ownership for dynamically supplied text.

## Exercise 5: Compare semantic fields

Compare two equal Points by x and y.

```c
struct Point a = {2, 3}, b = {2, 3};
CHECK(a.x == b.x && a.y == b.y);
```

**Expected:** Semantic equality is true.

Field comparison ignores padding. C does not supply whole-struct ==, and memcmp can distinguish irrelevant representation bytes.

## Exercise 6: Transfer invalid-tag diagnosis

Pass an unexpected discriminator to a validator.

```c
CHECK(!valid_tag((enum ValueTag)99));
```

**Expected:** The validator rejects it.

An enum name list is not a runtime input validator. External integer data still needs range or membership checks.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
