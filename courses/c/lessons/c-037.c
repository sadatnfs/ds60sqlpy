#include <stdio.h>

int main(void) {
  /* Exercise 1: Protect a shared count: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(locked_total(4,
     100) == 400);` to `CHECK(locked_total(5, 100) == 400);` inside its CHECK.
     Before running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: With `CHECK(locked_total(5, 100) == 400);` the run
     stops with `Check failed` at the CHECK on `locked_total(4, 100) == 400`,
     because the "protect a shared count" case no longer shows that the final
     count is 400. Restoring `CHECK(locked_total(4, 100) == 400);` brings that
     observation back. */

  /* Exercise 2: Handle one worker: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "handle one
     worker" case, so that it reads `CHECK(locked_total(2, 7) == 7);`. Run the
     example with that line, explain why the edited CHECK now fails even though
     the program state still means the result is 7, and restore it. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `locked_total(1, 7) == 7`. Once the line reads `CHECK(locked_total(1, 7) ==
     7);` again, the "handle one worker" case again shows that the result is 7.
   */

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
