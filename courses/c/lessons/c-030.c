#include <stdio.h>

int main(void) {
  /* Exercise 1: Guard a formerly unsafe index: change one input
     Copy worked example 1, the "guard a formerly unsafe index" case, into a
     scratch pad and change `int values[] = {2, 4, 6}, out = 0;` to `int
     values[] = {2, 4, 7}, out = 0;`. Before running, predict which CHECK fails
     and which value it sees in place of the worked result (the value 6 is
     returned); then run it and restore the original line. Expected: With `int
     values[] = {2, 4, 7}, out = 0;` the run stops with `Check failed` at the
     CHECK on `at_index(values, 3, 2, &out) && out == 6`, because the "guard a
     formerly unsafe index" case no longer shows that the value 6 is returned.
     Restoring `int values[] = {2, 4, 6}, out = 0;` brings that observation
     back. */

  /* Exercise 2: Reject the one-past index: debug a regression
     A regression changed one token in worked example 2, the "reject the
     one-past index" case, so one line now reads `int values[] = {2, 4, 6}, out
     = 10;`. Run the example with that line, use the failing CHECK to find why
     the operation fails and output remains 9 no longer holds and repair the
     line without changing the CHECK. Expected: Before the repair the run stops
     with `Check failed` at the CHECK on `!at_index(values, 3, 3, &out) && out
     == 9`. Once the line reads `int values[] = {2, 4, 6}, out = 9;` again, the
     "reject the one-past index" case again shows that the operation fails and
     output remains 9. */

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
