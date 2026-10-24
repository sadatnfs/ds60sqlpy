#include <stdio.h>

int main(void) {
  /* Exercise 1: Protect a shared count
     Run four threads doing one hundred locked increments each.
     Expected: The final count is 400. */

  /* Exercise 2: Handle one worker
     Run one worker doing seven increments.
     Expected: The result is 7. */

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
