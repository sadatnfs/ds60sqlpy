#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a pure calculation: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(twice(0) == 0);`
     to `CHECK(twice(1) == 0);` inside its CHECK. Before running, predict
     whether the CHECK still holds and explain why; then restore it. Expected:
     With `CHECK(twice(1) == 0);` the run stops with `Check failed` at the CHECK
     on `twice(0) == 0`, because the "call a pure calculation" case no longer
     shows that the results are 14 and 0. Restoring `CHECK(twice(0) == 0);`
     brings that observation back. */

  /* Exercise 2: Return an output on success: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "return an
     output on success" case, so that it reads `CHECK(try_area(4, 4, &out));`.
     Run the example with that line, explain why the edited CHECK now fails even
     though the program state still means success is true and output becomes 12,
     and restore it. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `out == 12`. Once the line reads `CHECK(try_area(3,
     4, &out));` again, the "return an output on success" case again shows that
     success is true and output becomes 12. */

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
