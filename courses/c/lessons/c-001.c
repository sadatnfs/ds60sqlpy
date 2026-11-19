#include <stdio.h>

int main(void) {
  /* Exercise 1: Check a first value: change one input
     Copy worked example 1 into a scratch pad and change `int total = 2 + 3;` to
     `int total = 3 + 3;`. Before running, predict which CHECK fails and which
     value it now sees; then run it and restore the original line. Expected: The
     changed run stops with `Check failed` at the CHECK on `total == 5`.
     Restoring the original line brings back the worked observation: the stored
     value is 5. */

  /* Exercise 2: Format a checked result: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int n = snprintf(out, sizeof out, "total=%d", 6);`. Run worked example 2
     with that line, use the failing CHECK to locate the defect and repair it
     without changing the CHECK. Expected: Before the repair the run stops with
     `Check failed` at the CHECK on `strcmp(out, "total=5") == 0`; after it the
     line reads `int n = snprintf(out, sizeof out, "total=%d", 5);` again and
     the result length is 7 and text is total=5. */

  /* Exercise 3: Trace statement order
     Start at 1, increment, then multiply by 3.
     Expected: The result is 6. */

  /* Exercise 4: Inspect a boolean condition
     Compare 4 with 4 and 4 with 5.
     Expected: Equality is true and inequality is true. */

  /* Exercise 5: Use an explicit return contract
     Call a helper returning the value 7.
     Expected: The caller receives 7. */

  /* Exercise 6: Transfer a receipt calculation
     Multiply 4 items by a unit amount of 6.
     Expected: The checked amount is 24. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
