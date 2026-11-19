#include <stdio.h>

int main(void) {
  /* Exercise 1: Change a caller-owned value: change one input
     Copy worked example 1 into a scratch pad and change `int n = 4;` to `int n
     = 5;`. Before running, predict which CHECK fails and which value it now
     sees; then run it and restore the original line. Expected: The changed run
     stops with `Check failed` at the CHECK on `n == 5`. Restoring the original
     line brings back the worked observation: the caller value becomes 5. */

  /* Exercise 2: Read a target copy: debug a regression
     A regression changed `int n = 3;` to `int n = 4;` in worked example 2. Run
     worked example 2 with that change, use the failing CHECK to explain the
     defect and repair it without changing the CHECK. Expected: Before the
     repair the run stops with `Check failed` at the CHECK on `copy == 3 && n ==
     9`; after it the line reads `int n = 3;` again and the copied value stays 3
     and the target becomes 9. */

  /* Exercise 3: Reject an absent target
     Pass NULL to an optional update helper.
     Expected: The helper returns false without an access. */

  /* Exercise 4: Update a present target
     Pass an integer address to the same helper.
     Expected: The helper returns true and stores 8. */

  /* Exercise 5: Distinguish pointer and target change
     Point p at a, then reassign p to b.
     Expected: Neither integer changes merely because p changes. */

  /* Exercise 6: Transfer a swap contract
     Swap two caller-owned integers through pointers.
     Expected: The values exchange positions. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
