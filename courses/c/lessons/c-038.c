#include <stdio.h>

int main(void) {
  /* Exercise 1: Inspect fetch-add semantics
     Add 3 to an atomic integer initially 2.
     Expected: The returned old value is 2 and current value is 5. */

  /* Exercise 2: Compare and exchange successfully
     Replace expected value 2 with 7.
     Expected: The operation succeeds and stores 7. */

  /* Exercise 3: Inspect failed compare-exchange
     Attempt replacement with stale expected value 2 when current is 3.
     Expected: It fails and expected becomes 3. */

  /* Exercise 4: Count independent events
     Perform ten relaxed increments before reading in the same thread.
     Expected: The count is 10. */

  /* Exercise 5: Publish initialized data
     Use a release flag from a worker and acquire it before reading its payload.
     Expected: The payload is 42. */

  /* Exercise 6: Transfer an atomic exchange
     Replace a flag value and inspect the returned prior state.
     Expected: The old state is false and the new state true. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
