# c-010: explained solutions

`c-010_solution.c` assembles the "use named fields" case through the "transfer invalid-tag diagnosis" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A struct groups named fields into one object. An enum gives meaningful names to integer constants, but it does not automatically prevent every other integer value from appearing in the representation. A tagged union pairs a discriminator with a union whose active interpretation depends on that tag. This can model alternatives without allocating a class hierarchy, but every reader must check the tag before interpreting the stored payload. Struct assignment copies fields, including pointer values rather than their targets. Struct padding and representation are implementation details, so bytewise comparison or raw struct serialization is not a general semantic equality policy.

struct Point names a type unless a typedef adds a shorter alias. A designated initializer uses .field=value. The dot operator accesses a struct value; -> accesses through a struct pointer. A union shares storage among alternatives. Switch on an enum tag and handle unexpected values explicitly. Compare meaningful fields rather than relying on memcmp over padding bytes.

## Exercise 1: Use named fields: change one input

In worked example 1, change `struct Point p = {.x = 2, .y = 3};` to `struct Point p = {.x = 3, .y = 3};`. Predict which value the CHECK on `p.x + p.y == 5` sees, then run and restore.

The unchanged code is worked example 1:

```c
struct Point p = {.x = 2, .y = 3};
CHECK(p.x + p.y == 5);
```

**Expected:** `Check failed` at `p.x + p.y == 5`; restoring `struct Point p = {.x = 2, .y = 3};` passes again.

Designated initialization preserves field meaning even if declaration order changes.

**Approach.** Evaluate the edited initializer: `.x = 3` and `.y = 3` give a field sum of 6, so the CHECK on 5 fails.

**Why it holds here.** Designated initializers bind each value to the named field, so the edit changes exactly `p.x`, and the sum changes from 5 to 6.

**A plausible wrong approach.** Treating the sum CHECK as proof that the fields were assigned correctly. `{.x = 3, .y = 2}` also sums to 5 and passes, so a swapped pair goes unnoticed; when field identity matters, check `p.x == 2 && p.y == 3`.

**Verify.** Print `p.x` and `p.y` and see `3 3` for the edit and `2 3` for the original.

## Exercise 2: Copy scalar fields: debug a regression

Worked example 2 now has a line reading `struct Point a = {3, 3};`. Repair it so that the original x stays 2 again.

The unchanged code is worked example 2:

```c
struct Point a = {2, 3};
struct Point b = a;
b.x = 9;
CHECK(a.x == 2 && b.x == 9);
```

**Expected:** `Check failed` at `a.x == 2 && b.x == 9` until the line reads `struct Point a = {2, 3};` again.

Scalar fields are copied into independent struct storage. Pointer fields would still designate their original targets.

**Approach.** Trace the regressed initializer: `a` starts as `{3, 3}`, `b = a` copies both fields, and `b.x = 9` changes only `b`.

**Why it holds here.** Struct assignment copies every member into `b`'s own storage, so `a.x` stays at its initial 3, and `a.x == 2` fails because of the initializer, not because of the later write.

**A plausible wrong approach.** Suspecting that `b.x = 9` wrote through to `a`, as with a reference type in other languages, and changing the assignment. C struct assignment copies values; only pointer members would still share a target.

**Verify.** Print `a.x` and `b.x` and see `3 9` with the regression and `2 9` after restoring `{2, 3}`.

## Exercise 3: Interpret an integer alternative

Create a tagged number with an integer payload.

```c
struct Value v = {.tag = VALUE_INT, .data.integer = 7};
CHECK(v.tag == VALUE_INT && v.data.integer == 7);
```

**Expected:** The checked payload is 7.

The tag establishes which union member this design permits the reader to interpret.

**Approach.** Store the integer alternative with `.tag = VALUE_INT` and `.data.integer = 7`, and read the payload only after checking the tag.

**Why it holds here.** The tag records which union member was last written, and the CHECK reads that same member, so the payload is 7.

