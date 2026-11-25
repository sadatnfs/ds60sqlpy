#include <stdio.h>

int main(void) {
  /* Exercise 1: Swap integer objects: change one input
     In worked example 1, change `int a = 2, b = 7;` to `int a = 3, b = 7;`.
     Predict which value the CHECK on `a == 7 && b == 2` sees, then run and
     restore. Expected: `Check failed` at `a == 7 && b == 2`; restoring `int a =
     2, b = 7;` passes again. */

  /* Exercise 2: Swap fixed byte arrays: debug a regression
     Worked example 2 now has a line reading `unsigned char a[] = {2, 2, 3}, b[]
     = {4, 5, 6};`. Repair it so that their byte contents exchange exactly
     again. Expected: `Check failed` at `a[0] == 4 && a[2] == 6 && b[0] == 1 &&
     b[2] == 3` until the line reads `unsigned char a[] = {1, 2, 3}, b[] = {4,
     5, 6};` again. */

  /* Exercise 3: Use a zero-length operation
     Invoke the helper with size zero and valid object pointers.
     Expected: Both objects remain unchanged. */

  /* Exercise 4: Round-trip a swap
     Swap two ints twice.
     Expected: The original values return. */

  /* Exercise 5: Read bytes through a generic input
     Count three nonzero bytes in a four-byte buffer.
     Expected: The count is 3. */

  /* Exercise 6: Transfer a typed structure copy
     Copy a Pair into another Pair using its exact size.
     Expected: Both semantic fields match. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
