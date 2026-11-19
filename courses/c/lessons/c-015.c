#include <stdio.h>

int main(void) {
  /* Exercise 1: Allocate and initialize: change one input
     Copy worked example 1 into a scratch pad and change `p[0] = 2;` to `p[1] =
     2;`. Before running, predict which CHECK fails and which value it now sees;
     then run it and restore the original line. Expected: The changed run stops
     with `Check failed` at the CHECK on `p[0] + p[1] + p[2] == 12`. Restoring
     the original line brings back the worked observation: the sum is 12 before
     release. */

  /* Exercise 2: Inspect zero-initialized integers: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(p[0] != 0 && p[1] == 0 && p[2] == 0);`. Run worked example 2 with
     that line, explain why the edited CHECK now fails for the same program
     state, and restore it. Expected: Before the repair the run stops with
     `Check failed` at the CHECK on `p[0] == 0 && p[1] == 0 && p[2] == 0`; after
     it the line reads `CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);` again and
     all three values are zero. */

  /* Exercise 3: Define the empty allocation policy
     Request zero elements through the helper.
     Expected: The helper returns NULL without an allocation. */

  /* Exercise 4: Reject multiplication overflow
     Request SIZE_MAX elements.
     Expected: The helper returns NULL before multiplication or allocation. */

  /* Exercise 5: Release an absent allocation
     Call free on NULL.
     Expected: The operation is harmless. */

  /* Exercise 6: Transfer ownership cleanup
     Allocate one value, release it and clear the owning pointer.
     Expected: The owner records absence afterward. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
