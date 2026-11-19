#include <stdio.h>

int main(void) {
  /* Exercise 1: Add ordinary values: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(add_checked(7,
     5, &out) && out == 12);` to `CHECK(add_checked(8, 5, &out) && out == 12);`
     inside its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: The changed run stops with `Check
     failed` at the CHECK on `add_checked(7, 5, &out) && out == 12`. Restoring
     the original line brings back the worked observation: the result is 12. */

  /* Exercise 2: Reject positive overflow: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int out = 10;`. Run worked example 2 with that line, use the failing CHECK
     to locate the defect and repair it without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `!add_checked(INT_MAX, 1, &out) && out == 9`; after it the line reads `int
     out = 9;` again and the operation fails and preserves output. */

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
