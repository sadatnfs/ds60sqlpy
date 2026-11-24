#include <stdio.h>

int main(void) {
  /* Exercise 1: Swap integer objects: change one input
     Copy worked example 1, the "swap integer objects" case, into a scratch pad
     and change `int a = 2, b = 7;` to `int a = 3, b = 7;`. Before running,
     predict which CHECK fails and which value it sees in place of the worked
     result (the values become 7 and 2); then run it and restore the original
     line. Expected: With `int a = 3, b = 7;` the run stops with `Check failed`
     at the CHECK on `a == 7 && b == 2`, because the "swap integer objects" case
     no longer shows that the values become 7 and 2. Restoring `int a = 2, b =
     7;` brings that observation back. */

  /* Exercise 2: Swap fixed byte arrays: debug a regression
     A regression changed one token in worked example 2, the "swap fixed byte
     arrays" case, so one line now reads `unsigned char a[] = {2, 2, 3}, b[] =
     {4, 5, 6};`. Run the example with that line, use the failing CHECK to find
     why their byte contents exchange exactly no longer holds and repair the
     line without changing the CHECK. Expected: Before the repair the run stops
     with `Check failed` at the CHECK on `a[0] == 4 && a[2] == 6 && b[0] == 1 &&
     b[2] == 3`. Once the line reads `unsigned char a[] = {1, 2, 3}, b[] = {4,
     5, 6};` again, the "swap fixed byte arrays" case again shows that their
     byte contents exchange exactly. */

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
