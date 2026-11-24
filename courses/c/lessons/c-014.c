#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a complete integer: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(parse_int("42",
     &out) && out == 42);` to `CHECK(parse_int("43", &out) && out == 42);`
     inside its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: With `CHECK(parse_int("43", &out)
     && out == 42);` the run stops with `Check failed` at the CHECK on
     `parse_int("42", &out) && out == 42`, because the "parse a complete
     integer" case no longer shows that success is true and output is 42.
     Restoring `CHECK(parse_int("42", &out) && out == 42);` brings that
     observation back. */

  /* Exercise 2: Reject trailing garbage: debug a regression
     A regression changed one token in worked example 2, the "reject trailing
     garbage" case, so one line now reads `int out = 8;`. Run the example with
     that line, use the failing CHECK to find why the call fails and output
     remains 7 no longer holds and repair the line without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `!parse_int("42x", &out) && out == 7`. Once the line reads `int out =
     7;` again, the "reject trailing garbage" case again shows that the call
     fails and output remains 7. */

  /* Exercise 3: Reject empty input
     Parse an empty string.
     Expected: No numeric value is accepted. */

  /* Exercise 4: Reject an oversized number
     Parse a very long positive integer.
     Expected: The operation rejects the range overflow. */

  /* Exercise 5: Retain a valid negative value
     Parse -7.
     Expected: The output is -7. */

  /* Exercise 6: Transfer the whitespace policy
     Compare leading whitespace with trailing whitespace.
     Expected: Leading whitespace is accepted; trailing whitespace is rejected.
   */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
