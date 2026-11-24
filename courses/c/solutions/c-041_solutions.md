# c-041: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-041_solution.c`, implements all six cases, from the "parse a valid list" case to the "transfer exact grammar boundaries" case, in one `main.c`.

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

**Expected:** With `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1 &&` the run stops with `Check failed` at the CHECK on `parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 && out[1] == 20 && out[2] == 3`, because the "parse a valid list" case no longer shows that three values are returned in order. Restoring `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&` brings that observation back.

The parser validates the entire grammar before publishing output.

## Exercise 2: Reject an empty field: debug a regression

A regression changed one token in worked example 2, the "reject an empty field" case, so one line now reads `unsigned out[3] = {10, 9, 9};`. Run the example with that line, use the failing CHECK to find why the parse fails and prior output is unchanged no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
unsigned out[3] = {9, 9, 9};
size_t count = 7;
CHECK(!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7`. Once the line reads `unsigned out[3] = {9, 9, 9};` again, the "reject an empty field" case again shows that the parse fails and prior output is unchanged.

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

Add a fresh distinguishing input for the "transfer exact grammar boundaries" case to your own c-041 source. Explain why every access in `parse_list` stays within a live object and each owned resource is released. An expected grammar failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "reject an empty field" case apart from ordinary output: the fixture proves its stated grammar, parser state and staged output assumptions, not universal safety.
