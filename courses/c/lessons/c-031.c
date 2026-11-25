#include <stdio.h>

int main(void) {
  /* Exercise 1: Add ordinary values: predict an edited check
     In worked example 1, change `CHECK(add_checked(7, 5, &out) && out == 12);`
     to `CHECK(add_checked(8, 5, &out) && out == 12);`. Predict whether the
     CHECK still holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(add_checked(8, 5, &out) && out == 12);` is false, although the
     result is 12. */

  /* Exercise 2: Reject positive overflow: debug a regression
     Worked example 2 now has a line reading `int out = 10;`. Repair it so that
     the operation fails and preserves output again. Expected: `Check failed` at
     `!add_checked(INT_MAX, 1, &out) && out == 9` until the line reads `int out
     = 9;` again. */

  /* Exercise 3: Reject negative overflow
     Add negative one to INT_MIN.
     Expected: The operation fails without evaluating the overflow. */

  /* Exercise 4: Accept exact boundaries
     Add zero to both int extremes.
     Expected: Both exact boundary values are accepted. */

  /* Exercise 5: Reject a size product
     Multiply SIZE_MAX by two through a size helper.
     Expected: The helper rejects it and preserves output. */

  /* Exercise 6: Transfer the zero product
     Multiply SIZE_MAX by zero.
     Expected: The checked mathematical result is zero. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
