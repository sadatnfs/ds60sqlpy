#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a valid list: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1
     &&` to `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1]
     == 1 &&` inside its CHECK. Before running, predict whether the CHECK still
     holds and explain why; then restore it. Expected: With
     `CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[1] == 1
     &&` the run stops with `Check failed` at the CHECK on `parse_list("1,20,3",
     out, 3, &count) && count == 3 && out[0] == 1 && out[1] == 20 && out[2] ==
     3`, because the "parse a valid list" case no longer shows that three values
     are returned in order. Restoring `CHECK(parse_list("1,20,3", out, 3,
     &count) && count == 3 && out[0] == 1 &&` brings that observation back. */

  /* Exercise 2: Reject an empty field: debug a regression
     A regression changed one token in worked example 2, the "reject an empty
     field" case, so one line now reads `unsigned out[3] = {10, 9, 9};`. Run the
     example with that line, use the failing CHECK to find why the parse fails
     and prior output is unchanged no longer holds and repair the line without
     changing the CHECK. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `!parse_list("1,,3", out, 3, &count) && out[0] == 9
     && count == 7`. Once the line reads `unsigned out[3] = {9, 9, 9};` again,
     the "reject an empty field" case again shows that the parse fails and prior
     output is unchanged. */

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
