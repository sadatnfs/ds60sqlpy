#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a valid list: predict an edited check
     In worked example 1, change `CHECK(parse_list("1,20,3", out, 3, &count) &&
     count == 3 && out[0] == 1 &&` to `CHECK(parse_list("1,20,3", out, 3,
     &count) && count == 3 && out[1] == 1 &&`. Predict whether the CHECK still
     holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1
     &&` is false, although three values are returned in order. */

  /* Exercise 2: Reject an empty field: debug a regression
     Worked example 2 now has a line reading `unsigned out[3] = {10, 9, 9};`.
     Repair it so that the parse fails and prior output is unchanged again.
     Expected: `Check failed` at `!parse_list("1,,3", out, 3, &count) && out[0]
     == 9 && count == 7` until the line reads `unsigned out[3] = {9, 9, 9};`
     again. */

  /* Exercise 3: Reject a trailing separator
     Parse 1,2,.
     Expected: The parse fails. */

  /* Exercise 4: Enforce output capacity
     Parse three values into capacity two.
     Expected: The operation fails without an overflow. */

  /* Exercise 5: Reject numeric overflow
     Parse a number with far too many digits.
     Expected: The range check rejects it. */

  /* Exercise 6: Transfer exact grammar boundaries
     Parse zero successfully and reject leading whitespace.
     Expected: Zero is valid; space-prefixed input is not. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
