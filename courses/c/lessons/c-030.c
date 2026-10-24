#include <stdio.h>

int main(void) {
  /* Exercise 1: Guard a formerly unsafe index
     Use a checked accessor on the final valid index.
     Expected: The value 6 is returned. */

  /* Exercise 2: Reject the one-past index
     Request index 3 from length 3.
     Expected: The operation fails and output remains 9. */

  /* Exercise 3: Reject an empty view
     Request index zero from an empty logical view.
     Expected: No access occurs. */

  /* Exercise 4: Verify a valid allocation lifetime
     Allocate, initialize, inspect and free one integer.
     Expected: The value is checked before release. */

  /* Exercise 5: Retain output capacity checks
     Format a short message into sufficient storage.
     Expected: The write fits completely. */

  /* Exercise 6: Transfer a newly discovered boundary
     Test a singleton at indices zero and one.
     Expected: Only zero is valid. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
