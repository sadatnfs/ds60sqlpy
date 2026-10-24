#include <stdio.h>

int main(void) {
  /* Exercise 1: Change a caller-owned value
     Increment integer 4 through its address.
     Expected: The caller value becomes 5. */

  /* Exercise 2: Read a target copy
     Copy the integer behind a pointer, then change the target.
     Expected: The copied value stays 3 and the target becomes 9. */

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
