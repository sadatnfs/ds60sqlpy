#include <stdio.h>

int main(void) {
  /* Exercise 1: Allocate and initialize
     Allocate three ints, assign 2, 4, 6 and sum them.
     Expected: The sum is 12 before release. */

  /* Exercise 2: Inspect zero-initialized integers
     Allocate three ints with calloc and read them.
     Expected: All three values are zero. */

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
