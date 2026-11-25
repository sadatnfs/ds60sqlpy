#include <stdio.h>

int main(void) {
  /* Exercise 1: Inspect fetch-add semantics: change one input
     In worked example 1, change `atomic_init(&value, 2);` to
     `atomic_init(&value, 3);`. Predict which value the CHECK on `old == 2 &&
     atomic_load(&value) == 5` sees, then run and restore. Expected: `Check
     failed` at `old == 2 && atomic_load(&value) == 5`; restoring
     `atomic_init(&value, 2);` passes again. */

  /* Exercise 2: Compare and exchange successfully: diagnose an edited check
     Worked example 2's CHECK now reads
     `CHECK(atomic_compare_exchange_strong(&value, &expected, 8));`. Explain why
     it fails although the operation succeeds and stores 7, then restore it.
     Expected: `Check failed` until the CHECK reads
     `CHECK(atomic_compare_exchange_strong(&value, &expected, 7));` again,
     though the operation succeeds and stores 7. */

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
