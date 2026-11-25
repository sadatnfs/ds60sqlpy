#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a complete integer: predict an edited check
     In worked example 1, change `CHECK(parse_int("42", &out) && out == 42);` to
     `CHECK(parse_int("43", &out) && out == 42);`. Predict whether the CHECK
     still holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(parse_int("43", &out) && out == 42);` is false, although success is
     true and output is 42. */

  /* Exercise 2: Reject trailing garbage: debug a regression
     Worked example 2 now has a line reading `int out = 8;`. Repair it so that
     the call fails and output remains 7 again. Expected: `Check failed` at
     `!parse_int("42x", &out) && out == 7` until the line reads `int out = 7;`
     again. */

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
