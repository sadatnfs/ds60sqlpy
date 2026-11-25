#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a pure calculation: predict an edited check
     In worked example 1, change `CHECK(twice(0) == 0);` to `CHECK(twice(1) ==
     0);`. Predict whether the CHECK still holds and why, then run and restore.
     Expected: `Check failed`: `CHECK(twice(1) == 0);` is false, although the
     results are 14 and 0. */

  /* Exercise 2: Return an output on success: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(try_area(4, 4, &out));`. Explain
     why it fails although success is true and output becomes 12, then restore
     it. Expected: `Check failed` until the CHECK reads `CHECK(try_area(3, 4,
     &out));` again, though success is true and output becomes 12. */

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
