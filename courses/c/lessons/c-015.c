#include <stdio.h>

int main(void) {
  /* Exercise 1: Allocate and initialize: change one input
     In worked example 1, change `p[0] = 2;` to `p[1] = 2;`. Predict which value
     the CHECK on `p[0] + p[1] + p[2] == 12` sees, then run and restore.
     Expected: `Check failed` at `p[0] + p[1] + p[2] == 12`; restoring `p[0] =
     2;` passes again. */

  /* Exercise 2: Inspect zero-initialized integers: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(p[0] != 0 && p[1] == 0 && p[2] ==
     0);`. Explain why it fails although all three values are zero, then restore
     it. Expected: `Check failed` until the CHECK reads `CHECK(p[0] == 0 && p[1]
     == 0 && p[2] == 0);` again, though all three values are zero. */

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
