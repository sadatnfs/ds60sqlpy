#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a pure calculation
     Evaluate twice for 7 and 0.
     Expected: The results are 14 and 0. */

  /* Exercise 2: Return an output on success
     Calculate area for width 3 and height 4.
     Expected: Success is true and output becomes 12. */

  /* Exercise 3: Preserve output on rejection
     Request area with width zero.
     Expected: The call fails and output remains -1. */

  /* Exercise 4: Trace copied scalar state
     Pass 5 to a helper that reassigns its parameter.
     Expected: The caller remains 5. */

  /* Exercise 5: Reject a missing output target
     Call try_area with a null output pointer.
     Expected: The call fails without dereferencing it. */

  /* Exercise 6: Transfer overflow prevention
     Request INT_MAX times 2.
     Expected: The operation rejects it and preserves output. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
