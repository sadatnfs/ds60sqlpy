#include <stdio.h>

int main(void) {
  /* Exercise 1: Protect a shared count: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(locked_total(4,
     100) == 400);` to `CHECK(locked_total(5, 100) == 400);` inside its CHECK.
     Before running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: The changed run stops with `Check failed` at the
     CHECK on `locked_total(4, 100) == 400`. Restoring the original line brings
     back the worked observation: the final count is 400. */

  /* Exercise 2: Handle one worker: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(locked_total(2, 7) == 7);`. Run worked example 2 with that line,
     explain why the edited CHECK now fails for the same program state, and
     restore it. Expected: Before the repair the run stops with `Check failed`
     at the CHECK on `locked_total(1, 7) == 7`; after it the line reads
     `CHECK(locked_total(1, 7) == 7);` again and the result is 7. */

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
