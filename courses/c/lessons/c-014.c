#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a complete integer: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(parse_int("42",
     &out) && out == 42);` to `CHECK(parse_int("43", &out) && out == 42);`
     inside its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: The changed run stops with `Check
     failed` at the CHECK on `parse_int("42", &out) && out == 42`. Restoring the
     original line brings back the worked observation: success is true and
     output is 42. */

  /* Exercise 2: Reject trailing garbage: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int out = 8;`. Run worked example 2 with that line, use the failing CHECK
     to locate the defect and repair it without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `!parse_int("42x", &out) && out == 7`; after it the line reads `int out =
     7;` again and the call fails and output remains 7. */

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
