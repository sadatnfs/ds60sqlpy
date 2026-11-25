#include <stdio.h>

int main(void) {
  /* Exercise 1: Guard a formerly unsafe index: change one input
     In worked example 1, change `int values[] = {2, 4, 6}, out = 0;` to `int
     values[] = {2, 4, 7}, out = 0;`. Predict which value the CHECK on
     `at_index(values, 3, 2, &out) && out == 6` sees, then run and restore.
     Expected: `Check failed` at `at_index(values, 3, 2, &out) && out == 6`;
     restoring `int values[] = {2, 4, 6}, out = 0;` passes again. */

  /* Exercise 2: Reject the one-past index: debug a regression
     Worked example 2 now has a line reading `int values[] = {2, 4, 6}, out =
     10;`. Repair it so that the operation fails and output remains 9 again.
     Expected: `Check failed` at `!at_index(values, 3, 3, &out) && out == 9`
     until the line reads `int values[] = {2, 4, 6}, out = 9;` again. */

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
