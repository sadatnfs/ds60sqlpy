#include <stdio.h>

int main(void) {
  /* Exercise 1: Protect a shared count: predict an edited check
     In worked example 1, change `CHECK(locked_total(4, 100) == 400);` to
     `CHECK(locked_total(5, 100) == 400);`. Predict whether the CHECK still
     holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(locked_total(5, 100) == 400);` is false, although the final count is
     400. */

  /* Exercise 2: Handle one worker: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(locked_total(2, 7) == 7);`.
     Explain why it fails although the result is 7, then restore it. Expected:
     `Check failed` until the CHECK reads `CHECK(locked_total(1, 7) == 7);`
     again, though the result is 7. */

  /* Exercise 3: Handle zero loop iterations
     Run two workers whose increment loops are empty.
     Expected: The result remains zero. */

  /* Exercise 4: Wait for a predicate
     Wait until a worker publishes ready with value 42.
     Expected: The parent observes value 42. */

  /* Exercise 5: Repeat independent synchronization
     Create and destroy the predicate fixture twice.
     Expected: Both operations return 42. */

  /* Exercise 6: Transfer count invariance
     Compare two workers times five increments with five workers times two.
     Expected: Both totals are 10. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
