#include <stdio.h>

int main(void) {
  /* Exercise 1: Inspect fetch-add semantics: change one input
     Copy worked example 1 into a scratch pad and change `atomic_init(&value,
     2);` to `atomic_init(&value, 3);`. Before running, predict which CHECK
     fails and which value it now sees; then run it and restore the original
     line. Expected: The changed run stops with `Check failed` at the CHECK on
     `old == 2 && atomic_load(&value) == 5`. Restoring the original line brings
     back the worked observation: the returned old value is 2 and current value
     is 5. */

  /* Exercise 2: Compare and exchange successfully: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(atomic_compare_exchange_strong(&value, &expected, 8));`. Run worked
     example 2 with that line, explain why the edited CHECK now fails for the
     same program state, and restore it. Expected: Before the repair the run
     stops with `Check failed` at the CHECK on `atomic_load(&value) == 7`; after
     it the line reads `CHECK(atomic_compare_exchange_strong(&value, &expected,
     7));` again and the operation succeeds and stores 7. */

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
