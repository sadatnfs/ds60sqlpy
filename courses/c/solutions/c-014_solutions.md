# c-014: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

External text must be parsed under an explicit grammar and range policy. atoi cannot report all useful failure distinctions, so robust code often uses strtol with an end pointer and errno. Parsing can consume no digits, stop before trailing garbage, or overflow the target type. A long result may still fail to fit an int even when strtol itself succeeded. Reset errno before the call and inspect it afterward. Define whitespace and sign rules deliberately. Preserve the output on failure so a caller cannot mistake a partial or stale result for a successful parse.

strtol(text,&end,10) parses base-ten text and stores where parsing stopped. end==text means no digits were consumed. errno==ERANGE reports range failure for long. Require *end=='\0' for this lesson's whole-string contract, then compare against INT_MIN and INT_MAX before converting. This helper accepts strtol leading whitespace and signs, but rejects trailing whitespace or other trailing text; a different user-facing policy should normalize explicitly before parsing.

## Exercise 1: Parse a complete integer

Parse 42 into an output integer.

```c
int out = 0;
CHECK(parse_int("42", &out) && out == 42);
```

**Expected:** Success is true and output is 42.

The parser validates complete consumption and final target range before assignment.

## Exercise 2: Reject trailing garbage

Parse 42x with an existing output of 7.

```c
int out = 7;
CHECK(!parse_int("42x", &out) && out == 7);
```

**Expected:** The call fails and output remains 7.

A valid prefix is not a valid complete input under this contract.

## Exercise 3: Reject empty input

Parse an empty string.

```c
int out = 7;
CHECK(!parse_int("", &out) && out == 7);
```

**Expected:** No numeric value is accepted.

The end pointer equals the start when no digits are consumed. A zero result alone cannot reveal that failure.

## Exercise 4: Reject an oversized number

Parse a very long positive integer.

```c
int out = 7;
CHECK(!parse_int("999999999999999999999999999999", &out) && out == 7);
```

**Expected:** The operation rejects the range overflow.

The test does not assume a particular long width. The fixture exceeds ordinary supported widths and exercises parser range evidence.

## Exercise 5: Retain a valid negative value

Parse -7.

```c
int out = 0;
CHECK(parse_int("-7", &out) && out == -7);
```

**Expected:** The output is -7.

A sign is part of this chosen grammar. Domain validation may impose additional restrictions afterward.

## Exercise 6: Transfer the whitespace policy

Compare leading whitespace with trailing whitespace.

```c
int out = 0;
CHECK(parse_int(" 3", &out) && out == 3);
CHECK(!parse_int("3 ", &out));
```

**Expected:** Leading whitespace is accepted; trailing whitespace is rejected.

This deliberate contrast makes the grammar observable. Do not change it accidentally by ignoring the end pointer.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
