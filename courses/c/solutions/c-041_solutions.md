# c-041: explained solutions

`c-041_solution.c` assembles the "parse a valid list" case through the "transfer exact grammar boundaries" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A parser should define the language it accepts before processing bytes. A small state machine makes separator, digit and termination rules visible. It is safer than repeatedly guessing with partial conversions and ignoring leftovers. This lesson parses a deliberately narrow grammar: one or more unsigned decimal integers separated by single commas, with no spaces, signs or quoted fields. It is not a general CSV parser. Each digit update checks for overflow before multiplying by ten, and the output count is bounded by caller capacity. Invalid input preserves the caller output by parsing into a bounded temporary array first.

The parser alternates between expecting a digit and accepting further digits or a comma. A comma requires a completed number and another number afterward. End-of-input commits the last value only if a digit was seen. The accumulator bound uses value>(UINT_MAX-digit)/10 before value*10+digit. A temporary staging array makes the final output update failure-atomic for the declared maximum of eight numbers.

## Exercise 1: Parse a valid list: predict an edited check

In worked example 1, change `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&` to `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1 &&`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
unsigned out[3] = {0};
size_t count = 0;
CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&
      out[1] == 20 && out[2] == 3);
```

**Expected:** `Check failed`: `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1 &&` is false, although three values are returned in order.

**Verify:** Explain which claim `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1 &&` makes that the state fails; restoring `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&` passes again.

The parser validates the entire grammar before publishing output.

## Exercise 2: Reject an empty field: debug a regression

Worked example 2 now has a line reading `unsigned out[3] = {10, 9, 9};`. Repair it so that the parse fails and prior output is unchanged again.

The unchanged code is worked example 2:

```c
unsigned out[3] = {9, 9, 9};
size_t count = 7;
CHECK(!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7);
```

**Expected:** `Check failed` at `!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7` until the line reads `unsigned out[3] = {9, 9, 9};` again.

**Verify:** Explain how `unsigned out[3] = {10, 9, 9};` changes the value `!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7` tests, using your failing and repaired runs.

Two separators in a row violate the required-digit state.

## Exercise 3: Reject a trailing separator

Parse 1,2,.

```c
unsigned out[3] = {0};
size_t count = 0;
CHECK(!parse_list("1,2,", out, 3, &count));
```

**Expected:** The parse fails.

**Verify:** Keep a CHECK equivalent to `!parse_list("1,2,", out, 3, &count)`. Control edit: `CHECK(parse_list("1,2,", out, 3, &count));` must fail; then restore it.

The final comma requires another number. Accepting it silently would change the declared grammar.

## Exercise 4: Enforce output capacity

Parse three values into capacity two.

```c
unsigned out[2] = {9, 9};
size_t count = 7;
CHECK(!parse_list("1,2,3", out, 2, &count) && out[0] == 9 && count == 7);
```

**Expected:** The operation fails without an overflow.

**Verify:** Keep a CHECK equivalent to `!parse_list("1,2,3", out, 2, &count) && out[0] == 9 && count == 7`. Control edit: changing `unsigned out[2] = {9, 9};` to `unsigned out[2] = {10, 9};` must fail it; then restore it.

The destination capacity is a hard bound, not a suggestion. The staged parser rejects excess before copying.

## Exercise 5: Reject numeric overflow

Parse a number with far too many digits.

```c
unsigned out[1] = {0};
size_t count = 0;
CHECK(!parse_list("999999999999999999999999", out, 1, &count));
```

**Expected:** The range check rejects it.

**Verify:** Keep a CHECK equivalent to `!parse_list("999999999999999999999999", out, 1, &count)`. Control edit: `CHECK(parse_list("999999999999999999999999", out, 1, &count));` must fail; then restore it.

The arithmetic check occurs before the overflowing multiplication.

## Exercise 6: Transfer exact grammar boundaries

Parse zero successfully and reject leading whitespace.

```c
unsigned out[1] = {9};
size_t count = 0;
CHECK(parse_list("0", out, 1, &count) && out[0] == 0 && count == 1);
CHECK(!parse_list(" 1", out, 1, &count));
```

**Expected:** Zero is valid; space-prefixed input is not.

**Verify:** Keep a CHECK equivalent to `parse_list("0", out, 1, &count) && out[0] == 0 && count == 1`. Control edit: `CHECK(parse_list("1", out, 1, &count) && out[0] == 0 && count == 1);` must fail; then restore it.

Whitespace handling is a deliberate grammar choice. A higher-level input layer can normalize it explicitly if the product requires that policy.

## After comparison

Parse `"7,08"` into two slots and CHECK that this grammar, as written, accepts the leading zero and stores 8. Then parse `"4294967296"` and CHECK the rejection while `out` keeps its previous contents, because values are staged in `temporary`. Explain which branch rejects the overflow before `value * 10U + digit` can wrap, and decide whether your own grammar should accept `08`.
