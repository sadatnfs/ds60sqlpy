# c-014: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-014_solution.c`, implements all six cases, from the "parse a complete integer" case to the "transfer the whitespace policy" case, in one `main.c`.

## Mechanism and assumptions

External text must be parsed under an explicit grammar and range policy. atoi cannot report all useful failure distinctions, so robust code often uses strtol with an end pointer and errno. Parsing can consume no digits, stop before trailing garbage, or overflow the target type. A long result may still fail to fit an int even when strtol itself succeeded. Reset errno before the call and inspect it afterward. Define whitespace and sign rules deliberately. Preserve the output on failure so a caller cannot mistake a partial or stale result for a successful parse.

strtol(text,&end,10) parses base-ten text and stores where parsing stopped. end==text means no digits were consumed. errno==ERANGE reports range failure for long. Require *end=='\0' for this lesson's whole-string contract, then compare against INT_MIN and INT_MAX before converting. This helper accepts strtol leading whitespace and signs, but rejects trailing whitespace or other trailing text; a different user-facing policy should normalize explicitly before parsing.

## Exercise 1: Parse a complete integer: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(parse_int("42", &out) && out == 42);` to `CHECK(parse_int("43", &out) && out == 42);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
int out = 0;
CHECK(parse_int("42", &out) && out == 42);
```

**Expected:** With `CHECK(parse_int("43", &out) && out == 42);` the run stops with `Check failed` at the CHECK on `parse_int("42", &out) && out == 42`, because the "parse a complete integer" case no longer shows that success is true and output is 42. Restoring `CHECK(parse_int("42", &out) && out == 42);` brings that observation back.

The parser validates complete consumption and final target range before assignment.

**Approach.** Split the edited CHECK into its two operands: `parse_int("43", &out)` succeeds and stores 43, then `out == 42` compares 43 with 42.

**Why it holds here.** `"43"` is a complete decimal integer in range, so every rejection test passes and the parser writes 43; the CHECK fails on the comparison, not on parsing.

**A plausible wrong approach.** Predicting the failure comes from the parser rejecting the input. Printing only the CHECK result hides which operand failed, so a learner may start changing a parser that is working correctly.

**Verify.** Print the return value and `out` in separate statements and see `1 43`.

## Exercise 2: Reject trailing garbage: debug a regression

A regression changed one token in worked example 2, the "reject trailing garbage" case, so one line now reads `int out = 8;`. Run the example with that line, use the failing CHECK to find why the call fails and output remains 7 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int out = 7;
CHECK(!parse_int("42x", &out) && out == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!parse_int("42x", &out) && out == 7`. Once the line reads `int out = 7;` again, the "reject trailing garbage" case again shows that the call fails and output remains 7.

A valid prefix is not a valid complete input under this contract.

**Approach.** Read the CHECK as two facts: the call must fail on `"42x"`, and `out` must still equal its starting value. The regression changed the start to 8.

**Why it holds here.** `strtol` stops at `x`, so `*end != '\0'` rejects the input before any assignment; `out` keeps 8, and the comparison with 7 fails until the initializer is 7 again.

**A plausible wrong approach.** Assigning `*out = (int)value;` before the validation checks. Then `"42x"` still returns false, but `out` becomes 42, which breaks the preserve-on-rejection contract this CHECK tests even with the correct initializer.

**Verify.** Print `out` after the call and see 8 before the repair and 7 after it.

## Exercise 3: Reject empty input

Parse an empty string.

```c
int out = 7;
CHECK(!parse_int("", &out) && out == 7);
```

**Expected:** No numeric value is accepted.

The end pointer equals the start when no digits are consumed. A zero result alone cannot reveal that failure.

**Approach.** Detect that no digits were consumed with `end == text`.

**Why it holds here.** For `""`, `strtol` performs no conversion and sets `end` to the start, so the parser returns false and leaves `out` at 7.

**A plausible wrong approach.** Using `atoi(text)`. It returns 0 for `""`, the same as for `"0"`, so the caller cannot tell an empty field from a real zero, and `atoi` also reports no range errors.

**Verify.** Print `atoi("")` and see 0, then confirm `parse_int("", &out)` returns 0 with `out` still 7.

## Exercise 4: Reject an oversized number

Parse a very long positive integer.

```c
int out = 7;
CHECK(!parse_int("999999999999999999999999999999", &out) && out == 7);
```

**Expected:** The operation rejects the range overflow.

The test does not assume a particular long width. The fixture exceeds ordinary supported widths and exercises parser range evidence.

**Approach.** Reset `errno` to 0, call `strtol` and reject when `errno == ERANGE`, before the `int` range test.

**Why it holds here.** The 30-digit input exceeds `long`, so `strtol` returns `LONG_MAX` 9223372036854775807 and sets `ERANGE`; the parser returns false without writing `out`.

**A plausible wrong approach.** Relying only on `value > INT_MAX`. That happens to work here because the worker's `long` is 64 bits, but where `long` is 32 bits, as on 64-bit Windows, `LONG_MAX` equals `INT_MAX` and the clamped value would be accepted as 2147483647.

**Verify.** Call `strtol` directly on the fixture and print the value and `errno == ERANGE`, and see `9223372036854775807 1`.

## Exercise 5: Retain a valid negative value

Parse -7.

```c
int out = 0;
CHECK(parse_int("-7", &out) && out == -7);
```

**Expected:** The output is -7.

A sign is part of this chosen grammar. Domain validation may impose additional restrictions afterward.

**Approach.** Let `strtol` accept the optional sign and range-check the resulting `long` against `INT_MIN`.

**Why it holds here.** `-7` converts to the `long` -7, which lies inside `int`, so the parser stores -7.

**A plausible wrong approach.** Parsing with `strtoul` to reuse an unsigned helper. `strtoul("-7", ...)` negates the converted value in unsigned arithmetic and returns 18446744073709551609 with no error, so a negative input silently becomes a huge positive one.

**Verify.** Print `strtoul("-7", &end, 10)` and see 18446744073709551609 with `errno` 0, then confirm `parse_int` yields -7.

## Exercise 6: Transfer the whitespace policy

Compare leading whitespace with trailing whitespace.

```c
int out = 0;
CHECK(parse_int(" 3", &out) && out == 3);
CHECK(!parse_int("3 ", &out));
```

**Expected:** Leading whitespace is accepted; trailing whitespace is rejected.

This deliberate contrast makes the grammar observable. Do not change it accidentally by ignoring the end pointer.

**Approach.** Keep the grammar asymmetric: `strtol` skips leading whitespace, and the `*end != '\0'` test rejects anything left over.

**Why it holds here.** `" 3"` converts to 3 with `end` at the terminator, while `"3 "` leaves `end` at the space, so the second call returns false and `out` keeps 3.

**A plausible wrong approach.** Checking only `end != text` to detect digits. That accepts `"3 "`, and also `"3x"`, so the second CHECK fails and the grammar quietly changes to accept any valid prefix.

**Verify.** Call both inputs in separate statements and print the returns and `out`: `1`, `0`, then 3.

## After comparison

Write `bool parse_port(const char *text, int *out)` that reuses `parse_int` and then requires 1..65535. Check `"80"`, `"0"`, `"65536"`, `"-1"`, `"8080 "` and `""`, and confirm that `*out` is unchanged after every rejection. Explain which check rejects `"65536"` (the domain check, not `ERANGE`) and why `" 80"` passes under the inherited whitespace policy.
