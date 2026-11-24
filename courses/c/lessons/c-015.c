#include <stdio.h>

int main(void) {
  /* Exercise 1: Allocate and initialize: change one input
     Copy worked example 1, the "allocate and initialize" case, into a scratch
     pad and change `p[0] = 2;` to `p[1] = 2;`. Before running, predict which
     CHECK fails and which value it sees in place of the worked result (the sum
     is 12 before release); then run it and restore the original line. Expected:
     With `p[1] = 2;` the run stops with `Check failed` at the CHECK on `p[0] +
     p[1] + p[2] == 12`, because the "allocate and initialize" case no longer
     shows that the sum is 12 before release. Restoring `p[0] = 2;` brings that
     observation back. */

  /* Exercise 2: Inspect zero-initialized integers: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "inspect
     zero-initialized integers" case, so that it reads `CHECK(p[0] != 0 && p[1]
     == 0 && p[2] == 0);`. Run the example with that line, explain why the
     edited CHECK now fails even though the program state still means all three
     values are zero, and restore it. Expected: Before the repair the run stops
     with `Check failed` at the CHECK on `p[0] == 0 && p[1] == 0 && p[2] == 0`.
     Once the line reads `CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);` again,
     the "inspect zero-initialized integers" case again shows that all three
     values are zero. */

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