**A plausible wrong approach.** Reading the other member, for example `strcmp(v.data.text, "ready")`, on this integer-tagged value. The union's 8 bytes then hold the integer 7 plus whatever was left in the rest, treated as an address, so passing it to `strcmp` is undefined behavior; the tag exists to prevent exactly that read.

**Verify.** Print `v.tag == VALUE_INT` and `v.data.integer` and see `1 7`; `sizeof v.data` is 8 on the worker because the pointer member is the largest.

## Exercise 4: Interpret a text alternative

Create a tagged value containing a borrowed string.

```c
struct Value v = {.tag = VALUE_TEXT, .data.text = "ready"};
CHECK(v.tag == VALUE_TEXT && strcmp(v.data.text, "ready") == 0);
```

**Expected:** The text is ready.

The text pointer borrows static string-literal storage. A general API would document ownership for dynamically supplied text.

**Approach.** Store a pointer to the string literal `"ready"` under `VALUE_TEXT` and compare the text with `strcmp`.

**Why it holds here.** A string literal has static storage duration, so the borrowed pointer remains valid for the whole program and `strcmp` returns 0.

**A plausible wrong approach.** Borrowing a local array instead, `{ char buf[] = "ready"; v.data.text = buf; }`, and comparing after the block. `buf` no longer exists, so the read through the dangling pointer is undefined; describe it rather than run it.

**Verify.** Print `v.data.text` with `%s` and see `ready`; under AddressSanitizer the defined version runs with no report.

## Exercise 5: Compare semantic fields

Compare two equal Points by x and y.

```c
struct Point a = {2, 3}, b = {2, 3};
CHECK(a.x == b.x && a.y == b.y);
```

**Expected:** Semantic equality is true.

Field comparison ignores padding. C does not supply whole-struct ==, and memcmp can distinguish irrelevant representation bytes.

**Approach.** Compare the meaningful fields one by one: `a.x == b.x && a.y == b.y`.

**Why it holds here.** Both points were initialized with 2 and 3, so each field comparison is true and the conjunction holds.

**A plausible wrong approach.** Writing `CHECK(a == b)`. C has no built-in equality for structs, so the compiler rejects the expression as invalid operands of type `struct Point`. `memcmp` would compile, but it also compares padding bytes, which this two-`int` struct lacks but a struct such as `{char c; int n;}` has.

**Verify.** Compile the `a == b` version to read the invalid-operands diagnostic, then print `sizeof(struct Point)` and see 8, exactly two `int`s, which confirms there is no padding here.

## Exercise 6: Transfer invalid-tag diagnosis

Pass an unexpected discriminator to a validator.

```c
CHECK(!valid_tag((enum ValueTag)99));
```

**Expected:** The validator rejects it.

An enum name list is not a runtime input validator. External integer data still needs range or membership checks.

**Approach.** Convert 99 to `enum ValueTag` and pass it to `valid_tag`, which accepts only the two named enumerators.

**Why it holds here.** An enum type is an integer type; the conversion keeps 99 because the worker's enum is 4 bytes, so `valid_tag` sees a value equal to neither enumerator and returns false.

**A plausible wrong approach.** Trusting the type alone, for example a `switch` with cases for `VALUE_INT` and `VALUE_TEXT` and no `default`, on the assumption that an `enum ValueTag` cannot hold anything else. 99 matches no case and falls through unhandled.

**Verify.** Print `(int)(enum ValueTag)99` and `valid_tag(VALUE_TEXT)` and see `99 1`.

## After comparison

Write `bool value_equal(const struct Value *a, const struct Value *b)` that returns false when either tag is invalid or the tags differ, compares integers with `==` and text with `strcmp`. Check that two `VALUE_INT` 7 values are equal, 7 and 8 are not, two `VALUE_TEXT` values pointing at different arrays that both hold `ready` are equal, and an integer 7 against tag 99 is unequal. Explain which case comparing `a->data.text == b->data.text` gets wrong.
