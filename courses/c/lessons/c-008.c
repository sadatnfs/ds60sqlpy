#include <stdio.h>

int main(void) {
  /* Exercise 1: Change a caller-owned value: change one input
     In worked example 1, change `int n = 4;` to `int n = 5;`. Predict which
     value the CHECK on `n == 5` sees, then run and restore. Expected: `Check
     failed` at `n == 5`; restoring `int n = 4;` passes again. */

  /* Exercise 2: Read a target copy: debug a regression
     In worked example 2, `int n = 3;` now reads `int n = 4;`. Repair it so that
     the copied value stays 3 and the target becomes 9 again. Expected: `Check
     failed` at `copy == 3 && n == 9` until the line reads `int n = 3;` again.
   */

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
