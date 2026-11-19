#include <stdio.h>

int main(void) {
  /* Exercise 1: Trace block shadowing: change one input
     Copy worked example 1 into a scratch pad and change `int value = 3;` to
     `int value = 4;`. Before running, predict which CHECK fails and which value
     it now sees; then run it and restore the original line. Expected: The
     changed run stops with `Check failed` at the CHECK on `value == 3`.
     Restoring the original line brings back the worked observation: after the
     inner block, the outer remains 3. */

  /* Exercise 2: Retain static state: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(next_count() != 2);`. Run worked example 2 with that line, explain
     why the edited CHECK now fails for the same program state, and restore it.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `next_count() == 2`; after it the line reads `CHECK(next_count() == 2);`
     again and it returns 1 and then 2. */

  /* Exercise 3: Return a static address
     Get a pointer to a static read-only value.
     Expected: The target remains valid and equals 7. */

  /* Exercise 4: Keep automatic state per call
     Call a function with an initialized local counter twice.
     Expected: Both calls return 1. */

  /* Exercise 5: Separate visibility from lifetime
     Retain a value copy obtained from an inner block.
     Expected: The copied scalar remains 9 afterward. */

  /* Exercise 6: Transfer initialized aggregation
     Initialize an accumulator before processing an empty range.
     Expected: The result is the defined zero identity. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
