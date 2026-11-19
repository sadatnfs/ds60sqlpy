# c-041: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A parser should define the language it accepts before processing bytes. A small state machine makes separator, digit and termination rules visible. It is safer than repeatedly guessing with partial conversions and ignoring leftovers. This lesson parses a deliberately narrow grammar: one or more unsigned decimal integers separated by single commas, with no spaces, signs or quoted fields. It is not a general CSV parser. Each digit update checks for overflow before multiplying by ten, and the output count is bounded by caller capacity. Invalid input preserves the caller output by parsing into a bounded temporary array first.

The parser alternates between expecting a digit and accepting further digits or a comma. A comma requires a completed number and another number afterward. End-of-input commits the last value only if a digit was seen. The accumulator bound uses value>(UINT_MAX-digit)/10 before value*10+digit. A temporary staging array makes the final output update failure-atomic for the declared maximum of eight numbers.

## Exercise 1: Parse a valid list: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&` to `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1 &&` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
unsigned out[3] = {0};
size_t count = 0;
CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&
      out[1] == 20 && out[2] == 3);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 && out[1] == 20 && out[2] == 3`. Restoring the original line brings back the worked observation: three values are returned in order.

The parser validates the entire grammar before publishing output.

## Exercise 2: Reject an empty field: debug a regression

A regression changed one token in worked example 2, so one line now reads `unsigned out[3] = {10, 9, 9};`. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
unsigned out[3] = {9, 9, 9};
size_t count = 7;
CHECK(!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7`; after it the line reads `unsigned out[3] = {9, 9, 9};` again and the parse fails and prior output is unchanged.

Two separators in a row violate the required-digit state.

## Exercise 3: Reject a trailing separator

Parse 1,2,.

```c
unsigned out[3] = {0};
size_t count = 0;
CHECK(!parse_list("1,2,", out, 3, &count));
```

**Expected:** The parse fails.

The final comma requires another number. Accepting it silently would change the declared grammar.

## Exercise 4: Enforce output capacity

Parse three values into capacity two.

```c
unsigned out[2] = {9, 9};
size_t count = 7;
CHECK(!parse_list("1,2,3", out, 2, &count) && out[0] == 9 && count == 7);
```

**Expected:** The operation fails without an overflow.

The destination capacity is a hard bound, not a suggestion. The staged parser rejects excess before copying.

## Exercise 5: Reject numeric overflow

Parse a number with far too many digits.

```c
unsigned out[1] = {0};
size_t count = 0;
CHECK(!parse_list("999999999999999999999999", out, 1, &count));
```

**Expected:** The range check rejects it.

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

Whitespace handling is a deliberate grammar choice. A higher-level input layer can normalize it explicitly if the product requires that policy.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
