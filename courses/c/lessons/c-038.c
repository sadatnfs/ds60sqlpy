#include <stdio.h>

int main(void) {
  /* Exercise 1: Inspect fetch-add semantics: change one input
     Copy worked example 1, the "inspect fetch-add semantics" case, into a
     scratch pad and change `atomic_init(&value, 2);` to `atomic_init(&value,
     3);`. Before running, predict which CHECK fails and which value it sees in
     place of the worked result (the returned old value is 2 and current value
     is 5); then run it and restore the original line. Expected: With
     `atomic_init(&value, 3);` the run stops with `Check failed` at the CHECK on
     `old == 2 && atomic_load(&value) == 5`, because the "inspect fetch-add
     semantics" case no longer shows that the returned old value is 2 and
     current value is 5. Restoring `atomic_init(&value, 2);` brings that
     observation back. */

  /* Exercise 2: Compare and exchange successfully: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "compare and
     exchange successfully" case, so that it reads
     `CHECK(atomic_compare_exchange_strong(&value, &expected, 8));`. Run the
     example with that line, explain why the edited CHECK now fails even though
     the program state still means the operation succeeds and stores 7, and
     restore it. Expected: Before the repair the run stops with `Check failed`
     at the CHECK on `atomic_load(&value) == 7`. Once the line reads
     `CHECK(atomic_compare_exchange_strong(&value, &expected, 7));` again, the
     "compare and exchange successfully" case again shows that the operation
     succeeds and stores 7. */

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
